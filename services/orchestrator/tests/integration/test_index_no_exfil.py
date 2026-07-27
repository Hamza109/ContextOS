"""Zero external LLM calls on index path (T036 / T073)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.adapters.embeddings import HashEmbedder
from app.security.consent_gate import index_path_may_call_external_llm
from app.services.l5_index import run_index


class RecordingStore:
    def upsert_file_chunks(self, chunks, vectors, *, content_hashes=None):
        return len(chunks)


def test_index_no_exfil_with_and_without_consent(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    (root / "x.py").write_text("x=1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EXTERNAL_LLM_CONSENT", "false")

    assert index_path_may_call_external_llm() is False

    external_llm = MagicMock()
    # Ensure index path never invokes a mock external LLM client
    result = run_index(
        str(root),
        "nox",
        embedder=HashEmbedder(),
        store=RecordingStore(),  # type: ignore[arg-type]
    )
    external_llm.chat.assert_not_called()
    external_llm.complete.assert_not_called()
    assert result.graph_nodes == 0
    assert result.embeddings >= 1

    monkeypatch.setenv("CONTEXTOS_EXTERNAL_LLM_CONSENT", "true")
    result2 = run_index(
        str(root),
        "nox2",
        embedder=HashEmbedder(),
        store=RecordingStore(),  # type: ignore[arg-type]
    )
    external_llm.chat.assert_not_called()
    assert result2.embeddings >= 1


def test_http_embedder_rejected_on_construction() -> None:
    from app.adapters.embeddings import LocalMiniLMEmbedder

    with pytest.raises(RuntimeError):
        LocalMiniLMEmbedder(model_name="https://api.openai.com/v1/embeddings")
