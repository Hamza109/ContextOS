"""GET /blast/{file_name} — Confirmed FR-08 blast radius (EP-007 / US-018).

OpenAPI sketch (T002): Confirmed response fields from api-contract §2.4;
Proposed owners: [] (OQ-15); Proposed index_revision freshness; Proposed
HTTP 200 / 404 / 503 (501 reserved if capability gated — not used once shipped).
IgnorePolicy ownership stays FastAPI-side (T010); MCP must not reimplement.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.api.schemas_blast import BlastResponse
from app.config import get_settings
from app.services.l1_blast import (
    DEFAULT_BLAST_HOPS,
    BlastNotFoundError,
    BlastService,
    BlastUnavailableError,
)
from app.telemetry.blast import blast_span, record_blast_attributes

router = APIRouter(tags=["blast"])


@router.get(
    "/blast/{file_name:path}",
    response_model=BlastResponse,
    summary="L1 blast-radius analysis for a file",
    description=(
        "Confirmed (api-contract §2.4): direct_dependents, transitive, db_tables, "
        "risk ∈ {HIGH,MEDIUM,LOW}, tests_to_run. "
        "Proposed: owners: [] only (OQ-15 — no element schema); "
        "index_revision freshness signal (US-027). "
        "Proposed statuses: 200; 404 unknown repo/file; 503 store unavailable. "
        "No source bodies. Auth/RBAC: OQ-01 open — local trusted draft."
    ),
    responses={
        200: {"description": "Proposed: success"},
        404: {"description": "Proposed: unknown repo or file"},
        503: {"description": "Proposed: graph store unavailable"},
    },
)
def get_blast(
    file_name: str,
    repo: str = Query(..., min_length=1, description="Confirmed query param"),
    max_hops: int = Query(
        DEFAULT_BLAST_HOPS,
        ge=1,
        le=5,
        description="Proposed hop bound (default 3; BRD IMPORTS*1..3)",
    ),
) -> BlastResponse:
    settings = get_settings()
    with blast_span("blast.request", repo=repo) as span:
        try:
            result = BlastService(settings).compute(
                repo, file_name, max_hops=max_hops
            )
        except BlastNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except BlastUnavailableError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        record_blast_attributes(
            span,
            duration_ms=result.duration_ms,
            hop_depth=result.hop_depth,
            node_count=result.node_count,
            direct_count=len(result.direct_dependents),
            transitive_count=len(result.transitive),
        )
        payload = result.as_response_dict()
        return BlastResponse(**payload)
