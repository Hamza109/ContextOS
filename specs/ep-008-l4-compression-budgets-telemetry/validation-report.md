# Validation Report: EP-008 L4 Context Compression, Token Budgets & Cost Telemetry

## Executive Summary

| Field | Value |
|-------|-------|
| **Feature Name** | EP-008 L4 Context Compression, Token Budgets & Cost Telemetry (`ep-008-l4-compression-budgets-telemetry`) |
| **Review Date** | 2026-07-29 |
| **Reviewer** | ContextOS Test Validation Agent (Spec Kit planning readiness) |
| **Stories in scope** | US-022, US-023, US-024 **only** |
| **Overall Status** | **CONDITIONAL APPROVAL** |
| **Overall Readiness Score** | **8.7 / 10** |
| **Implementation Readiness Decision** | **Yes** — Ready for lead-developer-agent with documented conditions |
| **Constitution Applied** | Yes (I–V + Roadmap Governance) |
| **Ready for lead-developer-agent** | **Yes** (conditions below) |

**Scope of this report:** Spec Kit triad planning & test-planning readiness only.  
**No test execution evidence reviewed; validation is limited to test planning readiness.**  
L4 modules (`l4_compression.py`, `l4_budgets.py`, `l4_relevance.py`, `headroom_summarizer.py`) are **Planned / Proposed**, not **Implemented**. Do not treat SC-001/SC-002 (60–95% savings, recall@10 >0.92) as passed.

**Primary condition:** **OQ-07** remains **blocking** for canonical Dev numeric AC (BRD §5 Dev=8k vs FR-11 Dev=12k). Artifacts correctly refuse to invent Confirmed Dev=8k or Dev=12k. Implementation may proceed with injectable budgets + Design=32k evidenced fixtures; Dev numeric AC stays gated (T021/T037).

---

## Evidence Reviewed

| Artifact | Role | Status |
|----------|------|--------|
| `.cursor/agent-handoffs/ep-008-brief.md` | Scope, Confirmed packing baseline, OQ-07/08/09 | Reviewed |
| `specs/ep-008-l4-compression-budgets-telemetry/spec.md` | Feature specification | Reviewed |
| `specs/ep-008-l4-compression-budgets-telemetry/plan.md` | Implementation plan | Reviewed |
| `specs/ep-008-l4-compression-budgets-telemetry/tasks.md` (T001–T037) | Task breakdown | Reviewed |
| `.specify/memory/constitution.md` v1.0.0 | Governance gates I–V | Reviewed |
| `.specify/templates/spec-template.md` | Spec Kit shape | Present |
| `.specify/templates/plan-template.md` | Plan Kit shape | Present |
| `.specify/templates/tasks-template.md` | Tasks Kit shape | Present |
| `.specify/templates/validation-*-template.md` | Validation template | **Absent** — format follows constitution + EP-007 pattern |
| `.cursor/rules/lean-spec-kit-artifacts.mdc` | Lean artifact set | Pass — triad + this report only |
| `docs/backlog/user-stories.md` | EP-008, US-022/023/024, OQ-07/08/09, A-03/A-06 | Reviewed |
| `docs/BRD_Context_OS.md` | §5 L4, FR-11..13, §10 compression NFR, §12 KPI, §15 V1 | Reviewed |
| `docs/architecture/architecture-overview.md` | L4 row / pipeline (cited by plan) | Cited |
| `docs/architecture/api-contract.md` §2.3 metrics; §3 dashboard; phase-budget NEEDS CLARIFICATION | Reviewed |
| `docs/architecture/architecture-decisions.md` | ADR-006, ADR-009, ADR-011 | Reviewed |
| Orchestrator baselines | `api/context.py` (`l4_gate: False`), `l5_phase_pack.py` packing estimates, `consent_gate.py`, `telemetry/context.py`, `ignore_policy.py`, `schemas_context.py` | Present |
| Tests baselines | `test_context_metrics_mvp.py`, `test_phase_no_l4_gate.py`, `test_context_contract.py` (`CONFIRMED_METRICS_FIELDS`) | Present |
| Graphify | `graphify query` EP-008 L4 / Headroom / packing metrics / OQ | Executed |

**Lean check:** No `quickstart.md`, `open-questions.md`, `out-of-scope-notes.md`, or `docs/design/ep-008-*` UI suite.

