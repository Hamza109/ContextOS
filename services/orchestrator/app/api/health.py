"""GET / health with unchanged public fields and live L1/L5 dependencies."""

from __future__ import annotations

from fastapi import APIRouter

from app.adapters.falkordb_store import FalkorDBStore
from app.adapters.qdrant_store import QdrantStore
from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get(
    "/",
    summary="Health and dependency status",
    description=(
        "Confirmed fields: status (ok|degraded|error), pipeline, falkor, qdrant "
        "(api-contract §2.1). "
        "FalkorDB backs L1 and Qdrant backs L5; either may report degraded readiness. "
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
    if settings.falkordb_url.startswith("memory://"):
        falkor_status = "ok"
    else:
        falkor_status = FalkorDBStore(settings).health()

    if qdrant_status == "ok" and falkor_status == "ok":
        status = "ok"
        pipeline = "l1_l5_index_ready"
    else:
        status = "degraded"
        unavailable = []
        if falkor_status != "ok":
            unavailable.append("falkordb")
        if qdrant_status != "ok":
            unavailable.append("qdrant")
        pipeline = f"index_dependencies_unavailable:{','.join(unavailable)}"

    return {
        "status": status,
        "pipeline": pipeline,
        "falkor": falkor_status,
        "qdrant": qdrant_status,
    }
