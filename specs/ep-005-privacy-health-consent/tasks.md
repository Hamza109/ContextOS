# Tasks: EP-005 Privacy Defaults, Health & Consent

**Input**: Design documents from `/specs/ep-005-privacy-health-consent/`

**Prerequisites**: `plan.md`, `spec.md` (US-013, US-014). Do **not** require or create `quickstart.md`, `open-questions.md`, or `out-of-scope-notes.md`.

**Tests**: Required — constitution III/V privacy + client boundaries; SC-001..SC-006, SC-008 measurable acceptance. **SC-007** (99.5% uptime) is **blocked** on **OQ-Uptime-Harness** — no Pass claim tasks.

**Organization**: Grouped by user story. Gap-fill only vs existing `IgnorePolicy` / `GET /` / `l5_search` / EP-001/002/004 — **no** L5/L3/CLI rebuild.

**Label rule**: Items marked **Proposed** MUST NOT be Confirmed-frozen. Do not invent unsupported APIs, metrics, or Pass criteria.

**Stories**: US-013, US-014 only. **OOS**: US-016, JetBrains, L1/L4, L2/L6, EP-004 rebuild, full RBAC.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: `[US1]` = US-013; `[US2]` = US-014
- **[Layer/Surface]**: `[L5]`, `[API]`, `[Security]`, `[VSCode]`, `[CLI]` as applicable
- Exact repository-relative paths included when known

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm gap matrix and fixtures before any story work. No new subsystems.

- [ ] T001 Inventory EP-005 gap matrix against cited modules: `services/orchestrator/app/security/ignore_policy.py`, `adapters/fs_walker.py`, `api/health.py`, `api/index.py`, `services/l5_index.py`, `services/l5_pack.py`, `services/l5_search.py`, `api/context.py`; record Confirmed vs Proposed gaps only (cite `plan.md` Gap Analysis — do not invent new endpoints)
- [ ] T002 [P] Inventory existing tests to extend (not replace): `services/orchestrator/tests/unit/test_ignore_policy.py`, `test_packer_exclusions.py`, `test_fs_walker.py`, `test_packer_binary_skip.py`; `integration/test_index_exclusions_qdrant.py`, `test_context_exclusions.py`, `test_context_degraded.py`; client: `clients/vscode/tests/no_client_policy_bypass.test.ts`, `clients/cli/tests/ask.test.ts`
- [ ] T003 [P] Confirm OOS boundaries in task execution notes: no US-016 consent work, no RBAC invent (OQ-01), no JetBrains/L1/L4/L2/L6/EP-004 rebuild, no Confirmed override UX (**OQ-OVERRIDE**)

**Checkpoint**: Gap inventory complete — foundational fixtures may begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared fixture + labeling conventions that BOTH stories reuse. **Blocks** US-013 and US-014 implementation/acceptance hardening.

**⚠️ CRITICAL**: No user-story acceptance hardening until this phase completes

- [ ] T004 Create or extend a shared ignore-exclusion fixture repository under `services/orchestrator/tests/fixtures/` (or extend existing tmp_path patterns) containing: `.gitignore`-matched paths, `.env`, secret-like files, `node_modules/`, `dist/`, `.git/`, and a binary sample — for packs **and** embeddings e2e (SC-001; FR-001, FR-002)
- [ ] T005 [P] Document in test module docstrings that HTTP status codes for `GET /` and degraded `POST /context` remain **Proposed** only (**OQ-HTTP-Health**, **OQ-Degraded-Shape**) — MUST NOT Confirmed-freeze in assertions comments
- [ ] T006 [P] Document that **OQ-Uptime-Harness** blocks SC-007 Pass; any uptime-related note is tracking-only, not a Pass gate
- [ ] T007 [P] Confirm no Confirmed “approved override” entity or API will be added (**OQ-OVERRIDE** / FR-003 / SC-002) — defaults stay enforced

