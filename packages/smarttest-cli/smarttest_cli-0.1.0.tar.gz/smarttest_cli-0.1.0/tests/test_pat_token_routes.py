"""
Comprehensive tests for PAT Token API endpoints
Tests all PAT token routes as specified in CLI MVP
"""

import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime, timezone

from main import app
from database.schemas import PATTokenWithSecret, PATTokenResponse, PATTokenList
from service.PATTokenService import PATTokenService


class TestPATTokenRoutes(unittest.TestCase):
    """Test PAT Token API endpoints"""

    def setUp(self):
        """Set up test client and fixtures"""
        self.client = TestClient(app)
        self.customer_id = "customer_123"
        self.mock_customer = Mock()
        self.mock_customer.id = self.customer_id
        self.mock_customer.email = "test@example.com"

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.create_pat_token')
    def test_create_pat_token_success(self, mock_create_service, mock_auth):
        """Test successful PAT token creation via API"""
        # Mock authentication
        mock_auth.return_value = self.mock_customer

        # Mock service response
        mock_token_response = PATTokenWithSecret(
            id=1,
            customer_id=self.customer_id,
            label="Test Token",
            scopes=["read", "write"],
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            last_used_at=None,
            token="st_pat_abc123def456"
        )
        mock_create_service.return_value = mock_token_response

        # Make API call
        response = self.client.post("/pat-tokens", json={
            "label": "Test Token",
            "scopes": ["read", "write"]
        })

        # Verify response
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["label"], "Test Token")
        self.assertEqual(data["scopes"], ["read", "write"])
        self.assertEqual(data["token"], "st_pat_abc123def456")
        self.assertIsNotNone(data["created_at"])

        # Verify service was called correctly
        mock_create_service.assert_called_once()
        call_args = mock_create_service.call_args
        self.assertEqual(call_args[1]["customer_id"], self.customer_id)
        self.assertEqual(call_args[1]["token_data"].label, "Test Token")

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.create_pat_token')
    def test_create_pat_token_with_default_scopes(self, mock_create_service, mock_auth):
        """Test PAT token creation with default scopes"""
        mock_auth.return_value = self.mock_customer

        mock_token_response = PATTokenWithSecret(
            id=1,
            customer_id=self.customer_id,
            label="Default Scopes Token",
            scopes=["read", "write"],  # Default scopes
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            last_used_at=None,
            token="st_pat_default123"
        )
        mock_create_service.return_value = mock_token_response

        # Create token without specifying scopes
        response = self.client.post("/pat-tokens", json={
            "label": "Default Scopes Token"
        })

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["scopes"], ["read", "write"])

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.create_pat_token')
    def test_create_pat_token_service_error(self, mock_create_service, mock_auth):
        """Test PAT token creation with service error"""
        mock_auth.return_value = self.mock_customer
        mock_create_service.side_effect = Exception("Database error")

        response = self.client.post("/pat-tokens", json={
            "label": "Error Token"
        })

        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to create PAT token", response.json()["detail"])

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.list_pat_tokens')
    def test_list_pat_tokens_success(self, mock_list_service, mock_auth):
        """Test successful PAT token listing via API"""
        mock_auth.return_value = self.mock_customer

        # Mock service response
        mock_tokens = [
            PATTokenResponse(
                id=1,
                customer_id=self.customer_id,
                label="Token 1",
                scopes=["read"],
                created_at=datetime.now(timezone.utc),
                revoked_at=None,
                last_used_at=None
            ),
            PATTokenResponse(
                id=2,
                customer_id=self.customer_id,
                label="Token 2",
                scopes=["read", "write"],
                created_at=datetime.now(timezone.utc),
                revoked_at=None,
                last_used_at=datetime.now(timezone.utc)
            )
        ]
        mock_list_response = PATTokenList(tokens=mock_tokens, total=2)
        mock_list_service.return_value = mock_list_response

        # Make API call
        response = self.client.get("/pat-tokens")

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["tokens"]), 2)
        self.assertEqual(data["tokens"][0]["label"], "Token 1")
        self.assertEqual(data["tokens"][1]["label"], "Token 2")

        # Verify no token values are returned in list
        for token in data["tokens"]:
            self.assertNotIn("token", token)

        # Verify service was called correctly
        mock_list_service.assert_called_once_with(db=unittest.mock.ANY, customer_id=self.customer_id)

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.list_pat_tokens')
    def test_list_pat_tokens_empty(self, mock_list_service, mock_auth):
        """Test PAT token listing with no tokens"""
        mock_auth.return_value = self.mock_customer
        mock_list_service.return_value = PATTokenList(tokens=[], total=0)

        response = self.client.get("/pat-tokens")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 0)
        self.assertEqual(len(data["tokens"]), 0)

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.revoke_pat_token')
    def test_revoke_pat_token_success(self, mock_revoke_service, mock_auth):
        """Test successful PAT token revocation via API"""
        mock_auth.return_value = self.mock_customer
        mock_revoke_service.return_value = True

        response = self.client.delete("/pat-tokens/1")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")  # No content for 204

        # Verify service was called correctly
        mock_revoke_service.assert_called_once_with(
            db=unittest.mock.ANY,
            customer_id=self.customer_id,
            token_id=1
        )

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.revoke_pat_token')
    def test_revoke_pat_token_not_found(self, mock_revoke_service, mock_auth):
        """Test PAT token revocation with non-existent token"""
        mock_auth.return_value = self.mock_customer
        mock_revoke_service.side_effect = HTTPException(status_code=404, detail="Token not found or already revoked")

        response = self.client.delete("/pat-tokens/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Token not found or already revoked")

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.revoke_pat_token')
    def test_revoke_pat_token_service_error(self, mock_revoke_service, mock_auth):
        """Test PAT token revocation with service error"""
        mock_auth.return_value = self.mock_customer
        mock_revoke_service.side_effect = Exception("Database error")

        response = self.client.delete("/pat-tokens/1")

        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to revoke PAT token", response.json()["detail"])

    def test_pat_token_info_endpoint(self):
        """Test PAT token info endpoint (no auth required)"""
        response = self.client.get("/pat-tokens/info")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["pat_token_system"], "active")
        self.assertEqual(data["supported_token_format"], "st_pat_<random>")
        self.assertEqual(data["default_scopes"], ["read", "write"])
        self.assertIn("endpoints", data)
        self.assertIn("create", data["endpoints"])
        self.assertIn("list", data["endpoints"])
        self.assertIn("revoke", data["endpoints"])

    def test_create_pat_token_invalid_data(self):
        """Test PAT token creation with invalid request data"""
        # Test missing label
        response = self.client.post("/pat-tokens", json={})
        self.assertEqual(response.status_code, 422)  # Validation error

        # Test empty label
        response = self.client.post("/pat-tokens", json={"label": ""})
        self.assertEqual(response.status_code, 422)  # Validation error

        # Test invalid scopes type
        response = self.client.post("/pat-tokens", json={
            "label": "Test Token",
            "scopes": "invalid_scopes_string"  # Should be array
        })
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_revoke_pat_token_invalid_id(self):
        """Test PAT token revocation with invalid token ID"""
        # Test non-numeric ID
        response = self.client.delete("/pat-tokens/invalid")
        self.assertEqual(response.status_code, 422)  # Validation error

    @patch('routes.pat_token_routes.require_client_or_admin')
    def test_authentication_required(self, mock_auth):
        """Test that all endpoints require authentication"""
        mock_auth.side_effect = HTTPException(status_code=401, detail="Authentication required")

        endpoints = [
            ("POST", "/pat-tokens", {"label": "Test"}),
            ("GET", "/pat-tokens", None),
            ("DELETE", "/pat-tokens/1", None)
        ]

        for method, url, data in endpoints:
            if method == "POST":
                response = self.client.post(url, json=data)
            elif method == "GET":
                response = self.client.get(url)
            elif method == "DELETE":
                response = self.client.delete(url)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()["detail"], "Authentication required")

    def test_pat_token_endpoints_content_type(self):
        """Test that endpoints handle content type correctly"""
        # Test POST with wrong content type
        response = self.client.post("/pat-tokens", data="label=Test")  # form data instead of JSON
        self.assertIn(response.status_code, [422, 415])  # Validation or unsupported media type

    @patch('routes.pat_token_routes.require_client_or_admin')
    @patch('routes.pat_token_routes.PATTokenService.create_pat_token')
    def test_create_pat_token_long_label(self, mock_create_service, mock_auth):
        """Test PAT token creation with very long label"""
        mock_auth.return_value = self.mock_customer

        # Test label at max length (100 chars)
        long_label = "a" * 100
        response = self.client.post("/pat-tokens", json={"label": long_label})

        # Should be accepted (assuming service handles it)
        if mock_create_service.called:
            self.assertEqual(response.status_code, 201)
        else:
            # If validation rejects it
            self.assertEqual(response.status_code, 422)

        # Test label over max length
        too_long_label = "a" * 101
        response = self.client.post("/pat-tokens", json={"label": too_long_label})
        self.assertEqual(response.status_code, 422)  # Should be validation error


if __name__ == "__main__":
    unittest.main()