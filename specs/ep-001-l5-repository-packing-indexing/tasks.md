# Tasks: EP-001 L5 Repository Packing & Indexing

**Input**: Design documents from `/specs/ep-001-l5-repository-packing-indexing/`

**Prerequisites**: plan.md (required), spec.md (required), architecture under `docs/architecture/` (api-contract, ADR-002/003/008/009/011/012/013, database-schema, implementation-guidelines)

**Tests**: REQUIRED — indexing intelligence claims (SC-001..010; NFR-001..007). Search recall@k and search p95 are **out of scope** (EP-002) and MUST NOT appear as acceptance for this feature.

**Organization**: Tasks are grouped by independently deliverable user story (US-001, US-002, US-011, US-012, US-016) so each story can be implemented and tested independently after foundational work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete paired tasks)
- **[Story]**: Maps to user story (`[US001]`, `[US002]`, `[US011]`, `[US012]`, `[US016]`)
- **[Layer/Surface]**: Tags such as `[L5]`, `[API]`, `[VSCode]`, `[Security]`, `[Telemetry]`
- Exact paths from plan Proposed layout (`services/orchestrator`, `clients/vscode`, `deploy/`) when known; discovery tasks for unknowns

## Path Conventions (Proposed — greenfield)

```text
services/orchestrator/app/{api,services,adapters,security,telemetry}/
services/orchestrator/tests/{unit,integration,contract}/
clients/vscode/{src,tests}/
deploy/docker-compose.yml
specs/ep-001-l5-repository-packing-indexing/
```

Source structure is **not present** in the repository as of plan date; Phase 1 scaffolds the Proposed layout from `docs/architecture/implementation-guidelines.md` §1.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold greenfield orchestrator + extension + deploy skeleton so later stories have a home.

- [x] T001 [L5] [API] Create Proposed monorepo directories `services/orchestrator/app/{api,services,adapters,security,telemetry}/`, `services/orchestrator/tests/{unit,integration,contract}/`, `clients/vscode/src/`, and `deploy/` per plan Project Structure
- [x] T002 [P] [API] Initialize FastAPI + Python 3.11 project in `services/orchestrator/` with `pyproject.toml` (or requirements) listing FastAPI, uvicorn, qdrant-client, sentence-transformers, OpenTelemetry SDK dependencies
- [x] T003 [P] [VSCode] Initialize VS Code extension TypeScript package in `clients/vscode/` with `package.json`, `tsconfig.json`, and extension entry `clients/vscode/src/extension.ts` (exact VS Code API/bundler versions Proposed — align with current extension norms)
- [x] T004 [P] [API] Add orchestrator Dockerfile at `services/orchestrator/Dockerfile` suitable for local Compose
- [x] T005 [P] Configure lint/format baselines for orchestrator (ruff/black or project-standard) under `services/orchestrator/` and for extension (eslint/prettier or project-standard) under `clients/vscode/`
- [x] T006 [P] [Discovery] Document OQ-PACKER clarification request: concrete Repomix package pin vs in-house adapter — record outcome in `specs/ep-001-l5-repository-packing-indexing/` notes or ADR follow-up; do not invent a Confirmed package choice in code contracts before clarification

**Checkpoint**: Scaffold exists; no user-story behavior required yet

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before ANY user-story implementation

**⚠️ CRITICAL**: No user story work (Phases 3–7) may begin until this phase is complete

