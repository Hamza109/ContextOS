# Tasks: EP-013 OKF Primary Knowledge Format

**Input**: `specs/ep-013-okf-primary-knowledge/spec.md` and `plan.md`  
**Prerequisites**: EP-001/EP-002 L5 pack+search, EP-005 privacy, EP-006 L1 metadata available as optional enrichment.  
**Status**: Implementation + runtime evidence + review complete (T030).

**Scope guardrails**: Generate OKF bundles and OKF-first `/context` composition only. Do not replace FalkorDB/Qdrant, add Confirmed endpoints/fields, implement Attested Computation runtime, blast/visualization, L4, L6, or client UX.

## Phase 1: Discovery Defaults (Blocking)

- [x] T001 [L5] Confirm OQ-OKF-01 default: Proposed `CONTEXTOS_OKF_CACHE_DIR` beside pack cache; bundle root `{cache}/{repo_name}/`. (FR-001; Plan OQ defaults)
- [x] T002 [L5] Confirm OQ-OKF-02 default: exact + token-normalized match over concept id/title/tags/description; no embedding required for OKF hit. (FR-005)
- [x] T003 [L5] Confirm OQ-OKF-03 default: no Confirmed `/index` response field for OKF concept counts. (FR-006)
- [x] T004 [P] [L2] Document L2-adjacent scope: generated docs/spec concepts only; external connectors remain EP-010 / OQ-03. (Roadmap governance)
- [x] T005 [P] [Security] Confirm metadata-only body rule and IgnorePolicy-before-generation invariant. (FR-003, FR-009)

**Checkpoint**: Defaults recorded; implementation may proceed without inventing Confirmed contracts. (Lead 2026-07-28 — see `ep-013-okf-brief.md`)

## Phase 2: Foundational OKF Boundaries

- [x] T006 [L5] Add Proposed settings `okf_cache_dir`, `okf_enabled`, `okf_link_expand_limit` to `services/orchestrator/app/config.py`. (T001; FR-001)
- [x] T007 [L5] Create Proposed adapter `services/orchestrator/app/adapters/okf_bundle.py` for write/read/list of OKF concepts, `index.md` generation, and malformed-skip counts. (FR-001, FR-003, FR-004)
- [x] T008 [L5] Create Proposed generator service `services/orchestrator/app/services/okf_generate.py` consuming only allowed doc/spec paths + optional L1 metadata summaries. (T005, T007; FR-001–FR-004, FR-009)
- [x] T009 [L5] Create Proposed retrieve service `services/orchestrator/app/services/okf_retrieve.py` implementing T002 matching and bounded link expansion. (T002, T007; FR-005, FR-010)
- [x] T010 [P] [L5] Add fixture bundle sources under **Proposed** `services/orchestrator/tests/fixtures/okf_knowledge_repo/` with architecture/spec samples, exclusion cases generated at test time, and expected concept IDs. (FR-002, FR-009; SC-001)

## Phase 3: US-046 — Generate OKF Bundle

### Tests

- [x] T011 [P] [US-046] [L5] Unit tests for concept frontmatter, Concept ID stability, markdown links, malformed skip in `tests/unit/test_okf_bundle.py` and `tests/unit/test_okf_generate.py`. (T007–T008, T010; FR-001–FR-004)
- [x] T012 [P] [US-046] [Security] Extend exclusion/no-exfil tests so ignored/secret/build/deps/binary content never becomes OKF sources. (T008, T010; FR-009; SC-004)
- [x] T013 [P] [US-046] [API] Assert `/index` Confirmed four-field response unchanged after OKF generation. (T003; FR-006; SC-005)

### Implementation

- [x] T014 [US-046] [L5] Implement generator for FR-002 source classes with provenance fields and metadata-only bodies. (T011; FR-001–FR-004)
- [x] T015 [US-046] [L5] Integrate `okf_generate` into `services/orchestrator/app/services/l5_index.py` after eligibility (and after L1 when present); OKF failure must not invent Confirmed HTTP semantics and must preserve L5/L1 outcomes where possible. (T008, T012–T014; FR-001, FR-010)
- [x] T016 [US-046] [Telemetry] Record OKF generate counts/timings/status only in indexing telemetry. (T015; FR-009)

### Acceptance

- [x] T017 [US-046] [L5] Integration test: index fixture → on-disk OKF concepts with valid `type` + provenance; excluded paths absent. (T015, T012; SC-001, SC-004)

