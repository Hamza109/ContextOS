"""GET / health — report qdrant; falkor unused/degraded OK for EP-001 / EP-005 A-07."""

from __future__ import annotations

from fastapi import APIRouter

from app.adapters.qdrant_store import QdrantStore
from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get(
    "/",
    summary="Health and dependency status",
    description=(
        "Confirmed fields: status (ok|degraded|error), pipeline, falkor, qdrant "
        "(api-contract §2.1). "
        "Falkor may be unused/absent for MVP without failing search readiness (A-07). "
        "HTTP status mapping is Proposed only (OQ-HTTP-Health): e.g. 200 for "
        "healthy/degraded body, 503 if critical deps down — MUST NOT Confirmed-freeze. "
        "Degraded search response shape remains Proposed (OQ-Degraded-Shape). "
        "SC-007 uptime Pass blocked on OQ-Uptime-Harness."
    ),
    responses={
        200: {
            "description": (
                "Proposed: healthy or degraded body with Confirmed fields "
                "(OQ-HTTP-Health — not Confirmed-frozen)"
            )
        },
        503: {
            "description": (
                "Proposed: critical dependency unavailable "
                "(OQ-HTTP-Health — not Confirmed-frozen; not currently emitted by default)"
            )
        },
    },
)
def health() -> dict:
    settings = get_settings()
    qdrant_status = QdrantStore(settings).health()
    # Falkor unused for EP-001 graph writes — report unused/degraded, do not fail MVP
    falkor_status = "unused"

    if qdrant_status == "ok":
        status = "ok"
        pipeline = "l5_index_ready"
    else:
        status = "degraded"
        pipeline = "l5_index_qdrant_unavailable"

    return {
        "status": status,
        "pipeline": pipeline,
        "falkor": falkor_status,
        "qdrant": qdrant_status,
    }
