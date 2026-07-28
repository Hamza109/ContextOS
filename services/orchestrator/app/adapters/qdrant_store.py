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

    def ensure_payload_indexes(self) -> None:
        """Proposed payload index on repo_name (and file_path) for filtered search latency."""
        from qdrant_client.http import models as qm

        self.ensure_collection()
        client = self._get_client()
        name = self.settings.qdrant_collection
        for field in ("repo_name", "file_path"):
            try:
                client.create_payload_index(
                    collection_name=name,
                    field_name=field,
                    field_schema=qm.PayloadSchemaType.KEYWORD,
                )
            except Exception as exc:  # noqa: BLE001
                # Index may already exist — ignore
                logger.debug("payload index %s: %s", field, exc)

    def search(
        self,
        query_vector: list[float],
        *,
        repo_name: str,
        limit: int = 20,
        file_path: str | None = None,
    ) -> list[dict[str, Any]]:
        """Filtered vector search by repo_name; optional file_path bias (Proposed)."""
        from qdrant_client.http import models as qm

        if len(query_vector) != self.settings.embedding_dim:
            raise ValueError(
                f"query vector dim {len(query_vector)} != {self.settings.embedding_dim}"
            )
        self.ensure_collection()
        self.ensure_payload_indexes()
        client = self._get_client()

        must: list[qm.FieldCondition] = [
            qm.FieldCondition(key="repo_name", match=qm.MatchValue(value=repo_name)),
        ]
        if file_path:
            # Proposed soft bias: prefer exact file when provided; still allow repo-wide
            # by running exact-file filter first, then falling back to repo-wide.
            try:
                exact = self._query_points(
                    client,
                    query_vector=query_vector,
                    query_filter=qm.Filter(
                        must=must
                        + [
                            qm.FieldCondition(
                                key="file_path", match=qm.MatchValue(value=file_path)
                            )
                        ]
                    ),
                    limit=max(1, min(limit, 10)),
                )
            except Exception:  # noqa: BLE001
                exact = []
        else:
            exact = []

        results = self._query_points(
            client,
            query_vector=query_vector,
            query_filter=qm.Filter(must=must),
            limit=limit,
        )

        # Merge exact-file hits first (Proposed bias), then repo-wide
        merged: list[Any] = list(exact) + [r for r in results if r not in exact]
        out: list[dict[str, Any]] = []
        seen: set[str] = set()
        for r in merged:
            payload = r.payload or {}
            key = f"{payload.get('file_path')}:{payload.get('chunk_index')}"
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "id": str(r.id),
                    "score": float(r.score or 0.0),
                    "repo_name": payload.get("repo_name"),
                    "file_path": payload.get("file_path"),
                    "content": payload.get("content"),
                    "token_count": payload.get("token_count"),
                    "chunk_index": payload.get("chunk_index"),
                }
            )
            if len(out) >= limit:
                break
        return out

    def _query_points(
        self,
        client: Any,
        *,
        query_vector: list[float],
        query_filter: Any,
        limit: int,
    ) -> list[Any]:
        """Query points across supported qdrant-client API versions.

        `search()` was removed from current qdrant-client releases in favor of
        `query_points()`. Keep the older call for the project's declared
        >=1.12 compatibility, and normalize the newer QueryResponse to points.
        """
        kwargs = {
            "collection_name": self.settings.qdrant_collection,
            "query_filter": query_filter,
            "limit": limit,
            "with_payload": True,
        }
        search = getattr(client, "search", None)
        if callable(search):
            return list(search(query_vector=query_vector, **kwargs))

        query_points = getattr(client, "query_points", None)
        if not callable(query_points):
            raise AttributeError("Qdrant client has neither search() nor query_points()")
        response = query_points(query=query_vector, **kwargs)
        return list(response.points)

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
