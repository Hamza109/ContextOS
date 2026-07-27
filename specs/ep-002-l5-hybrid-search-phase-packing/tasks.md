# Tasks: EP-002 L5 Hybrid Search & Phase-Aware Packing

**Input**: Design documents from `/specs/ep-002-l5-hybrid-search-phase-packing/`

**Prerequisites**: plan.md (required), spec.md (required), EP-001 pack/Qdrant foundation, `docs/architecture/api-contract.md` §2.3, ADR-014, ADR-006, ADR-011, constitution I–V, EP-001 `open-questions.md` OQ-PACK

**Tests**: REQUIRED — search relevance, latency (p95), phase composition, citation attribute presence, API contracts, privacy inheritance. SC-003 recall@10 verification is **blocked** until OQ-recall-harness resolves — tasks MUST mark blocked/skipped; do **not** invent Pass/Fail execution results. SC-002 p95 @ 500k LOC is blocked/skipped if NFR-scale fixture unavailable.

**Organization**: Tasks are grouped by independently deliverable user story (US-003, US-004, US-015) so each story can be implemented and tested independently after foundational work. Setup/foundational consumes EP-001 Qdrant/packs — does not re-plan indexing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete paired tasks)
- **[Story]**: Maps to user story (`[US003]`, `[US004]`, `[US015]`)
- **[Layer/Surface]**: Tags such as `[L5]`, `[API]`, `[Security]`, `[Telemetry]`
- Exact paths from plan when known (`services/orchestrator/...`); discovery tasks for OQ unknowns — label **Proposed**; do **not** Confirmed-freeze

## Path Conventions (Confirmed present + Proposed EP-002 modules)

```text
services/orchestrator/app/
  api/{context.py, schemas_context.py}          # Proposed NEW
  services/{l5_search.py, l5_phase_pack.py, l5_citations.py}  # Proposed NEW
  services/{l5_pack.py, l5_chunk.py, l5_index.py}             # EP-001 reuse
  adapters/{qdrant_store.py, embeddings.py, bm25_store.py}    # extend / Proposed NEW
  security/{ignore_policy.py, consent_gate.py}                # EP-001 reuse
  telemetry/{indexing.py, context.py}                         # context Proposed NEW
  config.py, main.py
services/orchestrator/tests/{unit,integration,contract}/
deploy/docker-compose.yml
specs/ep-002-l5-hybrid-search-phase-packing/
```

**Out of scope (do NOT schedule as deliverables)**: Serena/L3 (EP-003); L1 blast/`GET /blast`/`graph.html`; L4 Headroom product / FR-11 budgets / compression dashboard; L2/L6; full CLI epic (EP-004); extension DX (Ask clicks, Pack Context UX). CLI/`contextos ask` and extension Ask appear only as **consumer notes** of `POST /context` (FR-019).

**Label rule**: OQ-16, OQ-11, OQ-PACK, OQ-top_k, OQ-MVP-metrics, OQ-recall-harness, OQ-BM25-store, OQ-HTTP-/context, OQ-01 remain **OPEN**. Implementations may use **Proposed** mechanisms only — never Confirmed-freeze.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm EP-001 upstream readiness and scaffold Proposed EP-002 modules on branch `feature/ep-002-l5-hybrid-search-phase-packing` without inventing Confirmed contracts.

- [ ] T001 [L5] [API] Verify current branch is `feature/ep-002-l5-hybrid-search-phase-packing` and EP-001 modules exist under `services/orchestrator/app/` (`l5_pack.py`, `l5_index.py`, `adapters/qdrant_store.py`, `adapters/embeddings.py`, `security/ignore_policy.py`, `security/consent_gate.py`, `api/index.py`, `main.py`) — document gaps if missing (A-EP002-1)
- [ ] T002 [P] [L5] [Discovery] [OQ-PACK] Inventory Proposed EP-001 pack handoff fields from `services/orchestrator/app/services/l5_pack.py` (`PackResult`: `repo_name`, `xml_content`, `token_count`, `files_packed`, `files_excluded`, `artifact_path`) and pack cache keyed by `repo_name` under `CONTEXTOS_PACK_CACHE_DIR` — record as **Proposed only**; do **not** Confirmed-freeze field inventory (EP-001 open-questions.md OQ-PACK)
- [ ] T003 [P] [L5] [Discovery] Confirm Qdrant `codebase` collection + query embedding path reusable: `services/orchestrator/app/adapters/qdrant_store.py` (upsert/ensure present) and `services/orchestrator/app/adapters/embeddings.py` (`all-MiniLM-L6-v2`, 384-dim) — note search/query API not yet present (to be added in US-003)
- [ ] T004 [P] [API] Scaffold Proposed empty modules: `services/orchestrator/app/api/context.py`, `services/orchestrator/app/api/schemas_context.py`, `services/orchestrator/app/services/l5_search.py`, `services/orchestrator/app/services/l5_phase_pack.py`, `services/orchestrator/app/services/l5_citations.py`, `services/orchestrator/app/adapters/bm25_store.py`, `services/orchestrator/app/telemetry/context.py` per plan Project Structure (names **Proposed**)
- [ ] T005 [P] [Discovery] Record clarification tickets for EP-002 OQs in `specs/ep-002-l5-hybrid-search-phase-packing/` (open-questions checklist or equivalent): OQ-16, OQ-11, OQ-PACK, OQ-top_k, OQ-MVP-metrics, OQ-recall-harness, OQ-BM25-store, OQ-HTTP-/context, OQ-01 — **do not invent resolutions**; mark blocking impact per spec/plan Open Questions tables
- [ ] T006 [P] [Discovery] [OQ-BM25-store] Document Proposed BM25 placement choice for MVP: **Option A** (in-process BM25 over EP-001 pack/chunk texts for `repo`) as initial recommendation (plan A-EP002-4); list Options B/C as escalation only if NFR-001 fails with evidence — do **not** claim Confirmed store product; pick library as **Proposed** (e.g. `rank_bm25` or equivalent) without BRD pin
- [ ] T007 [P] Add/verify pytest layout stubs for EP-002 under `services/orchestrator/tests/{unit,integration,contract}/` aligned to EP-001 (`conftest.py` reuse)

