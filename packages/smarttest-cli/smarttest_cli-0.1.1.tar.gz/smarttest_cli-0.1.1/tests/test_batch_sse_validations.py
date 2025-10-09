from types import SimpleNamespace
from unittest.mock import patch

import pytest


def test_batch_processing_streams_generated_validations():
    import routes.batch_processing_routes as routes
    from database.schemas import BatchProcessingRequest
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    with patch("gpt.get_openai_client"), \
         patch("service.ClerkAuthService.get_clerk_client"), \
         patch.object(routes, "SubscriptionService") as sub, \
         patch.object(routes, "BatchProcessingService") as svc:

        class C(SimpleNamespace):
            id = "user_1"
        # Build app and override the dependency used by the router
        from routes.batch_processing_routes import router as batch_router
        from routes.batch_processing_routes import require_client_or_admin as dep
        app = FastAPI()
        app.dependency_overrides[dep] = lambda: C()
        app.include_router(batch_router)

        sub.get_usage_limits.return_value = SimpleNamespace(
            runs_used=0, runs_limit=10, runs_remaining=10, runs_limit_reached=False
        )

        # Mock generator: service yields completed event with one validation
        async def fake_process(ids):
            from database.schemas import BatchProcessingStreamEvent, BatchProcessingScenarioResult
            yield BatchProcessingStreamEvent(
                event_type="scenario_result",
                data=BatchProcessingScenarioResult(
                    scenario_id=1,
                    scenario_name="S1",
                    status="completed",
                    http_status=200,
                    response_body={},
                    response_headers={},
                    generated_validations=[{"validation_text": "status == 200", "description": None, "confidence": 0.9}],
                    matches_expectation=True,
                    confidence=1.0,
                    explanation="E",
                ),
            )

        svc.return_value.process_scenarios_batch.side_effect = fake_process

        client_app = TestClient(app)
        req = BatchProcessingRequest(scenario_ids=[1])
        resp = client_app.post("/batch-processing/scenarios/process", json=req.model_dump())

        # SSE stream aggregated by TestClient
        assert resp.status_code == 200
        # Minimal check: at least one chunk contains our validation text
        assert "status == 200" in resp.text


