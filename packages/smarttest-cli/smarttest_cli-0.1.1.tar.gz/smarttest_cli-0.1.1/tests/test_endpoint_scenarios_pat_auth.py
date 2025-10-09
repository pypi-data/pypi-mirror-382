"""
Test PAT token authentication for the new endpoint scenarios endpoint
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
def mock_endpoint_data():
    """Mock endpoint and scenarios data"""
    # Mock scenarios
    scenario1 = Mock()
    scenario1.id = 1
    scenario1.name = "Test Scenario 1"
    scenario1.endpoint_id = 2
    scenario1.active = True
    scenario1.validations = [Mock(), Mock()]  # 2 validations
    scenario1.created_at = datetime.now(timezone.utc)

    scenario2 = Mock()
    scenario2.id = 2
    scenario2.name = "Test Scenario 2"
    scenario2.endpoint_id = 2
    scenario2.active = True
    scenario2.validations = []  # No validations
    scenario2.created_at = datetime.now(timezone.utc)

    scenario3 = Mock()
    scenario3.id = 3
    scenario3.name = "Test Scenario 3"
    scenario3.endpoint_id = 2
    scenario3.active = False
    scenario3.validations = [Mock()]  # 1 validation
    scenario3.created_at = datetime.now(timezone.utc)

    # Mock endpoint
    endpoint = Mock()
    endpoint.id = 2
    endpoint.system_id = 3
    endpoint.scenarios = [scenario1, scenario2, scenario3]

    return {
        "endpoint": endpoint,
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


class TestEndpointScenariosEndpoint:
    """Test the new endpoint scenarios endpoint with PAT token auth"""

    def test_endpoint_scenarios_success_all(self, client, override_auth_dependency, mock_customer, mock_endpoint_data, mocker):
        """Test successful endpoint scenarios retrieval (all scenarios)"""
        # Mock service calls
        mocker.patch('routes.endpoint_routes.get_endpoint_by_id', return_value=mock_endpoint_data["endpoint"])
        mocker.patch('routes.endpoint_routes.CustomerService.check_user_system_access', return_value=None)

        # Make API call
        response = client.get("/endpoints/2/scenarios")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify basic structure
        assert "scenarios" in data
        assert "total" in data
        assert "endpoint_id" in data
        assert "filtered" in data

        # Verify data
        assert data["endpoint_id"] == 2
        assert data["total"] == 3
        assert data["filtered"] is False
        assert len(data["scenarios"]) == 3

        # Verify scenario data
        scenario_data = data["scenarios"][0]
        assert scenario_data["id"] == 1
        assert scenario_data["name"] == "Test Scenario 1"
        assert scenario_data["endpoint_id"] == 2
        assert scenario_data["active"] is True
        assert scenario_data["validation_count"] == 2

    def test_endpoint_scenarios_with_validations_only(self, client, override_auth_dependency, mock_customer, mock_endpoint_data, mocker):
        """Test endpoint scenarios with only_with_validations=true"""
        # Mock service calls
        mocker.patch('routes.endpoint_routes.get_endpoint_by_id', return_value=mock_endpoint_data["endpoint"])
        mocker.patch('routes.endpoint_routes.CustomerService.check_user_system_access', return_value=None)

        # Make API call with filter
        response = client.get("/endpoints/2/scenarios?only_with_validations=true")

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

    def test_endpoint_scenarios_endpoint_not_found(self, client, override_auth_dependency, mocker):
        """Test endpoint scenarios with non-existent endpoint"""
        mocker.patch('routes.endpoint_routes.get_endpoint_by_id', return_value=None)

        response = client.get("/endpoints/999/scenarios")

        assert response.status_code == 404
        assert "Endpoint not found with id 999" in response.json()["detail"]

    def test_endpoint_scenarios_requires_authentication(self, client):
        """Test that the endpoint requires authentication when no override is active"""
        response = client.get("/endpoints/2/scenarios")

        # Should require authentication (401)
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_endpoint_scenarios_access_control(self, client, override_auth_dependency, mock_endpoint_data, mocker):
        """Test that access control is enforced"""
        mocker.patch('routes.endpoint_routes.get_endpoint_by_id', return_value=mock_endpoint_data["endpoint"])

        # Mock access control to raise HTTPException
        from fastapi import HTTPException
        mocker.patch('routes.endpoint_routes.CustomerService.check_user_system_access',
                     side_effect=HTTPException(status_code=403, detail="Access denied"))

        response = client.get("/endpoints/2/scenarios")

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied"

    def test_endpoint_scenarios_empty_scenarios(self, client, override_auth_dependency, mock_customer, mocker):
        """Test endpoint with no scenarios"""
        # Mock endpoint with no scenarios
        empty_endpoint = Mock()
        empty_endpoint.id = 2
        empty_endpoint.system_id = 3
        empty_endpoint.scenarios = []

        mocker.patch('routes.endpoint_routes.get_endpoint_by_id', return_value=empty_endpoint)
        mocker.patch('routes.endpoint_routes.CustomerService.check_user_system_access', return_value=None)

        response = client.get("/endpoints/2/scenarios")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["scenarios"]) == 0

    def test_endpoint_scenarios_with_validations_filter_none_match(self, client, override_auth_dependency, mock_customer, mocker):
        """Test only_with_validations filter when no scenarios have validations"""
        # Mock endpoint where all scenarios have no validations
        scenario_no_val = Mock()
        scenario_no_val.id = 1
        scenario_no_val.name = "No Validations"
        scenario_no_val.endpoint_id = 2
        scenario_no_val.validations = []
        scenario_no_val.created_at = datetime.now(timezone.utc)

        endpoint = Mock()
        endpoint.id = 2
        endpoint.system_id = 3
        endpoint.scenarios = [scenario_no_val]

        mocker.patch('routes.endpoint_routes.get_endpoint_by_id', return_value=endpoint)
        mocker.patch('routes.endpoint_routes.CustomerService.check_user_system_access', return_value=None)

        response = client.get("/endpoints/2/scenarios?only_with_validations=true")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["filtered"] is True
        assert len(data["scenarios"]) == 0