- [x] T007 [API] Create FastAPI app entrypoint `services/orchestrator/app/main.py` with router include hooks and app lifespan placeholder
- [x] T008 [P] [API] Add shared request/response Pydantic models for confirmed `POST /index` in `services/orchestrator/app/api/schemas_index.py` — request: `repo_path`, `repo_name`; response: `files_indexed`, `graph_nodes`, `embeddings`, `time_ms` (no invented fields)
- [x] T009 [P] [API] Stub OpenAPI-aligned index router `services/orchestrator/app/api/index.py` registering `POST /index` returning placeholder response (wire real pipeline in story phases)
- [x] T010 [P] [Security] Implement ignore/exclusion policy module `services/orchestrator/app/security/ignore_policy.py` — respect `.gitignore`; hard-exclude `.env`, secrets, `node_modules`, `dist`, `.git`, build/deps, binaries; **no override path** until OQ-OVERRIDE clarified (FR-012)
- [x] T011 [P] [Security] Implement filesystem walker adapter `services/orchestrator/app/adapters/fs_walker.py` that applies `ignore_policy` before yielding allowed file paths
- [x] T012 [P] [Security] Implement consent gate module `services/orchestrator/app/security/consent_gate.py` with deny-by-default for query-time external LLM when consent/configuration absent (FR-021); do **not** invent consent UX/storage schema (OQ-US016 open)
- [x] T013 [P] [Telemetry] Bootstrap OpenTelemetry-compatible module `services/orchestrator/app/telemetry/indexing.py` with no-op/exporter-agnostic span helpers for `/index` (OQ-OTEL exporter vendor open)
- [x] T014 [P] Create Docker Compose stack `deploy/docker-compose.yml` with Qdrant service (+ API service skeleton); FalkorDB optional and unused for EP-001 graph writes
- [x] T015 [P] [API] Add configuration loader `services/orchestrator/app/config.py` for Qdrant URL, model path/name (`all-MiniLM-L6-v2`), and related Proposed env keys — document keys as Proposed
- [x] T016 [P] [Security] [Unit] Write unit tests for ignore/exclusion walker fixtures (`.env`, `node_modules`, `dist`, `.git`, binaries) in `services/orchestrator/tests/unit/test_ignore_policy.py` and `services/orchestrator/tests/unit/test_fs_walker.py` — MUST fail or be red until T010/T011 complete
- [x] T017 [Discovery] Record clarification tickets for OQ-14, OQ-US016, OQ-PACK, OQ-OVERRIDE, OQ-01, OQ-HTTP in `specs/ep-001-l5-repository-packing-indexing/` (open-questions checklist or equivalent) — **do not invent resolutions**; mark blocking impact per plan Open Questions table
- [x] T018 [Discovery] [OQ-PACK] Clarify pack artifact persistence location / retrieval shape for FR-004 (behavioral availability for EP-002) without freezing invented field inventory — document Proposed cache keyed by `repo_name` as provisional only
- [x] T019 [P] [Contract] Add contract test skeleton asserting confirmed `POST /index` request/response field names only in `services/orchestrator/tests/contract/test_index_contract.py`

**Checkpoint**: Foundation ready — user story implementation can begin (US-001 and US-002 first; extension stories after API usable)

---

## Phase 3: User Story 1 — Repo Flattening & Packing (US-001) (Priority: P1) 🎯 MVP

**Goal**: Flatten a local repository into an LLM-optimized XML-oriented packed representation with token pre-calculation and binary skip; expose via indexing path; make pack available for downstream EP-002 consumers (behavioral).

**Independent Test**: Call `POST /index` (or pack stage) on a fixture repo ≤500k LOC scale and verify XML-oriented pack, token count present, binaries skipped, ignored/excluded paths absent from pack (SC-001, SC-004 pack side).

### Clarification / Discovery (US-001)

- [x] T020 [US001] [Discovery] [OQ-PACK] Before freezing pack OpenAPI/artifact schema, confirm with product which pack fields beyond FR-01 XML-oriented content + token pre-calc are required — until resolved, implement **behavioral** FR-001/FR-002/FR-022 only (no invented documented fields)

### Tests for User Story 1

- [x] T021 [P] [US001] [L5] Write unit test for binary skip during packing in `services/orchestrator/tests/unit/test_packer_binary_skip.py`
- [x] T022 [P] [US001] [L5] Write unit test asserting token pre-calculation present on pack output in `services/orchestrator/tests/unit/test_packer_token_count.py`
- [x] T023 [P] [US001] [L5] [Security] Write unit/integration fixture test that `.gitignore`-matched and hard-excluded paths are absent from pack in `services/orchestrator/tests/unit/test_packer_exclusions.py` (SC-004 pack side)
- [x] T024 [P] [US001] [L5] Write acceptance/integration test for XML-oriented pack production on fixture repo in `services/orchestrator/tests/integration/test_pack_sc001.py` (SC-001)

### Implementation for User Story 1

- [x] T025 [P] [US001] [L5] Implement Repomix-style packer service `services/orchestrator/app/services/l5_pack.py` producing XML-oriented LLM-optimized flatten (FR-001); use clarified package from T006 or in-house adapter matching FR-01 behavior
- [x] T026 [P] [US001] [L5] Implement binary detection/skip in packer or walker path used by `l5_pack.py` (FR-003)
- [x] T027 [US001] [L5] Implement token count pre-calculation on packed representation in `services/orchestrator/app/services/l5_pack.py` (FR-002)
- [x] T028 [US001] [L5] Implement pack artifact persistence/availability for downstream consumers in `services/orchestrator/app/services/l5_pack.py` (and/or Proposed artifact store under orchestrator-managed path) per T018 provisional notes — behavioral FR-004 only; do not invent field inventory (FR-022)
- [x] T029 [US001] [API] [L5] Wire pack stage into `POST /index` handler in `services/orchestrator/app/api/index.py` using walker + ignore policy (FR-005, FR-010, FR-011) so packing runs under orchestrator ownership
- [x] T030 [US001] [Security] Ensure default exclusions remain in force with **no** override UX implemented (FR-012 / OQ-OVERRIDE)
- [x] T031 [US001] [Telemetry] Emit pack-related span/log attributes (e.g., exclusion counts without secret contents) via `services/orchestrator/app/telemetry/indexing.py` during pack stage

