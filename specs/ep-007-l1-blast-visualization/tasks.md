# Tasks: EP-007 L1 Blast Radius & Visualization

**Input**: `specs/ep-007-l1-blast-visualization/spec.md` and `plan.md`  
**Prerequisites**: EP-006 L1 on main (`l1_graph.py`, `falkordb_store.py`, `l1_parser.py`, `l1_structural_query.py`, `l1_entity_cache.py`); IgnorePolicy FastAPI-owned; api-contract §2.3–2.5; ADR-010.  
**Status**: FastAPI US-018/US-019 + API freshness/docs complete (2026-07-29). VS Code US-020 React Flow + US-027 UI complete (2026-07-29). Harness execution / validation-report evidence still open.

**Scope guardrails**: Stories **US-018, US-019, US-020, US-027 only**. Reuse EP-006 L1; **no** L1 parser/index redesign. **OUT**: EP-013 OKF, EP-008 L4, EP-010 L2, EP-011 L6, EP-009 PR bot beyond blast fields. OQ-15 owners → **Proposed** `owners: []` only — do **not** invent Confirmed owners schema, risk algorithm, `db_tables`/`tests_to_run` L2 linkage, `graph.html` auth, or freshness numeric threshold. FastAPI owns blast/graph/policy; MCP thin; `vscode-extension-engineer` owns US-020/US-027 UI. NFR p95/accuracy are **validation targets** — no pass claim without executed harness evidence.

**Format**: `[ID] [P?] [Story?] [Layer/Surface] Description` — `[P]` = safe parallel; story labels map to backlog IDs.

---

## Phase 1: Setup & Discovery (Blocking)

**Purpose**: Lock OpenAPI sketches, Proposed heuristics, fixtures, and harness designs before changing blast/graph routes.

- [x] T001 [L1] [API] Confirm EP-006 fixture `services/orchestrator/tests/fixtures/l1_structural_repo/` indexes via existing `POST /index` with FalkorDB evidence reusable for blast/graph; record revision/path identity rules consistent with EP-006 `source_path` / entity IDs (**Proposed** normalization). Do not redesign `l1_parser.py`. (A-001; FR-002; Plan Phase 0)
- [x] T002 [P] [API] Sketch OpenAPI request/response for Confirmed `GET /blast/{file_name}?repo=` against `docs/architecture/api-contract.md` §2.4: Confirmed fields `direct_dependents`, `transitive`, `db_tables`, `risk` ∈ `{HIGH,MEDIUM,LOW}`, `tests_to_run`; **Proposed** `owners: []` only (OQ-15). Proposed statuses `200` / `404` / `501`. Document in task notes / validation prep — do not invent new Confirmed HTTP envelopes. (FR-001, FR-003; Plan API Design)
- [x] T003 [P] [Viz] [API] Sketch Confirmed `GET /graph.html?repo=` contract vs api-contract §2.5 / ADR-010: vis-network, file nodes, IMPORTS edges, physics off, arrows, node `#64748b`, background `#0f172a`, depth 1–5; auth **NEEDS CLARIFICATION** — local trusted-client draft only. (FR-005; Plan Phase 0)
- [x] T004 [L1] Document **Proposed** L1-only heuristics for incomplete `db_tables` / `tests_to_run` / `risk` (empty arrays or path-derived test candidates; conservative risk enum) without inventing L2 SQL, ownership models, or Confirmed scoring algorithm. Record applicability limits for accuracy harness. (A-004; Plan US-018 §4; Open Questions)
- [x] T005 [P] [Telemetry] Design opt-in blast **latency** harness method: ~10k-node L1 graph, 3-hop queries, record machine/revision/cold-warm/p50/p95; target p95 `<2s` (BRD §10) — **no pass claim** until execution. Target path **Proposed** `services/orchestrator/tests/perf/test_blast_latency.py` (or `tests/eval/`). (SC-001; Constitution IV; Plan Performance harnesses)
- [x] T006 [P] [L1] Design opt-in blast **accuracy** harness: fixture with expected affected-tests set; measure correct-predicted rate vs `>95%` where rules apply (BRD §12); skip/partial if linkage Missing Evidence — **no silent pass**. Target path **Proposed** `services/orchestrator/tests/eval/test_blast_accuracy.py`. (SC-002; Plan Performance harnesses)

