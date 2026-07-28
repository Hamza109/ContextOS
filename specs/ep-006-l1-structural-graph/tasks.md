# Tasks: EP-006 L1 Structural Graph Generation

**Input**: `specs/ep-006-l1-structural-graph/spec.md` and `plan.md`  
**Prerequisites**: The existing FastAPI index path, local repository policy boundary, and upstream EP-001–EP-005 remain available.  
**Status**: Final validation executed 2026-07-28. Implementation tasks T007–T038 are complete. T026 and T027 executed with narrower synthetic evidence than originally planned, and the implemented T028 harness was skipped because no approved 1M-LOC corpus was available.

**Scope guardrails**: Deliver only L1 extraction/persistence through the existing `POST /index` and its existing `graph_nodes` field. Do not add routes or fields; do not implement `/blast`, visualization, L2/L4/L6, RBAC, CLI, VS Code, dashboards, or JetBrains work.

## Phase 1: Governance and Discovery (Blocking)

**Purpose**: Turn proposed or missing L1 operational details into approved, evidenced implementation decisions before changing the index path.

- [x] T001 [L1] Approved official `FalkorDB>=1.6.2,<2`, URL/prefix/timeout configuration, synchronous adapter boundary, and injectable query-capturing fake. Dependency/config edits remain T007. (FR-002; Plan Approved implementation design)
- [x] T002 [L1] Approved deterministic repository-scoped entity IDs; FR-007 node/edge provenance; `CONTAINS`/`DECLARES`/`MAKES_CALL`/`IMPORTS`; revision-scoped full replacement and affected-path incremental reconciliation; distinct persisted request-node count. (FR-001, FR-002, FR-007; Plan Data Model Changes)
- [x] T003 [L1] Approved `tree-sitter-language-pack>=1.13.3,<2` for Python, JavaScript, TypeScript/TSX, Go, and Java; syntactic call precision; import-only regex fallback; counted skips for unsupported/malformed source. (FR-003; Plan Approved implementation design)
- [x] T004 [P] [L1] Approved default Compose FalkorDB service with healthcheck, API `service_healthy` dependency, `CONTEXTOS_FALKORDB_URL=redis://falkordb:6379`, isolated integration graph names, and unchanged health response fields. Runtime verification remains T025. (FR-002)
- [x] T005 [L1] Approved fail-existing-index behavior for parse orchestration/FalkorDB failures, parse-before-write, cache refresh only after graph commit, and no graph-specific HTTP semantics. (FR-004)
- [x] T006 [P] [L1] Approved versioned five-language fixture design with canonical expected node/edge IDs; report TP/FP/FN and precision/recall/F1 separately with dataset revision, command, environment, and observed output. No result is claimed. (Constitution IV; SC-003)

**Checkpoint**: Passed 2026-07-28. Implementation dependencies and runtime/measurement results remain unexecuted.

## Phase 2: Foundational L1 Infrastructure (Blocking)

**Purpose**: Establish the policy-preserving internal boundaries and isolated test environment required by US-017.

- [x] T007 [L1] Add the selected FalkorDB dependency and **Proposed** configuration keys to `services/orchestrator/pyproject.toml` and `services/orchestrator/app/config.py`, including local-only connection handling; do not place credentials in source or `.env` fixtures. (T001; FR-002, FR-006)
- [x] T008 [L1] Wire the approved FalkorDB Compose configuration in `deploy/docker-compose.yml` and its API dependency/readiness behavior from T004; preserve the existing health response fields. Live Compose smoke passed. (T004, T007; FR-002, FR-004)
- [x] T009 [L1] Create the **Proposed** parser and FalkorDB adapter interfaces in `services/orchestrator/app/adapters/l1_parser.py` and `services/orchestrator/app/adapters/falkordb_store.py`, implementing only the T002/T003-approved contract and no graph-query API. (T001–T003; FR-001–FR-003, FR-007)
- [x] T010 [L1] Create the **Proposed** FastAPI-owned orchestration boundary in `services/orchestrator/app/services/l1_graph.py`; its input must be repository identity plus already-allowed paths, and it must not walk files, relax exclusions, or call external LLMs. (T002, T003, T005, T009; FR-005–FR-007)
- [x] T011 [P] [L1] Add approved structural fixture source and exclusion cases under **Proposed** `services/orchestrator/tests/fixtures/l1_structural_repo/`, including imports, typed declarations/calls, malformed or unsupported input as applicable, `.gitignore`, `.env`, secret, dependency/build, and binary cases. Sensitive/excluded cases are generated at test time rather than versioned. (T003, T006; FR-001, FR-003, FR-006)

