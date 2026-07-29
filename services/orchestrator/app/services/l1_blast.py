"""EP-007 L1 blast-radius assembly over EP-006 FalkorDB evidence.

T001 discovery notes (Proposed normalization):
- Resolve ``repo`` + ``file_name`` against revision-scoped ``File`` nodes by
  ``source_path`` (accept basename or relative path; match EP-006 identity).
- Traversal uses reverse IMPORTS (files that import the target) with bounded hops
  (default 3; BRD IMPORTS*1..3 latency context). No source bodies in payloads.

T004 Proposed L1-only heuristics (NOT Confirmed algorithms / L2 linkage):
- ``db_tables``: always ``[]`` (L2 Missing Evidence).
- ``tests_to_run``: path-derived conservative candidates only — if the target
  stem appears under a ``tests/`` File path already present in the graph, include
  those paths; otherwise ``[]``. Do NOT invent L2 test linkage.
- ``risk``: conservative L1-only —
  HIGH if ``len(transitive) > 10`` OR (``max_depth >= 3`` and
  ``len(direct_dependents) + len(transitive) >= 5``);
  MEDIUM if ``direct_dependents`` non-empty; else LOW.
- ``owners``: always ``[]`` (OQ-15 — Proposed empty array only; no element schema).

Accuracy harness applicability: only path-derived tests_to_run candidates where
matching File nodes exist; db_tables/owners/risk scoring remain Incomplete for
Confirmed correctness claims.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Literal, Protocol

from app.adapters.falkordb_store import get_graph_store
from app.config import Settings
from app.security.ignore_policy import path_is_hard_excluded

RiskLevel = Literal["HIGH", "MEDIUM", "LOW"]
DEFAULT_BLAST_HOPS = 3


class BlastStore(Protocol):
    def latest_revision(self, repo: str) -> str | None: ...

    def find_file_node(
        self, repo: str, revision: str, file_name: str
    ) -> Any: ...

    def reverse_imports_dependents(
        self,
        repo: str,
        revision: str,
        target_entity_id: str,
        *,
        max_hops: int = 3,
    ) -> tuple[list[str], list[str], int]: ...

    def get_entities(
        self, repo: str, revision: str, *, terms=(), limit: int = 100
    ) -> list[Any]: ...


@dataclass(frozen=True)
class BlastResult:
    """Confirmed FR-08 fields + Proposed owners / index_revision."""

    direct_dependents: list[str]
    transitive: list[str]
    db_tables: list[str]
    risk: RiskLevel
    tests_to_run: list[str]
    owners: list[Any]
    index_revision: str
    hop_depth: int
    duration_ms: int
    node_count: int

    def as_response_dict(self) -> dict[str, Any]:
        """Confirmed §2.4 fields + Proposed owners / index_revision."""
        return {
            "direct_dependents": self.direct_dependents,
            "transitive": self.transitive,
            "db_tables": self.db_tables,
            "risk": self.risk,
            "tests_to_run": self.tests_to_run,
            "owners": self.owners,
            # Proposed freshness signal (api-contract §2.4 notes) — not Confirmed.
            "index_revision": self.index_revision,
        }


class BlastNotFoundError(LookupError):
    """Proposed 404: unknown repo or file."""


class BlastUnavailableError(RuntimeError):
    """Proposed degrade when FalkorDB/graph store is unavailable."""


class BlastService:
    def __init__(self, settings: Settings, *, store: BlastStore | None = None) -> None:
        self.settings = settings
        self.store: BlastStore = store if store is not None else get_graph_store(settings)

    def compute(
        self,
        repo: str,
        file_name: str,
        *,
        max_hops: int = DEFAULT_BLAST_HOPS,
    ) -> BlastResult:
        started = time.perf_counter()
        if not repo or not str(repo).strip():
            raise BlastNotFoundError("repo must be non-empty")
        if not file_name or not str(file_name).strip():
            raise BlastNotFoundError("file_name must be non-empty")

        try:
            revision = self.store.latest_revision(repo)
        except Exception as exc:  # noqa: BLE001
            raise BlastUnavailableError("graph store unavailable") from exc

        if not revision:
            raise BlastNotFoundError(f"unknown or unindexed repo: {repo}")

        try:
            target = self.store.find_file_node(repo, revision, file_name)
        except Exception as exc:  # noqa: BLE001
            raise BlastUnavailableError("graph store unavailable") from exc

        if target is None:
            raise BlastNotFoundError(f"unknown file in repo {repo}: {file_name}")

        hops = max(1, min(int(max_hops), 5))
        try:
            direct, transitive, max_depth = self.store.reverse_imports_dependents(
                repo, revision, target.entity_id, max_hops=hops
            )
        except Exception as exc:  # noqa: BLE001
            raise BlastUnavailableError("graph store unavailable") from exc

        direct = _filter_paths(direct)
        transitive = _filter_paths(transitive)
        tests = _propose_tests_to_run(self.store, repo, revision, target.source_path)
        risk = _propose_risk(direct, transitive, max_depth)
        duration_ms = int((time.perf_counter() - started) * 1000)
        return BlastResult(
            direct_dependents=direct,
            transitive=transitive,
            db_tables=[],  # Proposed: L2 Missing Evidence
            risk=risk,
            tests_to_run=tests,
            owners=[],  # Proposed OQ-15 — empty array only
            index_revision=revision,
            hop_depth=max_depth if max_depth else hops,
            duration_ms=duration_ms,
            node_count=1 + len(direct) + len(transitive),
        )


def _filter_paths(paths: list[str]) -> list[str]:
    # T010: IgnorePolicy hard-exclude reuse on serialization (Constitution V).
    return [path for path in paths if not path_is_hard_excluded(path)]


def _propose_tests_to_run(
    store: BlastStore, repo: str, revision: str, source_path: str
) -> list[str]:
    """Proposed path-derived candidates only — no invented L2 linkage."""
    stem = PurePosixPath(source_path).stem
    if not stem:
        return []
    try:
        entities = store.get_entities(repo, revision, terms=(), limit=500)
    except Exception:  # noqa: BLE001
        return []
    candidates: list[str] = []
    for entity in entities:
        if getattr(entity, "entity_kind", None) != "File":
            continue
        path = str(getattr(entity, "source_path", ""))
        if path_is_hard_excluded(path):
            continue
        posix = PurePosixPath(path)
        if "tests" not in posix.parts and "test" not in posix.parts:
            continue
        name = posix.stem
        if stem in name or name in {f"test_{stem}", f"{stem}_test", f"{stem}_spec"}:
            candidates.append(path)
    return sorted(set(candidates))


def _propose_risk(
    direct: list[str], transitive: list[str], max_depth: int
) -> RiskLevel:
    """Proposed conservative L1-only heuristic — not a Confirmed algorithm."""
    total = len(direct) + len(transitive)
    if len(transitive) > 10 or (max_depth >= 3 and total >= 5):
        return "HIGH"
    if direct:
        return "MEDIUM"
    return "LOW"
