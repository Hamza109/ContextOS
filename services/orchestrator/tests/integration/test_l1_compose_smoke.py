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
        "CONTEXTOS_L1_COMPOSE_REPO_PATH to a fixture path mounted in API"
    ),
)
def test_compose_indexes_fixture_and_preserves_contracts() -> None:
    base_url = os.environ.get("CONTEXTOS_ORCHESTRATOR_BASE_URL", "http://127.0.0.1:8000")
    try:
        response = httpx.get(f"{base_url.rstrip('/')}/", timeout=5)
    except httpx.HTTPError as exc:
        pytest.fail(f"Compose smoke requested but API unavailable: {exc}")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"status", "pipeline", "falkor", "qdrant"}
    assert body["falkor"] == "ok"
    index = httpx.post(
        f"{base_url.rstrip('/')}/index",
        json={
            "repo_path": os.environ["CONTEXTOS_L1_COMPOSE_REPO_PATH"],
            "repo_name": "ep006-compose-smoke",
        },
        timeout=120,
    )
    assert index.status_code == 200, index.text
    result = index.json()
    assert set(result) == {"files_indexed", "graph_nodes", "embeddings", "time_ms"}
    assert result["files_indexed"] > 0
    assert result["graph_nodes"] > 0
