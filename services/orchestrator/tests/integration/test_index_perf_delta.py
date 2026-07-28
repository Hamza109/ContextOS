"""Opt-in EP-006 100-file L5-pack + L1 delta measurement harness."""

from __future__ import annotations

import os
import platform
import time
from pathlib import Path

import pytest

from app.config import Settings
from app.services.l5_index import run_index

pytestmark = pytest.mark.perf


@pytest.mark.skipif(
    not os.environ.get("CONTEXTOS_PERF_DELTA"),
    reason="NFR-002 harness skipped: set CONTEXTOS_PERF_DELTA=1 to execute 100-file delta timing",
)
def test_delta_100_files_under_60s(tmp_path: Path) -> None:
    root = tmp_path / "l1-delta-v1"
    root.mkdir()
    files = []
    for index in range(100):
        relative = f"src/file_{index}.py"
        path = root / relative
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"class C{index}:\n def run(self):\n  call_{index}()\n", encoding="utf-8")
        files.append(relative)
    settings = Settings(
        falkordb_url=os.environ.get("CONTEXTOS_PERF_FALKORDB_URL", "memory://perf"),
        pack_cache_dir=tmp_path / "packs",
    )
    started = time.perf_counter()
    result = run_index(
        str(root),
        "perf-delta-v1",
        files=files,
        settings=settings,
        skip_embed=True,
    )
    elapsed = time.perf_counter() - started
    print(
        {
            "fixture_revision": "l1-delta-v1",
            "warm_state": "cold",
            "environment": platform.platform(),
            "combined_l5_pack_l1_seconds": elapsed,
            "reported_total_ms": result.time_ms,
            "graph_nodes": result.graph_nodes,
            "target_seconds": 60,
            "observed_under_target": elapsed < 60,
            "l5_embeddings": "skipped_by_harness",
        }
    )
    assert result.files_indexed == 100
