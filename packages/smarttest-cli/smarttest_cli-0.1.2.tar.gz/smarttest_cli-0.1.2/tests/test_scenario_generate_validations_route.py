import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest


def test_generate_validations_route_uses_unified_dict():
    import routes.scenario_routes as routes
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    # Patch dependencies used by the route
    with patch("gpt.get_openai_client"), \
         patch("service.ClerkAuthService.get_clerk_client"), \
         patch.object(routes, "SubscriptionService") as sub, \
         patch.object(routes, "get_scenario_by_id") as get_scenario, \
         patch.object(routes, "get_endpoint_by_id") as get_endpoint, \
         patch.object(routes, "check_user_system_access") as chk, \
         patch.object(routes, "ScenarioService") as scenario_service, \
         patch.object(routes, "create_validation") as create_validation, \
         patch.object(routes, "gpt") as gpt_mod:
        # Build app AFTER patches so dependency is bound to the patched function
        from routes.scenario_routes import router as scenario_router
        app = FastAPI()

        # Override dependency explicitly
        async def fake_dep():
            return SimpleNamespace(id="user_1")
        # Import the centralized auth dependency
        from service.AuthService import require_auth
        app.dependency_overrides[require_auth] = fake_dep
        app.include_router(scenario_router)
        client_app = TestClient(app)

        # Usage limits happy path
        sub.get_usage_limits.return_value = SimpleNamespace(
            subscription=SimpleNamespace(tier=SimpleNamespace(auto_validation_generation_enabled=True, max_validation_generations_per_month=100)),
            current_usage=SimpleNamespace(validation_generations_used=0),
            validation_generations_remaining=10,
        )

        # Scenario and endpoint
        get_scenario.return_value = SimpleNamespace(id=1, endpoint_id=2, name="S1")
        get_endpoint.return_value = SimpleNamespace(id=2, system_id=3)

        # Execute scenario returns response
        scenario_service.execute_scenario_only.return_value = {
            "success": True,
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"ok": True},
        }

        # Unified generator dict
        gpt_mod.generate_validations_for_scenario.return_value = {
            "generated_validations": [
                {"validation_text": "status == 200", "description": None, "confidence": 0.9}
            ],
            "confidence": 1.0,
            "explanation": "E",
        }

        # Create validation no-op
        create_validation.side_effect = lambda db, v: SimpleNamespace(
            id=10,
            scenario_id=v.scenario_id,
            validation_text=v.validation_text,
            description=v.description,
        )

        # Make request
        resp = client_app.post("/scenario/1/generate-validations")

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert len(data["validations"]) == 1
        assert data["validations"][0]["validation_text"] == "status == 200"


