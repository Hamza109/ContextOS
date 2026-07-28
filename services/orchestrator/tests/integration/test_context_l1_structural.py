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


def test_context_l1_miss_and_blast_decline_preserve_l5(monkeypatch) -> None:
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
    blast = client.post(
        "/context",
        json={"query": "what is the blast radius of auth?", "repo": "repo", "top_k": 8},
    ).json()
    assert blast["final_context"] == "<base/>"
    assert blast["metrics"]["trace"]["l1_structural_status"] == "blast_declined"
    assert blast["blast_radius"] == {}
