import pytest
import sys
import os
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from service.ClerkAuthService import require_client_or_admin
from database.model import Base, ScenarioDB, EndpointDB, SystemDB
from database.schemas import BatchProcessingRequest, BatchProcessingStreamEvent, BatchProcessingScenarioResult


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
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def mock_customer():
    """Mock authenticated customer"""
    return MagicMock(id="test_customer_id", email="test@example.com")


@pytest.fixture
def override_auth_dependency(mock_customer):
    """Override FastAPI auth dependency to bypass Clerk during tests"""
    app.dependency_overrides[require_client_or_admin] = lambda: mock_customer
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_client_or_admin, None)

@pytest.fixture
def sample_scenarios(db_session):
    """Create sample scenarios in the database"""
    # Create system
    system = SystemDB(id=1, name="Test API", base_url="api.example.com")
    db_session.add(system)
    
    # Create endpoint
    endpoint = EndpointDB(
        id=1,
        endpoint="/users/{id}",
        method="GET",
        raw_definition={"path": "/users/{id}"},
        system_id=1
    )
    db_session.add(endpoint)
    
    # Create scenarios
    scenarios = [
        ScenarioDB(
            name="Test Scenario 1",
            endpoint_id=1,
            requires_auth=False
        ),
        ScenarioDB(
            name="Test Scenario 2", 
            endpoint_id=1,
            requires_auth=False
        ),
        ScenarioDB(
            name="Test Scenario 3",
            endpoint_id=1,
            requires_auth=False
        )
    ]
    
    for scenario in scenarios:
        db_session.add(scenario)
    
    db_session.commit()
    return scenarios


