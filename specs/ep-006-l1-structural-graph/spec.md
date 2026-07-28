# Feature Specification: EP-006 L1 Structural Graph Generation

**Feature Branch**: `feature/ep-006-l1-structural-graph`  
**Created**: 2026-07-28  
**Status**: Ready for implementation — discovery decisions and OQ-06 approved 2026-07-28  
**Input**: User description: "Deliver EP-006 only: US-017 typed L1 structural graph generation and US-021 hot-entity cache for natural-language structural queries."

## Evidence Classification

| Label | Meaning in this specification |
|---|---|
| **Confirmed** | Supported by the BRD, approved ADRs, architecture, or current repository evidence. |
| **Proposed** | A documented direction that is not a frozen product contract. |
| **Missing Evidence** | A required detail not established by available sources; it is not treated as a requirement. |

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Generate a typed structural graph (Priority: P1)

As a Staff Engineer, I want ContextOS to build and persist a typed File→Module→Class→Method→Call graph while indexing a repository, so that later dependency analysis has pre-indexed structural evidence.

**Why this priority**: US-017 is the V1 L1 foundation for EP-006 and is required before dependent blast-radius or structural-query capabilities can use graph data.

**Independent Test**: Index a repository fixture containing imports and supported structural constructs; inspect the resulting L1 store and index result to verify the typed structural chain is recorded and the Confirmed `graph_nodes` result reflects graph generation.

**Acceptance Scenarios**:

1. **Given** an eligible local repository, **When** indexing is requested through Confirmed `POST /index`, **Then** ContextOS builds and persists the File→Module→Class→Method→Call structural graph in FalkorDB.
2. **Given** source imports in an eligible repository, **When** L1 graph generation runs, **Then** import relationships are represented as structural graph evidence using the approved parser direction.
3. **Given** a 100-file changed scope and an agreed performance harness, **When** incremental L1 indexing is measured, **Then** the observed duration is evaluated against the BRD target of less than 60 seconds; no pass result is implied by this specification.
4. **Given** an invalid, inaccessible, or policy-excluded repository input, **When** indexing is requested, **Then** no structural graph content is created from excluded content and the result follows the existing documented indexing error behavior without defining new HTTP semantics.

---

### User Story 2 — Answer structural questions from hot entities (Priority: P2)

As a Developer, I want natural-language structural questions to use cached hot entities and L1 knowledge, so that I can ask questions such as “where is auth validated?” quickly.

**Why this priority**: US-021 depends on a usable L1 graph. Its FastAPI-owned cache and query boundary was approved on 2026-07-28.

**Independent Test**: Seed an L1 graph and its FastAPI-owned hot-entity cache, submit a supported structural question through existing `POST /context`, and verify the appended structural evidence is grounded in corresponding entities with repository, path, line, entity kind, and index-revision provenance. Verify `contextos_ask` receives the same result without owning cache state.

**Acceptance Scenarios**:

1. **Given** successfully indexed L1 data, **When** a Developer asks a supported location or structural-ownership question through `POST /context`, **Then** FastAPI appends locally retrieved structural evidence to `final_context` with source citations and an index revision.
2. **Given** `contextos_ask` invokes `POST /context`, **When** structural evidence is returned, **Then** the MCP server passes it through and stores no graph or cache state.
3. **Given** a cache miss, stale revision, or unavailable L1 dependency, **When** a structural question is requested, **Then** FastAPI falls back to existing L5 packed context, records a non-sensitive trace note, and does not invent structural evidence.
4. **Given** a blast-radius question, **When** it reaches EP-006 query enrichment, **Then** the enrichment declines it because blast computation remains EP-007 / US-018.

### Edge Cases

