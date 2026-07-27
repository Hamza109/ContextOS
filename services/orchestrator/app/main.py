"""ContextOS FastAPI orchestrator entrypoint (EP-001 + EP-002 L5 + EP-003 L3 enrichment)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.context import router as context_router
from app.api.health import router as health_router
from app.api.index import router as index_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Placeholder lifespan — model warm-up optional; avoid blocking cold start hard.
    settings = get_settings()
    settings.pack_cache_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="ContextOS Orchestrator",
    version="0.3.0",
    description=(
        "EP-001 L5 Repository Packing & Indexing + EP-002 Hybrid Search & Phase Packing "
        "+ EP-003 L3 Symbol (Serena) Pack Context enrichment. "
        "Confirmed Appendix D HTTP only: GET /, POST /index, POST /context "
        "(+ health). No Confirmed L3 symbol REST (api-contract §3; MCP-first Option A; "
        "OQ-Symbol-REST open). "
        "Proposed: Serena MCP knobs; safe-edit delimited block inside final_context "
        "(OQ-Safe-Edit-Shape); citation XML attributes (OQ-11). "
        "Local embeddings only on index path; no external LLM exfil. "
        "Out of scope: Confirmed symbol REST, L1 blast, L4 Headroom product, L2/L6, "
        "rename execution sandbox, full EP-004 CLI/Ask, JetBrains, extension DX."
    ),
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def _proposed_validation_handler(request: Request, exc: RequestValidationError):
    """Map validation failures on /context to Proposed 400 (OQ-HTTP-/context — not Confirmed)."""
    # Sanitize errors — Pydantic ctx may contain non-JSON ValueError instances
    detail = []
    for err in exc.errors():
        clean = {k: v for k, v in err.items() if k != "ctx"}
        if "ctx" in err and err["ctx"]:
            clean["ctx"] = {ck: str(cv) for ck, cv in err["ctx"].items()}
        detail.append(clean)
    if request.url.path.rstrip("/").endswith("/context"):
        return JSONResponse(
            status_code=400,
            content={"detail": detail, "proposed_status": "400"},
        )
    return JSONResponse(status_code=422, content={"detail": detail})


app.include_router(health_router)
app.include_router(index_router)
app.include_router(context_router)
