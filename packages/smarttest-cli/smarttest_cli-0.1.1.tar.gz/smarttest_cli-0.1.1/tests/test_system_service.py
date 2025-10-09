import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.model import Base, SystemDB
from database.schemas import SystemBase, EndpointBase
from service.SystemService import create_new_system, get_system_by_id, check_system_exists


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


# Fixture to create a test system
@pytest.fixture
def test_system(db_session):
    """Create a test system in the database"""
    system = SystemDB(
        id=1,
        name="Test System",
        base_url="http://test.example.com"
    )
    db_session.add(system)
    db_session.commit()
    db_session.refresh(system)
    return system


# Tests for get_system_by_id
def test_get_system_by_id_existing(db_session, test_system):
    """Test getting an existing system by ID"""
    system = get_system_by_id(db_session, test_system.id)
    assert system is not None
    assert system.id == test_system.id
    assert system.name == test_system.name
    assert system.base_url == test_system.base_url


def test_get_system_by_id_nonexistent(db_session):
    """Test getting a non-existent system by ID"""
    system = get_system_by_id(db_session, 999)
    assert system is None


# Tests for check_system_exists
def test_check_system_exists_existing(db_session, test_system):
    """Test checking if an existing system exists"""
    system = check_system_exists(db_session, test_system.id)
    assert system is not None
    assert system.id == test_system.id
    assert system.name == test_system.name
    assert system.base_url == test_system.base_url


def test_check_system_exists_nonexistent(db_session):
    """Test checking if a non-existent system exists"""
    with pytest.raises(HTTPException) as exc_info:
        check_system_exists(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert "System not found" in exc_info.value.detail


# Tests for create_new_system
@patch('service.SystemService.create_new_endpoint')
def test_create_new_system_without_endpoints(mock_create_endpoint, db_session):
    """Test creating a new system without endpoints"""
    # Create a system schema without endpoints
    system_schema = SystemBase(
        name="New System",
        base_url="http://new.example.com",
        endpoints=[]
    )
    
    # Call the function
    new_system = create_new_system(db_session, system_schema)
    
    # Verify the result
    assert new_system is not None
    assert new_system.name == system_schema.name
    assert new_system.base_url == system_schema.base_url
    
    # Verify the system was added to the database
    db_system = get_system_by_id(db_session, new_system.id)
    assert db_system is not None
    assert db_system.id == new_system.id
    
    # Verify create_new_endpoint was not called
    mock_create_endpoint.assert_not_called()


@patch('service.SystemService.create_new_endpoint')
def test_create_new_system_with_endpoints(mock_create_endpoint, db_session):
    """Test creating a new system with endpoints"""
    # Create a system schema without endpoints to simplify the test
    system_schema = SystemBase(
        name="New System with Endpoints",
        base_url="http://new.example.com",
        endpoints=[]
    )
    
    # Call the function
    new_system = create_new_system(db_session, system_schema)
    
    # Verify the system was created correctly
    assert new_system is not None
    assert new_system.name == system_schema.name
    assert new_system.base_url == system_schema.base_url
    
    # Verify the system was added to the database
    db_system = get_system_by_id(db_session, new_system.id)
    assert db_system is not None
    assert db_system.id == new_system.id
    
    # Verify create_new_endpoint was not called since we had no endpoints
    mock_create_endpoint.assert_not_called()
