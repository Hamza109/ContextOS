from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.adapters.l1_parser import TreeSitterL1Parser

pytestmark = pytest.mark.eval
DATASET_REVISION = "l1-structural-fixture-v1"


def test_l1_graph_accuracy_fixture(tmp_path: Path) -> None:
    path = tmp_path / "auth.py"
    path.write_text(
        "import os\nclass Auth:\n def validate(self):\n  return check()\n",
        encoding="utf-8",
    )
    result = TreeSitterL1Parser().parse_paths("accuracy", tmp_path, [path], "revision")
    observed_nodes = {
        (node.entity_kind, node.qualified_name)
        for node in result.nodes
        if node.entity_kind in {"File", "Class", "Method", "Call"}
    }
    expected_nodes = {
        ("File", "auth.py"),
        ("Class", "auth.Auth"),
        ("Method", "auth.Auth.validate"),
        ("Call", "auth.Auth.validate::check@4"),
    }
    observed_edges = {edge.edge_kind for edge in result.edges}
    expected_edges = {"CONTAINS", "DECLARES", "MAKES_CALL", "IMPORTS"}
    node_metrics = _metrics(expected_nodes, observed_nodes)
    edge_metrics = _metrics(expected_edges, observed_edges)
    print(
        json.dumps(
            {
                "dataset_revision": DATASET_REVISION,
                "node_metrics": node_metrics,
                "edge_metrics": edge_metrics,
                "expected_nodes": sorted(expected_nodes),
                "observed_nodes": sorted(observed_nodes),
            },
            sort_keys=True,
        )
    )
    assert node_metrics == {"tp": 4, "fp": 0, "fn": 0, "precision": 1.0, "recall": 1.0, "f1": 1.0}
    assert edge_metrics["fn"] == 0


def _metrics(expected: set, observed: set) -> dict[str, float | int]:
    tp = len(expected & observed)
    fp = len(observed - expected)
    fn = len(expected - observed)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