**Checkpoint**: Contracts, heuristics, and harness designs agreed; no public blast/graph routes required yet.

---

## Phase 2: Foundational (Blocking)

**Purpose**: Internal FastAPI blast/graph boundaries and privacy reuse that **MUST** land before story implementation.

**⚠️ CRITICAL**: US-018+ blocked until this phase completes.

- [x] T007 [L1] Add **Proposed** blast service boundary in `services/orchestrator/app/services/l1_blast.py` (or equivalent name from plan): resolve `repo` + `file_name` against EP-006 revision-scoped FalkorDB; traverse IMPORTS / structural neighbors; assemble Confirmed FR-08 fields + Proposed `owners: []`. Reuse `falkordb_store.py` query helpers only — **no** persist schema redesign; **no** `l1_parser.py` changes. (FR-001, FR-002, FR-003; Plan Components)
- [x] T008 [P] [L1] Add **Proposed** read/query helpers on `services/orchestrator/app/adapters/falkordb_store.py` for bounded IMPORTS hop traversal (1-hop direct / N-hop transitive, BRD pattern `IMPORTS*1..3` context) returning metadata/path/ids only — no source bodies. (FR-002, FR-009; Plan Technical Approach)
- [x] T009 [P] [API] Add **Proposed** blast schemas/router stubs in `services/orchestrator/app/api/blast.py` (+ schemas module as needed) and register in `services/orchestrator/app/main.py` without inventing Confirmed error envelopes beyond api-contract Proposed codes. (FR-001, FR-008; Plan Components)
- [x] T010 [P] [Security] Confirm reuse of `services/orchestrator/app/security/ignore_policy.py` for any blast/graph serialization path; document that MCP/extension must not reimplement policy (Constitution V). No IgnorePolicy redesign. (FR-008, FR-009)

**Checkpoint**: Service/adapter/router boundaries exist; policy ownership documented; story work can begin.

---

## Phase 3: User Story US-018 — Transitive Blast Radius (P1) 🎯 MVP

**Goal**: Confirmed `GET /blast/{file_name}?repo=` returns FR-08 fields from EP-006 L1; V1 populates existing `POST /context` `blast_radius` when applicable.

**Independent Test**: Index L1 fixture → `GET /blast/...` returns Confirmed fields; blast-intent `POST /context` populates `blast_radius` (not permanently empty for applicable V1 cases); Proposed `owners: []` only.

**Owner surface**: FastAPI orchestrator (MCP thin regression only).

### Tests for US-018

- [x] T011 [P] [US-018] [L1] Unit tests in **Proposed** `services/orchestrator/tests/unit/test_l1_blast.py`: 1-hop vs transitive; depth bounds; empty graph; unknown file; Confirmed field presence; `risk` enum; Proposed `owners: []` only — assert **no** Confirmed owners element schema. (FR-001, FR-003; Plan Unit Tests)
- [x] T012 [P] [US-018] [Security] Unit/integration asserts blast payloads contain **no** full source-byte fields; IgnorePolicy-excluded paths (`.gitignore`, `.env`, secrets, dependency/build, binaries) never appear in dependents/transitive lists. Extend or add beside `services/orchestrator/tests/integration/test_index_no_exfil.py` / **Proposed** `test_blast_no_exfil.py`. (FR-009; Constitution III)
- [x] T013 [P] [US-018] [API] Contract tests in **Proposed** `services/orchestrator/tests/contract/test_blast_contract.py` for OpenAPI/`GET /blast` shape vs §2.4; Proposed `404` unknown repo/file; no new Confirmed HTTP semantics. (FR-001; Plan Testing Strategy)
- [x] T014 [P] [US-018] [API] Extend `services/orchestrator/tests/contract/test_context_contract.py` and `services/orchestrator/tests/integration/test_context_l1_structural.py`: V1 blast-intent populates `blast_radius`; non-blast asks keep prior L5/L1 enrichment; replace permanent `blast_declined` empty expectation for applicable V1 cases without breaking non-blast paths. (FR-004; Plan US-018 §5)