- Policy-excluded paths, including `.gitignore` matches, `.env`, secrets, dependency folders, build output, and binaries, must not contribute source content to the graph index.
- Initial parser coverage is Python, JavaScript, TypeScript/TSX, Go, and Java. Tree-sitter is primary; conservative regex fallback extracts imports only after a supported grammar fails. Unsupported files are skipped with counts only, and malformed files never produce class/method/call evidence from regex.
- The `POST /index` incremental request shape beyond its Confirmed `repo_path` and `repo_name` fields remains **Proposed** under OQ-14; EP-006 must not treat additional fields as Confirmed.
- Cache entries are scoped by repository and index revision. A successful L1 commit invalidates the prior repository revision and warms the new revision; misses may be filled from FalkorDB. Stale or unavailable L1 data degrades to L5 context.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: ContextOS MUST generate an L1 structural graph with the Confirmed typed chain File→Module→Class→Method→Call when an eligible repository is indexed. *(US-017; BRD FR-07, §5 L1)*
- **FR-002**: ContextOS MUST persist generated L1 structural graph data in FalkorDB. *(US-017; ADR-004; BRD §14)*
- **FR-003**: ContextOS MUST derive import relationships for L1 graph generation using the approved CodeGraph/GitNexus/tree-sitter/regex direction. *(US-017; BRD FR-07; ADR-004)*
- **FR-004**: ContextOS MUST perform L1 graph generation through the Confirmed `POST /index` indexing behavior and report the Confirmed `graph_nodes` response field. It MUST NOT require a new Confirmed endpoint or request/response field. *(US-017; API contract §2.2; architecture overview §3.3)*
- **FR-005**: FastAPI MUST own L1 indexing and graph-policy enforcement; clients and integrations MUST NOT bypass this ownership. *(Governance; Constitution V; implementation guidelines §§3–4)*
- **FR-006**: L1 graph generation MUST apply repository indexing protections: respect `.gitignore`; exclude `.env`, secrets, build outputs, dependency folders, and binaries; and avoid external LLM source-code exfiltration during indexing. *(Governance; Constitution III; API contract §2.2)*
- **FR-007**: L1 graph nodes MUST retain `repo`, normalized `source_path`, `start_line`, `end_line`, `entity_kind`, deterministic `entity_id`, and `index_revision`; edges MUST retain `repo`, `source_path`, and `index_revision`. Full source bodies MUST NOT be persisted. *(Governance; Constitution III; implementation guidelines §3; approved T002 decision)*
- **FR-008**: FastAPI MUST own the hot-entity cache and structural-query composition. It MUST scope entries by repository and index revision, invalidate the previous revision after a successful L1 commit, ground evidence with FR-007 provenance, and degrade to existing L5 context on a miss/stale/unavailable L1 dependency. MCP MUST remain a stateless thin client of existing `POST /context`. *(US-021; BRD FR-10; approved OQ-06 decision)*

### Key Entities

| Entity | Conceptual attributes / relationship | Evidence status |
|---|---|---|
| Structural graph node | File, Module, Class, Method, or Call with deterministic identity, repository/path/range provenance, and index revision. | Confirmed typed chain; approved T002 persistence contract. |
| Import relationship | A dependency relationship between files in the structural graph. | Confirmed. |
| Index result | Repository indexing outcome including `files_indexed`, `graph_nodes`, `embeddings`, and `time_ms`. | Confirmed API response fields. |
| Hot entity cache entry | Structural metadata keyed by repository, index revision, and entity ID; default bounded LRU+TTL is 10,000 entries / 300 seconds. | Approved OQ-06 implementation contract. |

## ContextOS Impact *(mandatory for this project)*

### Affected Layers

| Layer | Impact | Evidence |
|---|---|---|
| **L1 Structural Knowledge Graphs** | **Affected — Confirmed.** Typed graph generation and hot-entity structural queries. | BRD §5 L1, FR-07, FR-10; ADR-004. |
| **L2 Multi-modal Project Graphs** | **N/A.** No multi-modal ingestion or linking is authorized. | BRD FR-14 is V2; user scope excludes L2. |
| **L3 Symbol & LSP Navigation** | **Dependency only.** Existing L3 may consume L1 expansion later; this feature does not re-spec Serena or MCP. | Implementation guidelines §4; user scope. |
| **L4 Context Compression** | **N/A.** | BRD FR-11–13; user scope excludes L4. |
| **L5 Context Packing & Semantic Search** | **Dependency only.** Existing index and hybrid retrieval remain upstream; this feature extends indexing with L1 graph data without re-specifying L5. | `POST /index` contract; upstream EP-001/EP-002. |
| **L6 Persistent Agent Memory** | **N/A.** FR-10 hot-entity cache is L1, not the V2 persistent-memory layer. | BRD layer definitions; user scope excludes L6. |

### Affected Surfaces

