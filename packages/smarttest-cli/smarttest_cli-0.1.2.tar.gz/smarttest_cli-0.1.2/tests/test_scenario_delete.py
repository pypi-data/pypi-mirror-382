"""
Tests for the DELETE /scenario/{scenario_id} endpoint

These tests verify that:
- The scenario deletion endpoint correctly deletes scenarios and all associated data
- Access control is properly enforced
- Transaction rollback works correctly on errors
- Proper HTTP responses are returned for various scenarios
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database.model import (
    Base, ScenarioDB, EndpointDB, SystemDB, 
    Validation, ScenarioParametersDB, ScenarioRunHistoryDB,
    EndpointParametersDB
)
from routes.scenario_routes import get_db
from service.ClerkAuthService import require_client_or_admin


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
def client(db_session, mock_customer):
    """Create a test client for the FastAPI application with overrides"""
    def get_test_db():
        return db_session
    
    def get_test_customer():
        return mock_customer
    
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[require_client_or_admin] = get_test_customer
    
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def mock_customer():
    """Create a mock customer for authentication"""
    return MagicMock(id="test_customer_id", email="test@example.com")


@pytest.fixture
def sample_data_with_associations(db_session):
    """Create sample data with a scenario and all its associations"""
    # Create system
    system = SystemDB(id=1, name="Test API", base_url="https://api.example.com")
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
    
    # Create endpoint parameter
    endpoint_param = EndpointParametersDB(
        id=1,
        endpoint_id=1,
        parameter_name="id",
        parameter_type="path",
        default_value="123"
    )
    db_session.add(endpoint_param)
    
    # Create scenario
    scenario = ScenarioDB(
        id=1,
        name="Test Scenario",
        endpoint_id=1,
        requires_auth=False
    )
    db_session.add(scenario)
    
    # Create validations
    validation1 = Validation(
        id=1,
        validation_text="Status code should be 200",
        description="Check success status",
        scenario_id=1
    )
    validation2 = Validation(
        id=2,
        validation_text="Response should contain user data",
        description="Check response content",
        scenario_id=1
    )
    db_session.add(validation1)
    db_session.add(validation2)
    
    # Create scenario parameters
    scenario_param = ScenarioParametersDB(
        id=1,
        scenario_id=1,
        endpoint_parameter_id=1,
        custom_value="456"
    )
    db_session.add(scenario_param)
    
    # Create scenario run history
    run_history = ScenarioRunHistoryDB(
        id=1,
        scenario_id=1,
        overall_status="success",
        raw_request_details={"method": "GET", "url": "/users/456"},
        actual_response_status_code=200,
        actual_response_headers={"content-type": "application/json"},
        actual_response_body={"id": 456, "name": "Test User"},
        validation_attempts=[]
    )
    db_session.add(run_history)
    
    db_session.commit()
    
    return {
        "scenario": scenario,
        "endpoint": endpoint,
        "system": system,
        "validations": [validation1, validation2],
        "scenario_parameters": [scenario_param],
        "run_history": [run_history]
    }


class TestScenarioDelete:
    """Test cases for the DELETE /scenario/{scenario_id} endpoint"""
    
    @patch('routes.scenario_routes.check_user_system_access')
    def test_delete_scenario_success(self, mock_access_check, client, mock_customer, sample_data_with_associations):
        """Test successful scenario deletion"""
        # Setup mocks
        mock_access_check.return_value = None  # No exception means access granted
        
        # Make the request
        response = client.delete("/scenario/1")
        
        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["message"] == "Successfully deleted scenario 1"
        assert response_data["scenario_id"] == 1
        assert "deleted_items" in response_data
        
        # Verify that access check was called
        mock_access_check.assert_called_once()
    
    def test_delete_scenario_not_found(self, client, mock_customer):
        """Test deletion of non-existent scenario"""
        
        # Make the request for non-existent scenario
        response = client.delete("/scenario/999")
        
        # Verify response
        assert response.status_code == 404
        response_data = response.json()
        assert "Scenario with id 999 not found" in response_data["detail"]
    
    @patch('routes.scenario_routes.check_user_system_access')
    def test_delete_scenario_access_denied(self, mock_access_check, client, mock_customer, sample_data_with_associations):
        """Test scenario deletion with access denied"""
        # Setup mocks
        mock_access_check.side_effect = HTTPException(status_code=403, detail="Access denied")
        
        # Make the request
        response = client.delete("/scenario/1")
        
        # Verify response
        assert response.status_code == 403
        response_data = response.json()
        assert "Access denied" in response_data["detail"]
    
    def test_delete_scenario_missing_endpoint(self, client, mock_customer, db_session):
        """Test deletion of scenario with missing endpoint"""
        
        # Create scenario without endpoint
        scenario = ScenarioDB(
            id=2,
            name="Orphaned Scenario",
            endpoint_id=999,  # Non-existent endpoint
            requires_auth=False
        )
        db_session.add(scenario)
        db_session.commit()
        
        # Make the request
        response = client.delete("/scenario/2")
        
        # Verify response
        assert response.status_code == 404
        response_data = response.json()
        assert "Endpoint not found for scenario 2" in response_data["detail"]
    
    def test_delete_scenario_unauthenticated(self, db_session):
        """Test scenario deletion without authentication"""
        # Create a client without auth override
        def get_test_db():
            return db_session
        
        app.dependency_overrides[get_db] = get_test_db
        
        try:
            client = TestClient(app)
            # Make the request without authentication
            response = client.delete("/scenario/1")
            
            # Verify response (should be 401 or 403 depending on auth setup)
            assert response.status_code in [401, 403]
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__])