**Checkpoint**: US-001 independently testable — pack + tokens + binary/exclusion correctness via SC-001/SC-004 pack tests

---

## Phase 4: User Story 2 — Privacy-Respecting Local Embedding Index (US-002) (Priority: P1) 🎯 MVP

**Goal**: Chunk allowed content (~500 tokens), embed locally with `all-MiniLM-L6-v2` (384-dim) into Qdrant `codebase`, return confirmed `POST /index` response fields, guarantee zero index-time external LLM exfil.

**Independent Test**: `POST /index` upserts 384-dim vectors to Qdrant; response includes `files_indexed`, `embeddings`, `time_ms`, `graph_nodes` (may be 0); mocks/network asserts show no source code sent to external LLM providers (SC-002, SC-003, SC-004 embed side).

### Tests for User Story 2

- [x] T032 [P] [US002] [L5] Write unit test that chunker approximates ~500-token chunks (FR-023) in `services/orchestrator/tests/unit/test_chunker.py` (tolerance Proposed)
- [x] T033 [P] [US002] [L5] Write unit test that embedder returns 384-dim vectors and never calls external LLM client in `services/orchestrator/tests/unit/test_embeddings_local.py` (SC-003 / NFR-005)
- [x] T034 [P] [US002] [API] [Contract] Extend `services/orchestrator/tests/contract/test_index_contract.py` to assert response fields `files_indexed`, `embeddings`, `time_ms`, `graph_nodes` only (SC-002; no invented fields)
- [x] T035 [P] [US002] [L5] Write integration test `POST /index` → Qdrant `codebase` upsert with payload concepts `repo_name` + `file_path` in `services/orchestrator/tests/integration/test_index_qdrant.py` (testcontainer or Compose Qdrant)
- [x] T036 [P] [US002] [Security] Write integration/security test asserting zero external LLM calls on index path (with and without consent flag present) in `services/orchestrator/tests/integration/test_index_no_exfil.py` (FR-009; SC-003; SC-009 index side)
- [x] T037 [P] [US002] [Security] Write test that excluded paths never appear in Qdrant payloads in `services/orchestrator/tests/integration/test_index_exclusions_qdrant.py` (SC-004 embed side)

### Implementation for User Story 2

- [x] T038 [P] [US002] [L5] Implement ~500-token chunker in `services/orchestrator/app/services/l5_chunk.py` (FR-023)
- [x] T039 [P] [US002] [L5] Implement local embedding adapter `services/orchestrator/app/adapters/embeddings.py` loading `sentence-transformers/all-MiniLM-L6-v2` on CPU; hard-fail if wired to external LLM endpoints (FR-007; NFR-005)
- [x] T040 [P] [US002] [L5] Implement Qdrant adapter `services/orchestrator/app/adapters/qdrant_store.py` ensuring collection `codebase` at 384-dim and upsert/delete by file scope (FR-008; database-schema §2)
- [x] T041 [US002] [L5] [API] Implement index orchestration service `services/orchestrator/app/services/l5_index.py` — walk → filter → pack → chunk → embed → upsert; measure `time_ms`; set `graph_nodes=0` for MVP (FR-006)
- [x] T042 [US002] [API] Complete `POST /index` in `services/orchestrator/app/api/index.py` to call `l5_index` and return confirmed response fields (FR-005, FR-006)
- [x] T043 [US002] [API] Add request validation for readable `repo_path` and non-empty `repo_name` in index router/schemas; map errors using **Proposed** status codes only and document OQ-HTTP as unresolved (do not treat Proposed codes as Confirmed)
- [x] T044 [US002] [API] Implement **Proposed** concurrent-index guard (single-flight / Proposed `409`) in index orchestration without claiming Confirmed HTTP semantics until OQ-HTTP resolves
- [x] T045 [US002] [Telemetry] Instrument `/index` duration and counts (`files_indexed`, `embeddings`, `graph_nodes`) in `services/orchestrator/app/telemetry/indexing.py` aligned to response fields (ADR-011)
- [x] T046 [US002] [L5] Add optional Proposed `content_hash` skip path in upsert/delta helper inside `l5_index.py` / qdrant adapter — labeled Proposed, not Confirmed requirement
- [x] T047 [US002] [Perf] Create performance harness skeleton for full-index timing toward NFR-001 / SC-005 in `services/orchestrator/tests/integration/test_index_perf_full.py` (may be skipped without 1M LOC corpus; must not invent search metrics)

