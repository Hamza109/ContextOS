"""Versioned OKF knowledge fixture (EP-013) with generated exclusion cases."""

from __future__ import annotations

import shutil
from pathlib import Path

FIXTURE_REVISION = "okf-knowledge-fixture-v1"

# Expected Concept IDs (path relative to bundle root without .md)
EXPECTED_DOC_CONCEPT_IDS = frozenset(
    {
        "docs/architecture/system-overview",
        "docs/backlog/user-stories",
        "specs/ep-demo-okf/spec",
        "specs/ep-demo-okf/plan",
        "specs/ep-demo-okf/tasks",
        "specs/ep-demo-okf/validation-report",
    }
)


def materialize_okf_knowledge_repo(destination: Path) -> Path:
    source = Path(__file__).with_name("okf_knowledge_repo")
    shutil.copytree(source, destination)
    generated = {
        ".env": "SECRET_TOKEN=must-not-become-okf-source\n",
        "secret.pem": "must-not-become-okf-source\n",
        "node_modules/leak.md": "# Leak\nmust-not-become-okf-source\n",
        "build/out.md": "# Build\nmust-not-become-okf-source\n",
        "ignored/secret-notes.md": "# Ignored\nmust-not-become-okf-source\n",
        "docs/architecture/.env": "NESTED=must-not-become-okf-source\n",
    }
    for relative, content in generated.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (destination / "asset.bin").write_bytes(b"\x00secret-binary")
    return destination