class TestBatchProcessingRoutes:
    """Test cases for batch processing API routes"""
    
    @patch('routes.batch_processing_routes.require_client_or_admin')
    @patch('routes.batch_processing_routes.SubscriptionService.get_usage_limits')
    @patch('routes.batch_processing_routes.SubscriptionService.increment_usage')
    @patch('routes.batch_processing_routes.BatchProcessingService')
    def test_process_scenarios_batch_success(self, mock_service_class, mock_increment, mock_usage, mock_auth, client, mock_customer, sample_scenarios, override_auth_dependency):
        """Test successful batch processing request"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 95
        mock_usage.return_value = mock_usage_response
        
        mock_increment.return_value = True
        
        # Mock service instance and its async generator
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Create mock events for the stream
        mock_events = [
            BatchProcessingStreamEvent(
                event_type="status",
                data={"status": "starting", "message": "Initializing..."}
            ),
            BatchProcessingStreamEvent(
                event_type="scenario_result",
                data={
                    "scenario_id": 1,
                    "scenario_name": "Get User Success", 
                    "status": "completed",
                    "matches_expectation": True,
                    "saved_validations_count": 3
                }
            ),
            BatchProcessingStreamEvent(
                event_type="completed",
                data={"status": "completed", "successful_scenarios": 1}
            )
        ]
        
        async def mock_generator():
            for event in mock_events:
                yield event
        
        mock_service.process_scenarios_batch.return_value = mock_generator()
        
        # Make request
        request_data = {"scenario_ids": [1, 2]}
        response = client.post(
            "/batch-processing/scenarios/process",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        assert "Cache-Control" in response.headers
        assert response.headers["Cache-Control"] == "no-cache"
        
        # Verify service was called correctly
        mock_service_class.assert_called_once()
        mock_service.process_scenarios_batch.assert_called_once_with([1, 2])
        
        # Verify usage tracking
        mock_increment.assert_called_once_with(mock_customer.db, mock_customer.id, "runs_executed", 2)
    
    @patch('routes.batch_processing_routes.require_client_or_admin')
    @patch('routes.batch_processing_routes.SubscriptionService.get_usage_limits')
    def test_process_scenarios_batch_usage_limit_exceeded(self, mock_usage, mock_auth, client, mock_customer, override_auth_dependency):
        """Test batch processing when usage limits are exceeded"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 98
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 2
        mock_usage.return_value = mock_usage_response
        
        # Request more scenarios than remaining limit
        request_data = {"scenario_ids": [1, 2, 3, 4, 5]}  # 5 scenarios > 2 remaining
        
        response = client.post(
            "/batch-processing/scenarios/process",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 403
        response_data = response.json()
        assert "Run execution limit would be exceeded" in response_data["detail"]
        assert "5 scenarios" in response_data["detail"]
        assert "2 runs remaining" in response_data["detail"]
    
    @patch('routes.batch_processing_routes.require_client_or_admin')
    @patch('routes.batch_processing_routes.SubscriptionService.get_usage_limits')
    def test_process_scenarios_batch_no_usage_limits(self, mock_usage, mock_auth, client, mock_customer, override_auth_dependency):
        """Test batch processing when usage limits cannot be retrieved"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        mock_usage.return_value = None  # Unable to get usage limits
        
        request_data = {"scenario_ids": [1, 2]}
        
        response = client.post(
            "/batch-processing/scenarios/process",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 403
        response_data = response.json()
        assert "Unable to verify subscription limits" in response_data["detail"]
    
    def test_process_scenarios_batch_invalid_request(self, client, override_auth_dependency):
        """Test batch processing with invalid request data"""
        # Test with empty scenario list
        response = client.post(
            "/batch-processing/scenarios/process",
            json={"scenario_ids": []},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test with too many scenarios
        response = client.post(
            "/batch-processing/scenarios/process", 
            json={"scenario_ids": list(range(1, 52))},  # 51 scenarios > max of 50
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test with invalid JSON
        response = client.post(
            "/batch-processing/scenarios/process",
            data="invalid json",
            headers={"Authorization": "Bearer test_token", "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_process_scenarios_batch_unauthorized(self, client):
        """Test batch processing without authentication"""
        request_data = {"scenario_ids": [1, 2]}
        
        response = client.post(
            "/batch-processing/scenarios/process",
            json=request_data
        )
        
        assert response.status_code == 401 or response.status_code == 403
    
    @patch('routes.batch_processing_routes.require_client_or_admin')
    @patch('routes.batch_processing_routes.SubscriptionService.get_usage_limits')
    @patch('routes.batch_processing_routes.SubscriptionService.increment_usage')
    @patch('routes.batch_processing_routes.BatchProcessingService')
    def test_process_scenarios_batch_service_error(self, mock_service_class, mock_increment, mock_usage, mock_auth, client, mock_customer, override_auth_dependency):
        """Test batch processing when service raises an error"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 95
        mock_usage.return_value = mock_usage_response
        
        # Make service raise an exception
        mock_service_class.side_effect = Exception("Service initialization failed")
        
        request_data = {"scenario_ids": [1, 2]}
        
        response = client.post(
            "/batch-processing/scenarios/process",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify error response
        assert response.status_code == 500
        response_data = response.json()
        assert "Failed to start batch processing" in response_data["detail"]
    
    @patch('routes.batch_processing_routes.require_client_or_admin')
    @patch('routes.batch_processing_routes.SubscriptionService.get_usage_limits')
    def test_get_batch_processing_status_success(self, mock_usage, mock_auth, client, mock_customer, override_auth_dependency):
        """Test successful batch processing status request"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 25
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 75
        mock_usage_response.runs_limit_reached = False
        mock_usage.return_value = mock_usage_response
        
        response = client.get(
            "/batch-processing/scenarios/status",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["batch_processing_available"] is True
        assert response_data["usage_limits"]["runs_used"] == 25
        assert response_data["usage_limits"]["runs_limit"] == 100
        assert response_data["usage_limits"]["runs_remaining"] == 75
        assert response_data["usage_limits"]["runs_limit_reached"] is False
        assert response_data["max_scenarios_per_batch"] == 50
        
        # Check features
        assert response_data["features"]["llm_evaluation"] is True
        assert response_data["features"]["validation_generation"] is True
        assert response_data["features"]["sse_streaming"] is True
    
    @patch('routes.batch_processing_routes.require_client_or_admin')
    @patch('routes.batch_processing_routes.SubscriptionService.get_usage_limits')
    def test_get_batch_processing_status_no_limits(self, mock_usage, mock_auth, client, mock_customer, override_auth_dependency):
        """Test batch processing status when usage limits cannot be retrieved"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        mock_usage.return_value = None
        
        response = client.get(
            "/batch-processing/scenarios/status",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify error response
        assert response.status_code == 403
        response_data = response.json()
        assert "Unable to verify subscription limits" in response_data["detail"]
    
    def test_get_batch_processing_status_unauthorized(self, client):
        """Test batch processing status without authentication"""
        response = client.get("/batch-processing/scenarios/status")
        
        assert response.status_code == 401 or response.status_code == 403
    
    @patch('routes.batch_processing_routes.require_client_or_admin')
    @patch('routes.batch_processing_routes.SubscriptionService.get_usage_limits')
    def test_get_batch_processing_status_service_error(self, mock_usage, mock_auth, client, mock_customer, override_auth_dependency):
        """Test batch processing status when service raises an error"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        mock_usage.side_effect = Exception("Database connection failed")
        
        response = client.get(
            "/batch-processing/scenarios/status",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify error response
        assert response.status_code == 500
        response_data = response.json()
        assert "Failed to get batch processing status" in response_data["detail"]
    
    def test_format_sse_event_function(self):
        """Test the format_sse_event helper function"""
        from routes.batch_processing_routes import format_sse_event
        
        # Create test event
        event = BatchProcessingStreamEvent(
            event_type="scenario_result",
            data={
                "scenario_id": 1,
                "scenario_name": "Test Scenario",
                "status": "completed"
            }
        )
        
        result = format_sse_event(event)
        
        # Verify SSE format
        assert result.startswith("event: scenario_result\n")
        assert "data: " in result
        assert result.endswith("\n\n")
        
        # Verify JSON is included
        assert "scenario_id" in result
        assert "Test Scenario" in result
        assert "completed" in result
    
    def test_format_sse_event_error_handling(self):
        """Test SSE event formatting with invalid data"""
        from routes.batch_processing_routes import format_sse_event
        
        # Create mock event that will cause JSON serialization error
        mock_event = MagicMock()
        mock_event.event_type = "test"
        mock_event.model_dump_json.side_effect = Exception("Serialization error")
        
        result = format_sse_event(mock_event)
        
        # Should return error event
        assert result.startswith("event: error\n")
        assert "Failed to format event" in result
        assert "Serialization error" in result
    
    @patch('routes.batch_processing_routes.require_client_or_admin')
    @patch('routes.batch_processing_routes.SubscriptionService.get_usage_limits')
    def test_request_validation_edge_cases(self, mock_usage, mock_auth, client, mock_customer, override_auth_dependency):
        """Test request validation edge cases"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 0
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 100
        mock_usage.return_value = mock_usage_response
        
        # Test minimum valid request (1 scenario)
        response = client.post(
            "/batch-processing/scenarios/process",
            json={"scenario_ids": [1]},
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should not be a validation error (but might fail later due to mocking)
        assert response.status_code != 422
        
        # Test maximum valid request (50 scenarios)
        response = client.post(
            "/batch-processing/scenarios/process",
            json={"scenario_ids": list(range(1, 51))},
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should not be a validation error (but might fail later due to mocking)
        assert response.status_code != 422
        
        # Test with non-integer scenario IDs
        response = client.post(
            "/batch-processing/scenarios/process",
            json={"scenario_ids": ["not_an_int", "also_not_int"]},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test with missing scenario_ids field
        response = client.post(
            "/batch-processing/scenarios/process",
            json={"wrong_field": [1, 2]},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422  # Validation error 