**Checkpoint**: Scaffold + OQ register exist; no user-story hybrid/phase/citation behavior required yet

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before ANY user-story implementation. Consumes EP-001 packs/Qdrant; owns Confirmed `POST /context` contract stubs.

**⚠️ CRITICAL**: No user story work (Phases 3–5) may begin until this phase is complete

- [ ] T008 [API] [L5] Create Confirmed request/response Pydantic models in `services/orchestrator/app/api/schemas_context.py` matching api-contract §2.3: request `query`, `file` (optional), `repo`, `top_k`; response `final_context`, `metrics` (`tokens_before`, `tokens_after`, `saving_percent`, `trace`), `blast_radius`, `memory`, `relevant_files`, `is_real` — **no invented Confirmed fields** (FR-003, FR-004)
- [ ] T009 [P] [API] Stub `POST /context` router in `services/orchestrator/app/api/context.py` returning placeholder Confirmed response shape (`is_real=false` / empty meaningful fields allowed only until US-003 wires real retrieval) — wire orchestration in story phases (FR-009)
- [ ] T010 [API] Register context router in `services/orchestrator/app/main.py` and ensure OpenAPI surfaces `POST /context` (ADR-002; FR-009)
- [ ] T011 [P] [API] Extend `services/orchestrator/app/config.py` with **Proposed** knobs for MMR λ, BM25/vector fusion weights, default phase (e.g. Dev), candidate-pool size, pack cache dir reuse — document keys as **Proposed** (not Confirmed); reuse Qdrant URL / embedding model / `CONTEXTOS_PACK_CACHE_DIR`
- [ ] T012 [P] [Telemetry] Bootstrap OpenTelemetry-compatible helpers in `services/orchestrator/app/telemetry/context.py` with exporter-agnostic span stubs for `/context` latency and Proposed child spans (vector, BM25, MMR, pack assemble) — exporter vendor remains open (ADR-011)
- [ ] T013 [P] [L5] Add pack-loader helper (extend `services/orchestrator/app/services/l5_pack.py` or thin wrapper used by context pipeline) to load EP-001 `PackResult` / cache by `repo_name` for search/packing consumers — treat `xml_content` / `token_count` / `artifact_path` as **Proposed** handoff only (FR-010; OQ-PACK)
- [ ] T014 [P] [Security] Confirm reuse of `services/orchestrator/app/security/ignore_policy.py` and `consent_gate.py` from context path — EP-002 MUST NOT re-pack excluded paths from disk bypassing index/pack; reserve RBAC hook comment without inventing roles (FR-018; OQ-01; NFR-005/NFR-006)
- [ ] T015 [P] [Contract] Add contract test skeleton asserting Confirmed `POST /context` request/response field names only in `services/orchestrator/tests/contract/test_context_contract.py` (SC-006; FR-003, FR-004) — MUST fail/red until router returns real models
- [ ] T016 [P] [Discovery] [OQ-top_k] Document that `top_k` accepts positive integer only until product Confirms min/max/default; FR-02 “top 8” remains illustrative — no Confirmed bounds freeze in schemas or docs (FR-006)
- [ ] T017 [P] [Discovery] [OQ-HTTP-/context] Document Proposed status labels (`200`, `400`, `403`, `404`, `503`, …) for `POST /context` as **Proposed only** — do not Confirmed-freeze in OpenAPI as Appendix D Confirmed (FR-020)
- [ ] T018 [P] [Discovery] [OQ-MVP-metrics] Document MVP `metrics` semantics: packing token counts acceptable (A-06); do not invent `saving_percent` pass thresholds (FR-017; SC-008)
- [ ] T019 [P] [Discovery] [OQ-recall-harness] Document that SC-003 / FR-008 recall@10 >0.92 verification is **blocked** until evaluation harness/dataset exists — tasks T050–T051 must remain blocked for pass claims (constitution Verification Gate)
- [ ] T020 [P] [Discovery] Assess availability of 500k LOC indexed fixture for SC-002 / NFR-001 p95 measurement — if unavailable, record gap and mark perf tasks blocked/skipped (no invented pass)