**Checkpoint**: The internal L1 boundaries consume only eligible source and can run against an isolated FalkorDB environment; no public API contract has changed.

## Phase 3: User Story US-017 — Generate a Typed Structural Graph (P1)

**Goal**: Generate and persist approved L1 structural/import evidence during the existing FastAPI index flow, then return the approved graph-node count through the existing response field.

**Independent Test**: Index the structural fixture through `POST /index`, inspect isolated FalkorDB evidence and response `graph_nodes`, and prove excluded source reached neither parser nor store.

### Tests for US-017

- [x] T012 [P] [US-017] [L1] Add parser mapping/failure-policy unit coverage in **Proposed** `services/orchestrator/tests/unit/test_l1_parser.py` for the T003-declared languages, typed chain, `IMPORTS`, malformed/unsupported behavior, and resolvable local/relative imports. (T003, T009, T011; FR-001, FR-003)
- [x] T013 [P] [US-017] [L1] Add FalkorDB adapter unit coverage in **Proposed** `services/orchestrator/tests/unit/test_falkordb_store.py` using the T001-approved double; verify provenance payload, idempotent count behavior, and update/delete reconciliation request construction. (T001, T002, T009; FR-002, FR-007)
- [x] T014 [P] [US-017] [L1] Add L1 service unit coverage in **Proposed** `services/orchestrator/tests/unit/test_l1_graph.py`; prove it accepts only supplied allowed paths, reports the T002 node-count rule, and applies the T005 failure decision. (T002, T005, T010; FR-001, FR-004–FR-007)
- [x] T015 [P] [US-017] [API] Assert the exact four-field response/OpenAPI contract remains unchanged while `graph_nodes` may be non-zero after L1 generation. Coverage is split between the existing index contract suite and `test_index_l1_graph.py`. (T010; FR-004)
- [x] T016 [P] [US-017] [Security] Extend `services/orchestrator/tests/integration/test_index_no_exfil.py` and `services/orchestrator/tests/integration/test_index_exclusions_qdrant.py` so ignored, `.env`, secret, dependency/build, and binary content never reaches L1 parser/store and no index-time external LLM client is called. (T010, T011; FR-006)

### Implementation for US-017

- [x] T017 [US-017] [L1] Implement selected extraction and normalized structural/import output in `services/orchestrator/app/adapters/l1_parser.py` according to T002/T003; retain source location/provenance metadata but not full source bodies. Resolvable local imports, including Python sibling relative imports like `from .tokens import ...`, now produce Confirmed File→File `IMPORTS` edges. (T012; FR-001, FR-003, FR-007)
- [x] T018 [US-017] [L1] Implement selected FalkorDB writes and T002-approved reconciliation/count semantics in `services/orchestrator/app/adapters/falkordb_store.py`, including stale relationship cleanup on full re-index and incident-edge cleanup for affected paths. (T013, T017; FR-002, FR-007)
- [x] T019 [US-017] [L1] Implement policy-owned L1 generation/persistence orchestration in `services/orchestrator/app/services/l1_graph.py`, including the T005 failure behavior, affected-path persistence filtering, and no independent repository walk. (T014, T017, T018; FR-001–FR-007)
- [x] T020 [US-017] [L1] Integrate `l1_graph` into `services/orchestrator/app/services/l5_index.py` after the existing `IgnorePolicy` and `walk_allowed_files` eligibility boundary, pass all eligible files to L1 for import resolution while keeping L5 chunking scoped to requested files, and replace the current zero with the approved `graph_nodes` result. Preserve L5 Qdrant work as a separate upstream concern. (T016, T019; FR-004–FR-006)
- [x] T021 [US-017] [API] Update only L1-status wording in `services/orchestrator/app/api/index.py` and comments in `services/orchestrator/app/api/schemas_index.py`; retain `POST /index`, `{repo_path, repo_name}`, and exactly `files_indexed`, `graph_nodes`, `embeddings`, `time_ms`. (T015, T020; FR-004)
- [x] T022 [US-017] [Telemetry] Extend `services/orchestrator/app/telemetry/indexing.py` and its invocation from `services/orchestrator/app/services/l5_index.py` with approved L1 parse/persist duration and count attributes; record counts/timings only, never source content or excluded filenames. (T020; FR-006; Plan §50)

