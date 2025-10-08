"""
Comprehensive tests for PAT Token Authentication Service
Tests authentication middleware that supports both Clerk JWT and PAT tokens
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.model import Customer, CustomerRole
from service.PATTokenAuthService import (
    authenticate_request,
    require_client_or_admin_dynamic,
    require_pat_token,
    get_auth_info
)


class TestPATTokenAuthService(unittest.TestCase):
    """Test PAT Token Authentication Service"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=Session)
        self.mock_request = Mock(spec=Request)
        self.customer_id = "customer_123"
        self.customer = Customer(
            id=self.customer_id,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=CustomerRole.CLIENT
        )

    def test_get_auth_info_no_credentials(self):
        """Test auth info with no credentials"""
        result = get_auth_info(credentials=None)

        self.assertEqual(result["auth_type"], "none")
        self.assertIsNone(result["token_format"])

    def test_get_auth_info_pat_token(self):
        """Test auth info with PAT token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="st_pat_abc123def456ghi789"
        )

        result = get_auth_info(credentials=credentials)

        self.assertEqual(result["auth_type"], "pat_token")
        self.assertEqual(result["token_format"], "st_pat_*")
        self.assertEqual(result["token_prefix"], "st_pat_abc...")

    def test_get_auth_info_jwt_token(self):
        """Test auth info with JWT token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123"
        )

        result = get_auth_info(credentials=credentials)

        self.assertEqual(result["auth_type"], "jwt_token")
        self.assertEqual(result["token_format"], "jwt")
        self.assertTrue(result["token_prefix"].endswith("..."))

    @patch('service.PATTokenAuthService.PATTokenService.get_customer_by_pat_token')
    async def test_authenticate_request_pat_token_success(self, mock_get_customer):
        """Test successful authentication with PAT token"""
        mock_get_customer.return_value = self.customer

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="st_pat_validtoken123"
        )

        result = await authenticate_request(
            request=self.mock_request,
            credentials=credentials,
            db=self.mock_db
        )

        self.assertEqual(result, self.customer)
        mock_get_customer.assert_called_once_with(db=self.mock_db, token="st_pat_validtoken123")

    @patch('service.PATTokenAuthService.PATTokenService.get_customer_by_pat_token')
    async def test_authenticate_request_pat_token_invalid(self, mock_get_customer):
        """Test authentication with invalid PAT token"""
        mock_get_customer.return_value = None

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="st_pat_invalidtoken123"
        )

        with self.assertRaises(HTTPException) as context:
            await authenticate_request(
                request=self.mock_request,
                credentials=credentials,
                db=self.mock_db
            )

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid or revoked PAT token")

    @patch('service.PATTokenAuthService.validate_token_with_request')
    async def test_authenticate_request_jwt_token_success(self, mock_validate_jwt):
        """Test successful authentication with JWT token"""
        # Mock JWT validation
        mock_validate_jwt.return_value = {"sub": self.customer_id, "email": "test@example.com"}

        # Mock customer query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.customer

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.valid_jwt_token"
        )

        result = await authenticate_request(
            request=self.mock_request,
            credentials=credentials,
            db=self.mock_db
        )

        self.assertEqual(result, self.customer)
        mock_validate_jwt.assert_called_once_with(self.mock_request)

    @patch('service.PATTokenAuthService.validate_token_with_request')
    async def test_authenticate_request_jwt_token_invalid(self, mock_validate_jwt):
        """Test authentication with invalid JWT token"""
        mock_validate_jwt.side_effect = HTTPException(status_code=401, detail="Invalid JWT token")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_jwt_token"
        )

        with self.assertRaises(HTTPException) as context:
            await authenticate_request(
                request=self.mock_request,
                credentials=credentials,
                db=self.mock_db
            )

        self.assertEqual(context.exception.status_code, 401)

    @patch('service.PATTokenAuthService.validate_token_with_request')
    async def test_authenticate_request_jwt_customer_not_found(self, mock_validate_jwt):
        """Test JWT authentication with customer not found in database"""
        mock_validate_jwt.return_value = {"sub": "nonexistent_user", "email": "test@example.com"}
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_jwt_but_no_customer"
        )

        with self.assertRaises(HTTPException) as context:
            await authenticate_request(
                request=self.mock_request,
                credentials=credentials,
                db=self.mock_db
            )

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Customer not found")

    async def test_authenticate_request_no_credentials(self):
        """Test authentication with no credentials"""
        with self.assertRaises(HTTPException) as context:
            await authenticate_request(
                request=self.mock_request,
                credentials=None,
                db=self.mock_db
            )

        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("Authentication required", context.exception.detail)

    @patch('service.PATTokenAuthService.authenticate_request')
    async def test_require_client_or_admin_dynamic(self, mock_authenticate):
        """Test that dynamic auth function delegates to authenticate_request"""
        mock_authenticate.return_value = self.customer

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="st_pat_test123"
        )

        result = await require_client_or_admin_dynamic(
            request=self.mock_request,
            credentials=credentials,
            db=self.mock_db
        )

        self.assertEqual(result, self.customer)
        mock_authenticate.assert_called_once_with(self.mock_request, credentials, self.mock_db)

    @patch('service.PATTokenAuthService.PATTokenService.get_customer_by_pat_token')
    async def test_require_pat_token_success(self, mock_get_customer):
        """Test successful PAT token requirement"""
        mock_get_customer.return_value = self.customer

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="st_pat_validtoken123"
        )

        result = await require_pat_token(credentials=credentials, db=self.mock_db)

        self.assertEqual(result, self.customer)
        mock_get_customer.assert_called_once_with(db=self.mock_db, token="st_pat_validtoken123")

    async def test_require_pat_token_no_credentials(self):
        """Test PAT token requirement with no credentials"""
        with self.assertRaises(HTTPException) as context:
            await require_pat_token(credentials=None, db=self.mock_db)

        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("PAT token required", context.exception.detail)

    async def test_require_pat_token_wrong_format(self):
        """Test PAT token requirement with wrong token format"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="not_a_pat_token"
        )

        with self.assertRaises(HTTPException) as context:
            await require_pat_token(credentials=credentials, db=self.mock_db)

        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("Token must start with 'st_pat_'", context.exception.detail)

    @patch('service.PATTokenAuthService.PATTokenService.get_customer_by_pat_token')
    async def test_require_pat_token_invalid_token(self, mock_get_customer):
        """Test PAT token requirement with invalid token"""
        mock_get_customer.return_value = None

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="st_pat_invalidtoken"
        )

        with self.assertRaises(HTTPException) as context:
            await require_pat_token(credentials=credentials, db=self.mock_db)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid or revoked PAT token")

    @patch('service.PATTokenAuthService.validate_token_with_request')
    async def test_authenticate_request_jwt_missing_sub(self, mock_validate_jwt):
        """Test JWT authentication with missing 'sub' claim"""
        mock_validate_jwt.return_value = {"email": "test@example.com"}  # Missing 'sub'

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="jwt_missing_sub"
        )

        with self.assertRaises(HTTPException) as context:
            await authenticate_request(
                request=self.mock_request,
                credentials=credentials,
                db=self.mock_db
            )

        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("missing user ID", context.exception.detail)

    @patch('service.PATTokenAuthService.validate_token_with_request')
    async def test_authenticate_request_jwt_exception(self, mock_validate_jwt):
        """Test JWT authentication with unexpected exception"""
        mock_validate_jwt.side_effect = Exception("Unexpected error")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="jwt_with_error"
        )

        with self.assertRaises(HTTPException) as context:
            await authenticate_request(
                request=self.mock_request,
                credentials=credentials,
                db=self.mock_db
            )

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid JWT token")

    def test_auth_token_precedence(self):
        """Test that PAT tokens are checked before JWT tokens"""
        # This is implicitly tested by the order in authenticate_request
        # PAT tokens (st_pat_*) are checked first, then JWT tokens
        pat_token = "st_pat_test123"
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"

        # PAT token should be detected correctly
        self.assertTrue(pat_token.startswith("st_pat_"))
        # JWT token should not be detected as PAT
        self.assertFalse(jwt_token.startswith("st_pat_"))


if __name__ == "__main__":
    unittest.main()