### Implementation for US-018

- [x] T015 [US-018] [L1] Implement traversal + response assembly in `services/orchestrator/app/services/l1_blast.py` using T004 Proposed heuristics for `db_tables` / `tests_to_run` / `risk`; always include Confirmed fields; Proposed `owners: []` only (OQ-15). Bound hop depth. (T007, T008, T011; FR-001–FR-003)
- [x] T016 [US-018] [API] Implement `GET /blast/{file_name}?repo=` in `services/orchestrator/app/api/blast.py`; validate non-empty `repo`/`file_name`; Proposed `404` / `501` per plan; register router in `services/orchestrator/app/main.py`. (T009, T013, T015; FR-001, FR-008)
- [x] T017 [US-018] [API] [L5] Wire V1 `blast_radius` population in `services/orchestrator/app/api/context.py` + `schemas_context.py` and adjust `services/orchestrator/app/services/l1_structural_query.py` so applicable blast asks no longer permanently return `blast_declined` empty `{}`; preserve non-blast L1 enrichment. Do **not** add new response fields. (T014, T015; FR-004)
- [x] T018 [P] [US-018] [Telemetry] Extend orchestrator telemetry (**Proposed** attrs: blast latency, hop depth, node counts — non-sensitive only) from existing `services/orchestrator/app/telemetry/` paths; never log source bodies. (Plan Observability)
- [x] T019 [US-018] [L1] [API] Integration: index EP-006 fixture → live/isolated FalkorDB → `GET /blast` returns Confirmed fields in **Proposed** `services/orchestrator/tests/integration/test_blast_l1.py`; unavailable FalkorDB degrades per Proposed status without new Confirmed envelopes. (T015–T017; FR-001, FR-002)
- [x] T020 [P] [US-018] [MCP] Regression only in `clients/mcp/tests/formatAskPack.test.ts` (and related thin-client tests): Ask pass-through of FastAPI `blast_radius` without MCP-owned blast state or policy. No new MCP blast tool. (FR-008; Constitution V)
- [x] T021 [US-018] [Telemetry] Scaffold opt-in latency harness from T005 (**Proposed** `services/orchestrator/tests/perf/test_blast_latency.py`); mark skip-by-default; document that execution/results belong in validation-report — **no pass assertion** in this task. (SC-001; Constitution IV)

**Checkpoint**: US-018 independently demoable via `GET /blast` + V1 `blast_radius` populate; privacy/contract tests green; latency harness scaffolded (not claimed).

---

## Phase 4: User Story US-019 — Interactive `graph.html` (P1)

**Goal**: Confirmed `GET /graph.html?repo=` serves vis-network over file nodes / IMPORTS edges with Confirmed visual defaults and depth 1–5.

**Independent Test**: Open `GET /graph.html?repo=` against L1-indexed fixture; verify vis-network contracts; Proposed `404` unknown repo.

**Owner surface**: FastAPI (API-served HTML).

### Tests for US-019