### Integration, acceptance, and operational verification

- [x] T023 [US-017] [L1] Add isolated FalkorDB integration/acceptance coverage in **Proposed** `services/orchestrator/tests/integration/test_index_l1_graph.py`: index fixture via service and `POST /index`, inspect typed/import/provenance evidence, and compare `graph_nodes` with the T002 count rule. Live FalkorDB integration passed. (T020–T022; FR-001–FR-004, FR-007)
- [x] T024 [US-017] [L1] Extend `services/orchestrator/tests/integration/test_index_delta_upsert.py` to re-index a changed allowed scope and verify only the T002-defined affected graph evidence is reconciled, including File→File imports to unchanged local targets; do not assert a new incremental request contract beyond existing proposed test inputs. (T020, T023; FR-001, FR-004; OQ-14)
- [x] T025 [US-017] [API] Add **Proposed** `services/orchestrator/tests/integration/test_l1_compose_smoke.py` and execute the approved API/Qdrant/FalkorDB Compose path. Result: passed; health reported FalkorDB `ok` and `/index` returned `graph_nodes>0`. (T008, T023; FR-002, FR-004)
- [x] T026 [US-017] [L1] Execute the graph-accuracy method in **Proposed** `services/orchestrator/tests/eval/test_l1_graph_accuracy.py` and record its outcome. Result: Python synthetic fixture precision/recall/F1 `1.0`; this is narrower than the planned five-language benchmark and is not a generalized accuracy claim. (T023; Constitution IV; SC-003)
- [x] T027 [US-017] [Telemetry] Replace and execute the opt-in 100-file harness in `services/orchestrator/tests/integration/test_index_perf_delta.py`. Result: cold synthetic combined L5-pack+L1 `0.0706s`, 500 graph nodes, embeddings skipped; the harness reports combined rather than separate L5/L1 stage timing. (T022, T024; SC-001)
- [x] T028 [US-017] [Telemetry] Replace the skeletal full-index harness in `services/orchestrator/tests/integration/test_index_perf_full.py` with an opt-in combined L5+L1 1M-LOC measurement harness. **Implemented, execution skipped** because no approved 1M-LOC corpus was available; `<15min` remains unverified. (T022; SC-002)

**Checkpoint**: US-017 is independently complete only when T023 verifies typed/import/provenance evidence and `graph_nodes`, T016 proves the no-exfil/ignore boundary, and all executed outcomes are recorded rather than inferred.

## Phase 4: User Story US-021 — Structural Questions from Hot Entities (P2)

**Status**: Design contract approved. Implementation is authorized only inside FastAPI and existing `POST /context`; no endpoint/field, MCP-owned state, or blast behavior is authorized.

**Goal**: Answer supported structural location/ownership questions from revision-scoped hot entities while preserving existing L5 fallback and stateless MCP.

**Independent Test**: Index the structural fixture, call `POST /context` with a supported question, and verify cited entity evidence in `final_context`; then prove cache hit, revision invalidation, stale/unavailable fallback, stateless MCP pass-through, and blast exclusion.

