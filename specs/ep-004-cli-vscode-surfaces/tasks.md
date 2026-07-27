# Tasks: EP-004 CLI & VS Code Developer Surfaces

**Input**: Design documents from `/specs/ep-004-cli-vscode-surfaces/`

**Prerequisites**: plan.md, spec.md, constitution I–V, api-contract §2.3 / §6, ADR-007, ep-004-brief; EP-002 / EP-003 cite-only (do **not** re-task L5/L3)

**Tests**: REQUIRED — CLI human ask mapping + grounded output (SC-001); VS Code Ask &lt;3 clicks (SC-003); thin-client boundary (SC-005); visible offline/unindexed failure (NFR-006). SC-002 machine-readable = **Proposed / OQ-10** — no Confirmed schema freeze or invented schema Pass. SC-004 IDE &lt;2s = target; Pass **blocked** until OQ-IDE-2s-Harness.

**Organization**: Setup → Foundational (blocking) → **US-007** → **US-008** → Polish. Stories independently testable after foundation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallel-safe (different files; no incomplete paired deps)
- **[Story]**: `[US007]` | `[US008]`
- **[Layer/Surface]**: `[CLI]` `[VSCode]` `[API]` `[Security]` `[Telemetry]` as applicable
- Exact paths when known; **Discovery** when Proposed/unknown — label **Proposed**; do **not** Confirmed-freeze

## Path Conventions (Confirmed + Proposed)

```text
# Confirmed present — consume / extend
clients/vscode/
  package.json                         # packContext exists; Ask NOT evidenced
  src/api/contextClient.ts             # postContext → POST /context
  src/api/types.ts                     # ContextRequest / ContextResponse
  src/commands/packContext.ts          # Pack Context pattern to reuse
  src/commands/index.ts
  src/extension.ts
  src/providers/packContextPresenter.ts
  src/config.ts                        # contextos.orchestratorBaseUrl
  tests/{pack_context_dx,no_client_policy_bypass}.test.ts

services/orchestrator/app/api/context.py   # POST /context owner — consume only

# Proposed (not present)
clients/cli/                           # contextos CLI — discovery/scaffold
  (entrypoint / ask)                   # Proposed layout
  tests/                               # Proposed
```

**Out of scope (do NOT schedule)**: JetBrains; other CLI verbs; L1 blast; L4 product; L2/L6; full EP-005; rebuilding L5/L3; new Appendix D endpoints; Confirmed OQ-10 freeze; inventing authn (OQ-01 / A-05); adjunct Spec Kit files.

**OQ-10 label rule**: Machine-readable CLI schema remains **Proposed only**. Tasks may add a Proposed flag/mode stub. Do **not** Confirmed-freeze fields, invent schema Pass criteria, or claim SC-002 Pass on a frozen schema.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Branch readiness, inventory Ask vs Pack gaps, CLI packaging discovery — no story behavior yet.

- [x] T001 [CLI] [VSCode] [API] Verify branch `feature/ep-004-cli-vscode-surfaces` and Confirmed-present modules: `clients/vscode/src/api/contextClient.ts`, `clients/vscode/src/api/types.ts`, `clients/vscode/src/commands/packContext.ts`, `clients/vscode/package.json`, `services/orchestrator/app/api/context.py` — document gaps (plan Project Structure; A-EP004-1)
- [x] T002 [P] [Discovery] [CLI] Confirm **no** CLI package under `clients/cli/` (or elsewhere under `clients/`) — record gap; target **Proposed** home `clients/cli/` per `docs/architecture/implementation-guidelines.md` §1 (A-EP004-5; OQ-CLI-Packaging)
- [x] T003 [P] [Discovery] [VSCode] Inventory Ask vs Pack: confirm `contextos.packContext` present and **no** Ask command in `clients/vscode/package.json` / `src/commands/` — record gap for US-008 (spec Edge Cases)
- [x] T004 [P] [Discovery] [API] Confirm Confirmed `POST /context` fields vs `clients/vscode/src/api/types.ts` (`query`, optional `file`, `repo`, `top_k`; response `final_context`, `metrics`, `relevant_files`, …) — consume only; do **not** schedule orchestrator intelligence changes (FR-002, FR-009; ADR-009)
- [x] T005 [P] [Discovery] Record EP-004 OQs in-file only (no standalone open-questions.md): **OQ-10**, OQ-IDE-2s-Harness, OQ-Ask-DX, OQ-CLI-Human-Format, OQ-01, OQ-CLI-Packaging — mark blocking impact per spec/plan; **do not invent resolutions**
- [x] T006 [P] [Discovery] [OQ-CLI-Packaging] Document **Proposed** CLI language/runtime/installer options under `clients/cli/` (e.g. TypeScript vs Python) without Confirmed-freezing packaging — pick one Proposed recommendation for scaffold (plan Phase 0)
- [x] T007 [P] [Discovery] Verify EP-001 indexed-workspace + EP-002/EP-003 `POST /context` usable for e2e fixtures — **cite** `specs/ep-001-*` / `ep-002-*` / `ep-003-*` only; do **not** re-task hybrid search, phase templates, or Serena policy (FR-009; A-EP004-1/2/3)

