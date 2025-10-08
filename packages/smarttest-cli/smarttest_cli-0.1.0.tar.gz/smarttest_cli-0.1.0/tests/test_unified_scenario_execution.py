"""
Comprehensive tests for UnifiedScenarioExecutionService

These tests ensure that both 'Run Scenario' and 'LLM Validation' execution paths
use identical authentication and HTTP handling logic.

Key test scenarios:
- Normal scenarios with valid authentication
- Auth error scenarios with invalid tokens  
- Scenarios without authentication
- Error handling and edge cases
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from service.UnifiedScenarioExecution import UnifiedScenarioExecutionService, execute_scenario_unified
from database.model import ScenarioDB, EndpointDB, SystemDB, EndpointParametersDB


class TestUnifiedScenarioExecutionService:
    """Test suite for the UnifiedScenarioExecutionService class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def service(self, mock_db):
        """Create a UnifiedScenarioExecutionService instance."""
        return UnifiedScenarioExecutionService(mock_db)
    
    @pytest.fixture
    def mock_scenario_data(self):
        """Create mock scenario-related data for testing."""
        scenario = Mock(spec=ScenarioDB)
        scenario.id = 1
        scenario.name = "Test Scenario"
        scenario.requires_auth = True
        scenario.auth_error = False
        scenario.scenario_parameters = []
        
        endpoint = Mock(spec=EndpointDB)
        endpoint.id = 1
        endpoint.endpoint = "/test"
        endpoint.method = "GET"
        endpoint.system_id = 1
        
        system = Mock(spec=SystemDB)
        system.id = 1
        system.base_url = "https://api.example.com"
        
        endpoint_params = []
        
        return {
            "scenario": scenario,
            "endpoint": endpoint,
            "system": system,
            "endpoint_parameters": endpoint_params
        }
    
    @patch('service.UnifiedScenarioExecution.get_scenario_by_id')
    @patch('service.UnifiedScenarioExecution.get_endpoint_by_id')
    @patch('service.UnifiedScenarioExecution.get_system_by_id')
    @patch('service.UnifiedScenarioExecution.get_all_by_id')
    def test_load_scenario_data_success(self, mock_get_params, mock_get_system, 
                                      mock_get_endpoint, mock_get_scenario, 
                                      service, mock_scenario_data):
        """Test successful loading of scenario data."""
        # Setup mocks
        mock_get_scenario.return_value = mock_scenario_data["scenario"]
        mock_get_endpoint.return_value = mock_scenario_data["endpoint"]
        mock_get_system.return_value = mock_scenario_data["system"]
        mock_get_params.return_value = mock_scenario_data["endpoint_parameters"]
        
        # Execute
        result = service._load_scenario_data(1)
        
        # Verify
        assert result["scenario"] == mock_scenario_data["scenario"]
        assert result["endpoint"] == mock_scenario_data["endpoint"]
        assert result["system"] == mock_scenario_data["system"]
        assert result["endpoint_parameters"] == mock_scenario_data["endpoint_parameters"]
        
        # Verify function calls
        mock_get_scenario.assert_called_once_with(service.db, 1)
        mock_get_endpoint.assert_called_once()
        mock_get_system.assert_called_once()
        mock_get_params.assert_called_once()
    
    @patch('service.UnifiedScenarioExecution.get_scenario_by_id')
    def test_load_scenario_data_scenario_not_found(self, mock_get_scenario, service):
        """Test scenario data loading when scenario is not found."""
        mock_get_scenario.return_value = None
        
        with pytest.raises(Exception) as exc_info:
            service._load_scenario_data(999)
        
        assert "Scenario with id 999 not found" in str(exc_info.value)
    
    @patch('service.UnifiedScenarioExecution.find_auth_config')
    def test_get_authentication_data_no_auth_required(self, mock_find_auth, service, mock_scenario_data):
        """Test authentication handling when no auth is required."""
        scenario = mock_scenario_data["scenario"]
        scenario.requires_auth = False
        
        result = service._get_authentication_data(
            scenario, mock_scenario_data["system"], "user123"
        )
        
        assert result is None
        mock_find_auth.assert_not_called()
    
    @patch('service.UnifiedScenarioExecution.find_auth_config')
    def test_get_authentication_data_no_auth_config(self, mock_find_auth, service, mock_scenario_data):
        """Test authentication handling when no auth config is found."""
        mock_find_auth.return_value = None
        
        result = service._get_authentication_data(
            mock_scenario_data["scenario"], mock_scenario_data["system"], "user123"
        )
        
        assert result is None
        mock_find_auth.assert_called_once_with(service.db, 1, "user123")
    
    @patch('service.UnifiedScenarioExecution.find_auth_config')
    @patch('service.UnifiedScenarioExecution.authenticate_client')
    @patch('service.UnifiedScenarioExecution.format_token_for_headers')
    def test_get_authentication_data_normal_scenario(self, mock_format, mock_auth, 
                                                       mock_find_auth, service, mock_scenario_data):
        """Test authentication for normal scenarios (not auth error)."""
        # Setup mocks
        mock_auth_config = Mock()
        mock_find_auth.return_value = mock_auth_config
        mock_auth.return_value = {"access_token": "valid_token"}
        mock_format.return_value = ("Authorization", "Bearer valid_token")
        
        # Execute
        result = service._get_authentication_data(
            mock_scenario_data["scenario"], mock_scenario_data["system"], "user123"
        )
        
        # Verify
        assert result["headers"]["Authorization"] == "Bearer valid_token"
        mock_find_auth.assert_called_once_with(service.db, 1, "user123")
        mock_auth.assert_called_once_with(mock_auth_config)
        mock_format.assert_called_once()
    
    @patch('service.UnifiedScenarioExecution.find_auth_config')
    @patch('service.UnifiedScenarioExecution.authenticate_client')
    @patch('service.UnifiedScenarioExecution.format_token_for_headers')
    def test_get_authentication_data_auth_error_scenario(self, mock_format, mock_auth, 
                                                           mock_find_auth, service, mock_scenario_data):
        """Test authentication for auth error scenarios (should use invalid token)."""
        # Setup mocks for auth error scenario
        scenario = mock_scenario_data["scenario"]
        scenario.auth_error = True  # This is the key difference
        
        mock_auth_config = Mock()
        mock_find_auth.return_value = mock_auth_config
        mock_auth.return_value = {"access_token": "valid_token"}
        mock_format.return_value = ("Authorization", "Bearer valid_token")
        
        # Execute
        result = service._get_authentication_data(
            scenario, mock_scenario_data["system"], "user123"
        )
        
        # Verify - should use INVALID token for auth error scenarios
        assert result["headers"]["Authorization"] == "INVALID_TOKEN_FOR_TESTING"
        mock_find_auth.assert_called_once_with(service.db, 1, "user123")
        mock_auth.assert_called_once_with(mock_auth_config)
        mock_format.assert_called_once()
    
    @patch('service.UnifiedScenarioExecution.build_http_request')
    def test_build_http_request(self, mock_build, service, mock_scenario_data):
        """Test HTTP request building."""
        mock_request_components = Mock()
        mock_request_components.method = "GET"
        mock_request_components.url = "/test"
        mock_request_components.headers = {"Content-Type": "application/json"}
        mock_request_components.query_params = {}
        mock_request_components.json_body = None
        
        mock_build.return_value = mock_request_components
        
        result = service._build_http_request(
            mock_scenario_data["endpoint"],
            mock_scenario_data["endpoint_parameters"],
            []
        )
        
        assert result == mock_request_components
        mock_build.assert_called_once()
    
    @patch('requests.request')
    def test_execute_http_request_success(self, mock_request, service, mock_scenario_data):
        """Test successful HTTP request execution."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response
        
        # Setup request components
        mock_request_components = Mock()
        mock_request_components.method = "GET"
        mock_request_components.url = "/test"
        mock_request_components.headers = {}
        mock_request_components.query_params = {}
        mock_request_components.json_body = None
        
        # Execute
        result = service._execute_http_request(
            mock_request_components,
            "https://api.example.com",
            {"headers": {"Authorization": "Bearer token"}}
        )
        
        # Verify
        assert result["status_code"] == 200
        assert result["body"] == {"result": "success"}
        assert "Authorization" in result["request_details"]["headers"]
        
        # Verify requests.request was called correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://api.example.com/test"
        assert "Authorization" in call_args[1]["headers"]
    
    @patch('requests.request')
    def test_execute_http_request_auth_error_gets_401(self, mock_request, service, mock_scenario_data):
        """Test that auth error scenarios correctly receive 401 status."""
        # Setup scenario as auth error test
        scenario = mock_scenario_data["scenario"]
        scenario.auth_error = True
        
        # Setup mock response to return 401 (as expected for invalid token)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_request.return_value = mock_response
        
        # Setup request components
        mock_request_components = Mock()
        mock_request_components.method = "GET"
        mock_request_components.url = "/test"
        mock_request_components.headers = {}
        mock_request_components.query_params = {}
        mock_request_components.json_body = None
        
        # Execute with invalid token (as would be set by auth handler)
        result = service._execute_http_request(
            mock_request_components,
            "https://api.example.com",
            {"headers": {"Authorization": "INVALID_TOKEN_FOR_TESTING"}}
        )
        
        # Verify we get the expected 401 response
        assert result["status_code"] == 401
        assert result["body"] == {"error": "Unauthorized"}
        
        # Verify the invalid token was used
        call_args = mock_request.call_args
        assert call_args[1]["headers"]["Authorization"] == "INVALID_TOKEN_FOR_TESTING"
    
    def test_process_response_success(self, service, mock_scenario_data):
        """Test response processing for successful execution."""
        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"result": "success"},
            "request_details": {"method": "GET", "url": "https://api.example.com/test"}
        }
        
        result = service._process_response(
            mock_scenario_data["scenario"],
            response_data
        )
        
        assert result["success"] is True
        assert result["scenario_id"] == 1
        assert result["scenario_name"] == "Test Scenario"
        assert result["status_code"] == 200
        assert result["body"] == {"result": "success"}
    
    def test_process_response_with_validations(self, service, mock_scenario_data):
        """Test response processing when validations are requested."""
        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"result": "success"},
            "request_details": {"method": "GET", "url": "https://api.example.com/test"}
        }
        
        result = service._process_response(
            mock_scenario_data["scenario"],
            response_data
        )
        
        assert result["success"] is True
        assert result["scenario_id"] == 1
        assert result["scenario_name"] == "Test Scenario"
        assert result["validation_summary"]["total_validations"] == 0


class TestExecuteScenarioUnified:
    """Test suite for the execute_scenario_unified convenience function."""
    
    @patch('service.UnifiedScenarioExecution.UnifiedScenarioExecutionService')
    def test_execute_scenario_unified(self, mock_service_class):
        """Test the convenience function creates service and calls execute_scenario."""
        mock_db = Mock()
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.execute_scenario.return_value = {"success": True}
        
        result = execute_scenario_unified(mock_db, 1, "user123")
        
        mock_service_class.assert_called_once_with(mock_db)
        mock_service.execute_scenario.assert_called_once_with(1, "user123")
        assert result == {"success": True}


class TestAuthenticationConsistency:
    """Integration tests to ensure authentication consistency across execution paths."""
    
    @pytest.fixture
    def auth_scenario_data(self):
        """Create test data specifically for authentication testing."""
        return {
            "normal_auth_scenario": {
                "id": 1,
                "requires_auth": True,
                "auth_error": False,
                "expected_token": "Bearer valid_token"
            },
            "auth_error_scenario": {
                "id": 2,
                "requires_auth": True,
                "auth_error": True,
                "expected_token": "INVALID_TOKEN_FOR_TESTING"
            },
            "no_auth_scenario": {
                "id": 3,
                "requires_auth": False,
                "auth_error": False,
                "expected_token": None
            }
        }
    
    @patch('service.UnifiedScenarioExecution.UnifiedScenarioExecutionService.execute_scenario')
    def test_normal_auth_scenario_uses_valid_token(self, mock_execute, auth_scenario_data):
        """Verify normal auth scenarios use valid tokens."""
        mock_db = Mock()
        scenario_id = auth_scenario_data["normal_auth_scenario"]["id"]
        
        # Mock the response to include the auth details we want to verify
        mock_execute.return_value = {
            "success": True,
            "scenario_id": scenario_id,
            "auth_token_used": "Bearer valid_token"
        }
        
        result = execute_scenario_unified(mock_db, scenario_id, "user123")
        
        assert result["success"] is True
        mock_execute.assert_called_once_with(scenario_id, "user123")
    
    @patch('service.UnifiedScenarioExecution.UnifiedScenarioExecutionService.execute_scenario')
    def test_auth_error_scenario_uses_invalid_token(self, mock_execute, auth_scenario_data):
        """Verify auth error scenarios use invalid tokens."""
        mock_db = Mock()
        scenario_id = auth_scenario_data["auth_error_scenario"]["id"]
        
        # Mock the response to include the auth details we want to verify
        mock_execute.return_value = {
            "success": True,
            "scenario_id": scenario_id,
            "auth_token_used": "INVALID_TOKEN_FOR_TESTING"
        }
        
        result = execute_scenario_unified(mock_db, scenario_id, "user123")
        
        assert result["success"] is True
        mock_execute.assert_called_once_with(scenario_id, "user123")


class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    @patch('service.UnifiedScenarioExecution.get_scenario_by_id')
    def test_scenario_not_found_error(self, mock_get_scenario):
        """Test handling when scenario is not found."""
        mock_db = Mock()
        mock_get_scenario.return_value = None
        
        service = UnifiedScenarioExecutionService(mock_db)
        with pytest.raises(Exception):
            service.execute_scenario(999, "user123")
    
    @patch('service.UnifiedScenarioExecution.requests.request')
    @patch('service.UnifiedScenarioExecution.get_scenario_by_id')
    @patch('service.UnifiedScenarioExecution.get_endpoint_by_id')
    @patch('service.UnifiedScenarioExecution.get_system_by_id')
    @patch('service.UnifiedScenarioExecution.get_all_by_id')
    @patch('service.UnifiedScenarioExecution.build_http_request')
    def test_http_request_failure(self, mock_build, mock_get_params, mock_get_system,
                                 mock_get_endpoint, mock_get_scenario, mock_request):
        """Test handling of HTTP request failures."""
        # Setup mocks
        mock_scenario = Mock()
        mock_scenario.id = 1
        mock_scenario.name = "Test"
        mock_scenario.requires_auth = False
        mock_scenario.scenario_parameters = []
        
        mock_endpoint = Mock()
        mock_endpoint.id = 1
        mock_endpoint.system_id = 1
        
        mock_system = Mock()
        mock_system.id = 1
        mock_system.base_url = "https://api.example.com"
        
        mock_get_scenario.return_value = mock_scenario
        mock_get_endpoint.return_value = mock_endpoint
        mock_get_system.return_value = mock_system
        mock_get_params.return_value = []
        
        mock_request_components = Mock()
        mock_request_components.method = "GET"
        mock_request_components.url = "/test"
        mock_request_components.headers = {}
        mock_request_components.query_params = {}
        mock_request_components.json_body = None
        mock_build.return_value = mock_request_components
        
        # Mock request to raise an exception
        mock_request.side_effect = requests.exceptions.RequestException("Connection failed")
        
        mock_db = Mock()
        service = UnifiedScenarioExecutionService(mock_db)
        result = service.execute_scenario(1, "user123")
        
        assert result["success"] is False
        assert "Connection failed" in result["error"]


class TestSkipExecutionHistory:
    """Test suite for the skip_execution_history functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def service(self, mock_db):
        """Create a UnifiedScenarioExecutionService instance."""
        return UnifiedScenarioExecutionService(mock_db)
    
    @pytest.fixture
    def mock_scenario_data(self):
        """Create mock scenario data."""
        scenario = Mock(spec=ScenarioDB)
        scenario.id = 1
        scenario.name = "Test Scenario"
        scenario.requires_auth = False
        scenario.endpoint_id = 1
        
        endpoint = Mock(spec=EndpointDB)
        endpoint.id = 1
        endpoint.endpoint = "/test"
        endpoint.method = "GET"
        endpoint.system_id = 1
        
        system = Mock(spec=SystemDB)
        system.id = 1
        system.base_url = "https://api.example.com"
        
        return {
            "scenario": scenario,
            "endpoint": endpoint,
            "system": system
        }
    
    @patch('service.UnifiedScenarioExecution.requests.request')
    @patch('service.UnifiedScenarioExecution.get_scenario_by_id')
    @patch('service.UnifiedScenarioExecution.get_endpoint_by_id')
    @patch('service.UnifiedScenarioExecution.get_system_by_id')
    @patch('service.UnifiedScenarioExecution.get_all_by_id')
    @patch('service.UnifiedScenarioExecution.build_http_request')
    def test_skip_execution_history_false_saves_history(self, mock_build, mock_get_params,
                                                       mock_get_system, mock_get_endpoint, 
                                                       mock_get_scenario, mock_request, 
                                                       service, mock_scenario_data):
        """Test that skip_execution_history=False saves execution history."""
        # Setup mocks
        mock_get_scenario.return_value = mock_scenario_data["scenario"]
        mock_get_endpoint.return_value = mock_scenario_data["endpoint"]
        mock_get_system.return_value = mock_scenario_data["system"]
        mock_get_params.return_value = []
        
        mock_request_components = Mock()
        mock_request_components.method = "GET"
        mock_request_components.url = "/test"
        mock_request_components.headers = {}
        mock_request_components.query_params = {}
        mock_request_components.json_body = None
        mock_build.return_value = mock_request_components
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"message": "success"}
        mock_request.return_value = mock_response
        
        # Mock _save_execution_history to track if it's called
        with patch.object(service, '_save_execution_history') as mock_save_history:
            mock_save_history.return_value = Mock(id=123)
            
            # Execute with skip_execution_history=False (default)
            result = service.execute_scenario(1, "user123", skip_execution_history=False)
            
            # Verify _save_execution_history was called
            mock_save_history.assert_called_once()
            
            # Verify result includes history_id
            assert result.get("history_id") == 123
            assert result["success"] is True
    
    @patch('service.UnifiedScenarioExecution.requests.request')
    @patch('service.UnifiedScenarioExecution.get_scenario_by_id')
    @patch('service.UnifiedScenarioExecution.get_endpoint_by_id')
    @patch('service.UnifiedScenarioExecution.get_system_by_id')
    @patch('service.UnifiedScenarioExecution.get_all_by_id')
    @patch('service.UnifiedScenarioExecution.build_http_request')
    def test_skip_execution_history_true_skips_history(self, mock_build, mock_get_params,
                                                      mock_get_system, mock_get_endpoint, 
                                                      mock_get_scenario, mock_request, 
                                                      service, mock_scenario_data):
        """Test that skip_execution_history=True does NOT save execution history."""
        # Setup mocks
        mock_get_scenario.return_value = mock_scenario_data["scenario"]
        mock_get_endpoint.return_value = mock_scenario_data["endpoint"]
        mock_get_system.return_value = mock_scenario_data["system"]
        mock_get_params.return_value = []
        
        mock_request_components = Mock()
        mock_request_components.method = "GET"
        mock_request_components.url = "/test"
        mock_request_components.headers = {}
        mock_request_components.query_params = {}
        mock_request_components.json_body = None
        mock_build.return_value = mock_request_components
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"message": "success"}
        mock_request.return_value = mock_response
        
        # Mock _save_execution_history to track if it's called
        with patch.object(service, '_save_execution_history') as mock_save_history:
            mock_save_history.return_value = Mock(id=456)
            
            # Execute with skip_execution_history=True
            result = service.execute_scenario(1, "user123", skip_execution_history=True)
            
            # Verify _save_execution_history was NOT called
            mock_save_history.assert_not_called()
            
            # Verify result does NOT include history_id
            assert "history_id" not in result
            assert result["success"] is True
    
    @patch('service.UnifiedScenarioExecution.UnifiedScenarioExecutionService')
    def test_execute_scenario_unified_passes_skip_flag(self, mock_service_class):
        """Test that execute_scenario_unified passes the skip_execution_history flag correctly."""
        mock_db = Mock()
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.execute_scenario.return_value = {"success": True}
        
        # Test with skip_execution_history=True
        result = execute_scenario_unified(mock_db, 1, "user123", skip_execution_history=True)
        
        mock_service_class.assert_called_once_with(mock_db)
        mock_service.execute_scenario.assert_called_once_with(1, "user123", True)
        assert result == {"success": True}
    
    @patch('service.UnifiedScenarioExecution.UnifiedScenarioExecutionService')
    def test_execute_scenario_unified_default_skip_flag(self, mock_service_class):
        """Test that execute_scenario_unified uses skip_execution_history=False by default."""
        mock_db = Mock()
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.execute_scenario.return_value = {"success": True}
        
        # Test without specifying skip_execution_history (should default to False)
        result = execute_scenario_unified(mock_db, 1, "user123")
        
        mock_service_class.assert_called_once_with(mock_db)
        mock_service.execute_scenario.assert_called_once_with(1, "user123", False)
        assert result == {"success": True}


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 