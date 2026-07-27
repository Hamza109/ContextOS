"""Unit tests for POST /context request validation (T024) — Proposed 400."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_empty_query_returns_proposed_400() -> None:
    resp = client.post(
        "/context",
        json={"query": "  ", "repo": "demo", "top_k": 5},
    )
    assert resp.status_code == 400


def test_missing_query_returns_proposed_400() -> None:
    resp = client.post(
        "/context",
        json={"repo": "demo", "top_k": 5},
    )
    assert resp.status_code == 400


def test_non_positive_top_k_returns_proposed_400() -> None:
    resp = client.post(
        "/context",
        json={"query": "where is auth", "repo": "demo", "top_k": 0},
    )
    assert resp.status_code == 400


def test_negative_top_k_returns_proposed_400() -> None:
    resp = client.post(
        "/context",
        json={"query": "where is auth", "repo": "demo", "top_k": -1},
    )
    assert resp.status_code == 400


def test_invalid_phase_returns_proposed_400() -> None:
    resp = client.post(
        "/context",
        json={"query": "where is auth", "repo": "demo", "top_k": 3, "phase": "Nope"},
    )
    assert resp.status_code == 400


def test_repo_path_traversal_returns_proposed_400() -> None:
    """T063: reject path-traversal characters in repo (Proposed 400)."""
    resp = client.post(
        "/context",
        json={"query": "where is auth", "repo": "../etc", "top_k": 3},
    )
    assert resp.status_code == 400


def test_file_path_traversal_returns_proposed_400() -> None:
    """T063: reject path-traversal characters in optional file (Proposed 400)."""
    resp = client.post(
        "/context",
        json={
            "query": "where is auth",
            "repo": "demo",
            "file": "../../.env",
            "top_k": 3,
        },
    )
    assert resp.status_code == 400