**Checkpoint**: Inventory + OQ register done; no ask behavior required

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared thin-client foundations before US-007 / US-008. **No** new Confirmed HTTP endpoints; **no** L5/L3 rebuild.

**⚠️ CRITICAL**: User-story phases MUST NOT start until this phase completes

- [x] T008 [CLI] [Discovery] Finalize **Proposed** scaffold plan for `clients/cli/` (entrypoint name, module layout, how to invoke `contextos ask`) from T006 — still **Proposed**; adjust path if discovery finds better evidenced home (A-EP004-5)
- [x] T009 [P] [CLI] Scaffold empty **Proposed** package tree under `clients/cli/` (entrypoint stub + `tests/` placeholder) — no ask logic yet
- [x] T010 [P] [VSCode] Confirm reuse of `postContext` in `clients/vscode/src/api/contextClient.ts` and settings via `clients/vscode/src/config.ts` (`contextos.orchestratorBaseUrl`) for Ask — no second HTTP client invent (FR-008; NFR-005)
- [x] T011 [P] [Security] Confirm boundary baseline: extend plan for `clients/vscode/tests/no_client_policy_bypass.test.ts` + **Proposed** CLI boundary checks — clients MUST NOT implement pack/search/symbol/ignore/consent locally (FR-010; SC-005; constitution V)
- [x] T012 [P] [Discovery] [OQ-10] Document machine-readable ask as **Proposed only** (candidate flag names e.g. `--json` / `--format` **Proposed**) — MUST NOT invent Confirmed schema fields or Pass criteria for frozen schema (FR-003; SC-002; SC-006)
- [x] T013 [P] [Discovery] [OQ-Ask-DX] Document **Proposed** gesture candidates (command palette ± keybinding ± context menu) that can satisfy &lt;3 clicks — do not Confirmed-freeze UX fixture yet (FR-006; SC-003)
- [x] T014 [P] [Discovery] [OQ-IDE-2s-Harness] Document SC-004 / NFR-001 Pass as **blocked** without composed harness evidence (shared with EP-002/EP-003) — deliver Ask surface; do not invent Pass (constitution IV)
- [x] T015 [P] [API] Explicitly confirm **no** new Appendix D routes for EP-004 — orchestrator work limited to consume / bugfix if contract broken (`services/orchestrator/app/api/context.py`) (plan API Design; ADR-009)

**Checkpoint**: CLI scaffold + extension reuse confirmed + OQ-10/Ask-DX/harness notes recorded; stories unblocked

---

## Phase 3: User Story 1 — CLI `contextos ask` (US-007) (Priority: P1) 🎯 MVP

**Goal**: Scriptable `contextos ask '<query>'` returns useful human-readable, context-grounded output via thin `POST /context` client (BO-04; FR-001..005, FR-010).

**Independent Test**: With CLI installed and orchestrator reachable against an indexed repo, run `contextos ask 'where is X?'` (or equivalent) and verify useful human-readable grounded output. Machine-readable verified only as **Proposed** (OQ-10) — no schema Pass invent.

**Layers/Surfaces**: `[CLI]` `[API]` `[Security]`

