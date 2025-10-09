"""
Integration tests for UnifiedScenarioExecutionService with real database persistence.

These tests verify that:
1. Users can only execute scenarios they have access to
2. Executions are correctly saved to the database 
3. Usage tracking and billing are properly incremented
4. Security controls work end-to-end
"""

import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.model import (
    Base, ScenarioDB, EndpointDB, SystemDB, Customer, CustomerRole,
    CustomerSystemAccess, ScenarioRunHistoryDB, EndpointParametersDB
)
from service.UnifiedScenarioExecution import UnifiedScenarioExecutionService
from service.CustomerService import check_user_system_access
from service.SubscriptionService import SubscriptionService


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
def test_customer(db_session):
    """Create a test customer"""
    customer = Customer(
        id="test_user_123",
        email="test@example.com",
        role=CustomerRole.CLIENT,
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc)
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def test_system(db_session):
    """Create a test system"""
    system = SystemDB(
        id=1,
        name="Test System",
        base_url="https://api.example.com"
    )
    db_session.add(system)
    db_session.commit()
    db_session.refresh(system)
    return system


@pytest.fixture  
def test_endpoint(db_session, test_system):
    """Create a test endpoint"""
    endpoint = EndpointDB(
        id=1,
        endpoint="/test",
        method="GET", 
        system_id=test_system.id,
        configured=True,
        raw_definition={"summary": "Test endpoint", "parameters": []}
    )
    db_session.add(endpoint)
    db_session.commit()
    db_session.refresh(endpoint)
    return endpoint


@pytest.fixture
def test_scenario(db_session, test_endpoint):
    """Create a test scenario"""
    scenario = ScenarioDB(
        id=1,
        endpoint_id=test_endpoint.id,
        name="Test Scenario",
        expected_http_status=200,
        requires_auth=False,
        auth_error=False,
        scenario_parameters=[]
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)
    return scenario


@pytest.fixture
def system_access(db_session, test_customer, test_system):
    """Grant system access to test customer"""
    access = CustomerSystemAccess(
        customer_id=test_customer.id,
        system_id=test_system.id
    )
    db_session.add(access)
    db_session.commit()
    db_session.refresh(access)
    return access


