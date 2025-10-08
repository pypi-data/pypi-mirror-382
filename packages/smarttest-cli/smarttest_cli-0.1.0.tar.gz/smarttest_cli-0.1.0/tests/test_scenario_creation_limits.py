from types import SimpleNamespace
from fastapi.testclient import TestClient

from main import app


def client() -> TestClient:
    return TestClient(app)


def _limits(
    *,
    scenarios_limit_reached: bool = False,
    scenarios_limit: int = 10,
    scenarios_used: int = 0,
    scenarios_remaining: int = 10,
):
    # Minimal shape to satisfy route logic accesses
    return SimpleNamespace(
        # scenario counts
        scenarios_limit_reached=scenarios_limit_reached,
        scenarios_limit=scenarios_limit,
        scenarios_used=scenarios_used,
        scenarios_remaining=scenarios_remaining,
        # other fields that some paths may read (keep benign defaults)
        runs_limit=1000,
        runs_used=0,
        runs_remaining=1000,
        subscription=SimpleNamespace(tier=SimpleNamespace(auto_validation_generation_enabled=True)),
    )


def test_endpoint_generate_scenarios_increments_usage(monkeypatch):
    test_client = client()

    # Auth
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_ep_inc")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Access check noop
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", lambda db, user_id, system_id: True)

    # Mock endpoint lookups and DB save behavior
    saved = {"scenarios": []}
    from service import EndpointService as ES
    from database.schemas import Scenario as ScenarioSchema, ScenarioBase

    def fake_check_endpoint_exists(db, endpoint_id):
        return SimpleNamespace(
            id=endpoint_id,
            system_id=1,
            method="GET",
            endpoint="/users",
            raw_definition={},
            definitions=[],
            definitions_for_params=[],
            definitions_for_responses=[],
            default_success_endpoint_parameters=[],
            scenarios=saved["scenarios"],
        )

    def fake_override_scenarios(db, endpoint_model):
        # Convert ScenarioBase -> Scenario with IDs for response serialization
        converted = []
        next_id = 100
        for s in getattr(endpoint_model, "scenarios", []):
            converted.append(
                ScenarioSchema(
                    id=next_id,
                    name=s.name,
                    expected_http_status=getattr(s, "expected_http_status", 200),
                    requires_auth=getattr(s, "requires_auth", False),
                    auth_error=getattr(s, "auth_error", False),
                )
            )
            next_id += 1
        saved["scenarios"] = converted

    monkeypatch.setattr(ES, "check_endpoint_exists", fake_check_endpoint_exists)
    monkeypatch.setattr(ES, "override_scenarios", fake_override_scenarios)

    # GPT generation
    import gpt as gpt_module

    scenarios = [
        ScenarioBase(name="S1", expected_http_status=200, requires_auth=False),
        ScenarioBase(name="S2", expected_http_status=200, requires_auth=False),
        ScenarioBase(name="S3", expected_http_status=200, requires_auth=False),
    ]

    monkeypatch.setattr(
        gpt_module,
        "create_scenarios_for_endpoint",
        lambda endpoint, customer_id=None, db=None: (True, "ok", scenarios),
    )

    # Limits and usage tracking
    from service import SubscriptionService as SubSvc

    monkeypatch.setattr(SubSvc.SubscriptionService, "get_usage_limits", staticmethod(lambda db, uid: _limits(scenarios_remaining=10)))

    calls = {"inc": []}

    def fake_increment_usage(db, uid, usage_type, count=1):
        calls["inc"].append((usage_type, count))
        return True

    monkeypatch.setattr(SubSvc.SubscriptionService, "increment_usage", staticmethod(fake_increment_usage))

    # Execute
    resp = test_client.get("/endpoints/1/generate-scenarios-gpt", headers={"Authorization": "Bearer t"})

    assert resp.status_code == 200, resp.text
    # Should increment scenarios_created by the actual count created (3)
    assert ("scenarios_created", 3) in calls["inc"], f"increments recorded: {calls['inc']}"
    data = resp.json()
    assert data.get("success") is True
    assert len(data.get("scenarios", [])) == 3


def test_endpoint_generate_scenarios_blocks_when_no_quota(monkeypatch):
    test_client = client()

    # Auth
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_no_quota")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Limits show exhausted
    from service import SubscriptionService as SubSvc

    monkeypatch.setattr(
        SubSvc.SubscriptionService,
        "get_usage_limits",
        staticmethod(lambda db, uid: _limits(scenarios_limit_reached=True, scenarios_limit=5, scenarios_used=5, scenarios_remaining=0)),
    )

    # Minimal endpoint access
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", lambda db, user_id, system_id: True)

    from service import EndpointService as ES

    def fake_check_endpoint_exists(db, endpoint_id):
        return SimpleNamespace(id=endpoint_id, system_id=1, method="GET", endpoint="/x", scenarios=[], raw_definition={}, definitions=[], definitions_for_params=[], definitions_for_responses=[], default_success_endpoint_parameters=[])

    monkeypatch.setattr(ES, "check_endpoint_exists", fake_check_endpoint_exists)

    resp = test_client.get("/endpoints/1/generate-scenarios-gpt", headers={"Authorization": "Bearer t"})
    assert resp.status_code == 403
    assert "Scenario creation limit reached" in resp.text