- [x] T029 [US-021] [L1] Resolved OQ-06: FastAPI owns a 10,000-entry/300-second bounded LRU+TTL entity cache keyed by `(repo, index_revision, entity_id)`; FalkorDB is source of truth; successful commits invalidate/warm revisions; existing `/context` composes evidence; MCP is stateless; failure degrades to L5; blast remains EP-007. (FR-008; OQ-06)
- [x] T030 [US-021] [L1] Approved evaluation design: versioned expected entity/citation fixtures; grounded-answer precision/recall/F1; post-warm cache hit rate; cold/warm p50/p95 latency; no threshold or pass claim before execution. (T029; FR-008; SC-003)
- [x] T031 [P] [US-021] [L1] Add cache unit coverage for bounds, TTL, repository/revision isolation, successful-index invalidation/warming, miss fill, and metadata-only values in `services/orchestrator/tests/unit/test_l1_entity_cache.py`. (T029; FR-008)
- [x] T032 [US-021] [L1] Implement the bounded process-local cache in `services/orchestrator/app/services/l1_entity_cache.py` and refresh it from `l1_graph` only after successful FalkorDB persistence; never store source bodies. (T018–T020, T031; FR-008)
- [x] T033 [P] [US-021] [API] Extend `services/orchestrator/tests/contract/test_context_contract.py` and add `services/orchestrator/tests/integration/test_context_l1_structural.py` for unchanged response fields, cited evidence, cache hit, stale/unavailable fallback, unsupported/blast decline, and no fabricated evidence. (T030–T032; FR-008)
- [x] T034 [US-021] [API] Add local structural-intent/entity matching and a delimited cited evidence block to existing `POST /context` in `services/orchestrator/app/api/context.py`; use only existing `final_context` and `metrics.trace`, preserve L5 output on all L1/cache failures, and add no blast computation. (T032–T033; FR-008)
- [x] T035 [P] [US-021] [MCP] Extend `clients/mcp/tests/formatAskPack.test.ts` only as needed to prove `contextos_ask` passes the enriched existing response through without graph/cache persistence or a new MCP tool. Add and execute the opt-in grounding/cache/latency harness at `services/orchestrator/tests/eval/test_l1_structural_queries.py`; measurements are synthetic in-process evidence only. (T030, T034; FR-008; SC-003)

**Checkpoint**: US-021 is independently complete only when cited grounding, cache lifecycle, L5 degradation, stateless MCP, and blast exclusion have executed evidence.

## Phase 5: Polish, Documentation, and Validation Evidence

- [x] T036 [P] [L1] Update L1 data-store/API documentation only for implemented decisions in `docs/architecture/database-schema.md`, `docs/architecture/api-contract.md`, and `docs/architecture/architecture-overview.md`; retain exclusions for new routes, blast/visualization, and MCP ownership. (FR-001–FR-008)
- [x] T037 [L1] Record executed unit, contract, integration, privacy, Compose, graph/query accuracy, cache, and performance commands/results (including skipped/unavailable cases) in `validation-report.md`; distinguish planned, executed, passed, failed, and skipped. (Constitution IV; FR-001–FR-008)
- [x] T038 [L1] Perform final regression and scope audit: run affected index/context/MCP/privacy/contract suites, confirm no route/field/visualization/RBAC/blast work was added, and verify health behavior remains compatible. Record evidence in `validation-report.md`. (FR-004–FR-008)

## Dependencies and Execution Order

- **Blocking path**: T001–T006 (complete) → T007–T010 → T012–T016 → T017–T022 → T023–T028 → T031–T035 → T036–T038.
- **Parallel work**: T004 and T006 may run in parallel with T001–T003; T011 follows T003/T006 independently. T012–T016 may run in parallel after Phase 2. T025–T028 can run in parallel after T023, subject to required environments.
- **US-017**: T017–T019 follow their respective unit tests; T020 is the integration point; T021–T022 follow T020; acceptance/evidence follows implementation.
- **US-021**: T029–T030 are complete; T031 follows them, T032 follows L1 persistence, T033 precedes T034, and T035 verifies MCP/evaluation after T034.

## Implementation Strategy

1. Resolve the L1 store/schema/parser/operational decisions before adding code.
2. Deliver US-017 through the existing FastAPI index path and stop for independent acceptance, privacy, and deployment verification.
3. Treat timing and graph-accuracy work as reproducible evidence harnesses, not pre-declared pass gates.
4. Deliver US-021 only through FastAPI cache and existing `/context`; preserve stateless MCP and exclude blast.

