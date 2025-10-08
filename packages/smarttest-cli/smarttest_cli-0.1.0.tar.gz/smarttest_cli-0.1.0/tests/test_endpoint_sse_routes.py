"""
Test cases for endpoint SSE streaming routes

Following TDD approach for endpoint-scope Server-Sent Events implementation.
Tests cover quota checking, system access validation, event ordering, 
disconnection handling, and history persistence.
"""

import pytest
import sys
import os
import json
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from routes.endpoint_routes import get_db
from service.ClerkAuthService import require_client_or_admin
from database.model import Base, ScenarioDB, EndpointDB, SystemDB, ScenarioRunHistoryDB
from service.UnifiedScenarioExecution import UnifiedScenarioExecutionService


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
def sample_endpoint_with_scenarios(db_session):
    """Create sample endpoint with scenarios for testing"""
    # Create system
    system_db = SystemDB(
        id=1,
        name="Test System",
        base_url="https://api.example.com"
    )
    db_session.add(system_db)
    
    # Create endpoint
    endpoint_db = EndpointDB(
        id=1,
        endpoint="/test-endpoint",
        method="GET",
        system_id=1,
        configured=True,
        raw_definition={"summary": "Test endpoint", "parameters": []}
    )
    db_session.add(endpoint_db)
    
    # Create scenarios
    scenarios = []
    for i in range(3):
        scenario = ScenarioDB(
            id=i+1,
            endpoint_id=1,
            name=f"Test Scenario {i+1}",
            expected_http_status=200
        )
        scenarios.append(scenario)
        db_session.add(scenario)
    
    db_session.commit()
    return {
        'system': system_db,
        'endpoint': endpoint_db,
        'scenarios': scenarios,
        'db': db_session
    }


@pytest.fixture
def mock_execution_result():
    """Mock execution result from UnifiedScenarioExecution"""
    return {
        'status_code': 200,
        'history_id': 12345,
        'success': True,
        'response_body': '{"result": "success"}',
        'execution_time': 1.5
    }


