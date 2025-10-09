import types
from types import SimpleNamespace
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from main import app


def client():
    return TestClient(app)


def test_generate_validations_rejects_when_quota_exhausted(monkeypatch):
    """
    When validation generations are exhausted, the endpoint should return 403 with a clear message.
    """
    test_client = TestClient(app)

    # Patch auth to simulate a signed-in customer with id "user_1"
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_1")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Patch scenario and endpoint lookups
    from service import ScenarioService, EndpointService
    monkeypatch.setattr(ScenarioService, "get_scenario_by_id", lambda db, sid: SimpleNamespace(id=1, endpoint_id=1, name="S1"))
    monkeypatch.setattr(EndpointService, "get_endpoint_by_id", lambda db, eid: SimpleNamespace(id=1, system_id=1, method="GET", endpoint="/x"))

    # Patch access check to no-op
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", lambda db, user_id, system_id: True)

    # Patch execute to avoid network
    from service import ScenarioService as SS
    monkeypatch.setattr(SS, "execute_scenario_only", lambda db, sid, uid: {"success": True, "status_code": 200, "headers": {}, "body": {}})

    # Patch GPT generation to avoid OpenAI
    import gpt as gpt_module
    monkeypatch.setattr(gpt_module, "generate_validations_for_scenario", lambda **kwargs: [{"validation_text": "foo"}])

    # Patch subscription limits to simulate exhausted validation generations
    from service import SubscriptionService as SubSvc

    def fake_get_usage_limits(db, user_id):
        # Provide the minimal attributes the route logic will read
        return SimpleNamespace(
            # runs
            runs_limit=100, runs_used=0, runs_remaining=100,
            # validations
            validation_generations_limit=3,
            validation_generations_used=3,
            validation_generations_remaining=0,
        )

    monkeypatch.setattr(SubSvc.SubscriptionService, "get_usage_limits", staticmethod(fake_get_usage_limits))

    # Perform request
    resp = test_client.post("/scenario/1/generate-validations", headers={"Authorization": "Bearer test"})

    assert resp.status_code == 403
    detail = resp.json().get("detail", "")
    assert "Validation generation limit reached" in detail or "only have" in detail


def test_generate_validations_increments_usage_on_success_and_not_runs(monkeypatch):
    """
    On successful validation generation: increments validation_generations_used but not runs_executed.
    """
    test_client = TestClient(app)

    # Auth
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_2")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Scenario and endpoint
    from service import ScenarioService, EndpointService
    monkeypatch.setattr(ScenarioService, "get_scenario_by_id", lambda db, sid: SimpleNamespace(id=2, endpoint_id=2, name="S2"))
    monkeypatch.setattr(EndpointService, "get_endpoint_by_id", lambda db, eid: SimpleNamespace(id=2, system_id=2, method="GET", endpoint="/y"))

    # Access check
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", lambda db, user_id, system_id: True)

    # Execute scenario without incrementing runs
    from service import ScenarioService as SS
    monkeypatch.setattr(SS, "execute_scenario_only", lambda db, sid, uid: {"success": True, "status_code": 200, "headers": {}, "body": {}})

    # GPT
    import gpt as gpt_module
    monkeypatch.setattr(gpt_module, "generate_validations_for_scenario", lambda **kwargs: [{"validation_text": "foo"}])

    # Track calls to increment methods
    calls = {"val_gens": 0, "runs": 0}

    from service import SubscriptionService as SubSvc

    def fake_get_usage_limits(db, user_id):
        return SimpleNamespace(
            runs_limit=100, runs_used=0, runs_remaining=100,
            validation_generations_limit=5,
            validation_generations_used=1,
            validation_generations_remaining=4,
        )

    def fake_increment_validation_generations(db, user_id, count=1):
        calls["val_gens"] += count
        return True

    # Ensure any runs increment is not called by this flow
    def fake_increment_usage(db, user_id, usage_type, count=1):
        if usage_type == "runs_executed":
            calls["runs"] += count
        return True

    monkeypatch.setattr(SubSvc.SubscriptionService, "get_usage_limits", staticmethod(fake_get_usage_limits))
    # We'll add this method in implementation; patch it now for TDD
    monkeypatch.setattr(SubSvc.SubscriptionService, "increment_validation_generations", staticmethod(fake_increment_validation_generations))
    monkeypatch.setattr(SubSvc.SubscriptionService, "increment_usage", staticmethod(fake_increment_usage))

    resp = test_client.post("/scenario/2/generate-validations", headers={"Authorization": "Bearer test"})

    assert resp.status_code == 200
    # Validation generations incremented once
    assert calls["val_gens"] == 1
    # Runs should not increment for validation generation path
    assert calls["runs"] == 0


def test_validation_generation_skips_execution_history(monkeypatch):
    """
    Test that validation generation calls execute_scenario_only with skip_execution_history=True
    to prevent execution history from being saved for validation generation requests.
    """
    test_client = TestClient(app)

    # Patch auth to simulate a signed-in customer
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_1")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Patch scenario and endpoint lookups
    from service import ScenarioService, EndpointService
    monkeypatch.setattr(ScenarioService, "get_scenario_by_id", 
                       lambda db, sid: SimpleNamespace(id=1, endpoint_id=1, name="S1"))
    monkeypatch.setattr(EndpointService, "get_endpoint_by_id", 
                       lambda db, eid: SimpleNamespace(id=1, system_id=1, method="GET", endpoint="/x"))

    # Patch access check
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", 
                       lambda db, user_id, system_id: True)

    # Track calls to execute_scenario_only to verify skip_execution_history flag
    execute_calls = []
    
    def mock_execute_scenario_only(db, scenario_id, user_id, skip_execution_history=False):
        execute_calls.append({
            "scenario_id": scenario_id,
            "user_id": user_id,
            "skip_execution_history": skip_execution_history
        })
        return {
            "success": True,
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"message": "success"}
        }
    
    # Patch execute_scenario_only to track calls
    from service import ScenarioService as SS
    monkeypatch.setattr(SS, "execute_scenario_only", mock_execute_scenario_only)

    # Patch GPT generation to avoid OpenAI
    import gpt as gpt_module
    monkeypatch.setattr(gpt_module, "generate_validations_for_scenario", 
                       lambda **kwargs: [{"validation_text": "status code should be 200"}])

    # Patch subscription limits with sufficient quota
    from service import SubscriptionService as SubSvc

    def fake_get_usage_limits(db, user_id):
        return SimpleNamespace(
            runs_limit=100, runs_used=0, runs_remaining=100,
            validation_generations_limit=10,
            validation_generations_used=0,
            validation_generations_remaining=10,
            subscription=SimpleNamespace(
                tier=SimpleNamespace(
                    auto_validation_generation_enabled=True
                )
            )
        )

    def fake_increment_validation_generations(db, user_id, count=1):
        return True

    monkeypatch.setattr(SubSvc.SubscriptionService, "get_usage_limits", staticmethod(fake_get_usage_limits))
    monkeypatch.setattr(SubSvc.SubscriptionService, "increment_validation_generations", 
                       staticmethod(fake_increment_validation_generations))

    # Call the validation generation endpoint
    resp = test_client.post("/scenario/1/generate-validations", headers={"Authorization": "Bearer test"})

    assert resp.status_code == 200
    
    # Verify that execute_scenario_only was called with skip_execution_history=True
    assert len(execute_calls) == 1
    call = execute_calls[0]
    assert call["scenario_id"] == 1
    assert call["user_id"] == "user_1"
    assert call["skip_execution_history"] is True, "Validation generation should skip execution history"


