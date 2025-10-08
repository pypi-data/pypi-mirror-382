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

from database.model import Base, Customer, CustomerSystemAccess, SystemDB
from database.schemas import CustomerCreate
from service.CustomerService import (
    get_customer_by_id, get_customer_by_email, create_customer,
    __get_system_access, __check_user_has_access_to_system, check_user_system_access,
    get_system_access_count, create_system_access, get_user_system_access,
    revoke_system_access
)


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


# Fixture to create a test customer
@pytest.fixture
def test_customer(db_session):
    """Create a test customer in the database"""
    customer_data = CustomerCreate(
        id="test_customer_id",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    db_customer = Customer(
        id=customer_data.id,
        email=customer_data.email,
        first_name=customer_data.first_name,
        last_name=customer_data.last_name
    )
    db_session.add(db_customer)
    db_session.commit()
    db_session.refresh(db_customer)
    return db_customer


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


# Fixture to create system access for a customer
@pytest.fixture
def test_system_access(db_session, test_customer, test_system):
    """Create system access for the test customer"""
    access = CustomerSystemAccess(
        customer_id=test_customer.id,
        system_id=test_system.id
    )
    db_session.add(access)
    db_session.commit()
    db_session.refresh(access)
    return access


# Tests for get_customer_by_id
def test_get_customer_by_id_existing(db_session, test_customer):
    """Test getting an existing customer by ID"""
    customer = get_customer_by_id(db_session, test_customer.id)
    assert customer is not None
    assert customer.id == test_customer.id
    assert customer.email == test_customer.email
    assert customer.first_name == test_customer.first_name
    assert customer.last_name == test_customer.last_name


def test_get_customer_by_id_nonexistent(db_session):
    """Test getting a non-existent customer by ID"""
    customer = get_customer_by_id(db_session, "nonexistent_id")
    assert customer is None


# Tests for get_customer_by_email
def test_get_customer_by_email_existing(db_session, test_customer):
    """Test getting an existing customer by email"""
    customer = get_customer_by_email(db_session, test_customer.email)
    assert customer is not None
    assert customer.id == test_customer.id
    assert customer.email == test_customer.email


def test_get_customer_by_email_nonexistent(db_session):
    """Test getting a non-existent customer by email"""
    customer = get_customer_by_email(db_session, "nonexistent@example.com")
    assert customer is None


# Tests for create_customer
def test_create_customer_success(db_session):
    """Test creating a new customer successfully"""
    customer_data = CustomerCreate(
        id="new_customer_id",
        email="new@example.com",
        first_name="New",
        last_name="Customer"
    )
    
    new_customer = create_customer(db_session, customer_data)
    assert new_customer is not None
    assert new_customer.id == customer_data.id
    assert new_customer.email == customer_data.email
    assert new_customer.first_name == customer_data.first_name
    assert new_customer.last_name == customer_data.last_name
    
    # Verify the customer was actually added to the database
    db_customer = get_customer_by_id(db_session, customer_data.id)
    assert db_customer is not None
    assert db_customer.id == customer_data.id


def test_create_customer_already_exists(db_session, test_customer):
    """Test creating a customer that already exists"""
    customer_data = CustomerCreate(
        id=test_customer.id,  # Use existing ID to trigger error
        email="another@example.com",
        first_name="Another",
        last_name="User"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_customer(db_session, customer_data)
    
    assert exc_info.value.status_code == 400
    assert "Customer already exists" in exc_info.value.detail


# Tests for system access functions
def test_get_system_access_existing(db_session, test_system_access):
    """Test getting existing system access"""
    access = __get_system_access(db_session, test_system_access.customer_id, test_system_access.system_id)
    assert access is not None
    assert access.customer_id == test_system_access.customer_id
    assert access.system_id == test_system_access.system_id


def test_get_system_access_nonexistent(db_session):
    """Test getting non-existent system access"""
    access = __get_system_access(db_session, "nonexistent_id", 999)
    assert access is None


def test_check_user_has_access_to_system_with_access(db_session, test_system_access):
    """Test checking if a user has access to a system when they do"""
    has_access = __check_user_has_access_to_system(
        db_session, test_system_access.customer_id, test_system_access.system_id
    )
    assert has_access is True


def test_check_user_has_access_to_system_without_access(db_session, test_customer, test_system):
    """Test checking if a user has access to a system when they don't"""
    # Create a different system that the user doesn't have access to
    new_system = SystemDB(id=2, name="Another System", base_url="http://another.example.com")
    db_session.add(new_system)
    db_session.commit()
    
    has_access = __check_user_has_access_to_system(db_session, test_customer.id, new_system.id)
    assert has_access is False


def test_check_user_system_access_with_access(db_session, test_system_access):
    """Test check_user_system_access when user has access"""
    access = check_user_system_access(
        db_session, test_system_access.customer_id, test_system_access.system_id
    )
    assert access is True


def test_check_user_system_access_without_access(db_session, test_customer):
    """Test check_user_system_access when user doesn't have access"""
    with pytest.raises(HTTPException) as exc_info:
        check_user_system_access(db_session, test_customer.id, 999)  # Non-existent system ID
    
    assert exc_info.value.status_code == 403
    assert "You don't have permission to access this system" in exc_info.value.detail


def test_get_system_access_count(db_session, test_system_access):
    """Test counting users with access to a system"""
    count = get_system_access_count(db_session, test_system_access.system_id)
    assert count == 1
    
    # Add another user with access
    new_customer = Customer(
        id="another_customer",
        email="another@example.com",
        first_name="Another",
        last_name="User"
    )
    db_session.add(new_customer)
    db_session.commit()
    
    new_access = CustomerSystemAccess(
        customer_id=new_customer.id,
        system_id=test_system_access.system_id
    )
    db_session.add(new_access)
    db_session.commit()
    
    # Count should now be 2
    count = get_system_access_count(db_session, test_system_access.system_id)
    assert count == 2


# Tests for create_system_access
@patch('service.CustomerService.check_system_exists')
def test_create_system_access_success(mock_check_system, db_session, test_customer, test_system):
    """Test creating system access successfully"""
    # Mock the check_system_exists function to avoid dependency
    mock_check_system.return_value = True
    
    # Create access for the customer
    access = create_system_access(
        db_session, test_customer.id, test_system.id, test_customer.id
    )
    
    assert access is not None
    assert access.customer_id == test_customer.id
    assert access.system_id == test_system.id
    
    # Verify access was added to the database
    db_access = __get_system_access(db_session, test_customer.id, test_system.id)
    assert db_access is not None


@patch('service.CustomerService.check_system_exists')
def test_create_system_access_already_exists(mock_check_system, db_session, test_system_access):
    """Test creating system access that already exists"""
    # Mock the check_system_exists function to avoid dependency
    mock_check_system.return_value = True
    
    with pytest.raises(HTTPException) as exc_info:
        create_system_access(
            db_session, 
            test_system_access.customer_id, 
            test_system_access.system_id, 
            test_system_access.customer_id
        )
    
    assert exc_info.value.status_code == 400
    assert "Customer already has access to this system" in exc_info.value.detail


# Tests for get_user_system_access
def test_get_user_system_access(db_session, test_system_access):
    """Test getting all systems a user has access to"""
    access_list = get_user_system_access(db_session, test_system_access.customer_id)
    assert len(access_list) == 1
    assert access_list[0].customer_id == test_system_access.customer_id
    assert access_list[0].system_id == test_system_access.system_id
    
    # Add access to another system
    new_system = SystemDB(id=2, name="Another System", base_url="http://another.example.com")
    db_session.add(new_system)
    db_session.commit()
    
    new_access = CustomerSystemAccess(
        customer_id=test_system_access.customer_id,
        system_id=new_system.id
    )
    db_session.add(new_access)
    db_session.commit()
    
    # Now user should have access to 2 systems
    access_list = get_user_system_access(db_session, test_system_access.customer_id)
    assert len(access_list) == 2


# Tests for revoke_system_access
def test_revoke_system_access_success(db_session, test_system_access):
    """Test revoking system access successfully"""
    # Add another user with access to prevent the "only user" check from failing
    new_customer = Customer(
        id="another_customer",
        email="another@example.com",
        first_name="Another",
        last_name="User"
    )
    db_session.add(new_customer)
    db_session.commit()
    
    new_access = CustomerSystemAccess(
        customer_id=new_customer.id,
        system_id=test_system_access.system_id
    )
    db_session.add(new_access)
    db_session.commit()
    
    # Now revoke the original user's access
    result = revoke_system_access(
        db_session, 
        test_system_access.customer_id, 
        test_system_access.system_id
    )
    
    assert "revoked" in result["message"]
    
    # Verify access was removed from the database
    access = __get_system_access(
        db_session, 
        test_system_access.customer_id, 
        test_system_access.system_id
    )
    assert access is None


def test_revoke_system_access_only_user(db_session, test_system_access):
    """Test revoking system access when user is the only one with access"""
    with pytest.raises(HTTPException) as exc_info:
        revoke_system_access(
            db_session, 
            test_system_access.customer_id, 
            test_system_access.system_id
        )
    
    assert exc_info.value.status_code == 400
    assert "only user with access" in exc_info.value.detail


def test_revoke_system_access_nonexistent(db_session, test_customer, test_system):
    """Test revoking non-existent system access"""
    # First give the user access to the system to pass the check_user_system_access check
    access = CustomerSystemAccess(
        customer_id=test_customer.id,
        system_id=test_system.id
    )
    db_session.add(access)
    db_session.commit()
    
    # Try to revoke access for a non-existent user
    with pytest.raises(HTTPException) as exc_info:
        revoke_system_access(
            db_session, 
            test_customer.id, 
            test_system.id, 
            "nonexistent_user"
        )
    
    assert exc_info.value.status_code == 404
    assert "No access found" in exc_info.value.detail