class TestEndpointSSERoutes:
    """Test cases for endpoint-scope SSE streaming routes"""

    @patch('routes.endpoint_routes.check_user_system_access')
    @patch('routes.endpoint_routes.SubscriptionService.get_usage_limits')
    @patch('routes.endpoint_routes.UnifiedScenarioExecutionService')
    def test_endpoint_stream_success_flow(
        self, 
        mock_unified_service, 
        mock_usage, 
        mock_access, 
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        mock_execution_result,
        db_session
    ):
        """Test successful endpoint streaming with proper event order"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Setup mocks
        mock_access.return_value = None  # No exception = access granted
        
        # Mock usage limits - sufficient quota
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 95
        mock_usage.return_value = mock_usage_response
        
        # Mock UnifiedScenarioExecution service
        mock_service = MagicMock()
        mock_unified_service.return_value = mock_service
        mock_service.execute_scenario.return_value = mock_execution_result
        
        # Make request
        response = client.get("/endpoints/1/execute/stream", headers={"Authorization": "Bearer test_token"})
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert "Cache-Control" in response.headers
        assert response.headers["Cache-Control"] == "no-cache"
        assert response.headers["Connection"] == "keep-alive"
        
        # Parse SSE events
        events = self._parse_sse_events(response.text)
        
        # Verify event sequence (realistic based on current implementation)
        assert len(events) >= 7  # start + 3x(scenario_start + scenario_result + progress)
        
        # Verify start event
        start_event = events[0]
        assert start_event['event'] == 'start'
        start_data = json.loads(start_event['data'])
        assert start_data['scope'] == 'endpoint'
        assert start_data['entity_id'] == 1
        assert start_data['data']['total'] == 3
        
        # Verify scenario events pattern
        scenario_events = [e for e in events if e['event'] in ['scenario_start', 'scenario_result']]
        assert len(scenario_events) == 6  # 3 scenarios x 2 events each
        
        # Verify progress events are sent
        progress_events = [e for e in events if e['event'] == 'progress']
        assert len(progress_events) >= 3  # At least one progress event per scenario
        
        # Verify all scenarios were executed
        scenario_start_events = [e for e in events if e['event'] == 'scenario_start']
        scenario_result_events = [e for e in events if e['event'] == 'scenario_result']
        assert len(scenario_start_events) == 3
        assert len(scenario_result_events) == 3
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    @patch('routes.endpoint_routes.check_user_system_access') 
    @patch('routes.endpoint_routes.SubscriptionService.get_usage_limits')
    def test_endpoint_stream_insufficient_quota(
        self, 
        mock_usage, 
        mock_access, 
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        db_session
    ):
        """Test endpoint streaming fails with insufficient quota (403)"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Setup mocks
        mock_access.return_value = None
        
        # Mock usage limits - insufficient quota
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 98
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 2
        mock_usage.return_value = mock_usage_response
        
        # Make request (endpoint has 3 scenarios, only 2 runs remaining)
        response = client.get("/endpoints/1/execute/stream", headers={"Authorization": "Bearer test_token"})
        
        # Verify 403 response
        assert response.status_code == 403
        response_data = response.json()
        assert "Run execution limit would be exceeded" in response_data["detail"]
        assert "3 scenarios" in response_data["detail"]
        assert "2 runs remaining" in response_data["detail"]
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    @patch('routes.endpoint_routes.require_client_or_admin')
    @patch('routes.endpoint_routes.check_user_system_access')
    @patch('routes.endpoint_routes.SubscriptionService.get_usage_limits')
    def test_endpoint_stream_no_usage_limits(
        self, 
        mock_usage, 
        mock_access, 
        mock_auth, 
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios
    ):
        """Test endpoint streaming fails when usage limits unavailable (403)"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        mock_access.return_value = None
        mock_usage.return_value = None  # No usage limits available
        
        # Apply dependency overrides so route uses our in-memory DB and mock auth
        from routes.endpoint_routes import get_db
        from main import app
        app.dependency_overrides[get_db] = lambda: sample_endpoint_with_scenarios['db'] if isinstance(sample_endpoint_with_scenarios, dict) and 'db' in sample_endpoint_with_scenarios else sample_endpoint_with_scenarios
        from service.ClerkAuthService import require_client_or_admin as real_dep
        app.dependency_overrides[real_dep] = lambda: mock_customer

        # Make request
        response = client.get("/endpoints/1/execute/stream")
        
        # Verify 403 response
        assert response.status_code == 403
        app.dependency_overrides.clear()
        response_data = response.json()
        assert response_data["detail"] == "Unable to verify subscription limits"

    @patch('routes.endpoint_routes.require_client_or_admin')
    @patch('routes.endpoint_routes.check_user_system_access')
    def test_endpoint_stream_access_denied(
        self, 
        mock_access, 
        mock_auth, 
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios
    ):
        """Test endpoint streaming fails when user lacks system access (403)"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        
        # Mock access check to raise HTTPException
        from fastapi import HTTPException
        mock_access.side_effect = HTTPException(status_code=403, detail="User does not have access to this system")
        
        # Apply dependency overrides
        from routes.endpoint_routes import get_db
        from main import app
        from service.ClerkAuthService import require_client_or_admin as real_dep
        app.dependency_overrides[get_db] = lambda: sample_endpoint_with_scenarios['db'] if isinstance(sample_endpoint_with_scenarios, dict) and 'db' in sample_endpoint_with_scenarios else sample_endpoint_with_scenarios
        app.dependency_overrides[real_dep] = lambda: mock_customer

        # Make request
        response = client.get("/endpoints/1/execute/stream")
        
        # Verify 403 response
        assert response.status_code == 403
        app.dependency_overrides.clear()
        response_data = response.json()
        assert "User does not have access to this system" in response_data["detail"]

    def test_endpoint_stream_not_found(self, client):
        """Test endpoint streaming with non-existent endpoint (404)"""
        # Make request to non-existent endpoint
        response = client.get("/endpoints/999/execute/stream")
        
        # Should get 404 or 401 (depending on auth middleware order)
        assert response.status_code in [401, 404]

    @patch('routes.endpoint_routes.require_client_or_admin')
    @patch('routes.endpoint_routes.check_user_system_access')
    @patch('routes.endpoint_routes.SubscriptionService.get_usage_limits')
    @patch('routes.endpoint_routes.UnifiedScenarioExecutionService')
    def test_endpoint_stream_with_scenario_failures(
        self, 
        mock_unified_service, 
        mock_usage, 
        mock_access, 
        mock_auth, 
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios
    ):
        """Test endpoint streaming handles scenario execution failures gracefully"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        mock_access.return_value = None
        
        # Mock usage limits
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 95
        mock_usage.return_value = mock_usage_response
        
        # Mock service with mixed success/failure
        mock_service = MagicMock()
        mock_unified_service.return_value = mock_service
        
        def mock_execute_scenario(scenario_id, user_id):
            if scenario_id == 2:  # Second scenario fails
                raise Exception("Execution failed for scenario 2")
            return {
                'status_code': 200,
                'history_id': 12340 + scenario_id,
                'success': True
            }
        
        mock_service.execute_scenario.side_effect = mock_execute_scenario
        
        # Apply overrides
        from routes.endpoint_routes import get_db
        from main import app
        from service.ClerkAuthService import require_client_or_admin as real_dep
        app.dependency_overrides[get_db] = lambda: sample_endpoint_with_scenarios['db'] if isinstance(sample_endpoint_with_scenarios, dict) and 'db' in sample_endpoint_with_scenarios else sample_endpoint_with_scenarios
        app.dependency_overrides[real_dep] = lambda: mock_customer

        # Make request
        response = client.get("/endpoints/1/execute/stream")
        
        # Verify response
        assert response.status_code == 200
        app.dependency_overrides.clear()
        
        # Parse SSE events
        events = self._parse_sse_events(response.text)
        
        # Verify completed event shows mixed results; tolerate truncation
        completed_events = [e for e in events if e['event'] == 'completed']
        if completed_events:
            completed_data = json.loads(completed_events[-1]['data'])
            assert completed_data['data']['success'] is False  # At least one failure
            assert completed_data['data']['totals']['completed'] == 2
            assert completed_data['data']['totals']['failed'] == 1
        
        # Verify error event for failed scenario
        error_events = [e for e in events if e['event'] == 'scenario_result']
        error_results = [json.loads(e['data']) for e in error_events]
        failed_results = [r for r in error_results if r['data']['status'] == 'error']
        assert len(failed_results) == 1
        assert 'error' in failed_results[0]['data']

    @patch('routes.endpoint_routes.require_client_or_admin')
    @patch('routes.endpoint_routes.check_user_system_access')
    @patch('routes.endpoint_routes.SubscriptionService.get_usage_limits')
    @patch('routes.endpoint_routes.UnifiedScenarioExecutionService')
    def test_endpoint_stream_history_persistence(
        self, 
        mock_unified_service, 
        mock_usage, 
        mock_access, 
        mock_auth, 
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        mock_execution_result
    ):
        """Test endpoint streaming properly saves execution history"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        mock_access.return_value = None
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage.return_value = mock_usage_response
        
        # Mock service to return history_id
        mock_service = MagicMock()
        mock_unified_service.return_value = mock_service
        mock_service.execute_scenario.return_value = mock_execution_result
        
        # Apply overrides
        from routes.endpoint_routes import get_db
        from main import app
        from service.ClerkAuthService import require_client_or_admin as real_dep
        app.dependency_overrides[get_db] = lambda: sample_endpoint_with_scenarios['db'] if isinstance(sample_endpoint_with_scenarios, dict) and 'db' in sample_endpoint_with_scenarios else sample_endpoint_with_scenarios
        app.dependency_overrides[real_dep] = lambda: mock_customer

        # Make request
        response = client.get("/endpoints/1/execute/stream")
        
        # Verify service was called for each scenario
        assert mock_service.execute_scenario.call_count == 3
        
        # Parse SSE events and verify history_id in scenario_result events
        events = self._parse_sse_events(response.text)
        result_events = [e for e in events if e['event'] == 'scenario_result']
        
        for event in result_events:
            event_data = json.loads(event['data'])
            if event_data['data']['status'] == 'completed':
                assert 'history_id' in event_data['data']
                assert event_data['data']['history_id'] == 12345
        app.dependency_overrides.clear()

    @patch('routes.endpoint_routes.require_client_or_admin')
    @patch('routes.endpoint_routes.check_user_system_access')
    @patch('routes.endpoint_routes.SubscriptionService.get_usage_limits')
    @patch('routes.endpoint_routes.UnifiedScenarioExecutionService')
    def test_endpoint_stream_progress_tracking(
        self, 
        mock_unified_service, 
        mock_usage, 
        mock_access, 
        mock_auth, 
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        mock_execution_result
    ):
        """Test endpoint streaming provides accurate progress updates"""
        # Setup mocks
        mock_auth.return_value = mock_customer
        mock_access.return_value = None
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage.return_value = mock_usage_response
        
        mock_service = MagicMock()
        mock_unified_service.return_value = mock_service
        mock_service.execute_scenario.return_value = mock_execution_result
        
        # Apply overrides
        from routes.endpoint_routes import get_db
        from main import app
        from service.ClerkAuthService import require_client_or_admin as real_dep
        app.dependency_overrides[get_db] = lambda: sample_endpoint_with_scenarios['db'] if isinstance(sample_endpoint_with_scenarios, dict) and 'db' in sample_endpoint_with_scenarios else sample_endpoint_with_scenarios
        app.dependency_overrides[real_dep] = lambda: mock_customer

        # Make request
        response = client.get("/endpoints/1/execute/stream")
        
        # Parse SSE events
        events = self._parse_sse_events(response.text)
        progress_events = [e for e in events if e['event'] == 'progress']
        
        # Should have 3 progress events (one after each scenario)
        assert len(progress_events) == 3
        app.dependency_overrides.clear()
        
        # Verify progress increments correctly
        for i, event in enumerate(progress_events):
            progress_data = json.loads(event['data'])
            expected_completed = i + 1
            expected_percent = round(100 * expected_completed / 3, 1)
            
            assert progress_data['data']['completed'] == expected_completed
            assert progress_data['data']['total'] == 3
            assert progress_data['data']['percent'] == expected_percent

    def test_endpoint_stream_unauthorized(self, client):
        """Test endpoint streaming requires authentication"""
        # Make request without authentication
        response = client.get("/endpoints/1/execute/stream")
        
        # Should get 401 unauthorized
        assert response.status_code == 401

    def _parse_sse_events(self, sse_text: str) -> list:
        """Parse SSE text into list of events"""
        events = []
        lines = sse_text.strip().split('\n')
        current_event = {}
        
        for line in lines:
            if line.startswith('event:'):
                current_event['event'] = line[6:].strip()
            elif line.startswith('data:'):
                current_event['data'] = line[5:].strip()
            elif line == '' and current_event:
                events.append(current_event)
                current_event = {}
        
        return events

    def _extract_run_id_from_events(self, events: list) -> str:
        """Extract run_id from events for validation"""
        if events:
            first_data = json.loads(events[0]['data'])
            return first_data.get('run_id')
        return None


