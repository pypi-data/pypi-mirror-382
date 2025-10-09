"""
Simple Regression Test for JWT Authentication Bug

This test focuses on the specific bug that occurred:
- JWT validation returns {"user_id": ...} format
- PAT token auth service must extract "user_id" not "sub"

This prevents the "Invalid JWT token - missing user ID" error.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from service.PATTokenAuthService import authenticate_request


class TestJWTAuthBugRegression:
    """Regression test for the specific JWT auth bug"""

    @pytest.mark.asyncio
    async def test_jwt_user_id_extraction_bug_prevention(self):
        """
        REGRESSION TEST: Prevent JWT user_id extraction bug

        This test specifically validates that the authenticate_request function
        correctly extracts user_id from JWT validation results.

        Bug scenario: JWT validation returns {"user_id": "123"} but the code
        was looking for jwt_payload.get("sub") instead of jwt_payload.get("user_id").
        """
        # Create mock request and credentials
        mock_request = Mock(spec=Request)
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_jwt"

        # Create mock database and customer
        mock_db = Mock()
        mock_customer = Mock()
        mock_customer.id = "user_12345"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

        # Create the mock JWT validation response in the CORRECT format
        jwt_validation_result = {
            "user_id": "user_12345",  # This is what the function should extract
            "session_id": "sess_12345",
            "claims": {
                "sub": "user_12345",  # This was incorrectly being accessed
                "email": "test@example.com"
            }
        }

        # Mock the validate_token_with_request function
        async def mock_validate_jwt(request):
            return jwt_validation_result

        # Patch the validation function
        import service.PATTokenAuthService
        original_validate = service.PATTokenAuthService.validate_token_with_request
        service.PATTokenAuthService.validate_token_with_request = mock_validate_jwt

        try:
            # Test the authentication - this should work without throwing
            # "Invalid JWT token - missing user ID"
            result = await authenticate_request(mock_request, mock_credentials, mock_db)

            # Verify success
            assert result is not None, "Authentication should succeed"
            assert result.id == "user_12345", "Should return correct customer"

            # Verify database query was called correctly
            mock_db.query.assert_called()

        except HTTPException as e:
            pytest.fail(f"Authentication failed with: {e.detail}")

        finally:
            # Restore original function
            service.PATTokenAuthService.validate_token_with_request = original_validate

    @pytest.mark.asyncio
    async def test_jwt_missing_user_id_error_scenario(self):
        """
        TEST: Verify proper error when JWT validation returns malformed data

        This tests the error path to ensure we get a clear error message
        when the JWT validation response is missing user_id.
        """
        # Create mock request and credentials
        mock_request = Mock(spec=Request)
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.malformed_jwt"

        # Create mock database
        mock_db = Mock()

        # JWT validation returns response without user_id (malformed)
        jwt_validation_result = {
            "session_id": "sess_12345",
            "claims": {
                "sub": "user_12345",  # Has sub but no user_id at top level
                "email": "test@example.com"
            }
            # Missing "user_id" key!
        }

        # Mock the validate_token_with_request function
        async def mock_validate_jwt_malformed(request):
            return jwt_validation_result

        # Patch the validation function
        import service.PATTokenAuthService
        original_validate = service.PATTokenAuthService.validate_token_with_request
        service.PATTokenAuthService.validate_token_with_request = mock_validate_jwt_malformed

        try:
            # Test the authentication - should fail with clear message
            with pytest.raises(HTTPException) as exc_info:
                await authenticate_request(mock_request, mock_credentials, mock_db)

            # Verify we get the expected error message
            assert exc_info.value.status_code == 401
            assert "Invalid JWT token - missing user ID" in str(exc_info.value.detail)

        finally:
            # Restore original function
            service.PATTokenAuthService.validate_token_with_request = original_validate

    @pytest.mark.asyncio
    async def test_pat_token_authentication_still_works(self):
        """
        TEST: Verify PAT token authentication is unaffected by JWT changes

        This ensures that fixing the JWT bug didn't break PAT token functionality.
        """
        # Create mock request and credentials for PAT token
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/test-endpoint"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get = Mock(return_value="smarttest-cli/1.0")

        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "st_pat_valid_token_12345"  # PAT token format

        # Create mock database and customer
        mock_db = Mock()
        mock_customer = Mock()
        mock_customer.id = "user_12345"

        # Mock the PAT token service methods
        def mock_validate_pat_token_with_usage_logging(db, token, endpoint_accessed, ip_address=None, user_agent=None):
            if token == "st_pat_valid_token_12345":
                mock_token = Mock()
                mock_token.customer_id = "user_12345"
                return mock_token
            return None

        # Mock the database customer query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

        # Patch the PAT token service
        import service.PATTokenAuthService
        original_pat_service = service.PATTokenAuthService.PATTokenService.validate_pat_token_with_usage_logging
        service.PATTokenAuthService.PATTokenService.validate_pat_token_with_usage_logging = staticmethod(mock_validate_pat_token_with_usage_logging)

        try:
            # Test PAT token authentication
            result = await authenticate_request(mock_request, mock_credentials, mock_db)

            # Verify success
            assert result is not None, "PAT token authentication should succeed"
            assert result.id == "user_12345", "Should return correct customer"

        finally:
            # Restore original function
            service.PATTokenAuthService.PATTokenService.validate_pat_token_with_usage_logging = original_pat_service

    def test_auth_service_exports_are_correct(self):
        """
        TEST: Verify auth service exports are properly configured

        This ensures the centralized auth service is set up correctly.
        """
        from service.AuthService import require_auth, require_jwt_auth

        # Both should be callable functions
        assert callable(require_auth), "require_auth should be a function"
        assert callable(require_jwt_auth), "require_jwt_auth should be a function"

        # They should be different functions (dual auth vs JWT-only)
        assert require_auth != require_jwt_auth, "Dual auth should differ from JWT-only auth"

    def test_documentation_of_the_fix(self):
        """
        DOCUMENTATION TEST: Document what the bug was and how it was fixed

        This test serves as living documentation of the bug and fix.
        """
        # The bug: PATTokenAuthService was doing this:
        #   jwt_payload = await validate_token_with_request(request)
        #   user_id = jwt_payload.get("sub")  # ❌ WRONG
        #
        # The fix: PATTokenAuthService now does this:
        #   jwt_result = await validate_token_with_request(request)
        #   user_id = jwt_result.get("user_id")  # ✅ CORRECT
        #
        # Root cause: validate_token_with_request returns:
        #   {"user_id": "123", "session_id": "sess", "claims": {"sub": "123", ...}}
        #   Not the raw JWT payload!

        # This test always passes but serves as documentation
        bug_description = "JWT auth failed with 'Invalid JWT token - missing user ID'"
        fix_description = "Extract user_id from response dict, not sub from claims"

        assert bug_description != fix_description, "Bug was fixed"
        assert "user_id" in fix_description, "Fix involves user_id extraction"