"""Unit: Proposed freshness / index_revision signals (T033 API side)."""

from __future__ import annotations

from app.adapters.falkordb_store import InMemoryFalkorStore
from app.adapters.l1_parser import StructuralNode
from app.api.graph import render_graph_html
from app.config import Settings
from app.services.l1_blast import BlastService


def test_blast_and_graph_expose_proposed_index_revision() -> None:
    store = InMemoryFalkorStore()
    store.persist(
        "repo",
        "fresh-rev",
        [StructuralNode("a", "repo", "a.py", "File", "a.py", 1, 1, "fresh-rev")],
        [],
    )
    blast = BlastService(Settings(falkordb_url="memory://f"), store=store).compute(
        "repo", "a.py"
    )
    assert blast.index_revision == "fresh-rev"
    assert blast.as_response_dict()["index_revision"] == "fresh-rev"

    html = render_graph_html(
        repo="repo",
        revision="fresh-rev",
        depth=1,
        nodes=[{"id": "a", "path": "a.py"}],
        edges=[],
    )
    assert 'data-index-revision="fresh-rev"' in html
    assert 'data-stale="false"' in html
