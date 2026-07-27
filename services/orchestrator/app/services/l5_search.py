"""Hybrid BM25 + vector retrieval with MMR re-ranking (ADR-014 / US-003).

Fusion weights and MMR λ are **Proposed** tunables (not Confirmed).
"""

from __future__ import annotations

import logging
import math
import re
import time
from dataclasses import dataclass
from typing import Any

from app.adapters.bm25_store import Bm25Store, get_bm25_store
from app.adapters.embeddings import EmbeddingBackend, get_embedder
from app.adapters.qdrant_store import QdrantStore
from app.config import Settings, get_settings
from app.services.l5_pack import PackResult, estimate_tokens, load_pack_by_repo
from app.telemetry.context import child_span, record_duration_ms, record_search_counts

logger = logging.getLogger(__name__)

_FILE_BLOCK = re.compile(
    r'<file\s+path="([^"]+)"[^>]*>(.*?)</file>',
    re.DOTALL | re.IGNORECASE,
)


@dataclass(frozen=True)
class SearchHit:
    path: str
    score: float
    content: str
    start_line: int | None = None
    end_line: int | None = None
    vector_score: float = 0.0
    bm25_score: float = 0.0


@dataclass(frozen=True)
class HybridSearchResult:
    hits: list[SearchHit]
    vector_hits: int
    bm25_hits: int
    degraded: bool
    trace_notes: list[str]
    pack: PackResult | None


def fuse_scores(
    vector_scores: dict[str, float],
    bm25_scores: dict[str, float],
    *,
    vector_weight: float,
    bm25_weight: float,
) -> dict[str, float]:
    """Proposed linear fusion after per-channel min-max normalization."""
    keys = set(vector_scores) | set(bm25_scores)
    v_norm = _minmax(vector_scores)
    b_norm = _minmax(bm25_scores)
    out: dict[str, float] = {}
    for k in keys:
        out[k] = vector_weight * v_norm.get(k, 0.0) + bm25_weight * b_norm.get(k, 0.0)
    return out


def mmr_rerank(
    candidates: list[SearchHit],
    *,
    lambda_mult: float,
    top_k: int,
    query_tokens: set[str] | None = None,
) -> list[SearchHit]:
    """Maximal Marginal Relevance over fused candidates (Proposed λ).

    Diversity uses token Jaccard between contents; relevance uses fused score.
    """
    if not candidates or top_k <= 0:
        return []
    remaining = list(candidates)
    selected: list[SearchHit] = []
    # Pre-tokenize
    token_sets = {_hit_key(h): _tokens(h.content or h.path) for h in remaining}

    while remaining and len(selected) < top_k:
        best_idx = 0
        best_val = float("-inf")
        for i, cand in enumerate(remaining):
            rel = cand.score
            if not selected:
                mmr_val = rel
            else:
                div = max(
                    _jaccard(token_sets[_hit_key(cand)], token_sets[_hit_key(s)])
                    for s in selected
                )
                mmr_val = lambda_mult * rel - (1.0 - lambda_mult) * div
            if mmr_val > best_val:
                best_val = mmr_val
                best_idx = i
        chosen = remaining.pop(best_idx)
        selected.append(chosen)
    return selected


