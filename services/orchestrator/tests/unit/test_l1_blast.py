"""Unit tests for EP-007 L1 blast service (T011)."""

from __future__ import annotations

import pytest

from app.adapters.falkordb_store import InMemoryFalkorStore
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings
from app.services.l1_blast import BlastNotFoundError, BlastService


def _file(entity_id: str, path: str, revision: str = "r1") -> StructuralNode:
    return StructuralNode(entity_id, "repo", path, "File", path, 1, 2, revision)


def _imports(source: str, target: str, source_path: str, revision: str = "r1") -> StructuralEdge:
    return StructuralEdge(source, target, "IMPORTS", "repo", source_path, revision)


def _chain_store() -> InMemoryFalkorStore:
    """a <- b <- c <- d  (reverse IMPORTS dependents of a: b direct; c,d transitive)."""
    store = InMemoryFalkorStore()
    nodes = [
        _file("a", "src/a.py"),
        _file("b", "src/b.py"),
        _file("c", "src/c.py"),
        _file("d", "src/d.py"),
        _file("t", "tests/test_a.py"),
    ]
    edges = [
        _imports("b", "a", "src/b.py"),
        _imports("c", "b", "src/c.py"),
        _imports("d", "c", "src/d.py"),
    ]
    store.persist("repo", "r1", nodes, edges)
    return store


def test_blast_direct_vs_transitive_and_confirmed_fields() -> None:
    service = BlastService(Settings(falkordb_url="memory://blast"), store=_chain_store())
    result = service.compute("repo", "src/a.py", max_hops=3)
    assert result.direct_dependents == ["src/b.py"]
    assert result.transitive == ["src/c.py", "src/d.py"]
    payload = result.as_response_dict()
    assert set(payload) >= {
        "direct_dependents",
        "transitive",
        "db_tables",
        "risk",
        "tests_to_run",
        "owners",
    }
    assert payload["db_tables"] == []
    assert payload["owners"] == []
    assert payload["risk"] in {"HIGH", "MEDIUM", "LOW"}
    assert payload["tests_to_run"] == ["tests/test_a.py"]
    assert payload["index_revision"] == "r1"
    # OQ-15: no Confirmed owners element schema — empty list only.
    assert isinstance(payload["owners"], list) and len(payload["owners"]) == 0


def test_blast_depth_bound_limits_transitive() -> None:
    service = BlastService(Settings(falkordb_url="memory://blast"), store=_chain_store())
    shallow = service.compute("repo", "a.py", max_hops=1)
    assert shallow.direct_dependents == ["src/b.py"]
    assert shallow.transitive == []


def test_blast_empty_graph_and_unknown_file() -> None:
    store = InMemoryFalkorStore()
    service = BlastService(Settings(falkordb_url="memory://blast"), store=store)
    with pytest.raises(BlastNotFoundError):
        service.compute("missing", "a.py")

    store.persist("repo", "r1", [_file("a", "a.py")], [])
    with pytest.raises(BlastNotFoundError):
        service.compute("repo", "missing.py")

    result = service.compute("repo", "a.py")
    assert result.direct_dependents == []
    assert result.transitive == []
    assert result.risk == "LOW"
    assert result.owners == []


def test_blast_risk_medium_when_direct_only() -> None:
    store = InMemoryFalkorStore()
    store.persist(
        "repo",
        "r1",
        [_file("a", "a.py"), _file("b", "b.py")],
        [_imports("b", "a", "b.py")],
    )
    result = BlastService(Settings(falkordb_url="memory://blast"), store=store).compute(
        "repo", "a.py"
    )
    assert result.risk == "MEDIUM"
