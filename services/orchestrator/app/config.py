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

    # --- EP-006 approved local/VPC FalkorDB and L1 cache knobs ---
    falkordb_url: str = Field(
        default="redis://localhost:6379",
        description="Proposed local/VPC FalkorDB URL; credentials come from environment only",
    )
    falkordb_graph_prefix: str = Field(
        default="contextos",
        description="Proposed graph-name prefix used for repository isolation",
    )
    falkordb_timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        description="Proposed FalkorDB socket/connect timeout",
    )
    l1_cache_max_entries: int = Field(default=10_000, gt=0)
    l1_cache_ttl_seconds: float = Field(default=300.0, gt=0)

    # Proposed: pack artifact cache keyed by repo_name (OQ-PACK provisional — T018)
    pack_cache_dir: Path = Field(
        default=Path("/tmp/contextos/packs"),
        description="Proposed provisional pack cache root (OQ-PACK open)",
    )

    # --- EP-013 Proposed OKF knobs (NOT Confirmed Appendix D) ---
    okf_cache_dir: Path = Field(
        default=Path("/tmp/contextos/okf"),
        description="Proposed OKF bundle cache root beside pack cache (OQ-OKF-01)",
    )
    okf_enabled: bool = Field(
        default=True,
        description="Proposed: enable OKF generate on /index and retrieve on /context",
    )
    okf_link_expand_limit: int = Field(
        default=5,
        gt=0,
        description="Proposed: max linked concepts to expand on OKF hit",
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

    # --- EP-008 Proposed L4 knobs (NOT Confirmed Appendix D; OQ-07/08/09 open) ---
    l4_enabled: bool = Field(
        default=False,
        description=(
            "Proposed: enable L4 Headroom-style compression on POST /context "
            "(default off — packing-estimate metrics when false)"
        ),
    )
    # Injectable phase → max_tokens. No Confirmed Dev=8k/12k (OQ-07). Design=32k is an
    # evidenced FR-11 example only — populate via env/tests, not hard-coded product truth.
    phase_budgets: dict[str, int] = Field(
        default_factory=dict,
        description=(
            "Proposed: phase→max_tokens map (JSON env OK). Empty = no hard ceiling. "
            "Dev canonical value [NEEDS CLARIFICATION: OQ-07]."
        ),
    )
    # Optional $/token stub — rates Missing Evidence (OQ-EP008-c); token-delta is primary.
    l4_cost_rate_per_1k_tokens: float | None = Field(
        default=None,
        description=(
            "Proposed optional cost stub ($ per 1k tokens). Missing Evidence for "
            "product rates — emit token-delta cost_saved when unset."
        ),
    )
    l4_relevance_summarize_threshold: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="Proposed: units at/below this relevance score are summarized aggressively",
    )
    l4_telemetry_enabled: bool = Field(
        default=True,
        description=(
            "Proposed: emit OTel-compatible compression attrs when L4 runs "
            "(OQ-EP008-b opt-out shape open — honor this flag only)"
        ),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
