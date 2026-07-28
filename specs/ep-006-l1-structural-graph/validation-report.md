# EP-006 Implementation Validation Report

## Executive Summary

- **Feature**: EP-006 L1 Structural Graph Generation (US-017 and US-021)
- **Validation date**: 2026-07-28
- **Scope**: T037–T038 implementation verification on `feature/ep-006-l1-structural-graph`
- **Overall status**: **PASS — IMPLEMENTATION VALIDATED WITH EXPLICIT RESIDUAL RISKS**
- **PR-readiness evidence decision**: **Ready for PR with comments**

The supplied executed evidence is strong: the full orchestrator, MCP tests/build, live
FalkorDB integration, and the full Compose API/Qdrant/FalkorDB smoke passed. Focused
evaluation and synthetic performance harnesses also passed within their declared fixtures.
The 1M-LOC harness remains skipped because no approved corpus was available.

Final defect-first review found one in-scope parser defect not covered by the earlier passing
suite: a resolvable Python relative import such as `from .tokens import check` did not produce
the required File→File `IMPORTS` edge to `pkg/tokens.py`. This has now been fixed in
`services/orchestrator/app/adapters/l1_parser.py` and regression-tested in
`services/orchestrator/tests/unit/test_l1_parser.py`. T017 is complete.

A subsequent PR-readiness pass found two stale-graph blockers: scoped L1 re-index lacked
unchanged-file context for local import resolution, and full re-index could leave stale
relationships when endpoint nodes remained. Both were fixed in `l5_index.py`, `l1_graph.py`,
and `falkordb_store.py`, with regression coverage in `test_index_delta_upsert.py` and
`test_falkordb_store.py`.

A final PR-readiness pass found a CI workflow Ruff blocker from legacy lint debt and
intentional parser fixtures. The workflow now excludes only the intentional L1 structural
source fixture corpus, and the remaining broad orchestrator Ruff issues were fixed without
behavior changes.

## Baseline and Environment

- Commit baseline: `9fd4898` (`Merge pull request #6 ...contextos-mcp-agent-wiring`)
- Branch: `feature/ep-006-l1-structural-graph`
- Host: macOS 26.6 arm64
- Test runtime selected by `uv`: Python 3.14.3; project declares Python `>=3.11`
- Existing unrelated changes were preserved; no commit, push, PR, or merge was performed.
- Graphify-first command:
  `graphify query "EP-006 T037 T038 validation tests public POST index context privacy metadata-only graph health MCP" --budget 1500`
  — passed.

## Executed Commands and Outcomes

### Focused EP-006 behavior

1. Focused unit/contract/integration/privacy/eval command:

   `uv run --project services/orchestrator --extra dev pytest` with:
   `test_l1_parser.py`, `test_falkordb_store.py`, `test_l1_graph.py`,
   `test_l1_entity_cache.py`, `test_l1_telemetry.py`, index/context/health contracts,
   L1 index/context integration, delta reconciliation, exclusions, no-exfiltration, and
   graph accuracy.

   **Outcome**: `46 passed, 1 skipped, 2 warnings in 2.00s` before the final T017 fix.
   The skip was the opt-in live FalkorDB test; it was executed separately and passed.
   An initial sandboxed run reported one filesystem permission failure while creating a
   temporary `.git/config`; the unrestricted rerun passed and confirms this was harness
   sandbox friction, not a product defect.

2. Live FalkorDB integration:

   `CONTEXTOS_FALKORDB_INTEGRATION=1 CONTEXTOS_FALKORDB_URL=redis://127.0.0.1:6379 uv run --project services/orchestrator --extra dev pytest tests/integration/test_index_l1_graph.py::test_live_falkor_persists_and_reads_structural_evidence -q -ra`

   **Outcome**: `4 passed` against live FalkorDB, including persistence/read behavior and
   the corrected official-client health ping through `client.connection.ping()`.

3. Graph accuracy:

   `uv run --project services/orchestrator --extra dev pytest tests/eval/test_l1_graph_accuracy.py -q -s -ra`

   **Outcome**: `1 passed`; dataset `l1-structural-fixture-v1`.
   Nodes: TP=4, FP=0, FN=0, precision/recall/F1=`1.0/1.0/1.0`.
   Edge kinds: TP=4, FP=0, FN=0, precision/recall/F1=`1.0/1.0/1.0`.