## Phase 4: US-047 — OKF-First Retrieval

### Tests

- [x] T018 [P] [US-047] [L5] Unit tests for match/miss/link-expand and no-fabrication in `tests/unit/test_okf_retrieve.py`. (T009; FR-005, FR-010)
- [x] T019 [P] [US-047] [API] Contract/integration tests: cited OKF block in `final_context`, trace `okf_status`, unchanged Confirmed response fields. (T009; FR-006; SC-002, SC-005)
- [x] T020 [P] [US-047] [MCP] Extend MCP pass-through tests only as needed; no OKF state in MCP. (FR-008)

### Implementation

- [x] T021 [US-047] [API] Compose OKF-first evidence in `services/orchestrator/app/api/context.py` before L1/L5 enrichment paths; preserve L5 on miss/error. (T018–T019; FR-005, FR-006, FR-010)
- [x] T022 [US-047] [Telemetry] Add non-sensitive OKF hit/miss/timing notes to existing `metrics.trace`. (T021; FR-006)

### Acceptance

- [x] T023 [US-047] [L5] Integration: known architecture question returns OKF citations with embeddings stubbed/disabled. (T021; SC-002)

## Phase 5: US-048 — Vector Fallback

- [x] T024 [P] [US-048] [L5] Integration test: semantic code query with no OKF match still uses hybrid BM25/vector path. (FR-007; SC-003)
- [x] T025 [US-048] [L5] Verify Qdrant indexing path remains enabled when `okf_enabled=true`; add regression assertion in index/context suites. (FR-007)
- [x] T026 [P] [US-048] [L5] Opt-in eval harness `tests/eval/test_okf_retrieval.py`: OKF grounding P/R/F1 + fallback recall on fixture; record measurements without pass claims. (Constitution IV)

## Phase 6: Documentation and Spec Kit Validation

- [x] T027 [P] Update architecture notes in `docs/architecture/architecture-overview.md` and `docs/architecture/api-contract.md` labeling OKF as Proposed exchange layer and retrieval precedence. (FR-001–FR-008)
- [x] T028 [P] Optional backlog sync note for EP-013 / US-046–US-048 in `docs/backlog/user-stories.md` or handoff only — do not invent Confirmed BRD claims. (OQ-OKF-04)
- [x] T029 Write Spec Kit `validation-report.md` for planning readiness (this triad). Result: APPROVED 9.0/10; runtime Not Executed. (Constitution I)
- [x] T030 After implementation: execute suites, update validation evidence, then write `review-report.md`. (Post-implementation only) — **2026-07-28**: runtime evidence (testing-agent) + `review-report.md` (review-pr-readiness-agent); **PR ready: Yes with comments**.

## Dependencies and Execution Order

- **Blocking path**: T001–T005 → T006–T010 → T011–T017 → T018–T023 → T024–T026 → T027–T029.
- **Parallel**: T011–T013 after T010; T018–T020 after T009; T024 with T023.
- **US independence**: US-046 complete at T017; US-047 at T023; US-048 at T025/T026.

## Implementation Strategy

1. Lock Proposed defaults without new Confirmed contracts.
2. Ship generator behind existing `/index`.
3. Ship OKF-first composition behind existing `/context` with mandatory L5 fallback tests.
4. Document Proposed architecture; defer review-report until runtime evidence exists.

## Parallel Team Assignment Hints

| Phase | Owner hint |
|---|---|
| T001–T010 | Backend / Spec author |
| T011–T017 | Backend + Testing |
| T018–T026 | Backend + Testing |
| T027–T029 | PM / Spec Kit validation |
| T030 | Lead + review after code |

## Requirement Traceability Matrix

| Tasks | FR / Stories | Plan section | Evidence expected |
|---|---|---|---|
| T001–T005, T006–T010 | FR-001–FR-004, FR-009 | Technical Approach; OQ defaults | Defaults + module boundaries |
| T011–T017 | US-046; FR-001–FR-004, FR-009–FR-010 | Data Model; Testing | Bundle on disk; privacy |
| T018–T023 | US-047; FR-005–FR-006, FR-008, FR-010 | Retrieval order | Cited OKF hit |
| T024–T026 | US-048; FR-007 | Fallback | Hybrid still works |
| T027–T029 | All | Docs + validation | Spec Kit readiness |
