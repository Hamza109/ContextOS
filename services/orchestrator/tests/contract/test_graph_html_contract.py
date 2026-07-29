"""Contract tests for GET /graph.html (T024)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.adapters.falkordb_store import InMemoryFalkorStore, get_graph_store, reset_memory_graph_store
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings, get_settings
from app.main import app


def _seed() -> None:
    reset_memory_graph_store()
    get_settings.cache_clear()
    store = get_graph_store(Settings(falkordb_url="memory://ep006-tests"))
    assert isinstance(store, InMemoryFalkorStore)
    a = StructuralNode("a", "graph-repo", "a.py", "File", "a.py", 1, 2, "r1")
    b = StructuralNode("b", "graph-repo", "b.py", "File", "b.py", 1, 2, "r1")
    cls = StructuralNode("c", "graph-repo", "a.py", "Class", "a.Auth", 1, 10, "r1")
    method = StructuralNode(
        "m", "graph-repo", "a.py", "Method", "a.Auth.validate", 3, 8, "r1"
    )
    store.persist(
        "graph-repo",
        "r1",
        [a, b, cls, method],
        [
            StructuralEdge("b", "a", "IMPORTS", "graph-repo", "b.py", "r1"),
            StructuralEdge("a", "c", "CONTAINS", "graph-repo", "a.py", "r1"),
            StructuralEdge("c", "m", "DECLARES", "graph-repo", "a.py", "r1"),
        ],
    )


def test_graph_html_contract_indexed_and_unknown() -> None:
    _seed()
    client = TestClient(app)
    ok = client.get("/graph.html", params={"repo": "graph-repo", "depth": 2})
    assert ok.status_code == 200
    assert "text/html" in ok.headers.get("content-type", "")
    body = ok.text
    assert "vis-network" in body
    assert "#4E79A7" in body  # Graphify / Tableau community palette
    assert "#0f172a" in body
    assert "legend-cb" in body
    assert 'data-index-revision="r1"' in body
    assert 'data-mode="files"' in body

    symbols = client.get(
        "/graph.html", params={"repo": "graph-repo", "depth": 2, "mode": "symbols"}
    )
    assert symbols.status_code == 200
    sbody = symbols.text
    assert 'data-mode="symbols"' in sbody
    assert "Kinds" in sbody
    assert "Class" in sbody
    assert "Auth" in sbody or "validate" in sbody

    missing = client.get("/graph.html", params={"repo": "missing-repo"})
    assert missing.status_code == 404

    schema = client.get("/openapi.json").json()
    assert "/graph.html" in schema["paths"]
    assert "mode" in schema["paths"]["/graph.html"]["get"]["parameters"][0]["name"] or any(
        p.get("name") == "mode"
        for p in schema["paths"]["/graph.html"]["get"]["parameters"]
    )
