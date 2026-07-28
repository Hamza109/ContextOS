"""Integration / contract: OKF-first /context (EP-013 T019/T021–T024)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.adapters.embeddings import HashEmbedder
from app.adapters.okf_bundle import OkfBundle, okf_bundle_root
from app.config import Settings
from app.main import app
from app.services.l5_index import run_index
from app.services.l5_pack import PackResult
from app.services.l5_phase_pack import PhasePackResult
from app.services.l5_search import HybridSearchResult, SearchHit
from tests.fixtures.okf_knowledge_repo_fixture import materialize_okf_knowledge_repo

CONFIRMED_RESPONSE_FIELDS = {
    "final_context",
    "metrics",
    "blast_radius",
    "memory",
    "relevant_files",
    "is_real",
}


class RecordingStore:
    def __init__(self) -> None:
        self.upserts = 0

    def upsert_file_chunks(self, chunks, vectors, *, content_hashes=None):
        self.upserts += len(chunks)
        return len(chunks)


def _patch_safe_edit_off(monkeypatch) -> None:
    monkeypatch.setenv("CONTEXTOS_CONTEXT_SAFE_EDIT_ENRICHMENT", "false")


def test_context_okf_hit_with_embeddings_stubbed(tmp_path: Path, monkeypatch) -> None:
    _patch_safe_edit_off(monkeypatch)
    repo = materialize_okf_knowledge_repo(tmp_path / "repo")
    packs = tmp_path / "packs"
    okf_dir = tmp_path / "okf"
    settings = Settings(
        pack_cache_dir=packs,
        okf_cache_dir=okf_dir,
        okf_enabled=True,
        falkordb_url="memory://okf-ctx",
        context_safe_edit_enrichment=False,
    )
    run_index(
        str(repo),
        "okf_ctx",
        settings=settings,
        embedder=HashEmbedder(),
        store=RecordingStore(),  # type: ignore[arg-type]
        skip_embed=True,
    )
    # Ensure bundle exists even with skip_embed
    assert OkfBundle(okf_bundle_root(okf_dir, "okf_ctx")).list_concepts()

    monkeypatch.setenv("CONTEXTOS_OKF_CACHE_DIR", str(okf_dir))
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(packs))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")
    monkeypatch.setenv("CONTEXTOS_FALKORDB_URL", "memory://okf-ctx")
    monkeypatch.setattr(
        "app.api.context.get_settings",
        lambda: Settings(
            pack_cache_dir=packs,
            okf_cache_dir=okf_dir,
            okf_enabled=True,
            falkordb_url="memory://okf-ctx",
            context_safe_edit_enrichment=False,
        ),
    )
    monkeypatch.setattr(
        "app.api.context.load_pack_by_repo",
        lambda *a, **k: PackResult("okf_ctx", "<base/>", 10, 1, 0, None),
    )
    monkeypatch.setattr(
        "app.api.context.hybrid_search",
        lambda **kwargs: HybridSearchResult([], 0, 0, True, ["embeddings_stubbed"], None),
    )
    monkeypatch.setattr(
        "app.api.context.pack_for_phase",
        lambda *a, **k: PhasePackResult("<base/>", 10, 5, 50.0, "Dev"),
    )
    monkeypatch.setattr("app.api.context.get_embedder", lambda *a, **k: object())
    monkeypatch.setattr("app.api.context.QdrantStore", lambda *a, **k: object())

    body = TestClient(app).post(
        "/context",
        json={
            "query": "What is the architecture overview and API contract?",
            "repo": "okf_ctx",
            "top_k": 8,
        },
    ).json()
    assert set(body) == CONFIRMED_RESPONSE_FIELDS
    assert "<okf_evidence" in body["final_context"]
    assert 'citation="okf:docs/architecture/system-overview"' in body["final_context"]
    assert body["metrics"]["trace"]["okf_status"] == "hit"
    assert body["metrics"]["trace"]["okf_concept_count"] >= 1


def test_context_okf_miss_falls_back_to_hybrid(tmp_path: Path, monkeypatch) -> None:
    _patch_safe_edit_off(monkeypatch)
    packs = tmp_path / "packs"
    okf_dir = tmp_path / "okf"
    # Seed empty-ish bundle with unrelated concept
    bundle = OkfBundle(okf_bundle_root(okf_dir, "okf_miss"))
    bundle.write_concept(
        "docs/architecture/system-overview",
        type="Architecture Doc",
        title="Architecture Overview",
        description="API layers",
        tags=["architecture"],
        sources=[{"uri": "docs/architecture/system-overview.md"}],
        generated={"by": "process:contextos-okf-generator", "at": "2026-07-28T00:00:00Z"},
        repo="okf_miss",
        index_revision="r1",
        body="# Architecture\n",
    )
    monkeypatch.setattr(
        "app.api.context.get_settings",
        lambda: Settings(
            pack_cache_dir=packs,
            okf_cache_dir=okf_dir,
            okf_enabled=True,
            falkordb_url="memory://okf-miss",
            context_safe_edit_enrichment=False,
        ),
    )
    monkeypatch.setattr(
        "app.api.context.load_pack_by_repo",
        lambda *a, **k: PackResult("okf_miss", "<base/>", 10, 1, 0, None),
    )
    hit = SearchHit(
        path="src/auth.py",
        score=0.9,
        content="def authenticate",
        start_line=1,
        end_line=3,
        vector_score=0.8,
        bm25_score=0.7,
    )
    monkeypatch.setattr(
        "app.api.context.hybrid_search",
        lambda **kwargs: HybridSearchResult([hit], 1, 1, False, [], None),
    )
    monkeypatch.setattr(
        "app.api.context.pack_for_phase",
        lambda *a, **k: PhasePackResult(
            "<file path='src/auth.py'>authenticate</file>",
            20,
            10,
            50.0,
            "Dev",
        ),
    )
    monkeypatch.setattr("app.api.context.get_embedder", lambda *a, **k: object())
    monkeypatch.setattr("app.api.context.QdrantStore", lambda *a, **k: object())

    body = TestClient(app).post(
        "/context",
        json={
            "query": "where is the authenticate function implemented in auth.py?",
            "repo": "okf_miss",
            "top_k": 8,
        },
    ).json()
    assert set(body) == CONFIRMED_RESPONSE_FIELDS
    assert body["metrics"]["trace"]["okf_status"] == "miss"
    assert "<okf_evidence" not in body["final_context"]
    assert body["metrics"]["trace"]["vector_hits"] == 1
    assert body["metrics"]["trace"]["bm25_hits"] == 1
    assert any(f.get("path") == "src/auth.py" for f in body["relevant_files"])


def test_qdrant_indexing_remains_when_okf_enabled(tmp_path: Path) -> None:
    """T025 regression: okf_enabled=true must not skip embeddings upsert."""
    repo = materialize_okf_knowledge_repo(tmp_path / "repo")
    store = RecordingStore()
    settings = Settings(
        pack_cache_dir=tmp_path / "packs",
        okf_cache_dir=tmp_path / "okf",
        okf_enabled=True,
        falkordb_url="memory://okf-qdrant",
    )
    result = run_index(
        str(repo),
        "okf_qdrant",
        settings=settings,
        embedder=HashEmbedder(),
        store=store,  # type: ignore[arg-type]
    )
    assert result.embeddings >= 1
    assert store.upserts == result.embeddings
