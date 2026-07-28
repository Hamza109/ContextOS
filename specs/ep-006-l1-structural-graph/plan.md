# Implementation Plan: EP-006 L1 Structural Graph Generation

**Branch**: `feature/ep-006-l1-structural-graph` | **Date**: 2026-07-28 | **Spec**: [spec.md](./spec.md)

**Input**: Approved feature specification for US-017 and US-021 only.

## Summary

EP-006 adds V1 L1 structural indexing to the existing FastAPI-owned repository index: eligible local source is already filtered by the established ignore/no-exfiltration path, then structural evidence is generated in the approved CodeGraph/GitNexus/tree-sitter/regex direction and persisted in FalkorDB. The only Confirmed public integration is the existing `POST /index` result's `graph_nodes` field; no route or field is added.

US-021 uses a FastAPI-owned revision-scoped hot-entity cache and existing `POST /context` composition. MCP remains stateless, cache/L1 failures preserve L5 context, and blast analysis remains EP-007. OQ-06 is resolved without adding a route or response field.

## Technical Context

**Language/Version**: Python 3.11 / FastAPI (Confirmed current orchestrator).

**Primary Dependencies**: FastAPI and OpenTelemetry API/SDK are installed. Approved implementation dependencies are official `FalkorDB>=1.6.2,<2` and `tree-sitter-language-pack>=1.13.3,<2`; both support Python 3.11. Dependency installation remains an implementation task, not executed discovery evidence.

**Storage**: FalkorDB structural graph (Confirmed V1); local repository filesystem is source of truth. Existing Qdrant L5 index remains an upstream dependency, not an EP-006 data-model change.

**Testing**: pytest is installed; existing unit, integration, contract, and opt-in `perf` layouts are Confirmed. The approved strategy uses an injectable unit fake and isolated per-test FalkorDB graph names; runtime verification remains pending.

**Target Platform**: Local/VPC-friendly Docker Compose POC (Confirmed). EP-006 moves FalkorDB into the default API dependency path, uses a container healthcheck and `service_healthy` ordering, and configures the API with `CONTEXTOS_FALKORDB_URL=redis://falkordb:6379`. Existing health response fields remain unchanged.

**Project Type**: FastAPI orchestrator in a multi-surface monorepo. No client-surface delivery is in scope.

**Performance Goals**: Validation targets only: measure a 100-file L1 delta against `<60s` and a combined L5+L1 1M-LOC full index against `<15 min`. No target is a pass claim until a representative harness executes.

**Constraints**: Preserve `POST /index` request/response contract; apply ignore policy before graph parsing/persistence; no index-time external LLM calls; retain graph provenance; keep FastAPI as policy owner. Graph failures fail the existing index request without new HTTP semantics. Incremental request fields beyond `repo_path`/`repo_name` remain Proposed under OQ-14.

**Scale/Scope**: US-017 (P1) and US-021 (P2) only. Excludes EP-007 blast/visualization, L2, L4, L6, RBAC delivery, JetBrains, dashboards, GitHub Action, CLI, and VS Code changes.

## ContextOS Technical Impact

**Affected Layers**:

| Layer | Plan impact |
|---|---|
| L1 | **Affected.** Generate typed `File→Module→Class→Method→Call` evidence, import relationships, FalkorDB persistence, `graph_nodes`, and FastAPI-owned hot-entity query enrichment. |
| L5 | Dependency only. Reuse its `run_index` orchestration, allowed-file walk, local indexing, Qdrant work, and existing response field. |
| L3 | Dependency only; no Serena/LSP lookup, reference, hover, or rename scope is changed. |
| L2 / L4 / L6 | N/A: no multi-modal links, compression, or persistent memory delivery is authorized. |

**Affected Surfaces**: FastAPI/indexing service and indexing telemetry are affected. Docker Compose/FalkorDB configuration is affected only to the extent required to run L1. CLI, VS Code extension, MCP server, Webviews, dashboards, GitHub Action, `GET /blast`, and `GET /graph.html` are N/A for this plan.