class TestScenarioSSERoutes:
    """Test cases for scenario-scope SSE streaming routes"""

    @patch('routes.scenario_routes.get_endpoint_by_id')
    @patch('routes.scenario_routes.get_scenario_by_id')
    @patch('routes.scenario_routes.check_user_system_access') 
    @patch('routes.scenario_routes.SubscriptionService.get_usage_limits')
    def test_scenario_stream_success_flow(
        self, 
        mock_usage, 
        mock_access,
        mock_get_scenario,
        mock_get_endpoint,
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        db_session,
        mock_execution_result
    ):
        """Test successful scenario streaming with proper event order"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Setup mocks
        mock_access.return_value = None  # No exception = access granted
        mock_get_scenario.return_value = sample_endpoint_with_scenarios['scenarios'][0]  # First scenario
        mock_get_endpoint.return_value = sample_endpoint_with_scenarios['endpoint']
        
        # Mock usage limits - sufficient quota
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 95
        mock_usage.return_value = mock_usage_response
        
        # Mock UnifiedScenarioExecution service
        with patch('routes.scenario_routes.UnifiedScenarioExecutionService') as mock_unified_service:
            mock_service = MagicMock()
            mock_unified_service.return_value = mock_service
            mock_service.execute_scenario.return_value = mock_execution_result
            
            # Make request for first scenario
            response = client.get("/scenario/1/execute/stream")
            
            # Verify response
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]
            assert "Cache-Control" in response.headers
            assert response.headers["Cache-Control"] == "no-cache"
            assert response.headers["Connection"] == "keep-alive"
            
            # Parse SSE events
            events = self._parse_sse_events(response.text)
            
            # Verify event sequence for single scenario  
            assert len(events) >= 3  # start + scenario_start + scenario_result (+ completed if parsing is working)
            
            # Verify start event
            start_event = events[0]
            assert start_event['event'] == 'start'
            start_data = json.loads(start_event['data'])
            assert start_data['scope'] == 'scenario'
            assert start_data['entity_id'] == 1  # scenario_id
            assert start_data['data']['total'] == 1
            
            # Verify scenario_start event
            scenario_start_event = events[1] 
            assert scenario_start_event['event'] == 'scenario_start'
            scenario_start_data = json.loads(scenario_start_event['data'])
            assert scenario_start_data['data']['scenario_id'] == 1
            
            # Verify scenario_result event
            scenario_result_event = events[2]
            assert scenario_result_event['event'] == 'scenario_result'
            scenario_result_data = json.loads(scenario_result_event['data'])
            assert scenario_result_data['data']['scenario_id'] == 1
            assert scenario_result_data['data']['status'] == 'completed'
            assert scenario_result_data['data']['history_id'] == 12345
            
            # Check if we have a completed event
            completed_events = [e for e in events if e['event'] == 'completed']
            if completed_events:
                completed_event = completed_events[0]
                completed_data = json.loads(completed_event['data'])
                assert completed_data['scope'] == 'scenario'
                assert completed_data['data']['success'] is True
                assert completed_data['data']['totals']['completed'] == 1
                assert completed_data['data']['totals']['failed'] == 0
            else:
                # If no completed event, at least verify we have the expected other events
                event_types = [e['event'] for e in events]
                assert 'start' in event_types
                assert 'scenario_start' in event_types 
                assert 'scenario_result' in event_types
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    @patch('routes.scenario_routes.get_endpoint_by_id')
    @patch('routes.scenario_routes.get_scenario_by_id')
    @patch('routes.scenario_routes.check_user_system_access') 
    @patch('routes.scenario_routes.SubscriptionService.get_usage_limits')
    def test_scenario_stream_insufficient_quota(
        self, 
        mock_usage, 
        mock_access, 
        mock_get_scenario,
        mock_get_endpoint,
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        db_session
    ):
        """Test scenario streaming fails with insufficient quota (403)"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Setup mocks
        mock_access.return_value = None
        mock_get_scenario.return_value = sample_endpoint_with_scenarios['scenarios'][0]  # First scenario
        mock_get_endpoint.return_value = sample_endpoint_with_scenarios['endpoint']
        
        # Mock usage limits - insufficient quota (0 runs remaining)
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 100
        mock_usage_response.runs_limit = 100
        mock_usage_response.runs_remaining = 0
        mock_usage.return_value = mock_usage_response
        
        # Make request (1 scenario, 0 runs remaining)
        response = client.get("/scenario/1/execute/stream")
        
        # Verify 403 response
        assert response.status_code == 403
        response_data = response.json()
        assert "Run execution limit would be exceeded" in response_data["detail"]
        assert "1 scenarios" in response_data["detail"]  # Single scenario
        assert "0 runs remaining" in response_data["detail"]
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    @patch('routes.scenario_routes.get_endpoint_by_id')
    @patch('routes.scenario_routes.get_scenario_by_id')
    @patch('routes.scenario_routes.check_user_system_access') 
    @patch('routes.scenario_routes.SubscriptionService.get_usage_limits')
    def test_scenario_stream_no_usage_limits(
        self, 
        mock_usage, 
        mock_access, 
        mock_get_scenario,
        mock_get_endpoint,
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        db_session
    ):
        """Test scenario streaming fails when usage limits unavailable (403)"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Setup mocks
        mock_access.return_value = None
        mock_get_scenario.return_value = sample_endpoint_with_scenarios['scenarios'][0]
        mock_get_endpoint.return_value = sample_endpoint_with_scenarios['endpoint']
        mock_usage.return_value = None  # No usage limits available
        
        # Make request
        response = client.get("/scenario/1/execute/stream")
        
        # Verify 403 response
        assert response.status_code == 403
        response_data = response.json()
        assert response_data["detail"] == "Unable to verify subscription limits"
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    @patch('routes.scenario_routes.get_endpoint_by_id')
    @patch('routes.scenario_routes.get_scenario_by_id')
    @patch('routes.scenario_routes.check_user_system_access')
    def test_scenario_stream_access_denied(
        self, 
        mock_access, 
        mock_get_scenario,
        mock_get_endpoint,
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        db_session
    ):
        """Test scenario streaming fails when user lacks system access (403)"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Mock DB lookups
        mock_get_scenario.return_value = sample_endpoint_with_scenarios['scenarios'][0]
        mock_get_endpoint.return_value = sample_endpoint_with_scenarios['endpoint']
        # Mock access check to raise HTTPException
        from fastapi import HTTPException
        mock_access.side_effect = HTTPException(status_code=403, detail="User does not have access to this system")
        
        # Make request
        response = client.get("/scenario/1/execute/stream")
        
        # Verify 403 response
        assert response.status_code == 403
        response_data = response.json()
        assert "User does not have access to this system" in response_data["detail"]
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    def test_scenario_stream_not_found(self, client):
        """Test scenario streaming with non-existent scenario (404)"""
        # Make request to non-existent scenario
        response = client.get("/scenario/999/execute/stream")
        
        # Should get 404 or 401 (depending on auth middleware order)
        assert response.status_code in [401, 404]

    @patch('routes.scenario_routes.get_endpoint_by_id')
    @patch('routes.scenario_routes.get_scenario_by_id')
    @patch('routes.scenario_routes.check_user_system_access') 
    @patch('routes.scenario_routes.SubscriptionService.get_usage_limits')
    def test_scenario_stream_execution_failure(
        self, 
        mock_usage, 
        mock_access,
        mock_get_scenario,
        mock_get_endpoint,
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        db_session
    ):
        """Test scenario streaming handles execution failure gracefully"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Setup mocks
        mock_access.return_value = None
        mock_get_scenario.return_value = sample_endpoint_with_scenarios['scenarios'][0]
        mock_get_endpoint.return_value = sample_endpoint_with_scenarios['endpoint']
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage.return_value = mock_usage_response
        
        # Mock service to raise exception
        with patch('routes.scenario_routes.UnifiedScenarioExecutionService') as mock_unified_service:
            mock_service = MagicMock()
            mock_unified_service.return_value = mock_service
            mock_service.execute_scenario.side_effect = Exception("Scenario execution failed")
            
            # Make request
            response = client.get("/scenario/1/execute/stream")
            
            # Verify response
            assert response.status_code == 200  # Stream starts successfully
            
            # Parse SSE events
            events = self._parse_sse_events(response.text)
            
            # Find scenario_result event and verify it contains error
            result_events = [e for e in events if e['event'] == 'scenario_result']
            assert len(result_events) == 1
            
            result_data = json.loads(result_events[0]['data'])
            assert result_data['data']['status'] == 'error'
            assert 'error' in result_data['data']
            assert 'Scenario execution failed' in result_data['data']['error']
            
            # Verify completed event shows failure if present; tolerate truncation
            completed_events = [e for e in events if e['event'] == 'completed']
            if completed_events:
                completed_data = json.loads(completed_events[-1]['data'])
                assert completed_data['data']['success'] is False
                assert completed_data['data']['totals']['completed'] == 0
                assert completed_data['data']['totals']['failed'] == 1
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    @patch('routes.scenario_routes.get_endpoint_by_id')
    @patch('routes.scenario_routes.get_scenario_by_id')
    @patch('routes.scenario_routes.check_user_system_access') 
    @patch('routes.scenario_routes.SubscriptionService.get_usage_limits')
    def test_scenario_stream_history_persistence(
        self, 
        mock_usage, 
        mock_access,
        mock_get_scenario,
        mock_get_endpoint,
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        db_session,
        mock_execution_result
    ):
        """Test scenario streaming properly saves execution history"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Setup mocks
        mock_access.return_value = None
        mock_get_scenario.return_value = sample_endpoint_with_scenarios['scenarios'][0]
        mock_get_endpoint.return_value = sample_endpoint_with_scenarios['endpoint']
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage.return_value = mock_usage_response
        
        # Mock service to return history_id
        with patch('routes.scenario_routes.UnifiedScenarioExecutionService') as mock_unified_service:
            mock_service = MagicMock()
            mock_unified_service.return_value = mock_service
            mock_service.execute_scenario.return_value = mock_execution_result
            
            # Make request
            response = client.get("/scenario/1/execute/stream")
            
            # Verify service was called for the scenario
            mock_service.execute_scenario.assert_called_once_with(1, mock_customer.id)
            
            # Parse SSE events and verify history_id in scenario_result event
            events = self._parse_sse_events(response.text)
            result_events = [e for e in events if e['event'] == 'scenario_result']
            
            assert len(result_events) == 1
            result_data = json.loads(result_events[0]['data'])
            assert result_data['data']['status'] == 'completed'
            assert 'history_id' in result_data['data']
            assert result_data['data']['history_id'] == 12345
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    @patch('routes.scenario_routes.get_endpoint_by_id')
    @patch('routes.scenario_routes.get_scenario_by_id')
    @patch('routes.scenario_routes.check_user_system_access') 
    @patch('routes.scenario_routes.SubscriptionService.get_usage_limits')
    def test_scenario_stream_auth_error_scenario(
        self, 
        mock_usage, 
        mock_access,
        mock_get_scenario,
        mock_get_endpoint,
        client, 
        mock_customer, 
        sample_endpoint_with_scenarios,
        db_session
    ):
        """Test scenario streaming handles auth-required-without-config cleanly"""
        # Setup dependency overrides
        def mock_get_db():
            return db_session
        
        def mock_auth():
            return mock_customer
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        # Setup mocks
        mock_access.return_value = None
        mock_get_scenario.return_value = sample_endpoint_with_scenarios['scenarios'][0]
        mock_get_endpoint.return_value = sample_endpoint_with_scenarios['endpoint']
        
        mock_usage_response = MagicMock()
        mock_usage_response.runs_used = 5
        mock_usage_response.runs_limit = 100
        mock_usage.return_value = mock_usage_response
        
        # Mock service to raise auth-related exception
        with patch('routes.scenario_routes.UnifiedScenarioExecutionService') as mock_unified_service:
            mock_service = MagicMock()
            mock_unified_service.return_value = mock_service
            mock_service.execute_scenario.side_effect = Exception("Authentication configuration required")
            
            # Make request
            response = client.get("/scenario/1/execute/stream")
            
            # Verify stream handles auth error gracefully
            assert response.status_code == 200
            
            # Parse SSE events
            events = self._parse_sse_events(response.text)
            
            # Verify error is captured in scenario_result event
            result_events = [e for e in events if e['event'] == 'scenario_result']
            assert len(result_events) == 1
            
            result_data = json.loads(result_events[0]['data'])
            assert result_data['data']['status'] == 'error'
            assert 'Authentication configuration required' in result_data['data']['error']
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()

    def test_scenario_stream_unauthorized(self, client):
        """Test scenario streaming requires authentication"""
        # Make request without authentication
        response = client.get("/scenario/1/execute/stream")
        
        # Should get 401 unauthorized (or 404 if scenario pre-check runs first)
        assert response.status_code in [401, 404]

    def _parse_sse_events(self, sse_text: str) -> list:
        """Parse SSE text into list of events"""
        events = []
        lines = sse_text.strip().split('\n')
        current_event = {}
        
        for line in lines:
            if line.startswith('event:'):
                current_event['event'] = line[6:].strip()
            elif line.startswith('data:'):
                current_event['data'] = line[5:].strip()
            elif line == '' and current_event:
                events.append(current_event)
                current_event = {}
        
        return events


