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

    # --- EP-002 Proposed search / packing knobs (NOT Confirmed Appendix D) ---
    search_mmr_lambda: float = Field(
        default=0.7,
        description="Proposed MMR λ (relevance vs diversity) — not Confirmed",
    )
    search_vector_weight: float = Field(
        default=0.55,
        description="Proposed vector fusion weight — not Confirmed",
    )
    search_bm25_weight: float = Field(
        default=0.45,
        description="Proposed BM25 fusion weight — not Confirmed",
    )
    search_candidate_pool: int = Field(
        default=40,
        description="Proposed candidate pool size before MMR — not Confirmed",
    )
    default_phase: str = Field(
        default="Dev",
        description="Proposed default SDLC phase when OQ-16 phase omitted — not Confirmed",
    )

    # --- EP-003 Proposed Serena MCP knobs (NOT Confirmed product freeze; ADR-005) ---
    # OQ-Symbol-REST remains open — these configure orchestrator→Serena enrichment only.
    serena_enabled: bool = Field(
        default=True,
        description="Proposed: enable Serena MCP adapter for L3 enrichment",
    )
    serena_command: str | None = Field(
        default=None,
        description=(
            "Proposed: Serena MCP launch command (stdio). "
            "SDK package pin NEEDS CLARIFICATION — do not invent Confirmed pin."
        ),
    )
    serena_args: str = Field(
        default="",
        description="Proposed: space-separated extra args for Serena MCP process",
    )
    serena_cwd: str | None = Field(
        default=None,
        description="Proposed: working directory for Serena MCP process",
    )
    serena_timeout_seconds: float = Field(
        default=30.0,
        description="Proposed: Serena MCP call timeout seconds",
    )
    serena_use_test_double: bool = Field(
        default=False,
        description=(
            "Proposed: force InMemorySerenaDouble (tests/local without live MCP). "
            "OQ-MCP-Fallback — not Confirmed product UX."
        ),
    )
    # Proposed: optional Pack Context safe-edit enrichment on POST /context (US-010).
    # Does not invent Confirmed Appendix D response fields — content goes in final_context.
    context_safe_edit_enrichment: bool = Field(
        default=True,
        description=(
            "Proposed: attach Serena-informed safe edit plan block to final_context "
            "(OQ-Safe-Edit-Shape open — delimited text interim)"
        ),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