**Data Stores / Services**: FalkorDB is added to the index write path and remains the L1 source of truth; local filesystem and existing security policy provide eligible inputs. Qdrant/local embeddings are unchanged L5 dependencies. FastAPI owns a process-local revision-scoped entity cache; MCP remains stateless.

**Privacy / Security Controls**: Reuse `IgnorePolicy` and `walk_allowed_files` before graph generation; preserve `.gitignore`, `.env`, secret, dependency/build-output, and binary exclusions; assert no external LLM call during indexing; persist provenance without source-content duplication unless an evidenced schema later requires it. RBAC policy/schema is not delivered.

**Observability**: Extend existing spans with L1 parse/persist timing, graph-node count, cache status/hit count, and structural-enrichment timing without source content or excluded filenames. Exact attribute names remain implementation detail; measurements remain unverified until execution.

**Measurable Intelligence Claims**: Index time, graph accuracy, structural-answer grounding, cache effectiveness, and latency require a documented fixture/corpus, method, and executed evidence. None is passed by this plan.

## Constitution Check

| Gate | Status | Evidence / mitigation |
|---|---|---|
| I — Evidence-first traceability | Pass | FR-001–FR-008 and approved implementation decisions map below; runtime and measurement evidence remains pending. |
| II — Six-layer integrity | Pass | L1 is delivered; L5/L3 are dependencies; L2/L4/L6 and client orchestration are excluded. |
| III — Local-first privacy/security | Pass with implementation obligations | Existing filtering/no-exfil precedes L1; provenance is approved; RBAC remains out of scope. |
| IV — Measurable claims | Conditional | Performance/accuracy/cache claims remain validation targets; opt-in harnesses require execution evidence. |
| V — surface boundary discipline | Pass | FastAPI owns indexing, cache, and query policy; MCP remains a thin client; no new endpoint/field is introduced. |
| Roadmap governance | Pass | This is V1 L1; it does not make L1 an MVP blocker or pull V2 work forward. |

**Post-design re-check**: The proposed L1 service/adapter boundary follows `api → security → service → adapter → store`; it adds no route, UI, client policy, or new store. No constitution violation or complexity exception is introduced.

## Project Structure

### Documentation

```text
specs/ep-006-l1-structural-graph/
├── spec.md
├── plan.md
├── tasks.md
└── validation-report.md
```

### Source Code

```text
services/orchestrator/
├── app/
│   ├── api/index.py
│   ├── api/schemas_index.py
│   ├── services/l5_index.py
│   ├── adapters/fs_walker.py
│   ├── security/ignore_policy.py
│   ├── telemetry/indexing.py
│   ├── api/health.py
│   └── config.py
├── tests/
│   ├── contract/test_index_contract.py
│   ├── integration/test_index_*.py
│   └── fixtures/
└── pyproject.toml

deploy/docker-compose.yml
```

**Structure Decision**: Existing FastAPI paths are Confirmed repository evidence. Approved implementation uses the `l1_*` service and FalkorDB/parser adapter paths listed in `tasks.md`, following the existing service/adapter/security/telemetry split.

## Complexity Tracking

Not applicable. The plan introduces no justified constitution violation or avoidable complexity.

## Technical Approach

### Confirmed architecture

1. `POST /index` calls `run_index`; its Confirmed request is `repo_path` and `repo_name`, and its Confirmed response retains exactly `files_indexed`, `graph_nodes`, `embeddings`, and `time_ms`.
2. The current L5 path validates a local repository, calls the no-exfil guard, applies `IgnorePolicy` through packing and `walk_allowed_files`, embeds allowed content locally, and records index telemetry. It currently reports `graph_nodes=0`.
3. EP-006 extends that index flow so L1 receives only the already eligible files, generates the Confirmed typed chain and import evidence, persists it in FalkorDB, and returns the generated node count through the existing `graph_nodes` field.
4. FastAPI owns graph-policy enforcement. FalkorDB is the Confirmed V1 L1 store; CodeGraph/GitNexus/tree-sitter/regex is the Confirmed extraction direction.

