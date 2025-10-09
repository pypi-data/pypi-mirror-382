"""
Comprehensive pytest tests for PAT Token API endpoints
Tests all PAT token routes as specified in CLI MVP
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime, timezone

from main import app
from database.schemas import PATTokenWithSecret, PATTokenResponse, PATTokenList
from service.PATTokenAuthService import require_client_or_admin_dynamic


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def mock_customer():
    """Mock authenticated customer"""
    customer = Mock()
    customer.id = "customer_123"
    customer.email = "test@example.com"
    return customer


@pytest.fixture
def override_auth_dependency(mock_customer):
    """Override FastAPI auth dependency to bypass authentication during tests"""
    app.dependency_overrides[require_client_or_admin_dynamic] = lambda: mock_customer
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_client_or_admin_dynamic, None)


class TestPATTokenRoutes:
    """Test PAT Token API endpoints using pytest"""

    def test_pat_token_info_endpoint(self, client):
        """Test PAT token info endpoint (no auth required)"""
        response = client.get("/pat-tokens/info")

        assert response.status_code == 200
        data = response.json()
        assert data["pat_token_system"] == "active"
        assert data["supported_token_format"] == "st_pat_<random>"
        assert data["default_scopes"] == ["read", "write"]
        assert "endpoints" in data
        assert "create" in data["endpoints"]
        assert "list" in data["endpoints"]
        assert "revoke" in data["endpoints"]

    def test_create_pat_token_success(self, client, override_auth_dependency, mock_customer, mocker):
        """Test successful PAT token creation via API"""
        # Mock service response
        mock_token_response = PATTokenWithSecret(
            id=1,
            customer_id=mock_customer.id,
            label="Test Token",
            scopes=["read", "write"],
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            last_used_at=None,
            token="st_pat_abc123def456"
        )
        mock_create_service = mocker.patch('routes.pat_token_routes.PATTokenService.create_pat_token')
        mock_create_service.return_value = mock_token_response

        # Make API call
        response = client.post("/pat-tokens", json={
            "label": "Test Token",
            "scopes": ["read", "write"]
        })

        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["label"] == "Test Token"
        assert data["scopes"] == ["read", "write"]
        assert data["token"] == "st_pat_abc123def456"
        assert "created_at" in data

        # Verify service was called correctly
        mock_create_service.assert_called_once()

    def test_create_pat_token_with_default_scopes(self, client, override_auth_dependency, mock_customer, mocker):
        """Test PAT token creation with default scopes"""
        mock_token_response = PATTokenWithSecret(
            id=1,
            customer_id=mock_customer.id,
            label="Default Scopes Token",
            scopes=["read", "write"],  # Default scopes
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            last_used_at=None,
            token="st_pat_default123"
        )
        mock_create_service = mocker.patch('routes.pat_token_routes.PATTokenService.create_pat_token')
        mock_create_service.return_value = mock_token_response

        # Create token without specifying scopes
        response = client.post("/pat-tokens", json={
            "label": "Default Scopes Token"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["scopes"] == ["read", "write"]

    def test_create_pat_token_service_error(self, client, override_auth_dependency, mocker):
        """Test PAT token creation with service error"""
        mock_create_service = mocker.patch('routes.pat_token_routes.PATTokenService.create_pat_token')
        mock_create_service.side_effect = Exception("Database error")

        response = client.post("/pat-tokens", json={
            "label": "Error Token"
        })

        assert response.status_code == 500
        assert "Failed to create PAT token" in response.json()["detail"]

    def test_list_pat_tokens_success(self, client, override_auth_dependency, mock_customer, mocker):
        """Test successful PAT token listing via API"""
        # Mock service response
        mock_tokens = [
            PATTokenResponse(
                id=1,
                customer_id=mock_customer.id,
                label="Token 1",
                scopes=["read"],
                created_at=datetime.now(timezone.utc),
                revoked_at=None,
                last_used_at=None
            ),
            PATTokenResponse(
                id=2,
                customer_id=mock_customer.id,
                label="Token 2",
                scopes=["read", "write"],
                created_at=datetime.now(timezone.utc),
                revoked_at=None,
                last_used_at=datetime.now(timezone.utc)
            )
        ]
        mock_list_response = PATTokenList(tokens=mock_tokens, total=2)
        mock_list_service = mocker.patch('routes.pat_token_routes.PATTokenService.list_pat_tokens')
        mock_list_service.return_value = mock_list_response

        # Make API call
        response = client.get("/pat-tokens")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tokens"]) == 2
        assert data["tokens"][0]["label"] == "Token 1"
        assert data["tokens"][1]["label"] == "Token 2"

        # Verify no token values are returned in list
        for token in data["tokens"]:
            assert "token" not in token

    def test_list_pat_tokens_empty(self, client, override_auth_dependency, mocker):
        """Test PAT token listing with no tokens"""
        mock_list_service = mocker.patch('routes.pat_token_routes.PATTokenService.list_pat_tokens')
        mock_list_service.return_value = PATTokenList(tokens=[], total=0)

        response = client.get("/pat-tokens")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["tokens"]) == 0

    def test_revoke_pat_token_success(self, client, override_auth_dependency, mock_customer, mocker):
        """Test successful PAT token revocation via API"""
        mock_revoke_service = mocker.patch('routes.pat_token_routes.PATTokenService.revoke_pat_token')
        mock_revoke_service.return_value = True

        response = client.delete("/pat-tokens/1")

        assert response.status_code == 204
        assert response.content == b""  # No content for 204

        # Verify service was called correctly
        mock_revoke_service.assert_called_once()

    def test_revoke_pat_token_not_found(self, client, override_auth_dependency, mocker):
        """Test PAT token revocation with non-existent token"""
        mock_revoke_service = mocker.patch('routes.pat_token_routes.PATTokenService.revoke_pat_token')
        mock_revoke_service.side_effect = HTTPException(status_code=404, detail="Token not found or already revoked")

        response = client.delete("/pat-tokens/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Token not found or already revoked"

    def test_revoke_pat_token_service_error(self, client, override_auth_dependency, mocker):
        """Test PAT token revocation with service error"""
        mock_revoke_service = mocker.patch('routes.pat_token_routes.PATTokenService.revoke_pat_token')
        mock_revoke_service.side_effect = Exception("Database error")

        response = client.delete("/pat-tokens/1")

        assert response.status_code == 500
        assert "Failed to revoke PAT token" in response.json()["detail"]

    @pytest.mark.parametrize("invalid_data,expected_status", [
        ({}, 422),  # Missing label - Pydantic validation
        ({"label": ""}, 500),  # Empty label - Service level validation
        ({"label": "a" * 101}, 422),  # Label too long - Pydantic validation
        ({"scopes": "invalid"}, 422),  # Invalid scopes format - Pydantic validation
    ])
    def test_create_pat_token_invalid_data(self, client, override_auth_dependency, invalid_data, expected_status):
        """Test PAT token creation with invalid request data"""
        response = client.post("/pat-tokens", json=invalid_data)
        assert response.status_code == expected_status

    def test_revoke_pat_token_invalid_id(self, client, override_auth_dependency):
        """Test PAT token revocation with invalid token ID"""
        # Test non-numeric ID
        response = client.delete("/pat-tokens/invalid")
        assert response.status_code == 422  # Validation error

    def test_authentication_required(self, client):
        """Test that protected endpoints require authentication when no override is active"""
        # Note: Without override_auth_dependency fixture, should require authentication
        endpoints = [
            ("POST", "/pat-tokens", {"label": "Test"}),
            ("GET", "/pat-tokens", None),
            ("DELETE", "/pat-tokens/1", None)
        ]

        for method, url, data in endpoints:
            if method == "POST":
                response = client.post(url, json=data)
            elif method == "GET":
                response = client.get(url)
            elif method == "DELETE":
                response = client.delete(url)

            assert response.status_code == 401  # Should require authentication

    def test_create_pat_token_long_label(self, client, override_auth_dependency):
        """Test PAT token creation with very long label"""
        # Test label over max length
        too_long_label = "a" * 101
        response = client.post("/pat-tokens", json={"label": too_long_label})
        assert response.status_code == 422  # Should be validation error