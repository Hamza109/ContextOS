"""Subprocess entrypoint for crash-isolated L1 tree-sitter parsing.

Invoked as ``python -m app.adapters.l1_parse_worker`` with a pickle payload on
stdin; writes a pickle ParseResult on stdout. Native grammar crashes become a
non-zero exit code so the parent can fall back without killing the API process.
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path


def main() -> int:
    payload = pickle.load(sys.stdin.buffer)
    repo, root_s, path_strs, revision = payload
    # Late import keeps spawn/bootstrap cost low and avoids circular imports at
    # package import time.
    from app.adapters.l1_parser import TreeSitterL1Parser

    parser = TreeSitterL1Parser(isolate_crashes=False)
    result = parser._parse_paths_inprocess(
        repo, Path(root_s), [Path(p) for p in path_strs], revision
    )
    pickle.dump(result, sys.stdout.buffer, protocol=pickle.HIGHEST_PROTOCOL)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
