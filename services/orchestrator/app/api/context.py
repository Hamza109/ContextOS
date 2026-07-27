"""POST /context router — Confirmed contract + Proposed extensions (EP-002).

Security: reuse ignore_policy / consent_gate inheritance from EP-001 packs/index.
Do NOT re-read excluded paths from disk to “help” packing (FR-018).
RBAC hook reserved — OQ-01 Missing Evidence (do not invent roles).
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, HTTPException

from app.adapters.embeddings import get_embedder
from app.adapters.qdrant_store import QdrantStore
from app.api.schemas_context import ContextMetrics, ContextRequest, ContextResponse
from app.config import get_settings
from app.services.l5_phase_pack import DEFAULT_PHASE, pack_for_phase
from app.services.l5_pack import load_pack_by_repo
from app.services.l5_search import hits_to_relevant_files, hybrid_search
from app.telemetry.context import child_span, context_span, record_duration_ms

logger = logging.getLogger(__name__)

router = APIRouter(tags=["context"])


@router.post(
    "/context",
    response_model=ContextResponse,
    summary="Retrieve hybrid-search packed context (L5)",
    description=(
        "Confirmed request: query, file (optional), repo, top_k. "
        "Confirmed response: final_context, metrics "
        "(tokens_before, tokens_after, saving_percent, trace), "
        "blast_radius, memory, relevant_files, is_real. "
        "Proposed (OQ-16): optional phase — NOT Appendix D Confirmed; default Dev. "
        "Proposed relevant_files item keys (path/score/...). "
        "Citations: file:line + confidence attributes inside final_context "
        "(OQ-11 open — Proposed XML interim). "
        "HTTP status codes Proposed only (OQ-HTTP-/context). "
        "FR-019 consumer note: future contextos ask / extension Ask SHOULD call this API; "
        "CLI/extension DX is out of scope for EP-002. "
        "No L4 Headroom gate (ADR-006)."
    ),
    responses={
        200: {"description": "Proposed: success (OQ-HTTP-/context)"},
        400: {"description": "Proposed: validation failure (OQ-HTTP-/context)"},
        403: {"description": "Proposed: RBAC/consent denial when schema exists (OQ-01 open)"},
        404: {"description": "Proposed: unknown/not-indexed repo (OQ-HTTP-/context)"},
        503: {"description": "Proposed: dependency degraded (OQ-HTTP-/context)"},
    },
)
def post_context(body: ContextRequest) -> ContextResponse:
    # OQ-01: RBAC/authn hook reserved — Missing Evidence; local/dev loopback MAY apply.
    # if not rbac_allows(actor, body.repo): raise HTTPException(403, ...)

    settings = get_settings()
    phase = body.phase or settings.default_phase or DEFAULT_PHASE

    with context_span("context.request", repo=body.repo, attributes={"top_k": body.top_k}) as span:
        started = time.perf_counter()
        pack = load_pack_by_repo(body.repo, settings=settings)

        # Prefer degraded partial results when pack missing but Qdrant may still have vectors
        if pack is None:
            # Soft probe: if neither pack nor any vector path likely — Proposed 404
            store = QdrantStore(settings)
            try:
                # Cheap health; actual emptiness checked after search
                if store.health() == "error":
                    raise HTTPException(
                        status_code=503,
                        detail="search dependencies unavailable (Proposed 503)",
                    )
            except HTTPException:
                raise
            except Exception:  # noqa: BLE001
                pass

        try:
            embedder = get_embedder(settings, stub=_use_stub_embedder())
            store = QdrantStore(settings)
            result = hybrid_search(
                query=body.query,
                repo=body.repo,
                top_k=body.top_k,
                file_bias=body.file,
                settings=settings,
                embedder=embedder,
                store=store,
                pack=pack,
            )
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("context search failed")
            raise HTTPException(status_code=500, detail=f"context search failed: {exc}") from exc

        if pack is None and not result.hits:
            raise HTTPException(
                status_code=404,
                detail=f"repo not indexed or pack missing: {body.repo} (Proposed 404)",
            )

        with child_span("context.pack.assemble") as pspan:
            t_pack = time.perf_counter()
            packed = pack_for_phase(
                result.hits,
                query=body.query,
                repo=body.repo,
                phase=phase,
                include_citations=True,
            )
            record_duration_ms(pspan, "duration_ms", (time.perf_counter() - t_pack) * 1000)

        trace: dict[str, Any] = {
            "phase": packed.phase,
            "vector_hits": result.vector_hits,
            "bm25_hits": result.bm25_hits,
            "mmr_selected": len(result.hits),
            "degraded": result.degraded,
            "notes": result.trace_notes,
            "duration_ms": int((time.perf_counter() - started) * 1000),
            "citations": "proposed_xml_attributes_oq11_open",
            "l4_gate": False,
        }
        record_duration_ms(span, "duration_ms", float(trace["duration_ms"]))

        return ContextResponse(
            final_context=packed.final_context,
            metrics=ContextMetrics(
                tokens_before=packed.tokens_before,
                tokens_after=packed.tokens_after,
                saving_percent=packed.saving_percent,
                trace=trace,
            ),
            blast_radius={},  # Proposed empty MVP
            memory={},  # Proposed empty MVP
            relevant_files=hits_to_relevant_files(result.hits),
            is_real=True,
        )


def _use_stub_embedder() -> bool:
    """Tests may set CONTEXTOS_EMBEDDING_STUB=1; production default False."""
    import os

    return os.environ.get("CONTEXTOS_EMBEDDING_STUB", "").lower() in {"1", "true", "yes"}


# Expose ValidationError mapping via FastAPI request validation;
# /context maps to Proposed 400 via main.py exception handler (OQ-HTTP-/context).