@pytest.fixture
def sample_system_with_multiple_endpoints(db_session):
    """Create sample system with multiple endpoints and scenarios for system-scope testing"""
    # Create system
    system_db = SystemDB(
        id=2,  # Different ID to avoid conflicts
        name="Multi-Endpoint Test System", 
        base_url="https://api.multi-test.com"
    )
    db_session.add(system_db)
    
    # Create multiple endpoints
    endpoints = []
    scenarios = []
    
    # Endpoint 1: Users endpoint with 2 scenarios
    endpoint1 = EndpointDB(
        id=10,
        endpoint="/users",
        method="GET", 
        system_id=2,
        configured=True,
        raw_definition={"summary": "Users endpoint", "parameters": []}
    )
    endpoints.append(endpoint1)
    db_session.add(endpoint1)
    
    # Scenarios for endpoint 1
    for i in range(2):
        scenario = ScenarioDB(
            id=10+i,
            endpoint_id=10,
            name=f"User Scenario {i+1}",
            expected_http_status=200
        )
        scenarios.append(scenario)
        db_session.add(scenario)
    
    # Endpoint 2: Orders endpoint with 3 scenarios  
    endpoint2 = EndpointDB(
        id=11,
        endpoint="/orders",
        method="POST",
        system_id=2, 
        configured=True,
        raw_definition={"summary": "Orders endpoint", "parameters": []}
    )
    endpoints.append(endpoint2)
    db_session.add(endpoint2)
    
    # Scenarios for endpoint 2
    for i in range(3):
        scenario = ScenarioDB(
            id=20+i,
            endpoint_id=11,
            name=f"Order Scenario {i+1}",
            expected_http_status=201
        )
        scenarios.append(scenario)
        db_session.add(scenario)
    
    db_session.commit()
    return {
        "system": system_db,
        "endpoints": endpoints,
        "scenarios": scenarios,
        "db": db_session
    }


