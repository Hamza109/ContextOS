# Tasks: EP-008 L4 Context Compression, Token Budgets & Cost Telemetry

**Input**: `specs/ep-008-l4-compression-budgets-telemetry/{spec.md,plan.md}`  
**Prerequisites**: EP-001/002 packing + `POST /context` metrics; US-016 consent; L5 pack/search; L3 symbols (reuse). L1 (EP-006/007) + OKF (EP-013) on main — **consume only**.  
**Branch**: `feature/ep-008-l4-compression-budgets-telemetry`

**Scope guardrails**: Deliver US-023 → US-022 → US-024 only. Do **not** redesign L1/OKF/packing/hybrid search. Do **not** invent Confirmed Dev=8k/12k (OQ-07), dashboard serving (OQ-08), or OTel exporter vendor (OQ-09). Paths below are **Proposed** unless noted Confirmed.

| Label | Meaning |
|---|---|
| **Confirmed** | Existing contract / BRD obligation |
| **Proposed** | Plan direction — not frozen product contract |
| **[OQ-07 gated]** | Must not hard-code Dev=8k or Dev=12k as product truth until OQ-07 resolves |

## Phase 1: Setup / Shared Infrastructure

- [ ] T001 [L4] [API] Discover current `/context` metrics + `l4_gate` behavior in `services/orchestrator/app/api/context.py`, `services/orchestrator/app/services/l5_phase_pack.py`, `services/orchestrator/tests/unit/test_context_metrics_mvp.py`, `tests/unit/test_phase_no_l4_gate.py`. Document Confirmed keys vs packing-estimate semantics (A-06). (FR-007, FR-012)
- [ ] T002 [P] [L4] Add **Proposed** settings to `services/orchestrator/app/config.py`: `l4_enabled` (default off — P-EP008-2), injectable `phase_budgets` map (no Confirmed Dev number), optional cost-rate table stub (rates Missing Evidence). (FR-005, FR-006; Plan Phase 0)
- [ ] T003 [P] [API] Contract tests lock Confirmed `POST /context` metrics keys (`tokens_before`, `tokens_after`, `saving_percent`, `trace`) with no new required Confirmed response fields — `services/orchestrator/tests/contract/test_context_metrics_keys.py` (extend existing if present). (FR-007; ADR-009)

**Checkpoint**: Feature flag + injectable budgets + contract lock ready; no Confirmed Dev budget invented.

## Phase 2: Foundational (Blocking)

**⚠️ BLOCKS US-023/022/024 implementation wiring**

- [ ] T004 [L4] Create **Proposed** result/types skeleton in `services/orchestrator/app/services/l4_compression.py` (`CompressionResult`: tokens_before/after, saving_percent, final_context, provenance, ratio). (Plan Data Model; FR-001, FR-007)
- [ ] T005 [P] [L4] Skeleton `services/orchestrator/app/services/l4_relevance.py` and `services/orchestrator/app/services/l4_budgets.py` (interfaces only; Design=32k as evidenced example constant OK; Dev value injectable only). (FR-005, FR-006)
- [ ] T006 [P] [L4] Skeleton `services/orchestrator/app/adapters/headroom_summarizer.py` with local/heuristic path + consented external hook stubs. (FR-002, FR-004; P-EP008-1)
- [ ] T007 [API] Wire no-op L4 hook in `services/orchestrator/app/api/context.py` after pack path: when `l4_enabled=false`, preserve packing-estimate metrics and `trace.l4_gate=false`. (FR-007, FR-010; A-06)

**Checkpoint**: Foundation ready — story work may begin.

---

## Phase 3: US-023 — Adaptive summarization + recall gate (P1) 🎯 MVP

**Goal**: Headroom-style adaptive summarization of low-relevance pack content; preserve symbols/types/TODOs; consent before external LLM; recall@10 harness scaffold.  
**Independent Test**: Large naive pack fixture → savings target 60–95%; preservation gates; recall harness runnable (no pass claim without execution).

### Tests

