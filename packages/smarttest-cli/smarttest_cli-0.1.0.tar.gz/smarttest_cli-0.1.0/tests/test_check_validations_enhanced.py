"""
Test enhanced check-validations endpoint with record_run and increment_usage
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from main import app
from service.AuthService import require_auth


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
    # Clear rate limiter state before each test
    from service.RateLimitService import rate_limiter
    rate_limiter._customer_requests.clear()

    app.dependency_overrides[require_auth] = lambda: mock_customer
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def mock_scenario_data():
    """Mock scenario and endpoint data"""
    scenario = Mock()
    scenario.id = 1
    scenario.endpoint_id = 2
    validation1 = Mock()
    validation1.id = 1
    validation1.validation_text = "status == 200"
    validation1.description = "Check status"
    scenario.validations = [validation1]

    endpoint = Mock()
    endpoint.id = 2
    endpoint.system_id = 3

    return {"scenario": scenario, "endpoint": endpoint}


class TestCheckValidationsEnhanced:
    """Test enhanced check-validations endpoint"""

    def test_check_validations_basic(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test basic validation checking without record_run or increment_usage"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.get_validations_by_scenario_id', return_value=mock_scenario_data["scenario"].validations)

        # Mock GPT validation result
        mock_validation_result = Mock()
        mock_validation_result.model_dump.return_value = {"passed": 1, "failed": 0}
        mocker.patch('routes.scenario_routes.gpt.check_validations_with_assistant', return_value=mock_validation_result)

        request_body = {
            "http_status": 200,
            "headers": {"content-type": "application/json"},
            "payload": {"result": "success"}
        }

        response = client.post("/scenario/1/check-validations", json=request_body)

        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == 1
        assert data["validation_results"]["passed"] == 1
        assert data["validation_results"]["failed"] == 0
        assert data["total_validations"] == 1
        assert "checked_at" in data
        # Should not have run_id when record_run=false
        assert "run_id" not in data

    def test_check_validations_with_record_run(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test validation checking with record_run=true"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.get_validations_by_scenario_id', return_value=mock_scenario_data["scenario"].validations)

        # Mock GPT validation result
        mock_validation_result = Mock()
        mock_validation_result.model_dump.return_value = {"passed": 1, "failed": 0}
        mocker.patch('routes.scenario_routes.gpt.check_validations_with_assistant', return_value=mock_validation_result)

        # Mock run history creation
        mock_run_history = Mock()
        mock_run_history.id = 12345
        mocker.patch('routes.scenario_routes.create_scenario_run_history_entry', return_value=mock_run_history)

        request_body = {
            "http_status": 200,
            "headers": {"content-type": "application/json"},
            "payload": {"result": "success"}
        }

        response = client.post("/scenario/1/check-validations?record_run=true", json=request_body)

        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == 1
        assert data["run_id"] == 12345

        # Verify create_scenario_run_history_entry was called
        from routes.scenario_routes import create_scenario_run_history_entry
        create_scenario_run_history_entry.assert_called_once()

    def test_check_validations_with_increment_usage(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test validation checking with increment_usage=true"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.get_validations_by_scenario_id', return_value=mock_scenario_data["scenario"].validations)

        # Mock GPT validation result
        mock_validation_result = Mock()
        mock_validation_result.model_dump.return_value = {"passed": 1, "failed": 0}
        mocker.patch('routes.scenario_routes.gpt.check_validations_with_assistant', return_value=mock_validation_result)

        # Mock subscription service
        mocker.patch('routes.scenario_routes.SubscriptionService.increment_usage', return_value=True)

        request_body = {
            "http_status": 200,
            "headers": {"content-type": "application/json"},
            "payload": {"result": "success"}
        }

        response = client.post("/scenario/1/check-validations?increment_usage=true", json=request_body)

        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == 1

        # Verify increment_usage was called
        from routes.scenario_routes import SubscriptionService
        SubscriptionService.increment_usage.assert_called_once_with(mocker.ANY, "customer_123", "runs_executed", 1)

    def test_check_validations_with_both_params(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test validation checking with both record_run=true and increment_usage=true"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.get_validations_by_scenario_id', return_value=mock_scenario_data["scenario"].validations)

        # Mock GPT validation result
        mock_validation_result = Mock()
        mock_validation_result.model_dump.return_value = {"passed": 0, "failed": 1}
        mocker.patch('routes.scenario_routes.gpt.check_validations_with_assistant', return_value=mock_validation_result)

        # Mock run history creation
        mock_run_history = Mock()
        mock_run_history.id = 67890
        mocker.patch('routes.scenario_routes.create_scenario_run_history_entry', return_value=mock_run_history)

        # Mock subscription service
        mocker.patch('routes.scenario_routes.SubscriptionService.increment_usage', return_value=True)

        request_body = {
            "http_status": 200,  # Good HTTP status but validation failed
            "headers": {"content-type": "application/json"},
            "payload": {"result": "unexpected"}
        }

        response = client.post("/scenario/1/check-validations?record_run=true&increment_usage=true", json=request_body)

        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == 1
        assert data["run_id"] == 67890
        assert data["validation_results"]["passed"] == 0
        assert data["validation_results"]["failed"] == 1

        # Verify both services were called
        from routes.scenario_routes import create_scenario_run_history_entry, SubscriptionService
        create_scenario_run_history_entry.assert_called_once()
        SubscriptionService.increment_usage.assert_called_once()

    def test_check_validations_http_error_status(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test validation checking with HTTP error status code"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.get_validations_by_scenario_id', return_value=mock_scenario_data["scenario"].validations)

        # Mock GPT validation result
        mock_validation_result = Mock()
        mock_validation_result.model_dump.return_value = {"passed": 0, "failed": 0}
        mocker.patch('routes.scenario_routes.gpt.check_validations_with_assistant', return_value=mock_validation_result)

        # Mock run history creation - should capture "failure" status for HTTP error
        mock_run_history = Mock()
        mock_run_history.id = 55555
        create_mock = mocker.patch('routes.scenario_routes.create_scenario_run_history_entry', return_value=mock_run_history)

        request_body = {
            "http_status": 500,  # HTTP error
            "headers": {"content-type": "application/json"},
            "payload": {"error": "Internal server error"}
        }

        response = client.post("/scenario/1/check-validations?record_run=true", json=request_body)

        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == 55555

        # Verify that overall_status was set to "failure" for HTTP error
        call_args = create_mock.call_args[0][1]  # Get ScenarioRunHistoryCreate object
        assert call_args.overall_status == "failure"

    def test_check_validations_graceful_degradation(self, client, override_auth_dependency, mock_customer, mock_scenario_data, mocker):
        """Test that validation checking continues even if record_run or increment_usage fails"""
        # Mock service calls
        mocker.patch('routes.scenario_routes.get_scenario_by_id', return_value=mock_scenario_data["scenario"])
        mocker.patch('routes.scenario_routes.get_endpoint_by_id', return_value=mock_scenario_data["endpoint"])
        mocker.patch('routes.scenario_routes.check_user_system_access', return_value=None)
        mocker.patch('routes.scenario_routes.get_validations_by_scenario_id', return_value=mock_scenario_data["scenario"].validations)

        # Mock GPT validation result
        mock_validation_result = Mock()
        mock_validation_result.model_dump.return_value = {"passed": 1, "failed": 0}
        mocker.patch('routes.scenario_routes.gpt.check_validations_with_assistant', return_value=mock_validation_result)

        # Mock services to fail
        mocker.patch('routes.scenario_routes.create_scenario_run_history_entry', side_effect=Exception("DB error"))
        mocker.patch('routes.scenario_routes.SubscriptionService.increment_usage', side_effect=Exception("Subscription error"))

        request_body = {
            "http_status": 200,
            "headers": {"content-type": "application/json"},
            "payload": {"result": "success"}
        }

        # Should still succeed even though record_run and increment_usage fail
        response = client.post("/scenario/1/check-validations?record_run=true&increment_usage=true", json=request_body)

        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == 1
        assert data["validation_results"]["passed"] == 1
        # No run_id should be present due to failure
        assert "run_id" not in data