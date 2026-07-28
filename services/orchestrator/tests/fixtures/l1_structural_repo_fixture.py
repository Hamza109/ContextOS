"""Versioned EP-006 fixture copier including generated privacy cases."""

from __future__ import annotations

import shutil
from pathlib import Path

FIXTURE_REVISION = "l1-structural-fixture-v1"


def materialize_l1_structural_repo(destination: Path) -> Path:
    source = Path(__file__).with_name("l1_structural_repo")
    shutil.copytree(source, destination)
    generated = {
        ".env": "TOKEN=must-not-parse\n",
        "secret.pem": "must-not-parse\n",
        "node_modules/dependency.js": "secretCall()\n",
        "build/generated.py": "secret_call()\n",
        "ignored/ignored.py": "secret_call()\n",
    }
    for relative, content in generated.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (destination / "asset.bin").write_bytes(b"\x00secret")
    return destination
