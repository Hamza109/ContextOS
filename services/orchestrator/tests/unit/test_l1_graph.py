from __future__ import annotations

from pathlib import Path

import pytest

from app.adapters.falkordb_store import InMemoryFalkorStore
from app.adapters.l1_parser import TreeSitterL1Parser
from app.config import Settings
from app.services.l1_entity_cache import L1EntityCache
from app.services.l1_graph import L1GraphService


def test_service_consumes_only_supplied_paths_and_reports_distinct_count(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed.py"
    excluded = tmp_path / "excluded.py"
    allowed.write_text("class A:\n def run(self):\n  call()\n", encoding="utf-8")
    excluded.write_text("SECRET = 'never parse'\n", encoding="utf-8")
    store = InMemoryFalkorStore()
    service = L1GraphService(
        Settings(falkordb_url="memory://test"),
        parser=TreeSitterL1Parser(),
        store=store,
        cache=L1EntityCache(),
    )
    result = service.generate("repo", tmp_path, [allowed])
    assert result.graph_nodes == len(store.nodes["repo"])
    assert {node.source_path for node in store.nodes["repo"].values()} == {"allowed.py"}


def test_store_failure_fails_generation_and_does_not_refresh_cache(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.write_text("x = 1\n", encoding="utf-8")
    cache = L1EntityCache()

    class FailingStore:
        def persist(self, *args, **kwargs):
            raise ConnectionError("unavailable")

        def get_entities(self, *args, **kwargs):
            raise AssertionError("must not warm after failed persist")

    service = L1GraphService(
        Settings(falkordb_url="memory://test"),
        store=FailingStore(),
        cache=cache,
    )
    with pytest.raises(ConnectionError):
        service.generate("repo", tmp_path, [path])
    assert len(cache) == 0
