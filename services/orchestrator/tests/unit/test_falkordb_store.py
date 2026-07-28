from __future__ import annotations

from dataclasses import dataclass

from app.adapters.falkordb_store import FalkorDBStore, InMemoryFalkorStore
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings


@dataclass
class Result:
    result_set: list


class CapturingGraph:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def query(self, query: str, params: dict | None = None) -> Result:
        self.calls.append((query, params or {}))
        return Result([])


def _node(entity_id: str, path: str = "a.py", revision: str = "r1") -> StructuralNode:
    return StructuralNode(entity_id, "repo", path, "File", path, 1, 2, revision)


def test_falkor_queries_are_parameterized_and_metadata_only() -> None:
    graph = CapturingGraph()
    store = FalkorDBStore(Settings(), graph=graph, repo="repo")
    node = _node("file-1")
    edge = StructuralEdge("file-1", "file-1", "CONTAINS", "repo", "a.py", "r1")
    result = store.persist("repo", "r1", [node], [edge])
    assert result.node_count == 1
    assert graph.calls
    rows = [row for _, params in graph.calls for row in params.get("rows", [])]
    assert all("source" not in row and "content" not in row for row in rows)
    assert any("$rows" in query for query, _ in graph.calls)


def test_full_persist_deletes_stale_relationships_by_revision() -> None:
    graph = CapturingGraph()
    store = FalkorDBStore(Settings(), graph=graph, repo="repo")
    store.persist("repo", "r2", [_node("file-1", revision="r2")], [])

    assert any(
        "MATCH ()-[r {repo: $repo}]->()" in query
        and "r.index_revision <> $revision" in query
        and params == {"repo": "repo", "revision": "r2"}
        for query, params in graph.calls
    )


def test_in_memory_store_is_idempotent_and_reconciles_affected_paths() -> None:
    store = InMemoryFalkorStore()
    first = [_node("a", "a.py"), _node("b", "b.py")]
    assert store.persist("repo", "r1", first, []).node_count == 2
    assert store.persist("repo", "r1", first, []).node_count == 2
    store.persist("repo", "r2", [_node("a2", "a.py", "r2")], [], affected_paths=["a.py"])
    assert set(store.nodes["repo"]) == {"a2", "b"}
    assert store.nodes["repo"]["b"].index_revision == "r2"


def test_in_memory_store_removes_edges_incident_to_affected_nodes() -> None:
    store = InMemoryFalkorStore()
    a = _node("a", "a.py")
    b = _node("b", "b.py")
    stale_edge = StructuralEdge("b", "a", "IMPORTS", "repo", "b.py", "r1")
    store.persist("repo", "r1", [a, b], [stale_edge])

    store.persist("repo", "r2", [_node("a2", "a.py", "r2")], [], affected_paths=["a.py"])

    assert store.edges["repo"] == []


def test_health_pings_the_clients_redis_connection(monkeypatch) -> None:
    from falkordb import FalkorDB

    class Connection:
        def ping(self) -> bool:
            return True

    class Client:
        connection = Connection()

    monkeypatch.setattr(FalkorDB, "from_url", staticmethod(lambda *args, **kwargs: Client()))
    assert FalkorDBStore(Settings()).health() == "ok"
