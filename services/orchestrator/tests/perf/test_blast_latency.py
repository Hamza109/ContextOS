"""Opt-in blast latency harness (T005/T021) — skip by default; NO pass claims.

Design (T005):
- Build ~10k-node L1 File graph with IMPORTS edges in InMemoryFalkorStore.
- Run 3-hop reverse-IMPORTS blast queries; record machine/revision/cold-warm/p50/p95.
- Target p95 <2s (BRD §10) is a validation target only — this module never asserts pass.
- Execution evidence belongs in specs/ep-007-l1-blast-visualization/validation-report.md.
"""

from __future__ import annotations

import os
import platform
import statistics
import time

import pytest

from app.adapters.falkordb_store import InMemoryFalkorStore
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings
from app.services.l1_blast import BlastService

pytestmark = pytest.mark.skipif(
    os.environ.get("CONTEXTOS_BLAST_LATENCY") != "1",
    reason="Opt-in: set CONTEXTOS_BLAST_LATENCY=1 to execute (no pass claim)",
)


def test_blast_latency_harness_records_percentiles_only() -> None:
    store = InMemoryFalkorStore()
    n = int(os.environ.get("CONTEXTOS_BLAST_LATENCY_NODES", "10000"))
    revision = "latency-harness-r1"
    nodes = [
        StructuralNode(f"f{i}", "latency", f"f{i}.py", "File", f"f{i}.py", 1, 1, revision)
        for i in range(n)
    ]
    edges = [
        StructuralEdge(f"f{i}", f"f{i - 1}", "IMPORTS", "latency", f"f{i}.py", revision)
        for i in range(1, n)
    ]
    store.persist("latency", revision, nodes, edges)
    service = BlastService(Settings(falkordb_url="memory://latency"), store=store)

    samples_ms: list[float] = []
    # Cold then warm
    for _ in range(12):
        started = time.perf_counter()
        service.compute("latency", "f0.py", max_hops=3)
        samples_ms.append((time.perf_counter() - started) * 1000)

    ordered = sorted(samples_ms)
    p50 = statistics.median(ordered)
    p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
    print(
        {
            "harness": "blast_latency",
            "machine": platform.node(),
            "platform": platform.platform(),
            "revision": revision,
            "nodes": n,
            "hops": 3,
            "samples_ms": samples_ms,
            "p50_ms": p50,
            "p95_ms": p95,
            "target_p95_ms": 2000,
            "pass_claimed": False,
            "note": "Record in validation-report; do not treat as SC-001 pass without review",
        }
    )
    # Structural sanity only — never assert p95 < 2s here.
    assert len(samples_ms) >= 10
