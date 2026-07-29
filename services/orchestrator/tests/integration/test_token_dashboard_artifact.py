"""Integration/smoke: token dashboard artifact (EP-008 T028). Serving Proposed (OQ-08)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.telemetry.compression import record_compression_attributes, reset_last_compression_event


def test_dashboard_static_file_exists() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "static"
        / "contextos_token_dashboard.html"
    )
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Tokens before" in text or "TOKENS_BEFORE" in text
    assert "Tokens after" in text or "TOKENS_AFTER" in text


def test_dashboard_route_renders_before_after() -> None:
    reset_last_compression_event()
    record_compression_attributes(
        None,
        tokens_before=1000,
        tokens_after=200,
        phase="Dev",
        repo="demo",
        budget_status="ok",
        enabled=True,
    )
    resp = TestClient(app).get("/contextos_token_dashboard.html")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert "1000" in resp.text
    assert "200" in resp.text
    assert "ContextOS" in resp.text
