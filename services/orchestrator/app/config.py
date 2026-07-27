"""Application configuration.

Env keys are **Proposed** (not Confirmed Appendix D). Do not invent Confirmed config schemas.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Proposed orchestrator settings for EP-001."""

    model_config = SettingsConfigDict(env_prefix="CONTEXTOS_", env_file=".env", extra="ignore")

    # Proposed: Qdrant HTTP URL (ADR-003 / database-schema)
    qdrant_url: str = Field(default="http://localhost:6333", description="Proposed")

    # Confirmed model identity; env override is Proposed
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Confirmed model name; path override Proposed",
    )

    qdrant_collection: str = Field(default="codebase", description="Confirmed collection name")

    embedding_dim: int = Field(default=384, description="Confirmed dimension")

    # Proposed: pack artifact cache keyed by repo_name (OQ-PACK provisional — T018)
    pack_cache_dir: Path = Field(
        default=Path("/tmp/contextos/packs"),
        description="Proposed provisional pack cache root (OQ-PACK open)",
    )

    # Proposed: local inference (Ollama) for query-time non-exfil path (FR-020); unused by /index
    local_inference_url: str | None = Field(
        default=None,
        description="Proposed Ollama/base URL for local query-time inference (FR-020)",
    )
    local_inference_enabled: bool = Field(
        default=False,
        description="Proposed flag to prefer local inference when configured",
    )

    # Proposed: consent configuration flag only — no UX/storage schema (OQ-US016 open)
    external_llm_consent: bool = Field(
        default=False,
        description="Proposed deny-by-default consent flag (OQ-US016 UX/storage unresolved)",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