### Clarification / Discovery (US-007)

- [x] T016 [US007] [Discovery] [OQ-CLI-Human-Format] Document **Proposed** human output layout (sections for `final_context` / relevant files) — Confirmed intent “useful”; exact layout Missing Evidence (FR-001)
- [x] T017 [US007] [Discovery] [OQ-10] Reaffirm machine mode remains Proposed; human-readable ships without Confirmed schema freeze (FR-003; A-EP004-4; SC-006)
- [x] T018 [US007] [Discovery] Confirm FR-005: only `ask` verb required — do **not** schedule other CLI verbs (api-contract §6 Missing Evidence taxonomy)

### Tests for User Story 1 (write first; expect fail/red until implementation)

- [x] T019 [P] [US007] [Unit] Write tests that CLI ask maps args → Confirmed `ContextRequest` fields (`query`, optional `file`/`repo`/`top_k`) under **Proposed** `clients/cli/tests/` — no local search/pack (FR-002; SC-005)
- [x] T020 [P] [US007] [Unit] Write tests for human-readable renderer covering non-empty `final_context` / relevant files presentation under **Proposed** `clients/cli/tests/` (FR-001; SC-001; OQ-CLI-Human-Format Proposed)
- [x] T021 [P] [US007] [Unit] Write tests that unreachable orchestrator / non-2xx surfaces visible failure (exact copy **Proposed**) under **Proposed** `clients/cli/tests/` (NFR-006)
- [x] T022 [P] [US007] [Security] Write boundary tests asserting CLI has no local hybrid search / phase packing / symbol policy / ignore engine (FR-002, FR-010; SC-005)
- [x] T023 [P] [US007] [OQ-10] Add **Proposed-only** tests that a machine-readable flag/mode exists when planned — assert flag wiring / smoke serialization **without** Confirmed field inventory or schema Pass criteria (FR-003; SC-002; SC-006)
- [x] T024 [US007] [Acceptance] Add acceptance checklist/fixture note for SC-001: `contextos ask 'where is X?'` → useful human-readable grounded output against mocked or live `POST /context` — do **not** invent CLI p95 Pass (FR-004; SC-001)

### Implementation for User Story 1

- [x] T025 [US007] [CLI] Implement `contextos ask` command under **Proposed** `clients/cli/` accepting natural-language query (illustrative: `contextos ask 'where is X?'`) (FR-001)
- [x] T026 [US007] [CLI] [API] Implement thin HTTP client calling Confirmed `POST /context` with `query` + optional `file`/`repo`/`top_k` — FastAPI owns intelligence (FR-002; api-contract §2.3 / §6)
- [x] T027 [US007] [CLI] Implement human-readable renderer of context result per T016 Proposed layout (FR-001; SC-001)
- [x] T028 [P] [US007] [CLI] [OQ-10] Implement optional **Proposed** machine-readable mode stub (flag name Proposed) — serialize ask result as **Proposed** only; do **not** Confirmed-freeze schema or invent schema Pass gates (FR-003; SC-002; SC-006)
- [x] T029 [US007] [CLI] Surface visible errors when orchestrator unreachable or request fails (Proposed copy) (NFR-006; FR-010)
- [x] T030 [US007] [CLI] Ensure no other CLI verbs are required/shipped for this epic (FR-005)
- [x] T031 [US007] Document install/run notes for `contextos ask` in package README or `--help` only — **no** Spec Kit adjunct files (lean rule)

**Checkpoint**: US-007 independently delivers human CLI ask via `POST /context`. SC-001/SC-005 addressable; SC-002 Proposed-only (OQ-10); no invented CLI SLA (FR-004).

---

## Phase 4: User Story 2 — VS Code Ask ContextOS &lt;3 Clicks (US-008) (Priority: P1)

**Goal**: Ask ContextOS entry in VS Code completes initiation in &lt;3 clicks; results via `postContext` / Pack Context DX patterns; no L5/L3 policy in extension (BO-01; FR-006..010).

**Independent Test**: With extension installed and connected to indexed workspace, invoke Ask ContextOS and verify initiation &lt;3 clicks (SC-003). On success, context suitable for MVP exit target; SC-004 Pass blocked without OQ-IDE-2s-Harness evidence.

