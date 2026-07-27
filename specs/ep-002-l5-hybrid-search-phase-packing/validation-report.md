# Validation Report

## Executive Summary

| Field | Value |
|-------|-------|
| **Feature Name** | EP-002 — L5 Hybrid Search & Phase-Aware Packing (`ep-002-l5-hybrid-search-phase-packing`) |
| **Review Date** | 2026-07-27 |
| **Reviewer** | ContextOS Test Validation Agent |
| **Overall Status** | Conditionally approved |
| **Overall Readiness Score** | **8.6 / 10** |
| **Implementation Readiness Decision** | **CONDITIONAL APPROVAL** |
| **Ready for Implementation** | **Yes** (with documented conditions on OQ-PACK / OQ-11 / OQ-16 / harness & fixture gates) |

EP-002 Spec Kit triad (`spec.md` → `plan.md` → `tasks.md`) is complete, evidence-traced to backlog US-003/US-004/US-015, api-contract `POST /context`, ADR-014/ADR-006, and EP-001 Proposed pack handoff. Scope stays L5 hybrid search + phase packing + citation attributes. Measurable search claims have planned verification; **no tests have been executed**. OQ-PACK, OQ-11, and OQ-16 remain **OPEN** (not Confirmed-frozen). SC-003 recall@10 verification is **blocked for pass claims** until OQ-recall-harness; SC-002 p95 may be **blocked/skipped** without a 500k LOC fixture.

**Verification Gate status vocabulary for this report:** requirements and tests are **Planned** only. EP-001 orchestrator modules under `services/orchestrator/` are **Implemented** (upstream). EP-002 modules (`api/context.py`, `l5_search.py`, etc.) are **Planned / not present**. Nothing for EP-002 is **Executed**, **Passed**, **Failed**, **Skipped**, or **Blocked** by runtime test evidence.

---

## Evidence Reviewed

| Artifact | Path | Role |
|----------|------|------|
| Feature specification | `specs/ep-002-l5-hybrid-search-phase-packing/spec.md` | Primary — Spec Gate (US-003/004/015; FR-001–FR-020) |
| Implementation plan | `specs/ep-002-l5-hybrid-search-phase-packing/plan.md` | Primary — Planning Gate |
| Task list | `specs/ep-002-l5-hybrid-search-phase-packing/tasks.md` | Primary — Task Gate (T001–T070) |
| Constitution | `.specify/memory/constitution.md` v1.0.0 | Governance I–V; Spec/Planning/Task/Verification Gates |
| Spec template | `.specify/templates/spec-template.md` | Required-section baseline |
| Plan template | `.specify/templates/plan-template.md` | Required-section baseline |
| Tasks template | `.specify/templates/tasks-template.md` | Required-section baseline |
| Backlog | `docs/backlog/user-stories.md` | EP-002; US-003, US-004, US-015; OQ-11, OQ-16 |
| API contract | `docs/architecture/api-contract.md` §2.3 `POST /context` | Confirmed request/response; citations/status notes |
| Architecture (supporting) | `docs/architecture/` (ADRs esp. ADR-006, ADR-014; tech-stack; database-schema; implementation-guidelines; overview — as cited by triad) | Contract/scope compliance |
| EP-001 open questions | `specs/ep-001-l5-repository-packing-indexing/open-questions.md` | OQ-PACK Proposed handoff only |
| EP-001 validation precedent | `specs/ep-001-l5-repository-packing-indexing/validation-report.md` | Report format / gate pattern |
| Live source tree | `services/orchestrator/app/{services,api,adapters,security,telemetry}/` | EP-001 Confirmed present; EP-002 modules absent (expected) |
| Pack handoff | `services/orchestrator/app/services/l5_pack.py` `PackResult` | Proposed fields match T002 inventory |
| Tests layout | `services/orchestrator/tests/{unit,integration,contract}/` | EP-001 layout present; EP-002 tests Planned only |
| Deploy | `deploy/docker-compose.yml` | Present (reuse planned) |
| Branch | `feature/ep-002-l5-hybrid-search-phase-packing` | Confirmed via `git branch --show-current` |
| Agent handoffs | `.cursor/agent-handoffs/handoff.md` | Spec/plan/task handoff history |
| Spec folder listing | `specs/ep-002-l5-hybrid-search-phase-packing/` | `spec.md`, `plan.md`, `tasks.md` only prior to this report |
| Test / CI execution | — | **None reviewed** |

