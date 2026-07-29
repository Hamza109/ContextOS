from __future__ import annotations

from fastapi.testclient import TestClient

from app.adapters.l1_parser import StructuralNode
from app.main import app
from app.services.l1_entity_cache import get_l1_entity_cache
from app.services.l5_pack import PackResult
from app.services.l5_phase_pack import PhasePackResult
from app.services.l5_search import HybridSearchResult


def _entity(revision: str = "revision-1") -> StructuralNode:
    return StructuralNode(
        "entity-auth",
        "repo",
        "src/auth.py",
        "Method",
        "auth.Auth.validate",
        12,
        14,
        revision,
    )


def _patch_l5(monkeypatch) -> None:
    monkeypatch.setenv("CONTEXTOS_CONTEXT_SAFE_EDIT_ENRICHMENT", "false")
    monkeypatch.setattr(
        "app.api.context.load_pack_by_repo",
        lambda *args, **kwargs: PackResult("repo", "<base/>", 10, 1, 0, None),
    )
    monkeypatch.setattr(
        "app.api.context.hybrid_search",
        lambda **kwargs: HybridSearchResult([], 0, 0, False, [], None),
    )
    monkeypatch.setattr(
        "app.api.context.pack_for_phase",
        lambda *args, **kwargs: PhasePackResult("<base/>", 10, 5, 50.0, "Dev"),
    )
    monkeypatch.setattr("app.api.context.get_embedder", lambda *args, **kwargs: object())
    monkeypatch.setattr("app.api.context.QdrantStore", lambda *args, **kwargs: object())


def test_context_appends_cited_structural_evidence_on_cache_hit(monkeypatch) -> None:
    _patch_l5(monkeypatch)
    cache = get_l1_entity_cache()
    cache.refresh("repo", "revision-1", [_entity()])
    response = TestClient(app).post(
        "/context",
        json={"query": "where is auth validated?", "file": None, "repo": "repo", "top_k": 8},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "final_context",
        "metrics",
        "blast_radius",
        "memory",
        "relevant_files",
        "is_real",
    }
    assert "<l1_structural_evidence" in body["final_context"]
    assert 'citation="src/auth.py:12"' in body["final_context"]
    assert body["metrics"]["trace"]["l1_cache_hit"] is True


def test_context_l1_miss_and_blast_intent_preserve_l5(monkeypatch) -> None:
    _patch_l5(monkeypatch)
    client = TestClient(app)
    miss = client.post(
        "/context",
        json={"query": "where is auth validated?", "repo": "missing", "top_k": 8},
    ).json()
    assert miss["final_context"] == "<base/>"
    assert miss["metrics"]["trace"]["l1_structural_status"] == "l1_miss"

    cache = get_l1_entity_cache()
    cache.refresh("repo", "revision-1", [_entity()])
    # EP-007: blast hint without file → not permanent blast_declined; empty blast_radius.
    blast = client.post(
        "/context",
        json={"query": "what is the blast radius of auth?", "repo": "repo", "top_k": 8},
    ).json()
    assert blast["final_context"] == "<base/>"
    assert blast["metrics"]["trace"]["l1_structural_status"] == "blast_intent_no_file"
    assert blast["blast_radius"] == {}
    assert blast["metrics"]["trace"]["blast_status"] == "blast_no_file"


def test_context_blast_intent_with_file_populates_blast_radius(monkeypatch) -> None:
    _patch_l5(monkeypatch)
    from app.adapters.falkordb_store import get_graph_store, reset_memory_graph_store
    from app.adapters.l1_parser import StructuralEdge, StructuralNode
    from app.config import Settings, get_settings

    reset_memory_graph_store()
    get_settings.cache_clear()
    store = get_graph_store(Settings(falkordb_url="memory://ep006-tests"))
    a = StructuralNode("a", "repo", "src/auth.py", "File", "src/auth.py", 1, 2, "r1")
    b = StructuralNode("b", "repo", "src/app.py", "File", "src/app.py", 1, 2, "r1")
    store.persist(
        "repo",
        "r1",
        [a, b],
        [StructuralEdge("b", "a", "IMPORTS", "repo", "src/app.py", "r1")],
    )

    client = TestClient(app)
    body = client.post(
        "/context",
        json={
            "query": "what is the blast radius of auth?",
            "file": "src/auth.py",
            "repo": "repo",
            "top_k": 8,
        },
    ).json()
    assert body["final_context"] == "<base/>"
    blast = body["blast_radius"]
    assert blast["direct_dependents"] == ["src/app.py"]
    assert blast["db_tables"] == []
    assert blast["owners"] == []
    assert blast["risk"] in {"HIGH", "MEDIUM", "LOW"}
    assert body["metrics"]["trace"]["l1_structural_status"] == "blast_attached"
    assert body["metrics"]["trace"]["blast_status"] == "blast_attached"