**Checkpoint**: Foundation ready — Confirmed schemas + router stub + pack load + OQ discoveries recorded; user stories may begin

---

## Phase 3: User Story 1 — Hybrid Semantic Search with MMR (US-003) (Priority: P1) 🎯 MVP

**Goal**: Answer “where is X?” via `POST /context` using hybrid BM25 + vector retrieval with MMR re-ranking over EP-001 packs/Qdrant; return ranked `relevant_files` with scores and Confirmed response skeleton (minimal `final_context` of top files acceptable before full phase templates).

**Independent Test**: Against an EP-001-indexed fixture repo, `POST /context` with Confirmed fields returns hybrid+MMR ranked files with scores; `is_real` true; `blast_radius`/`memory` MAY be empty/null (**Proposed** MVP). Measure p95 when fixture allows; recall@10 blocked until harness.

**Layers/Surfaces**: `[L5]` `[API]` `[Telemetry]` `[Security]`

### Clarification / Discovery (US-003)

- [ ] T021 [US003] [Discovery] [OQ-BM25-store] Lock implementation note to **Proposed Option A** in `services/orchestrator/app/adapters/bm25_store.py` (in-process over pack/chunks) unless product Confirms otherwise — escalate B/C only with measured NFR evidence; keep OQ open
- [ ] T022 [US003] [Discovery] [OQ-PACK] Before asserting pack field names in tests beyond Proposed handoff, re-confirm no Confirmed freeze — tests may use `PackResult` attributes as **Proposed** only

### Tests for User Story 1 (write first; expect fail/red until implementation)

- [ ] T023 [P] [US003] [Unit] Write unit tests for score fusion + MMR ordering/diversity in `services/orchestrator/tests/unit/test_mmr_fusion.py` (FR-002; ADR-014) — fail until `l5_search` implements MMR
- [ ] T024 [P] [US003] [Unit] Write unit tests for request validation (empty/invalid `query`, non-positive `top_k`) in `services/orchestrator/tests/unit/test_context_validation.py` — Proposed `400` labels only (FR-006, FR-020)
- [ ] T025 [P] [US003] [Contract] Extend `services/orchestrator/tests/contract/test_context_contract.py` to assert Confirmed response fields present and `relevant_files` carries scores behaviorally (exact item keys **Proposed**) (FR-004, FR-005, FR-006; SC-006)
- [ ] T026 [P] [US003] [Integration] Write integration test against indexed fixture + Qdrant: `POST /context` returns ranked `relevant_files` with scores, `is_real=true`, `blast_radius`/`memory` empty/null allowed in `services/orchestrator/tests/integration/test_context_hybrid_search.py` (SC-001; FR-001..006, FR-009, FR-010)
- [ ] T027 [P] [US003] [Integration] Write hybrid-signal behavioral test (keyword-heavy vs semantic-heavy queries exercise both BM25 and vector paths) in `services/orchestrator/tests/integration/test_context_hybrid_signals.py` (FR-001; ADR-014) — without requiring Confirmed BM25 product name
- [ ] T028 [P] [US003] [Security] [Integration] Write privacy inheritance test: `/context` response MUST NOT introduce excluded paths (`.env`, secrets, ignored, binaries) absent from EP-001 pack/index in `services/orchestrator/tests/integration/test_context_exclusions.py` (FR-018; NFR-004/NFR-005)
- [ ] T029 [US003] [Perf] Add performance harness task/script for semantic search p95 <800ms @ 500k LOC index in `services/orchestrator/tests/integration/test_context_search_perf.py` (or `tests/perf/`) — **blocked/skipped** if 500k fixture unavailable (T020); do not invent pass (FR-007; NFR-001; SC-002)
- [ ] T030 [US003] [Discovery] [OQ-recall-harness] Create **blocked** placeholder for recall@10 >0.92 harness in `services/orchestrator/tests/integration/test_context_recall_at_10.py` (or `tests/eval/`) documenting Missing Evidence dataset — MUST NOT claim Pass; SC-003 / FR-008 verification blocked until harness exists

### Implementation for User Story 1