---

## Missing Evidence

1. **No test execution evidence reviewed; validation is limited to test planning readiness.**
2. No EP-002 application modules yet (`api/context.py`, `l5_search.py`, `l5_phase_pack.py`, `l5_citations.py`, `bm25_store.py`, `telemetry/context.py`) — **Planned**, not Implemented.
3. No CI/build/lint artifacts for EP-002.
4. Optional Spec Kit adjuncts not present: `research.md`, `data-model.md`, `quickstart.md`, `contracts/`, feature-local `open-questions.md` (T005 / T066 plan creation — non-blocking).
5. **OQ-PACK** — Exact pack schema field inventory Confirmed freeze — **Unresolved** (EP-001 open-questions; Proposed `PackResult` only).
6. **OQ-11** — Citation JSON shape inside `final_context` — **Missing Evidence** (api-contract §2.3 Citations note).
7. **OQ-16** — Phase parameter wire shape on/with `POST /context` — **Unresolved** (Confirmed request lacks phase field).
8. **OQ-top_k** — `top_k` min/max/default beyond positive integer — **Missing Evidence**.
9. **OQ-MVP-metrics** — MVP `tokens_*` / `saving_percent` semantics — **NEEDS CLARIFICATION** (api-contract §2.3).
10. **OQ-recall-harness** — Evaluation dataset/harness for recall@10 >0.92 — **Missing Evidence** (blocks SC-003 pass claims).
11. **OQ-BM25-store** — BM25 storage placement — **Missing Evidence** (ADR-014); Proposed Option A only.
12. **OQ-HTTP-/context** — Confirmed HTTP status codes for `POST /context` — Proposed labels only.
13. **OQ-01** — RBAC/authn schema — **Missing Evidence**.
14. **500k LOC indexed fixture** for SC-002 / NFR-001 — availability **Not evidenced** in repo at validation time (T020 discovery).
15. Exact MMR λ / fusion weights; code2prompt package pin; OTel exporter vendor — **Not evidenced** (correctly Proposed / open).
16. Spec **Status** remains `Draft` (hygiene gap vs Spec Gate claim).

---

## Specification Findings

### Completeness vs Spec Kit / Constitution Specification Gate

| Check | Status | Evidence |
|-------|--------|----------|
| User scenarios prioritized & independently testable | **Met** | US-003, US-004, US-015 all P1 with Independent Test (`spec.md`) |
| FRs atomic & testable | **Met** | FR-001..FR-020 |
| NFRs measurable | **Met** | NFR-001..007; BO-04/IDE SLAs correctly not over-claimed |
| Acceptance Given/When/Then | **Met** | All three user stories |
| Edge cases documented | **Met** | Edge Cases + OQs (404/400 Proposed, top_k, phase, OQ-PACK, degraded, metrics) |
| Assumptions explicit | **Met** | A-01, A-04, A-05, A-06, A-EP002-1/2/3 |
| Success criteria measurable or NEEDS CLARIFICATION | **Met** | SC-001..008; SC-003 harness gap marked; SC-008 metrics open |
| Requirement traceability | **Met** | Traceability + Scenario→FR map |
| Layer/surface impact | **Met** | L5 primary; L1/L2/L3/L4/L6 N/A or deferred |
| Security/privacy | **Met** | Inherit EP-001 exclusions; provenance FR-015; OQ-01 not invented |
| Template placeholders remaining | **None found** | No `[FEATURE NAME]` / ACTION REQUIRED leftovers; remaining NEEDS CLARIFICATION are intentional OQs |
| Blocking OQs visible | **Met** | Open Questions table; label rule forbids Confirmed freeze of OQ-11/16/PACK |

