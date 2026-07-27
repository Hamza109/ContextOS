"""ContextOS FastAPI orchestrator entrypoint (EP-001 L5 packing & indexing)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

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
    version="0.1.0",
    description=(
        "EP-001 L5 Repository Packing & Indexing. "
        "Confirmed POST /index fields only; OQ-14 Proposed optional scope labeled. "
        "Local embeddings only on index path; no external LLM exfil."
    ),
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(index_router)
