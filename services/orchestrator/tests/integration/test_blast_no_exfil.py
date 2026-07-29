"""No source-byte / IgnorePolicy exfil on blast payloads (T012)."""

from __future__ import annotations

from app.adapters.falkordb_store import InMemoryFalkorStore
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings
from app.services.l1_blast import BlastService


def test_blast_payload_has_no_source_bodies_and_filters_excluded_paths() -> None:
    store = InMemoryFalkorStore()
    nodes = [
        StructuralNode("a", "repo", "src/a.py", "File", "src/a.py", 1, 2, "r1"),
        StructuralNode("b", "repo", "src/b.py", "File", "src/b.py", 1, 2, "r1"),
        StructuralNode(
            "env", "repo", ".env", "File", ".env", 1, 1, "r1"
        ),  # should never serialize
        StructuralNode(
            "nm",
            "repo",
            "node_modules/x.js",
            "File",
            "node_modules/x.js",
            1,
            1,
            "r1",
        ),
    ]
    edges = [
        StructuralEdge("b", "a", "IMPORTS", "repo", "src/b.py", "r1"),
        StructuralEdge("env", "a", "IMPORTS", "repo", ".env", "r1"),
        StructuralEdge("nm", "a", "IMPORTS", "repo", "node_modules/x.js", "r1"),
    ]
    store.persist("repo", "r1", nodes, edges)
    result = BlastService(Settings(falkordb_url="memory://nox"), store=store).compute(
        "repo", "src/a.py"
    )
    payload = result.as_response_dict()
    blob = str(payload)
    assert "SECRET" not in blob
    assert "content" not in payload
    assert "source" not in payload
    assert ".env" not in result.direct_dependents
    assert "node_modules/x.js" not in result.direct_dependents
    assert "src/b.py" in result.direct_dependents
