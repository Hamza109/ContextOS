"""Proposed BM25 adapter — Option A in-process over pack/chunk texts (OQ-BM25-store).

Library choice: in-house Okapi BM25 (rank_bm25-compatible math) — **not** BRD-pinned.
Options B/C escalate only with measured NFR-001 evidence.
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from dataclasses import dataclass
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


@dataclass(frozen=True)
class Bm25Hit:
    doc_id: str
    score: float
    file_path: str
    content: str
    start_line: int | None = None
    end_line: int | None = None


@dataclass
class _CorpusDoc:
    doc_id: str
    file_path: str
    content: str
    tokens: list[str]
    start_line: int | None = None
    end_line: int | None = None


class Bm25Store:
    """In-process BM25 index keyed by repo_name + content hash (Proposed Option A)."""

    def __init__(self, *, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._lock = Lock()
        # cache: (repo_name, content_hash) -> (docs, avgdl, df, N)
        self._cache: dict[str, tuple[list[_CorpusDoc], float, dict[str, int], int]] = {}

    def build_from_texts(
        self,
        repo_name: str,
        documents: list[dict[str, Any]],
    ) -> str:
        """Build/replace corpus for repo.

        Each document: {doc_id, file_path, content, start_line?, end_line?}
        Returns content hash key used for cache.
        """
        joined = "\n".join(d.get("content", "") for d in documents)
        content_hash = hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]
        cache_key = f"{repo_name}:{content_hash}"

        with self._lock:
            if cache_key in self._cache:
                return cache_key

            docs: list[_CorpusDoc] = []
            for d in documents:
                content = d.get("content") or ""
                tokens = _tokenize(content)
                docs.append(
                    _CorpusDoc(
                        doc_id=str(d.get("doc_id") or d.get("file_path") or ""),
                        file_path=str(d.get("file_path") or ""),
                        content=content,
                        tokens=tokens,
                        start_line=d.get("start_line"),
                        end_line=d.get("end_line"),
                    )
                )
            n = len(docs) or 1
            avgdl = sum(len(x.tokens) for x in docs) / n
            df: dict[str, int] = {}
            for doc in docs:
                for term in set(doc.tokens):
                    df[term] = df.get(term, 0) + 1
            self._cache[cache_key] = (docs, avgdl, df, len(docs))
            # Keep only latest key per repo to bound memory
            for old in [k for k in self._cache if k.startswith(f"{repo_name}:") and k != cache_key]:
                del self._cache[old]
            logger.debug("BM25 corpus built for %s docs=%s", repo_name, len(docs))
            return cache_key

    def search(self, cache_key: str, query: str, *, top_n: int = 50) -> list[Bm25Hit]:
        with self._lock:
            entry = self._cache.get(cache_key)
        if not entry:
            return []
        docs, avgdl, df, n = entry
        q_tokens = _tokenize(query)
        if not q_tokens or not docs:
            return []

        scored: list[Bm25Hit] = []
        for doc in docs:
            score = _bm25_score(q_tokens, doc.tokens, df, n, avgdl, self.k1, self.b)
            if score > 0:
                scored.append(
                    Bm25Hit(
                        doc_id=doc.doc_id,
                        score=float(score),
                        file_path=doc.file_path,
                        content=doc.content,
                        start_line=doc.start_line,
                        end_line=doc.end_line,
                    )
                )
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_n]


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def _bm25_score(
    query_tokens: list[str],
    doc_tokens: list[str],
    df: dict[str, int],
    n: int,
    avgdl: float,
    k1: float,
    b: float,
) -> float:
    if not doc_tokens:
        return 0.0
    tf: dict[str, int] = {}
    for t in doc_tokens:
        tf[t] = tf.get(t, 0) + 1
    dl = len(doc_tokens)
    score = 0.0
    for term in query_tokens:
        if term not in tf:
            continue
        n_q = df.get(term, 0)
        idf = math.log(1 + (n - n_q + 0.5) / (n_q + 0.5))
        freq = tf[term]
        denom = freq + k1 * (1 - b + b * dl / max(avgdl, 1e-9))
        score += idf * (freq * (k1 + 1)) / denom
    return score


# Process-wide default store (Proposed per-process cache)
_DEFAULT_STORE = Bm25Store()


def get_bm25_store() -> Bm25Store:
    return _DEFAULT_STORE