def hybrid_search(
    *,
    query: str,
    repo: str,
    top_k: int,
    file_bias: str | None = None,
    settings: Settings | None = None,
    embedder: EmbeddingBackend | None = None,
    store: QdrantStore | None = None,
    bm25: Bm25Store | None = None,
    pack: PackResult | None = None,
) -> HybridSearchResult:
    """Run vector + BM25 + fusion + MMR. Prefer degraded partial results over hard-fail."""
    cfg = settings or get_settings()
    notes: list[str] = []
    degraded = False

    pack_obj = pack or load_pack_by_repo(repo, settings=cfg)
    if pack_obj is None:
        notes.append("pack_cache_miss")
        degraded = True

    emb = embedder or get_embedder(cfg, stub=False)
    qstore = store or QdrantStore(cfg)
    bm25_store = bm25 or get_bm25_store()

    vector_raw: list[dict[str, Any]] = []
    bm25_hits_n = 0

    # --- Vector ---
    t0 = time.perf_counter()
    with child_span("context.vector") as vspan:
        try:
            qvec = emb.embed([query])[0]
            limit = max(top_k, cfg.search_candidate_pool)
            vector_raw = qstore.search(
                qvec,
                repo_name=repo,
                limit=limit,
                file_path=file_bias,
            )
            record_duration_ms(vspan, "duration_ms", (time.perf_counter() - t0) * 1000)
        except Exception as exc:  # noqa: BLE001
            logger.warning("vector search degraded: %s", exc)
            notes.append(f"vector_error:{type(exc).__name__}")
            degraded = True
            record_duration_ms(vspan, "duration_ms", (time.perf_counter() - t0) * 1000)

    # --- BM25 corpus from pack / vector payloads ---
    documents = _documents_from_pack_and_vector(pack_obj, vector_raw)
    t1 = time.perf_counter()
    bm25_scores: dict[str, float] = {}
    content_by_path: dict[str, str] = {}
    lines_by_path: dict[str, tuple[int | None, int | None]] = {}
    with child_span("context.bm25") as bspan:
        try:
            if documents:
                cache_key = bm25_store.build_from_texts(repo, documents)
                hits = bm25_store.search(cache_key, query, top_n=cfg.search_candidate_pool)
                bm25_hits_n = len(hits)
                for h in hits:
                    bm25_scores[h.file_path] = max(bm25_scores.get(h.file_path, 0.0), h.score)
                    content_by_path.setdefault(h.file_path, h.content)
                    lines_by_path.setdefault(h.file_path, (h.start_line, h.end_line))
            else:
                notes.append("bm25_empty_corpus")
                degraded = True
            record_duration_ms(bspan, "duration_ms", (time.perf_counter() - t1) * 1000)
        except Exception as exc:  # noqa: BLE001
            logger.warning("bm25 search degraded: %s", exc)
            notes.append(f"bm25_error:{type(exc).__name__}")
            degraded = True
            record_duration_ms(bspan, "duration_ms", (time.perf_counter() - t1) * 1000)

    vector_scores: dict[str, float] = {}
    for row in vector_raw:
        path = str(row.get("file_path") or "")
        if not path:
            continue
        score = float(row.get("score") or 0.0)
        vector_scores[path] = max(vector_scores.get(path, 0.0), score)
        content_by_path.setdefault(path, str(row.get("content") or ""))
        # Approximate line from chunk content presence — Proposed
        if path not in lines_by_path:
            lines_by_path[path] = (1, None)

    fused = fuse_scores(
        vector_scores,
        bm25_scores,
        vector_weight=cfg.search_vector_weight,
        bm25_weight=cfg.search_bm25_weight,
    )

    candidates = [
        SearchHit(
            path=path,
            score=score,
            content=content_by_path.get(path, ""),
            start_line=(lines_by_path.get(path) or (None, None))[0],
            end_line=(lines_by_path.get(path) or (None, None))[1],
            vector_score=vector_scores.get(path, 0.0),
            bm25_score=bm25_scores.get(path, 0.0),
        )
        for path, score in fused.items()
    ]
    candidates.sort(key=lambda h: h.score, reverse=True)

    t2 = time.perf_counter()
    with child_span("context.mmr") as mspan:
        selected = mmr_rerank(
            candidates,
            lambda_mult=cfg.search_mmr_lambda,
            top_k=top_k,
        )
        record_duration_ms(mspan, "duration_ms", (time.perf_counter() - t2) * 1000)

    record_search_counts(
        None,
        vector_hits=len(vector_scores),
        bm25_hits=bm25_hits_n,
        mmr_selected=len(selected),
    )

    if not selected and (vector_scores or bm25_scores):
        # Fallback: take top fused without MMR
        selected = candidates[:top_k]
        notes.append("mmr_empty_fallback")
        degraded = True

    return HybridSearchResult(
        hits=selected,
        vector_hits=len(vector_scores),
        bm25_hits=bm25_hits_n,
        degraded=degraded,
        trace_notes=notes,
        pack=pack_obj,
    )


def _documents_from_pack_and_vector(
    pack: PackResult | None,
    vector_raw: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    seen: set[str] = set()
    if pack and pack.xml_content:
        for m in _FILE_BLOCK.finditer(pack.xml_content):
            path = m.group(1)
            body = m.group(2)
            # Strip CDATA wrappers if present
            body = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", body, flags=re.DOTALL)
            docs.append(
                {
                    "doc_id": path,
                    "file_path": path,
                    "content": body.strip(),
                    "start_line": 1,
                    "end_line": max(1, body.count("\n") + 1),
                }
            )
            seen.add(path)
    for row in vector_raw:
        path = str(row.get("file_path") or "")
        if not path or path in seen:
            continue
        docs.append(
            {
                "doc_id": path,
                "file_path": path,
                "content": str(row.get("content") or ""),
                "start_line": 1,
                "end_line": None,
            }
        )
        seen.add(path)
    return docs


def _minmax(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    vals = list(scores.values())
    lo, hi = min(vals), max(vals)
    if math.isclose(hi, lo):
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", text or "")}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b) or 1
    return inter / union


def _hit_key(h: SearchHit) -> str:
    return h.path


def hits_to_relevant_files(hits: list[SearchHit]) -> list[dict[str, Any]]:
    """Proposed relevant_files item shape."""
    out: list[dict[str, Any]] = []
    for h in hits:
        item: dict[str, Any] = {"path": h.path, "score": round(h.score, 6)}
        if h.start_line is not None:
            item["start_line"] = h.start_line
        if h.end_line is not None:
            item["end_line"] = h.end_line
        if h.content:
            item["snippet"] = h.content[:240]
        out.append(item)
    return out


# Re-export for tests / pack metrics
__all__ = [
    "SearchHit",
    "HybridSearchResult",
    "fuse_scores",
    "mmr_rerank",
    "hybrid_search",
    "hits_to_relevant_files",
    "estimate_tokens",
]