- [ ] T008 [P] [US-023] [L4] Unit: relevance ordering (query/phase/recency-as-available) in `services/orchestrator/tests/unit/test_l4_relevance.py`. (FR-001; algorithm Proposed)
- [ ] T009 [P] [US-023] [L4] Unit: summarizer preserves symbols, types, TODOs in `tests/unit/test_l4_summarizer_preserve.py`. (FR-002; BRD §13)
- [ ] T010 [P] [US-023] [Security] Unit: no external LLM call without consent; local path allowed — `tests/unit/test_l4_summarize_consent.py` using `security/consent_gate.py`. (FR-004; US-016)
- [ ] T011 [P] [US-023] [Security] Unit: IgnorePolicy-excluded paths never enter summarize input — `tests/unit/test_l4_ignore_policy.py`. (FR-011)
- [ ] T012 [P] [US-023] [L4] Unit: savings math on fixture pack in `tests/unit/test_l4_savings_math.py` (assert band only when fixture sized for it). (FR-001; SC-001)
- [ ] T013 [P] [US-023] [L4] Opt-in eval scaffold `services/orchestrator/tests/eval/test_l4_recall_at_10.py` + large naive pack fixture under `tests/fixtures/l4_naive_pack/` — measure recall@10 vs **>0.92**; **record only, no pass claim until run**. (FR-003; SC-002; Constitution IV)

### Implementation

- [ ] T014 [US-023] [L4] Implement Proposed relevance scoring in `l4_relevance.py` (reuse hybrid hit scores + phase_role; optional recency if present — do not invent store fields). (FR-001)
- [ ] T015 [US-023] [L4] Implement local/heuristic adaptive summarizer in `adapters/headroom_summarizer.py`; external LLM only via consent gate. (FR-001, FR-002, FR-004)
- [ ] T016 [US-023] [L4] Implement `CompressionService.compress` in `l4_compression.py` (score → summarize low-relevance → re-estimate tokens → provenance). (FR-001, FR-011)
- [ ] T017 [US-023] [API] Integrate CompressionService into `api/context.py` when `l4_enabled=true`; set **Proposed** `trace.l4_gate=true` + `l4_stage_order`; do not change Confirmed response field set. (FR-007, FR-010, FR-012)

### Acceptance

- [ ] T018 [US-023] [API] Integration: L4 on compresses `final_context`; packing-only path unchanged when L4 off — `tests/integration/test_context_l4_summarize.py`. (FR-001, FR-007; SC-001 target)

**Checkpoint**: US-023 independently testable (MVP).

---

## Phase 4: US-022 — Per-phase token budgets (P1)

**Goal**: Headroom-style phase budget enforcement with hard-fail + Proposed degradation loop.  
**Independent Test**: Injectable ceiling exceeded → degrade then hard-fail; under-budget succeeds. Design=32k fixture OK. **Dev numeric AC blocked on OQ-07.**

### Tests

- [ ] T019 [P] [US-022] [L4] Unit: under-budget success; over-budget degradation then hard-fail with **injectable** ceilings — `tests/unit/test_l4_budgets.py`. (FR-005; OQ-EP008-a Proposed prune)
- [ ] T020 [P] [US-022] [L4] Unit/integration fixture: Design phase max **32k** (FR-11 evidenced example) — `tests/unit/test_l4_budget_design_32k.py`. (FR-005, FR-006)
- [ ] T021 [US-022] [L4] **[OQ-07 gated]** Dev canonical numeric AC tests (`Dev=8k` **or** `Dev=12k`) — create as `pytest.mark.skip` / xfail until OQ-07 resolves; use parameterized injectable budgets only until then. Path: `tests/unit/test_l4_budget_dev_oq07.py`. (FR-006; SC-003)

### Implementation

- [ ] T022 [US-022] [L4] Implement budget enforcer in `l4_budgets.py` (phase → max_tokens; Proposed iterative prune of lowest-relevance units; hard-fail when unmet). Document Proposed steps; keep OQ-EP008-a open. (FR-005)
- [ ] T023 [US-022] [API] Wire budget enforce after compress in `api/context.py`; record outcome in `metrics.trace` (Proposed `budget_status` / `degraded`). Proposed HTTP `413`/`422`/`503` — **not Confirmed**; prefer explicit trace even on 200 soft-degrade. (FR-005, FR-010)
- [ ] T024 [US-022] [API] Integration: configured budget hard-fail/degrade path — `tests/integration/test_context_l4_budgets.py` (injectable ceilings; Design=32k example). (FR-005; SC-003 functional)