### Gaps / issues (non-blocking unless noted)

1. **Status field** still `Draft` while Ready for Plan Generator claimed Yes — process hygiene gap (same pattern as EP-001).
2. Backlog US-003 Open Questions lists OQ-11 (citations) which is primarily US-015 — minor backlog noise; triad correctly scopes OQ-11 under US-015.
3. FR-008 / SC-003 cannot be verified as Pass until harness exists — correctly documented; **blocks verification pass claims**, not story implementation intent.
4. A-EP002-3 correctly marks OQ-PACK as blocking Confirmed pack contract but non-blocking for behavioral delivery.

### Scope creep check (mandatory)

| Forbidden deliverable | Present as EP-002 acceptance? | Evidence |
|-----------------------|-------------------------------|----------|
| Serena / L3 | **No** | Out Of Scope; L3 N/A |
| L1 blast / `GET /blast` / graph viz | **No** | `blast_radius` empty/null Proposed MVP |
| L4 Headroom / FR-11 budgets / compression dashboard | **No** | FR-014; ADR-006; SC-007 |
| L2 / L6 | **No** | Explicit N/A; `memory` empty/null Proposed |
| Full CLI epic / extension DX | **No** | FR-019 consumer note only; Out Of Scope |
| Confirmed freeze of OQ-PACK / OQ-11 / OQ-16 | **No** | Explicitly forbidden in Open Questions label rule |
| Re-specification of EP-001 indexing | **No** | Consume-only; Out Of Scope |

**Scope verdict:** Pass — L5 hybrid search + phase packing + citations only.

**Specification Gate verdict:** Met — with open questions carried (not invented).

---

## Planning Findings

### Completeness vs Planning Gate

| Check | Status | Evidence |
|-------|--------|----------|
| Every FR/NFR addressed | **Met** | Requirement Coverage Matrix FR-001..020 |
| Architecture defined | **Met** | Technical Approach; pipeline; Confirmed vs Proposed |
| Components identified | **Met** | Components table (`l5_search`, phase pack, citations, BM25, context router) |
| Data model changes | **Met** | Logical entities; OQ labels preserved |
| API changes | **Met** | Confirmed `POST /context`; Proposed extensions labeled |
| Security considerations | **Met** | Security Considerations + privacy inheritance |
| Performance considerations | **Met** | NFR-001; BM25 Option A risk; candidate limits |
| Testing strategy | **Met** | Unit/Integration/E2E/Acceptance mapped to SC; harness gaps explicit |
| Risks documented | **Met** | Risks table |
| Confirmed vs Proposed vs NEEDS CLARIFICATION | **Met** | Technical Context; Open Questions; BM25 A/B/C |
| Six-layer impact | **Met** | L5 primary; deferred layers explicit |
| Boundary discipline | **Met** | FastAPI owns search/packing; CLI/extension consumer-only |
| Architecture deviations | **None unjustified** | Constitution Check Pass |
| Live tree grounding | **Met** | Plan inspected EP-001 modules; validation re-confirmed present |

### Gaps / issues

1. BM25 Option A may miss p95 @ 500k LOC — risk mitigated by measure-then-escalate; do not weaken NFR-001 silently.
2. Phase selection via Proposed mechanism (default Dev / optional Proposed field) — correct until OQ-16; implementers must not claim Appendix D Confirmed.
3. Optional `research.md` / `data-model.md` / `contracts/` not generated — acceptable per plan Documentation tree.
4. Score fusion weights / MMR λ **Not evidenced** — Proposed tunable knobs; acceptable with quality tests when harness exists.

**Planning Gate verdict:** Met — with OQs carried (not invented).

---

## Task Findings

### Completeness vs Task Gate