### Approved implementation design for US-017

1. Add an L1 graph-generation service invoked by `run_index` after eligible-file discovery and before index result construction. It consumes repository identity plus allowed file paths; it does not independently walk or relax policy.
2. Add a FalkorDB adapter using official `FalkorDB>=1.6.2,<2`, configured by Proposed environment keys `CONTEXTOS_FALKORDB_URL`, `CONTEXTOS_FALKORDB_GRAPH_PREFIX`, and `CONTEXTOS_FALKORDB_TIMEOUT_SECONDS`. The adapter accepts an injectable protocol-compatible fake that captures normalized write/query requests for unit tests.
3. Use `tree-sitter-language-pack>=1.13.3,<2` for Python, JavaScript, TypeScript/TSX, Go, and Java. Normalize parse output into the typed chain and `IMPORTS` relationships. Calls are syntactic callee references, not semantic cross-language resolution. If a supported grammar fails, conservative regex fallback extracts imports only; malformed or unsupported files produce a counted skip and no guessed class/method/call nodes.
4. Keep L5 Qdrant upserts and L1 FalkorDB writes separate, linked only by Confirmed repository/source-location concepts. Do not copy full file bodies into graph storage unless an approved schema requires it.
5. `graph_nodes` is the number of distinct structural nodes generated and successfully persisted for the request after deterministic de-duplication. Re-indexing unchanged input returns the same count and does not duplicate nodes.
6. Parse all eligible input before writes. A FalkorDB connection, parse orchestration, or persistence failure fails the existing index operation through its generic error path; no graph-specific HTTP status or envelope is added. Cache refresh occurs only after a successful graph commit.

### Approved US-021 design

FastAPI owns a bounded process-local LRU+TTL cache of structural entities (defaults: 10,000 entries, 300 seconds), keyed by `(repo, index_revision, entity_id)`. FalkorDB remains the source of truth. A successful L1 commit invalidates the prior repository revision and warms the new revision with File, Module, Class, and Method metadata; misses may query FalkorDB and fill the current revision. Each entry contains entity identity, kind, qualified name, repository, normalized path, line range, revision, and relationship summary—never full source.

Existing `POST /context` performs local structural intent detection and exact/token-normalized entity matching, then appends a delimited cited evidence block inside `final_context`. It adds only non-sensitive status/timing/hit notes to existing `metrics.trace`; no response field or endpoint is added. Cache miss, stale revision, unsupported question, or unavailable FalkorDB falls back to unchanged L5 context. Existing MCP `contextos_ask` remains stateless and simply passes this response through. Blast-radius computation is explicitly declined and remains EP-007 / US-018.

Structural-query evaluation uses a versioned fixture with expected entity IDs/citations. Report grounded-answer precision/recall/F1, cache hit rate after one warm-up pass, and cold/warm p50/p95 latency. These are measurements, not pass claims until executed.

### Remaining non-blocking evidence

- OQ-14 incremental index request contract beyond Confirmed fields.
- Executed Compose, accuracy, cache, and performance results.

## Architecture Impact

| Area | Impact |
|---|---|
| Frontend | N/A. No extension, Webview, visualization, dashboard, CLI, or JetBrains work is authorized. |
| Backend | **Affected.** Extend existing FastAPI-owned index orchestration with an L1 service and FalkorDB adapter (Proposed module names). |
| Database | **Affected.** FalkorDB receives the approved L1 nodes/edges and revision/provenance schema. Qdrant is unchanged. |
| Infrastructure | **Affected.** FalkorDB becomes a healthchecked default API dependency in Compose; runtime smoke evidence is pending. |
| AI Components | No external model. Local L5 embeddings remain unchanged. Structural extraction and entity matching are deterministic/local. |

