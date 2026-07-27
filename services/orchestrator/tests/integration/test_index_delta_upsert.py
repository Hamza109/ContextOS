"""Delta upsert replaces Qdrant chunks for changed file_path (T062)."""

from __future__ import annotations

from pathlib import Path

from app.adapters.embeddings import HashEmbedder
from app.services.l5_index import run_index


class DeltaStore:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def upsert_file_chunks(self, chunks, vectors, *, content_hashes=None):
        self.calls.append([c.file_path for c in chunks])
        return len(chunks)


def test_delta_reindex_scopes_to_file(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    (root / "a.py").write_text("a=1\n", encoding="utf-8")
    (root / "b.py").write_text("b=1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    store = DeltaStore()
    result = run_index(
        str(root),
        "delta",
        files=["a.py"],
        embedder=HashEmbedder(),
        store=store,  # type: ignore[arg-type]
    )
    assert result.mode == "incremental"
    assert result.files_indexed == 1
    assert store.calls
    assert set(store.calls[0]) == {"a.py"}
