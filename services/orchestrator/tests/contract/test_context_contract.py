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
    assert set(ContextResponse.model_fields.keys()) == CONFIRMED_RESPONSE_FIELDS


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


def test_no_invented_confirmed_l3_response_fields() -> None:
    """T061: Proposed enrichment must not add Confirmed Appendix D L3 fields (FR-012)."""
    model_fields = set(ContextResponse.model_fields.keys())
    invented = {
        "safe_edit_plan",
        "symbol_definition",
        "references",
        "rename_scope",
        "l3",
        "serena",
    }
    assert model_fields.isdisjoint(invented)
    assert CONFIRMED_RESPONSE_FIELDS.issubset(model_fields)


def test_openapi_has_no_confirmed_symbol_rest_paths() -> None:
    """T071: OpenAPI Confirmed Appendix D unchanged — no L3 symbol REST."""
    client = TestClient(app)
    paths = set(client.get("/openapi.json").json()["paths"].keys())
    assert "/context" in paths
    for p in ("/symbol", "/definition", "/references", "/rename-scope", "/serena"):
        assert p not in paths


def test_no_l1_cache_or_graph_response_fields() -> None:
    fields = set(ContextResponse.model_fields)
    assert fields.isdisjoint({"l1", "graph", "entities", "cache", "index_revision"})


def test_openapi_includes_blast_and_graph_routes() -> None:
    """EP-007 Confirmed Appendix D routes present; context field set unchanged."""
    client = TestClient(app)
    paths = set(client.get("/openapi.json").json()["paths"].keys())
    assert "/context" in paths
    assert "/graph.html" in paths
    assert any(p.startswith("/blast/") for p in paths)