## Components

| Component | Action | Status / boundary |
|---|---|---|
| `app/services/l5_index.py` | Invoke L1 after policy-allowed discovery, commit graph before cache refresh, and return real `graph_nodes`. | Confirmed extension point; approved sequencing. |
| Proposed `app/services/l1_*` | Create graph extraction/orchestration service. | Proposed naming; must not implement blast/visualization. |
| Proposed `app/adapters/falkordb_*` | Create official-client persistence boundary for L1 graph writes. | Approved behavior; module naming remains internal. |
| Proposed parser adapter(s) | Extract five-language imports and typed structural evidence. | Approved package, coverage, fallback, and precision boundary. |
| `app/api/index.py`, `app/api/schemas_index.py` | Retain existing route/Confirmed fields; update descriptions only if needed to remove the MVP-zero statement. | No new route/field. |
| `app/security/ignore_policy.py`, `app/adapters/fs_walker.py` | Reuse; do not duplicate or bypass. | Confirmed existing enforcement boundary. |
| `app/telemetry/indexing.py` | Record L1 timings/counts through existing index telemetry. | Exact attributes Proposed. |
| `app/config.py`, `deploy/docker-compose.yml`, `app/api/health.py` | Add approved FalkorDB URL/prefix/timeout, default healthchecked service dependency, and preserve health response fields. | Design approved; runtime smoke pending. |
| Test fixtures and existing test suites | Add L1 structural, privacy, contract, integration, and opt-in performance coverage. | Required before claims. |
| Existing MCP integration | Preserve stateless `contextos_ask` pass-through. | Dependency/regression scope only; no MCP state or new tool. |

## Data Model Changes

**Confirmed conceptual additions**: FalkorDB stores `File`, `Module`, `Class`, `Method`, and `Call` structural nodes for an indexed repository, with `IMPORTS` file relationships. Outputs retain repository and source-path/location provenance sufficient to identify their origin.

**Approved persistence contract**:

- Labels: `File`, `Module`, `Class`, `Method`, `Call`.
- Containment/structural edges: `CONTAINS`, `DECLARES`, `MAKES_CALL`; file dependencies use Confirmed `IMPORTS`.
- Every node has `entity_id`, `repo`, `source_path`, `entity_kind`, `qualified_name`, `start_line`, `end_line`, and `index_revision`. Every edge has `repo`, `source_path`, and `index_revision`. Full source is not stored.
- `entity_id` is deterministic from repository identity, normalized source path, entity kind, qualified name, and source range. Repository identity is included in every merge key, preventing cross-repository collisions.
- Full index: parse first, then replace that repository's prior graph snapshot with the new revision. Incremental internal service operation: delete/rebuild evidence owned by affected source paths; deleted paths remove their owned nodes and incident edges. Both paths use deterministic `MERGE` operations and clean stale revision data only after successful persistence.
- `graph_nodes` counts distinct nodes in the successfully persisted request after de-duplication.

**Migration requirements**: No relational migration is required. Existing repositories acquire L1 data on their next full index; no automatic background backfill is authorized. Revision reconciliation follows the approved full/incremental rules above.

## API Design

No new API endpoint or Confirmed field is planned.

| Boundary | Plan |
|---|---|
| `POST /index` request | Preserve Confirmed `{repo_path, repo_name}`. Existing optional `paths`/`files` remain Proposed under OQ-14 and are not required by EP-006. |
| `POST /index` response | Preserve Confirmed `files_indexed`, `graph_nodes`, `embeddings`, `time_ms`; change only `graph_nodes` behavior from current L5 zero to the L1 generation count. |
| Errors | L1 write/generation failures use the existing generic index failure path; no graph-specific HTTP semantics. |
| US-021 | Existing `POST /context` may append a cited L1 evidence block inside `final_context` and trace notes inside existing `metrics.trace`; no new endpoint or field. |

