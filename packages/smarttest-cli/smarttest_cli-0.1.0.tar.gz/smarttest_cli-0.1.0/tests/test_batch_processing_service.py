import pytest
import sys
import os
import json
import asyncio
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
import unittest.mock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.model import Base, ScenarioDB, EndpointDB, SystemDB, EndpointParametersDB, Validation
from database.schemas import BatchProcessingStreamEvent, BatchProcessingScenarioResult, GeneratedValidation
from service.BatchProcessingService import BatchProcessingService


# Setup in-memory SQLite database for testing
@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_system(db_session):
    """Create a sample system in the database"""
    system = SystemDB(
        id=1,
        name="Test API",
        base_url="api.example.com"
    )
    db_session.add(system)
    db_session.commit()
    db_session.refresh(system)
    return system


@pytest.fixture
def sample_endpoint(db_session, sample_system):
    """Create a sample endpoint in the database"""
    endpoint = EndpointDB(
        id=1,
        endpoint="/users/{id}",
        method="GET",
        raw_definition={"path": "/users/{id}", "method": "get"},
        system_id=sample_system.id
    )
    db_session.add(endpoint)
    db_session.commit()
    db_session.refresh(endpoint)
    return endpoint


@pytest.fixture
def sample_scenario(db_session, sample_endpoint):
    """Create a sample scenario in the database"""
    scenario = ScenarioDB(
        id=1,
        name="Get User Success",
        endpoint_id=sample_endpoint.id,
        requires_auth=False,
        auth_error=False
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)
    return scenario


@pytest.fixture
def sample_endpoint_parameters(db_session, sample_endpoint):
    """Create sample endpoint parameters"""
    param = EndpointParametersDB(
        id=1,
        parameter_name="id",
        parameter_type="path",
        default_value="123",
        endpoint_id=sample_endpoint.id
    )
    db_session.add(param)
    db_session.commit()
    db_session.refresh(param)
    return [param]


@pytest.fixture
def batch_service(db_session):
    """Create a BatchProcessingService instance"""
    return BatchProcessingService(db_session, "test_customer_id")