**Checkpoint**: US-022 independently testable without inventing Confirmed Dev budget.

---

## Phase 5: US-024 — Compression telemetry + token dashboard (P2)

**Goal**: OTel-compatible compression ratio, recall@k, cost-saved; L4-meaningful Confirmed metrics; minimal `contextos_token_dashboard.html`.  
**Independent Test**: After L4 compress, metrics + OTel attrs present; dashboard artifact shows before/after; L4-off still packing estimates.

### Tests

- [ ] T025 [P] [US-024] [Telemetry] Unit: compression ratio / cost-saved (token-delta primary; $ rates optional) math — `tests/unit/test_l4_telemetry_math.py`. (FR-008; A-EP008-3)
- [ ] T026 [P] [US-024] [API] Integration: L4 on → meaningful `tokens_*` / `saving_percent`; L4 off → packing estimates + `l4_gate=false` — `tests/integration/test_context_l4_metrics_semantics.py`. (FR-007; A-06)
- [ ] T027 [P] [US-024] [Telemetry] Contract/integration: OTel-compatible attrs emitted when L4 runs (`compression.ratio`, `compression.recall_at_k` when measured, `compression.cost_saved`) — exporter vendor **not** asserted (**[OQ-09]**). Path: `tests/unit/test_l4_otel_attrs.py`. (FR-008; SC-005)
- [ ] T028 [P] [US-024] [Viz] Integration/smoke: dashboard artifact exists and renders before/after tokens — `tests/integration/test_token_dashboard_artifact.py`. Serving choice labeled Proposed (**[OQ-08]**). (FR-009; SC-006)

### Implementation

- [ ] T029 [US-024] [Telemetry] Extend `services/orchestrator/app/telemetry/context.py` **or** add `telemetry/compression.py` to emit FR-13 metrics; honor any configured telemetry opt-out without inventing opt-out API (OQ-EP008-b). (FR-008, FR-010; Constitution V)
- [ ] T030 [US-024] [API] Ensure L4-on path populates Confirmed metrics as L4 outcomes (pre-L4 vs post-L4 per plan dual-mode table); packing path untouched when off. (FR-007; SC-004)
- [ ] T031 [US-024] [Viz] Create minimal `contextos_token_dashboard.html` under **Proposed** `services/orchestrator/app/static/` (or sibling of existing static/graph pattern). Before/after token cost only — **no** full UI design suite. Serving: Proposed static mount; do not invent Confirmed `GET /metrics`. (**[OQ-08]**; FR-009; SC-006)

**Checkpoint**: US-024 independently testable; OQ-08/09 remain unresolved labels.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T032 [P] [Security] Audit L4 summarize/telemetry paths for IgnorePolicy + provenance + no secret bodies in payloads. (FR-011; Constitution III)
- [ ] T033 [P] [L1] [L5] Regression: L1 blast/graph and OKF generate/retrieve suites still pass; no L1/OKF redesign. (FR-012)
- [ ] T034 [P] Docs: OpenAPI / `docs/architecture/api-contract.md` notes — L4-meaningful metrics when compression runs; Proposed status codes and dashboard serving labeled Proposed. (FR-007, FR-009, FR-010)
- [ ] T035 Write Spec Kit `validation-report.md` after triad (planning readiness). Runtime evidence deferred until suites execute. (Constitution I)
- [ ] T036 After implementation + tests: update validation evidence; write `review-report.md`. (Post-implementation only)
- [ ] T037 **[OQ-07 gated]** When product resolves OQ-07: unlock T021, set Confirmed Dev budget in settings docs, unskip Dev numeric AC. (FR-006; SC-003)

---

## Dependencies & Execution Order