**Checkpoint**: Foundation ready — US-013 and US-014 may proceed (parallel if staffed)

---

## Phase 3: User Story 1 — Indexing Ignore Rules & Secret Exclusion (US-013, Priority: P1) 🎯 MVP

**Goal**: Orchestrator-enforced `.gitignore` + hard exclusions on pack/index; clients MUST NOT bypass; no Confirmed override UX.

**Independent Test**: Index fixture repo via orchestrated `POST /index` path; excluded paths absent from packs **and** embeddings; VS Code/CLI negative/boundary checks prove no local policy bypass.

**Layers/Surfaces**: `[L5]` `[API]` `[Security]` `[VSCode]` `[CLI]`

### Tests for User Story 1

> Write/extend tests so they fail on regressions before gap-fill; measure SC-001, SC-002, SC-003.

- [ ] T008 [P] [US1] [Security] Extend unit coverage in `services/orchestrator/tests/unit/test_ignore_policy.py` for `.gitignore` respect + hard exclusions (`.env`, secrets, build/deps examples `node_modules`/`dist`, `.git`, binaries) — FR-001, FR-002
- [ ] T009 [P] [US1] [L5] Extend `services/orchestrator/tests/unit/test_packer_exclusions.py` and/or `test_packer_binary_skip.py` so excluded paths are absent from pack XML/output — SC-001 packs half
- [ ] T010 [P] [US1] [L5] Extend `services/orchestrator/tests/unit/test_fs_walker.py` so `walk_allowed_files` never yields fixture excluded paths — FR-001, FR-002
- [ ] T011 [US1] [L5] [API] Extend `services/orchestrator/tests/integration/test_index_exclusions_qdrant.py` (and pack assertions as needed) into full fixture e2e: after `run_index` / `POST /index`, excluded paths absent from **packs and embeddings/Qdrant payloads** — SC-001; FR-005 cite EP-001 (do not re-spec packing product)
- [ ] T012 [P] [US1] [Security] Add/extend negative test asserting default exclusions remain in force with **no** Confirmed override path shipped (assert absence of override API/flag or document OQ-OVERRIDE open) — FR-003, SC-002; **Proposed** only for any future override
- [ ] T013 [P] [US1] [VSCode] Extend `clients/vscode/tests/no_client_policy_bypass.test.ts` for EP-005 SC-003: extension MUST NOT implement local ignore/pack/upload of excluded paths; `indexClient` / auto-index only call orchestrator — FR-004
- [ ] T014 [P] [US1] [CLI] Extend `clients/cli/tests/ask.test.ts` (or add focused boundary test under `clients/cli/tests/`) asserting CLI has no local `IgnorePolicy` / pack engine and cannot force-index excluded paths around orchestrator — FR-004, SC-003

### Implementation for User Story 1

- [ ] T015 [US1] [Security] Gap-fill only in `services/orchestrator/app/security/ignore_policy.py` if T008–T011 fail (gitignore/hard-exclusion edges) — no full git-engine invent; no Confirmed override (**OQ-OVERRIDE**)
- [ ] T016 [US1] [L5] Gap-fill only in `services/orchestrator/app/adapters/fs_walker.py` if walker allow-list leaks excluded paths — FR-001, FR-002
- [ ] T017 [US1] [L5] [API] Verify `services/orchestrator/app/api/index.py` + `services/l5_index.py` + `l5_pack.py` apply `IgnorePolicy` on full and scoped index (`paths`/`files` filtered after allow-list) — FR-005; cite EP-001; fix only if SC-001 fails
- [ ] T018 [US1] [VSCode] Boundary review only on `clients/vscode/src/api/indexClient.ts`, `indexing/autoIndex.ts`, `extension.ts` — ensure thin client; **no** DX rebuild (A-EP005-3)
- [ ] T019 [US1] [CLI] Boundary review only under `clients/cli/` — ensure thin client; **no** CLI rebuild
- [ ] T020 [US1] [Security] Confirm secret-glob inventory extensions (if any) do not invent Confirmed product UX or override workflow — FR-002, FR-003