**Layers/Surfaces**: `[VSCode]` `[API]` `[Security]` `[Telemetry]`

**Depends on**: Foundational (T010+). Independently testable from CLI (US-007) via mocks if needed.

### Clarification / Discovery (US-008)

- [x] T032 [US008] [Discovery] [OQ-Ask-DX] Select **Proposed** gesture sequence from T013 that meets &lt;3 clicks (e.g. palette command alone = 1–2 gestures) — document click-count fixture; keep OQ open until UX freeze (FR-006; SC-003)
- [x] T033 [US008] [Discovery] Confirm Ask is **distinct** from Pack Context (`contextos.packContext`) — do not re-spec Pack; Proposed Ask ID e.g. `contextos.askContext` (plan Complexity; A-EP004-6)
- [x] T034 [US008] [Discovery] [OQ-IDE-2s-Harness] Confirm latency instrumentation allowed; Pass claims for SC-004 remain **blocked** without harness (FR-007; NFR-001)

### Tests for User Story 2 (write first; expect fail/red until implementation)

- [x] T035 [P] [US008] [VSCode] Write vitest for Ask command registration + `postContext` / `ContextRequest` build only in `clients/vscode/tests/ask_context_dx.test.ts` (mirror `pack_context_dx.test.ts`) (FR-008; SC-005)
- [x] T036 [P] [US008] [VSCode] Write vitest / fixture asserting Ask initiation path satisfies &lt;3 clicks per T032 Proposed sequence in `clients/vscode/tests/` (FR-006; SC-003) — document gesture count; do not invent unstated extra NFRs
- [x] T037 [P] [US008] [Security] Extend `clients/vscode/tests/no_client_policy_bypass.test.ts` (or sibling) so Ask path MUST NOT reimplement pack/search/symbol/ignore/consent (FR-008, FR-010; SC-005)
- [x] T038 [P] [US008] [VSCode] Write tests for visible failure when orchestrator unreachable / request fails (Proposed copy) in `clients/vscode/tests/ask_context_dx.test.ts` (NFR-006)
- [x] T039 [US008] [OQ-IDE-2s-Harness] Add **blocked** placeholder for SC-004 &lt;2s symbol-accurate measurement (instrumentation hook OK) — MUST NOT invent Pass/Fail without harness evidence (FR-007; NFR-001; constitution Verification Gate)

### Implementation for User Story 2

- [x] T040 [US008] [VSCode] Implement Ask command module (Proposed path `clients/vscode/src/commands/askContext.ts`; Proposed ID `contextos.askContext`) calling `postContext` from `clients/vscode/src/api/contextClient.ts` — DX only (FR-008)
- [x] T041 [US008] [VSCode] Implement Ask result presenter reusing Pack Context patterns (Proposed `clients/vscode/src/providers/askContextPresenter.ts` or shared presenter) — no local packing (FR-008; A-EP004-6)
- [x] T042 [US008] [VSCode] Register Ask in `clients/vscode/src/commands/index.ts` + `clients/vscode/src/extension.ts`
- [x] T043 [US008] [VSCode] Add Ask contributes to `clients/vscode/package.json` (command title + optional keybinding/menu per T032) so initiation &lt;3 clicks (FR-006; SC-003; OQ-Ask-DX Proposed)
- [x] T044 [US008] [VSCode] Prompt/collect natural-language query (palette InputBox or selection bias) → map to Confirmed `ContextRequest` via existing types in `clients/vscode/src/api/types.ts` (FR-008, FR-009)
- [x] T045 [US008] [VSCode] Surface visible errors for offline/unindexed/failed ask (Proposed copy) (NFR-006; FR-010)
- [x] T046 [P] [US008] [Telemetry] Add **Proposed** client-side latency logging for Ask success path (names Proposed) — supports SC-004 measurement later; orchestrator OTel remains EP-002/003 cite-only (plan Telemetry)
- [x] T047 [US008] Verify Pack Context + L3 commands unchanged (`contextos.packContext`, definition/references/rename) — regression boundary (SC-005; FR-009)

