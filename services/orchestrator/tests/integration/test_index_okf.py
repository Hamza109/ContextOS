"""Integration: OKF generate on index + privacy (EP-013 T012/T013/T017/T025)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.adapters.embeddings import HashEmbedder
from app.adapters.okf_bundle import OkfBundle, okf_bundle_root
from app.api.schemas_index import IndexResponse
from app.config import Settings
from app.main import app
from app.services.l5_index import run_index
from tests.fixtures.okf_knowledge_repo_fixture import (
    EXPECTED_DOC_CONCEPT_IDS,
    materialize_okf_knowledge_repo,
)


class RecordingStore:
    def __init__(self) -> None:
        self.upserts = 0

    def upsert_file_chunks(self, chunks, vectors, *, content_hashes=None):
        self.upserts += len(chunks)
        return len(chunks)


def test_index_fixture_writes_okf_with_provenance_and_exclusions(
    tmp_path: Path, monkeypatch
) -> None:
    repo = materialize_okf_knowledge_repo(tmp_path / "repo")
    okf_dir = tmp_path / "okf"
    packs = tmp_path / "packs"
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(packs))
    monkeypatch.setenv("CONTEXTOS_OKF_CACHE_DIR", str(okf_dir))
    monkeypatch.setenv("CONTEXTOS_FALKORDB_URL", "memory://okf-index")
    settings = Settings(
        pack_cache_dir=packs,
        okf_cache_dir=okf_dir,
        okf_enabled=True,
        falkordb_url="memory://okf-index",
    )
    store = RecordingStore()
    result = run_index(
        str(repo),
        "okf_knowledge",
        settings=settings,
        embedder=HashEmbedder(),
        store=store,  # type: ignore[arg-type]
    )
    # Confirmed four-field IndexResult shape (T013 / T025 Qdrant path remains)
    assert result.files_indexed >= 1
    assert result.embeddings >= 1
    assert store.upserts >= 1
    assert isinstance(result.graph_nodes, int)
    assert isinstance(result.time_ms, int)

    bundle = OkfBundle(okf_bundle_root(okf_dir, "okf_knowledge"))
    concepts = bundle.list_concepts()
    ids = {c.concept_id for c in concepts}
    assert EXPECTED_DOC_CONCEPT_IDS.issubset(ids)
    for concept in concepts:
        assert concept.type
        assert concept.frontmatter.get("sources") or concept.frontmatter.get("generated")
        blob = concept.body + str(concept.frontmatter)
        assert "must-not-become-okf-source" not in blob
        assert "SECRET_TOKEN" not in blob


def test_index_http_confirmed_four_fields_unchanged(tmp_path: Path, monkeypatch) -> None:
    repo = materialize_okf_knowledge_repo(tmp_path / "repo")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_OKF_CACHE_DIR", str(tmp_path / "okf"))
    monkeypatch.setenv("CONTEXTOS_FALKORDB_URL", "memory://okf-http")

    from app.api import index as index_api
    from app.adapters.embeddings import HashEmbedder

    store = RecordingStore()

    def _fast_index(repo_path, repo_name, *, paths=None, files=None):
        return run_index(
            repo_path,
            repo_name,
            paths=paths,
            files=files,
            settings=Settings(
                pack_cache_dir=tmp_path / "packs",
                okf_cache_dir=tmp_path / "okf",
                okf_enabled=True,
                falkordb_url="memory://okf-http",
            ),
            embedder=HashEmbedder(),
            store=store,  # type: ignore[arg-type]
        )

    monkeypatch.setattr(index_api, "run_index", _fast_index)
    client = TestClient(app)
    response = client.post(
        "/index",
        json={"repo_path": str(repo), "repo_name": "okf_http"},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"files_indexed", "graph_nodes", "embeddings", "time_ms"}
    IndexResponse.model_validate(body)
    assert body["embeddings"] >= 1


def test_okf_failure_preserves_index_outcome(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "a.py").write_text("x = 1\n", encoding="utf-8")
    settings = Settings(
        pack_cache_dir=tmp_path / "packs",
        okf_cache_dir=tmp_path / "okf",
        okf_enabled=True,
        falkordb_url="memory://okf-fail",
    )
    from app.services.okf_generate import OkfGenerateResult

    monkeypatch.setattr(
        "app.services.l5_index.generate_okf_bundle",
        lambda *a, **k: OkfGenerateResult(
            status="error",
            concepts_written=0,
            sources_used=0,
            duration_ms=1,
            index_revision="x",
            bundle_root=None,
            error="RuntimeError",
        ),
    )
    result = run_index(
        str(root),
        "okf_fail",
        settings=settings,
        embedder=HashEmbedder(),
        store=RecordingStore(),  # type: ignore[arg-type]
    )
    assert result.embeddings >= 1
    assert result.files_indexed >= 1
