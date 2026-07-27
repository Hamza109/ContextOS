# Tasks: EP-003 L3 Symbol & LSP Navigation (Serena)

**Input**: Design documents from `/specs/ep-003-l3-symbol-lsp-navigation/`

**Prerequisites**: plan.md, spec.md, ADR-005, api-contract §3, constitution I–V, EP-001 indexing foundation, EP-002 `POST /context` packing + citations (cite only — do **not** re-task), `clients/vscode` indexing DX patterns

**Tests**: REQUIRED — definition attributes, references + 2-line context + file-type filter, rename-scope analysis (no execution sandbox), Pack Context behavioral safe-edit plan, citation attribute presence (OQ-11), FastAPI↔VS Code boundary, MCP-first transport. SC-002 (99% accuracy) verification is **Proposed design only** until OQ-12 resolves — tasks MUST mark blocked for Pass claims; do **not** invent Pass/Fail execution results or Confirmed measure method. Composed <2s IDE harness (OQ-IDE-2s-Harness) blocked for Pass claims.

**Organization**: Tasks grouped by independently deliverable user story: **US-005 → US-006 → US-009 → US-010** after Setup + Foundational. Setup/foundational scaffolds Proposed L3 modules and consumes EP-001/EP-002 — does not re-plan indexing/search/phase packing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete paired tasks)
- **[Story]**: Maps to user story (`[US005]`, `[US006]`, `[US009]`, `[US010]`)
- **[Layer/Surface]**: Tags such as `[L3]`, `[API]`, `[VSCode]`, `[Security]`, `[Telemetry]`
- Exact paths from plan when known; discovery tasks for OQ unknowns — label **Proposed**; do **not** Confirmed-freeze

## Path Conventions (Confirmed present + Proposed EP-003 modules)

```text
services/orchestrator/app/
  api/context.py                         # EP-002 Confirmed POST /context — consume; Proposed L3 enrichment only
  services/l5_*                          # EP-001/EP-002 — reuse for Pack Context packing (cite only)
  services/l3_symbol.py                  # Proposed NEW — SymbolService (FR-04..06)
  adapters/serena_mcp.py                 # Proposed NEW — Serena MCP client adapter
  security/{ignore_policy.py,consent_gate.py}  # EP-001 reuse — no second ignore engine
  telemetry/symbol.py                    # Proposed NEW — L3 spans (names open)
  config.py, main.py
services/orchestrator/tests/{unit,integration,contract}/
clients/vscode/
  src/extension.ts                       # Confirmed present — register symbol/Pack Context commands
  src/api/indexClient.ts                 # Confirmed present
  src/api/contextClient.ts               # Proposed NEW — Pack Context → POST /context
  src/providers/                         # Proposed NEW — hover / references presentation
  src/commands/                          # Proposed NEW — definition, references, rename-scope, packContext
  src/mcp/                               # Proposed NEW — Serena MCP client wiring (DX only)
  tests/no_client_policy_bypass.test.ts  # Confirmed present — extend for symbol policy
deploy/docker-compose.yml
specs/ep-003-l3-symbol-lsp-navigation/
```

**Out of scope (do NOT schedule as deliverables)**: L1 blast/`GET /blast`/`graph.html`; L4 Headroom product; L2/L6; full EP-004 CLI/Ask epic beyond US-010 Pack Context surface; rename **execution** sandbox (BRD §6); inventing Confirmed symbol REST (api-contract §3); re-tasking EP-001 indexing or EP-002 hybrid/phase/citation schema freeze; JetBrains; `docs/design/*` / quickstart / standalone open-questions.

**Label rule**: OQ-12, OQ-11, OQ-Symbol-REST, OQ-Lang-Set, OQ-Safe-Edit-Shape, OQ-Unresolved-Symbol, OQ-MCP-Fallback, OQ-IDE-2s-Harness, OQ-01 remain **OPEN**. Implementations may use **Proposed** mechanisms only — never Confirmed-freeze Symbol REST, citation JSON, safe-edit schema, language inventory, or accuracy Pass results.

**Transport rule (Proposed MVP)**: MCP-first Option A for FR-04..06 IDE paths; orchestrator MAY call Serena for Pack Context enrichment. Symbol proxy REST is **Proposed / deferred** — not MVP-required (FR-012; SC-009).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm branch + upstream readiness; scaffold Proposed L3 modules without inventing Confirmed symbol REST or freezing OQs.