**Checkpoint**: US-002 independently testable via `POST /index` + Qdrant + no-exfil + contract fields; US-001+US-002 together deliver MVP packing+embedding API

---

## Phase 5: User Story 3 — Auto-Index on Extension Install (US-011) (Priority: P2)

**Goal**: On VS Code extension install/activation, trigger workspace indexing through FastAPI `POST /index`; extension owns progress/cancellation UX only — never indexing policy.

**Independent Test**: Activate extension against mock or live orchestrator; verify `POST /index` is invoked for workspace repo; progress/cancel works; no local reimplementation of ignore/consent policy (SC-007; FR-013..015).

### Tests for User Story 3

- [x] T048 [P] [US011] [VSCode] Write extension test that activation triggers `POST /index` (mock server acceptable) in `clients/vscode/tests/activation_auto_index.test.ts` (SC-007)
- [x] T049 [P] [US011] [VSCode] Write test that cancellation aborts in-flight client index request in `clients/vscode/tests/index_cancellation.test.ts` (FR-015; OQ-CANCEL server-side semantics remain open — assert client cancel only)
- [x] T050 [P] [US011] [VSCode] [Security] Write test/code-review checklist assertion that extension does not pack files locally or bypass backend ignore policy in `clients/vscode/tests/no_client_policy_bypass.test.ts` (FR-014)

### Implementation for User Story 3

- [x] T051 [P] [US011] [VSCode] Implement orchestrator HTTP client `clients/vscode/src/api/indexClient.ts` calling confirmed `POST /index` with `{repo_path, repo_name}` only (no invented endpoints)
- [x] T052 [P] [US011] [VSCode] Add Proposed extension settings for orchestrator base URL in `clients/vscode/package.json` / `clients/vscode/src/config.ts` (discovery of exact setting keys — document as Proposed)
- [x] T053 [US011] [VSCode] Implement activation auto-index trigger in `clients/vscode/src/extension.ts` (and/or `clients/vscode/src/indexing/autoIndex.ts`) on install/activation (FR-013)
- [x] T054 [US011] [VSCode] Implement progress notification UX during index in `clients/vscode/src/indexing/progress.ts` (FR-015)
- [x] T055 [US011] [VSCode] Wire cancellation token to abort in-flight `POST /index` request (FR-015; Proposed client-side cancel only — OQ-CANCEL)
- [x] T056 [US011] [VSCode] Ensure extension never uploads excluded paths or reimplements ignore/consent policy — API-only orchestration (FR-014; constitution V)
- [x] T057 [US011] [Perf] Add optional observational timing log/test for ~200-file auto-index ~10s illustrative target (NFR-004 / SC-008 observational) in `clients/vscode/tests/` or orchestrator integration — hardware-gated; do not invent stricter SLA

**Checkpoint**: US-011 independently testable — activate → backend index; progress/cancel; policy stays server-side

---

## Phase 6: User Story 4 — Incremental Re-Index on File Save (US-012) (Priority: P2)

**Goal**: On file save in an already indexed workspace, trigger incremental re-index for changed scope within delta timing targets; **no invented endpoints** — OQ-14 gating.

**Independent Test**: Save a file; extension invokes orchestrator incremental path; delta for 100-file change set targets <60s (SC-006); single-file ~0.5s observational (SC-008). API shape beyond confirmed `POST /index` remains provisional until OQ-14 resolves.

### Clarification / Discovery (US-012) — BLOCKING for contract freeze

- [x] T058 [US012] [Discovery] [OQ-14] **Blocking for US-012 API contract freeze**: Clarify incremental delta index API with product — either confirm Proposed reuse of `POST /index` with optional narrower-scope fields, or approve an ADR for any new endpoint. **Do not invent** additional confirmed endpoints (FR-017; ADR-009). Record decision in feature open-questions notes before locking OpenAPI.
- [x] T059 [US012] [Discovery] After T058, document provisional OpenAPI delta fields (if any) as **Proposed** in `docs/architecture/api-contract.md` sync notes or feature `contracts/` excerpt — never as Confirmed Appendix D until product confirms

### Tests for User Story 4

- [x] T060 [P] [US012] [VSCode] Write extension test that file save triggers incremental re-index call to orchestrator in `clients/vscode/tests/save_incremental_reindex.test.ts` (SC-008 trigger; FR-016)
- [x] T061 [P] [US012] [L5] [Perf] Write delta performance harness for 100-file change set targeting <60s in `services/orchestrator/tests/integration/test_index_perf_delta.py` (SC-006 / NFR-002)
- [x] T062 [P] [US012] [L5] Write integration test that re-index updates/replaces Qdrant chunks for changed `file_path` scope in `services/orchestrator/tests/integration/test_index_delta_upsert.py`

