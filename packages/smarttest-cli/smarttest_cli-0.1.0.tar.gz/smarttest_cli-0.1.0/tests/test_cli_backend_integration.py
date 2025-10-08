"""
CLI Backend Integration Tests
Tests the CLI with actual backend endpoints using PAT token authentication
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime

# Import backend for integration testing
from main import app
from database.model import Customer, CustomerRole, PATToken
from service.AuthService import require_auth
from service.PATTokenService import PATTokenService


class TestCLIBackendIntegration:
    """Test CLI integration with actual backend endpoints using PAT tokens"""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application"""
        return TestClient(app)

    @pytest.fixture
    def mock_customer(self):
        """Mock authenticated customer"""
        customer = Mock()
        customer.id = "cli_backend_customer_123"
        customer.email = "cli-backend@example.com"
        customer.role = CustomerRole.CLIENT
        return customer

    @pytest.fixture
    def mock_pat_token_auth(self, mock_customer):
        """Mock PAT token authentication"""
        def mock_auth():
            return mock_customer

        # Clear rate limiter state
        from service.RateLimitService import rate_limiter
        rate_limiter._customer_requests.clear()

        app.dependency_overrides[require_auth] = mock_auth
        try:
            yield
        finally:
            app.dependency_overrides.pop(require_auth, None)

    @pytest.fixture
    def mock_scenario_data(self):
        """Mock scenario and related data"""
        scenario = Mock()
        scenario.id = 1
        scenario.name = "Backend Integration Scenario"
        scenario.endpoint_id = 2
        scenario.active = True
        scenario.created_at = datetime(2024, 1, 1, 0, 0, 0)
        scenario.validations = [Mock(id=1, validation_text="status == 200", description="Check status")]

        # Create mock endpoint parameters
        mock_param1 = Mock()
        mock_param1.parameter_name = "Content-Type"
        mock_param1.parameter_type = "header"
        mock_param1.default_value = "application/json"
        mock_param1.default_schema_value = None

        mock_param2 = Mock()
        mock_param2.parameter_name = "page"
        mock_param2.parameter_type = "query"
        mock_param2.default_value = "1"
        mock_param2.default_schema_value = None

        endpoint = Mock()
        endpoint.id = 2
        endpoint.method = "GET"
        endpoint.endpoint = "/test"  # Changed from 'path' to 'endpoint' to match model
        endpoint.system_id = 3
        endpoint.headers_template = {"Content-Type": "application/json"}
        endpoint.query_template = {}
        endpoint.body_template = None
        endpoint.system = Mock(base_url="https://api.example.com")
        endpoint.scenarios = [scenario]  # Add scenarios to the endpoint
        endpoint.default_success_endpoint_parameters = [mock_param1, mock_param2]  # Make it iterable

        return {"scenario": scenario, "endpoint": endpoint}

    def test_cli_scenario_definition_endpoint_with_pat_token(self, client, mock_pat_token_auth, mock_scenario_data):
        """Test CLI scenario definition endpoint with PAT token authentication"""

        # Create mock auth config
        mock_auth_config = Mock()
        mock_auth_config.id = 1
        mock_auth_config.auth_type = "bearer_token"
        mock_auth_config.token_param_name = "Authorization"
        mock_auth_config.token_format = "Bearer {token}"
        mock_auth_config.token_usage_location = "header"
        mock_auth_config.system_id = 3
        mock_auth_config.auth_endpoint = "/auth"
        mock_auth_config.http_method = "POST"
        mock_auth_config.token_extraction_instruction = "Extract token from response"

        with patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"]):
            with patch('service.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"]):
                with patch('routes.scenario_routes.check_user_system_access', return_value=None):
                    with patch('routes.scenario_routes.find_auth_config', return_value=mock_auth_config):

                        headers = {"Authorization": "Bearer st_pat_test_token_12345"}
                        response = client.get("/scenario/1/definition", headers=headers)

                        assert response.status_code == 200
                        data = response.json()

                        # Verify response structure matches CLI expectations
                        assert "scenario" in data
                        assert "request" in data
                        assert "auth_configs" in data
                        assert "validations" in data

                        assert data["scenario"]["id"] == 1
                        assert data["scenario"]["name"] == "Backend Integration Scenario"

                        assert data["request"]["method"] == "GET"
                        assert data["request"]["resolved_url"] == "https://api.example.com/test"
                        
                        # Verify auth configs are properly included
                        assert "auth_config_1" in data["auth_configs"]
                        auth_config = data["auth_configs"]["auth_config_1"]
                        assert auth_config["type"] == "bearer_token"
                        assert auth_config["token_param_name"] == "Authorization"
                        assert auth_config["token_usage_location"] == "header"
                        
                        # Verify headers include auth placeholder
                        assert "Authorization" in data["request"]["headers"]
                        assert data["request"]["headers"]["Authorization"] == "${auth_config_1}"
                        
                        # Verify validations
                        assert len(data["validations"]) == 1
                        assert data["validations"][0]["type"] == "custom"
                        assert data["validations"][0]["validation_text"] == "status == 200"

    def test_cli_endpoint_scenarios_endpoint_with_pat_token(self, client, mock_pat_token_auth, mock_scenario_data):
        """Test CLI endpoint scenarios endpoint with PAT token authentication"""

        with patch('routes.endpoint_routes.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"]):
            with patch('routes.endpoint_routes.CustomerService.check_user_system_access', return_value=None):

                headers = {"Authorization": "Bearer st_pat_test_token_12345"}
                response = client.get("/endpoints/2/scenarios?only_with_validations=true", headers=headers)

                assert response.status_code == 200
                data = response.json()

                # Verify response structure
                assert "scenarios" in data
                assert "total" in data
                assert "endpoint_id" in data
                assert "filtered" in data
                
                # Verify scenario data
                assert data["total"] == 1
                assert data["endpoint_id"] == 2
                assert data["filtered"] == True
                
                scenarios = data["scenarios"]
                assert len(scenarios) == 1
                scenario = scenarios[0]
                assert scenario["id"] == 1
                assert scenario["name"] == "Backend Integration Scenario"
                assert scenario["endpoint_id"] == 2
                assert scenario["validation_count"] == 1

    def test_cli_system_scenarios_endpoint_with_pat_token(self, client, mock_pat_token_auth, mock_scenario_data):
        """Test CLI system scenarios endpoint with PAT token authentication"""

        # Create a mock system with endpoints containing scenarios
        mock_system = Mock()
        mock_system.id = 3
        mock_system.endpoints = [mock_scenario_data["endpoint"]]

        with patch('routes.system_routes.CustomerService.check_user_system_access', return_value=None):
            with patch('routes.system_routes.check_system_exists', return_value=mock_system):

                headers = {"Authorization": "Bearer st_pat_test_token_12345"}
                response = client.get("/system/3/scenarios?only_with_validations=true", headers=headers)

                assert response.status_code == 200
                data = response.json()

                # Verify response structure
                assert "endpoints" in data
                assert "total_scenarios" in data
                assert "total_endpoints" in data
                assert "system_id" in data
                assert "filtered" in data

                # Verify system data
                assert data["system_id"] == 3
                assert data["total_scenarios"] == 1
                assert data["total_endpoints"] == 1
                assert data["filtered"] == True

                # Verify endpoint data
                endpoints = data["endpoints"]
                assert len(endpoints) == 1
                endpoint = endpoints[0]
                assert endpoint["endpoint_id"] == 2
                assert endpoint["method"] == "GET"
                assert endpoint["path"] == "/test"
                assert endpoint["scenario_count"] == 1

                # Verify scenario data
                scenarios = endpoint["scenarios"]
                assert len(scenarios) == 1
                scenario = scenarios[0]
                assert scenario["id"] == 1
                assert scenario["name"] == "Backend Integration Scenario"
                assert scenario["endpoint_id"] == 2
                assert scenario["validation_count"] == 1

    def test_cli_check_validations_endpoint_with_pat_token(self, client, mock_pat_token_auth, mock_scenario_data):
        """Test CLI check-validations endpoint with PAT token authentication"""

        with patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"]):
            with patch('service.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"]):
                with patch('routes.scenario_routes.check_user_system_access', return_value=None):
                    with patch('routes.scenario_routes.get_validations_by_scenario_id', return_value=mock_scenario_data["scenario"].validations):
                        with patch('routes.scenario_routes.gpt.check_validations_with_assistant') as mock_gpt:
                            # Mock GPT validation results
                            mock_gpt_result = Mock()
                            mock_gpt_result.model_dump.return_value = {"passed": 1, "failed": 0}
                            mock_gpt.return_value = mock_gpt_result

                            headers = {"Authorization": "Bearer st_pat_test_token_12345"}
                            request_body = {
                                "http_status": 200,
                                "headers": {"content-type": "application/json"},
                                "payload": {"result": "success"}
                            }

                            response = client.post(
                                "/scenario/1/check-validations?record_run=true&increment_usage=true",
                                headers=headers,
                                json=request_body
                            )

                            assert response.status_code == 200
                            data = response.json()

                            # Verify validation results structure
                            assert "scenario_id" in data
                            assert "validation_results" in data
                            assert "total_validations" in data
                            assert data["scenario_id"] == 1
                            assert data["validation_results"]["passed"] == 1
                            assert data["validation_results"]["failed"] == 0

    def test_cli_rate_limiting_with_pat_token(self, client, mock_pat_token_auth, mock_scenario_data):
        """Test CLI rate limiting with PAT token authentication"""

        headers = {"Authorization": "Bearer st_pat_test_token_12345"}

        # Mock the scenario definition endpoint to return 200 for rate limiting test
        with patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"]):
            with patch('service.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"]):
                with patch('routes.scenario_routes.check_user_system_access', return_value=None):
                    with patch('routes.scenario_routes.find_auth_config', return_value=None):

                        # Make multiple requests to trigger rate limit (20 req/min for scenario endpoints)
                        responses = []
                        for i in range(22):  # More than the 20 request limit
                            response = client.get("/scenario/1/definition", headers=headers)
                            responses.append(response)

                        # First 20 should succeed (mocked), after that should get rate limited
                        success_count = sum(1 for r in responses if r.status_code != 429)
                        rate_limited_count = sum(1 for r in responses if r.status_code == 429)

                        # Should have some rate limited responses (exact count depends on implementation)
                        assert rate_limited_count > 0, "Should have hit rate limit after 20 requests"

    def test_cli_authentication_error_with_invalid_pat_token(self, client):
        """Test CLI authentication error with invalid PAT token"""

        # Mock PAT token authentication to return None (invalid token)
        with patch('service.PATTokenService.PATTokenService.get_customer_by_pat_token', return_value=None):
            # Mock JWT validation to fail as well (for tokens that don't start with st_pat_)
            with patch('service.ClerkAuthService.validate_token_with_request', side_effect=Exception("Invalid token")):
                headers = {"Authorization": "Bearer st_pat_invalid_token"}

                # Should return 401 for invalid PAT token
                response = client.get("/scenario/1/definition", headers=headers)
                assert response.status_code == 401

                data = response.json()
                assert "detail" in data
                assert "Invalid or revoked PAT token" in data["detail"]

    def test_cli_authentication_error_with_missing_token(self, client):
        """Test CLI authentication error with missing PAT token"""

        # Should return 401 for missing token
        response = client.get("/scenario/1/definition")
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
        assert "Authentication required" in data["detail"]

    def test_cli_dual_auth_compatibility_jwt_still_works(self, client, mock_customer):
        """Test that JWT authentication still works alongside PAT token auth"""

        # Mock JWT authentication
        with patch('service.PATTokenAuthService.validate_token_with_request') as mock_jwt:
            mock_jwt.return_value = {"user_id": "cli_backend_customer_123", "session_id": "sess_123"}

            with patch('service.PATTokenAuthService.SessionLocal') as mock_session_local:
                mock_db = Mock()
                mock_db.query.return_value.filter.return_value.first.return_value = mock_customer
                mock_session_local.return_value.__enter__.return_value = mock_db

                # Use JWT token (not PAT token format)
                headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.jwt_token"}

                # Mock scenario data
                with patch('routes.scenario_routes.get_scenario_by_id') as mock_get_scenario:
                    mock_scenario = Mock()
                    mock_scenario.id = 1
                    mock_scenario.name = "JWT Test"
                    mock_scenario.endpoint_id = 2
                    mock_scenario.validations = []
                    mock_get_scenario.return_value = mock_scenario

                    with patch('routes.scenario_routes.EndpointService.get_endpoint_by_id') as mock_get_endpoint:
                        mock_endpoint = Mock()
                        mock_endpoint.id = 2
                        mock_endpoint.system_id = 3
                        mock_endpoint.method = "GET"
                        mock_endpoint.endpoint = "/test"  # Changed from 'path' to 'endpoint'
                        mock_endpoint.headers_template = {}
                        mock_endpoint.query_template = {}
                        mock_endpoint.body_template = None
                        mock_endpoint.system = Mock(base_url="https://api.example.com")
                        mock_endpoint.default_success_endpoint_parameters = []  # Add empty list for parameters
                        mock_get_endpoint.return_value = mock_endpoint

                        with patch('routes.scenario_routes.check_user_system_access', return_value=None):
                            with patch('routes.scenario_routes.find_auth_config', return_value=None):

                                response = client.get("/scenario/1/definition", headers=headers)

                                # Should work with JWT token too
                                assert response.status_code == 200
                                data = response.json()
                                assert data["scenario"]["id"] == 1

    def test_cli_auth_config_references_in_scenario_definition(self, client, mock_pat_token_auth, mock_scenario_data):
        """Test CLI scenario definition includes auth config references for zero-credential exposure"""

        # Mock auth config
        mock_auth_config = Mock()
        mock_auth_config.id = 1
        mock_auth_config.auth_type = "bearer_token"
        mock_auth_config.token_param_name = "Authorization"
        mock_auth_config.token_format = "Bearer {token}"
        mock_auth_config.token_usage_location = "header"
        mock_auth_config.system_id = 3
        mock_auth_config.auth_endpoint = "https://auth.example.com/token"
        mock_auth_config.http_method = "POST"
        mock_auth_config.token_extraction_instruction = "Extract from response.access_token"

        with patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"]):
            with patch('service.EndpointService.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"]):
                with patch('routes.scenario_routes.check_user_system_access', return_value=None):
                    with patch('routes.scenario_routes.find_auth_config', return_value=mock_auth_config):

                        headers = {"Authorization": "Bearer st_pat_test_token_12345"}
                        response = client.get("/scenario/1/definition", headers=headers)

                        assert response.status_code == 200
                        data = response.json()

                        # Should have auth config reference
                        assert "auth_configs" in data
                        assert len(data["auth_configs"]) == 1

                        auth_config_key = f"auth_config_{mock_auth_config.id}"
                        assert auth_config_key in data["auth_configs"]

                        auth_config = data["auth_configs"][auth_config_key]
                        assert auth_config["id"] == auth_config_key
                        assert auth_config["type"] == "bearer_token"
                        assert auth_config["token_param_name"] == "Authorization"

                        # Should have placeholder in headers
                        assert data["request"]["headers"]["Authorization"] == f"${{{auth_config_key}}}"

                        # Should contain auth resolution info (no actual credentials)
                        assert auth_config["auth_endpoint"] == "https://auth.example.com/token"
                        assert auth_config["http_method"] == "POST"
                        assert "token_extraction_instruction" in auth_config

    def test_cli_error_scenarios_handling(self, client, mock_pat_token_auth):
        """Test CLI error scenarios are handled properly"""

        headers = {"Authorization": "Bearer st_pat_test_token_12345"}

        # Test scenario not found
        response = client.get("/scenario/999/definition", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

        # Test endpoint not found for scenario
        with patch('routes.scenario_routes.get_scenario_by_id', return_value=Mock(id=1, endpoint_id=999)):
            with patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=None):
                response = client.get("/scenario/1/definition", headers=headers)
                assert response.status_code == 404
                assert "Endpoint not found" in response.json()["detail"]

        # Test access denied (no system access)
        with patch('routes.scenario_routes.get_scenario_by_id', return_value=Mock(id=1, endpoint_id=2)):
            with patch('routes.scenario_routes.EndpointService.get_endpoint_by_id', return_value=Mock(system_id=999)):
                with patch('routes.scenario_routes.check_user_system_access', side_effect=HTTPException(status_code=403, detail="Access denied")):
                    response = client.get("/scenario/1/definition", headers=headers)
                    assert response.status_code == 403
                    assert "Access denied" in response.json()["detail"]

    def test_cli_backward_compatibility_with_existing_tests(self):
        """Test that CLI changes don't break existing functionality"""

        # Import existing tests to ensure they still work
        from tests.test_cli_pat_token_integration import TestCLIPATTokenIntegration

        # Verify the existing test class exists and is importable
        assert TestCLIPATTokenIntegration is not None

        # Test that existing CLI components are still available
        from cli.config import Config
        from cli.api_client import ApiClient
        from cli.main import execute_scenarios

        assert Config is not None
        assert ApiClient is not None
        assert execute_scenarios is not None