"""Contract tests for confirmed POST /context field names (T015, T025, T053)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.schemas_context import ContextMetrics, ContextRequest, ContextResponse
from app.main import app

CONFIRMED_REQUEST_FIELDS = {"query", "file", "repo", "top_k"}
CONFIRMED_RESPONSE_FIELDS = {
    "final_context",
    "metrics",
    "blast_radius",
    "memory",
    "relevant_files",
    "is_real",
}
CONFIRMED_METRICS_FIELDS = {"tokens_before", "tokens_after", "saving_percent", "trace"}


def test_context_request_confirmed_fields() -> None:
    model_fields = set(ContextRequest.model_fields.keys())
    assert CONFIRMED_REQUEST_FIELDS.issubset(model_fields)
    # Proposed optional phase (OQ-16) may exist but must not be required
    if "phase" in ContextRequest.model_fields:
        assert ContextRequest.model_fields["phase"].is_required() is False


def test_context_response_confirmed_fields() -> None:
    assert CONFIRMED_RESPONSE_FIELDS.issubset(set(ContextResponse.model_fields.keys()))


def test_context_metrics_confirmed_keys() -> None:
    assert set(ContextMetrics.model_fields.keys()) == CONFIRMED_METRICS_FIELDS


def test_openapi_context_confirmed_response_properties() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    assert "/context" in schema["paths"]
    post = schema["paths"]["/context"]["post"]
    ref = post["responses"]["200"]["content"]["application/json"]["schema"]
    if "$ref" in ref:
        name = ref["$ref"].split("/")[-1]
        props = set(schema["components"]["schemas"][name]["properties"].keys())
    else:
        props = set(ref.get("properties", {}).keys())
    assert CONFIRMED_RESPONSE_FIELDS.issubset(props)


def test_relevant_files_score_behavior_documented_proposed() -> None:
    """Item keys are Proposed — assert score-carrying shape is available on model helper."""
    from app.api.schemas_context import RelevantFileItem

    item = RelevantFileItem(path="a.py", score=0.9)
    assert item.path == "a.py"
    assert item.score == 0.9
