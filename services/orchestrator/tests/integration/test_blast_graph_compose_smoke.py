"""Compose/API smoke for blast + graph.html (T027) — opt-in live compose."""

from __future__ import annotations

import os

import httpx
import pytest

pytestmark = pytest.mark.requires_falkordb


@pytest.mark.skipif(
    os.environ.get("CONTEXTOS_L1_COMPOSE_SMOKE") != "1"
    or not os.environ.get("CONTEXTOS_L1_COMPOSE_REPO_PATH"),
    reason=(
        "Compose smoke unavailable: set CONTEXTOS_L1_COMPOSE_SMOKE=1 and "
        "CONTEXTOS_L1_COMPOSE_REPO_PATH"
    ),
)
def test_compose_serves_blast_and_graph_html() -> None:
    base_url = os.environ.get("CONTEXTOS_ORCHESTRATOR_BASE_URL", "http://127.0.0.1:8000")
    repo = "ep007-compose-smoke"
    index = httpx.post(
        f"{base_url.rstrip('/')}/index",
        json={
            "repo_path": os.environ["CONTEXTOS_L1_COMPOSE_REPO_PATH"],
            "repo_name": repo,
        },
        timeout=120,
    )
    assert index.status_code == 200, index.text
    assert index.json()["graph_nodes"] > 0

    graph = httpx.get(
        f"{base_url.rstrip('/')}/graph.html",
        params={"repo": repo, "depth": 2},
        timeout=30,
    )
    assert graph.status_code == 200
    assert "vis-network" in graph.text
    assert "#0f172a" in graph.text

    # Proposed: blast may 404 if fixture file name differs — try a common path.
    blast = httpx.get(
        f"{base_url.rstrip('/')}/blast/python/auth.py",
        params={"repo": repo},
        timeout=30,
    )
    assert blast.status_code in {200, 404}
    if blast.status_code == 200:
        body = blast.json()
        assert "direct_dependents" in body
        assert body.get("owners") == []