def test_system_generate_scenarios_increments_usage_and_caps(monkeypatch):
    test_client = client()

    # Auth
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_sys")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Access check noop
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", lambda db, user_id, system_id: True)

    # System with two endpoints
    from service import SystemService as SSvc

    def fake_check_system_exists(db, system_id):
        ep1 = SimpleNamespace(id=11, endpoint="/a", method="GET", raw_definition={}, definitions=[], definitions_for_params=[], definitions_for_responses=[], default_success_endpoint_parameters=[], scenarios=[])
        ep2 = SimpleNamespace(id=12, endpoint="/b", method="GET", raw_definition={}, definitions=[], definitions_for_params=[], definitions_for_responses=[], default_success_endpoint_parameters=[], scenarios=[])
        return SimpleNamespace(id=system_id, endpoints=[ep1, ep2])

    monkeypatch.setattr(SSvc, "check_system_exists", fake_check_system_exists)

    # Endpoint lookup for fresh fetch after save
    saved_by_ep = {11: [], 12: []}
    from service import EndpointService as ES
    from database.schemas import Scenario as ScenarioSchema, ScenarioBase

    def fake_check_endpoint_exists(db, endpoint_id):
        return SimpleNamespace(id=endpoint_id, system_id=1, method="GET", endpoint="/x", scenarios=saved_by_ep[endpoint_id], raw_definition={}, definitions=[], definitions_for_params=[], definitions_for_responses=[], default_success_endpoint_parameters=[])

    def fake_override_scenarios(db, endpoint_model):
        # Save limited scenarios for each endpoint with IDs
        next_id = 200
        converted = []
        for s in getattr(endpoint_model, "scenarios", []):
            converted.append(
                ScenarioSchema(
                    id=next_id,
                    name=s.name,
                    expected_http_status=getattr(s, "expected_http_status", 200),
                    requires_auth=getattr(s, "requires_auth", False),
                    auth_error=getattr(s, "auth_error", False),
                )
            )
            next_id += 1
        saved_by_ep[getattr(endpoint_model, "id", 0) or getattr(endpoint_model, "endpoint_id", 0)] = converted

    monkeypatch.setattr(ES, "check_endpoint_exists", fake_check_endpoint_exists)
    monkeypatch.setattr(ES, "override_scenarios", fake_override_scenarios)

    # GPT returns 3 scenarios per endpoint
    import gpt as gpt_module

    generated = [
        ScenarioBase(name="A1", expected_http_status=200, requires_auth=False),
        ScenarioBase(name="A2", expected_http_status=200, requires_auth=False),
        ScenarioBase(name="A3", expected_http_status=200, requires_auth=False),
    ]

    monkeypatch.setattr(
        gpt_module,
        "create_scenarios_for_endpoint",
        lambda endpoint, customer_id=None, db=None: (True, "ok", list(generated)),
    )

    # Limits: total remaining 4 across the system, so expect 3 for first endpoint, 1 for second
    from service import SubscriptionService as SubSvc

    monkeypatch.setattr(SubSvc.SubscriptionService, "can_create_scenario", staticmethod(lambda db, uid: True))
    monkeypatch.setattr(SubSvc.SubscriptionService, "get_usage_limits", staticmethod(lambda db, uid: _limits(scenarios_remaining=4)))

    calls = {"inc": []}

    def fake_increment_usage(db, uid, usage_type, count=1):
        calls["inc"].append((usage_type, count))
        return True

    monkeypatch.setattr(SubSvc.SubscriptionService, "increment_usage", staticmethod(fake_increment_usage))

    resp = test_client.post("/system/1/generate-scenarios", headers={"Authorization": "Bearer t"})

    assert resp.status_code == 200
    # Single increment with total created count 4
    assert ("scenarios_created", 4) in calls["inc"]