---

## Missing Evidence

| Item | Classification | Impact |
|------|----------------|--------|
| Executed L4 unit/integration/contract/eval tests | Missing Evidence | Expected until implementation |
| Executed SC-001 savings harness (60–95%) | Missing Evidence | Planned T012/T013/T018 — **no pass claim** |
| Executed SC-002 recall@10 >0.92 harness | Missing Evidence | Planned T013 — **no pass claim** |
| CI/build/lint results for EP-008 | Missing Evidence | Not claimed |
| `l4_compression.py` / `l4_budgets.py` / `l4_relevance.py` / `headroom_summarizer.py` | Planned only | Proposed paths in plan/tasks |
| `contextos_token_dashboard.html` | Planned only | Confirmed name; serving OQ-08 |
| Canonical Dev phase budget (8k vs 12k) | **NEEDS CLARIFICATION: OQ-07** | Blocks numeric Dev AC only |
| Dashboard serving mechanism | **NEEDS CLARIFICATION: OQ-08** | Non-blocking; Proposed static default |
| OTel exporter / collector vendor | **NEEDS CLARIFICATION: OQ-09** | Non-blocking; compat-only |
| Exact hard-fail vs degradation step table | Missing Evidence / OQ-EP008-a | Blocks precise step AC; Proposed prune OK |
| Telemetry opt-out API shape | Missing Evidence / OQ-EP008-b | Non-bypass obligation only |
| Cost $ rate table ($0.50→$0.05) | Missing Evidence / OQ-EP008-c | Token-delta primary acceptable |
| Headroom library package pin | Missing Evidence | Style Confirmed (ADR-006); pin Proposed |
| Dashboard / API authn-RBAC schema | Missing Evidence | Do not invent |
| `review-report.md` | Not due | After implementation + tests only |
| Dedicated validation template under `.specify/` | Absent | Non-blocking |

`No test execution evidence reviewed; validation is limited to test planning readiness.`

---

## Specification Findings

| Check | Result | Evidence |
|-------|--------|----------|
| Required Spec Kit sections | **Pass** | Scenarios, FRs, entities, ContextOS Impact, NFRs, SC, Assumptions, Dependencies, OOS, OQs, Traceability |
| Stories = US-022/023/024 only | **Pass** | Three prioritized stories; L1/OKF redesign, L2/L6, full UI suite excluded |
| Independently testable scenarios | **Pass** | Independent Test + Given/When/Then per story |
| FRs atomic & testable | **Pass** | FR-001–FR-012 |
| Confirmed vs Proposed labeling | **Pass** | Evidence Classification table; OQ-07/08/09 as NEEDS CLARIFICATION; HTTP codes Proposed |
| Six-layer impact | **Pass** | L4 Affected; L5 integration; L3 dependency; L1/L2/L6 N/A redesign (FR-012) |
| Surfaces | **Pass** | FastAPI owns L4; CLI/VS Code thin; minimal dashboard; GHA N/A |
| Privacy / consent / IgnorePolicy | **Pass** | FR-004, FR-011; Edge Cases; Constitution III |
| Success criteria measurable or labeled | **Pass** | SC-001/002 validation targets not achieved; SC-003 Dev AC blocked on OQ-07 |
| Edge cases | **Pass** | Under-budget, consent deny, tiny packs, IgnorePolicy, packing-when-L4-off, degradation Missing Evidence |
| No template placeholders | **Pass** | Clean |
| Packing metrics baseline vs L4 | **Pass** | Prerequisites + FR-007 + A-06: Confirmed keys exist as packing estimates today; L4-meaningful when compress runs |
| OQ-07/08/09 not invented as Confirmed | **Pass** | Explicit blocking/non-blocking; FR-006 forbids inventing Dev numbers |
| Lean artifact set | **Pass** | Residual OQs inside spec only |

### Gaps (non-blocking)

1. Spec **Status** still `Draft` — recommend flipping to Ready for Plan/Implementation after this gate.
2. Epic-internal Priority P1 (US-023/022) / P2 (US-024) vs backlog product Priority **P2** for all three — sequencing within V1 epic, not a scope conflict (same pattern as EP-007).
3. Spec FR-006 cites `api-contract §5`; phase-budget clarification lives in api-contract open-questions / phase-budgets table (Dev=12k vs §5 Dev=8k) — evidence aligned; section label slightly imprecise.
4. Accessibility not evidenced for minimal HTML — correctly avoided inventing a11y numeric targets.