## UI / UX Changes

Not applicable. Graph visualization, `GET /graph.html`, `GET /blast`, Webviews, CLI, and dashboard work belong to excluded EP-007 or other scopes.

## Security Considerations

- **Authentication/authorization**: Authn and RBAC schema are Missing Evidence. RBAC delivery is excluded; L1 must not add a bypass or make authorization claims.
- **Input validation**: Continue existing local-directory and non-empty repository-name validation. Scope-field behavior remains Proposed/OQ-14.
- **Sensitive data**: Run the existing exclusion policy before parsing, buffering, logging, telemetry, or FalkorDB persistence. Graph data must never be derived from `.env`, secret material, binaries, ignored paths, dependencies, or build output.
- **No exfiltration**: Keep the existing index-path invariant that refuses external LLM use. Structural parsing and persistence are local/VPC operations.
- **Provenance/logging**: Persist the approved FR-007 repository/path/range/kind/entity/revision fields while avoiding source bodies, secrets, and excluded filenames in telemetry.
- **US-021**: Cache entries contain structural metadata/provenance only, are repository/revision scoped, expire after 300 seconds by default, and are never persisted by MCP. Failure traces contain status/count/timing only.

## Performance Considerations

- Reuse incremental scope only as currently Proposed under OQ-14; do not claim a new delta contract.
- Avoid a second repository walk and avoid persisting full source text in FalkorDB where structural metadata/provenance is sufficient (the latter is Proposed guidance).
- Instrument parse, graph-persist, and total index durations separately where compatible with the existing OTel span; record counts, not sensitive content.
- Build opt-in benchmark harnesses around a declared 100-file delta fixture and a representative 1M-LOC corpus. Collect machine, dependency availability, fixture revision, warm/cold state, timing, failure/skip reason, and L5/L1 breakdown.
- `<60s` delta and `<15 min` full index are validation targets. Graph accuracy, cache effectiveness, and any latency targets remain unverified without an approved fixture and executed harness.

## Testing Strategy

### Unit Tests

- Parser-output mapping for the typed chain and `IMPORTS` across Python, JavaScript, TypeScript/TSX, Go, and Java fixtures.
- Ignore-policy boundary: excluded files never reach L1 parser/adapter; retain existing `.gitignore`, secret, binary, dependency, and build-output cases.
- L1 service passes repository/provenance identity and reports deterministic node-count semantics.
- FalkorDB adapter request construction, repository isolation, revision replacement, deletion reconciliation, and idempotency using the injectable fake.
- Hot-entity LRU/TTL behavior, revision invalidation, warming, miss fill, and repository isolation.
- No-index-time-exfil guard still rejects external LLM paths.

### Integration Tests

- Index an eligible fixture through `run_index`/`POST /index`; verify persisted typed structural evidence and imports in an isolated FalkorDB instance.
- Re-index a changed eligible scope and verify affected graph data is reconciled according to the then-approved update policy.
- Index invalid, inaccessible, and excluded-path fixtures; verify no L1 graph persistence and existing error behavior, without asserting new HTTP semantics.
- Exercise unavailable/misconfigured FalkorDB only after an approved degradation/failure decision; do not convert current health behavior into an unapproved contract.

### End-to-End Tests

No client E2E test is in scope. A local Compose smoke test may index a fixture with API, Qdrant, and FalkorDB only after configuration is implemented; it validates deployment wiring, not visualization, blast, or MCP/cache behavior.

### Acceptance Tests

- US-017: fixture inspection proves the typed chain/import evidence is stored and `POST /index.graph_nodes` reflects generation.
- US-017: policy-excluded inputs create no structural evidence.
- US-021: seed graph/cache data and verify supported structural questions produce cited entities through `POST /context`; verify stale/unavailable/unsupported/blast cases retain L5 context without fabricated evidence.