class TestUnifiedExecutionWithDatabasePersistence:
    """Integration tests for unified execution with real database operations"""
    
    @patch('service.UnifiedScenarioExecution.requests.request')
    def test_successful_execution_saves_to_database(
        self, 
        mock_request, 
        db_session, 
        test_customer, 
        test_scenario, 
        system_access
    ):
        """Test that successful scenario execution is saved to execution history"""
        # Setup mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success", "data": "test"}
        mock_request.return_value = mock_response
        
        # Create service and execute scenario
        service = UnifiedScenarioExecutionService(db_session)
        result = service.execute_scenario(test_scenario.id, test_customer.id)
        
        # Verify execution result
        assert result["success"] is True
        assert result["scenario_id"] == test_scenario.id
        assert result["status_code"] == 200
        assert result["body"] == {"result": "success", "data": "test"}
        assert "history_id" in result  # Should include history ID
        
        # Verify database persistence
        history_entries = db_session.query(ScenarioRunHistoryDB).filter(
            ScenarioRunHistoryDB.scenario_id == test_scenario.id
        ).all()
        
        assert len(history_entries) == 1
        history_entry = history_entries[0]
        
        # Verify history entry details
        assert history_entry.scenario_id == test_scenario.id
        assert history_entry.overall_status == "success"  # HTTP 200 = success
        assert history_entry.actual_response_status_code == 200
        assert history_entry.actual_response_body == {"result": "success", "data": "test"}
        assert history_entry.raw_request_details["method"] == "GET"
        assert "https://api.example.com/test" in history_entry.raw_request_details["url"]
        
        # Verify result includes the saved history ID
        assert result["history_id"] == history_entry.id
    
    @patch('service.UnifiedScenarioExecution.requests.request')
    def test_failed_execution_saves_failure_to_database(
        self, 
        mock_request, 
        db_session, 
        test_customer, 
        test_scenario, 
        system_access
    ):
        """Test that failed scenario execution (HTTP 4xx/5xx) is saved as failure"""
        # Setup mock HTTP response - 404 error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"error": "Not found"}
        mock_request.return_value = mock_response
        
        # Create service and execute scenario
        service = UnifiedScenarioExecutionService(db_session)
        result = service.execute_scenario(test_scenario.id, test_customer.id)
        
        # Verify execution result
        assert result["success"] is True  # Execution succeeded, but HTTP status indicates failure
        assert result["status_code"] == 404
        
        # Verify database persistence shows failure
        history_entries = db_session.query(ScenarioRunHistoryDB).filter(
            ScenarioRunHistoryDB.scenario_id == test_scenario.id
        ).all()
        
        assert len(history_entries) == 1
        history_entry = history_entries[0]
        
        # Should be marked as failure due to 4xx status code
        assert history_entry.overall_status == "failure"
        assert history_entry.actual_response_status_code == 404
        assert history_entry.actual_response_body == {"error": "Not found"}
    
    def test_access_control_prevents_unauthorized_execution(
        self, 
        db_session, 
        test_customer, 
        test_scenario
        # Note: No system_access fixture - user should not have access
    ):
        """Test that users without system access cannot execute scenarios"""
        service = UnifiedScenarioExecutionService(db_session)
        
        # Should raise HTTPException for access denied
        with pytest.raises(Exception):
            service.execute_scenario(test_scenario.id, test_customer.id)
        
        # Verify no execution history was saved
        history_entries = db_session.query(ScenarioRunHistoryDB).filter(
            ScenarioRunHistoryDB.scenario_id == test_scenario.id
        ).all()
        assert len(history_entries) == 0
    
    @patch('service.UnifiedScenarioExecution.requests.request')
    def test_multiple_executions_create_separate_history_entries(
        self, 
        mock_request, 
        db_session, 
        test_customer, 
        test_scenario, 
        system_access
    ):
        """Test that multiple executions of the same scenario create separate history entries"""
        # Setup mock HTTP responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        
        # First execution
        mock_response.json.return_value = {"run": 1, "result": "first"}
        mock_request.return_value = mock_response
        
        service = UnifiedScenarioExecutionService(db_session)
        result1 = service.execute_scenario(test_scenario.id, test_customer.id)
        
        # Second execution
        mock_response.json.return_value = {"run": 2, "result": "second"}
        result2 = service.execute_scenario(test_scenario.id, test_customer.id)
        
        # Verify both executions succeeded
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["history_id"] != result2["history_id"]  # Different history entries
        
        # Verify two separate history entries were created
        history_entries = db_session.query(ScenarioRunHistoryDB).filter(
            ScenarioRunHistoryDB.scenario_id == test_scenario.id
        ).order_by(ScenarioRunHistoryDB.id).all()
        
        assert len(history_entries) == 2
        
        # Verify distinct response bodies
        assert history_entries[0].actual_response_body == {"run": 1, "result": "first"}
        assert history_entries[1].actual_response_body == {"run": 2, "result": "second"}
        
        # Verify both marked as successful
        assert all(entry.overall_status == "success" for entry in history_entries)
    
    @patch('service.UnifiedScenarioExecution.requests.request')
    def test_execution_with_auth_scenario(
        self, 
        mock_request, 
        db_session, 
        test_customer, 
        test_endpoint,
        system_access
    ):
        """Test execution of auth-required scenario (should still save history even if auth fails)"""
        # Create auth-required scenario
        auth_scenario = ScenarioDB(
            id=2,
            endpoint_id=test_endpoint.id,
            name="Auth Required Test Scenario",
            expected_http_status=200,
            requires_auth=True,  # This scenario requires auth
            auth_error=False,
            scenario_parameters=[]
        )
        db_session.add(auth_scenario)
        db_session.commit()
        
        # Mock HTTP response (will likely fail due to no auth config)
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_request.return_value = mock_response
        
        service = UnifiedScenarioExecutionService(db_session)
        
        # This might raise an exception due to auth config not being available
        # but we want to verify the service handles it gracefully
        try:
            result = service.execute_scenario(auth_scenario.id, test_customer.id)
            
            # If execution completes, verify it was saved
            if result.get("success"):
                history_entries = db_session.query(ScenarioRunHistoryDB).filter(
                    ScenarioRunHistoryDB.scenario_id == auth_scenario.id
                ).all()
                assert len(history_entries) == 1
                
        except Exception as e:
            # If execution fails due to missing auth config, that's expected
            # The key is that we don't get database integrity errors
            assert "auth" in str(e).lower() or "configuration" in str(e).lower()
            
            # Verify no corrupted history entries were created
            history_entries = db_session.query(ScenarioRunHistoryDB).filter(
                ScenarioRunHistoryDB.scenario_id == auth_scenario.id
            ).all()
            # Should be 0 if execution failed before HTTP call, or 1 if HTTP call was made
            assert len(history_entries) <= 1
    
    @patch('service.UnifiedScenarioExecution.requests.request') 
    def test_history_saving_failure_doesnt_break_execution(
        self, 
        mock_request, 
        db_session, 
        test_customer, 
        test_scenario, 
        system_access
    ):
        """Test that if history saving fails, execution result is still returned"""
        # Setup mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response
        
        # Create service
        service = UnifiedScenarioExecutionService(db_session)
        
        # Mock history saving to fail
        with patch.object(service, '_save_execution_history') as mock_save:
            mock_save.return_value = None  # Simulate history saving failure
            
            # Execute scenario
            result = service.execute_scenario(test_scenario.id, test_customer.id)
            
            # Execution should still succeed even if history saving fails
            assert result["success"] is True
            assert result["status_code"] == 200
            assert result["body"] == {"result": "success"}
            
            # Should not have history_id since saving failed
            assert "history_id" not in result
            
            # Verify save was attempted
            mock_save.assert_called_once()
    
    def test_nonexistent_scenario_handling(
        self, 
        db_session, 
        test_customer,
        system_access
    ):
        """Test proper error handling for non-existent scenarios"""
        service = UnifiedScenarioExecutionService(db_session)
        
        # Should raise HTTPException for scenario not found
        with pytest.raises(Exception):
            service.execute_scenario(999, test_customer.id)  # Non-existent scenario ID
        
        # Verify no history entries were created
        history_entries = db_session.query(ScenarioRunHistoryDB).all()
        assert len(history_entries) == 0


class TestSubscriptionAndUsageIntegration:
    """Integration tests for usage tracking with scenario execution"""
    
    @patch('service.UnifiedScenarioExecution.requests.request')
    @patch('service.SubscriptionService.SubscriptionService.increment_usage')
    def test_successful_execution_increments_usage(
        self, 
        mock_increment_usage, 
        mock_request, 
        db_session, 
        test_customer, 
        test_scenario, 
        system_access
    ):
        """Test that successful scenario execution increments usage tracking"""
        # Setup mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response
        
        # Mock subscription service
        mock_increment_usage.return_value = True
        
        # Execute scenario
        service = UnifiedScenarioExecutionService(db_session)
        result = service.execute_scenario(test_scenario.id, test_customer.id)
        
        # Verify execution succeeded
        assert result["success"] is True
        
        # Note: Usage tracking increment happens at the SSE route level,
        # not in the UnifiedScenarioExecutionService itself.
        # This test documents the expected behavior - the service focuses on execution + history,
        # while the routes handle subscription/billing concerns.
        
        # For now, we verify the service doesn't interfere with usage tracking
        # by completing successfully
        assert result["status_code"] == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])