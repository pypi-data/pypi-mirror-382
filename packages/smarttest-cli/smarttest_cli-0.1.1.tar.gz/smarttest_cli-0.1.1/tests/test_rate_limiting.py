"""
Test rate limiting for CLI endpoints
"""

import pytest
import time
from unittest.mock import Mock
from fastapi.testclient import TestClient

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
def override_auth_dependency(mock_customer):
    """Override FastAPI auth dependency to bypass authentication during tests"""
    # Clear rate limiter state before each test
    from service.RateLimitService import rate_limiter
    rate_limiter._customer_requests.clear()

    app.dependency_overrides[require_auth] = lambda: mock_customer
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def mock_scenario_data():
    """Mock scenario and related data"""
    # Mock scenario
    scenario = Mock()
    scenario.id = 1
    scenario.name = "Test Scenario"
    scenario.endpoint_id = 2
    scenario.validations = [
        Mock(validation_text="status == 200", description="Status check")
    ]

    # Mock endpoint
    endpoint = Mock()
    endpoint.id = 2
    endpoint.method = "GET"
    endpoint.path = "/api/test"
    endpoint.headers_template = {"Content-Type": "application/json"}
    endpoint.query_template = {"limit": "10"}
    endpoint.body_template = None
    endpoint.system_id = 3

    # Mock system
    system = Mock()
    system.id = 3
    system.base_url = "https://api.example.com"
    endpoint.system = system

    return {
        "scenario": scenario,
        "endpoint": endpoint,
        "system": system
    }


class TestRateLimiting:
    """Test rate limiting for CLI endpoints"""

    def test_scenario_definition_rate_limit_within_limit(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test that requests within rate limit are allowed"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.find_auth_config', return_value=None)

        # Make 5 requests (well within the 10/minute limit)
        for i in range(5):
            response = client.get("/scenario/1/definition")
            assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"

    def test_scenario_definition_rate_limit_exceeded(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test that requests exceeding rate limit are rejected"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.find_auth_config', return_value=None)

        # Make 10 requests (at the limit)
        for i in range(10):
            response = client.get("/scenario/1/definition")
            assert response.status_code == 200, f"Request {i+1} within limit failed"

        # 11th request should be rate limited
        response = client.get("/scenario/1/definition")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
        assert "10 requests per minute" in response.json()["detail"]

    def test_endpoint_scenarios_rate_limit_exceeded(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test rate limiting on endpoint scenarios endpoint"""
        # Create proper mock endpoint with scenarios
        endpoint = Mock()
        endpoint.id = 2
        endpoint.system_id = 3
        scenario1 = Mock()
        scenario1.id = 1
        scenario1.name = "Test Scenario"
        scenario1.active = True
        scenario1.validations = [Mock()]
        from datetime import datetime
        scenario1.created_at = datetime(2023, 1, 1)
        endpoint.scenarios = [scenario1]

        # Mock service calls
        mocker.patch('routes.endpoint_routes.get_endpoint_by_id', return_value=endpoint)
        mocker.patch('routes.endpoint_routes.CustomerService.check_user_system_access', return_value=None)

        # Make 10 requests (at the limit)
        for i in range(10):
            response = client.get("/endpoints/2/scenarios")
            assert response.status_code == 200, f"Request {i+1} within limit failed"

        # 11th request should be rate limited
        response = client.get("/endpoints/2/scenarios")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_system_scenarios_rate_limit_exceeded(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test rate limiting on system scenarios endpoint"""
        # Mock service calls
        system = Mock()
        system.id = 3
        system.endpoints = []

        mocker.patch('routes.system_routes.check_system_exists', return_value=system)
        mocker.patch('routes.system_routes.CustomerService.check_user_system_access', return_value=None)

        # Make 10 requests (at the limit)
        for i in range(10):
            response = client.get("/system/3/scenarios")
            assert response.status_code == 200, f"Request {i+1} within limit failed"

        # 11th request should be rate limited
        response = client.get("/system/3/scenarios")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_check_validations_rate_limit_exceeded(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test rate limiting on check validations endpoint"""
        # Create scenario with validations
        scenario = Mock()
        scenario.id = 1
        scenario.endpoint_id = 2
        validation1 = Mock()
        validation1.id = 1
        validation1.validation_text = "status == 200"
        validation1.description = "Check status"
        scenario.validations = [validation1]

        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=scenario)
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        # Mock the GPT validation method
        mock_validation_result = Mock()
        mock_validation_result.model_dump.return_value = {"passed": 1, "failed": 0, "details": []}
        mocker.patch('routes.scenario_routes.gpt.check_validations_with_assistant', return_value=mock_validation_result)

        request_body = {
            "http_status": 200,
            "headers": {"content-type": "application/json"},
            "payload": {"result": "ok"}
        }

        # Make 10 requests (at the limit)
        for i in range(10):
            response = client.post("/scenario/1/check-validations", json=request_body)
            assert response.status_code == 200, f"Request {i+1} within limit failed"

        # 11th request should be rate limited
        response = client.post("/scenario/1/check-validations", json=request_body)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_rate_limit_per_customer_isolation(self, client, mock_scenario_data, mocker):
        """Test that rate limits are isolated per customer"""
        # Clear rate limiter state
        from service.RateLimitService import rate_limiter
        rate_limiter._customer_requests.clear()
        # Create two different customers
        customer1 = Mock()
        customer1.id = "customer_1"
        customer1.email = "customer1@example.com"

        customer2 = Mock()
        customer2.id = "customer_2"
        customer2.email = "customer2@example.com"

        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.find_auth_config', return_value=None)

        # Customer 1 makes 10 requests (at the limit)
        app.dependency_overrides[require_auth] = lambda: customer1
        for i in range(10):
            response = client.get("/scenario/1/definition")
            assert response.status_code == 200

        # Customer 1's 11th request should be rate limited
        response = client.get("/scenario/1/definition")
        assert response.status_code == 429

        # Customer 2 should still be able to make requests
        app.dependency_overrides[require_auth] = lambda: customer2
        response = client.get("/scenario/1/definition")
        assert response.status_code == 200

        # Cleanup
        app.dependency_overrides.pop(require_auth, None)