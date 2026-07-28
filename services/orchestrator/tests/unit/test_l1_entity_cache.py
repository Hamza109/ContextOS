from __future__ import annotations

from app.adapters.falkordb_store import InMemoryFalkorStore
from app.adapters.l1_parser import StructuralNode
from app.config import Settings
from app.services.l1_entity_cache import L1EntityCache
from app.services.l1_structural_query import StructuralQueryService


def _node(repo: str, revision: str, entity_id: str) -> StructuralNode:
    return StructuralNode(entity_id, repo, "auth.py", "Method", f"Auth.{entity_id}", 2, 3, revision)


def test_cache_enforces_lru_bound_and_repository_revision_isolation() -> None:
    now = [0.0]
    cache = L1EntityCache(2, 10, clock=lambda: now[0])
    cache.refresh("a", "r1", [_node("a", "r1", "one"), _node("a", "r1", "two")])
    assert cache.get("a", "r1", "one") is not None
    cache.put(_node("a", "r1", "three"))
    assert cache.get("a", "r1", "two") is None
    assert cache.get("b", "r1", "one") is None
    assert cache.get("a", "r2", "one") is None


def test_cache_ttl_and_successful_revision_refresh() -> None:
    now = [0.0]
    cache = L1EntityCache(10, 5, clock=lambda: now[0])
    cache.refresh("repo", "r1", [_node("repo", "r1", "old")])
    now[0] = 6
    assert cache.lookup("repo", ["old"]).entities == []
    cache.refresh("repo", "r2", [_node("repo", "r2", "new")])
    assert cache.current_revision("repo") == "r2"
    assert cache.get("repo", "r1", "old") is None
    assert cache.lookup("repo", ["new"]).hit is True


def test_cache_values_are_metadata_only() -> None:
    cache = L1EntityCache()
    entity = _node("repo", "rev", "method")
    cache.refresh("repo", "rev", [entity])
    stored = cache.get("repo", "rev", "method")
    assert stored is not None
    assert not hasattr(stored, "content") and not hasattr(stored, "source")


def test_query_miss_fills_cache_from_source_of_truth() -> None:
    cache = L1EntityCache()
    store = InMemoryFalkorStore()
    entity = _node("repo", "rev", "validate")
    store.persist("repo", "rev", [entity], [])
    result = StructuralQueryService(
        Settings(falkordb_url="memory://test"),
        cache=cache,
        store=store,
    ).enrich("<base/>", repo="repo", query="where is validate defined?")
    assert result.status == "attached"
    assert result.cache_hit is False
    assert cache.get("repo", "rev", "validate") == entity


def test_query_store_failure_preserves_l5_context() -> None:
    class FailingStore:
        def latest_revision(self, repo):
            raise ConnectionError("down")

    result = StructuralQueryService(
        Settings(falkordb_url="redis://localhost:6379"),
        cache=L1EntityCache(),
        store=FailingStore(),
    ).enrich("<base/>", repo="repo", query="where is auth defined?")
    assert result.status == "l1_unavailable"
    assert result.final_context == "<base/>"
