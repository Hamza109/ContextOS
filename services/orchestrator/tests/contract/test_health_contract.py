"""GET / health contract tests (EP-005 T021–T022 / FR-006, FR-007, SC-004, SC-005).

Confirmed fields: status (ok|degraded|error), pipeline, falkor, qdrant.
HTTP status codes remain Proposed only (OQ-HTTP-Health) — MUST NOT Confirmed-freeze.
OQ-Uptime-Harness blocks SC-007 Pass — tracking only; no Pass claim here (T006 / T029).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

CONFIRMED_STATUS_VALUES = frozenset({"ok", "degraded", "error"})
CONFIRMED_FIELDS = ("status", "pipeline", "falkor", "qdrant")


def test_health_confirmed_fields_present() -> None:
    """SC-004 / FR-006: Confirmed body fields from api-contract §2.1."""
    client = TestClient(app)
    resp = client.get("/")
    # Proposed HTTP mapping (OQ-HTTP-Health): current implementation returns 200
    # for healthy/degraded body; do NOT Confirmed-freeze 200 vs 503 here.
    assert resp.status_code in {200, 503}  # Proposed set only
    data: dict[str, Any] = resp.json()
    for field in CONFIRMED_FIELDS:
        assert field in data, f"missing Confirmed health field: {field}"
    assert data["status"] in CONFIRMED_STATUS_VALUES
    assert isinstance(data["pipeline"], str) and data["pipeline"]
    assert isinstance(data["falkor"], str) and data["falkor"]
    assert isinstance(data["qdrant"], str) and data["qdrant"]


def test_health_a07_falkor_unused_does_not_force_error() -> None:
    """A-07 / FR-007 / SC-005: Falkor unused/absent alone must not force status=error.

    When Qdrant reports ok, overall status stays ok even if falkor is unused.
    """
    client = TestClient(app)
    with patch("app.api.health.QdrantStore") as store_cls:
        store_cls.return_value.health.return_value = "ok"
        resp = client.get("/")
    # Proposed HTTP (OQ-HTTP-Health) — observe without freezing
    assert resp.status_code in {200, 503}
    data = resp.json()
    assert data["falkor"] == "unused"
    assert data["qdrant"] == "ok"
    assert data["status"] == "ok"
    assert data["status"] != "error"
    assert "pipeline" in data and data["pipeline"]


def test_health_qdrant_down_degrades_not_falkor_driven() -> None:
    """When Qdrant is unavailable, status reflects Qdrant/pipeline — not Falkor alone."""
    client = TestClient(app)
    with patch("app.api.health.QdrantStore") as store_cls:
        store_cls.return_value.health.return_value = "error"
        resp = client.get("/")
    assert resp.status_code in {200, 503}  # Proposed (OQ-HTTP-Health)
    data = resp.json()
    assert data["falkor"] == "unused"
    assert data["qdrant"] == "error"
    assert data["status"] == "degraded"
    # MVP search readiness is not failed solely by Falkor absence
    assert data["status"] != "error"


def test_sc007_uptime_harness_not_claimed() -> None:
    """T029: OQ-Uptime-Harness blocks SC-007 Pass — document skip only."""
    # No harness wired; this test exists so CI cannot silently claim SC-007 Pass.
    assert True, "SC-007 Pass skipped — OQ-Uptime-Harness open (tracking only)"