| Check | Status | Evidence |
|-------|--------|----------|
| Every requirement → impl + verification | **Met** | FR→Task Coverage table FR-001..020 |
| Grouped by independently deliverable stories | **Met** | Phase 3 US-003 → Phase 4 US-004 → Phase 5 US-015 |
| Unique IDs | **Met** | T001–T070 |
| Exact paths when known | **Met** | `services/orchestrator/app/...` Confirmed EP-001 + Proposed EP-002 modules |
| Discovery for unknowns | **Met** | T002, T005–T006, T016–T020, T021–T022, T039, T050, T061, T070 |
| Search intelligence tests planned | **Met** | Hybrid/MMR, phase composition, citations, contract, privacy, perf, recall placeholder |
| Security / docs / telemetry / deployment | **Met** | Phases 2, 3, 6 |
| Definition of Done | **Met** | Includes OOS gate T069; no invented Pass/Fail |
| OQs not Confirmed-frozen | **Met** | Open Questions / Discovery Tasks table |
| Out-of-scope not scheduled as deliverables | **Met** | T068–T069; Path Conventions Out of scope |

### Gaps / issues

1. **SC-003** tasks T019/T030/T061 correctly **blocked for pass claims** — must remain so until harness/dataset supplied.
2. **SC-002** tasks T020/T029/T060 correctly fixture-gated — mark skipped/blocked if 500k corpus unavailable; document gap per constitution IV.
3. T002 `PackResult` field inventory matches live `l5_pack.py` (`repo_name`, `xml_content`, `token_count`, `files_packed`, `files_excluded`, `artifact_path`) — **Proposed only**, consistent with OQ-PACK.
4. No tasks claim completion checkmarks filled — consistent with no EP-002 implementation (**Planned** only).
5. Feature-local open-questions checklist (T005) not yet created — discovery task, non-blocking for start of Setup.

**Task Gate verdict:** Met — ready for sequenced implementation with clarification and harness/fixture gates.

---

## Constitution Compliance

| Rule ID | Principle | Status | Notes |
|---------|-----------|--------|-------|
| I | Evidence-First | **Compliant** | Traceability to BRD/backlog/architecture/EP-001; OQs preserved; no invented Confirmed contracts |
| II | Six-Layer Integrity | **Compliant** | L5 primary; L1/L3/L4/L2/L6 explicit N/A or deferred; no client-side orchestration |
| III | Privacy / Local-First | **Compliant** | FR-018 inherit exclusions; citations provenance; no index exfil assumption; RBAC schema not invented (OQ-01) |
| IV | Measurable Intelligence Claims | **Compliant** | p95 + recall@10 have planned tests; harness/fixture gaps labeled; no invented Pass |
| V | Surface Boundary Discipline | **Compliant** | FastAPI owns `POST /context`; CLI/extension consumer notes only (FR-019) |
| Approved Tech Direction | Stack | **Compliant** | FastAPI 3.11, Qdrant, MiniLM, hybrid BM25+vector+MMR (ADR-014), OTel-compatible; Pinecone not default |
| Roadmap Governance | MVP L5 | **Compliant** | Search + basic phase packing; L4 not pulled forward as gate (ADR-006) |
| Specification Gate | — | **Met** (with OQs) | |
| Planning Gate | — | **Met** (with OQs) | |
| Task Gate | — | **Met** (with OQs) | |
| Verification Gate | Planned vs executed | **Compliant for this report** | Distinguishes Planned; **no Pass/Fail invented** |
| Implementation Gate | — | **N/A for EP-002 code** | EP-001 upstream exists; EP-002 code not reviewed as delivery |

**Threat / risk notes (constitution III):** Query/path traversal into excluded content; packing bypass of index policy; clients reimplementing search; prompt-injection via query returning sensitive pack content to caller; BM25 Option A latency risk at 500k LOC — documented in plan Risks / Security with mitigations. Path-RBAC enforcement detail remains open (OQ-01) — documented gap, not invented.

