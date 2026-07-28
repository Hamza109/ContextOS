from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.adapters.falkordb_store import FalkorDBStore, InMemoryFalkorStore
from app.config import Settings
from app.main import app
from app.services.l1_entity_cache import L1EntityCache
from app.services.l1_graph import L1GraphService
from app.services.l5_index import IndexResult, run_index
from tests.fixtures.l1_structural_repo_fixture import materialize_l1_structural_repo


def test_index_persists_typed_provenance_and_reports_node_count(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "auth.py").write_text(
        "import os\nclass Auth:\n def validate(self):\n  return check()\n",
        encoding="utf-8",
    )
    store = InMemoryFalkorStore()
    service = L1GraphService(
        Settings(falkordb_url="memory://acceptance"),
        store=store,
        cache=L1EntityCache(),
    )
    result = run_index(
        str(root),
        "acceptance",
        settings=Settings(
            falkordb_url="memory://acceptance",
            pack_cache_dir=tmp_path / "packs",
        ),
        graph_service=service,
        skip_embed=True,
    )
    nodes = list(store.nodes["acceptance"].values())
    edges = store.edges["acceptance"]
    assert result.graph_nodes == len(nodes)
    assert {"File", "Module", "Class", "Method", "Call"} <= {
        node.entity_kind for node in nodes
    }
    assert {"CONTAINS", "DECLARES", "MAKES_CALL", "IMPORTS"} <= {
        edge.edge_kind for edge in edges
    }
    assert all(
        node.repo == "acceptance"
        and node.source_path == "auth.py"
        and node.start_line >= 1
        and node.index_revision
        for node in nodes
    )
    assert all(not hasattr(node, "content") for node in nodes)


def test_post_index_keeps_exact_response_shape_with_nonzero_graph(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.index.run_index",
        lambda *args, **kwargs: IndexResult(1, 5, 2, 10),
    )
    response = TestClient(app).post(
        "/index",
        json={"repo_path": "/tmp/repo", "repo_name": "repo"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "files_indexed": 1,
        "graph_nodes": 5,
        "embeddings": 2,
        "time_ms": 10,
    }


def test_versioned_fixture_exclusions_never_reach_l1(tmp_path: Path) -> None:
    root = materialize_l1_structural_repo(tmp_path / "fixture")
    store = InMemoryFalkorStore()
    service = L1GraphService(
        Settings(falkordb_url="memory://fixture"),
        store=store,
        cache=L1EntityCache(),
    )
    run_index(
        str(root),
        "fixture",
        settings=Settings(
            falkordb_url="memory://fixture",
            pack_cache_dir=tmp_path / "packs",
        ),
        graph_service=service,
        skip_embed=True,
    )
    persisted = {node.source_path for node in store.nodes["fixture"].values()}
    assert not persisted.intersection(
        {
            ".env",
            "secret.pem",
            "asset.bin",
            "node_modules/dependency.js",
            "build/generated.py",
            "ignored/ignored.py",
        }
    )


@pytest.mark.requires_falkordb
@pytest.mark.skipif(
    os.environ.get("CONTEXTOS_FALKORDB_INTEGRATION") != "1",
    reason="live FalkorDB integration skipped: set CONTEXTOS_FALKORDB_INTEGRATION=1",
)
def test_live_falkor_persists_and_reads_structural_evidence(tmp_path: Path) -> None:
    repo = f"live-{uuid.uuid4().hex}"
    path = tmp_path / "auth.py"
    path.write_text("class Auth:\n def validate(self):\n  check()\n", encoding="utf-8")
    settings = Settings(
        falkordb_url=os.environ.get("CONTEXTOS_FALKORDB_URL", "redis://127.0.0.1:6379"),
        falkordb_graph_prefix="ep006_test",
    )
    store = FalkorDBStore(settings)
    service = L1GraphService(settings, store=store, cache=L1EntityCache())
    result = service.generate(repo, tmp_path, [path])
    try:
        entities = store.get_entities(repo, result.index_revision)
        assert result.graph_nodes >= 4
        assert any(entity.qualified_name.endswith("Auth.validate") for entity in entities)
        assert all(entity.source_path == "auth.py" for entity in entities)
    finally:
        store.for_repo(repo).graph.delete()
