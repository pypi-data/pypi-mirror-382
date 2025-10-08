"""
Comprehensive pytest tests for PAT Token Service
Tests all PAT token functionality as specified in CLI MVP
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from database.model import PATToken, Customer, CustomerRole
from database.schemas import PATTokenCreate
from service.PATTokenService import PATTokenService


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def customer():
    """Test customer fixture"""
    return Customer(
        id="customer_123",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role=CustomerRole.CLIENT
    )


@pytest.fixture
def customer_id():
    """Customer ID fixture"""
    return "customer_123"


class TestPATTokenService:
    """Test PAT Token Service functionality using pytest"""

    def test_generate_token_format(self):
        """Test token generation follows correct format"""
        token = PATTokenService.generate_token()

        assert token.startswith("st_pat_")
        assert len(token) > 32  # Should be long enough

        # Generate multiple tokens to ensure uniqueness
        tokens = set()
        for _ in range(10):
            tokens.add(PATTokenService.generate_token())

        assert len(tokens) == 10  # All should be unique

    def test_hash_token_consistency(self):
        """Test token hashing is consistent and secure"""
        token = "st_pat_test123456789"
        hash1 = PATTokenService.hash_token(token)
        hash2 = PATTokenService.hash_token(token)

        assert hash1 == hash2  # Same token should produce same hash
        assert len(hash1) == 64  # SHA-256 produces 64-char hex string

        # Different tokens should produce different hashes
        different_hash = PATTokenService.hash_token("st_pat_different")
        assert hash1 != different_hash

    def test_create_pat_token_success(self, mock_db, customer, customer_id):
        """Test successful PAT token creation"""
        # Mock database interactions
        mock_db.query.return_value.filter.return_value.first.return_value = customer

        # Mock the token that gets refreshed
        def mock_refresh(token):
            token.id = 1
            token.created_at = datetime.now(timezone.utc)
            token.revoked_at = None
            token.last_used_at = None

        mock_db.refresh.side_effect = mock_refresh

        # Create token
        token_data = PATTokenCreate(label="Test Token", scopes=["read", "write"])
        result = PATTokenService.create_pat_token(
            db=mock_db,
            customer_id=customer_id,
            token_data=token_data
        )

        # Verify database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # Verify response
        assert result.label == "Test Token"
        assert result.scopes == ["read", "write"]
        assert result.token.startswith("st_pat_")

    def test_create_pat_token_customer_not_found(self, mock_db):
        """Test PAT token creation with non-existent customer"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        token_data = PATTokenCreate(label="Test Token")

        with pytest.raises(HTTPException) as exc_info:
            PATTokenService.create_pat_token(
                db=mock_db,
                customer_id="nonexistent",
                token_data=token_data
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Customer not found"

    def test_create_pat_token_default_scopes(self, mock_db, customer, customer_id):
        """Test PAT token creation with default scopes"""
        mock_db.query.return_value.filter.return_value.first.return_value = customer

        # Mock the token that gets refreshed
        def mock_refresh(token):
            token.id = 1
            token.created_at = datetime.now(timezone.utc)
            token.revoked_at = None
            token.last_used_at = None

        mock_db.refresh.side_effect = mock_refresh

        # Create token without specifying scopes
        token_data = PATTokenCreate(label="Test Token")
        result = PATTokenService.create_pat_token(
            db=mock_db,
            customer_id=customer_id,
            token_data=token_data
        )

        # Verify default scopes were applied
        added_token = mock_db.add.call_args[0][0]
        assert added_token.scopes == ["read", "write"]

    def test_list_pat_tokens_success(self, mock_db, customer, customer_id):
        """Test successful PAT token listing"""
        # Mock customer exists
        mock_db.query.return_value.filter.return_value.first.return_value = customer

        # Mock token query
        mock_tokens = [
            Mock(
                id=1, customer_id=customer_id, label="Token 1", scopes=["read"],
                created_at=datetime.now(timezone.utc), revoked_at=None, last_used_at=None
            ),
            Mock(
                id=2, customer_id=customer_id, label="Token 2", scopes=["read", "write"],
                created_at=datetime.now(timezone.utc), revoked_at=None, last_used_at=None
            )
        ]

        query_mock = Mock()
        query_mock.filter.return_value.filter.return_value.order_by.return_value.all.return_value = mock_tokens
        mock_db.query.return_value = query_mock

        # Call service
        result = PATTokenService.list_pat_tokens(db=mock_db, customer_id=customer_id)

        # Verify results
        assert result.total == 2
        assert len(result.tokens) == 2
        assert result.tokens[0].label == "Token 1"
        assert result.tokens[1].label == "Token 2"

    def test_list_pat_tokens_customer_not_found(self, mock_db):
        """Test PAT token listing with non-existent customer"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            PATTokenService.list_pat_tokens(db=mock_db, customer_id="nonexistent")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Customer not found"

    def test_revoke_pat_token_success(self, mock_db, customer_id):
        """Test successful PAT token revocation"""
        mock_token = Mock()
        mock_token.id = 1
        mock_token.customer_id = customer_id
        mock_token.revoked_at = None

        query_mock = Mock()
        query_mock.filter.return_value.filter.return_value.filter.return_value.first.return_value = mock_token
        mock_db.query.return_value = query_mock

        # Call service
        result = PATTokenService.revoke_pat_token(
            db=mock_db,
            customer_id=customer_id,
            token_id=1
        )

        # Verify token was revoked
        assert result is True
        assert isinstance(mock_token.revoked_at, datetime)
        mock_db.commit.assert_called_once()

    def test_revoke_pat_token_not_found(self, mock_db, customer_id):
        """Test PAT token revocation with non-existent token"""
        query_mock = Mock()
        query_mock.filter.return_value.filter.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value = query_mock

        with pytest.raises(HTTPException) as exc_info:
            PATTokenService.revoke_pat_token(
                db=mock_db,
                customer_id=customer_id,
                token_id=999
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Token not found or already revoked"

    def test_validate_pat_token_valid(self, mock_db, customer_id):
        """Test PAT token validation with valid token"""
        token = "st_pat_validtoken123"
        token_hash = PATTokenService.hash_token(token)

        mock_token = Mock()
        mock_token.id = 1
        mock_token.customer_id = customer_id
        mock_token.token_hash = token_hash
        mock_token.revoked_at = None
        mock_token.last_used_at = None

        query_mock = Mock()
        query_mock.filter.return_value.filter.return_value.first.return_value = mock_token
        mock_db.query.return_value = query_mock

        # Call service
        result = PATTokenService.validate_pat_token(db=mock_db, token=token)

        # Verify results
        assert result == mock_token
        assert isinstance(mock_token.last_used_at, datetime)
        mock_db.commit.assert_called_once()

    @pytest.mark.parametrize("invalid_token", [
        "invalid_token",
        "bearer_token_123",
        "",
        None,
        "st_pat"  # Too short
    ])
    def test_validate_pat_token_invalid_format(self, mock_db, invalid_token):
        """Test PAT token validation with invalid format"""
        result = PATTokenService.validate_pat_token(db=mock_db, token=invalid_token)
        assert result is None

    def test_validate_pat_token_not_found(self, mock_db):
        """Test PAT token validation with non-existent token"""
        token = "st_pat_nonexistent123"

        query_mock = Mock()
        query_mock.filter.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value = query_mock

        result = PATTokenService.validate_pat_token(db=mock_db, token=token)
        assert result is None

    def test_validate_pat_token_revoked(self, mock_db):
        """Test PAT token validation with revoked token"""
        token = "st_pat_revokedtoken123"

        # Mock that no active token is found (because revoked tokens are filtered out)
        query_mock = Mock()
        query_mock.filter.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value = query_mock

        result = PATTokenService.validate_pat_token(db=mock_db, token=token)
        assert result is None

    def test_get_customer_by_pat_token_success(self, mock_db, customer, customer_id):
        """Test getting customer by valid PAT token"""
        token = "st_pat_validtoken123"

        # Mock token validation
        mock_token = Mock()
        mock_token.customer_id = customer_id

        # Mock customer query
        customer_query_mock = Mock()
        customer_query_mock.filter.return_value.first.return_value = customer

        # Set up query return values
        token_query_mock = Mock()
        token_query_mock.filter.return_value.filter.return_value.first.return_value = mock_token

        def query_side_effect(model):
            if model == PATToken:
                return token_query_mock
            elif model == Customer:
                return customer_query_mock
            return Mock()

        mock_db.query.side_effect = query_side_effect

        result = PATTokenService.get_customer_by_pat_token(db=mock_db, token=token)

        assert result == customer

    def test_get_customer_by_pat_token_invalid(self, mock_db):
        """Test getting customer by invalid PAT token"""
        token = "invalid_token"

        result = PATTokenService.get_customer_by_pat_token(db=mock_db, token=token)
        assert result is None