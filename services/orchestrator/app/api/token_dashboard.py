"""GET /contextos_token_dashboard.html — Proposed EP-008 token cost dashboard (OQ-08).

Serving choice labeled **Proposed** (sibling of graph.html pattern). Auth Missing Evidence —
local trusted draft only. No Confirmed GET /metrics.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.telemetry.compression import get_last_compression_event

router = APIRouter(tags=["telemetry"])

_STATIC = Path(__file__).resolve().parent.parent / "static" / "contextos_token_dashboard.html"


@router.get(
    "/contextos_token_dashboard.html",
    response_class=HTMLResponse,
    summary="Minimal L4 token cost dashboard (Proposed)",
    description=(
        "Proposed EP-008 artifact (FR-09 / US-024). Shows before/after token cost from "
        "the last L4 compress event when available, else a static demo fixture. "
        "Serving mechanism [NEEDS CLARIFICATION: OQ-08]. Auth Missing Evidence — "
        "local trusted draft only. Not Confirmed GET /metrics."
    ),
    responses={
        200: {"description": "Proposed: text/html success"},
    },
)
def get_token_dashboard() -> HTMLResponse:
    event = get_last_compression_event()
    if event is None:
        # Static demo fixture when no L4 run yet
        tokens_before, tokens_after = 85000, 7200
        saving = round((tokens_before - tokens_after) / tokens_before * 100.0, 2)
        source = "demo_fixture"
        phase = "Design"
        budget_status = "n/a"
        repo = "(demo)"
    else:
        tokens_before = event.tokens_before
        tokens_after = event.tokens_after
        saving = event.saving_percent
        source = "last_l4_event"
        phase = event.phase or "—"
        budget_status = event.budget_status or "—"
        repo = event.repo or "—"

    template = _STATIC.read_text(encoding="utf-8") if _STATIC.is_file() else _FALLBACK_HTML
    html = (
        template.replace("{{TOKENS_BEFORE}}", str(tokens_before))
        .replace("{{TOKENS_AFTER}}", str(tokens_after))
        .replace("{{SAVING_PERCENT}}", f"{saving}")
        .replace("{{SOURCE}}", escape(source))
        .replace("{{PHASE}}", escape(str(phase)))
        .replace("{{BUDGET_STATUS}}", escape(str(budget_status)))
        .replace("{{REPO}}", escape(str(repo)))
    )
    return HTMLResponse(content=html)


_FALLBACK_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"/><title>ContextOS Token Dashboard</title></head>
<body>
  <h1>ContextOS Token Dashboard</h1>
  <p>Before: {{TOKENS_BEFORE}} · After: {{TOKENS_AFTER}} · Saving: {{SAVING_PERCENT}}%</p>
  <p>Source: {{SOURCE}} · Phase: {{PHASE}} · Budget: {{BUDGET_STATUS}} · Repo: {{REPO}}</p>
</body>
</html>
"""