4. Structural-query/cache evaluation:

   `CONTEXTOS_L1_QUERY_EVAL=1 uv run --project services/orchestrator --extra dev pytest tests/eval/test_l1_structural_queries.py -q -s -ra`

   **Outcome**: `1 passed`; dataset `l1-structural-queries-v1`.
   Grounding precision/recall/F1=`1.0/1.0/1.0`; post-warm cache hit rate=`1.0`;
   p50 approximately `0.0057ms`, p95 approximately `0.0207ms`. This is a small deterministic fixture baseline,
   not a production latency claim.

5. Opt-in 100-file delta harness:

   `CONTEXTOS_PERF_DELTA=1 uv run --project services/orchestrator --extra dev pytest tests/integration/test_index_perf_delta.py -q -s -ra`

   **Outcome**: `1 passed`; fixture `l1-delta-v1`, 100 files, 500 graph nodes,
   cold combined L5-pack/L1=`0.0706s`, below the `<60s` target.
   Embeddings were intentionally skipped by this harness.

6. Final T017 parser regression:

   `uv run pytest tests/unit/test_l1_parser.py tests/eval/test_l1_graph_accuracy.py -q`

   **Outcome**: `11 passed in 0.12s`. Coverage includes local absolute imports and Python
   sibling relative imports such as `from .tokens import check`, both producing File→File
   `IMPORTS` edges when the target file is indexed.

### Full regression and client checks

7. Full orchestrator:

   `uv run --project services/orchestrator --extra dev pytest services/orchestrator/tests -q -ra`

   **Outcome**: `137 passed, 9 skipped, 13 warnings`.
   EP-006 skips in this aggregate run: query eval, live FalkorDB, delta harness,
   1M-LOC harness, and Compose smoke; the first three were subsequently executed and
   passed. Other skips are documented pre-existing EP-002/EP-003 harness blockers.

8. MCP:

   `npm --prefix clients/mcp test && npm --prefix clients/mcp run lint && npm --prefix clients/mcp run build`

   **Outcome**: Vitest `4 passed`; TypeScript no-emit check passed; build passed.

9. CI-shaped orchestrator lint and tests:

   `uv run ruff check app tests --exclude tests/fixtures/l1_structural_repo`

   **Outcome**: passed. The excluded fixture directory intentionally contains malformed and
   language-sample source used to validate parser behavior.

   `uv run python -m pytest -v --tb=short -m "not perf"`

   **Outcome**: `137 passed, 6 skipped, 3 deselected, 13 warnings`.

10. EP-006-touched Python lint:

   `uv run --project services/orchestrator --extra dev ruff check <EP-006 changed Python files and executable tests>`

   **Outcome**: `All checks passed!`

11. VS Code extension CI job:

    `npm run lint && npm test` in `clients/vscode`

    **Outcome**: TypeScript no-emit passed; Vitest `10 passed` files,
    `38 passed | 1 skipped`.

12. Compile:

    `uv run --project services/orchestrator python -m compileall -q services/orchestrator/app services/orchestrator/tests/{unit,contract,integration,eval}`

    **Outcome**: passed. Compiling the entire fixture tree separately reports the expected
    syntax error in `fixtures/l1_structural_repo/malformed/broken.py`, which exists to test
    conservative malformed-source handling.

### Compose and opt-in blockers

13. `docker compose -f deploy/docker-compose.yml config`

    **Outcome**: passed. It resolves API `service_healthy` dependencies on FalkorDB and
    Qdrant, FalkorDB healthcheck/configuration, and the unchanged API port/wiring.

14. Full Compose API smoke:

    `docker compose -f deploy/docker-compose.yml up -d --build api`

    **Outcome**: passed after host disk space was recovered, Docker Desktop restarted, and
    the API Dockerfile was updated to preinstall the official CPU-only ARM64 Torch wheel
    and cache heavy dependencies before app-code layers. Command:
    `CONTEXTOS_L1_COMPOSE_SMOKE=1 CONTEXTOS_L1_COMPOSE_REPO_PATH=/repos/fixture CONTEXTOS_ORCHESTRATOR_BASE_URL=http://127.0.0.1:8001 uv run pytest tests/integration/test_l1_compose_smoke.py -q`.
    Final result: `1 passed in 32.99s`; health reported FalkorDB `ok`, and `/index` returned
    `graph_nodes > 0`.

