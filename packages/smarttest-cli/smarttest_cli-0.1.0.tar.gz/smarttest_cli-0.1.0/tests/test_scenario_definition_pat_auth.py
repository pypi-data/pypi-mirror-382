"""
Test PAT token authentication for the new scenario definition endpoint
"""

import pytest
from unittest.mock import Mock, MagicMock
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

    # Mock system
    system = Mock()
    system.id = 3
    system.base_url = "https://api.example.com"
    endpoint.system = system
    endpoint.system_id = 3

    return {
        "scenario": scenario,
        "endpoint": endpoint,
        "system": system
    }


@pytest.fixture
def override_auth_dependency(mock_customer):
    """Override FastAPI auth dependency to bypass authentication during tests"""
    app.dependency_overrides[require_auth] = lambda: mock_customer
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_auth, None)


class TestScenarioDefinitionEndpoint:
    """Test the new scenario definition endpoint with PAT token auth"""

    def test_scenario_definition_endpoint_success(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test successful scenario definition retrieval with authentication"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)

        # Make API call
        response = client.get("/scenario/1/definition")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify scenario data
        assert data["scenario"]["id"] == 1
        assert data["scenario"]["name"] == "Test Scenario"

        # Verify request data
        assert data["request"]["method"] == "GET"
        assert data["request"]["resolved_url"] == "https://api.example.com/api/test"
        assert data["request"]["headers"] == {"Content-Type": "application/json"}
        assert data["request"]["query"] == {"limit": "10"}
        assert data["request"]["body"] is None

        # Verify validations
        assert len(data["validations"]) == 1
        assert data["validations"][0]["validation_text"] == "status == 200"
        assert data["validations"][0]["description"] == "Status check"

        # Verify auth_configs structure exists
        assert "auth_configs" in data
        assert isinstance(data["auth_configs"], dict)

    def test_scenario_definition_not_found(self, client, override_auth_dependency, mocker):
        """Test scenario definition with non-existent scenario"""
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=None)

        response = client.get("/scenario/999/definition")

        assert response.status_code == 404
        assert response.json()["detail"] == "Scenario not found"

    def test_scenario_definition_endpoint_not_found(self, client, override_auth_dependency, mock_scenario_data, mocker):
        """Test scenario definition with non-existent endpoint"""
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=None)

        response = client.get("/scenario/1/definition")

        assert response.status_code == 404
        assert "Endpoint not found for scenario 1" in response.json()["detail"]

    def test_scenario_definition_requires_authentication(self, client):
        """Test that the endpoint requires authentication when no override is active"""
        response = client.get("/scenario/1/definition")

        # Should require authentication (401)
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_scenario_definition_with_auth_config(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test scenario definition with auth config references (zero credential exposure)"""
        # Mock auth config
        mock_auth_config = Mock()
        mock_auth_config.id = 456
        mock_auth_config.auth_type = "bearer_token"
        mock_auth_config.token_usage_location = "header"
        mock_auth_config.token_param_name = "Authorization"
        mock_auth_config.token_format = "Bearer {token}"
        mock_auth_config.system_id = 3
        mock_auth_config.auth_endpoint = "https://auth.example.com/token"
        mock_auth_config.http_method = "POST"
        mock_auth_config.token_extraction_instruction = "Extract access_token from JSON response"

        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.find_auth_config', return_value=mock_auth_config)

        # Make API call
        response = client.get("/scenario/1/definition")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify auth config reference is included in request headers
        assert "Authorization" in data["request"]["headers"]
        assert data["request"]["headers"]["Authorization"] == "${auth_config_456}"

        # Verify auth_configs contains metadata (no actual tokens)
        assert "auth_configs" in data
        assert "auth_config_456" in data["auth_configs"]

        auth_config_ref = data["auth_configs"]["auth_config_456"]
        assert auth_config_ref["id"] == "auth_config_456"
        assert auth_config_ref["type"] == "bearer_token"
        assert auth_config_ref["token_param_name"] == "Authorization"
        assert auth_config_ref["token_format"] == "Bearer {token}"
        assert auth_config_ref["token_usage_location"] == "header"
        assert auth_config_ref["system_id"] == 3
        assert auth_config_ref["auth_endpoint"] == "https://auth.example.com/token"
        assert auth_config_ref["http_method"] == "POST"
        assert auth_config_ref["token_extraction_instruction"] == "Extract access_token from JSON response"

        # Verify no actual tokens or credentials are exposed
        assert "token" not in auth_config_ref
        assert "auth_headers" not in auth_config_ref
        assert "auth_body" not in auth_config_ref

    def test_scenario_definition_with_query_auth_config(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test scenario definition with query parameter auth config"""
        # Mock auth config for query parameter
        mock_auth_config = Mock()
        mock_auth_config.id = 789
        mock_auth_config.auth_type = "api_key"
        mock_auth_config.token_usage_location = "query"
        mock_auth_config.token_param_name = "api_key"
        mock_auth_config.token_format = None
        mock_auth_config.system_id = 3
        mock_auth_config.auth_endpoint = "https://auth.example.com/key"
        mock_auth_config.http_method = "GET"
        mock_auth_config.token_extraction_instruction = "Extract api_key from response"

        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.find_auth_config', return_value=mock_auth_config)

        # Make API call
        response = client.get("/scenario/1/definition")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify auth config reference is included in query parameters
        assert "api_key" in data["request"]["query"]
        assert data["request"]["query"]["api_key"] == "${auth_config_789}"

        # Verify auth_configs contains query auth metadata
        auth_config_ref = data["auth_configs"]["auth_config_789"]
        assert auth_config_ref["token_usage_location"] == "query"
        assert auth_config_ref["token_param_name"] == "api_key"
        assert auth_config_ref["token_format"] is None

    def test_scenario_definition_access_control(self, client, override_auth_dependency, mock_scenario_data, mocker):
        """Test that access control is enforced"""
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])

        # Mock access control to raise HTTPException
        from fastapi import HTTPException
        mocker.patch('routes.scenario_routes.check_user_system_access', side_effect=HTTPException(status_code=403, detail="Access denied"))

        response = client.get("/scenario/1/definition")

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied"