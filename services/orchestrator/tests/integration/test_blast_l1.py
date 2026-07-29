"""Integration: index fixture → GET /blast Confirmed fields (T019)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.adapters.falkordb_store import InMemoryFalkorStore
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings
from app.main import app
from app.services.l1_blast import BlastService
from app.services.l1_entity_cache import L1EntityCache
from app.services.l1_graph import L1GraphService
from app.services.l5_index import run_index
from tests.fixtures.l1_structural_repo_fixture import materialize_l1_structural_repo


def test_blast_from_indexed_fixture_returns_confirmed_fields(tmp_path: Path) -> None:
    root = materialize_l1_structural_repo(tmp_path / "fixture")
    store = InMemoryFalkorStore()
    # Add a dependent IMPORTS edge so blast has a non-empty direct list.
    settings = Settings(
        falkordb_url="memory://blast-int",
        pack_cache_dir=tmp_path / "packs",
        okf_cache_dir=tmp_path / "okf",
        okf_enabled=False,
    )
    service = L1GraphService(settings, store=store, cache=L1EntityCache())
    result = run_index(
        str(root),
        "blast-fixture",
        settings=settings,
        graph_service=service,
        skip_embed=True,
    )
    assert result.graph_nodes > 0
    revision = store.latest_revision("blast-fixture")
    assert revision
    # Inject a synthetic File→File IMPORTS edge for deterministic dependents.
    target = next(
        n for n in store.nodes["blast-fixture"].values() if n.source_path.endswith("auth.py")
    )
    dependent = StructuralNode(
        "dep-file",
        "blast-fixture",
        "python/dependent.py",
        "File",
        "python/dependent.py",
        1,
        1,
        revision,
    )
    store.nodes["blast-fixture"][dependent.entity_id] = dependent
    store.edges["blast-fixture"].append(
        StructuralEdge(
            dependent.entity_id,
            target.entity_id,
            "IMPORTS",
            "blast-fixture",
            dependent.source_path,
            revision,
        )
    )

    blast = BlastService(settings, store=store).compute(
        "blast-fixture", target.source_path
    )
    assert blast.direct_dependents == ["python/dependent.py"]
    assert blast.db_tables == []
    assert blast.owners == []
    assert blast.risk in {"HIGH", "MEDIUM", "LOW"}
    assert blast.index_revision == revision


def test_get_blast_http_against_shared_memory_store(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CONTEXTOS_FALKORDB_URL", "memory://ep006-tests")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_OKF_CACHE_DIR", str(tmp_path / "okf"))
    from app.adapters.falkordb_store import get_graph_store, reset_memory_graph_store
    from app.config import get_settings

    reset_memory_graph_store()
    get_settings.cache_clear()

    root = tmp_path / "repo"
    root.mkdir()
    (root / "lib.py").write_text("X = 1\n", encoding="utf-8")
    (root / "app.py").write_text("import lib\n", encoding="utf-8")

    client = TestClient(app)
    index = client.post(
        "/index",
        json={"repo_path": str(root), "repo_name": "http-blast"},
    )
    assert index.status_code == 200
    assert index.json()["graph_nodes"] > 0

    store = get_graph_store(get_settings())
    # Ensure IMPORTS edge exists between File nodes for this tiny repo.
    files = {
        n.source_path: n
        for n in store.nodes.get("http-blast", {}).values()
        if n.entity_kind == "File"
    }
    if "lib.py" in files and "app.py" in files:
        rev = store.latest_revision("http-blast")
        store.edges.setdefault("http-blast", []).append(
            StructuralEdge(
                files["app.py"].entity_id,
                files["lib.py"].entity_id,
                "IMPORTS",
                "http-blast",
                "app.py",
                rev or "r",
            )
        )

    response = client.get("/blast/lib.py", params={"repo": "http-blast"})
    assert response.status_code == 200
    body = response.json()
    assert "direct_dependents" in body
    assert body["owners"] == []
    assert body["risk"] in {"HIGH", "MEDIUM", "LOW"}