### Blocking for story intent?

**Partial.** Functional US-022 (hard-fail + degradation with injectable budgets) and full US-023/US-024 can proceed. **Canonical Dev numeric AC** cannot be Confirmed until OQ-07 resolves. OQ-EP008-a blocks only *precise degradation step* AC, not a Proposed prune loop.

---

## Planning Findings

| Check | Result | Evidence |
|-------|--------|----------|
| Every FR addressed | **Pass** | Requirement Coverage Matrix FR-001–FR-012 → Planned |
| Architecture / components | **Pass** | CompressionService + relevance + budgets + summarizer adapter; `/context` integration |
| Data model | **Pass** | No Confirmed DB schema; Proposed config/in-memory entities |
| API changes | **Pass** | Confirmed `POST /context` fields unchanged (ADR-009); L4-meaningful metrics when on; no new Confirmed endpoints |
| Packing vs L4 metrics separation | **Pass** | Dual-mode table (`l4_gate` false/true); packing estimates when L4 off (A-06) |
| Security | **Pass** | Consent gate, IgnorePolicy, provenance, no invented dashboard auth |
| Performance | **Pass** | Local/heuristic default Proposed; eval harnesses opt-in; no invented L4-only p95 |
| Testing strategy | **Pass** | Unit / integration / contract / opt-in eval / regression |
| Risks | **Pass** | OQ-07, symbol drop, exfil, metrics confusion, degradation ambiguity, OQ-08/09, latency |
| L1/OKF out of redesign | **Pass** | FR-012; consume packs only |
| Measurable claims gated | **Pass** | Constitution IV Conditional until harness execution; Dev AC gated OQ-07 |
| OQ labeling | **Pass** | OQ-07/08/09 + OQ-EP008-a/b/c retained; no Confirmed invention |

### Gaps (non-blocking)

1. Exact L4 insertion order vs OKF/L1 enrichment remains **Proposed** (`l4_stage_order` in trace) — acceptable discovery for T001/T017.
2. Proposed OTel attribute names (`compression.ratio`, etc.) are implementation labels for Confirmed FR-13 metric concepts — correctly not frozen as product HTTP contract.
3. No dedicated Compose/deploy task — justified: no new required service (plan Technical Context).

---

## Task Findings

| Check | Result | Evidence |
|-------|--------|----------|
| Every FR has tasks | **Pass** | Task Traceability Matrix T001–T037 → FR-001–012 |
| Components have tasks | **Pass** | Skeletons T004–T006; implement T014–T016, T022, T029–T031; wire T007/T017/T023 |
| Testing tasks | **Pass** | T008–T013, T018–T021, T024–T028; eval scaffold T013 |
| Docs tasks | **Pass** | T034 OpenAPI/api-contract notes |
| Security / governance | **Pass** | T010, T011, T032; regression T033 |
| OQ-07 gated correctly | **Pass** | T021 skip/xfail; T037 unlock; injectable only until resolve |
| OQ-08/09 not Confirmed | **Pass** | T027/T028/T029/T031 labeled Proposed |
| Story grouping + DoD | **Pass** | US-023 → US-022 → US-024; checkpoints; Definition of Done table |
| Actionable paths | **Pass** | Exact Proposed module/test paths; T001 discovery of insertion point |
| Lean Spec Kit | **Pass** | T035 = this validation-report; no adjunct artifacts |
| Independently executable stories | **Pass** | Checkpoints at T018 / T024 / T031 |

### Gaps (non-blocking)

1. T003 names `test_context_metrics_keys.py` while Confirmed-keys lock already exists in `tests/contract/test_context_contract.py` — tasks say “extend existing if present”; implementers should extend the existing contract file rather than duplicating.
2. Deployment/ops tasks minimal — acceptable for in-process CompressionService; OTel sink remains OQ-09.
3. T036 `review-report.md` correctly deferred post-implementation.

### Missing work?

**None blocking** for Conditional Approval. Unlock Dev numeric AC only after OQ-07 (T037).

---