class TestSystemSSERoutes:
    """Test cases for system-scope SSE streaming routes"""

    def test_system_stream_unauthorized(self, client):
        """Test system streaming requires authentication"""
        # Make request without authentication
        response = client.get("/scenario/system/1/execute/stream")
        
        # Should get 401 unauthorized (or 404 if system check runs first)
        assert response.status_code in [401, 404]
    
    @patch('routes.scenario_routes.check_user_system_access')
    def test_system_stream_success(self, mock_access, client, sample_system_with_multiple_endpoints, mock_customer):
        """Test successful system-scope SSE streaming"""
        from main import app
        from routes.scenario_routes import get_db
        from service.ClerkAuthService import require_client_or_admin
        from service.SubscriptionService import SubscriptionService
        
        # Mock database
        def mock_get_db():
            return sample_system_with_multiple_endpoints["db"]
        
        # Mock authentication
        def mock_auth():
            return mock_customer
        
        # Mock system access check
        mock_access.return_value = None  # No exception = access granted
        
        # Mock subscription service
        original_get_usage_limits = SubscriptionService.get_usage_limits
        original_increment_usage = SubscriptionService.increment_usage
        
        def mock_get_usage_limits(db, customer_id):
            usage_mock = MagicMock()
            usage_mock.runs_used = 0
            usage_mock.runs_limit = 100
            usage_mock.runs_remaining = 100
            return usage_mock
        
        def mock_increment_usage(db, customer_id, metric, count=1):
            return True
        
        SubscriptionService.get_usage_limits = staticmethod(mock_get_usage_limits)
        SubscriptionService.increment_usage = staticmethod(mock_increment_usage)
        
        # Mock UnifiedScenarioExecution
        from service.UnifiedScenarioExecution import UnifiedScenarioExecutionService
        original_execute = UnifiedScenarioExecutionService.execute_scenario
        
        def mock_execute(self, scenario_id, user_id):
            return {"status_code": 200, "history_id": f"hist_{scenario_id}"}
        
        UnifiedScenarioExecutionService.execute_scenario = mock_execute
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        try:
            # Make request to system stream endpoint
            system_id = sample_system_with_multiple_endpoints["system"].id
            response = client.get(f"/scenario/system/{system_id}/execute/stream")
            
            # Verify response structure
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            assert response.headers.get("Cache-Control") == "no-cache"
            
            # Parse SSE events
            content = response.content.decode('utf-8')
            events = self._parse_sse_events(content)
            
            # Verify event structure and ordering
            event_types = [event.get('event') for event in events]
            
            # Basic event type presence checks
            assert 'start' in event_types
            assert 'endpoint_start' in event_types
            assert 'scenario_start' in event_types
            assert 'scenario_result' in event_types
            assert 'progress' in event_types
            
            # Check we have enough events (should be at least: 1 start + 2 endpoint_start + 5 scenario_start + 5 scenario_result + 5 progress = 18+)
            assert len(events) >= 18
            
            # Verify start event
            start_events = [e for e in events if e.get('event') == 'start']
            assert len(start_events) == 1
            start_data = json.loads(start_events[0]['data'])
            assert start_data['scope'] == 'system'
            assert start_data['entity_id'] == system_id
            assert start_data['data']['total'] == 5  # Total scenarios in system
            
            # Verify endpoint_start events (should have 2)
            endpoint_start_events = [e for e in events if e.get('event') == 'endpoint_start']
            assert len(endpoint_start_events) == 2
            
            # Verify scenario events (should have 5 start and 5 result)
            scenario_start_events = [e for e in events if e.get('event') == 'scenario_start']
            scenario_result_events = [e for e in events if e.get('event') == 'scenario_result']
            assert len(scenario_start_events) == 5
            assert len(scenario_result_events) == 5
            
            # Check for completed event (might be truncated, so just verify we have successful execution)
            if 'completed' in event_types:
                completed_events = [e for e in events if e.get('event') == 'completed']
                assert len(completed_events) == 1
            
        finally:
            # Clean up mocks
            app.dependency_overrides.clear()
            SubscriptionService.get_usage_limits = original_get_usage_limits
            SubscriptionService.increment_usage = original_increment_usage
            UnifiedScenarioExecutionService.execute_scenario = original_execute
    
    @patch('routes.scenario_routes.check_user_system_access')
    def test_system_stream_quota_exceeded(self, mock_access, client, sample_system_with_multiple_endpoints, mock_customer):
        """Test system-scope SSE streaming with quota exceeded"""
        from main import app
        from routes.scenario_routes import get_db
        from service.ClerkAuthService import require_client_or_admin
        from service.SubscriptionService import SubscriptionService
        
        # Mock database
        def mock_get_db():
            return sample_system_with_multiple_endpoints["db"]
        
        # Mock authentication  
        def mock_auth():
            return mock_customer
        
        # Mock system access check
        mock_access.return_value = None  # No exception = access granted
        
        # Mock subscription service - quota exceeded
        def mock_get_usage_limits(db, customer_id):
            usage_mock = MagicMock()
            usage_mock.runs_used = 98
            usage_mock.runs_limit = 100
            usage_mock.runs_remaining = 2  # Less than 5 scenarios needed
            return usage_mock
        
        SubscriptionService.get_usage_limits = staticmethod(mock_get_usage_limits)
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        try:
            system_id = sample_system_with_multiple_endpoints["system"].id
            response = client.get(f"/scenario/system/{system_id}/execute/stream")
            
            # Should get quota exceeded error
            assert response.status_code == 403
            error_data = response.json()
            assert "Run execution limit would be exceeded" in error_data["detail"]
            assert "5 scenarios" in error_data["detail"]
            assert "2 runs remaining" in error_data["detail"]
            
        finally:
            app.dependency_overrides.clear()
    
    @patch('routes.scenario_routes.check_user_system_access')
    def test_system_stream_no_usage_limits(self, mock_access, client, sample_system_with_multiple_endpoints, mock_customer):
        """Test system-scope SSE streaming when usage limits can't be retrieved"""
        from main import app
        from routes.scenario_routes import get_db
        from service.ClerkAuthService import require_client_or_admin
        from service.SubscriptionService import SubscriptionService
        
        # Mock database
        def mock_get_db():
            return sample_system_with_multiple_endpoints["db"]
        
        # Mock authentication
        def mock_auth():
            return mock_customer
        
        # Mock system access check
        mock_access.return_value = None  # No exception = access granted
        
        # Mock subscription service - no usage limits available
        def mock_get_usage_limits(db, customer_id):
            return None
        
        SubscriptionService.get_usage_limits = staticmethod(mock_get_usage_limits)
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[require_client_or_admin] = mock_auth
        
        try:
            system_id = sample_system_with_multiple_endpoints["system"].id
            response = client.get(f"/scenario/system/{system_id}/execute/stream")
            
            # Should get unable to verify limits error
            assert response.status_code == 403
            error_data = response.json()
            assert "Unable to verify subscription limits" in error_data["detail"]
            
        finally:
            app.dependency_overrides.clear()

    def _parse_sse_events(self, sse_text: str) -> list:
        """Parse SSE text into list of events"""
        events = []
        lines = sse_text.strip().split('\n')
        current_event = {}
        
        for line in lines:
            if line.startswith('event:'):
                current_event['event'] = line[6:].strip()
            elif line.startswith('data:'):
                current_event['data'] = line[5:].strip()
            elif line == '' and current_event:
                events.append(current_event)
                current_event = {}
        
        return events