| Surface | Impact | Evidence |
|---|---|---|
| **FastAPI / API** | **Affected — Confirmed.** `POST /index` is the existing indexing path and carries `graph_nodes`; FastAPI owns policy. | API contract §2.2; Constitution V. |
| **MCP integration** | **Dependency only.** Existing `contextos_ask` remains a stateless thin client of `POST /context`; FastAPI owns graph/cache/query policy. | BRD FR-10; Constitution V; approved OQ-06 decision. |
| **CLI** | **N/A.** Existing CLI is an upstream dependency only. | User scope; upstream EP-004. |
| **VS Code extension** | **N/A.** Existing extension behavior is an upstream dependency only. | User scope; upstream EP-004. |
| **Webview / dashboard / visualization** | **N/A.** `GET /blast` and all graph visualization, including `graph.html`, are EP-007. | BRD FR-08–09; ADR-004; user scope. |
| **GitHub Action / CI** | **N/A.** | User scope excludes it. |

### Privacy And Security

- **Confirmed**: The orchestrator enforces index-time repository handling; `.gitignore` is respected and `.env`, secrets, build output, dependency folders, and binaries are excluded.
- **Confirmed**: Indexing must not send source code to external LLM providers; query-time external LLM use requires explicit consent/configuration.
- **Confirmed governance, out of scope**: RBAC per repository path remains a platform requirement but is not delivered by EP-006; role/path/authentication schema is Missing Evidence.
- **Approved**: Source provenance uses the FR-007 fields for nodes and repository/path/revision for edges; full source bodies are excluded.

## Non-Functional Requirements

### Performance

- **Confirmed target, not a pass claim**: A 100-file L1 incremental index is measured against `<60s`; full 1M-LOC indexing is measured against `<15 min` where the combined L5+L1 harness applies. (BRD FR-07, §10)
- **Missing Evidence**: No verified EP-006 harness, dataset, or result supports an indexing-latency pass assertion.
- **Out of scope**: Blast query p95 is EP-007. Structural-answer grounding, cache effectiveness, and latency are measured by EP-006 harnesses but are not claimed as passed before execution.

### Security

- L1 indexing must preserve the Confirmed repository exclusions and no-exfiltration control in FR-006.
- L1 graph provenance must be preserved under FR-007.
- RBAC enforcement design is excluded and cannot be inferred from the confirmed requirement alone.

### Reliability

- Existing health and Compose evidence shows FalkorDB is optional/unused in the current L5 state; EP-006 must not claim a new health contract or availability result without verified evidence.
- L1 generation/persistence failure fails the existing index operation through its existing generic error path; no graph-specific HTTP contract is added. Query cache/L1 failure degrades to L5 context with a trace note.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 — Validation target, not achieved**: With an agreed L1 benchmark harness, a 100-file incremental L1 index is measured against `<60s`. (BRD FR-07, §10)
- **SC-002 — Validation target, not achieved**: With an agreed combined L5+L1 benchmark harness, a 1M-LOC full index is measured against `<15 min`. (BRD §10)
- **SC-003 — Measurement prerequisite**: Graph precision/recall/F1, structural-answer grounding, cache hit rate, and query latency MUST be measured using the approved fixtures and evidence format. No pass claim may be made until those harnesses execute.

## Confirmed Facts

- EP-006 is V1 and is limited here to US-017 and US-021.
- FalkorDB is the approved V1 persistence store for L1; CodeGraph/GitNexus/tree-sitter/regex is the approved graph-generation direction.
- The documented `POST /index` request is `{repo_path, repo_name}` and its response includes `graph_nodes`; current upstream L5 implementation reports `graph_nodes: 0`, so this is an extension point rather than evidence of completed L1 generation.
- FastAPI owns indexing and graph policy. Current upstream health/Compose evidence shows FalkorDB as optional/unused before V1.
- Existing Confirmed routes include `GET /`, `POST /index`, `POST /context`, `GET /blast/{file_name}`, and `GET /graph.html?repo=`; this feature only builds through `POST /index`.

## Assumptions

| ID | Assumption | Blocking? | Rationale |
|---|---|---|---|
| A-001 | Eligible repositories are available locally to the existing indexing path. | Non-blocking | Confirmed `POST /index` is repository-local. |
| A-002 | Upstream EP-001 through EP-005 and merged PR #6 remain available as dependencies. | Non-blocking | They supply existing indexing, hybrid retrieval, client, privacy/health, and MCP-wiring boundaries; none is re-specified here. |

## Dependencies