## Constitution Compliance

| Principle / Gate | Status | Evidence |
|------------------|--------|----------|
| **I — Evidence-First** | **Pass** | FR/SC cite BRD FR-11..13, ADR-006/009/011, api-contract §2.3, backlog; Missing Evidence labeled |
| **II — Six-Layer Integrity** | **Pass** | L4 delivery; L5/L3 consume/reuse; L1/OKF out of redesign (FR-012) |
| **III — Privacy/Security** | **Pass with obligations** | Consent before external summarize (FR-004); IgnorePolicy + provenance (FR-011); no index-time LLM |
| **IV — Measurable Intelligence** | **Conditional** | 60–95%, recall@10 >0.92, symbol preservation have planned harnesses; no pass without execution; Dev numeric blocked OQ-07 |
| **V — Surface Boundaries** | **Pass** | FastAPI owns L4 (FR-010); clients thin; dashboard presentation only; telemetry opt-out non-bypass |
| **Roadmap Governance** | **Pass** | V1 L1+L4 slice for L4; no V2 L2/L6 pull |
| **Spec / Plan / Task Gates** | **Pass** | Triad complete; blocking OQs visible |
| **Lean Spec Kit** | **Pass** | Only required artifacts; OQs inside triad |

**Applicable governance rule IDs:** Constitution I–V; ADR-006 (L4 in V1); ADR-009 (HTTP surface); ADR-011 (OTel-compatible); api-contract §2.3 Confirmed metrics keys; backlog OQ-07/08/09.

**Violations:** None identified. No Confirmed Dev budget, dashboard serving, or exporter vendor invented.

---

## Traceability Matrix

| Requirement | Planned Component | Task Coverage | Evidence | Status |
|-------------|-------------------|---------------|----------|--------|
| FR-001 Adaptive summarize 60–95% | CompressionService + relevance + summarizer | T008, T012–T018 | BRD FR-12; §10; US-023 | Covered — Planned |
| FR-002 Preserve symbols/types/TODOs | `headroom_summarizer` + preserve tests | T009, T015 | BRD FR-12; §13 | Covered — Planned |
| FR-003 recall@10 >0.92 + symbol gate | Eval harness + preserve suite | T009, T013 | BRD §10; §13 | Covered — Planned (eval) |
| FR-004 Consent before external LLM | `consent_gate` + summarizer | T010, T015 | US-016; Constitution III | Covered — Planned |
| FR-005 Phase budgets hard-fail + degrade | `l4_budgets` + `/context` wire | T019–T020, T022–T024 | BRD FR-11; US-022 | Covered — Planned |
| FR-006 Dev canonical value gated | Injectable budgets; T021/T037 | T002, T005, T021, T037 | OQ-07; api-contract phase budgets | Covered — Gated |
| FR-007 L4-meaningful Confirmed metrics | Dual-mode metrics; `/context` | T001, T003, T007, T017, T026, T030 | api-contract §2.3; A-06; ADR-006 | Covered — Planned |
| FR-008 OTel ratio / recall@k / cost-saved | `telemetry/compression` or extend context | T025, T027, T029 | FR-13; ADR-011 | Covered — Planned |
| FR-009 Token dashboard artifact | `contextos_token_dashboard.html` | T028, T031 | FR-13; OQ-08 | Covered — Planned |
| FR-010 FastAPI owns L4; no client bypass | `/context` ownership; thin clients | T007, T017, T023, T029 | Constitution V | Covered — Planned |
| FR-011 IgnorePolicy + provenance | Summarize path + audit | T011, T016, T032 | Constitution III | Covered — Planned |
| FR-012 No L1/OKF redesign | Consume packs; regression | T001, T017, T033 | Brief; ADR-001; roadmap | Covered — Planned |
| SC-001 Savings target | Fixtures + integration | T012, T018 | Spec SC-001 | Planned — not verified |
| SC-002 Recall target | Eval scaffold | T013 | Spec SC-002 | Planned — not verified |
| SC-003 Budget functional / Dev gated | Budgets + OQ-07 gate | T019–T024, T037 | Spec SC-003 | Planned — Dev blocked |
| SC-004 Meaningful metrics | Integration semantics | T026, T030 | Spec SC-004 | Planned — not verified |
| SC-005 OTel emission | Attr tests + emit | T027, T029 | Spec SC-005 | Planned — not verified |
| SC-006 Dashboard artifact | Smoke + HTML | T028, T031 | Spec SC-006 | Planned — not verified |

