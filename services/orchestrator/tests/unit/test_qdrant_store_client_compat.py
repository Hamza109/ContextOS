"""Compatibility coverage for Qdrant client search API changes."""

from __future__ import annotations

from types import SimpleNamespace

from app.adapters.qdrant_store import QdrantStore
from app.config import Settings


def test_query_points_uses_modern_client_api() -> None:
    point = SimpleNamespace(
        id="id-1",
        score=0.9,
        payload={
            "repo_name": "demo",
            "file_path": "src/auth.py",
            "content": "def login(): pass",
            "token_count": 5,
            "chunk_index": 0,
        },
    )

    class ModernClient:
        def query_points(self, **kwargs):
            assert kwargs["query"] == [0.1, 0.2]
            assert kwargs["collection_name"] == "codebase"
            return SimpleNamespace(points=[point])

    settings = Settings(embedding_dim=2)
    store = QdrantStore(settings=settings, client=ModernClient())
    store.ensure_collection = lambda: None  # type: ignore[method-assign]
    store.ensure_payload_indexes = lambda: None  # type: ignore[method-assign]

    rows = store.search([0.1, 0.2], repo_name="demo", limit=3)

    assert rows == [
        {
            "id": "id-1",
            "score": 0.9,
            "repo_name": "demo",
            "file_path": "src/auth.py",
            "content": "def login(): pass",
            "token_count": 5,
            "chunk_index": 0,
        }
    ]


def test_query_points_retains_legacy_search_client_api() -> None:
    point = SimpleNamespace(
        id="id-2",
        score=0.5,
        payload={
            "repo_name": "demo",
            "file_path": "src/legacy.py",
            "content": "legacy",
            "token_count": 1,
            "chunk_index": 0,
        },
    )

    class LegacyClient:
        def search(self, **kwargs):
            assert kwargs["query_vector"] == [0.1, 0.2]
            return [point]

    settings = Settings(embedding_dim=2)
    store = QdrantStore(settings=settings, client=LegacyClient())
    store.ensure_collection = lambda: None  # type: ignore[method-assign]
    store.ensure_payload_indexes = lambda: None  # type: ignore[method-assign]

    assert store.search([0.1, 0.2], repo_name="demo", limit=3)[0]["id"] == "id-2"