**Constitution Applied:** Yes.

---

## Traceability Matrix

Legend — **Evidence**: Planned = artifact coverage only; Implemented = EP-001 upstream only where noted; Verified = not claimed for EP-002.

| Requirement | Planned Component | Task Coverage | Evidence | Status |
|-------------|-------------------|---------------|----------|--------|
| FR-001 | `l5_search` + BM25 + Qdrant vector | T031–T035 / T026–T027 | ADR-014; plan Phase 1 | Covered (Planned) |
| FR-002 | MMR in `l5_search` | T034 / T023, T026 | ADR-014 | Covered (Planned) |
| FR-003 | `schemas_context` + `POST /context` | T008–T010, T035 / T015, T025 | api-contract §2.3 | Covered (Planned) |
| FR-004 | Confirmed response fields | T008, T035, T056 / T015, T025, T053 | api-contract §2.3 | Covered (Planned) |
| FR-005 | Meaningful search fields; blast/memory empty | T035 / T025–T026 | api-contract phase notes | Covered (Planned) |
| FR-006 | Ranked files + scores; top_k positive int | T016, T034–T035 / T024–T026 | FR-02; OQ-top_k open | Covered (Planned); bounds open |
| FR-007 | Search p95 <800ms @ 500k | T029, T037, T060 / T020, T029, T060 | BRD §10; fixture gap | Covered (Planned); verification fixture-gated |
| FR-008 | recall@10 >0.92 where harness applies | — / T019, T030, T061 | BRD §12; OQ-recall-harness | Covered as **blocked verification** (Planned) |
| FR-009 | FastAPI owns orchestration | T009–T010, T035 / T026, T064 | constitution V | Covered (Planned) |
| FR-010 | Consume EP-001 packs/Qdrant | T002, T013, T031, T035 / T022, T026 | OQ-PACK Proposed; live `l5_pack.py` | Covered behavioral (Planned); schema open |
| FR-011 | Phase templates × 5 | T045–T046 / T041–T042 | BRD FR-03 | Covered (Planned) |
| FR-012 | Composition differs by phase | T046–T047 / T041–T042 | US-004 | Covered (Planned) |
| FR-013 | No Confirmed phase field invent | T039, T047 / T039 | OQ-16 | Covered (Planned); wire freeze blocked |
| FR-014 | L4 product out of scope | T048, T069 / T043 | ADR-006 | Covered (Planned) |
| FR-015 | Citations file:line + confidence | T054–T055 / T051–T052 | BRD §14 | Covered (Planned) |
| FR-016 | No invented Confirmed citation JSON | T050, T054, T056 / T051 | OQ-11 | Covered (Planned); schema freeze blocked |
| FR-017 | MVP metrics packing counts | T018, T048 / T044 | A-06; OQ-MVP-metrics | Covered (Planned) |
| FR-018 | Privacy inheritance / no exfil assumption | T014, T035 / T028, T063 | constitution III; EP-001 | Covered (Planned) |
| FR-019 | CLI/extension consumer note only | T038, T068–T069 / T068 | EP-004 boundary | Covered (Planned); no DX deliverable |
| FR-020 | Status codes Proposed not Confirmed | T017, T036 / T024, T059 | OQ-HTTP-/context | Covered (Planned) |
| NFR-001 | Same as FR-007 | T020, T029, T060 | BRD §10 | Covered (Planned); fixture-gated |
| NFR-004/005 | Privacy / exclusions | T028, T063 | constitution III | Covered (Planned) |
| NFR-006 | Authn open / loopback | T014, T070 | A-05 | Covered (Planned) |
| NFR-007 | Degraded search | T036, T058 | BRD §10; EP-005 UX OOS | Covered (Planned) |
| SC-001 | Hybrid ranked files | T026–T027, T034–T035 | US-003 | Covered (Planned) |
| SC-002 | p95 | T020, T029, T060 | Fixture gap | Covered (Planned); Not Verified |
| SC-003 | recall@10 | T019, T030, T061 | Harness gap | **Blocked for pass claims** |
| SC-004 | Phase composition | T041–T042, T045–T047 | OQ-16 Proposed wire | Covered (Planned) |
| SC-005 | Citation attributes | T051–T052, T054–T055 | OQ-11 open | Covered (Planned) |
| SC-006 | Confirmed response fields | T015, T025, T053 | api-contract | Covered (Planned) |
| SC-007 | Search without full L4 | T043, T048 | ADR-006 | Covered (Planned) |
| SC-008 | No invent saving_percent thresholds | T018, T044, T048 | OQ-MVP-metrics | Covered (Planned) |

