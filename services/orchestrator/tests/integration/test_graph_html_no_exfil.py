"""No-exfil / IgnorePolicy tests for graph.html serialization (T023)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.adapters.falkordb_store import get_graph_store, reset_memory_graph_store
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings, get_settings
from app.main import app


def test_graph_html_excludes_hard_excluded_paths_and_source_bodies() -> None:
    reset_memory_graph_store()
    get_settings.cache_clear()
    store = get_graph_store(Settings(falkordb_url="memory://ep006-tests"))
    nodes = [
        StructuralNode("a", "g", "src/a.py", "File", "src/a.py", 1, 2, "r1"),
        StructuralNode("e", "g", ".env", "File", ".env", 1, 1, "r1"),
        StructuralNode("n", "g", "node_modules/x.js", "File", "node_modules/x.js", 1, 1, "r1"),
    ]
    edges = [
        StructuralEdge("e", "a", "IMPORTS", "g", ".env", "r1"),
        StructuralEdge("n", "a", "IMPORTS", "g", "node_modules/x.js", "r1"),
    ]
    store.persist("g", "r1", nodes, edges)

    response = TestClient(app).get("/graph.html", params={"repo": "g"})
    assert response.status_code == 200
    text = response.text
    assert ".env" not in text or '".env"' not in text
    assert "node_modules/x.js" not in text
    assert "src/a.py" in text
    assert "must-not" not in text
    assert '"content"' not in text
