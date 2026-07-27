"""POST /context router — Confirmed contract + Proposed extensions (EP-002 + EP-003 L3).

Security: reuse ignore_policy / consent_gate inheritance from EP-001 packs/index.
Do NOT re-read excluded paths from disk to “help” packing (FR-018).
RBAC hook reserved — OQ-01 Missing Evidence (do not invent roles).

EP-003 Proposed: optional Serena-informed safe edit plan appended inside Confirmed
``final_context`` string only (OQ-Safe-Edit-Shape) — no new Appendix D response fields.
No Confirmed L3 symbol REST (OQ-Symbol-REST; MCP-first Option A).
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, HTTPException

from app.adapters.embeddings import get_embedder
from app.adapters.qdrant_store import QdrantStore
from app.adapters.serena_mcp import InMemorySerenaDouble, SerenaMCPAdapter, SerenaMCPConfig
from app.api.schemas_context import ContextMetrics, ContextRequest, ContextResponse
from app.config import get_settings
from app.services.l3_symbol import SymbolService, attach_safe_edit_plan
from app.services.l5_phase_pack import DEFAULT_PHASE, pack_for_phase
from app.services.l5_pack import load_pack_by_repo
from app.services.l5_search import hits_to_relevant_files, hybrid_search
from app.telemetry.context import child_span, context_span, record_duration_ms
from app.telemetry.symbol import symbol_span

logger = logging.getLogger(__name__)

router = APIRouter(tags=["context"])


@router.post(
    "/context",
    response_model=ContextResponse,
    summary="Retrieve hybrid-search packed context (L5) + optional L3 safe-edit enrichment",
    description=(
        "Confirmed request: query, file (optional), repo, top_k. "
        "Confirmed response: final_context, metrics "
        "(tokens_before, tokens_after, saving_percent, trace), "
        "blast_radius, memory, relevant_files, is_real. "
        "Proposed (OQ-16): optional phase — NOT Appendix D Confirmed; default Dev. "
        "Proposed relevant_files item keys (path/score/...). "
        "Citations: file:line + confidence attributes inside final_context "
        "(OQ-11 open — Proposed XML interim). "
        "Proposed (EP-003): Serena-informed safe edit plan may be appended as a "
        "delimited block inside final_context (OQ-Safe-Edit-Shape open) — "
        "NOT a new Confirmed response field; NOT Confirmed symbol REST. "
        "HTTP status codes Proposed only (OQ-HTTP-/context). "
        "FR-019 consumer note: future contextos ask / extension Ask SHOULD call this API; "
        "full Ask <3 clicks / CLI remain EP-004 (EP-003 delivers Pack Context surface only). "
        "No L4 Headroom gate (ADR-006). No L1 blast expand."
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

        final_context = packed.final_context
        safe_edit_attached = False
        if settings.context_safe_edit_enrichment:
            final_context, safe_edit_attached = _maybe_attach_safe_edit(
                final_context,
                body=body,
                settings=settings,
            )

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
            # Proposed EP-003 trace note only — not a Confirmed Appendix D field
            "l3_safe_edit_enrichment": safe_edit_attached,
        }
        record_duration_ms(span, "duration_ms", float(trace["duration_ms"]))

        return ContextResponse(
            final_context=final_context,
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


def _maybe_attach_safe_edit(
    final_context: str,
    *,
    body: ContextRequest,
    settings: Any,
) -> tuple[str, bool]:
    """Proposed Serena enrichment — content only in final_context (no new response keys)."""
    with symbol_span(
        "symbol.pack_context.composition",
        attributes={"repo": body.repo, "file": body.file or ""},
    ):
        try:
            adapter = _serena_adapter_for_settings(settings)
            service = SymbolService(adapter=adapter, settings=settings)
            # Derive symbol signals from Confirmed request fields only (query/file).
            # No invented Confirmed request keys for line/column (OQ-Safe-Edit-Shape).
            plan = service.compose_safe_edit_plan(
                path=body.file,
                line=1 if body.file else None,
                symbol=None,
                query=body.query,
            )
            if plan is None:
                return final_context, False
            return attach_safe_edit_plan(final_context, plan), True
        except Exception as exc:  # noqa: BLE001
            # OQ-MCP-Fallback: clear log; do not fail Confirmed packing path
            logger.warning(
                "Proposed L3 safe-edit enrichment skipped (Serena unavailable/error): %s",
                exc,
            )
            return final_context, False


def _serena_adapter_for_settings(settings: Any) -> SerenaMCPAdapter:
    cfg = SerenaMCPConfig(
        enabled=settings.serena_enabled,
        command=settings.serena_command,
        args=[a for a in (settings.serena_args or "").split() if a],
        cwd=settings.serena_cwd,
        timeout_seconds=settings.serena_timeout_seconds,
        use_test_double=settings.serena_use_test_double or not settings.serena_command,
    )
    if cfg.use_test_double or not cfg.command:
        # Default enrichment path uses double until live Serena command configured
        return SerenaMCPAdapter(cfg, session=InMemorySerenaDouble())
    return SerenaMCPAdapter(cfg)


def _use_stub_embedder() -> bool:
    """Tests may set CONTEXTOS_EMBEDDING_STUB=1; production default False."""
    import os

    return os.environ.get("CONTEXTOS_EMBEDDING_STUB", "").lower() in {"1", "true", "yes"}


# Expose ValidationError mapping via FastAPI request validation;
# /context maps to Proposed 400 via main.py exception handler (OQ-HTTP-/context).