class TestBatchProcessingService:
    """Test cases for BatchProcessingService"""
    
    @pytest.mark.asyncio
    async def test_validate_scenarios_success(self, batch_service, sample_scenario, sample_endpoint, sample_system):
        """Test successful scenario validation"""
        scenario_ids = [sample_scenario.id]
        
        result = await batch_service._validate_scenarios(scenario_ids)
        
        assert len(result) == 1
        assert result[0]["id"] == sample_scenario.id
        assert result[0]["name"] == sample_scenario.name
        assert result[0]["requires_auth"] == sample_scenario.requires_auth
        assert result[0]["endpoint"].id == sample_endpoint.id
        assert result[0]["system"].id == sample_system.id
    
    @pytest.mark.asyncio
    async def test_validate_scenarios_not_found(self, batch_service):
        """Test scenario validation with non-existent scenario"""
        scenario_ids = [999]
        
        result = await batch_service._validate_scenarios(scenario_ids)
        
        assert len(result) == 0
    
    @pytest.mark.asyncio 
    async def test_validate_scenarios_missing_endpoint(self, batch_service, db_session):
        """Test scenario validation with missing endpoint"""
        # Create scenario without endpoint
        scenario = ScenarioDB(
            id=2,
            name="Orphaned Scenario", 
            endpoint_id=999,  # Non-existent endpoint
            requires_auth=False
        )
        db_session.add(scenario)
        db_session.commit()
        
        result = await batch_service._validate_scenarios([scenario.id])
        
        assert len(result) == 0
    
    @pytest.mark.asyncio 
    @patch('service.BatchProcessingService.get_all_by_id')
    @patch('httpx.AsyncClient')
    async def test_execute_http_request_success(self, mock_async_client, mock_get_params, batch_service, sample_scenario, sample_endpoint, sample_system, sample_endpoint_parameters):
        """Test successful HTTP request execution"""
        # Setup mocks
        mock_get_params.return_value = sample_endpoint_parameters
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"id": 123, "name": "John Doe"}
        mock_client_instance = MagicMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create a mock scenario with the required structure
        scenario_data = {
            "id": sample_scenario.id,
            "name": sample_scenario.name,
            "scenario_parameters": [],
            "endpoint": sample_endpoint,
            "system": sample_system
        }
        
        result = await batch_service._execute_http_request(scenario_data)
        
        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["response_body"] == {"id": 123, "name": "John Doe"}
        assert "Content-Type" in result["response_headers"]
        
        # Verify request was called correctly
        mock_client_instance.request.assert_awaited()
        call_args = mock_client_instance.request.call_args
        assert call_args.kwargs["method"] == "GET"
        assert "https://api.example.com/users/123" in call_args.kwargs["url"]
    
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.get_all_by_id')
    @patch('service.BatchProcessingService.build_http_request')
    @patch('httpx.AsyncClient')
    async def test_execute_http_request_failure(self, mock_async_client, mock_build_request, mock_get_params, batch_service, sample_scenario, sample_endpoint, sample_system):
        """Test HTTP request execution failure"""
        # Setup mocks
        mock_get_params.return_value = []
        
        # Mock build_http_request to return a valid request components object
        mock_request_components = MagicMock()
        mock_request_components.url = "/users/123"
        mock_request_components.method = "GET"
        mock_request_components.headers = {}
        mock_request_components.json_body = None
        mock_request_components.query_params = {}
        mock_build_request.return_value = mock_request_components
        
        # Make the actual HTTP request raise an exception
        mock_client_instance = MagicMock()
        mock_client_instance.request = AsyncMock(side_effect=Exception("Network error"))
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        scenario_data = {
            "id": sample_scenario.id,
            "endpoint": sample_endpoint,
            "system": sample_system,
            "scenario_parameters": []
        }
        
        result = await batch_service._execute_http_request(scenario_data)
        
        assert result["success"] is False
        assert "Network error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.evaluate_scenario_with_new_assistant')
    async def test_evaluate_with_llm_success(self, mock_llm, batch_service):
        """Test successful LLM evaluation"""
        # Setup mock
        mock_llm.return_value = {
            "matches_expectation": True,
            "confidence": 0.9,
            "explanation": "Response matches the expected user data structure",
            "generated_validations": [
                {
                    "validation_text": "Response status code should be 200",
                    "description": "Verify successful response",
                    "confidence": 0.95
                }
            ]
        }
        
        # Mock scenario data  
        scenario_dict = {
            "scenario_id": 1,
            "scenario_name": "Test Scenario"
        }
        
        http_result = {
            "status_code": 200,
            "response_headers": {"Content-Type": "application/json"},
            "response_body": {"id": 123, "name": "John Doe"}
        }
        
        result = await batch_service._evaluate_with_llm(scenario_dict, http_result)
        
        assert result["matches_expectation"] is True
        assert result["confidence"] == 0.9
        assert len(result["generated_validations"]) == 1
        
        # Verify LLM was called with correct parameters
        mock_llm.assert_called_once()
        call_args = mock_llm.call_args[1]
        assert call_args["scenario_name"] == "Test Scenario"
        assert call_args["expected_status"] == 200
        assert call_args["actual_status"] == 200
    
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.evaluate_scenario_with_new_assistant')
    async def test_evaluate_with_llm_failure(self, mock_llm, batch_service):
        """Test LLM evaluation failure"""
        # Setup mock to raise exception
        mock_llm.side_effect = Exception("LLM API error")
        
        # Mock scenario data  
        scenario_dict = {
            "scenario_id": 1,
            "scenario_name": "Test Scenario"
        }
        
        http_result = {
            "status_code": 200,
            "response_headers": {},
            "response_body": {}
        }
        
        result = await batch_service._evaluate_with_llm(scenario_dict, http_result)
        
        assert result["matches_expectation"] is False
        assert result["confidence"] == 0.0
        assert "LLM evaluation failed" in result["explanation"]
        assert len(result["generated_validations"]) == 0
    
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.create_validation')
    async def test_save_generated_validations_success(self, mock_create, batch_service):
        """Test successful validation saving"""
        generated_validations = [
            {
                "validation_text": "Response status should be 200",
                "description": "Check success status",
                "confidence": 0.9
            },
            {
                "validation_text": "Response should contain user data", 
                "description": "Verify user fields",
                "confidence": 0.8
            }
        ]
        
        result = await batch_service._save_generated_validations(1, generated_validations)
        
        assert result == 2
        assert mock_create.call_count == 2
    
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.create_validation')
    async def test_save_generated_validations_partial_failure(self, mock_create, batch_service):
        """Test validation saving with partial failures"""
        # Setup mock to fail on second call
        mock_create.side_effect = [None, Exception("DB error")]
        
        generated_validations = [
            {"validation_text": "Test 1", "description": "Desc 1"},
            {"validation_text": "Test 2", "description": "Desc 2"}
        ]
        
        result = await batch_service._save_generated_validations(1, generated_validations)
        
        assert result == 1  # Only one saved successfully
        assert mock_create.call_count == 2
    
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.find_auth_config')
    @patch('service.BatchProcessingService.authenticate_client')
    async def test_get_auth_token_success(self, mock_auth, mock_find, batch_service):
        """Test successful authentication token retrieval"""
        # Setup mocks
        mock_auth_config = MagicMock()
        mock_auth_config.auth_endpoint = "https://auth.example.com/token"
        mock_auth_config.http_method = "POST"
        mock_auth_config.auth_headers = {}
        mock_auth_config.auth_body = {"grant_type": "client_credentials"}
        
        mock_find.return_value = mock_auth_config
        mock_auth.return_value = "test_token_123"
        
        result = await batch_service._get_auth_token(1)
        
        assert result == "test_token_123"
        mock_find.assert_called_once_with(batch_service.db, 1, batch_service.customer_id)
        mock_auth.assert_called_once_with(mock_auth_config, batch_service.customer_id, batch_service.db)

    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.find_auth_config')
    async def test_get_auth_token_no_config(self, mock_find, batch_service):
        """Test authentication token retrieval when no auth config exists"""
        mock_find.return_value = None
        
        result = await batch_service._get_auth_token(1)
        
        assert result is None

    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.find_auth_config')
    @patch('service.BatchProcessingService.authenticate_client')
    async def test_get_auth_token_failure(self, mock_auth, mock_find, batch_service):
        """Test authentication token retrieval failure"""
        mock_auth_config = MagicMock()
        mock_find.return_value = mock_auth_config
        mock_auth.side_effect = Exception("Auth failed")
        
        result = await batch_service._get_auth_token(1)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_apply_authentication_header_success(self, batch_service):
        """Test successful authentication application to headers"""
        # Mock request components
        mock_request_components = MagicMock()
        mock_request_components.headers = {}
        mock_request_components.query_params = {}
        
        # Mock auth config
        mock_auth_config = MagicMock()
        mock_auth_config.token_usage_location = "header"
        mock_auth_config.token_param_name = "Authorization"
        mock_auth_config.token_format = "Bearer {token}"
        
        with patch.object(batch_service, '_get_auth_token', return_value="test_token_123") as mock_get_token, \
             patch('service.BatchProcessingService.find_auth_config', return_value=mock_auth_config):
            
            await batch_service._apply_authentication(1, mock_request_components)
            
            assert mock_request_components.headers["Authorization"] == "Bearer test_token_123"
            mock_get_token.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_apply_authentication_query_success(self, batch_service):
        """Test successful authentication application to query parameters"""
        # Mock request components
        mock_request_components = MagicMock()
        mock_request_components.headers = {}
        mock_request_components.query_params = {}
        
        # Mock auth config for query param auth
        mock_auth_config = MagicMock()
        mock_auth_config.token_usage_location = "query"
        mock_auth_config.token_param_name = "api_key"
        mock_auth_config.token_format = None
        
        with patch.object(batch_service, '_get_auth_token', return_value="test_api_key_456") as mock_get_token, \
             patch('service.BatchProcessingService.find_auth_config', return_value=mock_auth_config):
            
            await batch_service._apply_authentication(1, mock_request_components)
            
            assert mock_request_components.query_params["api_key"] == "test_api_key_456"
            mock_get_token.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_apply_authentication_cookie_success(self, batch_service):
        """Test successful authentication application to cookies"""
        # Mock request components - need to add cookies attribute
        mock_request_components = MagicMock()
        mock_request_components.headers = {}
        mock_request_components.query_params = {}
        mock_request_components.cookies = {}
        
        # Mock auth config for cookie auth
        mock_auth_config = MagicMock()
        mock_auth_config.token_usage_location = "cookie"
        mock_auth_config.token_param_name = "session_token"
        mock_auth_config.token_format = None
        
        with patch.object(batch_service, '_get_auth_token', return_value="session_123") as mock_get_token, \
             patch('service.BatchProcessingService.find_auth_config', return_value=mock_auth_config):
            
            await batch_service._apply_authentication(1, mock_request_components)
            
            assert mock_request_components.cookies["session_token"] == "session_123"
            mock_get_token.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_apply_authentication_no_token(self, batch_service):
        """Test authentication application when no token is available"""
        mock_request_components = MagicMock()
        mock_request_components.headers = {}
        
        with patch.object(batch_service, '_get_auth_token', return_value=None):
            await batch_service._apply_authentication(1, mock_request_components)
            
            # Should not modify request components
            assert mock_request_components.headers == {}

    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.find_auth_config')
    @patch('service.BatchProcessingService.authenticate_client')
    @patch('service.BatchProcessingService.format_token_for_headers')
    async def test_get_auth_headers_success_legacy(self, mock_format, mock_auth, mock_find, batch_service):
        """Test successful authentication header retrieval (legacy method for backward compatibility)"""
        # Setup mocks
        mock_auth_config = MagicMock()
        mock_auth_config.auth_endpoint = "https://auth.example.com/token"
        mock_auth_config.http_method = "POST"
        mock_auth_config.auth_headers = {}
        mock_auth_config.auth_body = {"grant_type": "client_credentials"}
        mock_auth_config.token_source = "body"
        mock_auth_config.token_path = "access_token"
        mock_auth_config.token_format = "Bearer {token}"
        mock_auth_config.header_name_to_use_token = "Authorization"
        
        mock_find.return_value = mock_auth_config
        mock_auth.return_value = "test_token"
        mock_format.return_value = {"Authorization": "Bearer test_token"}
        
        result = await batch_service._get_auth_headers(1)
        
        assert result == {"Authorization": "Bearer test_token"}
        mock_find.assert_called_once_with(batch_service.db, 1, batch_service.customer_id)
        mock_auth.assert_called_once()
        mock_format.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.find_auth_config')
    async def test_get_auth_headers_no_config(self, mock_find, batch_service):
        """Test authentication when no auth config exists"""
        mock_find.return_value = None
        
        result = await batch_service._get_auth_headers(1)
        
        assert result is None
    
    def test_estimate_tokens_used(self, batch_service):
        """Test token usage estimation"""
        # Mock scenario data  
        scenario_dict = {
            "scenario_id": 1,
            "scenario_name": "Test Scenario",
            "description": "A test scenario for user API"
        }
        
        http_result = {
            "response_body": {"id": 123, "name": "John Doe", "email": "john@example.com"}
        }
        
        llm_result = {
            "explanation": "The response matches the expected user data structure with all required fields present",
            "generated_validations": [
                {"validation_text": "Response status should be 200", "description": "Check status"}
            ]
        }
        
        result = batch_service._estimate_tokens_used(scenario_dict, http_result, llm_result)
        
        assert isinstance(result, int)
        assert result > 0
        assert result < 10000  # Reasonable upper bound
    
    def test_create_status_event(self, batch_service):
        """Test status event creation"""
        batch_service.total_scenarios = 10
        batch_service.processed_scenarios = 3
        batch_service.successful_scenarios = 2
        batch_service.failed_scenarios = 1
        batch_service.estimated_tokens_used = 1500
        
        event = batch_service._create_status_event("processing", "Processing scenarios...")
        
        assert event.event_type == "status"
        assert event.data.total_scenarios == 10
        assert event.data.processed_scenarios == 3
        assert event.data.successful_scenarios == 2
        assert event.data.failed_scenarios == 1
        assert event.data.status == "processing"
        assert event.data.message == "Processing scenarios..."
        assert event.data.progress_percent == 30.0  # 3/10 * 100
        assert event.data.estimated_tokens_used == 1500
    
    @pytest.mark.asyncio
    async def test_process_scenarios_batch_end_to_end(self, batch_service, sample_scenario, sample_endpoint, sample_system):
        """Test the complete batch processing workflow"""
        # This is an integration test that mocks external dependencies
        with patch.object(batch_service, '_execute_http_request') as mock_http, \
             patch.object(batch_service, '_evaluate_with_llm') as mock_llm, \
             patch.object(batch_service, '_save_generated_validations') as mock_save:
            
            # Setup mocks
            mock_http.return_value = {
                "success": True,
                "status_code": 200,
                "response_headers": {"Content-Type": "application/json"},
                "response_body": {"id": 123, "name": "John Doe"}
            }
            
            mock_llm.return_value = {
                "matches_expectation": True,
                "confidence": 0.9,
                "explanation": "Response matches expectations",
                "generated_validations": [
                    {"validation_text": "Status should be 200", "description": "Check status"}
                ]
            }
            
            mock_save.return_value = 1
            
            # Process scenarios
            events = []
            async for event in batch_service.process_scenarios_batch([sample_scenario.id]):
                events.append(event)
            
            # Verify events
            assert len(events) >= 4  # starting, processing, scenario_result, completed
            
            # Check event types
            event_types = [event.event_type for event in events]
            assert "status" in event_types
            assert "scenario_result" in event_types
            assert "completed" in event_types
            
            # Check final status
            completed_event = next(e for e in events if e.event_type == "completed")
            assert completed_event.data.successful_scenarios == 1
            assert completed_event.data.failed_scenarios == 0
            assert completed_event.data.status == "completed"
    
    @pytest.mark.asyncio
    async def test_process_scenarios_batch_with_failures(self, batch_service, sample_scenario):
        """Test batch processing with scenario failures"""
        with patch.object(batch_service, '_execute_http_request') as mock_http:
            # Setup mock to fail
            mock_http.side_effect = Exception("Network error")
            
            # Process scenarios
            events = []
            async for event in batch_service.process_scenarios_batch([sample_scenario.id]):
                events.append(event)
            
            # Verify failure handling
            scenario_results = [e for e in events if e.event_type == "scenario_result"]
            assert len(scenario_results) == 1
            assert scenario_results[0].data.status == "failed"
            assert "Network error" in scenario_results[0].data.error_message
            
            # Check final status
            completed_event = next(e for e in events if e.event_type == "completed")
            assert completed_event.data.failed_scenarios == 1
            assert completed_event.data.successful_scenarios == 0

    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.get_all_by_id')
    @patch('service.BatchProcessingService.build_http_request')
    @patch('httpx.AsyncClient')
    async def test_execute_http_request_with_query_auth(self, mock_async_client, mock_build_request, mock_get_params, batch_service, sample_scenario, sample_endpoint, sample_system):
        """Test HTTP request execution with query parameter authentication"""
        # Setup mocks for endpoint parameters
        mock_get_params.return_value = []
        
        # Mock build_http_request to return a valid request components object
        mock_request_components = MagicMock()
        mock_request_components.url = "/users/123"
        mock_request_components.method = "GET"
        mock_request_components.headers = {}
        mock_request_components.json_body = None
        mock_request_components.query_params = {}
        mock_build_request.return_value = mock_request_components
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        
        # Mock httpx client
        mock_client_instance = MagicMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create scenario data requiring auth
        scenario_data = {
            "id": sample_scenario.id,
            "name": sample_scenario.name,
            "requires_auth": True,
            "auth_error": False,
            "scenario_parameters": [],
            "endpoint": sample_endpoint,
            "system": sample_system
        }
        
        # Mock auth config for query param authentication
        with patch.object(batch_service, '_apply_authentication') as mock_apply_auth:
            result = await batch_service._execute_http_request(scenario_data)
            
            # Verify authentication was applied
            mock_apply_auth.assert_called_once_with(sample_system.id, unittest.mock.ANY)
            
            # Verify HTTP request succeeded
            assert result["success"] is True
            assert result["status_code"] == 200
            
            # Verify request was made
            mock_client_instance.request.assert_awaited_once()

    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.get_all_by_id')
    @patch('service.BatchProcessingService.build_http_request')
    @patch('httpx.AsyncClient')
    async def test_execute_http_request_with_cookie_auth_verification(self, mock_async_client, mock_build_request, mock_get_params, batch_service, sample_scenario, sample_endpoint, sample_system):
        """Test HTTP request execution includes cookies when set by authentication"""
        # Setup mocks
        mock_get_params.return_value = []
        
        # Mock build_http_request
        mock_request_components = MagicMock()
        mock_request_components.url = "/users/123"
        mock_request_components.method = "GET"
        mock_request_components.headers = {}
        mock_request_components.json_body = None
        mock_request_components.query_params = {}
        mock_build_request.return_value = mock_request_components
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        mock_client_instance = MagicMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create auth requiring scenario
        scenario_data = {
            "id": sample_scenario.id,
            "name": sample_scenario.name,
            "requires_auth": True,
            "auth_error": False,
            "scenario_parameters": [],
            "endpoint": sample_endpoint,
            "system": sample_system
        }
        
        # Mock authentication that sets cookies
        async def mock_apply_auth(system_id, request_components):
            request_components.cookies = {"session_token": "test_cookie_value"}
            
        with patch.object(batch_service, '_apply_authentication', side_effect=mock_apply_auth):
            await batch_service._execute_http_request(scenario_data)
            
            # Verify cookies were passed to HTTP client
            call_args = mock_client_instance.request.call_args
            assert "cookies" in call_args.kwargs
            assert call_args.kwargs["cookies"] == {"session_token": "test_cookie_value"}