def test_create_endpoint_blocks_without_quota(monkeypatch):
    test_client = client()

    # Auth
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_no_create")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Limits deny creation
    from service import SubscriptionService as SubSvc
    monkeypatch.setattr(SubSvc.SubscriptionService, "can_create_scenario", staticmethod(lambda db, uid: False))
    monkeypatch.setattr(SubSvc.SubscriptionService, "get_usage_limits", staticmethod(lambda db, uid: _limits(scenarios_limit_reached=True, scenarios_limit=1, scenarios_used=1, scenarios_remaining=0)))

    # Minimal endpoint access
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", lambda db, user_id, system_id: True)

    from service import EndpointService as ES

    def fake_check_endpoint_exists(db, endpoint_id):
        return SimpleNamespace(id=endpoint_id, system_id=1)

    monkeypatch.setattr(ES, "check_endpoint_exists", fake_check_endpoint_exists)

    resp = test_client.post("/endpoints/1/scenarios", headers={"Authorization": "Bearer t"})
    assert resp.status_code == 403


def test_endpoint_generate_scenarios_partial_creation_message(monkeypatch):
    test_client = client()

    # Auth
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_partial")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Access noop
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", lambda db, user_id, system_id: True)

    # Endpoint existence and save
    saved = {"scenarios": []}
    from service import EndpointService as ES
    from database.schemas import Scenario as ScenarioSchema, ScenarioBase

    def fake_check_endpoint_exists(db, endpoint_id):
        return SimpleNamespace(id=endpoint_id, system_id=1, method="GET", endpoint="/x", scenarios=saved["scenarios"], raw_definition={}, definitions=[], definitions_for_params=[], definitions_for_responses=[], default_success_endpoint_parameters=[])

    def fake_override_scenarios(db, endpoint_model):
        converted = []
        next_id = 300
        for s in getattr(endpoint_model, "scenarios", []):
            converted.append(
                ScenarioSchema(
                    id=next_id,
                    name=s.name,
                    expected_http_status=getattr(s, "expected_http_status", 200),
                    requires_auth=getattr(s, "requires_auth", False),
                    auth_error=getattr(s, "auth_error", False),
                )
            )
            next_id += 1
        saved["scenarios"] = converted

    monkeypatch.setattr(ES, "check_endpoint_exists", fake_check_endpoint_exists)
    monkeypatch.setattr(ES, "override_scenarios", fake_override_scenarios)

    # GPT returns 5 scenarios but remaining is 2
    import gpt as gpt_module
    generated = [
        ScenarioBase(name=f"P{i}", expected_http_status=200, requires_auth=False) for i in range(5)
    ]
    monkeypatch.setattr(
        gpt_module,
        "create_scenarios_for_endpoint",
        lambda endpoint, customer_id=None, db=None: (True, "ok", list(generated)),
    )

    from service import SubscriptionService as SubSvc
    monkeypatch.setattr(SubSvc.SubscriptionService, "get_usage_limits", staticmethod(lambda db, uid: _limits(scenarios_remaining=2)))

    resp = test_client.get("/endpoints/1/generate-scenarios-gpt", headers={"Authorization": "Bearer t"})
    assert resp.status_code == 200
    msg = resp.json().get("message", "")
    assert "Only 2 scenario(s) were created" in msg


def test_endpoint_generate_scenarios_does_not_increment_on_failure(monkeypatch):
    test_client = client()

    # Auth
    from service import ClerkAuthService

    async def fake_require_client_or_admin():
        return SimpleNamespace(id="user_fail")

    monkeypatch.setattr(ClerkAuthService, "require_client_or_admin", fake_require_client_or_admin)

    # Access noop
    from service import CustomerService
    monkeypatch.setattr(CustomerService, "check_user_system_access", lambda db, user_id, system_id: True)

    # Endpoint exists
    from service import EndpointService as ES

    def fake_check_endpoint_exists(db, endpoint_id):
        return SimpleNamespace(id=endpoint_id, system_id=1, method="GET", endpoint="/x", scenarios=[], raw_definition={}, definitions=[], definitions_for_params=[], definitions_for_responses=[], default_success_endpoint_parameters=[])

    monkeypatch.setattr(ES, "check_endpoint_exists", fake_check_endpoint_exists)

    # GPT fails
    import gpt as gpt_module
    monkeypatch.setattr(
        gpt_module,
        "create_scenarios_for_endpoint",
        lambda endpoint, customer_id=None, db=None: (False, "error", []),
    )

    # Track usage increments to ensure none happen
    from service import SubscriptionService as SubSvc
    calls = {"inc": 0}

    def fake_increment_usage(db, uid, usage_type, count=1):
        calls["inc"] += 1
        return True

    monkeypatch.setattr(SubSvc.SubscriptionService, "get_usage_limits", staticmethod(lambda db, uid: _limits(scenarios_remaining=5)))
    monkeypatch.setattr(SubSvc.SubscriptionService, "increment_usage", staticmethod(fake_increment_usage))

    resp = test_client.get("/endpoints/1/generate-scenarios-gpt", headers={"Authorization": "Bearer t"})
    assert resp.status_code == 400
    assert calls["inc"] == 0