### Implementation for User Story 4

- [x] T063 [US012] [VSCode] Implement save listener in `clients/vscode/src/indexing/onSaveReindex.ts` that triggers incremental re-index for changed scope after T058 decision (FR-016)
- [x] T064 [US012] [API] [L5] Implement incremental/delta indexing path in `services/orchestrator/app/services/l5_index.py` reusing confirmed `POST /index` per OQ-14 outcome — optional narrower-scope fields only if Proposed/approved; **no** new Confirmed endpoints without ADR (FR-017)
- [x] T065 [US012] [API] Update `services/orchestrator/app/api/index.py` and schemas to accept provisional Proposed narrower-scope fields only after T058/T059 — label Proposed in OpenAPI until Confirmed
- [x] T066 [US012] [L5] Ensure Qdrant adapter deletes/replaces vectors for saved file scope in `services/orchestrator/app/adapters/qdrant_store.py`
- [x] T067 [US012] [Perf] Capture observational single-file save re-index timing (~0.5s illustrative, NFR-003) without inventing a stricter global SLA
- [x] T068 [US012] [Telemetry] Add delta/index span attributes distinguishing full vs incremental when Proposed mode exists in `services/orchestrator/app/telemetry/indexing.py`

**Checkpoint**: US-012 independently testable — save → delta re-index; SC-006 harness; contract remains Proposed until OQ-14 confirmed

---

## Phase 7: User Story 5 — Query-Time External LLM Consent Gate (US-016) (Priority: P2)

**Goal**: Deny-by-default query-time external LLM use without consent/configuration; when consent present, restrict to allowed packed/compressed context path narrative; allow local Ollama non-exfil option when configured; index path remains no-exfil regardless of consent. Consent UX/storage detail blocked on OQ-US016.

**Independent Test**: Without consent, external LLM path blocked; with consent flag present, only allowed context path; index path still never calls external LLM (SC-009; SC-010 limited to deny-by-default — no invented UI pass criteria).

### Clarification / Discovery (US-016)

- [x] T069 [US016] [Discovery] [OQ-US016] **Blocking for consent UX/storage implementation detail**: Clarify consent UX and storage mechanism with product. Until resolved, ship **behavioral deny-by-default gate only** (FR-021); do not invent settings UI schema, secure-storage layout, or consent CRUD REST APIs.

### Tests for User Story 5

- [x] T070 [P] [US016] [Security] Write unit tests for consent gate deny-when-absent / allow-when-present in `services/orchestrator/tests/unit/test_consent_gate.py` (FR-018; NFR-007)
- [x] T071 [P] [US016] [Security] Write unit/integration test that consented external path is restricted to allowed packed/compressed context narrative (behavioral hook) in `services/orchestrator/tests/unit/test_consent_allowed_context_path.py` (FR-019) — no invented EP-002 `/context` delivery
- [x] T072 [P] [US016] [Security] Write test documenting local Ollama/config path may operate without external exfil when configured in `services/orchestrator/tests/unit/test_local_inference_option.py` (FR-020)
- [x] T073 [P] [US016] [Security] Regression: re-run index no-exfil tests with consent absent and present in `services/orchestrator/tests/integration/test_index_no_exfil.py` (FR-009; SC-009)

### Implementation for User Story 5

- [x] T074 [US016] [Security] Complete orchestrator consent check integration points in `services/orchestrator/app/security/consent_gate.py` so any query-time external LLM invocation path is blocked without consent (FR-018)
- [x] T075 [US016] [Security] Enforce allowed packed/compressed context-only transmission when consent present (FR-019) at the security boundary — do not implement full L4 compression (out of scope)
- [x] T076 [US016] [Security] Document and support configuration hook for local inference (e.g., Ollama) without external exfil in `services/orchestrator/app/config.py` / security module docs (FR-020)
- [x] T077 [US016] [Security] Explicitly leave consent UX/storage unimplemented beyond deny-by-default until T069 resolves (FR-021; SC-010)
- [x] T078 [US016] [Security] Verify index orchestration never consults external LLM clients regardless of consent state (wire assert in `l5_index` / embeddings adapter)

**Checkpoint**: US-016 independently testable for deny-by-default + index no-exfil; UX/storage remain open (OQ-US016)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, perf validation, telemetry verification, documentation, deployment readiness, regression — no EP-002/EP-003/L1/L4 pull-forward