- [ ] T031 [P] [US003] [L5] Extend `services/orchestrator/app/adapters/qdrant_store.py` with filtered vector search by `repo_name` (and optional `file` bias as **Proposed**) over collection `codebase` — **Proposed** payload index on `repo_name` if missing for latency (FR-001, FR-010)
- [ ] T032 [P] [US003] [L5] Reuse `services/orchestrator/app/adapters/embeddings.py` to embed query vectors (384-dim MiniLM) for search path (FR-001; ADR-003)
- [ ] T033 [US003] [L5] Implement **Proposed** BM25 adapter in `services/orchestrator/app/adapters/bm25_store.py` (Option A: build/query over pack XML / chunk texts for `repo`; optional per-process cache keyed by `repo_name` + content hash) — label Proposed; OQ-BM25-store remains open (FR-001; T021)
- [ ] T034 [US003] [L5] Implement hybrid retrieval + **Proposed** tunable score fusion + MMR re-ranking in `services/orchestrator/app/services/l5_search.py` producing ranked hits with scores for `relevant_files` / packing candidates (FR-001, FR-002, FR-006; ADR-014)
- [ ] T035 [US003] [API] Wire `POST /context` in `services/orchestrator/app/api/context.py` to: validate Confirmed fields → load pack/index for `repo` → hybrid+MMR → populate `relevant_files`, minimal `final_context`, `metrics` skeleton (packing counts **Proposed**), `is_real=true`, empty/null `blast_radius`/`memory` (**Proposed**) (FR-003..006, FR-009, FR-010, FR-017, FR-020)
- [ ] T036 [US003] [API] Map unknown/not-indexed `repo` and invalid inputs to **Proposed** status labels (`404` / `400`) without Confirmed freeze; prefer degraded partial results over hard-fail-all when partial index allows (NFR-007; FR-020) — no EP-005 operator UX
- [ ] T037 [US003] [Telemetry] Instrument search latency spans (vector / BM25 / MMR / total) via `services/orchestrator/app/telemetry/context.py` from context router (ADR-011)
- [ ] T038 [US003] [Docs] Label OpenAPI descriptions for any Proposed extensions (`relevant_files[]` item shape, status codes) as **Proposed** — Confirmed request remains `query`/`file`/`repo`/`top_k` only (FR-003, FR-019 consumer note: CLI/extension may call same API later; **no** CLI/extension DX implementation)

**Checkpoint**: US-003 independently delivers hybrid “where is X?” via `POST /context` without requiring phase template matrix or citation schema freeze. SC-001/SC-006 partial met when tests pass; SC-002/SC-003 remain fixture/harness gated.

---

## Phase 4: User Story 2 — Phase-Aware Prompt Templates (US-004) (Priority: P1)

**Goal**: Assemble context packs using code2prompt-style templates scoped to SDLC phases Requirements / Design / Dev / Test / Deploy; pack composition differs by phase for the same query/repo. Full L4 Headroom **out of scope** (FR-014; ADR-006).

**Independent Test**: Same query/repo under two supported phases yields different pack composition; five named phases supported as product concepts. Phase wire shape remains OQ-16 (**Proposed** mechanism only).

**Depends on**: US-003 candidate retrieval (`l5_search` / `relevant_files`).

**Layers/Surfaces**: `[L5]` `[API]`

### Clarification / Discovery (US-004)

- [ ] T039 [US004] [Discovery] [OQ-16] Select one **Proposed** phase-selection mechanism without Confirmed wire freeze: (a) optional Proposed request field (e.g. `phase`) labeled Proposed in OpenAPI **or** (b) config/default phase (e.g. Dev) + test injection — record choice in EP-002 open-questions notes; Confirmed request remains without phase until product Confirms (FR-013; A-EP002-5)
- [ ] T040 [US004] [Discovery] Confirm code2prompt **style** templates may be in-house under `services/orchestrator/app/services/l5_phase_pack.py` (or `templates/`) — concrete package pin **NEEDS CLARIFICATION**; do not claim Confirmed package

### Tests for User Story 2

- [ ] T041 [P] [US004] [Unit] Write unit tests that each of 5 phases produces distinct composition for a fixed candidate set in `services/orchestrator/tests/unit/test_phase_templates.py` (FR-011, FR-012; SC-004)
- [ ] T042 [P] [US004] [Integration] Write integration test: same query/repo, two phases → different `final_context` composition via Proposed OQ-16 mechanism in `services/orchestrator/tests/integration/test_context_phase_packing.py` (SC-004)
- [ ] T043 [P] [US004] [Unit/Integration] Assert no Headroom / full L4 budget gate required for packing success (SC-007; FR-014) in `services/orchestrator/tests/unit/test_phase_no_l4_gate.py` (or assert within T042)
- [ ] T044 [P] [US004] [Unit] Assert `metrics` object always present with Confirmed keys; MVP values may be packing token counts only — no `saving_percent` threshold invent in `services/orchestrator/tests/unit/test_context_metrics_mvp.py` (FR-017; SC-008; OQ-MVP-metrics)

### Implementation for User Story 2