**Orphan Requirements:** None.  
**Orphan Tasks:** None material (T001 discovery, T035 this report, T036 post-impl review are intentional).  
**Missing Coverage:** None for planning readiness.

---

## Risk Assessment

| Risk | Level | Justification |
|------|-------|---------------|
| OQ-07 unresolved (Dev 8k vs 12k) | **HIGH** for numeric Dev AC; **LOW** for implementation start | Artifacts gate correctly; injectable budgets unblock coding |
| Compression drops key symbols | **MEDIUM** | Preserve tests + recall harness planned; claim rule explicit |
| External LLM exfiltration | **MEDIUM** | Consent gate + Proposed local/heuristic default mitigates |
| Packing metrics mistaken for L4 savings | **MEDIUM** | Dual-mode table + `l4_gate` + T026/T030 — residual confusion if docs lag |
| Degradation algorithm ambiguity (OQ-EP008-a) | **MEDIUM** | Precise step AC blocked; Proposed prune loop documented |
| OQ-08/09 delay (serving / exporter) | **LOW** | Ship artifact + OTel-compatible emit labeled Proposed |
| Latency if LLM summarize defaults on | **MEDIUM** | Plan prefers local path; flag default off (P-EP008-2) |
| L4 vs OKF/L1 enrichment order | **LOW** | Proposed; record `l4_stage_order`; T001 discovery |
| Requirement ambiguity elsewhere | **LOW** | Strong Confirmed/Proposed labeling |
| Dependency on US-003/004/005 | **LOW** | Packing/search/symbols present on main baselines |

---

## Readiness Score

| Area | Score | Justification |
|------|-------|---------------|
| Specification Quality | **9.0 / 10** | Complete triad sections; excellent Evidence Classification; OQs retained; Status still Draft (−0.5 soft) |
| Planning Quality | **9.0 / 10** | Clear architecture, dual-mode metrics, security/perf/test/risks; insertion order Proposed only |
| Task Coverage | **9.0 / 10** | T001–T037 map all FRs/SCs; OQ gates correct; minor contract-test path naming |
| Governance Compliance | **9.5 / 10** | Constitution I–V + ADR-006/009/011 honored; no invented Confirmed contracts |
| Test Planning Readiness | **8.5 / 10** | Strong unit/integration/contract/eval plan; measurable claims gated; no execution yet (expected) |
| **Overall Readiness** | **8.7 / 10** | Sound Conditional Approval; OQ-07 is the expected residual blocker for Dev numeric AC |

---

## Approval Decision

### **CONDITIONAL APPROVAL**

**Rationale:** Spec, plan, and tasks are complete, consistent, and traceable. Packing-baseline metrics are clearly separated from L4-meaningful metrics. OQ-07/08/09 are retained as NEEDS CLARIFICATION and are **not** invented as Confirmed contracts. Measurable intelligence claims have planned harnesses without false pass claims. Lean Spec Kit constraints are respected.

**Conditions for implementation handoff:**

1. **OQ-07** remains blocking for **canonical Dev numeric AC** — use injectable budgets; Design=32k OK; skip/xfail Dev=8k/12k product-truth fixtures until resolved (T021/T037).
2. Treat degradation step table as **Proposed** until OQ-EP008-a clarified; do not claim Confirmed step AC.
3. Do not invent Confirmed dashboard serving (OQ-08), OTel vendor (OQ-09), opt-out API, $ rate table, or new Confirmed HTTP fields/endpoints (ADR-009).
4. Default summarize path SHOULD remain local/heuristic; external LLM only via consent (FR-004).
5. Keep `l4_enabled` default off until quality gates green (P-EP008-2) — Proposed but recommended.
6. No L1 blast/graph or OKF redesign (FR-012); regression T033 required.
7. SC-001/SC-002 remain **validation targets** until harness execution evidence exists.
8. After implementation + tests: update validation evidence and produce `review-report.md` (T036) — not now.

**Not APPROVED (unconditional):** OQ-07 blocks Confirmed Dev numeric AC.  
**Not REJECTED:** No missing triad artifacts, no governance violations, no orphan FRs, no invented Confirmed OQ contracts, test planning covers measurable claims.