- [x] T022 [P] [US-019] [Viz] Unit tests for HTML/payload builder (**Proposed** `services/orchestrator/tests/unit/test_graph_html.py`): physics disabled, arrows, colors `#64748b` / `#0f172a`, IMPORTS-only edges, depth clamp 1–5, no source bodies. (FR-005, FR-009; Plan Unit Tests)
- [x] T023 [P] [US-019] [Security] No-exfil / IgnorePolicy tests for graph serialization — excluded paths absent from node list; payload metadata-only. **Proposed** `services/orchestrator/tests/integration/test_graph_html_no_exfil.py`. (FR-009)
- [x] T024 [P] [US-019] [API] Contract/integration in **Proposed** `services/orchestrator/tests/contract/test_graph_html_contract.py` + integration: `text/html` for indexed repo; Proposed `404` unknown; do not invent Confirmed auth assertions. (FR-005; graph.html auth OQ)

### Implementation for US-019

- [x] T025 [US-019] [Viz] [API] Implement `GET /graph.html?repo=` in **Proposed** `services/orchestrator/app/api/graph.py` (or equivalent static HTML route): load file nodes + IMPORTS from FalkorDB via existing store; embed vis-network with Confirmed defaults; interactive depth 1–5; cap payload size; register in `main.py`. Auth remains **NEEDS CLARIFICATION** — local trusted draft only. (T003, T022–T024; FR-005, FR-008)
- [x] T026 [P] [US-019] [Telemetry] Instrument graph.html serve timing (**Proposed** non-sensitive attrs only). (Plan Observability)
- [x] T027 [US-019] [API] Compose/API smoke: extend **Proposed** path alongside `services/orchestrator/tests/integration/test_l1_compose_smoke.py` or add `test_blast_graph_compose_smoke.py` — API + FalkorDB serve blast + graph.html for fixture. (T019, T025; Plan E2E)

**Checkpoint**: US-019 independently viewable; SC-003 visual/depth contracts demonstrable; no Confirmed auth claim.

---

## Phase 5: User Story US-020 — VS Code React Flow Panel (P2, phaseable)

**Goal**: React Flow Webview panel for dependency/blast visualization over FastAPI-owned data; sanitized IPC; no client policy bypass.

**Independent Test**: With V1 extension features enabled and FastAPI blast/graph available (or mocked), open ContextOS graph/blast panel; interact via React Flow; prove no client-side blast computation or IgnorePolicy bypass.

**Phaseability**: May follow Phase 3–4 API delivery; **remains in epic**. Owner: **vscode-extension-engineer** (FastAPI contracts already shipped).

**Depends on**: US-018 / US-019 contracts (T016, T025) available or mocked.

### Tests for US-020

- [x] T028 [P] [US-020] [VSCode] Vitest (or existing extension test harness) for Webview message sanitize + `no_client_policy_bypass` regression under **Proposed** `clients/vscode/` test paths — extension must not invent blast computation or bypass FastAPI validation/IgnorePolicy. (FR-006, FR-008; Constitution III, V)
- [x] T029 [P] [US-020] [VSCode] Panel interaction tests (mock FastAPI blast/graph): React Flow renders nodes/edges from API payloads; error/empty states handled without fabricating graph evidence. (FR-006; SC-005)

### Implementation for US-020

- [x] T030 [US-020] [VSCode] Add React Flow dependency and **Proposed** Webview panel module under `clients/vscode/src/` (e.g. `webview/` or `providers/graphBlastPanel.ts` + assets); wire command/registration in `clients/vscode/src/extension.ts` / `commands/`. Consume FastAPI blast/graph clients only — extend `clients/vscode/src/api/` as thin HTTP client. (ADR-010; FR-006; Plan Phase 3)
- [x] T031 [US-020] [VSCode] Sanitize Webview↔extension messages and backend responses per Constitution III; document that `graph.html` embedding auth remains **NEEDS CLARIFICATION** if panel embeds HTML vs native React Flow data. Prefer FastAPI JSON blast/graph data for React Flow. (T028, T030; FR-006)
- [x] T032 [US-020] [VSCode] Wire panel to display US-027 staleness signal when freshness metadata indicates drift (hook points only if US-027 metadata not yet final — coordinate with T034–T036). (FR-006, FR-007; A-003)

**Checkpoint**: SC-005 — React Flow panel interacts with FastAPI data without client-owned policy (may land after API phases).

---

## Phase 6: User Story US-027 — Staleness Signaling + Polish (P2)

**Goal**: Clear staleness badge/warning on graph/blast/search DX when freshness metadata indicates drift; clear after delta/full index restores freshness. Threshold remains **NEEDS CLARIFICATION**.

**Independent Test**: Force Proposed freshness/drift signal → badge appears; reindex/restore → badge clears; no Confirmed numeric threshold asserted.

### Tests for US-027

- [x] T033 [P] [US-027] [API] [VSCode] Unit/UX tests: warn when Proposed freshness flag/revision drift set; clear when restored — **Proposed** orchestrator unit path and/or `clients/vscode` presenter tests. Do not assert a Confirmed threshold constant. (FR-007; SC-004; Plan Unit Tests)

### Implementation for US-027

- [x] T034 [US-027] [API] Expose or reuse available freshness signals (e.g. `index_revision`, last index timestamps from existing index flows) as **Proposed** metadata to clients — do **not** invent Confirmed DB table (database-schema §6 remains Proposed). Touchpoints: existing index/context response surfaces only as needed; no OKF changes. (A-002; FR-007; Plan US-027)
- [x] T035 [US-027] [VSCode] Implement staleness badge (or equivalent clear warning) on graph/blast/search developer surfaces in `clients/vscode/src/`; clear on refresh after delta/full index restores freshness. Configurable **Proposed** threshold or boolean flag only. Owner: vscode-extension-engineer. (T033, T034; FR-007; SC-004)
- [x] T036 [US-027] [VSCode] [API] Acceptance: badge appear/clear scenario documented with executed steps in validation-report; freshness threshold labeled **NEEDS CLARIFICATION** — no Confirmed constant. (SC-004)
  - **Extension note (2026-07-29)**: appear/clear scenario steps recorded in handoff + `stalenessPresenter.ts` docstring; validation-report evidence table update may be completed by testing-agent.

### NFR harness execution (measurable validation — no false pass)

- [x] T037 [US-018] [Telemetry] Execute opt-in blast latency harness (T005/T021) at 3-hop / ~10k nodes; record machine, revision, cold/warm, p50/p95 in `specs/ep-007-l1-blast-visualization/validation-report.md`. Pass **only** with executed evidence vs `<2s`; otherwise report measured/skipped — **no false pass**. (SC-001; Constitution IV) — **Executed 2026-07-29**: InMemory 10k/3-hop p95≈9.16ms `<2s` (see validation-report Implementation Evidence); residual: live FalkorDB unmeasured
- [x] T038 [US-018] [L1] Execute opt-in blast accuracy harness (T006) against fixture expected set; report correct-predicted rate vs `>95%` where rules apply; skip/partial if linkage Incomplete; record in validation-report — **no silent pass**. (SC-002; Constitution IV) — **Executed PARTIAL**: path-derived `tests_to_run` P=1.0/R=1.0; L2 `db_tables`/owners/risk Incomplete — **no full SC-002 pass**

### Polish & cross-cutting