- [x] T079 [P] [Security] Security verification pass: `.gitignore` / `.env` / secrets / build/deps / binaries / `.git` exclusions; no override path; index-time no-exfil; query-time deny-by-default — document results in `specs/ep-001-l5-repository-packing-indexing/` verification notes or future validation-report
- [x] T080 [P] [Security] Document OQ-01 RBAC gap: path-RBAC schema Missing Evidence — MVP POC may defer enforcement detail; do not invent roles/authn (record in open questions)
- [ ] T081 [P] [Perf] Execute/record NFR-001 full-index harness results (<15 min / 1M LOC) when corpus available; if unmet, document gap per constitution IV in feature notes (no search p95)
- [ ] T082 [P] [Perf] Execute/record NFR-002 delta harness (<60s / 100-file) results
- [x] T083 [P] [Telemetry] Verify OTel-compatible spans/attributes for `/index` duration and counts; keep exporter vendor as OQ-OTEL
- [x] T084 [P] [Contract] Freeze OpenAPI snapshot for **Confirmed** `POST /index` fields only in `services/orchestrator/tests/contract/` and sync clients; keep OQ-14 Proposed fields labeled provisional
- [x] T085 [P] Documentation: Update or add feature quickstart/ops notes under `specs/ep-001-l5-repository-packing-indexing/quickstart.md` (or `docs/`) covering Compose up, model weights (~90MB), Qdrant, extension settings — without inventing unresolved OQ answers
- [x] T086 [P] Documentation: Sync architecture api-contract incremental note with OQ-14 status (Proposed reuse only until confirmed) in `docs/architecture/api-contract.md` if product allows doc-only update
- [x] T087 [Deployment] Validate `deploy/docker-compose.yml` smoke: API reachable + Qdrant healthy; model volume documented; fail clearly if weights missing
- [x] T088 [Deployment] Document rollback: disable extension auto-index/save triggers; tear down Compose; no destructive Qdrant wipe required for rollback of triggers
- [x] T089 Regression suite: ensure exclusion + no-exfil + contract tests run on changes to walker/embedder/index router/extension client
- [x] T090 Confirm out-of-scope gate: no hybrid search, Serena, blast radius, L4 compression implementation, L2/L6, CLI primary acceptance, or invented endpoints shipped under EP-001

**Checkpoint**: Feature ready for validation-report / Implementation Gate handoff

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies — start immediately
- **Phase 2 Foundational**: Depends on Phase 1 — **BLOCKS all user stories**
- **Phase 3 US-001**: Depends on Phase 2
- **Phase 4 US-002**: Depends on Phase 2; practically builds on US-001 pack stage (T029) for full pipeline but pack tests remain independently meaningful
- **Phase 5 US-011**: Depends on Phase 4 (`POST /index` complete) for live path; mock-server extension tests may start after T051 client exists
- **Phase 6 US-012**: Depends on Phase 5 activation client patterns + Phase 4 index service; **T058 OQ-14 blocks API contract freeze**
- **Phase 7 US-016**: Depends on Phase 2 consent module (T012); can proceed in parallel with extension stories for gate unit tests; **T069 blocks consent UX detail**
- **Phase 8 Polish**: Depends on all desired user stories complete

### User Story Dependencies

| Story | Priority | Depends on | Independently testable after |
|-------|----------|------------|------------------------------|
| US-001 | P1 | Phase 2 | Pack/exclusion tests green |
| US-002 | P1 | Phase 2 (+ pack wire for E2E index) | `POST /index` + Qdrant + no-exfil |
| US-011 | P2 | US-002 API | Activation → mock/live index |
| US-012 | P2 | US-011 client + US-002 index; OQ-14 for contract freeze | Save → delta call + SC-006 |
| US-016 | P2 | Phase 2 consent foundation | Deny-by-default + index no-exfil regression |

### Within Each User Story

1. Discovery/clarification tasks that block contract/UX freeze (where applicable)
2. Tests written and failing first where feasible
3. Adapters/services before API wiring
4. Extension client before triggers
5. Story checkpoint before next priority (or parallel if staffed and independent)

### Parallel Opportunities

- T002–T006 (setup) in parallel after T001 dirs exist
- T008–T015, T016, T019 foundational parallel where files differ
- US-001 test tasks T021–T024 in parallel
- US-002 test tasks T032–T037 in parallel; adapters T038–T040 in parallel
- US-011 tests T048–T050 in parallel
- US-016 unit tests T070–T072 can run parallel to US-011/US-012 implementation after T012
- Polish T079–T086 largely parallel

---

## Parallel Example: User Story 2