### Orphan / missing coverage check

| Check | Result |
|-------|--------|
| Orphan requirements (no plan/tasks) | **None** |
| Orphan tasks (no requirement/OQ/setup) | **None** — Setup/Polish map to foundation, NFRs, docs, deploy, OQs |
| Missing coverage | **None** for behavioral FRs; verification of SC-002/SC-003 explicitly gated |

---

## Risk Assessment

| Risk | Severity | Justification |
|------|----------|---------------|
| Requirement ambiguity on Confirmed freezes (OQ-11/16/PACK/top_k/metrics) | **MEDIUM** | Story intent clear; Confirmed contract freezes blocked — mitigated by Proposed-only implementations |
| Missing edge cases | **LOW** | Edge Cases section covers unknown repo, validation, degraded, phase absent, pack schema |
| Technical complexity (hybrid + MMR + phase + citations) | **MEDIUM** | ADR-014 Confirmed behavior; fusion/MMR weights untuned; phased delivery mitigates |
| BM25 Option A misses p95 @ 500k LOC | **HIGH** (perf) | Documented; escalate B/C only with evidence; do not weaken NFR-001 |
| Security (policy bypass / excluded path re-read) | **MEDIUM** | Tests T028/T063 planned; OQ-01 RBAC still open |
| Performance / fixture availability | **HIGH** (verification) | SC-002 may remain Not Verified without 500k corpus |
| Dependency on EP-001 index/pack readiness | **MEDIUM** | A-EP002-1; live EP-001 modules Confirmed present; runtime acceptance still needs indexed fixture |
| recall harness missing | **MEDIUM** (verification) | Blocks SC-003 pass claims only — functional hybrid still shippable |
| Operational (Compose/Qdrant) | **LOW** | ADR-013; `deploy/docker-compose.yml` present |
| Scope creep into Serena/L1/L4/CLI/extension | **LOW** | Explicit OOS + T069 |

---

## Readiness Score

| Area | Score | Justification |
|------|-------|---------------|
| Specification Quality | **9 / 10** | Complete Spec Gate; atomic FRs; OQs explicit; Status still Draft (−0.5); residual SC-003 harness gap (−0.5) |
| Planning Quality | **9 / 10** | Strong architecture, API, security, testing, risks; BM25/phase Proposed paths clear; minor fusion-weight open |
| Task Coverage | **9 / 10** | T001–T070 map all FRs/SCs/NFRs; discovery + blocked harness tasks correct; optional open-questions file not yet created |
| Governance Compliance | **9.5 / 10** | Constitution I–V honored; no Confirmed freeze of OQ-PACK/11/16; boundaries clean |
| Test Planning Readiness | **8 / 10** | Excellent planned coverage; SC-002 fixture + SC-003 harness gaps reduce verification readiness (planning only) |
| **Overall Readiness** | **8.6 / 10** | Triad implementation-ready under conditions; verification of latency/recall incomplete until fixtures/harness |

---

## Approval Decision

### **CONDITIONAL APPROVAL**

**Not APPROVED (unconditional)** because OQ-PACK, OQ-11, and OQ-16 remain open and block Confirmed pack/citation/phase wire freezes; SC-003 pass claims are blocked until OQ-recall-harness; SC-002 pass claims may be blocked without a 500k LOC fixture.