- [x] T039 [P] [Security] Final privacy audit: blast + graph.html payloads — IgnorePolicy respected; no source-byte exfil; Webview sanitize covered. Record in validation-report. (FR-009; Constitution III) — **Re-confirmed executed**: `test_blast_no_exfil` + `test_graph_html_no_exfil` + vscode `webview_sanitize` green
- [x] T040 [P] [MCP] [API] Regression: EP-006 index/`graph_nodes`/non-blast structural enrichment; context field set unchanged except `blast_radius` population; MCP thin; **OKF paths untouched** (`okf_generate.py` / `okf_retrieve.py` / OKF tests) — EP-013 out of scope. (FR-008; Out of Scope) — **Re-confirmed**: `git diff` no okf_*; MCP formatAskPack 4/4; EP-006 L1 subset 8 passed / 1 skipped
- [x] T041 [P] Documentation: update `docs/architecture/api-contract.md` §2.4–2.5 only for implemented Confirmed/Proposed decisions; retain OQ-15 / auth / threshold as open; lean notes only — **no** `quickstart.md`, `open-questions.md`, `out-of-scope-notes.md`, or full `docs/design` UI suite. (Lean Spec Kit; Plan Phase 4) — **Spot-checked 2026-07-29**: §2.4–2.5 present; OQ-15/auth/threshold labeled
- [x] T042 Record all executed/skipped harness and story evidence in `specs/ep-007-l1-blast-visualization/validation-report.md`; distinguish planned / executed / passed / failed / skipped. (Constitution IV)

**Checkpoint**: US-027 SC-004 satisfied for presence/clear; NFR harnesses executed or explicitly skipped with evidence; epic ready for review-report after implementation + tests.

---

## Dependencies & Execution Order

### Phase dependencies

| Phase | Depends on | Blocks |
|---|---|---|
| 1 Setup/Discovery | — | Phase 2 |
| 2 Foundational | Phase 1 | All stories |
| 3 US-018 | Phase 2 | US-019 data consumers; US-020 API mocks; harness scaffold |
| 4 US-019 | Phase 2; preferably US-018 store helpers | US-020 graph data; Compose smoke |
| 5 US-020 | US-018 + US-019 contracts (or mocks) | Staleness panel wiring |
| 6 US-027 + polish | Freshness signal + panels as available; harness scaffolds | validation-report / DoD |

### User story dependencies

| Story | Priority | Dependencies |
|---|---|---|
| US-018 | P1 MVP | Phase 2; EP-006 L1 fixture |
| US-019 | P1 | Phase 2; FalkorDB IMPORTS read path |
| US-020 | P2 phaseable | FastAPI blast/graph contracts; EP-004 shell |
| US-027 | P2 | Proposed freshness metadata; surfaces from US-019/020/search DX |

### Parallel opportunities

- T002–T006 after T001 can partially parallelize.
- T008–T010 parallel within Phase 2 after T007 shape agreed.
- T011–T014 parallel before/during early US-018 impl.
- T022–T024 parallel before US-019 impl.
- T028–T029 parallel before US-020 impl.
- T037–T038 parallel after fixtures/harnesses ready; T039–T041 parallel in polish.

### Within-story order

Tests that can fail first → service/adapter → API → integration → harness evidence.

---

## Implementation Strategy

### MVP-first

1. Phase 1–2 foundation  
2. Phase 3 US-018 (`GET /blast` + V1 `blast_radius`) → stop and validate  
3. Phase 4 US-019 (`graph.html`) → validate SC-003  
4. Phase 5 US-020 React Flow (may slip after API; keep tasks)  
5. Phase 6 US-027 + execute/document NFR harnesses  

### Incremental delivery

| Increment | Deliverable |
|---|---|
| A | Blast API + privacy/contract |
| B | graph.html vis-network |
| C | React Flow IDE panel |
| D | Staleness UX + harness evidence |

### Parallel team strategy

| Role | Own |
|---|---|
| FastAPI / L1 | Phases 1–4, T034 API freshness, harnesses T037–T038 |
| vscode-extension-engineer | Phase 5 US-020, US-027 UI T035–T036 |
| MCP | Thin regression T020, T040 only |

---

## Definition of Done

| Criterion | Measure |
|---|---|
| US-018 | Confirmed FR-08 fields on fixture via `GET /blast`; V1 `blast_radius` populate; Proposed `owners: []` only |
| US-019 | Confirmed visual/depth contracts on `graph.html` |
| US-020 | React Flow panel over FastAPI data; sanitize + no policy bypass (phaseable but tasked) |
| US-027 | Badge appear/clear; threshold not invented as Confirmed |
| FR-008 / FR-009 | FastAPI owns policy; IgnorePolicy + no source-byte exfil tests green |
| SC-001 / SC-002 | Harness executed or skipped with recorded evidence — **no false pass** |
| Out of scope | No OKF / L2 / L4 / L6 / L1 parser redesign changes |
| Artifacts | `tasks.md` complete; validation-report after triad; review-report after impl+tests |

