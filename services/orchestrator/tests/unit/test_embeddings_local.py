"""Local 384-dim embedder + no external LLM (T033)."""

from __future__ import annotations

import pytest

from app.adapters.embeddings import HashEmbedder, LocalMiniLMEmbedder


def test_hash_embedder_384_dim() -> None:
    emb = HashEmbedder()
    vectors = emb.embed(["hello world", "second"])
    assert len(vectors) == 2
    assert all(len(v) == 384 for v in vectors)


def test_local_embedder_rejects_http_endpoint() -> None:
    with pytest.raises(RuntimeError, match="forbidden|refused"):
        LocalMiniLMEmbedder(model_name="https://api.openai.com/v1/embeddings")


def test_local_embedder_rejects_openai_named() -> None:
    with pytest.raises(RuntimeError, match="refused"):
        LocalMiniLMEmbedder(model_name="openai/text-embedding-3-small")