**Checkpoint**: US-008 independently delivers Ask &lt;3 clicks via thin `POST /context`. SC-003/SC-005 addressable; SC-004 Pass gated on harness.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Boundary governance, regression, deployment readiness — no new product scope.

- [x] T048 [P] [Security] Boundary review checklist: CLI + extension are thin clients of `POST /context`; no client-side pack/search/symbol policy (SC-005; FR-002, FR-008, FR-010; constitution V)
- [x] T049 [P] [Governance] Verify **OQ-10** still open — no Confirmed schema freeze in code/docs/tests Pass criteria (SC-006; FR-003)
- [x] T050 [P] [CLI] [VSCode] Regression: Pack Context + L3 DX + `services/orchestrator/app/api/context.py` contract consume-only — no new Confirmed endpoints (FR-009; ADR-009)
- [x] T051 [P] Smoke: human `contextos ask` + VS Code Ask happy-path against mocked or loopback orchestrator (A-05) — document blocked e2e if unindexed (A-EP004-3)
- [x] T052 [P] [Discovery] Confirm no JetBrains / other-CLI-verbs / L1/L4/L2/L6 / EP-005 expansion landed in this epic (spec Out of Scope)
- [x] T053 [P] Docs: update extension contribution titles / CLI `--help` only as needed — **no** quickstart / open-questions / out-of-scope-notes / `docs/design/ep-004-*` adjuncts
- [x] T054 Deployment readiness: document local loopback run assumptions (A-05); secrets stay out of repo; reuse `contextos.orchestratorBaseUrl` patterns (NFR-004, NFR-005)
- [x] T055 Carry open OQs (OQ-10, OQ-IDE-2s-Harness, OQ-Ask-DX, OQ-CLI-Human-Format, OQ-01, OQ-CLI-Packaging) into validation-report notes — no invented Pass

**Checkpoint**: EP-004 surfaces ready for Spec Kit validation; OQ-10 remains Proposed-only

---

## Dependencies & Execution Order

### Phase dependencies

| Phase | Depends on | Notes |
|-------|------------|-------|
| 1 Setup | — | Start immediately |
| 2 Foundational | Phase 1 | **Blocks** US-007 / US-008 |
| 3 US-007 | Phase 2 | MVP CLI; independent of US-008 |
| 4 US-008 | Phase 2 | Can parallel US-007 after foundation |
| 5 Polish | US-007 + US-008 desired complete | Boundary + OQ carry-forward |

### User story dependencies

| Story | Depends on | Parallel? |
|-------|------------|-----------|
| US-007 | Foundational | Yes vs US-008 after Phase 2 |
| US-008 | Foundational; reuses `contextClient` / Pack patterns | Yes vs US-007; e2e needs EP-001/002/003 |

### Within-story order

1. Discovery / OQ notes → 2. Tests (red) → 3. Implementation → 4. Checkpoint

### Parallel opportunities

- Phase 1 `[P]` inventory tasks
- Phase 2 `[P]` discovery + scaffold prep
- After Phase 2: US-007 CLI track ∥ US-008 VS Code track
- Within stories: `[P]` unit/security tests in parallel

---

## Implementation Strategy

### MVP-first

1. Phase 1–2 foundation  
2. Phase 3 US-007 human CLI ask → validate SC-001  
3. Phase 4 US-008 Ask &lt;3 clicks → validate SC-003  
4. Phase 5 boundary + OQ-10 governance  

### Incremental delivery

| Increment | Value |
|-----------|-------|
| CLI human ask | BO-04 / SC-001 |
| VS Code Ask &lt;3 clicks | BO-01 / SC-003 |
| Proposed machine mode | SC-002 Proposed only (OQ-10) |
| IDE &lt;2s Pass | Blocked on OQ-IDE-2s-Harness |

### Parallel team (optional)

- Dev A: `clients/cli/` (US-007)  
- Dev B: `clients/vscode/` Ask (US-008)  
- Shared: boundary tests + OQ-10 non-freeze rule  

---

## Definition of Done