- [ ] T045 [US004] [L5] Implement code2prompt-style phase templates for Requirements, Design, Dev, Test, Deploy in `services/orchestrator/app/services/l5_phase_pack.py` (FR-011)
- [ ] T046 [US004] [L5] Assemble `final_context` from hybrid candidates under selected phase so composition differs by phase scoping (FR-012; SC-004)
- [ ] T047 [US004] [API] Integrate phase pack into `services/orchestrator/app/api/context.py` pipeline after hybrid+MMR; apply **Proposed** OQ-16 selection from T039 — reject unsupported phase values if Proposed field used; do **not** add Confirmed request field to Appendix D claims (FR-013)
- [ ] T048 [US004] [API] Populate MVP `metrics` with packing token counts (**Proposed** per A-06 / OQ-MVP-metrics); leave full compression semantics to V1/L4 (FR-014, FR-017)
- [ ] T049 [US004] [Docs] Document five phase concepts + Proposed selection mechanism in OpenAPI description / optional `specs/ep-002-l5-hybrid-search-phase-packing/quickstart.md` — label Proposed; no Confirmed phase wire freeze

**Checkpoint**: US-004 independently proves phase-scoped packing differences; no L4 product gate. SC-004/SC-007 addressed when tests pass.

---

## Phase 5: User Story 3 — Provenance Citations (US-015) (Priority: P1)

**Goal**: Successful packed `final_context` includes provenance citations with **file:line** and **confidence** (BRD §14). Exact JSON citation schema remains OQ-11 — do **not** invent Confirmed field names.

**Independent Test**: Inspect `final_context` from successful `POST /context` for file:line + confidence attributes (presence), without asserting invented JSON keys.

**Depends on**: US-003 retrieval + US-004 packing path.

**Layers/Surfaces**: `[L5]` `[API]` `[Security]`

### Clarification / Discovery (US-015)

- [ ] T050 [US015] [Discovery] [OQ-11] Document **Proposed** interim citation representation (e.g. XML/attributes or delimited blocks inside packed string) satisfying file:line + confidence — do **not** Confirmed-freeze JSON schema (FR-016)

### Tests for User Story 3

- [ ] T051 [P] [US015] [Unit] Write unit tests asserting citation **attributes** file:line + confidence present in packed string output without asserting invented Confirmed JSON keys in `services/orchestrator/tests/unit/test_citations.py` (FR-015, FR-016; SC-005)
- [ ] T052 [P] [US015] [Integration] Write integration test: successful `POST /context` `final_context` includes file:line + confidence; Confirmed response fields remain coherent (`is_real`, `relevant_files`, `metrics`) in `services/orchestrator/tests/integration/test_context_citations.py` (SC-005, SC-006)
- [ ] T053 [P] [US015] [Contract] Regression-extend `services/orchestrator/tests/contract/test_context_contract.py` for Confirmed field presence after citation wiring (SC-006)

### Implementation for User Story 3

- [ ] T054 [US015] [L5] Implement citation/provenance helper in `services/orchestrator/app/services/l5_citations.py` attaching file:line + confidence into packed context per BRD §14 using **Proposed** interim representation from T050 (FR-015; constitution III)
- [ ] T055 [US015] [L5] Integrate citations into `l5_phase_pack` / context pipeline so successful packs always include citation attributes (FR-015)
- [ ] T056 [US015] [API] Ensure `POST /context` successful responses keep Confirmed fields coherent; do not invent parallel Confirmed citation JSON objects (FR-004, FR-016)
- [ ] T057 [US015] [Docs] Document citation attribute requirements (file:line + confidence) and OQ-11 open status in OpenAPI notes / quickstart — Proposed only

**Checkpoint**: US-015 independently verifiable via `final_context` inspection. SC-005 met on attribute presence; Confirmed citation JSON still open.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reliability notes, OpenAPI labeling, perf/recall gap documentation, EP-001 regression, security, telemetry, deployment readiness — no out-of-scope epics.

