"""
Comprehensive pytest tests for PAT Token Usage Statistics
Tests the new usage statistics functionality
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.testclient import TestClient

from database.model import PATToken, Customer, TokenUsageLog, CustomerRole
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
def pat_token():
    """Test PAT token fixture"""
    return PATToken(
        id=1,
        customer_id="customer_123",
        token_hash="hashed_token",
        label="Test Token",
        scopes=["read", "write"],
        created_at=datetime.now(timezone.utc) - timedelta(days=30),
        last_used_at=datetime.now(timezone.utc) - timedelta(hours=1),
        revoked_at=None
    )


@pytest.fixture
def usage_logs():
    """Test usage logs fixture"""
    base_time = datetime.now(timezone.utc)

    logs = []
    # Create usage logs for the past 30 days
    for i in range(30):
        access_time = base_time - timedelta(days=i)

        # Create 2-5 logs per day
        daily_logs = min(5, max(2, (30 - i) // 6))  # More recent = more usage

        for j in range(daily_logs):
            log_time = access_time - timedelta(hours=j * 2)
            endpoint = ["/scenarios", "/endpoints", "/systems", "/pat-tokens"][j % 4]

            logs.append(TokenUsageLog(
                id=len(logs) + 1,
                customer_id="customer_123",
                token_id=1,
                endpoint_accessed=f"GET {endpoint}",
                ip_address=f"192.168.1.{100 + (i % 50)}",
                user_agent="smarttest-cli/1.0",
                accessed_at=log_time
            ))

    return logs


class TestPATTokenUsageLogging:
    """Test PAT token usage logging functionality"""

    def test_log_token_usage_success(self, mock_db):
        """Test successful token usage logging"""

        # Test the logging method
        PATTokenService.log_token_usage(
            db=mock_db,
            token_id=1,
            customer_id="customer_123",
            endpoint_accessed="GET /scenarios",
            ip_address="192.168.1.100",
            user_agent="smarttest-cli/1.0"
        )

        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        # Check the logged data structure
        logged_usage = mock_db.add.call_args[0][0]
        assert logged_usage.customer_id == "customer_123"
        assert logged_usage.token_id == 1
        assert logged_usage.endpoint_accessed == "GET /scenarios"
        assert logged_usage.ip_address == "192.168.1.100"
        assert logged_usage.user_agent == "smarttest-cli/1.0"

    def test_log_token_usage_with_exception(self, mock_db):
        """Test token usage logging handles exceptions gracefully"""

        # Mock database exception
        mock_db.commit.side_effect = Exception("Database error")

        # Should not raise exception even if logging fails
        try:
            PATTokenService.log_token_usage(
                db=mock_db,
                token_id=1,
                customer_id="customer_123",
                endpoint_accessed="GET /scenarios"
            )
        except Exception:
            pytest.fail("log_token_usage should not raise exceptions")

    @patch('service.PATTokenService.PATTokenService.validate_pat_token')
    def test_validate_pat_token_with_usage_logging(self, mock_validate, mock_db, pat_token):
        """Test PAT token validation with usage logging"""

        mock_validate.return_value = pat_token

        result = PATTokenService.validate_pat_token_with_usage_logging(
            db=mock_db,
            token="st_pat_test_token",
            endpoint_accessed="GET /scenarios",
            ip_address="192.168.1.100",
            user_agent="smarttest-cli/1.0"
        )

        # Verify token validation was called
        mock_validate.assert_called_once_with(mock_db, "st_pat_test_token")

        # Verify usage was logged
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        # Verify return value
        assert result == pat_token

    @patch('service.PATTokenService.PATTokenService.validate_pat_token')
    def test_validate_pat_token_with_usage_logging_invalid_token(self, mock_validate, mock_db):
        """Test PAT token validation with usage logging for invalid token"""

        mock_validate.return_value = None

        result = PATTokenService.validate_pat_token_with_usage_logging(
            db=mock_db,
            token="st_pat_invalid_token",
            endpoint_accessed="GET /scenarios"
        )

        # Verify token validation was called
        mock_validate.assert_called_once_with(mock_db, "st_pat_invalid_token")

        # Verify usage was NOT logged for invalid token
        mock_db.add.assert_not_called()

        # Verify return value
        assert result is None


class TestPATTokenUsageStatistics:
    """Test PAT token usage statistics functionality"""

    def test_get_token_usage_statistics_success(self, mock_db, pat_token, usage_logs):
        """Test successful retrieval of token usage statistics"""

        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = pat_token
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = usage_logs

        result = PATTokenService.get_token_usage_statistics(
            db=mock_db,
            customer_id="customer_123",
            token_id=1,
            days=30
        )

        # Verify structure
        assert "token_id" in result
        assert "usage_summary" in result
        assert "daily_usage" in result
        assert "recent_ip_addresses" in result

        # Verify token_id
        assert result["token_id"] == 1

        # Verify usage summary
        summary = result["usage_summary"]
        assert "total_requests" in summary
        assert "last_used_at" in summary
        assert "most_used_endpoint" in summary
        assert "requests_last_7_days" in summary
        assert "requests_last_30_days" in summary

        # Verify counts
        assert summary["total_requests"] == len(usage_logs)
        assert summary["requests_last_30_days"] == len(usage_logs)

        # Verify daily usage format
        daily_usage = result["daily_usage"]
        assert isinstance(daily_usage, list)
        if daily_usage:
            first_entry = daily_usage[0]
            assert "date" in first_entry
            assert "request_count" in first_entry
            assert "unique_endpoints" in first_entry

        # Verify recent IP addresses
        recent_ips = result["recent_ip_addresses"]
        assert isinstance(recent_ips, list)
        assert len(recent_ips) <= 5  # Should limit to 5 IPs

    def test_get_token_usage_statistics_token_not_found(self, mock_db):
        """Test token usage statistics for non-existent token"""

        # Mock token not found
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            PATTokenService.get_token_usage_statistics(
                db=mock_db,
                customer_id="customer_123",
                token_id=999,
                days=30
            )

        assert exc_info.value.status_code == 404
        assert "Token not found" in str(exc_info.value.detail)

    def test_get_token_usage_statistics_no_usage(self, mock_db, pat_token):
        """Test token usage statistics with no usage logs"""

        # Mock token exists but no usage logs
        mock_db.query.return_value.filter.return_value.first.return_value = pat_token
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = []

        result = PATTokenService.get_token_usage_statistics(
            db=mock_db,
            customer_id="customer_123",
            token_id=1,
            days=30
        )

        # Verify empty usage
        summary = result["usage_summary"]
        assert summary["total_requests"] == 0
        assert summary["requests_last_7_days"] == 0
        assert summary["requests_last_30_days"] == 0
        assert summary["most_used_endpoint"] is None

        assert result["daily_usage"] == []
        assert result["recent_ip_addresses"] == []

    def test_get_token_usage_statistics_date_filtering(self, mock_db, pat_token, usage_logs):
        """Test token usage statistics with custom date range"""

        # Filter logs to last 7 days for this test
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_logs = [log for log in usage_logs if log.accessed_at >= seven_days_ago]

        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = pat_token
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = recent_logs

        result = PATTokenService.get_token_usage_statistics(
            db=mock_db,
            customer_id="customer_123",
            token_id=1,
            days=7
        )

        # Verify filtered results
        summary = result["usage_summary"]
        assert summary["total_requests"] == len(recent_logs)
        assert summary["requests_last_7_days"] == len(recent_logs)


class TestPATTokenUsageRoutes:
    """Test PAT token usage statistics API endpoints"""

    @patch('routes.pat_token_routes.PATTokenService.get_token_usage_statistics')
    @patch('routes.pat_token_routes.require_client_or_admin')
    def test_get_pat_token_usage_endpoint_success(self, mock_auth, mock_stats, customer):
        """Test successful GET /pat-tokens/{id}/usage endpoint"""

        from main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Mock authentication
        mock_auth.return_value = customer

        # Mock statistics response
        mock_stats.return_value = {
            "token_id": 1,
            "usage_summary": {
                "total_requests": 100,
                "last_used_at": datetime.now(timezone.utc).isoformat(),
                "most_used_endpoint": "GET /scenarios",
                "requests_last_7_days": 20,
                "requests_last_30_days": 80
            },
            "daily_usage": [
                {
                    "date": "2024-01-20",
                    "request_count": 5,
                    "unique_endpoints": 2
                }
            ],
            "recent_ip_addresses": [
                {
                    "ip_address": "192.168.1.100",
                    "last_seen": datetime.now(timezone.utc)
                }
            ]
        }

        # Mock database dependency
        def mock_get_db():
            return Mock()

        app.dependency_overrides = {
            "routes.pat_token_routes.get_db": mock_get_db,
            "routes.pat_token_routes.require_client_or_admin": lambda: customer
        }

        try:
            response = client.get("/pat-tokens/1/usage")

            assert response.status_code == 200

            data = response.json()
            assert data["token_id"] == 1
            assert "usage_summary" in data
            assert "daily_usage" in data
            assert "recent_ip_addresses" in data

        finally:
            app.dependency_overrides.clear()

    @patch('routes.pat_token_routes.require_client_or_admin')
    def test_get_pat_token_usage_endpoint_invalid_days(self, mock_auth, customer):
        """Test GET /pat-tokens/{id}/usage endpoint with invalid days parameter"""

        from main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Mock authentication
        mock_auth.return_value = customer

        def mock_get_db():
            return Mock()

        app.dependency_overrides = {
            "routes.pat_token_routes.get_db": mock_get_db,
            "routes.pat_token_routes.require_client_or_admin": lambda: customer
        }

        try:
            # Test invalid days (too high)
            response = client.get("/pat-tokens/1/usage?days=500")
            assert response.status_code == 400
            assert "Days parameter must be between 1 and 365" in response.json()["detail"]

            # Test invalid days (too low)
            response = client.get("/pat-tokens/1/usage?days=0")
            assert response.status_code == 400
            assert "Days parameter must be between 1 and 365" in response.json()["detail"]

        finally:
            app.dependency_overrides.clear()

    def test_pat_token_info_includes_usage_endpoint(self):
        """Test that PAT token info endpoint includes the new usage endpoint"""

        from main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        response = client.get("/pat-tokens/info")

        assert response.status_code == 200

        data = response.json()
        assert "endpoints" in data
        assert "usage" in data["endpoints"]
        assert data["endpoints"]["usage"] == "GET /pat-tokens/{id}/usage"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])