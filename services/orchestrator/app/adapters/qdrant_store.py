"""Qdrant adapter for collection `codebase` (384-dim) — FR-008."""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.config import Settings, get_settings
from app.services.l5_chunk import Chunk

logger = logging.getLogger(__name__)


class QdrantStore:
    def __init__(self, settings: Settings | None = None, client: Any | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = client

    def _get_client(self):
        if self._client is not None:
            return self._client
        from qdrant_client import QdrantClient

        self._client = QdrantClient(url=self.settings.qdrant_url)
        return self._client

    def ensure_collection(self) -> None:
        from qdrant_client.http import models as qm

        client = self._get_client()
        name = self.settings.qdrant_collection
        dim = self.settings.embedding_dim
        existing = {c.name for c in client.get_collections().collections}
        if name in existing:
            return
        client.create_collection(
            collection_name=name,
            vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
        )
        logger.info("Created Qdrant collection %s (%s-dim)", name, dim)

    def delete_by_file(self, repo_name: str, file_path: str) -> None:
        """Delete/replace scope: remove existing points for repo_name + file_path."""
        from qdrant_client.http import models as qm

        self.ensure_collection()
        client = self._get_client()
        client.delete(
            collection_name=self.settings.qdrant_collection,
            points_selector=qm.FilterSelector(
                filter=qm.Filter(
                    must=[
                        qm.FieldCondition(key="repo_name", match=qm.MatchValue(value=repo_name)),
                        qm.FieldCondition(key="file_path", match=qm.MatchValue(value=file_path)),
                    ]
                )
            ),
        )

    def upsert_chunks(
        self,
        chunks: list[Chunk],
        vectors: list[list[float]],
        *,
        content_hashes: list[str] | None = None,
    ) -> int:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors length mismatch")
        if not chunks:
            return 0

        from qdrant_client.http import models as qm

        self.ensure_collection()
        client = self._get_client()
        now = datetime.now(UTC).isoformat()
        points: list[qm.PointStruct] = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
            if len(vector) != self.settings.embedding_dim:
                raise ValueError(f"vector dim {len(vector)} != {self.settings.embedding_dim}")
            point_id = _point_id(chunk.repo_name, chunk.file_path, chunk.chunk_index)
            payload: dict[str, Any] = {
                "repo_name": chunk.repo_name,
                "file_path": chunk.file_path,
                "content": chunk.content,
                "token_count": chunk.token_count,
                "indexed_at": now,
                "chunk_index": chunk.chunk_index,
            }
            if content_hashes is not None:
                # Proposed optional content_hash for delta skip (database-schema §2)
                payload["content_hash"] = content_hashes[i]
            points.append(qm.PointStruct(id=point_id, vector=vector, payload=payload))

        client.upsert(collection_name=self.settings.qdrant_collection, points=points)
        return len(points)

    def upsert_file_chunks(
        self,
        chunks: list[Chunk],
        vectors: list[list[float]],
        *,
        content_hashes: list[str] | None = None,
    ) -> int:
        """Delete existing vectors for the file scope then upsert (US-012 delta)."""
        if not chunks:
            return 0
        self.ensure_collection()
        # All chunks for a call should share file_path when replacing one file;
        # for multi-file batches, group by file_path.
        by_file: dict[tuple[str, str], list[int]] = {}
        for i, c in enumerate(chunks):
            by_file.setdefault((c.repo_name, c.file_path), []).append(i)

        total = 0
        for (repo_name, file_path), idxs in by_file.items():
            self.delete_by_file(repo_name, file_path)
            sub_chunks = [chunks[i] for i in idxs]
            sub_vecs = [vectors[i] for i in idxs]
            sub_hashes = [content_hashes[i] for i in idxs] if content_hashes else None
            total += self.upsert_chunks(sub_chunks, sub_vecs, content_hashes=sub_hashes)
        return total

    def health(self) -> str:
        try:
            client = self._get_client()
            client.get_collections()
            return "ok"
        except Exception as exc:  # noqa: BLE001
            logger.warning("Qdrant health check failed: %s", exc)
            return "error"


def content_hash(text: str) -> str:
    """Proposed optional hash for unchanged-file skip."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _point_id(repo_name: str, file_path: str, chunk_index: int) -> str:
    raw = f"{repo_name}:{file_path}:{chunk_index}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))