15. 1M-LOC full-index harness:

    **Outcome**: **skipped**. `CONTEXTOS_PERF_CORPUS` and a benchmark FalkorDB URL were not
    supplied. The `<15min` target remains unverified.

## Contract and Scope Audit

- Generated OpenAPI paths are exactly `GET /`, `POST /index`, and `POST /context`;
  no EP-006 route was added.
- Actual `POST /index` request schema properties are
  `repo_path`, `repo_name`, optional Proposed `paths`, and optional Proposed `files`.
  Git diff confirms EP-006 did not add these optional OQ-14 properties. Response properties
  are exactly `files_indexed`, `graph_nodes`, `embeddings`, and `time_ms`.
- Actual `POST /context` request properties are `query`, `file`, `repo`, `top_k`, and the
  pre-existing optional Proposed `phase`. Response properties remain exactly
  `final_context`, `metrics`, `blast_radius`, `memory`, `relevant_files`, and `is_real`.
  L1 evidence is appended only inside `final_context`; trace uses the existing metrics field.
- MCP registers exactly the existing `contextos_health`, `contextos_index`, and
  `contextos_ask` tools. Tests/build and source audit show no graph/cache state or new tool.
- Structural blast hints return `blast_declined`; no blast computation, graph HTML, or
  visualization route/data was added. Existing empty `blast_radius` response compatibility
  is unchanged.
- Ignore/no-exfil tests prove `.gitignore`, `.env`, secrets, dependencies, build output,
  binaries, and external indexing LLM calls do not reach L1 persistence.
- Node/edge persistence, cache values, and L1 telemetry are metadata/provenance/count/timing
  only; tests assert no source body storage and no sensitive path/content telemetry.
- Health response keys remain exactly `status`, `pipeline`, `falkor`, and `qdrant`;
  contract and degraded-dependency tests passed.

## Requirement Verification

- **FR-001–FR-003, FR-007**: passed deterministic parser/service/store, persisted graph,
  five-language fixture, import/typed-chain, resolvable File→File imports including Python
  relative imports, full stale-relationship cleanup, incremental import reconciliation,
  provenance, reconciliation, and accuracy tests.
- **FR-004–FR-005**: passed exact API/OpenAPI and FastAPI ownership/scope audit.
- **FR-006**: passed privacy exclusions and no-index-time-exfiltration tests.
- **FR-008**: passed cache lifecycle/isolation, cited `/context` grounding, stale/unavailable
  fallback, stateless MCP, and blast-decline tests.
- **SC-001**: measured pass on the declared 100-file local harness, with embeddings skipped.
- **SC-002**: skipped/blocked; no approved 1M-LOC corpus.
- **SC-003**: deterministic graph and query fixture measurements executed and passed;
  external-corpus generalization remains unproven.

## Defects, Warnings, and Residual Risks

- **Defects found/fixed**: Python sibling relative imports did not resolve to File→File
  `IMPORTS`; scoped L1 re-index lacked unchanged-file context for local import resolution;
  full re-index could leave stale relationships whose endpoint nodes remained. All three
  were fixed and regression-tested.
- Host validation used Python 3.14, while the container targets Python 3.11. The Python 3.11
  Docker image built and the Compose smoke path executed successfully.
- Qdrant client `1.18.0` warns that running server `1.12.5` is incompatible by its supported
  version-window policy; regression tests pass, but deployment versions should be aligned.
- FastAPI/httpx emits a Starlette deprecation warning.
- Accuracy/query metrics use small deterministic fixtures and do not establish broad
  five-language production quality.
- CI-shaped broad Ruff passes with the intentional structural fixture corpus excluded from
  linting.
- The first Docker build pulled multi-gigabyte CUDA artifacts on arm64 and exposed a host
  disk-space failure. The Dockerfile now preinstalls CPU-only Torch and caches heavyweight
  dependencies before copying app code, but Docker disk usage should still be monitored.

## Decision

**Evidence is sufficient to begin PR-readiness review**, with the unexecuted 1M-LOC corpus
benchmark, dependency-version warning, fixture-scale quality limitations, and non-blocking
cleanup warnings carried as explicit residual risks. Final PR-readiness review found no
blockers and marked the feature ready for PR with comments.
