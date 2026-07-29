"""Contract tests for Confirmed GET /blast (T013)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.adapters.falkordb_store import InMemoryFalkorStore, get_graph_store, reset_memory_graph_store
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.api.schemas_blast import BlastResponse
from app.config import Settings, get_settings
from app.main import app

CONFIRMED_BLAST_FIELDS = {
    "direct_dependents",
    "transitive",
    "db_tables",
    "risk",
    "tests_to_run",
}


def _seed() -> None:
    reset_memory_graph_store()
    get_settings.cache_clear()
    store = get_graph_store(Settings(falkordb_url="memory://ep006-tests"))
    assert isinstance(store, InMemoryFalkorStore)
    a = StructuralNode("a", "blast-repo", "core.py", "File", "core.py", 1, 2, "r1")
    b = StructuralNode("b", "blast-repo", "app.py", "File", "app.py", 1, 2, "r1")
    store.persist(
        "blast-repo",
        "r1",
        [a, b],
        [StructuralEdge("b", "a", "IMPORTS", "blast-repo", "app.py", "r1")],
    )


def test_blast_response_model_confirmed_and_proposed_owners() -> None:
    fields = set(BlastResponse.model_fields.keys())
    assert CONFIRMED_BLAST_FIELDS.issubset(fields)
    assert "owners" in fields
    assert BlastResponse.model_fields["owners"].is_required() is False


def test_openapi_blast_path_and_shape() -> None:
    _seed()
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert any(p.startswith("/blast/") for p in paths)
    response = client.get("/blast/core.py", params={"repo": "blast-repo"})
    assert response.status_code == 200
    body = response.json()
    assert CONFIRMED_BLAST_FIELDS.issubset(body)
    assert body["owners"] == []
    assert body["risk"] in {"HIGH", "MEDIUM", "LOW"}
    assert body["direct_dependents"] == ["app.py"]
    assert "content" not in body
    assert "source" not in body


def test_blast_proposed_404_unknown_repo_or_file() -> None:
    _seed()
    client = TestClient(app)
    assert client.get("/blast/core.py", params={"repo": "nope"}).status_code == 404
    assert (
        client.get("/blast/missing.py", params={"repo": "blast-repo"}).status_code == 404
    )