---

## Evidence Reviewed

| Artifact | Use |
|---|---|
| `specs/ep-007-l1-blast-visualization/spec.md` | US-018/019/020/027; FR-001–FR-009; OQs |
| `specs/ep-007-l1-blast-visualization/plan.md` | Phases, components, harnesses, exclusions |
| `.cursor/agent-handoffs/ep-007-brief.md` | Phasing + NFR rules |
| `specs/ep-006-l1-structural-graph/tasks.md` | Style / reuse patterns |
| `.specify/memory/constitution.md` | Gates I–V; measurable claims |
| `.specify/templates/tasks-template.md` | Structure |
| `.cursor/rules/lean-spec-kit-artifacts.mdc` | Lean artifacts |
| Orchestrator paths | `main.py`, `context.py`, `schemas_context.py`, `l1_structural_query.py` (`blast_declined`), `falkordb_store.py`, `ignore_policy.py`, L1 services |
| `docs/architecture/api-contract.md` §2.3–2.5; ADR-010; database-schema §3/§6 |
| Graphify | `EP-007 blast graph tasks FastAPI VS Code` |

---

## Open Questions / Discovery Tasks

| Item | Status | Owning tasks | Notes |
|---|---|---|---|
| OQ-15 owners JSON shape | **NEEDS CLARIFICATION** | T002, T011, T015 | Proposed `owners: []` only — **no** Confirmed schema |
| graph.html auth / embedding | **NEEDS CLARIFICATION** | T003, T024, T025, T031 | Local trusted draft; no Confirmed auth |
| Freshness threshold | **NEEDS CLARIFICATION** | T033–T036 | Presence/clear only; Proposed flag/config |
| `db_tables` / `tests_to_run` linkage | Missing Evidence | T004, T015, T038 | L1-only heuristics; harness may skip |
| Risk scoring algorithm | Missing Evidence | T004, T015 | Enum presence required; correctness claims blocked |

---

## Task Traceability Matrix

| Task / Phase | Source requirement | Plan reference | Evidence |
|---|---|---|---|
| T001–T006 Phase 1 | FR-001–005; SC-001/002; OQs | Phase 0 Foundation | Discovery / harness design |
| T007–T010 Phase 2 | FR-001, FR-002, FR-008, FR-009 | Components; Foundational | Service/adapter/router/policy |
| T011–T021 US-018 | FR-001–FR-004, FR-008–FR-009; SC-001 | Phase 1 US-018; Testing | Blast API + context populate + privacy |
| T022–T027 US-019 | FR-005, FR-008–FR-009; SC-003 | Phase 2 US-019 | graph.html vis-network |
| T028–T032 US-020 | FR-006, FR-008; SC-005 | Phase 3 US-020 | React Flow Webview |
| T033–T036 US-027 | FR-007; SC-004 | Phase 4 US-027 | Staleness appear/clear |
| T037–T038 | SC-001, SC-002; Constitution IV | Perf harnesses | Opt-in latency/accuracy evidence |
| T039–T042 Polish | FR-008–FR-009; Out of Scope | Phase 4 polish | Privacy, OKF non-touch, docs, validation-report |

---

## Notes

- Story labels use backlog IDs **US-018 / US-019 / US-020 / US-027** (not generic US1…).
- US-020 tasks stay in this file even if sequenced after FastAPI blast/graph.
- Do not generate `quickstart.md`, adjunct OQ files, or full design-suite docs.
- Label every incomplete contract **Proposed** vs **Confirmed** in implementation notes and validation-report.