- [ ] T058 [P] [L5] Add/extend degraded/partial-index behavior tests where feasible (reduced `relevant_files` + trace note vs hard-fail-all) in `services/orchestrator/tests/integration/test_context_degraded.py` — no EP-005 health UX (NFR-007)
- [ ] T059 [P] [API] [Docs] Review OpenAPI for `POST /context`: Confirmed fields unlabeled as Proposed; all Proposed extensions (`phase`, status codes, `relevant_files` item keys, citation interim shape) explicitly labeled Proposed
- [ ] T060 [Perf] Attempt NFR-001 p95 measurement at 500k LOC when fixture available (revisit T029); if blocked, document gap in validation later — **do not invent pass** (SC-002)
- [ ] T061 [Discovery] [OQ-recall-harness] Confirm SC-003 remains blocked in task/validation notes until harness/dataset supplied — no invented recall Pass (SC-003; FR-008)
- [ ] T062 [P] [Regression] Ensure EP-001 `POST /index` / pack / exclusion / no-exfil / consent deny-by-default tests remain green under `services/orchestrator/tests/`
- [ ] T063 [P] [Security] Verify context path does not re-read `.env`/ignored/secrets/binaries from disk to “help” packing; path-traversal / input sanitization for `query`/`repo`/`file` (FR-018; Security Considerations)
- [ ] T064 [P] [Security] Confirm clients cannot bypass orchestrator validation/policy for search/packing (FR-009; constitution V) — API-only delivery; no CLI/extension search reimplementation in this epic (FR-019)
- [ ] T065 [P] [Telemetry] Verify `/context` spans emit duration for search vs pack assemble via `telemetry/context.py` (exporter vendor still open)
- [ ] T066 [P] [Docs] Author or update optional `specs/ep-002-l5-hybrid-search-phase-packing/quickstart.md` for Compose + index-then-`POST /context` smoke (reuse `deploy/docker-compose.yml`) — no invented Confirmed contracts
- [ ] T067 [P] [Deploy] Docker Compose smoke: API + Qdrant; EP-001 `POST /index` then `POST /context` returns files (E2E smoke) — CLI/extension Ask **not** required
- [ ] T068 [P] Document FR-019 consumer note only: future `contextos ask` / extension Ask SHOULD call `POST /context` — **do not** implement CLI epic or extension DX here
- [ ] T069 Explicitly confirm out-of-scope exclusions remain unscheduled: Serena/L3, L1 blast, L4 Headroom product, L2/L6, EP-004 CLI surface, extension DX
- [ ] T070 [P] [Discovery] [OQ-01] Document RBAC/authn schema still Missing Evidence — reserve hook only; local/dev loopback MAY apply (A-05; NFR-006)

**Checkpoint**: Polish complete; ready for validation-report agent (with SC-002/SC-003 gaps labeled if still blocked)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately on feature branch
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US-003 (Phase 3)**: Depends on Foundational; consumes EP-001 pack/Qdrant — **MVP path**
- **US-004 (Phase 4)**: Depends on Foundational + US-003 candidate retrieval
- **US-015 (Phase 5)**: Depends on Foundational + US-003 + US-004 packing path
- **Polish (Phase 6)**: Depends on desired user stories complete (prefer all three for full SC coverage)

### User Story Dependencies

```text
Phase 1 Setup
    → Phase 2 Foundational (BLOCKING)
        → Phase 3 US-003 (Hybrid + MMR) 🎯 MVP
            → Phase 4 US-004 (Phase templates)
                → Phase 5 US-015 (Citations)
                    → Phase 6 Polish
```

- **US-003 (P1)**: No dependency on US-004/US-015 — independently testable after Foundational
- **US-004 (P1)**: Needs hybrid candidates from US-003; independently testable for phase composition
- **US-015 (P1)**: Needs packed `final_context` path from US-004; independently verifiable via citation attributes

### Within Each User Story

1. Discovery tasks for open OQs (Proposed only)
2. Tests written (expect fail/red) before or with implementation
3. Adapters/services before API wiring
4. Telemetry/docs after core behavior
5. Story checkpoint before next priority dependency

### Parallel Opportunities

| Window | Parallel tasks |
|--------|----------------|
| Phase 1 | T002–T007 (different files / docs) |
| Phase 2 | T008 vs T011–T014 vs T015–T020 after T009/T010 sequencing for router registration |
| US-003 tests | T023–T028 in parallel; T029–T030 gated |
| US-003 impl | T031–T032 parallel; then T033→T034→T035 |
| US-004 tests | T041–T044 in parallel after T039 |
| US-015 tests | T051–T053 in parallel after T050 |
| Polish | T058–T070 largely parallel across files |

### Dependency Graph (summary)

```text
T001–T007 (Setup)
    └─ T008–T020 (Foundational)
           └─ US-003: T021–T038
                  └─ US-004: T039–T049
                         └─ US-015: T050–T057
                                └─ Polish: T058–T070
```

Blocked verification edges (non-blocking for implementation intent):

```text
T019/T030/T061 ──blocks──► SC-003 pass claims (OQ-recall-harness)
T020/T029/T060 ──may block──► SC-002 pass claims (500k fixture)
T002/T022       ──blocks──► Confirmed pack schema freeze (OQ-PACK)
T039            ──blocks──► Confirmed phase wire freeze (OQ-16)
T050            ──blocks──► Confirmed citation JSON freeze (OQ-11)
```

---

## Parallel Example: User Story 1 (US-003)

```bash
# Launch US-003 tests together (after Foundational):
Task: "Unit MMR/fusion tests in services/orchestrator/tests/unit/test_mmr_fusion.py"
Task: "Unit validation tests in services/orchestrator/tests/unit/test_context_validation.py"
Task: "Contract tests in services/orchestrator/tests/contract/test_context_contract.py"
Task: "Integration hybrid search in services/orchestrator/tests/integration/test_context_hybrid_search.py"

# Launch adapters in parallel where safe:
Task: "Extend qdrant_store search in services/orchestrator/app/adapters/qdrant_store.py"
Task: "Reuse embeddings query encode in services/orchestrator/app/adapters/embeddings.py"
# Then BM25 → l5_search → context router sequentially
```