| Dependency | Status | Boundary |
|---|---|---|
| EP-001 L5 Repository Packing & Indexing | Upstream dependency | Reuse existing `POST /index`, ignore policy, local indexing, and `graph_nodes` response field; do not re-spec L5. |
| EP-002 L5 Hybrid Search & Phase Packing | Upstream dependency | Hybrid retrieval is not changed by EP-006. |
| EP-003 L3 Symbol & LSP Navigation | Upstream dependency | No Serena/MCP contract is added or changed. |
| EP-004 CLI & VS Code Developer Surfaces | Upstream dependency | Clients remain thin; no CLI/extension behavior is specified. |
| EP-005 Privacy Defaults, Health & Consent | Upstream dependency | L1 must preserve existing index policy; no new health contract is specified. |
| Merged PR #6, ContextOS MCP agent wiring | Upstream dependency | Existing MCP calls remain client wiring; it does not resolve the FR-10 FastAPI↔codebase-memory-MCP boundary. |
| OQ-06 | **Resolved 2026-07-28** | FastAPI owns cache/query policy through existing `POST /context`; MCP is stateless; revision invalidation and L5 degradation are required; blast remains EP-007. |

## Out Of Scope

- EP-007 blast-radius analysis (`GET /blast`) and all graph visualization, including `graph.html` and Webviews.
- L4 compression; L2 multi-modal ingestion/linking; L6 persistent memory.
- RBAC implementation, JetBrains, dashboards, GitHub Action/CI, and new CLI or VS Code behavior.
- New HTTP endpoints, index request fields, MCP-owned storage/APIs, or health response fields.
- Any graph accuracy, cache effectiveness, or latency pass assertion without an executed, verified harness.

## Open Questions

| ID | Question | Status | Blocking impact |
|---|---|---|---|
| **OQ-06** | What is the FastAPI↔codebase-memory-MCP contract for FR-10? | **Resolved 2026-07-28**: FastAPI owns a bounded process-local LRU+TTL entity cache (default 10,000 entries / 300 seconds), keyed by `(repo, index_revision, entity_id)`; successful index commits invalidate the prior revision and warm the new one; `POST /context` composes cited evidence; MCP remains stateless; cache/L1 failure degrades to L5; blast is rejected/deferred to EP-007. | Non-blocking; implementation and evaluation tasks are defined in `tasks.md`. |
| OQ-14 | Does incremental `POST /index` use any request fields beyond the Confirmed request, and what is their contract? | Proposed / unresolved | Non-blocking for US-017 intent; no extra field is assumed in this specification. |
| L1 provenance schema | Which persisted fields identify source and generation context? | **Resolved by T002**: FR-007 fields and deterministic IDs; no source bodies. | Non-blocking. |
| L1 parser coverage and failure policy | Which languages and fallback semantics are supported? | **Resolved by T003**: Python, JS, TS/TSX, Go, Java; tree-sitter primary; import-only regex fallback. | Non-blocking. |

## Requirement Traceability

| Requirement ID | Source | Evidence |
|---|---|---|
| FR-001 | US-017 | `docs/backlog/user-stories.md` US-017; BRD FR-07, §5 L1 |
| FR-002 | US-017 | ADR-004; BRD §14; `database-schema.md` §3 |
| FR-003 | US-017 | BRD FR-07; ADR-004; `tech-stack.md` L1 entries |
| FR-004 | US-017 | `api-contract.md` §2.2; BRD Appendix D; `architecture-overview.md` §3.3 |
| FR-005 | Constitution governance | Constitution V; `implementation-guidelines.md` §§3–4 |
| FR-006 | Constitution governance and existing indexing policy | Constitution III; BRD §10; `api-contract.md` §2.2 |
| FR-007 | Constitution governance and approved T002 schema | Constitution III; `implementation-guidelines.md` §3; plan Data Model Changes |
| FR-008 | US-021 | `docs/backlog/user-stories.md` US-021 and OQ-06; BRD FR-10; `architecture-overview.md` §6.3 |

## Specification Validation

- **Coverage**: FR-001–FR-008 are atomic and each is traceable; scenarios cover US-017 and US-021.
- **Boundary check**: L1/FastAPI are affected; L5/L3 and upstream EP-001..005/PR #6 are dependencies only; L2/L4/L6, clients, blast, and visualization are excluded.
- **Evidence check**: Approved implementation decisions are distinguished from unexecuted measurement claims. No new route, response field, MCP-owned policy, blast behavior, or performance pass is asserted.
- **Blocker check**: T001–T006 and OQ-06 are resolved. Implementation evidence remains pending by design.