| Criterion | Measure |
|-----------|---------|
| FR-001..010 covered | Tasks + verification present |
| SC-001 | Human CLI ask grounded output verified |
| SC-002 | Proposed machine mode only; **no** Confirmed schema Pass |
| SC-003 | Ask initiation &lt;3 clicks verified per Proposed fixture |
| SC-004 | Target documented; Pass only with harness evidence |
| SC-005 | Boundary review + tests pass |
| SC-006 | OQ-10 not Confirmed-frozen |
| No adjunct Spec Kit files | Only `tasks.md` added this step |
| No L5/L3 rebuild / JetBrains / extra verbs | Scope check T052 |
| Constitution I–V | Thin clients; evidence-first; measurable claims labeled |

---

## Evidence Reviewed

| Artifact | Use |
|----------|-----|
| `specs/ep-004-cli-vscode-surfaces/spec.md` | FR/SC/US/OQs |
| `specs/ep-004-cli-vscode-surfaces/plan.md` | Phases / paths / testing |
| `.specify/memory/constitution.md` | Gates I–V; Task Gate |
| `.cursor/rules/lean-spec-kit-artifacts.mdc` | ONLY tasks.md |
| `.specify/templates/tasks-template.md` | Structure |
| `.cursor/agent-handoffs/ep-004-brief.md` | Scope constraints |
| `clients/vscode/src/api/contextClient.ts`, `types.ts`, `commands/packContext.ts`, `package.json` | Reuse paths; Ask absent |
| `services/orchestrator/app/api/context.py` | Consume owner |
| `docs/architecture/api-contract.md` §2.3 / §6 | CLI → `/context` |
| `docs/architecture/implementation-guidelines.md` §1 | Proposed `clients/cli/` |
| Prior `specs/ep-00*/tasks.md` | Lean style / OQ handling pattern |

---

## Open Questions / Discovery Tasks

| OQ | Task refs | Handling |
|----|-----------|----------|
| **OQ-10** | T005, T012, T017, T023, T028, T049, T055 | Proposed machine mode only; **no** Confirmed schema; **no** invented schema Pass |
| OQ-IDE-2s-Harness | T014, T034, T039, T055 | Instrument OK; Pass blocked |
| OQ-Ask-DX | T013, T032, T043 | Proposed gesture; fixture until freeze |
| OQ-CLI-Human-Format | T016, T020, T027 | Proposed layout; “useful” AC |
| OQ-CLI-Packaging | T002, T006, T008, T009 | Discovery → Proposed scaffold |
| OQ-01 | T005, T055 | A-05 loopback; no invented authn |

---

## Task Traceability Matrix

| Task / Phase | Source Requirement | Plan Reference | Evidence |
|--------------|-------------------|----------------|----------|
| Phase 1 T001–T007 | Setup; FR-009 cite | Phase 0 | Inventory / OQs |
| Phase 2 T008–T015 | Thin-client foundation; FR-010; OQ-10 | Phase 0–1 prep | Scaffold + boundary |
| Phase 3 T016–T031 | FR-001..005, FR-010; SC-001/002/005/006 | Phase 1 US-007 | CLI ask |
| Phase 4 T032–T047 | FR-006..010; SC-003/004/005; NFR-001/006 | Phase 2 US-008 | Ask DX |
| Phase 5 T048–T055 | SC-005/006; NFR-003..005; governance | Phase 3 Polish | Boundary + OQs |
| T023/T028/T049 | FR-003; SC-002; SC-006 | OQ-10 | Proposed machine only |
| T039/T046 | FR-007; NFR-001; SC-004 | OQ-IDE-2s-Harness | Pass gated |
| T022/T037/T048 | FR-002/008/010; SC-005 | Security / Testing | Boundary |
| — | FR-005; Out of Scope | Plan reminder | No extra verbs / JetBrains / L1–L4 / L2/L6 |

---

## Notes

- Story labels: `[US007]` = US-007 CLI ask; `[US008]` = US-008 VS Code Ask
- Do **not** mark tasks complete in this file until implementation evidence exists
- Prefer mocks for surface build when EP-002/003 e2e unavailable (A-EP004-1/2)
- Lean Spec Kit: generate **only** this `tasks.md` for the task-generator step
