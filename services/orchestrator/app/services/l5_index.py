"""FastAPI index orchestration: shared policy → L5 index + L1 graph."""

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
from app.services.l1_graph import L1GraphService
from app.services.l5_chunk import Chunk, chunk_file
from app.services.l5_pack import PackResult, pack_repository
from app.services.l1_entity_cache import get_l1_entity_cache
from app.services.okf_generate import generate_okf_bundle
from app.telemetry.indexing import (
    index_span,
    record_index_counts,
    record_l1_attributes,
    record_okf_attributes,
    record_pack_attributes,
)

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
    graph_service: L1GraphService | None = None,
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

            policy = IgnorePolicy.from_repo(root)
            all_allowed = walk_allowed_files(root, policy)
            allowed = all_allowed
            if scope:
                wanted = set(scope)
                allowed = [
                    p for p in all_allowed if p.relative_to(root).as_posix() in wanted
                ]

            l1 = graph_service or L1GraphService(cfg)
            l1_result = l1.generate(
                repo_name,
                root,
                all_allowed,
                affected_paths=scope if mode == "incremental" else None,
            )
            record_l1_attributes(
                span,
                parse_ms=l1_result.parse_ms,
                persist_ms=l1_result.persist_ms,
                parsed_files=l1_result.parsed_files,
                graph_nodes=l1_result.graph_nodes,
                unsupported_files=l1_result.unsupported_files,
                malformed_files=l1_result.malformed_files,
            )

            # EP-013 Proposed: OKF generate after eligibility + L1; failures must not
            # invent Confirmed HTTP semantics or break L5/L1 outcomes.
            l1_entities = get_l1_entity_cache().lookup(
                repo_name, [], limit=40
            ).entities
            okf_result = generate_okf_bundle(
                root,
                repo_name,
                settings=cfg,
                policy=policy,
                allowed_paths=all_allowed,
                index_revision=l1_result.index_revision,
                l1_entities=l1_entities,
            )
            record_okf_attributes(
                span,
                status=okf_result.status,
                concepts_written=okf_result.concepts_written,
                sources_used=okf_result.sources_used,
                duration_ms=okf_result.duration_ms,
            )

            all_chunks: list[Chunk] = []
            hashes: list[str] = []
            for path in allowed:
                file_chunks = chunk_file(path, repo_name=repo_name, root=root)
                for ch in file_chunks:
                    all_chunks.append(ch)
                    hashes.append(content_hash(ch.content))  # Proposed content_hash

            embeddings_count = 0
            if all_chunks and not skip_embed:
                emb = embedder or get_embedder(cfg)
                qdrant = store or QdrantStore(cfg)
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
                graph_nodes=l1_result.graph_nodes,
                embeddings=embeddings_count,
                time_ms=elapsed_ms,
                pack=pack,
                mode=mode,
            )
            record_index_counts(
                span,
                files_indexed=result.files_indexed,
                embeddings=result.embeddings,
                graph_nodes=result.graph_nodes,
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
