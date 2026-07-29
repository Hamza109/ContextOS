"""Shared pytest fixtures."""

from __future__ import annotations

import os

import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache(monkeypatch):
    # Unit/integration suites use the explicitly configured injectable L1 store.
    # Production defaults and Compose continue to require FalkorDB.
    if "CONTEXTOS_FALKORDB_URL" not in os.environ:
        monkeypatch.setenv("CONTEXTOS_FALKORDB_URL", "memory://ep006-tests")
    get_settings.cache_clear()
    from app.services.l1_entity_cache import get_l1_entity_cache

    get_l1_entity_cache.cache_clear()
    from app.adapters.falkordb_store import reset_memory_graph_store

    reset_memory_graph_store()
    yield
    get_l1_entity_cache.cache_clear()
    reset_memory_graph_store()
    get_settings.cache_clear()