---

## Implementation Strategy

### MVP First (US-003 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundational (CRITICAL)
3. Complete Phase 3 US-003 (hybrid + MMR via `POST /context`)
4. **STOP and VALIDATE**: SC-001 + partial SC-006; note SC-002/SC-003 gates
5. Demo API search without phase/citation polish if needed

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US-003 → hybrid search demo (MVP “Search works” contribution)
3. US-004 → phase-aware packing demo (basic prompt packing)
4. US-015 → Pack & Cite attributes demo
5. Polish → validation-report ready (with harness gaps labeled)

### Parallel Team Strategy

- Dev A: Foundational schemas/router + US-003 search pipeline
- Dev B: BM25 adapter + MMR unit tests + perf harness scaffolding
- Dev C (after US-003 candidates): US-004 templates → US-015 citations
- Shared: OQ discovery docs; no Confirmed freezes without product

---

## Definition of Done

- [ ] All FR-001..FR-020 have implementation and verification coverage (open FRs via discovery / Proposed-only / blocked-harness tasks — not invented Confirmed resolutions)
- [ ] User stories US-003, US-004, US-015 independently testable at their checkpoints
- [ ] SC-001, SC-004, SC-005, SC-006, SC-007 addressed with planned tests; SC-002 gated on 500k fixture; SC-003 **blocked** until OQ-recall-harness; SC-008 no invented `saving_percent` thresholds
- [ ] Security: privacy inheritance, no index-exfil assumption, orchestrator ownership verified
- [ ] Telemetry: `/context` latency spans instrumented (exporter vendor open)
- [ ] OpenAPI/docs label Proposed vs Confirmed correctly
- [ ] Open questions remain explicitly unresolved unless product clarifies
- [ ] No scope creep into Serena, L1 blast, L4 product, L2/L6, CLI epic, extension DX
- [ ] Constitution Task Gate criteria met
- [ ] **No invented Pass/Fail test execution results** in this artifact (Verification Gate)

---

## Evidence Reviewed

| Artifact | Path / ID |
|----------|-----------|
| Feature spec | `specs/ep-002-l5-hybrid-search-phase-packing/spec.md` |
| Implementation plan | `specs/ep-002-l5-hybrid-search-phase-packing/plan.md` |
| Constitution Task Gate | `.specify/memory/constitution.md` v1.0.0 |
| Tasks template | `.specify/templates/tasks-template.md` |
| API contract | `docs/architecture/api-contract.md` §2.3 `POST /context` |
| ADR-014 | Hybrid BM25+vector+MMR; BM25 placement Missing Evidence |
| ADR-006 | L4 compression not MVP gate |
| ADR-011 | OTel-compatible; exporter open |
| EP-001 OQ-PACK | `specs/ep-001-l5-repository-packing-indexing/open-questions.md` |
| EP-001 pack handoff | `services/orchestrator/app/services/l5_pack.py` `PackResult` (Proposed) |
| Live tree | `services/orchestrator/app/**` Confirmed EP-001 modules to reuse/extend |

---

## Open Questions / Discovery Tasks

| OQ ID | Task IDs | Blocking? | Resolution status in tasks |
|-------|----------|-----------|----------------------------|
| OQ-16 | T005, T039, T047, T049 | **Blocks Confirmed phase wire freeze** | Proposed mechanism only; five phases still required |
| OQ-11 | T005, T050, T051, T054, T057 | **Blocks Confirmed citation JSON freeze** | Require file:line + confidence attributes |
| OQ-PACK | T002, T005, T013, T022 | **Blocks Confirmed pack contract freeze** | Consume Proposed `PackResult`/cache only |
| OQ-top_k | T005, T016, T024, T035 | Blocks numeric AC freeze | Positive integer only; no min/max invent |
| OQ-MVP-metrics | T005, T018, T044, T048 | Blocks Confirmed metric interpretation | Packing counts Proposed (A-06) |
| OQ-recall-harness | T005, T019, T030, T061 | **Blocks SC-003 verification pass claims** | Placeholder blocked; no invented Pass |
| OQ-BM25-store | T005, T006, T021, T033 | Design Missing Evidence | Proposed Option A first |
| OQ-HTTP-/context | T005, T017, T036, T059 | Non-blocking for functional draft | Proposed codes labeled only |
| OQ-01 | T005, T014, T070 | Non-blocking for MVP search intent | Hook reserved; no invented RBAC |

---

## Task Traceability Matrix