```bash
# Tests in parallel:
Task: "Unit test chunker ~500 tokens in services/orchestrator/tests/unit/test_chunker.py"
Task: "Unit test local 384-dim embedder + no external LLM in services/orchestrator/tests/unit/test_embeddings_local.py"
Task: "Contract test POST /index response fields in services/orchestrator/tests/contract/test_index_contract.py"
Task: "Integration test Qdrant upsert in services/orchestrator/tests/integration/test_index_qdrant.py"

# Adapters in parallel:
Task: "Chunker in services/orchestrator/app/services/l5_chunk.py"
Task: "Embeddings adapter in services/orchestrator/app/adapters/embeddings.py"
Task: "Qdrant adapter in services/orchestrator/app/adapters/qdrant_store.py"
```

---

## Implementation Strategy

### MVP First (US-001 + US-002)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundational (CRITICAL)
3. Complete Phase 3 US-001 (packing)
4. Complete Phase 4 US-002 (local embed + `POST /index`)
5. **STOP and VALIDATE**: Contract + exclusion + no-exfil + SC-001..004
6. Demo API indexing without extension if needed

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US-001 → pack independently → demo
3. US-002 → full `POST /index` → MVP API demo
4. US-011 → auto-index DX → install demo
5. US-012 after OQ-14 clarification gate → save freshness
6. US-016 deny-by-default gate (UX later) → privacy model complete for EP-001
7. Polish → validation-report ready

### Parallel Team Strategy

- Dev A: Orchestrator US-001 → US-002
- Dev B: Foundational security + consent gate + US-016 behavioral tests
- Dev C: VS Code US-011 → US-012 (blocked on OQ-14 for contract freeze only)

---

## Definition of Done

- [ ] All FR-001..FR-023 have implementation and verification coverage (FR-012/FR-017/FR-021/FR-022 satisfied via default-only / Proposed / discovery tasks — not invented product resolutions)
- [ ] All user stories US-001, US-002, US-011, US-012, US-016 independently testable at their checkpoints
- [ ] SC-001..SC-010 addressed; SC-010 limited to deny-by-default (no invented UI criteria)
- [ ] Indexing NFR tests present (NFR-001..007); **no** search recall/p95 acceptance
- [ ] Security: ignore/exclusion, index no-exfil, query-time deny-by-default verified
- [ ] Telemetry: `/index` duration/counts instrumented (exporter vendor open)
- [ ] Documentation and deployment smoke complete
- [ ] Open questions OQ-14, OQ-US016, OQ-PACK remain explicitly unresolved unless product clarifies
- [ ] No application scope creep into EP-002/EP-003/V1 L1/L4/L2/L6
- [ ] Constitution Task Gate criteria met

---

## Evidence Reviewed

| Artifact | Path / ID |
|----------|-----------|
| Feature spec | `specs/ep-001-l5-repository-packing-indexing/spec.md` |
| Implementation plan | `specs/ep-001-l5-repository-packing-indexing/plan.md` |
| Constitution Task Gate | `.specify/memory/constitution.md` v1.0.0 |
| Tasks template | `.specify/templates/tasks-template.md` |
| PM → task-generator handoff | `.cursor/agent-handoffs/handoff.md` |
| API contract | `docs/architecture/api-contract.md` §2.2 |
| ADRs | ADR-001, ADR-002, ADR-003, ADR-008, ADR-009, ADR-011, ADR-012, ADR-013 |
| Implementation guidelines | `docs/architecture/implementation-guidelines.md` (Proposed layout) |
| Database schema | `docs/architecture/database-schema.md` §2 |
| Source code | **Not present** — paths Proposed |

---

## Open Questions / Discovery Tasks

| OQ ID | Task IDs | Blocking? | Resolution status in tasks |
|-------|----------|-----------|----------------------------|
| OQ-14 | T017, T058, T059, T064, T065 | **Blocking for US-012 API contract freeze** | Discovery only — Proposed `POST /index` reuse; no invented endpoints |
| OQ-US016 | T017, T069, T077 | **Blocking for consent UX/storage detail** | Deny-by-default ships; UX/storage not invented |
| OQ-PACK | T017, T018, T020, T028 | **Blocking for pack contract freeze** | Behavioral FR-01 pack only |
| OQ-OVERRIDE | T017, T030, T079 | Non-blocking while defaults exclude-all | No override implementation |
| OQ-01 | T017, T080 | Non-blocking for POC defaults | Gap documented; no invented RBAC |
| OQ-HTTP | T017, T043, T044 | Non-blocking for functional draft | Proposed codes labeled only |
| OQ-OTEL | T013, T083 | Non-blocking | Compatible SDK; exporter open |
| OQ-PACKER | T006, T025 | Non-blocking if FR-01 behavior met | Clarification before package pin as Confirmed |
| OQ-CANCEL | T049, T055 | Non-blocking | Client cancel Proposed; server cancel Not evidenced |

---

## Task Traceability Matrix