---

## Recommended Improvements

1. Flip spec **Status** from `Draft` → Ready for Implementation (conditional).
2. In T003, explicitly extend `services/orchestrator/tests/contract/test_context_contract.py` rather than implying a new keys-only file.
3. When OQ-07 resolves, document the chosen Dev budget in api-contract + settings docs in the same change as T037.
4. Prefer one sentence in OpenAPI noting packing-estimate vs L4-meaningful metrics to reduce ops confusion (T034).
5. Keep OQ-EP008-a visible in review-report until degradation steps are product-confirmed.

---

## Assumption Audit

### Valid Assumptions

| ID | Assumption | Why valid |
|----|------------|-----------|
| A-03 | Downstream LLM ~128k; ContextOS still enforces budgets | Backlog + BRD §13; budgets remain product control plane |
| A-06 | Packing-estimate metrics valid when L4 off; full L4 metrics at V1 | ADR-006; api-contract §2.3; repo `l5_phase_pack` + `l4_gate: False` |
| A-EP008-1 | L4 consumes packs without redesigning L5/L1/OKF | Architecture pipeline; brief; FR-012 |
| A-EP008-2 | Minimal HTML dashboard; no full UI suite | ep-008-brief; lean Spec Kit |
| Confirmed metrics keys | `tokens_before`, `tokens_after`, `saving_percent`, `trace` | api-contract §2.3; `test_context_contract.py` |
| ADR-006 / 011 / 009 | L4 in V1; OTel-compatible; evidenced HTTP surface | architecture-decisions.md |

### Risky Assumptions

| ID | Assumption | Risk |
|----|------------|------|
| P-EP008-1 | Default local/heuristic summarize (not external LLM) | Quality may miss BRD “LLM summarization” wording — mitigate with consent-gated optional LLM + recall/preserve gates |
| P-EP008-2 | `l4_enabled` default off | V1 exit requires L4 eventually; flag must ship on before claiming V1 done |
| A-EP008-3 | Cost-saved = token-delta first; $ rates optional | BO-02 $0.50→$0.05 KPI not fully computable until rate table (OQ-EP008-c) |
| P-EP008-3 / relevance heuristic | Reuse hybrid scores + phase_role | Exact BRD §14 formula Missing Evidence — label Proposed in code/tests |
| Soft-degrade on HTTP 200 | Trace records budget outcome without Confirmed 413/422/503 | Clients may miss hard-fail unless documented |

### Blocking Assumptions

| ID | Assumption | Status |
|----|------------|--------|
| Canonical Dev budget as normative AC | Must not assume 8k or 12k | **Blocked on OQ-07** — correctly not assumed |
| Confirmed degradation step table | Must not invent | **Blocked on OQ-EP008-a** for precise AC only |
| Confirmed dashboard serving / OTel vendor | Must not invent | **Blocked on OQ-08/09** for those contracts only — non-blocking for coding |

---

## Key Open Questions Retained

| ID | Topic | Blocking? |
|----|-------|-----------|
| **OQ-07** | Dev budget 8k (§5) vs 12k (FR-11) | **Yes** — numeric Dev AC / SC-003 Dev fixtures |
| **OQ-08** | Dashboard serving: static HTML vs API / Proposed `GET /metrics` | No |
| **OQ-09** | OTel exporter / collector vendor | No |
| OQ-EP008-a | Exact hard-fail vs degradation steps | Yes for precise step AC; Proposed prune OK |
| OQ-EP008-b | Telemetry opt-out API shape | No (non-bypass only) |
| OQ-EP008-c | Cost-saved $ rate table | No |

---

## Implementation Status Note

| Area | Status |
|------|--------|
| Spec / Plan / Tasks | **Planned** (complete triad) |
| L4 CompressionService & budgets | **Not Implemented** (Proposed modules) |
| Packing metrics baseline (EP-001/002) | **Implemented** (Confirmed keys; packing estimates; `l4_gate=false`) |
| SC-001 / SC-002 harnesses | **Planned** — not executed |
| This validation | **Planning readiness only** |

Do not treat EP-008 L4 as shipped. Do not claim compression savings or recall gates passed without command/CI evidence.
