"""L5 index orchestration: walk → filter → pack → chunk → embed → upsert.

graph_nodes MUST be 0 for EP-001 MVP (no L1 writes).
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from app.adapters.embeddings import EmbeddingBackend, get_embedder
from app.adapters.fs_walker import walk_allowed_files
from app.adapters.qdrant_store import QdrantStore, content_hash
from app.config import Settings, get_settings
from app.security.consent_gate import index_path_may_call_external_llm
from app.security.ignore_policy import IgnorePolicy
from app.services.l5_chunk import Chunk, chunk_file
from app.services.l5_pack import PackResult, pack_repository
from app.telemetry.indexing import index_span, record_index_counts, record_pack_attributes

logger = logging.getLogger(__name__)

# Proposed single-flight guard (OQ-HTTP — 409 not Confirmed)
_index_lock = threading.Lock()
_active_repos: set[str] = set()


class IndexInProgressError(RuntimeError):
    """Proposed concurrent-index conflict (maps to Proposed HTTP 409)."""


class InvalidRepoError(ValueError):
    """Proposed validation failure (maps to Proposed HTTP 400)."""


@dataclass(frozen=True)
class IndexResult:
    files_indexed: int
    graph_nodes: int
    embeddings: int
    time_ms: int
    pack: PackResult | None = None
    mode: str = "full"


def run_index(
    repo_path: str,
    repo_name: str,
    *,
    paths: list[str] | None = None,
    files: list[str] | None = None,
    settings: Settings | None = None,
    embedder: EmbeddingBackend | None = None,
    store: QdrantStore | None = None,
    skip_embed: bool = False,
) -> IndexResult:
    """Full or Proposed incremental index. Never calls external LLM."""
    if index_path_may_call_external_llm():
        raise RuntimeError("Invariant violated: index path must not call external LLM")

    cfg = settings or get_settings()
    root = Path(repo_path).expanduser().resolve()
    if not repo_name or not str(repo_name).strip():
        raise InvalidRepoError("repo_name must be a non-empty string")
    if not root.is_dir():
        raise InvalidRepoError(f"repo_path is not a readable directory: {repo_path}")

    # Proposed narrower scope (OQ-14) — optional paths/files
    scope = _merge_scope(paths, files)
    mode = "incremental" if scope else "full"

    if not _index_lock.acquire(blocking=False):
        raise IndexInProgressError("another index operation is in progress")
    try:
        if repo_name in _active_repos:
            raise IndexInProgressError(f"index already in progress for repo_name={repo_name}")
        _active_repos.add(repo_name)
    except IndexInProgressError:
        _index_lock.release()
        raise

    started = time.perf_counter()
    try:
        with index_span("index.repository", repo_name=repo_name, mode=mode) as span:
            pack = pack_repository(root, repo_name, settings=cfg, paths_filter=scope)
            record_pack_attributes(
                span,
                token_count=pack.token_count,
                files_packed=pack.files_packed,
                exclusions=pack.files_excluded,
            )

            if skip_embed:
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                result = IndexResult(
                    files_indexed=pack.files_packed,
                    graph_nodes=0,
                    embeddings=0,
                    time_ms=elapsed_ms,
                    pack=pack,
                    mode=mode,
                )
                record_index_counts(
                    span,
                    files_indexed=result.files_indexed,
                    embeddings=result.embeddings,
                    graph_nodes=0,
                    time_ms=result.time_ms,
                    exclusions=pack.files_excluded,
                )
                return result

            policy = IgnorePolicy.from_repo(root)
            allowed = walk_allowed_files(root, policy)
            if scope:
                wanted = set(scope)
                allowed = [p for p in allowed if p.relative_to(root).as_posix() in wanted]

            all_chunks: list[Chunk] = []
            hashes: list[str] = []
            for path in allowed:
                file_chunks = chunk_file(path, repo_name=repo_name, root=root)
                for ch in file_chunks:
                    all_chunks.append(ch)
                    hashes.append(content_hash(ch.content))  # Proposed content_hash

            emb = embedder or get_embedder(cfg)
            qdrant = store or QdrantStore(cfg)

            embeddings_count = 0
            if all_chunks:
                texts = [c.content for c in all_chunks]
                vectors = emb.embed(texts)
                # Defense: ensure no accidental HTTP LLM in embedder type
                if hasattr(emb, "model_name"):
                    name = str(getattr(emb, "model_name", "")).lower()
                    if name.startswith("http"):
                        raise RuntimeError("External embedding URL refused on index path")

                if mode == "incremental":
                    embeddings_count = qdrant.upsert_file_chunks(
                        all_chunks, vectors, content_hashes=hashes
                    )
                else:
                    # Full re-index: replace per-file scopes for consistency
                    embeddings_count = qdrant.upsert_file_chunks(
                        all_chunks, vectors, content_hashes=hashes
                    )

            elapsed_ms = int((time.perf_counter() - started) * 1000)
            # Observational single-file timing note (NFR-003) — logged, not SLA
            if mode == "incremental" and scope and len(scope) == 1:
                logger.info(
                    "observational single-file re-index time_ms=%s repo=%s file=%s "
                    "(NFR-003 ~0.5s illustrative)",
                    elapsed_ms,
                    repo_name,
                    scope[0],
                )

            result = IndexResult(
                files_indexed=len(allowed),
                graph_nodes=0,  # MVP: no L1 writes
                embeddings=embeddings_count,
                time_ms=elapsed_ms,
                pack=pack,
                mode=mode,
            )
            record_index_counts(
                span,
                files_indexed=result.files_indexed,
                embeddings=result.embeddings,
                graph_nodes=0,
                time_ms=result.time_ms,
                exclusions=pack.files_excluded,
            )
            return result
    finally:
        _active_repos.discard(repo_name)
        _index_lock.release()


def _merge_scope(paths: list[str] | None, files: list[str] | None) -> list[str] | None:
    merged: list[str] = []
    if paths:
        merged.extend(paths)
    if files:
        merged.extend(files)
    if not merged:
        return None
    # Normalize to posix relative-ish strings
    return [p.replace("\\", "/").lstrip("./") for p in merged]