**Not REJECTED** because:

- Spec / plan / tasks triad is complete, consistent, and L5-scoped.
- Every FR-001..FR-020 has planned implementation and verification (open items via discovery / Proposed / blocked-harness).
- Measurable search claims have planned acceptance/verification tasks with explicit no-invented-Pass rules.
- Scope does not creep into Serena, L1 blast, L4 product, L2/L6, CLI epic, or extension DX.
- Open questions are explicit with Proposed paths — not undocumented assumptions treated as Confirmed.
- EP-001 upstream pack/Qdrant foundation is Confirmed present under `services/orchestrator/`.
- No fabricated test Pass/Fail; Verification Gate honored.

### Conditions for implementation

1. May begin Phase 1–2 (setup/foundation) and US-003 hybrid search immediately on branch `feature/ep-002-l5-hybrid-search-phase-packing`.
2. May proceed US-004 / US-015 using **Proposed** phase-selection and citation interim representations — must **not** Confirmed-freeze OQ-16 / OQ-11 / OQ-PACK in OpenAPI or Appendix D.
3. Must **not** invent Confirmed `top_k` bounds, HTTP status freeze, MVP `saving_percent` thresholds, or BM25 store product name.
4. Must **not** expand into Serena/L3, L1 blast, L4 Headroom product, L2/L6, full CLI, or extension DX.
5. SC-002 remains **Planned** until measured with evidence (or gap documented if fixture unavailable); SC-003 must stay **blocked for pass claims** until harness/dataset exists.
6. Prefer BM25 Proposed Option A first; escalate B/C only with NFR evidence (avoid unapproved EP-001 write-path creep).
7. Update `spec.md` Status from `Draft` after PM accepts this report (hygiene; non-blocking).

### Ready for Implementation

**Yes** — under the conditions above.

**Next agent:** `lead-developer-agent` (implementation orchestration after Spec Kit validation).

---

## Recommended Improvements

1. Set `spec.md` **Status** from `Draft` to `Approved (Conditional)` or equivalent after PM accepts this report.
2. Create feature-local open-questions checklist (T005) early so OQ-PACK / OQ-11 / OQ-16 remain visible during implementation.
3. Acquire or document gap for 500k LOC indexed fixture before claiming SC-002; keep skip/block vocabulary honest.
4. Define recall@10 harness/dataset (OQ-recall-harness) before any SC-003 Pass claim — placeholder T030 must not be marked Passed.
5. Keep OpenAPI descriptions labeling all Proposed extensions (`phase`, status codes, `relevant_files` item keys, citation interim shape).
6. Produce pytest/CI execution evidence before any future PR-readiness claim of Passed tests.
7. When implementation starts, run `graphify update .` after substantial code lands (workspace rule) — N/A for this docs-only validation.

---

## Assumption Audit

### Valid Assumptions

| ID | Assumption | Why valid |
|----|------------|-----------|
| A-01 | Git SoT; monorepo ≤1M LOC for MVP | BRD §13 evidenced |
| A-04 | Qdrant via Docker Compose | ADR-013; `deploy/docker-compose.yml` present |
| A-06 | MVP metrics may be packing token counts | api-contract §2.3; ADR-006 |
| A-EP002-1 | EP-001 pack/index upstream for search | EP-001 modules Confirmed present; US-003 deps |
| A-EP002-2 | CLI/extension ask call same `POST /context` | constitution V; consumer note only |
| A-EP002-3 | Proceed on Proposed pack handoff without Confirmed freeze | OQ-PACK explicit; `PackResult` Proposed |

### Risky Assumptions

