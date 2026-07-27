"""Local CPU embeddings via sentence-transformers/all-MiniLM-L6-v2 (ADR-003).

Hard-fails if configured to call external LLM embedding endpoints (FR-007, NFR-005).
"""

from __future__ import annotations

import hashlib
import logging
from typing import Protocol

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

CONFIRMED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CONFIRMED_DIM = 384

# Hostnames/URLs that must never be used for index-time embeddings.
_FORBIDDEN_LLM_MARKERS = (
    "api.openai.com",
    "generativelanguage.googleapis.com",
    "api.anthropic.com",
    "api.cohere.ai",
    "openai",
    "anthropic",
    "gemini",
)


class EmbeddingBackend(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class LocalMiniLMEmbedder:
    """Loads local all-MiniLM-L6-v2 on CPU. Never calls external LLM APIs."""

    def __init__(self, model_name: str = CONFIRMED_MODEL, dim: int = CONFIRMED_DIM) -> None:
        self._guard_model_name(model_name)
        self.model_name = model_name
        self.dim = dim
        self._model = None

    @staticmethod
    def _guard_model_name(model_name: str) -> None:
        lower = model_name.lower()
        for marker in _FORBIDDEN_LLM_MARKERS:
            if marker in lower and "minilm" not in lower:
                raise RuntimeError(
                    f"External LLM embedding endpoint refused for index path: {model_name}"
                )
        if lower.startswith("http://") or lower.startswith("https://"):
            raise RuntimeError(
                f"HTTP embedding endpoints are forbidden on index path: {model_name}"
            )

    def _ensure_model(self):
        if self._model is not None:
            return self._model
        from sentence_transformers import SentenceTransformer

        logger.info("Loading local embedding model %s (CPU)", self.model_name)
        self._model = SentenceTransformer(self.model_name, device="cpu")
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._ensure_model()
        vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        out: list[list[float]] = []
        for row in vectors:
            vec = [float(x) for x in row]
            if len(vec) != self.dim:
                raise RuntimeError(f"Expected {self.dim}-dim embeddings, got {len(vec)}")
            out.append(vec)
        return out


class HashEmbedder:
    """Deterministic 384-dim stub for unit tests (not for production indexing)."""

    def __init__(self, dim: int = CONFIRMED_DIM) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            # Expand hash bytes into dim floats in [-1, 1]
            vals: list[float] = []
            seed = digest
            while len(vals) < self.dim:
                for b in seed:
                    vals.append((b / 127.5) - 1.0)
                    if len(vals) >= self.dim:
                        break
                seed = hashlib.sha256(seed).digest()
            out.append(vals[: self.dim])
        return out


def get_embedder(settings: Settings | None = None, *, stub: bool = False) -> EmbeddingBackend:
    cfg = settings or get_settings()
    if stub:
        return HashEmbedder(dim=cfg.embedding_dim)
    return LocalMiniLMEmbedder(model_name=cfg.embedding_model, dim=cfg.embedding_dim)
