"""Excluded paths never appear in Qdrant payloads (EP-005 T011 / SC-001 e2e).

Packs AND embeddings must omit fixture excluded paths after run_index.
"""

from __future__ import annotations

from pathlib import Path

from app.adapters.embeddings import HashEmbedder
from app.adapters.fs_walker import walk_allowed_files
from app.services.l5_index import run_index
from app.services.l5_pack import pack_repository
from tests.fixtures.ignore_exclusion_repo import (
    ALLOWED_REL_PATHS,
    EXCLUDED_REL_PATHS,
    materialize_ignore_exclusion_repo,
)


class CapturingStore:
    def __init__(self) -> None:
        self.payloads: list[dict] = []

    def upsert_file_chunks(self, chunks, vectors, *, content_hashes=None):
        for c in chunks:
            self.payloads.append({"repo_name": c.repo_name, "file_path": c.file_path})
        return len(chunks)


def test_excluded_paths_not_in_payloads(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    (root / "ok.py").write_text("ok=1\n", encoding="utf-8")
    (root / ".env").write_text("S=1\n", encoding="utf-8")
    (root / "node_modules" / "a.js").parent.mkdir(parents=True)
    (root / "node_modules" / "a.js").write_text("1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    store = CapturingStore()
    run_index(str(root), "exq", embedder=HashEmbedder(), store=store)  # type: ignore[arg-type]

    paths = {p["file_path"] for p in store.payloads}
    assert "ok.py" in paths
    assert ".env" not in paths
    assert not any("node_modules" in p for p in paths)

    # Walker-level confirmation
    allowed = walk_allowed_files(root)
    assert all(".env" not in str(p) for p in allowed)


def test_shared_fixture_packs_and_embeddings(tmp_path: Path, monkeypatch) -> None:
    """Full fixture e2e: excluded absent from pack XML and embedding payloads."""
    root = materialize_ignore_exclusion_repo(tmp_path / "fixture_repo")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    store = CapturingStore()
    result = run_index(
        str(root),
        "fixture_e2e",
        embedder=HashEmbedder(),
        store=store,  # type: ignore[arg-type]
    )
    assert result.pack is not None
    for excl in EXCLUDED_REL_PATHS:
        assert f'path="{excl}"' not in result.pack.xml_content
        assert excl not in {p["file_path"] for p in store.payloads}

    emb_paths = {p["file_path"] for p in store.payloads}
    for ok in ALLOWED_REL_PATHS:
        assert ok in emb_paths or f'path="{ok}"' in result.pack.xml_content

    # Scoped paths/files filtered AFTER allow-list — cannot force .env
    store2 = CapturingStore()
    run_index(
        str(root),
        "fixture_scoped",
        files=[".env", "src/main.py"],
        embedder=HashEmbedder(),
        store=store2,  # type: ignore[arg-type]
    )
    scoped_paths = {p["file_path"] for p in store2.payloads}
    assert ".env" not in scoped_paths
    assert "src/main.py" in scoped_paths

    # Pack-only confirmation for same fixture
    pack = pack_repository(root, "fixture_pack_only")
    assert pack.files_packed >= 1
    assert all(f'path="{e}"' not in pack.xml_content for e in EXCLUDED_REL_PATHS)
