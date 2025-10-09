"""
Test PAT token authentication for the new system scenarios endpoint
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from main import app
from service.AuthService import require_auth


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def mock_customer():
    """Mock authenticated customer"""
    customer = Mock()
    customer.id = "customer_123"
    customer.email = "test@example.com"
    return customer


@pytest.fixture
def mock_system_data():
    """Mock system with endpoints and scenarios"""
    # Mock scenarios for endpoint 1
    scenario1 = Mock()
    scenario1.id = 1
    scenario1.name = "Test Scenario 1"
    scenario1.endpoint_id = 1
    scenario1.active = True
    scenario1.validations = [Mock(), Mock()]  # 2 validations
    scenario1.created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)

    scenario2 = Mock()
    scenario2.id = 2
    scenario2.name = "Test Scenario 2"
    scenario2.endpoint_id = 1
    scenario2.active = True
    scenario2.validations = []  # No validations
    scenario2.created_at = datetime(2023, 1, 2, tzinfo=timezone.utc)

    # Mock scenarios for endpoint 2
    scenario3 = Mock()
    scenario3.id = 3
    scenario3.name = "Test Scenario 3"
    scenario3.endpoint_id = 2
    scenario3.active = False
    scenario3.validations = [Mock()]  # 1 validation
    scenario3.created_at = datetime(2023, 1, 3, tzinfo=timezone.utc)

    # Mock endpoints
    endpoint1 = Mock()
    endpoint1.id = 1
    endpoint1.scenarios = [scenario1, scenario2]

    endpoint2 = Mock()
    endpoint2.id = 2
    endpoint2.scenarios = [scenario3]

    # Mock system
    system = Mock()
    system.id = 3
    system.endpoints = [endpoint1, endpoint2]

    return {
        "system": system,
        "scenarios": [scenario1, scenario2, scenario3]
    }


@pytest.fixture
def override_auth_dependency(mock_customer):
    """Override FastAPI auth dependency to bypass authentication during tests"""
    app.dependency_overrides[require_auth] = lambda: mock_customer
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_auth, None)


class TestSystemScenariosEndpoint:
    """Test the new system scenarios endpoint with PAT token auth"""

    def test_system_scenarios_success_all(self, client, override_auth_dependency, mock_customer, mock_system_data, mocker):
        """Test successful system scenarios retrieval (all scenarios)"""
        # Mock service calls
        mocker.patch('routes.system_routes.check_system_exists', return_value=mock_system_data["system"])
        mocker.patch('routes.system_routes.CustomerService.check_user_system_access', return_value=None)

        # Make API call
        response = client.get("/system/3/scenarios")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify basic structure
        assert "scenarios" in data
        assert "total" in data
        assert "system_id" in data
        assert "filtered" in data

        # Verify data
        assert data["system_id"] == 3
        assert data["total"] == 3
        assert data["filtered"] is False
        assert len(data["scenarios"]) == 3

        # Verify scenarios are sorted by creation date (newest first)
        assert data["scenarios"][0]["id"] == 3  # Created 2023-01-03
        assert data["scenarios"][1]["id"] == 2  # Created 2023-01-02
        assert data["scenarios"][2]["id"] == 1  # Created 2023-01-01

        # Verify scenario data structure
        scenario_data = data["scenarios"][0]
        assert scenario_data["id"] == 3
        assert scenario_data["name"] == "Test Scenario 3"
        assert scenario_data["endpoint_id"] == 2
        assert scenario_data["active"] is False
        assert scenario_data["validation_count"] == 1

    def test_system_scenarios_with_validations_only(self, client, override_auth_dependency, mock_customer, mock_system_data, mocker):
        """Test system scenarios with only_with_validations=true"""
        # Mock service calls
        mocker.patch('routes.system_routes.check_system_exists', return_value=mock_system_data["system"])
        mocker.patch('routes.system_routes.CustomerService.check_user_system_access', return_value=None)

        # Make API call with filter
        response = client.get("/system/3/scenarios?only_with_validations=true")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Should only return scenarios with validations (scenario1 and scenario3)
        assert data["total"] == 2
        assert data["filtered"] is True
        assert len(data["scenarios"]) == 2

        # Verify returned scenarios have validations
        for scenario in data["scenarios"]:
            assert scenario["validation_count"] > 0

        # Verify correct scenarios returned (should be scenario3 first, then scenario1)
        assert data["scenarios"][0]["id"] == 3
        assert data["scenarios"][1]["id"] == 1

    def test_system_scenarios_system_not_found(self, client, override_auth_dependency, mocker):
        """Test system scenarios with non-existent system"""
        # Mock access control to pass, then let check_system_exists fail
        mocker.patch('routes.system_routes.CustomerService.check_user_system_access', return_value=None)

        from fastapi import HTTPException
        mocker.patch('routes.system_routes.check_system_exists', side_effect=HTTPException(status_code=404, detail="System not found with id 999"))

        response = client.get("/system/999/scenarios")

        assert response.status_code == 404
        assert "System not found with id 999" in response.json()["detail"]

    def test_system_scenarios_requires_authentication(self, client):
        """Test that the endpoint requires authentication when no override is active"""
        response = client.get("/system/3/scenarios")

        # Should require authentication (401)
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_system_scenarios_access_control(self, client, override_auth_dependency, mock_system_data, mocker):
        """Test that access control is enforced"""
        mocker.patch('routes.system_routes.check_system_exists', return_value=mock_system_data["system"])

        # Mock access control to raise HTTPException
        from fastapi import HTTPException
        mocker.patch('routes.system_routes.CustomerService.check_user_system_access',
                     side_effect=HTTPException(status_code=403, detail="Access denied"))

        response = client.get("/system/3/scenarios")

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied"

    def test_system_scenarios_empty_system(self, client, override_auth_dependency, mock_customer, mocker):
        """Test system with no endpoints/scenarios"""
        # Mock system with no endpoints
        empty_system = Mock()
        empty_system.id = 3
        empty_system.endpoints = []

        mocker.patch('routes.system_routes.check_system_exists', return_value=empty_system)
        mocker.patch('routes.system_routes.CustomerService.check_user_system_access', return_value=None)

        response = client.get("/system/3/scenarios")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["scenarios"]) == 0

    def test_system_scenarios_with_validations_filter_none_match(self, client, override_auth_dependency, mock_customer, mocker):
        """Test only_with_validations filter when no scenarios have validations"""
        # Mock scenario with no validations
        scenario_no_val = Mock()
        scenario_no_val.id = 1
        scenario_no_val.name = "No Validations"
        scenario_no_val.endpoint_id = 1
        scenario_no_val.validations = []
        scenario_no_val.created_at = datetime.now(timezone.utc)

        endpoint = Mock()
        endpoint.id = 1
        endpoint.scenarios = [scenario_no_val]

        system = Mock()
        system.id = 3
        system.endpoints = [endpoint]

        mocker.patch('routes.system_routes.check_system_exists', return_value=system)
        mocker.patch('routes.system_routes.CustomerService.check_user_system_access', return_value=None)

        response = client.get("/system/3/scenarios?only_with_validations=true")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["filtered"] is True
        assert len(data["scenarios"]) == 0

    def test_system_scenarios_multiple_endpoints_mixed_scenarios(self, client, override_auth_dependency, mock_customer, mock_system_data, mocker):
        """Test system with multiple endpoints containing mixed scenarios"""
        # Mock service calls
        mocker.patch('routes.system_routes.check_system_exists', return_value=mock_system_data["system"])
        mocker.patch('routes.system_routes.CustomerService.check_user_system_access', return_value=None)

        # Make API call
        response = client.get("/system/3/scenarios")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify we get scenarios from both endpoints
        endpoint_ids = {scenario["endpoint_id"] for scenario in data["scenarios"]}
        assert endpoint_ids == {1, 2}

        # Verify total count
        assert data["total"] == 3