"""Opt-in blast accuracy harness design (T006) — skip by default; NO pass claims.

Design:
- Fixture with expected affected-tests set for path-derived Proposed heuristics only.
- Measure correct-predicted rate vs >95% where rules apply (BRD §12).
- Skip/partial when L2 linkage Missing Evidence (db_tables/owners/risk algorithm).
- Execution evidence belongs in validation-report.md — no silent pass.
"""

from __future__ import annotations

import os

import pytest

from app.adapters.falkordb_store import InMemoryFalkorStore
from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings
from app.services.l1_blast import BlastService

pytestmark = pytest.mark.skipif(
    os.environ.get("CONTEXTOS_BLAST_ACCURACY") != "1",
    reason="Opt-in: set CONTEXTOS_BLAST_ACCURACY=1 to execute (no pass claim)",
)


def test_blast_accuracy_path_derived_tests_only() -> None:
    store = InMemoryFalkorStore()
    nodes = [
        StructuralNode("a", "acc", "src/foo.py", "File", "src/foo.py", 1, 2, "r1"),
        StructuralNode("b", "acc", "src/bar.py", "File", "src/bar.py", 1, 2, "r1"),
        StructuralNode(
            "t", "acc", "tests/test_foo.py", "File", "tests/test_foo.py", 1, 2, "r1"
        ),
    ]
    edges = [StructuralEdge("b", "a", "IMPORTS", "acc", "src/bar.py", "r1")]
    store.persist("acc", "r1", nodes, edges)

    result = BlastService(Settings(falkordb_url="memory://acc"), store=store).compute(
        "acc", "src/foo.py"
    )
    expected_tests = {"tests/test_foo.py"}
    predicted = set(result.tests_to_run)
    tp = len(expected_tests & predicted)
    fp = len(predicted - expected_tests)
    fn = len(expected_tests - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    print(
        {
            "harness": "blast_accuracy",
            "scope": "path_derived_tests_to_run_only",
            "expected_tests": sorted(expected_tests),
            "predicted_tests": sorted(predicted),
            "precision": precision,
            "recall": recall,
            "db_tables_applicable": False,
            "owners_applicable": False,
            "risk_algorithm_confirmed": False,
            "target_accuracy": 0.95,
            "pass_claimed": False,
            "note": "Partial: L2 linkage Incomplete; record in validation-report",
        }
    )
    # Design scaffold only — assert harness ran, not SC-002 pass.
    assert "tests/test_foo.py" in result.tests_to_run
