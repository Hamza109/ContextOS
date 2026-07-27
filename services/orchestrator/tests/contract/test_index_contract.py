"""Contract tests for confirmed POST /index field names only (T019, T034)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.schemas_index import IndexRequest, IndexResponse
from app.main import app

CONFIRMED_REQUEST_FIELDS = {"repo_path", "repo_name"}
CONFIRMED_RESPONSE_FIELDS = {"files_indexed", "graph_nodes", "embeddings", "time_ms"}


def test_index_request_confirmed_fields() -> None:
    model_fields = set(IndexRequest.model_fields.keys())
    assert CONFIRMED_REQUEST_FIELDS.issubset(model_fields)
    # Proposed optional fields may exist but must not be required
    for name in ("paths", "files"):
        if name in IndexRequest.model_fields:
            assert IndexRequest.model_fields[name].is_required() is False


def test_index_response_confirmed_fields_only() -> None:
    assert set(IndexResponse.model_fields.keys()) == CONFIRMED_RESPONSE_FIELDS


def test_openapi_index_confirmed_response_properties() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    index_post = schema["paths"]["/index"]["post"]
    ref = index_post["responses"]["200"]["content"]["application/json"]["schema"]
    # Resolve $ref if present
    if "$ref" in ref:
        name = ref["$ref"].split("/")[-1]
        props = set(schema["components"]["schemas"][name]["properties"].keys())
    else:
        props = set(ref.get("properties", {}).keys())
    assert props == CONFIRMED_RESPONSE_FIELDS