**Checkpoint**: US-013 independently verifiable — SC-001, SC-002, SC-003; clients cannot bypass orchestrator ignore policy

---

## Phase 4: User Story 2 — Health Endpoint & Graceful Degraded Search (US-014, Priority: P1)

**Goal**: Confirmed `GET /` fields (pipeline + Qdrant; Falkor unused OK per **A-07**); graceful degraded search under partial failure; HTTP/degraded shapes stay **Proposed**.

**Independent Test**: Call `GET /` and assert Confirmed fields; Falkor unused/absent does not alone fail MVP search; induce partial index/dependency failure and verify `POST /context` prefers degraded discovery over hard-fail-all when possible.

**Layers/Surfaces**: `[API]` `[L5]` `[Telemetry]` (health/degrade notes only)

### Tests for User Story 2

- [ ] T021 [P] [US2] [API] Add contract/unit tests (e.g. `services/orchestrator/tests/contract/test_health_contract.py` and/or unit under `tests/unit/`) asserting `GET /` JSON includes Confirmed fields `status` (`ok|degraded|error`), `pipeline`, `falkor`, `qdrant` — FR-006, SC-004; cite api-contract §2.1
- [ ] T022 [P] [US2] [API] Add A-07 acceptance test: when Falkor reports `unused`/absent and Qdrant/`pipeline` are healthy, health `status` is not forced to `error` solely by Falkor absence; MVP search path remains usable — FR-007, SC-005, NFR-007
- [ ] T023 [US2] [L5] [API] Extend `services/orchestrator/tests/integration/test_context_degraded.py` for partial-index / partial-dependency failure: `POST /context` returns usable degraded discovery when possible rather than hard-failing all discovery — FR-009, SC-006; **do not** invent Confirmed response fields (**OQ-Degraded-Shape**)
- [ ] T024 [P] [US2] [API] In health/degraded tests, label HTTP status assertions as **Proposed** only (e.g. existing always-200 vs Proposed `200`/`503`) — FR-008, SC-008; **OQ-HTTP-Health** — MUST NOT Confirmed-freeze status codes
- [ ] T025 [P] [US2] [L5] Strengthen Qdrant-down / pack-miss cases in `test_context_degraded.py` (behavioral degrade vs total outage); keep `metrics.trace.degraded` / `notes` labeled **Proposed** observability (P-1), not Appendix D Confirmed — FR-010

### Implementation for User Story 2

- [ ] T026 [US2] [API] Gap-fill only in `services/orchestrator/app/api/health.py` to ensure Confirmed fields + pipeline/Qdrant reporting + A-07 Falkor unused semantics — FR-006, FR-007; HTTP status mapping remains **Proposed** (**OQ-HTTP-Health**)
- [ ] T027 [US2] [L5] Gap-fill only in `services/orchestrator/app/services/l5_search.py` and/or `api/context.py` for operability: prefer partial/degraded results when any modality remains usable — FR-009; cite EP-002 (no BM25/vector/MMR rebuild)
- [ ] T028 [US2] [API] Ensure OpenAPI/`health` descriptions do not Confirmed-freeze Proposed HTTP codes or invent degraded schema fields — FR-008, FR-010
- [ ] T029 [US2] Explicitly **skip** SC-007 Pass claim; leave **OQ-Uptime-Harness** open (tracking note only in validation later) — NFR-005, A-EP005-6

**Checkpoint**: US-014 independently verifiable — SC-004, SC-005, SC-006, SC-008; SC-007 not Pass-claimed

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Regression, security boundary, docs cite-only, deployment readiness for POC — no scope expansion.

