"""Excluded paths never appear in Qdrant payloads (T037)."""

from __future__ import annotations

from pathlib import Path

from app.adapters.embeddings import HashEmbedder
from app.adapters.fs_walker import walk_allowed_files
from app.services.l5_index import run_index


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
