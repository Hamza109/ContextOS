"""POST /index router — Confirmed contract + Proposed optional scope (OQ-14)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas_index import IndexRequest, IndexResponse
from app.services.l5_index import IndexInProgressError, InvalidRepoError, run_index

router = APIRouter(tags=["index"])


@router.post(
    "/index",
    response_model=IndexResponse,
    summary="Index a repository (L5 content + L1 structural graph)",
    description=(
        "Confirmed: request {repo_path, repo_name} → "
        "{files_indexed, graph_nodes, embeddings, time_ms}. "
        "Optional paths/files are Proposed (OQ-14) only. "
        "HTTP status codes are Proposed (OQ-HTTP unresolved). "
        "graph_nodes is the distinct L1 node count persisted for this request."
    ),
    responses={
        400: {"description": "Proposed: invalid/unreadable repo_path or empty repo_name (OQ-HTTP)"},
        409: {"description": "Proposed: index already in progress (OQ-HTTP)"},
        500: {"description": "Proposed: indexing failure (OQ-HTTP)"},
    },
)
def post_index(body: IndexRequest) -> IndexResponse:
    try:
        result = run_index(
            body.repo_path,
            body.repo_name,
            paths=body.paths,
            files=body.files,
        )
    except InvalidRepoError as exc:
        # Proposed 400 — not Confirmed (OQ-HTTP)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IndexInProgressError as exc:
        # Proposed 409 — not Confirmed (OQ-HTTP)
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"indexing failed: {exc}") from exc

    return IndexResponse(
        files_indexed=result.files_indexed,
        graph_nodes=result.graph_nodes,
        embeddings=result.embeddings,
        time_ms=result.time_ms,
    )
