"""Pydantic models for confirmed POST /index fields only (+ Proposed optional scope)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    """Confirmed request fields: repo_path, repo_name.

    Optional paths/files are **Proposed** only (OQ-14) — not Confirmed Appendix D.
    """

    repo_path: str = Field(..., description="Confirmed: local path to repository")
    repo_name: str = Field(..., description="Confirmed: logical repository name")
    # Proposed (OQ-14) — narrower scope for incremental re-index; not Confirmed
    paths: list[str] | None = Field(
        default=None,
        description="Proposed (OQ-14): optional path scope for incremental index — not Confirmed",
    )
    files: list[str] | None = Field(
        default=None,
        description="Proposed (OQ-14): optional file list for incremental index — not Confirmed",
    )


class IndexResponse(BaseModel):
    """Confirmed response fields only; graph_nodes now carries persisted L1 count."""

    files_indexed: int
    graph_nodes: int
    embeddings: int
    time_ms: int