- [ ] T030 [P] Regression: re-run EP-001 exclusion-related tests (`test_ignore_policy`, `test_packer_exclusions`, `test_index_exclusions_qdrant`, `test_index_no_exfil` cite) — ensure EP-005 gap-fills do not break index privacy foundation
- [ ] T031 [P] Regression: re-run EP-002 healthy hybrid path (`test_context_hybrid_search.py` / related) when deps healthy — degrade path must not break happy path
- [ ] T032 [Security] Privacy/security verification checklist: defaults enforced; no Confirmed override; clients no bypass; no secrets in fixtures committed as real secrets — NFR-001..NFR-003
- [ ] T033 [P] Scope audit: confirm no US-016, RBAC invent, JetBrains, L1/L4, L2/L6, or EP-004 rebuild landed — FR-011
- [ ] T034 [P] Documentation cite-only: if OpenAPI descriptions updated, keep Proposed labels for OQ-HTTP-Health / OQ-Degraded-Shape; do **not** create adjunct Spec Kit files
- [ ] T035 Deployment readiness (local POC): Compose/Qdrant as today; Falkor may be absent (A-07); auth on `GET /` remains open (**OQ-Health-Auth**, A-05) — non-blocking
- [ ] T036 Smoke: `GET /` fields + one ignore fixture index + one degraded `POST /context` path — map evidence to SC-001..SC-006, SC-008 only

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Immediate
- **Phase 2 (Foundational)**: After Setup — **BLOCKS** US-013 and US-014
- **Phase 3 (US-013)**: After Foundational — MVP privacy defaults
- **Phase 4 (US-014)**: After Foundational — may run **in parallel** with Phase 3 if staffed (different primary files: policy/index vs health/search)
- **Phase 5 (Polish)**: After both user stories complete

### User Story Dependencies

| Story | Depends on | Notes |
|-------|------------|-------|
| US-013 (US1) | Phase 2 | Independently testable; cites EP-001 pack/index |
| US-014 (US2) | Phase 2 | Independently testable; cites EP-002 hybrid; no dependency on shipping US-013 code changes if policy already present |

### Within Each Story

1. Tests first (extend existing; expect fail on gaps)
2. Gap-fill implementation only where tests fail
3. Boundary review for clients (US-013)
4. Checkpoint before polish

### Parallel Opportunities

- T001–T003; T005–T007 after T004 fixture direction known
- T008–T010, T012–T014 in parallel within US-013 tests
- T021, T022, T024, T025 in parallel within US-014 tests
- Phase 3 and Phase 4 in parallel after Phase 2
- T030–T034 polish items marked [P]

---

## Implementation Strategy

### MVP First (US-013)

1. Phase 1 + 2  
2. Phase 3 (US-013) — privacy defaults acceptance  
3. **STOP and VALIDATE** SC-001..SC-003  

### Incremental Delivery

1. Add Phase 4 (US-014) — health + degrade operability  
2. Validate SC-004..SC-006, SC-008  
3. Phase 5 polish + regression  

### Parallel Team Strategy

- Dev A: US-013 policy/index/client boundary  
- Dev B: US-014 health/degraded search  
- Shared: fixture (T004) owned once in Phase 2  

---

## Definition of Done

- [ ] FR-001..FR-011 covered (FR-011 = OOS confirmed by audit, not implemented)
- [ ] SC-001..SC-006, SC-008 have verification tasks/evidence path; **SC-007** explicitly **not** Pass-claimed (**OQ-Uptime-Harness**)
- [ ] No Confirmed freeze of **OQ-OVERRIDE**, **OQ-HTTP-Health**, **OQ-Degraded-Shape**, **OQ-Uptime-Harness**
- [ ] Clients MUST NOT bypass orchestrator ignore policy (tests + review)
- [ ] `GET /` Confirmed fields present; Falkor unused OK (A-07)
- [ ] Degraded search behavioral acceptance without invented Confirmed schema
- [ ] Gap-fill only — no L5/L3/CLI/EP-004 rebuild
- [ ] Constitution I–V respected; lean Spec Kit only (`tasks.md` this file)

---

## Evidence Reviewed

