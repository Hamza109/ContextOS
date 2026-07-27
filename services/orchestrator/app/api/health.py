"""GET / health — report qdrant; falkor unused/degraded OK for EP-001."""

from __future__ import annotations

from fastapi import APIRouter

from app.adapters.qdrant_store import QdrantStore
from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get(
    "/",
    summary="Health and dependency status",
    description=(
        "Confirmed fields: status, pipeline, falkor, qdrant. "
        "Falkor may be unused/degraded for EP-001 without failing MVP indexing."
    ),
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