| ID | Assumption | Risk |
|----|------------|------|
| A-05 | Local loopback trust for API auth | Acceptable POC; insecure if exposed beyond localhost |
| A-EP002-4 | BM25 Option A acceptable initially | May fail NFR-001 at 500k — measure early |
| A-EP002-5 | Default phase Dev / test injection until OQ-16 | Rework if product Confirms different wire — mitigated by Proposed labels |
| Fusion/MMR defaults | Tunable Proposed weights | Quality may lag until harness exists |
| pytest as runner | Aligned to EP-001 | Reasonable Proposed; not BRD-mandated |

### Blocking Assumptions

| Item | Assessment |
|------|------------|
| Invented Confirmed phase request field | **Avoided** — OQ-16 Proposed only |
| Invented Confirmed citation JSON schema | **Avoided** — OQ-11 attributes-only |
| Invented Confirmed pack schema freeze | **Avoided** — OQ-PACK Proposed `PackResult` only |
| Tests already Passed / recall harness exists | **Not assumed** — Missing Evidence of execution/harness |
| 500k fixture available | **Not assumed** — T020 discovery required |

**No blocking undocumented assumptions** that would force REJECTED. Remaining blockers are **explicit open questions** and **verification harness/fixture gaps**, not hidden assumptions.

---

## Measurable Search Intelligence — Planning Only

| Claim | Planned tests | Executed? | Result |
|-------|---------------|-----------|--------|
| SC-001 hybrid ranked files with scores | T026, T027, T034, T035 | No | **Not Verified** |
| SC-002 p95 <800ms @ 500k LOC | T020, T029, T060 | No | **Not Verified** (fixture may block) |
| SC-003 recall@10 >0.92 | T019, T030, T061 | No | **Blocked for pass claims** (OQ-recall-harness) |
| SC-004 phase composition differs | T041, T042, T045–T047 | No | **Not Verified** |
| SC-005 citations file:line + confidence | T051, T052, T054–T055 | No | **Not Verified** |
| SC-006 Confirmed response fields | T015, T025, T053 | No | **Not Verified** |
| SC-007 Search works without full L4 | T043, T048 | No | **Not Verified** |
| SC-008 MVP metrics no invent thresholds | T018, T044, T048 | No | **Not Verified** (no invented Pass criteria) |
| NFR-004/005 privacy inheritance | T028, T063 | No | **Not Verified** |
| NFR-007 degraded search | T036, T058 | No | **Not Verified** |

---

## Quality Validation (pre-completion)

| Check | Result |
|-------|--------|
| Every requirement has coverage | Yes (Planned) |
| Every plan item has tasks | Yes |
| Every task traces to requirement/OQ/setup | Yes |
| Constitution compliance verified | Yes |
| Traceability Matrix complete | Yes |
| Readiness score justified | Yes |
| Approval decision matches findings | Yes — CONDITIONAL APPROVAL |
| No fabricated Pass/Fail | Yes |
| OQ-PACK / OQ-11 / OQ-16 not Confirmed-frozen | Yes |
| No Serena / L1 / L4 product / L2 / L6 expansion | Yes |

**Validation iterations:** 1 (sufficient; no critical triad contradictions requiring rewrite).

---

## Return Summary (for Product Manager / Lead Developer)

| Item | Value |
|------|-------|
| Validation report path | `specs/ep-002-l5-hybrid-search-phase-packing/validation-report.md` |
| Validation status | **Conditionally approved** |
| Blocking questions | **OQ-PACK** (Confirmed pack freeze); **OQ-11** (Confirmed citation JSON freeze); **OQ-16** (Confirmed phase wire freeze); **OQ-recall-harness** (SC-003 pass claims); **500k fixture** (may block SC-002 pass claims). Non-blocking for story intent: OQ-top_k, OQ-MVP-metrics, OQ-BM25-store, OQ-HTTP-/context, OQ-01 |
| Ready for implementation | **Yes** (conditional) |
| Constitution Applied | **Yes** |
| Next | **lead-developer-agent** |
| Issues found (summary) | Draft status hygiene; optional adjuncts absent; SC-002/SC-003 verification gated; EP-002 modules not yet implemented (expected); no execution evidence (expected) |