### Regression Tests

- Existing `/index` OpenAPI/response-field contract remains exact; L5 Qdrant index and local embedding tests continue passing.
- Existing health behavior remains compatible unless a separately approved health-contract change is made.
- Existing privacy/no-exfil and partial-index/degraded-search tests remain unchanged in intent.

### Performance and evaluation harnesses

- Replace the current skeletal `test_index_perf_delta.py` timing placeholder with a reproducible 100-file L1 delta measurement when a fixture and FalkorDB environment are available.
- Extend the existing full-index skeleton to measure combined L5+L1 1M-LOC indexing when an approved corpus is provided.
- Add graph-accuracy fixtures with expected nodes/edges and publish precision/recall methodology before any accuracy claim.
- Add an opt-in US-021 harness that reports grounded-answer precision/recall/F1, warm cache hit rate, and cold/warm p50/p95 latency without pre-declaring pass thresholds.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Parser extraction is syntactic and language-limited | Incorrect semantic assumptions | Declare five-language coverage, import-only fallback, and syntactic call precision; test fixtures and report accuracy. |
| Graph reconciliation can leave stale evidence if interrupted | Stale L1 evidence | Parse before writes, use revision-scoped deterministic merges, activate/clean revisions only after persistence, and test interruption/re-index paths. |
| FalkorDB Compose/API wiring is currently unimplemented | L1 unavailable in local POC | Implement the approved default healthchecked dependency and preserve existing health fields; verify with T025. |
| L1 adds index latency | Misses validation targets | Timed stage telemetry and opt-in delta/full harnesses; no SLA pass assertion without evidence. |
| Policy bypass leaks excluded source | Security/privacy incident | Consume only `walk_allowed_files` output; test exclusions and no-exfil invariant before graph writes. |
| Process-local cache differs across multiple API workers | Variable hit rate, not incorrect results | FalkorDB remains source of truth; revision keys prevent stale grounding; misses refill locally. Distributed cache is out of scope until deployment evidence requires it. |

## Dependencies

| Dependency | Relationship |
|---|---|
| EP-001 | Upstream existing FastAPI `POST /index`, L5 index orchestration, ignore policy, local embeddings, Qdrant, and current `graph_nodes=0` extension point. |
| EP-002 | Upstream hybrid retrieval; unchanged. |
| EP-003 | Upstream L3/Serena boundary; unchanged. |
| EP-004 | Upstream thin CLI/VS Code surface boundary; no client implementation here. |
| EP-005 | Upstream privacy, health, consent, and degraded-operation boundaries; preserve them. |
| Merged PR #6 | Upstream ContextOS MCP agent wiring only; it does not resolve OQ-06. |
| FalkorDB / approved parser direction | Official client and language-pack versions selected by T001/T003; runtime verification remains an implementation task. |
| OQ-06 | Resolved 2026-07-28 with FastAPI ownership and existing `/context` composition. |

## Implementation Phases

### Phase 0 — Foundation and decisions (completed 2026-07-28)

1. Selected official FalkorDB and tree-sitter language-pack dependencies and five-language initial coverage.
2. Approved the schema, provenance, node count, reconciliation, failure, Compose, fixture, and evaluation contracts.
3. Resolved OQ-06 with FastAPI-owned cache/query composition and stateless MCP.

### Phase 1 — US-017 (P1)

1. Introduce the L1 service/adapter boundary in the existing index flow after existing eligibility filtering.
2. Generate and persist typed structural/import evidence, update `IndexResult.graph_nodes`, and preserve the four-field response contract.
3. Add unit, integration, contract-regression, privacy/no-exfil, and Compose smoke coverage.
4. Instrument L1 timing/counts and implement the delta/full performance harnesses as executable validation tools.

### Phase 2 — US-021 (P2)

Implement the FastAPI-owned entity cache, refresh it after successful L1 commit, and enrich existing `POST /context` with cited structural evidence and explicit L5 fallback. Preserve stateless MCP behavior and exclude blast analysis.