| Order | Phase | Depends on |
|---|---|---|
| 1 | Setup T001–T003 | — |
| 2 | Foundational T004–T007 | Setup |
| 3 | US-023 T008–T018 | Foundational |
| 4 | US-022 T019–T024 | US-023 compress path (T016–T017) |
| 5 | US-024 T025–T031 | US-023 (metrics need real L4); budgets optional |
| 6 | Polish T032–T036 | Desired stories |
| — | T021 / T037 | **OQ-07 resolution** |

**Parallel**: T008–T013 after T006; T019–T020 after T005; T025–T028 after T017; T032–T034 after story checkpoints.

**Story independence**: US-023 MVP at T018; US-022 at T024; US-024 at T031.

## Implementation Strategy

1. Lock Confirmed metrics + feature flag; packing-only when L4 off (A-06).
2. Ship US-023 local/heuristic summarize + consent + preservation + recall scaffold (MVP).
3. Ship US-022 injectable budgets + Design=32k; gate Dev numeric on OQ-07.
4. Ship US-024 OTel attrs + L4-meaningful metrics + minimal HTML dashboard (serving Proposed).
5. Regression vs L1/OKF; Spec Kit validation → review after runtime.

## Definition of Done

| Criterion | Gate |
|---|---|
| FR-001..012 have tasks | Traceability matrix below |
| US-023/022/024 independently testable | Checkpoints |
| Confirmed metrics keys unchanged | T003, T026 |
| L4-on vs packing-off semantics explicit | T007, T026, T030 |
| Dev numeric AC not invented | T021, T037 gated |
| No L1/OKF redesign | T033; FR-012 |
| Consent + IgnorePolicy covered | T010, T011, T032 |
| recall@10 + symbol preservation tasks exist | T009, T013 |
| No quickstart / OQ adjunct / full UI suite | Lean Spec Kit only |

## OQ-Gated / Clarification Index

| ID | Tasks | Blocking? |
|---|---|---|
| **OQ-07** Dev 8k vs 12k | T021, T037 (and any Dev=N fixture assertions) | **Yes** for numeric Dev AC |
| **OQ-08** Dashboard serving | T028, T031 (Proposed static default) | No |
| **OQ-09** OTel exporter vendor | T027, T029 (compat only; no vendor pin) | No |
| OQ-EP008-a Degradation steps | T019, T022 (Proposed prune; Missing Evidence) | Yes for precise step AC |
| OQ-EP008-b Telemetry opt-out API | T029 (non-bypass only) | No |
| OQ-EP008-c $ rate table | T025, T029 (token-delta primary) | No |

## Task Traceability Matrix

| Tasks | FR / Stories | Plan reference | Evidence |
|---|---|---|---|
| T001–T007 | FR-006, FR-007, FR-010, FR-012 | Phase 0 Setup/Foundation | Flag, skeletons, contract lock |
| T008–T018 | US-023; FR-001–004, FR-011 | Phase 1 US-023 | Summarize, consent, recall scaffold |
| T019–T024 | US-022; FR-005–006 | Phase 2 US-022 | Budgets; OQ-07 gated Dev |
| T025–T031 | US-024; FR-007–009 | Phase 3 US-024 | OTel, metrics meaning, dashboard |
| T032–T037 | FR-010–012; SC-001–006 | Phase 4 Polish | Security, regression, Spec Kit |

## Evidence Reviewed

- `specs/ep-008-l4-compression-budgets-telemetry/{spec.md,plan.md}`
- `.cursor/agent-handoffs/ep-008-brief.md`
- `.specify/memory/constitution.md`, `.specify/templates/tasks-template.md`
- Graphify: `EP-008 CompressionService tasks Headroom budget telemetry`; `l5_phase_pack` / `post_context`
- Repo paths: `api/context.py`, `l5_phase_pack.py`, `consent_gate.py`, `telemetry/context.py`, `config.py`

## Open Questions / Discovery

- T001 discovery of exact `/context` insertion point vs OKF/L1 enrichment order (Proposed default in plan: compress returned pack body; record `l4_stage_order`).
- No Confirmed Headroom package pin — adapter stays Proposed until chosen.
- Dashboard auth / RBAC schema Missing Evidence — do not invent in T031.