## Definition of Done

- US-017 satisfies FR-001–FR-007 with executed contract, unit, integration, privacy, and Compose evidence.
- `POST /index` retains its confirmed request/response fields and reports the approved L1 node count.
- Excluded or binary source is never parsed, persisted, logged as source content, or sent to an external LLM during indexing.
- Graph schema/provenance/reconciliation/parser/failure decisions and their test evidence are documented.
- Delta/full timing and graph-accuracy harness outcomes are recorded without unsupported pass claims.
- US-021 returns cited structural evidence through existing `/context`, with verified revision invalidation, L5 degradation, stateless MCP, and blast exclusion.

## Evidence Reviewed

- `.specify/memory/constitution.md`
- `.cursor/rules/lean-spec-kit-artifacts.mdc`
- Latest EP-006 handoff in `.cursor/agent-handoffs/handoff.md`
- `specs/ep-006-l1-structural-graph/spec.md` and `plan.md`
- `services/orchestrator/app/services/l5_index.py`, `app/api/index.py`, `app/api/schemas_index.py`, `app/security/ignore_policy.py`, `app/adapters/fs_walker.py`, `app/telemetry/indexing.py`, `app/config.py`, and `app/api/health.py`
- `deploy/docker-compose.yml`, `services/orchestrator/pyproject.toml`, and the cited index contract, privacy, delta, no-exfiltration, and performance tests

## Open Questions / Discovery Tasks

| Item | Owning tasks | Status |
|---|---|---|
| FalkorDB driver/config/test environment | T001, T004, T007–T008 | Complete; implementation/runtime evidence recorded |
| L1 schema, provenance, count, reconciliation | T002, T013, T018, T024 | Complete; tests and validation evidence recorded |
| Parser coverage and failure behavior | T003, T012, T017 | Complete; tests and fixture accuracy evidence recorded |
| Graph-generation failure behavior | T005, T014, T019 | Complete; unit/failure-path evidence recorded |
| OQ-06 hot-entity cache boundary | T029–T035 | Resolved; implementation and evidence pending |

## Task-Level Coverage Matrix

| Tasks | Source requirement / story | Plan reference | Completion evidence |
|---|---|---|---|
| T001, T004, T007–T008 | FR-002; US-017 | Technical Context; §§117–123, 155–159 | Approved driver/config decision and isolated Compose readiness result |
| T002, T013, T018, T024 | FR-001, FR-002, FR-007; US-017 | Data Model Changes; §123 | Schema/count/reconciliation decision plus adapter and re-index evidence |
| T003, T006, T011–T012, T017, T026 | FR-001, FR-003; US-017 | §§120, 207–210, 237–239 | Declared coverage, fixtures, parser tests, and executed evaluation evidence |
| T005, T014, T019 | FR-004; US-017 | §§123–124, Risks | Approved failure decision and tested behavior |
| T009–T010, T019–T020 | FR-005; US-017 | Confirmed architecture; Components | FastAPI-owned service/adapter boundary and code review |
| T015, T020–T021, T023 | FR-004; US-017 | API Design; §§270–277 | Exact contract regression and `graph_nodes` acceptance evidence |
| T016, T020, T022, T033 | FR-006; US-017 | Privacy/Security; §§185–191 | Exclusion/no-exfil tests and telemetry/scope audit |
| T013, T017–T019, T023 | FR-007; US-017 | Data Model Changes; Testing Strategy | Provenance payload and persisted evidence inspection |
| T022, T027–T028, T032 | SC-001, SC-002, Constitution IV | Performance Considerations; §§232–240 | Timed harness outputs or explicit skip/block evidence |
| T025, T036–T038 | FR-002, FR-004–FR-008 | Phase 5 — Polish | Compose, documentation, regression, and validation evidence |
| T029–T035 | FR-008; US-021 | Approved US-021 design | Cache/query implementation, cited grounding, fallback, stateless MCP, and measured evidence |
