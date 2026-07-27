"""ContextOS FastAPI orchestrator entrypoint (EP-001 + EP-002 L5)."""

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
    version="0.2.0",
    description=(
        "EP-001 L5 Repository Packing & Indexing + EP-002 Hybrid Search & Phase Packing. "
        "Confirmed POST /index and POST /context fields only; "
        "Proposed extensions (phase OQ-16, citation interim OQ-11, status codes) labeled. "
        "Local embeddings only on index path; no external LLM exfil. "
        "Out of scope: Serena/L3, L1 blast, L4 Headroom product, L2/L6, CLI epic, extension DX."
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
