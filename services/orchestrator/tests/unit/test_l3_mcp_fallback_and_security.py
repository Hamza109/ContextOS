"""Security / polish: MCP unavailable clear error; ignore inheritance (T070, T072, T073)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.adapters.serena_mcp import (
    InMemorySerenaDouble,
    SerenaMCPAdapter,
    SerenaMCPConfig,
    SerenaUnavailableError,
)
from app.services.l3_symbol import SymbolService


def test_serena_unavailable_clear_error() -> None:
    session = InMemorySerenaDouble(available=False)
    adapter = SerenaMCPAdapter(SerenaMCPConfig(use_test_double=True), session=session)
    with pytest.raises(SerenaUnavailableError, match="unavailable"):
        adapter.find_definition(path="a.py", line=1, symbol="x")


def test_disabled_serena_raises_unavailable() -> None:
    adapter = SerenaMCPAdapter(SerenaMCPConfig(enabled=False, use_test_double=True))
    with pytest.raises(SerenaUnavailableError, match="disabled"):
        adapter.connect()


def test_symbol_service_blocks_env_path_read(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("SECRET=1\n", encoding="utf-8")
    svc = SymbolService(
        adapter=SerenaMCPAdapter(
            SerenaMCPConfig(use_test_double=True), session=InMemorySerenaDouble()
        ),
        workspace_root=tmp_path,
    )
    # Direct policy check
    with pytest.raises(PermissionError, match="excluded"):
        svc._check_path_allowed(".env")


def test_no_confirmed_symbol_rest_routes() -> None:
    """T021/T071: OpenAPI must not claim Appendix D L3 symbol endpoints."""
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    paths = set(client.get("/openapi.json").json()["paths"].keys())
    forbidden = {
        "/symbol",
        "/symbols",
        "/definition",
        "/references",
        "/rename",
        "/rename-scope",
        "/l3",
        "/serena",
    }
    assert paths.isdisjoint(forbidden)
    assert "/context" in paths
    assert "/index" in paths
