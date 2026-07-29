"""Contract lock: Confirmed POST /context metrics keys (EP-008 T003)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.schemas_context import ContextMetrics
from app.main import app

# Confirmed Appendix D / api-contract §2.3 — no new required Confirmed fields.
CONFIRMED_METRICS_FIELDS = {"tokens_before", "tokens_after", "saving_percent", "trace"}


def test_confirmed_metrics_keys_locked() -> None:
    assert set(ContextMetrics.model_fields.keys()) == CONFIRMED_METRICS_FIELDS


def test_openapi_metrics_schema_confirmed_keys_only() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    metrics = schema["components"]["schemas"]["ContextMetrics"]["properties"]
    assert set(metrics.keys()) == CONFIRMED_METRICS_FIELDS