| Artifact | Role |
|----------|------|
| `specs/ep-005-privacy-health-consent/spec.md` | FR/SC/US-013/US-014 |
| `specs/ep-005-privacy-health-consent/plan.md` | Gap analysis + phases |
| `.cursor/agent-handoffs/ep-005-brief.md` | Scope + hard constraints |
| Latest handoffs in `.cursor/agent-handoffs/handoff.md` | plan-generator → task-generator |
| `.specify/memory/constitution.md` | III privacy; V boundaries; IV measurable claims |
| `.specify/templates/tasks-template.md` | Task structure |
| Code: `ignore_policy.py`, `fs_walker.py`, `health.py`, `index.py`, `l5_index.py`, `l5_pack.py`, `l5_search.py`, `context.py` | Gap-fill targets |
| Clients: `clients/vscode/src/api/indexClient.ts`, `no_client_policy_bypass.test.ts`; `clients/cli/` | Thin boundary |
| Tests listed in plan Project Structure | Extend, don’t reinvent |

---

## Open Questions / Discovery Tasks

| OQ ID | Representation in tasks | Blocking for |
|-------|-------------------------|--------------|
| **OQ-OVERRIDE** | T007, T012, T015, T020 — defaults enforced; **no** Confirmed override implementation | Confirmed override product |
| **OQ-HTTP-Health** | T005, T024, T026, T028 — Proposed HTTP labels only; no status-code freeze | Confirmed `GET /` status freeze |
| **OQ-Degraded-Shape** | T005, T023, T025, T027 — behavioral degrade only; no Confirmed schema invent | Confirmed degrade schema/UX |
| **OQ-Uptime-Harness** | T006, T029 — tracking only; **blocks SC-007 Pass** | SC-007 Pass claims |
| OQ-Health-Auth | T035 — non-blocking POC (A-05) | Auth on `GET /` |
| OQ-01 / US-016 | T003, T033 — explicit OOS; no invent | Not this epic |

**Discovery**: T001–T002 inventory only — paths Confirmed present; no invented modules. If SC-001 fails on gitignore negation edges, fix narrowly in T015/T016 (plan Risks) — do not invent a full git engine.

---

## Task Traceability Matrix

| Task / Phase | Source Requirement | Plan Reference | Evidence |
|--------------|-------------------|----------------|----------|
| Phase 1 T001–T003 | FR-011; plan Gap Analysis | Phases §1 Foundation | plan.md Gap Analysis; brief OOS |
| Phase 2 T004–T007 | FR-001..FR-003; SC-001; OQs | Testing Strategy; Planning Assumptions | Fixture + OQ labels |
| T008–T011, T015–T017 | FR-001, FR-002, FR-005; SC-001 | US-013 phase; Components | ignore_policy / pack / index tests |
| T012, T007, T020 | FR-003; SC-002; OQ-OVERRIDE | Technical Approach Proposed | No override UX |
| T013–T014, T018–T019 | FR-004; SC-003; NFR-002 | Client / boundary | vscode/cli tests |
| T021, T026, T028 | FR-006, FR-008; SC-004, SC-008 | US-014; API Design | health.py; api-contract §2.1 |
| T022 | FR-007; SC-005; A-07; NFR-007 | Gap Analysis Falkor | health falkor unused |
| T023–T025, T027 | FR-009, FR-010; SC-006 | Degraded search gap | l5_search / context / test_context_degraded |
| T006, T029 | NFR-005; SC-007; OQ-Uptime-Harness | Measurable claims caveat | No Pass without harness |
| T030–T036 | Polish; FR-011; regression | Phase 4 Polish | EP-001/002 cite |

---

## Notes

- Gap-fill and acceptance-harden only — cite EP-001/002/004; do not rebuild L5 packing/search or client surfaces
- **Proposed** vs **Confirmed** labels must survive into tests and OpenAPI text
- Ready for **test-validation-agent** → `validation-report.md` after this triad file exists
