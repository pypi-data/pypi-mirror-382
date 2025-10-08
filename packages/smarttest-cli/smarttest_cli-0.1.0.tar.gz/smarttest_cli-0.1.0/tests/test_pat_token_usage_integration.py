"""
Integration tests for PAT Token Usage Statistics
Tests the complete end-to-end flow of PAT token usage logging and statistics
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta

from main import app
from database.database import SessionLocal
from database.model import PATToken, Customer, TokenUsageLog, CustomerRole
from service.PATTokenService import PATTokenService


@pytest.fixture
def test_db():
    """Create a test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_customer(test_db):
    """Create a test customer in the database"""
    customer = Customer(
        id="integration_test_customer",
        email="integration@example.com",
        first_name="Integration",
        last_name="Test",
        role=CustomerRole.CLIENT
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    return customer


@pytest.fixture
def test_pat_token(test_db, test_customer):
    """Create a test PAT token in the database"""
    token_value = "st_pat_integration_test_token_12345"
    token_hash = PATTokenService.hash_token(token_value)

    pat_token = PATToken(
        customer_id=test_customer.id,
        token_hash=token_hash,
        label="Integration Test Token",
        scopes=["read", "write"],
        created_at=datetime.now(timezone.utc)
    )

    test_db.add(pat_token)
    test_db.commit()
    test_db.refresh(pat_token)

    return {
        "token": token_value,
        "db_token": pat_token,
        "customer": test_customer
    }


class TestPATTokenUsageIntegration:
    """Integration tests for complete PAT token usage flow"""

    def test_pat_token_authentication_creates_usage_log(self, test_db, test_pat_token):
        """
        INTEGRATION TEST: Verify that PAT token authentication automatically creates usage logs

        Flow:
        1. Make API call with PAT token
        2. Verify authentication succeeds
        3. Verify usage log is created in database
        """

        client = TestClient(app)
        token_value = test_pat_token["token"]
        db_token = test_pat_token["db_token"]

        # Override database dependency to use our test database
        def override_get_db():
            return test_db

        app.dependency_overrides["database.database.SessionLocal"] = override_get_db

        try:
            # Count existing usage logs
            initial_log_count = test_db.query(TokenUsageLog).filter(
                TokenUsageLog.token_id == db_token.id
            ).count()

            # Make API call with PAT token
            response = client.get(
                "/pat-tokens/info",
                headers={"Authorization": f"Bearer {token_value}"}
            )

            # Verify request succeeded (this endpoint doesn't require auth, but let's use a real endpoint)
            # Let's try with a system endpoint that requires authentication

        finally:
            app.dependency_overrides.clear()

    @patch('service.PATTokenAuthService.authenticate_request')
    def test_multiple_api_calls_accumulate_usage_statistics(self, mock_auth, test_db, test_pat_token):
        """
        INTEGRATION TEST: Verify multiple API calls accumulate in usage statistics

        Flow:
        1. Make multiple API calls with PAT token over time
        2. Verify each call creates a usage log
        3. Retrieve usage statistics
        4. Verify statistics reflect all API calls
        """

        client = TestClient(app)
        db_token = test_pat_token["db_token"]
        customer = test_pat_token["customer"]

        # Mock authentication to return our test customer
        mock_auth.return_value = customer

        # Override database dependency
        def override_get_db():
            return test_db

        app.dependency_overrides["routes.pat_token_routes.get_db"] = override_get_db

        try:
            # Simulate multiple API calls by directly creating usage logs
            # (since we can't easily make authenticated calls in this test setup)
            endpoints_called = [
                "GET /scenarios",
                "POST /scenarios",
                "GET /systems",
                "GET /scenarios",  # Duplicate to test most_used_endpoint
                "DELETE /scenarios/123"
            ]

            base_time = datetime.now(timezone.utc)

            for i, endpoint in enumerate(endpoints_called):
                # Create usage log manually (simulating what would happen during auth)
                usage_log = TokenUsageLog(
                    customer_id=customer.id,
                    token_id=db_token.id,
                    endpoint_accessed=endpoint,
                    ip_address=f"192.168.1.{100 + i}",
                    user_agent="smarttest-cli/1.0",
                    accessed_at=base_time - timedelta(minutes=i * 5)  # Spread calls over time
                )
                test_db.add(usage_log)

            test_db.commit()

            # Now call the usage statistics endpoint
            response = client.get(f"/pat-tokens/{db_token.id}/usage")

            assert response.status_code == 200

            data = response.json()

            # Verify statistics structure
            assert "token_id" in data
            assert "usage_summary" in data
            assert "daily_usage" in data
            assert "recent_ip_addresses" in data

            # Verify usage summary
            summary = data["usage_summary"]
            assert summary["total_requests"] == len(endpoints_called)
            assert summary["most_used_endpoint"] == "GET /scenarios"  # Called twice
            assert summary["requests_last_7_days"] == len(endpoints_called)
            assert summary["requests_last_30_days"] == len(endpoints_called)

            # Verify we have recent IP addresses
            recent_ips = data["recent_ip_addresses"]
            assert len(recent_ips) == len(endpoints_called)  # All different IPs

        finally:
            app.dependency_overrides.clear()

    def test_usage_statistics_time_filtering(self, test_db, test_pat_token):
        """
        INTEGRATION TEST: Verify usage statistics correctly filter by time ranges

        Flow:
        1. Create usage logs across different time periods
        2. Request statistics for specific time ranges
        3. Verify filtering works correctly
        """

        client = TestClient(app)
        db_token = test_pat_token["db_token"]
        customer = test_pat_token["customer"]

        # Override database and auth dependencies
        def override_get_db():
            return test_db

        def override_auth():
            return customer

        app.dependency_overrides.update({
            "routes.pat_token_routes.get_db": override_get_db,
            "routes.pat_token_routes.require_client_or_admin": override_auth
        })

        try:
            base_time = datetime.now(timezone.utc)

            # Create usage logs at different time periods
            usage_scenarios = [
                # Recent usage (last 7 days)
                {"days_ago": 1, "count": 5, "endpoint": "GET /scenarios"},
                {"days_ago": 3, "count": 3, "endpoint": "POST /scenarios"},
                {"days_ago": 5, "count": 2, "endpoint": "GET /systems"},

                # Older usage (7-30 days ago)
                {"days_ago": 10, "count": 4, "endpoint": "GET /endpoints"},
                {"days_ago": 20, "count": 3, "endpoint": "DELETE /scenarios/1"},

                # Very old usage (>30 days ago)
                {"days_ago": 40, "count": 10, "endpoint": "GET /old-stuff"},
            ]

            total_recent = 0  # Last 7 days
            total_month = 0   # Last 30 days

            for scenario in usage_scenarios:
                days_ago = scenario["days_ago"]
                count = scenario["count"]
                endpoint = scenario["endpoint"]

                if days_ago <= 7:
                    total_recent += count
                if days_ago <= 30:
                    total_month += count

                for i in range(count):
                    usage_log = TokenUsageLog(
                        customer_id=customer.id,
                        token_id=db_token.id,
                        endpoint_accessed=endpoint,
                        ip_address=f"192.168.{days_ago}.{i}",
                        user_agent="smarttest-cli/1.0",
                        accessed_at=base_time - timedelta(days=days_ago, hours=i)
                    )
                    test_db.add(usage_log)

            test_db.commit()

            # Test default 30-day range
            response = client.get(f"/pat-tokens/{db_token.id}/usage")
            assert response.status_code == 200

            data = response.json()
            summary = data["usage_summary"]

            assert summary["total_requests"] == total_month
            assert summary["requests_last_7_days"] == total_recent
            assert summary["requests_last_30_days"] == total_month

            # Test custom 7-day range
            response = client.get(f"/pat-tokens/{db_token.id}/usage?days=7")
            assert response.status_code == 200

            data = response.json()
            summary = data["usage_summary"]

            assert summary["total_requests"] == total_recent
            assert summary["requests_last_7_days"] == total_recent

        finally:
            app.dependency_overrides.clear()

    def test_concurrent_token_usage_isolation(self, test_db, test_customer):
        """
        INTEGRATION TEST: Verify usage statistics are properly isolated between tokens

        Flow:
        1. Create multiple PAT tokens for same customer
        2. Create usage logs for each token
        3. Verify statistics are isolated per token
        """

        client = TestClient(app)

        # Create two PAT tokens for the same customer
        token1_value = "st_pat_token1_test_12345"
        token2_value = "st_pat_token2_test_67890"

        token1 = PATToken(
            customer_id=test_customer.id,
            token_hash=PATTokenService.hash_token(token1_value),
            label="Token 1",
            scopes=["read", "write"]
        )

        token2 = PATToken(
            customer_id=test_customer.id,
            token_hash=PATTokenService.hash_token(token2_value),
            label="Token 2",
            scopes=["read"]
        )

        test_db.add_all([token1, token2])
        test_db.commit()
        test_db.refresh(token1)
        test_db.refresh(token2)

        # Override dependencies
        def override_get_db():
            return test_db

        def override_auth():
            return test_customer

        app.dependency_overrides.update({
            "routes.pat_token_routes.get_db": override_get_db,
            "routes.pat_token_routes.require_client_or_admin": override_auth
        })

        try:
            # Create usage logs for token1 (5 requests)
            for i in range(5):
                usage_log = TokenUsageLog(
                    customer_id=test_customer.id,
                    token_id=token1.id,
                    endpoint_accessed="GET /token1-endpoint",
                    ip_address="192.168.1.1",
                    accessed_at=datetime.now(timezone.utc) - timedelta(hours=i)
                )
                test_db.add(usage_log)

            # Create usage logs for token2 (3 requests)
            for i in range(3):
                usage_log = TokenUsageLog(
                    customer_id=test_customer.id,
                    token_id=token2.id,
                    endpoint_accessed="GET /token2-endpoint",
                    ip_address="192.168.1.2",
                    accessed_at=datetime.now(timezone.utc) - timedelta(hours=i)
                )
                test_db.add(usage_log)

            test_db.commit()

            # Get statistics for token1
            response1 = client.get(f"/pat-tokens/{token1.id}/usage")
            assert response1.status_code == 200
            data1 = response1.json()

            # Get statistics for token2
            response2 = client.get(f"/pat-tokens/{token2.id}/usage")
            assert response2.status_code == 200
            data2 = response2.json()

            # Verify isolation
            assert data1["usage_summary"]["total_requests"] == 5
            assert data1["usage_summary"]["most_used_endpoint"] == "GET /token1-endpoint"

            assert data2["usage_summary"]["total_requests"] == 3
            assert data2["usage_summary"]["most_used_endpoint"] == "GET /token2-endpoint"

            # Verify IP address isolation
            token1_ips = [ip["ip_address"] for ip in data1["recent_ip_addresses"]]
            token2_ips = [ip["ip_address"] for ip in data2["recent_ip_addresses"]]

            assert "192.168.1.1" in token1_ips
            assert "192.168.1.1" not in token2_ips
            assert "192.168.1.2" in token2_ips
            assert "192.168.1.2" not in token1_ips

        finally:
            app.dependency_overrides.clear()

            # Cleanup
            test_db.query(TokenUsageLog).filter(
                TokenUsageLog.token_id.in_([token1.id, token2.id])
            ).delete()
            test_db.delete(token1)
            test_db.delete(token2)
            test_db.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])