- [ ] T001 [L3] [API] [VSCode] Verify current branch is `feature/ep-003-l3-symbol-lsp-navigation` and Confirmed-present modules exist: `services/orchestrator/app/services/l5_*.py`, `adapters/qdrant_store.py`, `api/context.py`, `security/ignore_policy.py`, `consent_gate.py`, `clients/vscode/src/extension.ts`, `clients/vscode/src/api/indexClient.ts`, `clients/vscode/tests/no_client_policy_bypass.test.ts` — document gaps if missing (plan Project Structure; A-EP003-2/3)
- [ ] T002 [P] [L3] [Discovery] Confirm via inventory (no app-code invention): **no** existing `l3_*` / `serena_mcp` under `services/orchestrator/app/` — record gap; Proposed modules to create per plan (A-EP003-1 readiness note)
- [ ] T003 [P] [Discovery] [OQ-Symbol-REST] Record MVP transport as **Proposed Option A** (MCP-only for IDE FR-04..06; orchestrator Serena for Pack Context enrichment) — document Option B (Symbol proxy REST) as deferred; do **not** invent Confirmed REST paths or Appendix D claims (FR-012; SC-009; api-contract §3)
- [ ] T004 [P] [Discovery] Record clarification tickets for EP-003 OQs in task/validation notes (in-file only — no standalone open-questions.md): OQ-12, OQ-11, OQ-Symbol-REST, OQ-Lang-Set, OQ-Safe-Edit-Shape, OQ-Unresolved-Symbol, OQ-MCP-Fallback, OQ-IDE-2s-Harness, OQ-01 — **do not invent resolutions**; mark blocking impact per spec/plan Open Questions tables
- [ ] T005 [P] [L3] [API] Scaffold Proposed empty modules: `services/orchestrator/app/adapters/serena_mcp.py`, `services/orchestrator/app/services/l3_symbol.py`, `services/orchestrator/app/telemetry/symbol.py` per plan Project Structure (names **Proposed**)
- [ ] T006 [P] [VSCode] Scaffold Proposed empty folders/modules under `clients/vscode/src/`: `providers/`, `commands/`, `mcp/`, `api/contextClient.ts` (names **Proposed**; IDs like `contextos.packContext` Proposed only)
- [ ] T007 [P] [Discovery] [OQ-Lang-Set] Document **Proposed** small AC fixture language subset for Serena-supported languages until inventory confirmed — do **not** claim language-complete matrix Pass (FR-002)
- [ ] T008 [P] Add/verify pytest stubs for L3 under `services/orchestrator/tests/{unit,integration,contract}/` and vitest layout under `clients/vscode/tests/` aligned to existing EP-001/EP-002 patterns
- [ ] T009 [P] [Discovery] Verify EP-001 indexed-workspace + EP-002 `POST /context` usable for Pack Context fixtures — **cite** `specs/ep-001-*` / `specs/ep-002-*` only; do **not** schedule re-implementation of hybrid search, phase templates, or index policy (FR-010)

**Checkpoint**: Scaffold + OQ register exist; no user-story symbol/Pack Context behavior required yet

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core L3 infrastructure that MUST complete before ANY user-story implementation. Owns Serena adapter skeleton, SymbolService stubs, MCP DX wiring stubs, telemetry skeleton, security reuse — **no** Confirmed symbol REST router.

**⚠️ CRITICAL**: No user story work (Phases 3–6) may begin until this phase is complete