### Phase 3 — Polish / cross-cutting

Document executed harness evidence in the later validation report, including skips/blockers. Preserve partial-index/degraded-search behavior where an approved decision defines it. Do not add EP-007, L2/L4/L6, RBAC, or client/UI work.

## Evidence Reviewed

- `specs/ep-006-l1-structural-graph/spec.md`
- `.specify/memory/constitution.md`
- `.cursor/rules/lean-spec-kit-artifacts.mdc`
- Latest EP-006 blocks in `.cursor/agent-handoffs/handoff.md`
- `docs/BRD_Context_OS.md`: FR-07, FR-10, §5 L1, §10, §14, §15
- `docs/architecture/architecture-decisions.md` ADR-004; `architecture-overview.md`; `database-schema.md`; `implementation-guidelines.md`; `tech-stack.md`; `api-contract.md` §2.2
- Current `POST /index`, L5 index, ignore policy, file walker, indexing telemetry, health, configuration, Compose, and index contract/performance tests
- Upstream EP-001..005 and merged PR #6 as dependencies only

## Planning Assumptions

| ID | Assumption | Status |
|---|---|---|
| A-001 | Eligible repositories remain locally available to the existing `POST /index` path. | Non-blocking; supported by current implementation. |
| A-002 | Existing upstream EP-001..005 and merged PR #6 boundaries remain available without being changed by EP-006. | Non-blocking dependency assumption. |
| A-003 | The approved Compose healthcheck can provision isolated FalkorDB for integration tests. | Implementation assumption; integration remains unverified until the smoke test executes. |

## Open Questions

| ID | Status | Required resolution |
|---|---|---|
| OQ-06 | **Resolved 2026-07-28** | FastAPI owns revision-scoped LRU+TTL cache and `/context` composition; MCP is stateless; stale/miss/unavailable degrades to L5; blast remains EP-007. |
| OQ-14 | Proposed / unresolved | Confirm whether incremental `POST /index` fields beyond `repo_path`/`repo_name` exist; EP-006 does not depend on or confirm them. |
| L1 schema/provenance | Resolved T002 | Approved in Data Model Changes; implementation evidence pending. |
| Parser coverage/failure | Resolved T003 | Five languages, tree-sitter primary, import-only regex fallback; implementation evidence pending. |
| Falkor operation | Resolved T001/T004/T005 | Official client, default Compose dependency, unchanged health fields, fail existing index operation; runtime evidence pending. |

## Requirement Coverage Matrix

| Requirement ID | Planned Implementation | Evidence | Status |
|---|---|---|---|
| FR-001 | US-017 L1 service maps eligible source to typed chain and verifies fixtures. | BRD FR-07, §5 L1; spec | Planned |
| FR-002 | FalkorDB adapter persists approved revision-scoped L1 structural evidence. | ADR-004; BRD §14; T001–T002 | Ready |
| FR-003 | Language-pack parser plus import-only fallback implements declared five-language coverage. | BRD FR-07; ADR-004; T003 | Ready |
| FR-004 | Extend existing `POST /index` and real `graph_nodes`; retain existing request/response fields. | API contract §2.2; current router/service; spec | Planned |
| FR-005 | Keep graph generation/policy in FastAPI services; no client/MCP bypass. | Constitution V; implementation guidelines §§3–5 | Planned |
| FR-006 | Reuse current ignore walker and no-exfil guard before L1 parsing/persistence; regression test exclusions. | Constitution III; current `IgnorePolicy`; spec | Planned |
| FR-007 | Carry approved repository/path/range/kind/entity/revision provenance through L1. | Constitution III; T002; spec | Ready |
| FR-008 | FastAPI-owned revision-scoped entity cache and existing `/context` evidence composition; stateless MCP and L5 degradation. | BRD FR-10; approved OQ-06; spec | Ready |
