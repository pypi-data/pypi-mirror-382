import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import json

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.ClerkAuthService import (
    validate_token, get_current_user, verify_system_access, create_clerk_customer
)
from database.model import CustomerSystemAccess


# Mock the Clerk client for testing
@pytest.fixture
def mock_clerk_client():
    """Create a mock Clerk client for testing"""
    with patch('service.ClerkAuthService.get_clerk_client') as mock_get_client:
        # Create the actual mock client
        mock_client = MagicMock()

        # Make get_clerk_client() return our mock client
        mock_get_client.return_value = mock_client

        # Create a mock response for the verify method
        mock_verify_response = MagicMock()
        mock_verify_response.user_id = "test_user_id"
        mock_verify_response.session_id = "test_session_id"

        # Set up the mock clients.verify method
        mock_client.clients.verify.return_value = mock_verify_response

        # Create a mock response for the users.create method
        mock_create_response = MagicMock()
        mock_create_response.id = "test_user_id"

        # Set up the mock users.create method
        mock_client.users.create.return_value = mock_create_response

        yield mock_client


# Mock the database session for testing
@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing"""
    mock_db = MagicMock()
    
    # Set up the query method to return a mock query object
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    
    # Set up the filter method to return itself for chaining
    mock_query.filter.return_value = mock_query
    
    # Set up the first method to return None by default (no access)
    mock_query.first.return_value = None
    
    yield mock_db


# Tests for validate_token
@pytest.mark.asyncio
async def test_validate_token_success(mock_clerk_client, mock_db_session):
    """Test successful token validation"""
    # Create mock credentials
    mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test_token")
    
    # Call the function
    result = await validate_token(mock_credentials, mock_db_session)
    
    # Verify the result
    assert result["user_id"] == "test_user_id"
    assert result["session_id"] == "test_session_id"
    
    # Verify the clerk client was called correctly
    mock_clerk_client.clients.verify.assert_called_once_with(request={"token": "test_token"})


@pytest.mark.asyncio
async def test_validate_token_no_credentials(mock_clerk_client, mock_db_session):
    """Test token validation with no credentials"""
    with pytest.raises(HTTPException) as exc_info:
        await validate_token(None, mock_db_session)
    
    assert exc_info.value.status_code == 401
    assert "Invalid authentication credentials" in exc_info.value.detail


@pytest.mark.asyncio
async def test_validate_token_clerk_error(mock_clerk_client, mock_db_session):
    """Test token validation with Clerk error"""
    # Create mock credentials
    mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test_token")
    
    # Make the clerk client raise an exception
    mock_clerk_client.clients.verify.side_effect = Exception("Clerk error")
    
    with pytest.raises(HTTPException) as exc_info:
        await validate_token(mock_credentials, mock_db_session)
    
    assert exc_info.value.status_code == 401
    assert "Invalid authentication credentials" in exc_info.value.detail
    assert "Clerk error" in exc_info.value.detail


# Tests for get_current_user
@pytest.mark.asyncio
async def test_get_current_user_success():
    """Test getting current user successfully"""
    token_data = {"user_id": "test_user_id", "session_id": "test_session_id"}
    
    result = await get_current_user(token_data)
    
    assert result["user_id"] == "test_user_id"


@pytest.mark.asyncio
async def test_get_current_user_no_user_id():
    """Test getting current user with no user ID in token data"""
    token_data = {"session_id": "test_session_id"}  # Missing user_id
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token_data)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


# Tests for verify_system_access
@pytest.mark.asyncio
async def test_verify_system_access_with_access(mock_db_session):
    """Test verifying system access when user has access"""
    # Set up the mock to return an access record
    mock_access = CustomerSystemAccess(
        id=1,
        customer_id="test_user_id",
        system_id=1
    )
    mock_db_session.query().filter().first.return_value = mock_access
    
    user_data = {"user_id": "test_user_id"}
    
    result = await verify_system_access(1, user_data, mock_db_session)
    
    assert result is True


@pytest.mark.asyncio
async def test_verify_system_access_without_access(mock_db_session):
    """Test verifying system access when user doesn't have access"""
    # Set up the mock to return None (no access)
    mock_db_session.query().filter().first.return_value = None
    
    user_data = {"user_id": "test_user_id"}
    
    with pytest.raises(HTTPException) as exc_info:
        await verify_system_access(1, user_data, mock_db_session)
    
    assert exc_info.value.status_code == 403
    assert "User does not have access to system" in exc_info.value.detail


# Tests for create_clerk_customer
def test_create_clerk_customer_success(mock_clerk_client):
    """Test creating a customer in Clerk successfully"""
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
    password = "SecurePassword123!"
    
    result = create_clerk_customer(email, first_name, last_name, password)
    
    assert result["id"] == "test_user_id"
    assert result["email"] == email
    assert result["first_name"] == first_name
    assert result["last_name"] == last_name
    
    # Verify the clerk client was called correctly
    mock_clerk_client.users.create.assert_called_once_with(request={
        "email_address": [email],
        "first_name": first_name,
        "last_name": last_name,
        "password": password
    })


def test_create_clerk_customer_clerk_error(mock_clerk_client):
    """Test creating a customer in Clerk with an error"""
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
    password = "SecurePassword123!"
    
    # Make the clerk client raise an exception
    mock_clerk_client.users.create.side_effect = Exception("Clerk error")
    
    with pytest.raises(HTTPException) as exc_info:
        create_clerk_customer(email, first_name, last_name, password)
    
    assert exc_info.value.status_code == 400
    assert "Error creating customer in Clerk" in exc_info.value.detail
    assert "Clerk error" in exc_info.value.detail


@patch('service.ClerkAuthService.get_clerk_client', return_value=None)
def test_create_clerk_customer_no_client(mock_get_client):
    """Test creating a customer when Clerk client is not initialized"""
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
    password = "SecurePassword123!"
    
    with pytest.raises(HTTPException) as exc_info:
        create_clerk_customer(email, first_name, last_name, password)
    
    assert exc_info.value.status_code == 400
    assert "Error creating customer in Clerk" in exc_info.value.detail