| Task / Phase | Source Requirement | Plan Reference | Evidence |
|--------------|-------------------|----------------|----------|
| Phase 1 T001–T006 | Setup; greenfield | Plan Phase 0; Project Structure | implementation-guidelines §1 |
| Phase 2 T007–T019 | FR-005 stub, FR-010..012, FR-021 gate, telemetry, Compose | Plan Phase 0; Components; Security | ADR-012, ADR-011, ADR-013 |
| Phase 3 US-001 T020–T031 | FR-001..004, FR-010..012, FR-022; SC-001, SC-004 | Plan Phase 1 | BRD FR-01; spec US-001 |
| Phase 4 US-002 T032–T047 | FR-005..009, FR-023; NFR-001/005; SC-002..005 | Plan Phase 2 | ADR-003; Appendix D |
| Phase 5 US-011 T048–T057 | FR-013..015; NFR-004; SC-007 | Plan Phase 3 | BRD §14 On Install |
| Phase 6 US-012 T058–T068 | FR-016..017; NFR-002..003; SC-006, SC-008 | Plan Phase 4; OQ-14 | BRD §6/§10/§14; ADR-009 |
| Phase 7 US-016 T069–T078 | FR-018..021; NFR-007; SC-009..010 | Plan Phase 5; OQ-US016 | Appendix C; constitution III |
| Phase 8 T079–T090 | NFR-001..007; security; docs; deploy; regression | Plan Phase 6 | Constitution Task Gate |
| Discovery OQs | OQ-14, OQ-US016, OQ-PACK (+ related) | Plan Open Questions | Spec Open Questions; PM handoff |

### FR → Task Coverage (implementation + verification)

| FR | Implementation tasks | Verification tasks |
|----|---------------------|-------------------|
| FR-001 | T025, T029 | T024 |
| FR-002 | T027 | T022 |
| FR-003 | T026 | T021 |
| FR-004 | T028, T018 | T024 (availability behavioral) |
| FR-005 | T008, T009, T042, T051 | T034, T019 |
| FR-006 | T041, T042 | T034, T035 |
| FR-007 | T039 | T033, T035 |
| FR-008 | T040, T041 | T035 |
| FR-009 | T039, T041, T078 | T036, T073 |
| FR-010 | T010, T011, T029 | T016, T023, T037 |
| FR-011 | T010, T011, T029 | T016, T023, T037 |
| FR-012 | T010, T030 | T079 |
| FR-013 | T053 | T048 |
| FR-014 | T056 | T050 |
| FR-015 | T054, T055 | T049 |
| FR-016 | T063, T064 | T060, T062 |
| FR-017 | T058, T059, T064, T065 | T084 (provisional labeling) |
| FR-018 | T012, T074 | T070 |
| FR-019 | T075 | T071 |
| FR-020 | T076 | T072 |
| FR-021 | T012, T069, T077 | T070; SC-010 limited |
| FR-022 | T020, T028 | T020 discovery gate |
| FR-023 | T038 | T032 |

### NFR / SC → Verification

| Claim | Tasks |
|-------|-------|
| NFR-001 / SC-005 | T047, T081 |
| NFR-002 / SC-006 | T061, T082 |
| NFR-003 / SC-008 timing | T067 |
| NFR-004 / SC-008/~200 files | T057 |
| NFR-005 / SC-003 | T033, T036 |
| NFR-006 / SC-004 | T016, T023, T037, T079 |
| NFR-007 / SC-009 | T070, T073, T074 |
| SC-001 | T021–T024, T025–T029 |
| SC-002 | T034, T042 |
| SC-007 | T048, T053 |
| SC-010 | T069, T077 (deny-by-default only) |

---

## Constitution Compliance (Task Gate)

| Gate Check | Status |
|------------|--------|
| Every requirement has implementation and verification coverage | **Met** (FR-001..023 + NFR-001..007; open FRs via discovery/default-only tasks) |
| Tasks grouped by independently deliverable user story | **Met** (US-001, US-002, US-011, US-012, US-016) |
| Exact paths when known; discovery for unknowns | **Met** (Proposed `services/orchestrator`, `clients/vscode`, `deploy/`) |
| Tests for affected indexing intelligence claims | **Met** (no search recall/p95) |
| Security, documentation, telemetry, deployment where applicable | **Met** (Phases 2, 7, 8) |
| OQ-14 / OQ-US016 / OQ-PACK carried as clarification — not invented | **Met** |

**Task Gate**: **Yes** — ready for validation / implement sequencing with open clarifications remaining.

---

## Notes

- `[P]` = different files, safe parallelization
- Do not mark tasks complete in this file until implementation evidence exists
- Commit after each task or logical group during implement phase
- Stop at any story checkpoint to validate independently
- Still **no** application source code is produced by the task-generator agent itself