| Task / Phase | Source Requirement | Plan Reference | Evidence |
|--------------|-------------------|----------------|----------|
| Phase 1 T001–T007 | Setup; EP-001 consume; OQ register | Plan Phase 0; Project Structure | Live tree; OQ-PACK |
| Phase 2 T008–T020 | FR-003/004/009/010; telemetry; OQ discoveries | Plan Phase 0; API Design | api-contract §2.3; ADR-011 |
| Phase 3 US-003 T021–T038 | FR-001..010, FR-017..020; SC-001..003, SC-006; NFR-001 | Plan Phase 1 | ADR-014; BRD FR-02 §10 §12 |
| Phase 4 US-004 T039–T049 | FR-011..014, FR-017; SC-004, SC-007, SC-008 | Plan Phase 2 | BRD FR-03 §8 §15; ADR-006 |
| Phase 5 US-015 T050–T057 | FR-015..016; SC-005, SC-006 | Plan Phase 3 | BRD §14; constitution III |
| Phase 6 T058–T070 | NFR-004..007; FR-009/018/019; docs/deploy/regression | Plan Phase 4 | Constitution Task Gate |
| Discovery OQs | All OQs in Open Questions table | Plan Open Questions | Spec Open Questions |

### FR → Task Coverage (implementation + verification)

| FR | Implementation tasks | Verification tasks |
|----|---------------------|-------------------|
| FR-001 | T031, T032, T033, T034, T035 | T026, T027 |
| FR-002 | T034 | T023, T026 |
| FR-003 | T008, T009, T010, T035 | T015, T025 |
| FR-004 | T008, T035, T056 | T015, T025, T053 |
| FR-005 | T035 | T026, T025 |
| FR-006 | T034, T035; T016 (bounds open) | T024, T025, T026 |
| FR-007 | T037; T029/T060 (perf) | T029, T060 (fixture-gated) |
| FR-008 | — (harness gap) | T019, T030, T061 (**blocked** until harness) |
| FR-009 | T009, T010, T035 | T026, T064 |
| FR-010 | T002, T013, T031, T035 | T022, T026 |
| FR-011 | T045, T046 | T041, T042 |
| FR-012 | T046, T047 | T041, T042 |
| FR-013 | T039, T047 | T039 discovery (no Confirmed freeze) |
| FR-014 | T048; T069 (OOS) | T043 |
| FR-015 | T054, T055 | T051, T052 |
| FR-016 | T050, T054, T056 | T051 (no invented keys) |
| FR-017 | T018, T048 | T044 |
| FR-018 | T014, T035 | T028, T063 |
| FR-019 | T038, T068, T069 | T068 (consumer note only — no DX deliverable) |
| FR-020 | T017, T036 | T024, T036, T059 |

### NFR / SC → Verification

| Claim | Tasks | Notes |
|-------|-------|-------|
| NFR-001 / SC-002 p95 <800ms @ 500k | T020, T029, T060 | Blocked/skipped if fixture missing |
| NFR-004 / NFR-005 privacy inherit | T028, T063 | — |
| NFR-006 authn open | T014, T070 | A-05 loopback OK |
| NFR-007 degraded search | T036, T058 | No EP-005 UX |
| SC-001 hybrid ranked files | T026, T027, T034, T035 | — |
| SC-003 recall@10 >0.92 | T019, T030, T061 | **Blocked** — OQ-recall-harness |
| SC-004 phase composition | T041, T042, T045–T047 | OQ-16 Proposed wire |
| SC-005 citations attributes | T051, T052, T054–T055 | OQ-11 open |
| SC-006 Confirmed fields | T015, T025, T053 | — |
| SC-007 Search works w/o full L4 | T043, T048 | ADR-006 |
| SC-008 MVP metrics | T018, T044, T048 | No invent thresholds |

---

## Constitution Compliance (Task Gate)

| Gate Check | Status |
|------------|--------|
| Every requirement has implementation and verification coverage | **Met** (FR-001..020; open items via discovery/Proposed/blocked-harness) |
| Tasks grouped by independently deliverable user story | **Met** (US-003, US-004, US-015) |
| Exact paths when known; discovery for unknowns | **Met** (`services/orchestrator/...`; OQ discoveries) |
| Tests for measurable intelligence claims | **Met** (p95 + recall harness tasks; no invented Pass results) |
| Security, documentation, telemetry, deployment where applicable | **Met** (Phases 2, 3, 6) |
| OQs carried as clarification — not Confirmed-frozen | **Met** |
| Out-of-scope epics not scheduled as deliverables | **Met** (T069) |

**Task Gate**: **Yes** — ready for Test Validation / implement sequencing with open clarifications and harness/fixture blockers remaining.

---

## Notes

- `[P]` = different files, safe parallelization
- Do **not** mark tasks complete in this file until implementation evidence exists
- Do **not** invent Pass/Fail execution results here (constitution Verification Gate)
- Commit after each task or logical group during implement phase
- Stop at any story checkpoint to validate independently
- Still **no** application source code is produced by the task-generator agent itself
- Stay on branch `feature/ep-002-l5-hybrid-search-phase-packing` — no push/merge from this agent