- [ ] T010 [L3] [API] Implement Serena MCP adapter skeleton in `services/orchestrator/app/adapters/serena_mcp.py` with connection/session hooks for definition/references/hover/rename-scope — pin versions where feasible; exact SDK package pins **NEEDS CLARIFICATION** (ADR-005; FR-001, FR-012)
- [ ] T011 [P] [L3] [API] Implement SymbolService skeleton in `services/orchestrator/app/services/l3_symbol.py` with method stubs for definition, references, rename-scope analysis, hover docs — used when orchestrator needs symbols (Pack Context enrichment); no Confirmed REST exposure (FR-011; FR-012)
- [ ] T012 [P] [API] Extend `services/orchestrator/app/config.py` with **Proposed** knobs for Serena MCP endpoint/command/settings — document keys as **Proposed** (not Confirmed product freeze); reuse orchestrator base URL patterns for Pack Context clients
- [ ] T013 [P] [Telemetry] Bootstrap OpenTelemetry-compatible helpers in `services/orchestrator/app/telemetry/symbol.py` with exporter-agnostic span stubs for definition/references/rename-scope/Pack Context composition — exact metric names Missing Evidence; exporter vendor remains open (ADR-011)
- [ ] T014 [P] [Security] Confirm reuse of `services/orchestrator/app/security/ignore_policy.py` and `consent_gate.py` from any Pack Context / enrichment path — EP-003 MUST NOT invent a second ignore engine in extension; reserve RBAC hook comment without inventing roles (FR-013; OQ-01; NFR-003/NFR-004)
- [ ] T015 [P] [VSCode] Wire thin MCP client stub under `clients/vscode/src/mcp/` for Serena DX paths only — no search/index/symbol-policy logic (FR-011; ADR-005)
- [ ] T016 [P] [VSCode] Add **Proposed** `clients/vscode/src/api/contextClient.ts` skeleton that calls Confirmed `POST /context` (EP-002 fields only: `query`/`file`/`repo`/`top_k`) — no local pack/search (FR-010, FR-011)
- [ ] T017 [P] [Security] [VSCode] Extend boundary test plan in `clients/vscode/tests/no_client_policy_bypass.test.ts` (or sibling) to assert extension MUST NOT reimplement search/index/**symbol policy** — fail/red until commands are thin clients (FR-011, FR-013; SC-008)
- [ ] T018 [P] [Discovery] [OQ-MCP-Fallback] Document **Proposed** MCP-unavailable behavior (clear IDE/orchestrator error; optional regex fallback only if labeled Proposed) — do **not** Confirmed-freeze product UX (NFR-006; BRD §13)
- [ ] T019 [P] [Discovery] [OQ-12] Author **Proposed verification design note only** for FR-04 99% accuracy (candidate approaches, fixture needs, evidence format) — MUST NOT invent Confirmed measure method, Pass/Fail results, or claim SC-002 Pass (FR-003; constitution IV / Verification Gate; A-EP003-5)
- [ ] T020 [P] [Discovery] [OQ-IDE-2s-Harness] Document composed <2s symbol-accurate IDE context harness as **blocked** for Pass claims (shared with EP-004 US-008) — EP-003 contributes L3 precision only; do not invent EP-003-only Confirmed SLA Pass (NFR-001)
- [ ] T021 [P] [Discovery] Confirm no Confirmed symbol REST router will be added under `services/orchestrator/app/api/` for MVP — OpenAPI must not claim Appendix D L3 endpoints (FR-012; SC-009)

**Checkpoint**: Foundation ready — Serena adapter + SymbolService stubs + extension MCP/contextClient stubs + OQ discoveries recorded; user stories may begin

---

## Phase 3: User Story 1 — Symbol Definition Lookup (US-005) (Priority: P1) 🎯 MVP

**Goal**: Resolve symbol definitions via Serena MCP returning file:line, signature, and docstring when available; VS Code hover/commands present results without reimplementing symbol-resolution policy.

**Independent Test**: For a Proposed fixture language subset symbol, request definition lookup and verify location includes file:line, signature, and docstring when available. Accuracy vs 99% is **Proposed verification design only** (OQ-12) — no Pass/Fail invent.

**Layers/Surfaces**: `[L3]` `[API]` `[VSCode]` `[Telemetry]` `[Security]`

### Clarification / Discovery (US-005)

- [ ] T022 [US005] [Discovery] [OQ-Lang-Set] Lock AC fixtures to **Proposed** language subset from T007 — keep OQ-Lang-Set open; do not claim 12+ language-complete Pass (FR-002)
- [ ] T023 [US005] [Discovery] [OQ-Unresolved-Symbol] Document MVP unresolved/ambiguous behavior as no/partial definition — **no** L1 blast expand in EP-003 (FR-015; Missing Evidence UX)
- [ ] T024 [US005] [Discovery] [OQ-12] Confirm SC-002 / FR-003 accuracy Pass remains **blocked** until measurement method agreed — only Proposed design from T019 may proceed (constitution Verification Gate)

### Tests for User Story 1 (write first; expect fail/red until implementation)

- [ ] T025 [P] [US005] [Unit] Write unit tests mapping Serena payloads → Definition Result attributes (file:line, signature, docstring when available) in `services/orchestrator/tests/unit/test_l3_definition_mapping.py` — no invented Confirmed REST schema asserts (FR-001; SC-001)
- [ ] T026 [P] [US005] [Unit] Write unit tests for hover/doc presentation mapping without inventing undocumented hover schema fields in `services/orchestrator/tests/unit/test_l3_hover_docs.py` (FR-014)
- [ ] T027 [P] [US005] [Integration] Write integration test (Serena MCP or test double) for definition lookup on Proposed fixture language subset in `services/orchestrator/tests/integration/test_l3_definition.py` (SC-001; FR-001, FR-002)
- [ ] T028 [P] [US005] [VSCode] Write vitest smoke for definition hover/command wiring (thin MCP/client; no policy) in `clients/vscode/tests/definition_lookup_dx.test.ts` (FR-011, FR-013; SC-008)
- [ ] T029 [US005] [Discovery] [OQ-12] Create **blocked** placeholder for 99% accuracy evaluation harness under `services/orchestrator/tests/` (e.g. `tests/eval/test_l3_definition_accuracy_oq12.py` or docs note in test) — MUST document Missing Evidence method; MUST NOT claim Pass/Fail (FR-003; SC-002)

### Implementation for User Story 1

- [ ] T030 [US005] [L3] [API] Implement definition lookup path in `services/orchestrator/app/adapters/serena_mcp.py` + mapping in `services/orchestrator/app/services/l3_symbol.py` returning file:line, signature, docstring when available (FR-001)
- [ ] T031 [P] [US005] [L3] [API] Implement hover/document-symbol passthrough from Serena in SymbolService / adapter without inventing undocumented fields (FR-014)
- [ ] T032 [US005] [VSCode] Implement hover provider in `clients/vscode/src/providers/` presenting Serena-backed definition/hover docs (FR-014; ADR-005)
- [ ] T033 [US005] [VSCode] Implement definition lookup command in `clients/vscode/src/commands/` registered from `clients/vscode/src/extension.ts` — DX only; MCP wiring via `src/mcp/` (FR-011, FR-013)
- [ ] T034 [US005] [Telemetry] Instrument definition-lookup spans via `services/orchestrator/app/telemetry/symbol.py` (Proposed names only)
- [ ] T035 [US005] [API] Ensure unsupported language / unresolved symbol returns clear no/partial result per T023 — Proposed UX only; no L1 expand (FR-002, FR-015)

**Checkpoint**: US-005 independently delivers definition lookup + IDE presentation without requiring references/rename/Pack Context. SC-001/SC-008 partial; SC-002 design-only / Pass blocked (OQ-12).

---

## Phase 4: User Story 2 — Find All References (US-006) (Priority: P1)

**Goal**: Return monorepo references for a resolved symbol with 2 lines before/after call-site context and file-type filter; VS Code owns presentation.

**Independent Test**: For a resolved symbol in an indexed workspace fixture, find-all-references returns refs with ±2 line context; applying a file-type filter yields filtered results (empty filtered set allowed conceptually).

**Depends on**: US-005 resolution identity (definition).

**Layers/Surfaces**: `[L3]` `[API]` `[VSCode]` `[Telemetry]`

### Clarification / Discovery (US-006)

- [ ] T036 [US006] [Discovery] Document empty file-type-filtered set as conceptually valid — exact empty-result contract **Not evidenced**; do not invent Confirmed empty schema (spec Edge Cases)

### Tests for User Story 2

- [ ] T037 [P] [US006] [Unit] Write unit tests asserting reference call-site context window = 2 lines before + 2 after in `services/orchestrator/tests/unit/test_l3_reference_context.py` (FR-004; SC-003)
- [ ] T038 [P] [US006] [Unit] Write unit tests for file-type filter behavior (including empty filtered set) in `services/orchestrator/tests/unit/test_l3_reference_filter.py` (FR-005; SC-004)
- [ ] T039 [P] [US006] [Integration] Write integration test (Serena or double) for monorepo references + 2-line context in `services/orchestrator/tests/integration/test_l3_references.py` (SC-003; FR-004) — assumes indexed workspace fixture (cite EP-001; do not re-task indexer)
- [ ] T040 [P] [US006] [Integration] Write integration test for file-type filter on references in `services/orchestrator/tests/integration/test_l3_references_filter.py` (SC-004; FR-005)
- [ ] T041 [P] [US006] [VSCode] Write vitest for references command/UI presentation + filter control wiring in `clients/vscode/tests/find_references_dx.test.ts` (FR-011; SC-008)

### Implementation for User Story 2

- [ ] T042 [US006] [L3] [API] Implement find-all-references via Serena in `adapters/serena_mcp.py` + `services/l3_symbol.py` including ±2 line call-site context (FR-004)
- [ ] T043 [US006] [L3] [API] Implement file-type filter on reference results in SymbolService (FR-005)
- [ ] T044 [US006] [VSCode] Implement find-references command + results presentation (+ file-type filter UX) in `clients/vscode/src/commands/` / `providers/` — DX only (FR-011, FR-013)
- [ ] T045 [US006] [Telemetry] Instrument references spans via `telemetry/symbol.py` (Proposed names)

**Checkpoint**: US-006 independently delivers references + filter + IDE presentation given US-005 identity. SC-003/SC-004 addressed when tests pass.

---

## Phase 5: User Story 3 — Rename Scope Analysis (US-009) (Priority: P1)

**Goal**: Compute safe rename scope and breaking-change count **before** rename execution; IDE review surface; **no** execution sandbox.

**Independent Test**: Select a symbol; run Serena-backed rename-scope analysis; verify safe scope + breaking-change count (≥0, zero valid); confirm IDE review surface; assert no ContextOS rename-execution/sandbox claim.

**Depends on**: US-005, US-006.

**Layers/Surfaces**: `[L3]` `[API]` `[VSCode]` `[Telemetry]` `[Security]`

### Clarification / Discovery (US-009)

- [ ] T046 [US009] [Discovery] Explicitly confirm rename **execution** / code-execution sandbox remain **out of scope** (BRD §6; FR-007; FR-015) — tasks must not schedule execute/apply-rename product

### Tests for User Story 3

- [ ] T047 [P] [US009] [Unit] Write unit tests that rename analysis produces safe scope + breaking-change count (including zero) in `services/orchestrator/tests/unit/test_l3_rename_scope.py` (FR-006; SC-005)
- [ ] T048 [P] [US009] [Integration] Write integration test for Serena-backed rename-scope analysis on fixture symbol in `services/orchestrator/tests/integration/test_l3_rename_scope.py` (SC-005; FR-006)
- [ ] T049 [P] [US009] [VSCode] Write vitest for rename-scope review surface (presentation only; no execute) in `clients/vscode/tests/rename_scope_dx.test.ts` (FR-007; SC-005)
- [ ] T050 [P] [US009] [Security] Assert no rename-execution/sandbox APIs or UI claiming ContextOS sandbox in extension/orchestrator surfaces (static/boundary check) (FR-007; FR-015)

### Implementation for User Story 3

- [ ] T051 [US009] [L3] [API] Implement rename-scope **analysis** (safe scope + breaking-change count) via Serena in `adapters/serena_mcp.py` + `services/l3_symbol.py` — analysis only (FR-006)
- [ ] T052 [US009] [VSCode] Implement rename-scope review command/view in `clients/vscode/src/commands/` / `providers/` so developer can review prior to executing rename elsewhere — **no** execute/sandbox UX claim (FR-007)
- [ ] T053 [US009] [Telemetry] Instrument rename-scope analysis spans via `telemetry/symbol.py` (Proposed names)

**Checkpoint**: US-009 independently delivers analysis + IDE review without execution. SC-005 addressed when tests pass; sandbox remains out of scope.

---

## Phase 6: User Story 4 — Pack Context & Safe Edit Plan (US-010) (Priority: P1)

**Goal**: VS Code Pack Context (right-click or equivalent) packs relevant context via Confirmed `POST /context` (EP-002) and provides a Serena-informed safe edit plan (behavioral — not whole-file rewrite). Citations: file:line + confidence when present (OQ-11 — no invented JSON).

**Independent Test**: Invoke Pack Context from extension with file/symbol selection; verify packed relevant context + Serena-informed safe edit plan (behavioral intent). When citations present, verify file:line + confidence attributes without inventing Confirmed JSON keys. Extension MUST call FastAPI — no local pack/search/index/symbol policy.

**Depends on**: EP-001/EP-002 upstream (cite); US-005 for symbol-aware enrichment. US-008 Ask <3 clicks is conceptual EP-004 dep — **do not** expand full Ask/CLI epic.

**Layers/Surfaces**: `[L3]` `[L5-consume]` `[API]` `[VSCode]` `[Telemetry]` `[Security]`

### Clarification / Discovery (US-010)

- [ ] T054 [US010] [Discovery] [OQ-Safe-Edit-Shape] Select **Proposed** interim representation for safe edit plan (e.g. structured text / delimited block alongside packed context / IDE presentation) — behavioral intent only; do **not** Confirmed-freeze JSON schema (FR-008; A-EP003-6)
- [ ] T055 [US010] [Discovery] [OQ-11] Confirm citation verification asserts **attributes** file:line + confidence only — reuse EP-002 citation behavior; do **not** invent Confirmed JSON field names (FR-009; cite EP-002 FR-015/016)
- [ ] T056 [US010] [Discovery] Confirm Pack Context consumes EP-001 index + EP-002 `POST /context` without re-specifying hybrid search / phase templates / citation schema — cite specs only (FR-010)

### Tests for User Story 4

- [ ] T057 [P] [US010] [Unit] Write unit tests for safe-edit-plan **behavioral discriminator** (symbol-scoped guidance vs “rewrite entire file” directive) using Proposed interim markers — no invented Confirmed schema keys — in `services/orchestrator/tests/unit/test_l3_safe_edit_plan.py` (FR-008; SC-006)
- [ ] T058 [P] [US010] [Integration] Write integration test: orchestrator Pack Context enrichment path calls SymbolService/Serena and attaches Proposed safe edit plan content without breaking Confirmed `POST /context` fields in `services/orchestrator/tests/integration/test_context_safe_edit_enrichment.py` (FR-008, FR-010, FR-012; SC-006, SC-009)
- [ ] T059 [P] [US010] [Integration] Write integration test: when citations present on packed output, file:line + confidence attributes exist without asserting invented JSON keys in `services/orchestrator/tests/integration/test_pack_context_citations_attributes.py` (FR-009; SC-007; OQ-11)
- [ ] T060 [P] [US010] [VSCode] Write vitest: Pack Context command/context-menu calls `contextClient` → `POST /context`; presents plan; does **not** local-pack/search/index in `clients/vscode/tests/pack_context_dx.test.ts` (FR-008, FR-010, FR-011; SC-006, SC-008)
- [ ] T061 [P] [US010] [Contract] Regression-extend EP-002 `services/orchestrator/tests/contract/test_context_contract.py` for Confirmed field presence after Proposed enrichment — do **not** add invented Confirmed Appendix D fields (FR-010, FR-012)
- [ ] T062 [P] [US010] [Security] Assert Pack Context path cannot bypass orchestrator consent/ignore policy from extension (extend `no_client_policy_bypass` / integration) (FR-013; NFR-003)

### Implementation for User Story 4

- [ ] T063 [US010] [VSCode] Implement Pack Context command / context-menu (`contextos.packContext` or equivalent — **Proposed** ID) in `clients/vscode/src/commands/` registered from `extension.ts` (FR-008)
- [ ] T064 [US010] [VSCode] Complete `clients/vscode/src/api/contextClient.ts` to invoke Confirmed `POST /context` with selection-derived `query`/`file`/`repo`/`top_k` — no local pack/search/index (FR-010, FR-011)
- [ ] T065 [US010] [API] [L3] Implement **Proposed** Serena-informed safe edit plan enrichment on Pack Context / `POST /context` path via `l3_symbol` + `serena_mcp` — must **not** re-spec EP-002 hybrid/phase; do not invent Confirmed new Appendix D response fields (FR-008, FR-010, FR-012; ADR-005)
- [ ] T066 [US010] [VSCode] Present packed context + safe edit plan in IDE (Webview optional; if used, sanitize messages per constitution III) — behavioral FR-008 only (OQ-Safe-Edit-Shape)
- [ ] T067 [US010] [API] Ensure citation attributes file:line + confidence preserved when present via EP-002 citation path — no invented JSON keys (FR-009; OQ-11)
- [ ] T068 [US010] [Telemetry] Instrument Pack Context composition / Serena enrichment spans via `telemetry/symbol.py` and/or reuse `telemetry/context.py` (Proposed names)
- [ ] T069 [US010] [Docs] Document consumer note only: full Ask <3 clicks / CLI ask remain EP-004 — EP-003 delivers Pack Context / safe edit plan surface only (FR-015; A-EP003-4)

**Checkpoint**: US-010 independently verifies Pack Context + behavioral safe edit plan + citation attributes + boundary. SC-006/SC-007/SC-008/SC-009 addressed when tests pass; schemas remain Proposed where OQ-open.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: MCP degraded path notes, boundary/regression, OpenAPI labeling (no invented Confirmed symbol REST), OQ-12/IDE-2s documentation for later validation-report, deploy smoke — no out-of-scope epics.

- [ ] T070 [P] [L3] Implement/verify **Proposed** MCP-unavailable clear error path (orchestrator + IDE) per T018 — optional regex fallback only if labeled Proposed and tested as degraded; no Confirmed fallback Pass invent (OQ-MCP-Fallback; NFR-006)
- [ ] T071 [P] [API] [Docs] Review OpenAPI: Confirmed Appendix D unchanged (no L3 symbol REST); any Proposed proxy (if ever added) explicitly labeled Proposed — prefer none for MVP (FR-012; SC-009)
- [ ] T072 [P] [Security] Verify symbol/Pack Context paths do not walk excluded `.env`/ignored/secrets/binaries via client-side “helpful” reads; inherit EP-001 ignore (NFR-003, NFR-004; constitution III)
- [ ] T073 [P] [Security] Confirm clients cannot bypass orchestrator validation/consent/indexing policy for packing or symbol ops (FR-011, FR-013; SC-008)
- [ ] T074 [P] [Regression] Ensure EP-001 `POST /index` / ignore / no-exfil / consent tests remain green under `services/orchestrator/tests/`
- [ ] T075 [P] [Regression] Ensure EP-002 `POST /context` hybrid/phase/citation tests remain green under `services/orchestrator/tests/`
- [ ] T076 [P] [Regression] [VSCode] Ensure existing indexing DX tests under `clients/vscode/tests/` remain green (`activation_auto_index`, `save_incremental_reindex`, `no_client_policy_bypass`, etc.)
- [ ] T077 [P] [Telemetry] Verify L3 spans emit for definition/references/rename-scope/Pack Context composition via `telemetry/symbol.py` (exporter vendor still open)
- [ ] T078 [Discovery] [OQ-12] Confirm SC-002 remains **Proposed verification design only** in task/validation notes — no invented accuracy Pass/Fail (FR-003; SC-002)
- [ ] T079 [Discovery] [OQ-IDE-2s-Harness] Confirm composed <2s Pass remains blocked until harness agreed with EP-004 — no invented Pass (NFR-001)
- [ ] T080 [P] [Deploy] Docker Compose + local Serena smoke **Proposed** for orchestrator enrichment path (reuse `deploy/docker-compose.yml`) — Serena local process config Proposed; full Ask E2E not required
- [ ] T081 Explicitly confirm out-of-scope exclusions remain unscheduled: L1 blast/FalkorDB/`GET /blast`/`graph.html`; L4 Headroom; L2/L6; rename execution sandbox; Confirmed symbol REST invention; EP-001/EP-002 re-implementation; full EP-004 CLI/Ask; JetBrains; `docs/design/*` / quickstart (FR-015)
- [ ] T082 [P] [Discovery] [OQ-01] Document RBAC/authn schema still Missing Evidence — reserve hook only; local MCP + trusted loopback MAY apply (NFR-005)

**Checkpoint**: Polish complete; ready for validation-report agent with OQ-12 / IDE-2s / schema gaps labeled (no Pass invention)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately on feature branch
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US-005 (Phase 3)**: Depends on Foundational — **MVP path**
- **US-006 (Phase 4)**: Depends on Foundational + US-005 resolution identity
- **US-009 (Phase 5)**: Depends on Foundational + US-005 + US-006
- **US-010 (Phase 6)**: Depends on Foundational + EP-001/EP-002 upstream + US-005 (symbol enrichment); may proceed in parallel with US-009 once US-005 done if staffed carefully
- **Polish (Phase 7)**: Depends on desired user stories complete (prefer all four for full SC coverage)

### User Story Dependencies

```text
Phase 1 Setup
    → Phase 2 Foundational (BLOCKING)
        → Phase 3 US-005 (Definition) 🎯 MVP
            → Phase 4 US-006 (References)
                → Phase 5 US-009 (Rename scope analysis)
            → Phase 6 US-010 (Pack Context + safe edit plan)  [also needs EP-001/EP-002]
                → Phase 7 Polish
```

- **US-005 (P1)**: No dependency on US-006/009/010 — independently testable after Foundational
- **US-006 (P1)**: Needs US-005 symbol identity; independently testable for refs/filter
- **US-009 (P1)**: Needs US-005/006; independently testable as analysis-only
- **US-010 (P1)**: Needs EP-001/EP-002 + US-005; independently testable for Pack Context behavioral plan (US-008 conceptual only)

### Within Each User Story

1. Discovery tasks for open OQs (Proposed only)
2. Tests written (expect fail/red) before or with implementation
3. Adapter/SymbolService before extension DX wiring
4. Orchestrator enrichment before Pack Context presentation
5. Telemetry/docs after core behavior
6. Story checkpoint before next priority dependency

### Parallel Opportunities

| Window | Parallel tasks |
|--------|----------------|
| Phase 1 | T002–T009 (different files / docs) |
| Phase 2 | T010–T021 after T005/T006 scaffold; T017 boundary with T015/T016 |
| US-005 tests | T025–T028 in parallel; T029 OQ-12 blocked placeholder |
| US-005 impl | T030–T031 then T032–T033; T034–T035 parallel |
| US-006 tests | T037–T041 in parallel |
| US-009 tests | T047–T050 in parallel after T046 |
| US-010 tests | T057–T062 in parallel after T054–T056 |
| Polish | T070–T082 largely parallel across files |

### Dependency Graph (summary)

```text
T001–T009 (Setup)
    └─ T010–T021 (Foundational)
           └─ US-005: T022–T035
                  ├─ US-006: T036–T045
                  │      └─ US-009: T046–T053
                  └─ US-010: T054–T069
                         └─ Polish: T070–T082
```

Blocked verification edges (non-blocking for implementation intent):

```text
T019/T024/T029/T078 ──blocks──► SC-002 Pass claims (OQ-12 — Proposed design only)
T020/T079            ──blocks──► composed <2s Pass claims (OQ-IDE-2s-Harness)
T003/T021/T071       ──blocks──► Confirmed Symbol REST freeze (OQ-Symbol-REST)
T007/T022            ──blocks──► language-complete matrix Pass (OQ-Lang-Set)
T054                 ──blocks──► Confirmed safe-edit schema freeze (OQ-Safe-Edit-Shape)
T055/T059/T067       ──blocks──► Confirmed citation JSON freeze (OQ-11)
T018/T070            ──blocks──► Confirmed MCP fallback product Pass (OQ-MCP-Fallback)
```

---

## Parallel Example: User Story 1 (US-005)

```bash
# Launch US-005 tests together (after Foundational):
Task: "Unit definition mapping in services/orchestrator/tests/unit/test_l3_definition_mapping.py"
Task: "Unit hover docs in services/orchestrator/tests/unit/test_l3_hover_docs.py"
Task: "Integration definition in services/orchestrator/tests/integration/test_l3_definition.py"
Task: "VS Code DX smoke in clients/vscode/tests/definition_lookup_dx.test.ts"

# Then implement adapter → SymbolService → extension providers/commands
```

---

## Implementation Strategy

### MVP First (US-005 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundational (CRITICAL)
3. Complete Phase 3 US-005 (definition + hover/command DX)
4. **STOP and VALIDATE**: SC-001 + SC-008 partial; note SC-002 OQ-12 design-only

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US-005 → Test independently → Demo definition lookup
3. US-006 → Test independently → Demo references + filter
4. US-009 → Test independently → Demo rename-scope review (no execute)
5. US-010 → Test independently → Demo Pack Context + safe edit plan
6. Polish → regression + OQ gap documentation

### Parallel Team Strategy

| Role | Ownership |
|------|-----------|
| Backend | `serena_mcp`, `l3_symbol`, optional `POST /context` enrichment, pytest |
| Extension | `providers/`, `commands/`, `mcp/`, `contextClient`, vitest boundary |
| Shared | OQ discovery notes; SC-008 boundary; no Confirmed REST invention |

With two developers after Foundational: A owns US-005→US-006→US-009 orchestrator; B owns extension DX for those stories + starts US-010 `contextClient` after US-005.

---

## Definition of Done

- [ ] All FR-001..FR-015 have implementation + verification coverage (FR-003/SC-002 = Proposed design only until OQ-12)
- [ ] US-005, US-006, US-009, US-010 independently testable at checkpoints
- [ ] FastAPI owns orchestration; VS Code owns DX; extension does not reimplement search/index/symbol policy (SC-008)
- [ ] MCP-first MVP; no invented Confirmed symbol REST (SC-009)
- [ ] Rename execution sandbox not delivered (FR-007/FR-015)
- [ ] EP-001/EP-002 not re-tasked; Pack Context consumes `POST /context` (FR-010)
- [ ] Unit/integration/E2E(smoke)/boundary tests written; fail-then-pass where applicable
- [ ] OQ-12 / OQ-IDE-2s Pass claims explicitly blocked — no invented Pass/Fail
- [ ] Security: ignore inheritance, no silent bypass, no cloud exfil invent for L3
- [ ] Telemetry stubs present (names Proposed)
- [ ] Lean Spec Kit only — no quickstart / open-questions.md / out-of-scope-notes / docs/design
- [ ] Ready for validation-report agent with gaps labeled

---

## Evidence Reviewed

| Artifact | Use |
|----------|-----|
| `specs/ep-003-l3-symbol-lsp-navigation/spec.md` | FR-001..015; US-005/006/009/010; OQs |
| `specs/ep-003-l3-symbol-lsp-navigation/plan.md` | Phases; Proposed modules; testing strategy |
| `.specify/memory/constitution.md` v1.0.0 | I–V; Task/Verification Gates |
| `.cursor/rules/lean-spec-kit-artifacts.mdc` | Lean artifact discipline |
| `.cursor/agent-handoffs/ep-003-brief.md` | Scope lock; OQ checklist |
| `.cursor/agent-handoffs/handoff.md` | Latest plan-generator handoff |
| `.specify/templates/tasks-template.md` | Required task structure |
| `specs/ep-002-l5-hybrid-search-phase-packing/tasks.md` | Lean style model |
| `docs/architecture/implementation-guidelines.md` | `l3_*`, Serena adapter, no intelligence in extension |
| `docs/architecture/api-contract.md` §3 | Symbol REST Proposed / MCP-only |
| ADR-005 / ADR-002 / ADR-007 / ADR-009 / ADR-011 | Serena; boundaries; VS Code; HTTP; OTel |
| Live tree `services/orchestrator/app/**`, `clients/vscode/**` | Confirmed present; no `l3_*` yet |
| `graphify query` (Serena/L3) | Pre-exploration; docs + EP-001/002 nodes; no L3 code |

---

## Open Questions / Discovery Tasks

| OQ | Handling in tasks | Blocks |
|----|-------------------|--------|
| **OQ-12** | T019, T024, T029, T078 — Proposed verification design only | SC-002 Pass claims |
| **OQ-11** | T055, T059, T067 — attribute presence only | Confirmed citation JSON |
| **OQ-Symbol-REST** | T003, T021, T071 — MCP-first Option A | Confirmed REST |
| **OQ-Lang-Set** | T007, T022 — Proposed subset fixtures | Language-complete matrix |
| **OQ-Safe-Edit-Shape** | T054, T057, T065–T066 — behavioral only | Confirmed safe-edit schema |
| **OQ-Unresolved-Symbol** | T023, T035 — no/partial; no L1 expand | Exact UX freeze |
| **OQ-MCP-Fallback** | T018, T070 — Proposed error/degraded | Confirmed fallback product |
| **OQ-IDE-2s-Harness** | T020, T079 — blocked Pass | Composed <2s Pass |
| **OQ-01** | T014, T082 — reserve hooks | RBAC schema |

---

## Task Traceability Matrix

| Task / Phase | Source Requirement | Plan Reference | Evidence |
|--------------|-------------------|----------------|----------|
| Phase 1 Setup T001–T009 | FR-010, FR-012, FR-015; OQs | Phase 0 Setup/Foundation | Branch; scaffold; cite EP-001/002 |
| Phase 2 Foundational T010–T021 | FR-011, FR-012, FR-013; NFR-003/004/006; OQ-12 design | Phase 0; Components | Adapter/SymbolService stubs; boundary |
| Phase 3 US-005 T022–T035 | FR-001, FR-002, FR-003, FR-011, FR-013, FR-014; SC-001/002/008 | Phase 1 US-005 | Definition + hover DX |
| Phase 4 US-006 T036–T045 | FR-004, FR-005, FR-011; SC-003/004 | Phase 2 US-006 | Refs + filter |
| Phase 5 US-009 T046–T053 | FR-006, FR-007, FR-015; SC-005 | Phase 3 US-009 | Analysis only |
| Phase 6 US-010 T054–T069 | FR-008..FR-013; SC-006..009 | Phase 4 US-010 | Pack Context + safe edit |
| Phase 7 Polish T070–T082 | FR-012..015; NFR-001/003/004/006; OQ-12 | Phase 5 Polish | Regression; no Pass invent |
| OQ-12 tasks | FR-003; SC-002 | Testing Strategy harness gaps | Proposed design only |
| Boundary tests | FR-011, FR-013; SC-008 | Security Considerations | `no_client_policy_bypass` extend |
| No Confirmed REST | FR-012; SC-009 | API Design Option A | api-contract §3 |

---

## Notes

- [P] = different files, no incomplete paired-task dependency
- Story labels: `[US005]` `[US006]` `[US009]` `[US010]`
- Layer tags: `[L3]` `[API]` `[VSCode]` `[Security]` `[Telemetry]` (`[L5-consume]` for Pack Context cite-only)
- Prefer MCP-first; never Confirmed-freeze Symbol REST, OQ-11, OQ-12 method, safe-edit schema, or language inventory
- Do **not** invent Pass/Fail for OQ-12 or composed <2s harness
- Commit after each task or logical group when implementing (out of scope for this task-generator artifact)
- Stop at any story checkpoint to validate independently
