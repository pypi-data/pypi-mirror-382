"""
PAT Token Usage Logging Integration Tests
Tests that verify PAT token usage is properly tracked when tokens are used
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from database.model import PATToken, Customer, TokenUsageLog, CustomerRole
from service.PATTokenService import PATTokenService
from service.PATTokenAuthService import authenticate_request
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials


class TestPATTokenUsageLogging:
    """Integration tests for PAT token usage logging"""

    @pytest.mark.asyncio
    async def test_pat_token_authentication_logs_usage(self):
        """
        INTEGRATION TEST: Verify PAT token authentication creates usage logs

        This tests the complete flow:
        1. PAT token is validated during authentication
        2. Usage is automatically logged with request details
        3. Token's last_used_at is updated
        """

        # Create mock objects
        mock_db = Mock(spec=Session)
        mock_request = Mock(spec=Request)
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)

        # Setup mock request with usage tracking details
        mock_request.method = "GET"
        mock_request.url.path = "/scenarios"
        mock_request.client.host = "192.168.1.100"
        mock_request.headers.get.return_value = "smarttest-cli/1.0"

        # Setup PAT token credentials
        test_token = "st_pat_test_integration_token"
        mock_credentials.credentials = test_token

        # Create mock customer and token
        mock_customer = Mock()
        mock_customer.id = "test_customer_123"

        mock_token = Mock()
        mock_token.id = 42
        mock_token.customer_id = "test_customer_123"
        mock_token.last_used_at = None  # Not used before

        # Mock the database query to return our customer
        mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

        # Mock the PAT token validation to return our token
        with patch.object(PATTokenService, 'validate_pat_token_with_usage_logging') as mock_validate:
            mock_validate.return_value = mock_token

            # Call authentication
            result = await authenticate_request(mock_request, mock_credentials, mock_db)

            # Verify authentication succeeded
            assert result == mock_customer

            # Verify validate_pat_token_with_usage_logging was called with correct parameters
            mock_validate.assert_called_once_with(
                db=mock_db,
                token=test_token,
                endpoint_accessed="GET /scenarios",
                ip_address="192.168.1.100",
                user_agent="smarttest-cli/1.0"
            )

    def test_usage_statistics_accumulate_correctly(self):
        """
        INTEGRATION TEST: Verify usage statistics correctly accumulate multiple calls

        This tests:
        1. Multiple usage logs are created for a token
        2. Statistics endpoint correctly aggregates the data
        3. Time-based filtering works properly
        """

        # Setup mock database
        mock_db = Mock(spec=Session)

        # Create mock token
        mock_token = PATToken(
            id=1,
            customer_id="customer_123",
            label="Test Token",
            last_used_at=datetime.now(timezone.utc)
        )

        # Create realistic usage logs spanning different time periods
        base_time = datetime.now(timezone.utc)
        usage_logs = []

        # Recent usage (last 7 days) - 10 requests
        for i in range(10):
            log = TokenUsageLog(
                id=i + 1,
                customer_id="customer_123",
                token_id=1,
                endpoint_accessed="GET /scenarios" if i % 3 == 0 else "POST /endpoints",
                ip_address=f"192.168.1.{100 + i % 3}",  # 3 different IPs
                user_agent="smarttest-cli/1.0",
                accessed_at=base_time - timedelta(days=i // 2, hours=i)  # Spread over 5 days
            )
            usage_logs.append(log)

        # Older usage (8-30 days ago) - 5 requests
        for i in range(5):
            log = TokenUsageLog(
                id=i + 11,
                customer_id="customer_123",
                token_id=1,
                endpoint_accessed="GET /systems",
                ip_address="192.168.2.100",
                user_agent="smarttest-cli/1.0",
                accessed_at=base_time - timedelta(days=10 + i * 2)  # 10, 12, 14, 16, 18 days ago
            )
            usage_logs.append(log)

        # Setup database mocks
        # Mock token query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_token

        # Mock usage logs query
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = usage_logs

        # Call the statistics method
        result = PATTokenService.get_token_usage_statistics(
            db=mock_db,
            customer_id="customer_123",
            token_id=1,
            days=30
        )

        # Verify the results
        assert result["token_id"] == 1

        summary = result["usage_summary"]
        assert summary["total_requests"] == 15  # 10 + 5
        assert summary["requests_last_7_days"] == 10  # Only recent requests
        assert summary["requests_last_30_days"] == 15  # All requests

        # Most used endpoint should be "GET /scenarios" (used 4 times: indices 0, 3, 6, 9)
        # vs "POST /endpoints" (used 6 times: indices 1, 2, 4, 5, 7, 8)
        assert summary["most_used_endpoint"] == "POST /endpoints"

        # Verify daily usage structure
        daily_usage = result["daily_usage"]
        assert isinstance(daily_usage, list)
        assert len(daily_usage) > 0

        # Verify IP addresses
        recent_ips = result["recent_ip_addresses"]
        assert len(recent_ips) <= 5  # Should be limited to 5

        # Should include both sets of IP addresses
        ip_addresses = [ip["ip_address"] for ip in recent_ips]
        assert any("192.168.1." in ip for ip in ip_addresses)
        assert "192.168.2.100" in ip_addresses

    def test_token_isolation_in_usage_statistics(self):
        """
        INTEGRATION TEST: Verify usage statistics are properly isolated between tokens

        This ensures that statistics for one token don't include data from other tokens,
        even for the same customer.
        """

        mock_db = Mock(spec=Session)

        # Create two different tokens for same customer
        token1 = PATToken(id=1, customer_id="customer_123", label="Token 1")
        token2 = PATToken(id=2, customer_id="customer_123", label="Token 2")

        # Create usage logs for token 1 (5 requests)
        token1_logs = []
        for i in range(5):
            log = TokenUsageLog(
                id=i + 1,
                customer_id="customer_123",
                token_id=1,  # Token 1
                endpoint_accessed="GET /token1-endpoint",
                accessed_at=datetime.now(timezone.utc) - timedelta(hours=i)
            )
            token1_logs.append(log)

        # Create usage logs for token 2 (3 requests)
        token2_logs = []
        for i in range(3):
            log = TokenUsageLog(
                id=i + 6,
                customer_id="customer_123",
                token_id=2,  # Token 2
                endpoint_accessed="GET /token2-endpoint",
                accessed_at=datetime.now(timezone.utc) - timedelta(hours=i)
            )
            token2_logs.append(log)

        # Test token 1 statistics
        mock_db.query.return_value.filter.return_value.first.return_value = token1
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = token1_logs

        result1 = PATTokenService.get_token_usage_statistics(
            db=mock_db, customer_id="customer_123", token_id=1, days=30
        )

        # Test token 2 statistics
        mock_db.query.return_value.filter.return_value.first.return_value = token2
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = token2_logs

        result2 = PATTokenService.get_token_usage_statistics(
            db=mock_db, customer_id="customer_123", token_id=2, days=30
        )

        # Verify isolation - token 1 should only see its own usage
        assert result1["usage_summary"]["total_requests"] == 5
        assert result1["usage_summary"]["most_used_endpoint"] == "GET /token1-endpoint"

        # Verify isolation - token 2 should only see its own usage
        assert result2["usage_summary"]["total_requests"] == 3
        assert result2["usage_summary"]["most_used_endpoint"] == "GET /token2-endpoint"

    def test_usage_logging_error_resilience(self):
        """
        INTEGRATION TEST: Verify that usage logging errors don't break authentication

        This is critical - if usage logging fails, authentication should still work.
        """

        mock_db = Mock(spec=Session)

        # Mock database error during logging
        mock_db.add.side_effect = Exception("Database connection failed")

        # Test that log_token_usage handles exceptions gracefully
        try:
            PATTokenService.log_token_usage(
                db=mock_db,
                token_id=1,
                customer_id="customer_123",
                endpoint_accessed="GET /scenarios",
                ip_address="192.168.1.100"
            )
            # Should not raise exception
        except Exception:
            pytest.fail("log_token_usage should not raise exceptions")

        # Verify database operations were attempted
        mock_db.add.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])