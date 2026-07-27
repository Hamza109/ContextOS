# Validation Report

## Executive Summary

| Field | Value |
|-------|-------|
| **Feature Name** | EP-003 — L3 Symbol & LSP Navigation (Serena) (`ep-003-l3-symbol-lsp-navigation`) |
| **Review Date** | 2026-07-27 |
| **Reviewer** | ContextOS Test Validation Agent |
| **Overall Status** | Conditionally approved |
| **Overall Readiness Score** | **8.5 / 10** |
| **Implementation Readiness Decision** | **CONDITIONAL APPROVAL** |
| **Ready for Implementation** | **Yes** (with documented conditions on OQ-12 / OQ-11 / OQ-Symbol-REST / OQ-Safe-Edit-Shape / OQ-Lang-Set / OQ-IDE-2s-Harness) |

EP-003 Spec Kit triad (`spec.md` → `plan.md` → `tasks.md`) is complete, evidence-traced to backlog US-005/US-006/US-009/US-010, BRD FR-04..06 / §11 / §14 / §15, ADR-005, api-contract §3, and constitution I–V. Scope stays L3 Serena symbol navigation + Pack Context safe-edit composition (L5 consume-only). Measurable L3 claims have planned verification; **OQ-12 remains OPEN — 99% accuracy is Proposed verification design only** (no Pass/Fail invent). **No tests have been executed.**

**Verification Gate status vocabulary for this report:** requirements and tests are **Planned** only. EP-001/EP-002 orchestrator L5 modules under `services/orchestrator/` and VS Code indexing DX under `clients/vscode/` are **Implemented** (upstream). EP-003 modules (`l3_symbol.py`, `serena_mcp.py`, extension providers/commands/mcp, `contextClient.ts`) are **Planned / not present**. Nothing for EP-003 is **Executed**, **Passed**, **Failed**, **Skipped**, or **Blocked** by runtime test evidence.

---

## Evidence Reviewed

| Artifact | Path | Role |
|----------|------|------|
| Feature specification | `specs/ep-003-l3-symbol-lsp-navigation/spec.md` | Primary — Spec Gate (US-005/006/009/010; FR-001–FR-015) |
| Implementation plan | `specs/ep-003-l3-symbol-lsp-navigation/plan.md` | Primary — Planning Gate |
| Task list | `specs/ep-003-l3-symbol-lsp-navigation/tasks.md` | Primary — Task Gate (T001–T082) |
| Constitution | `.specify/memory/constitution.md` v1.0.0 | Governance I–V; Spec/Planning/Task/Verification Gates |
| Lean Spec Kit rule | `.cursor/rules/lean-spec-kit-artifacts.mdc` | Required vs forbidden adjuncts |
| EP-003 brief | `.cursor/agent-handoffs/ep-003-brief.md` | Scope lock; OQ checklist; boundary rules |
| Agent handoffs | `.cursor/agent-handoffs/handoff.md` | Spec → plan → task handoff chain (latest: task-generator) |
| Spec template | `.specify/templates/spec-template.md` | Required-section baseline |
| Plan template | `.specify/templates/plan-template.md` | Required-section baseline |
| Tasks template | `.specify/templates/tasks-template.md` | Required-section baseline |
| Lean reference validation | `specs/ep-002-l5-hybrid-search-phase-packing/validation-report.md` | Report format / gate pattern |
| Backlog | `docs/backlog/user-stories.md` (as cited by triad) | EP-003; US-005/006/009/010; OQ-12 |
| API contract | `docs/architecture/api-contract.md` §3 | Symbol proxy REST **NEEDS CLARIFICATION** / may remain MCP-only |
| Architecture (supporting) | `docs/architecture/` (overview, ADRs esp. ADR-005/002/007/009/011, tech-stack, implementation-guidelines, backend-architecture.puml — as cited) | L3 / Serena / boundary compliance |
| Live source tree | `services/orchestrator/app/{services,api,adapters,security,telemetry}/`, `clients/vscode/` | EP-001/EP-002 Confirmed present; no `l3_*` / `serena_mcp` yet |
| Extension boundary test | `clients/vscode/tests/no_client_policy_bypass.test.ts` | Confirmed present — extend planned |
| Deploy | `deploy/docker-compose.yml` | Present (reuse planned) |
| Branch | `feature/ep-003-l3-symbol-lsp-navigation` | Confirmed via `git branch --show-current` |
| Spec folder listing | `specs/ep-003-l3-symbol-lsp-navigation/` | `spec.md`, `plan.md`, `tasks.md` only prior to this report |
| Test / CI execution | — | **None reviewed** |

---

## Missing Evidence

1. **No test execution evidence reviewed; validation is limited to test planning readiness.**
2. No EP-003 application modules yet (`adapters/serena_mcp.py`, `services/l3_symbol.py`, `telemetry/symbol.py`, extension `providers/` / `commands/` / `mcp/`, `api/contextClient.ts`) — **Planned**, not Implemented.
3. No CI/build/lint artifacts for EP-003.
4. Optional Spec Kit adjuncts correctly absent (lean): `quickstart.md`, `open-questions.md`, `out-of-scope-notes.md`, `docs/design/*`, `review-report.md` (review only after implementation + tests).
5. **OQ-12** — Measurement method for Serena 99% definition accuracy — **Unresolved** (blocks SC-002 Pass claims; Proposed verification only).
6. **OQ-11** — Citation JSON shape inside packed Pack Context / `final_context` — **Missing Evidence** for Confirmed field names (shared with EP-002; attributes file:line + confidence required).
7. **OQ-Symbol-REST** — Symbol proxy REST vs MCP-only — **NEEDS CLARIFICATION** (api-contract §3); MCP-first Option A Proposed for MVP.
8. **OQ-Lang-Set** — Exact Serena language inventory beyond “12+” — **Missing Evidence** (blocks language-complete fixture matrix).
9. **OQ-Safe-Edit-Shape** — Exact safe edit plan machine schema — **Not evidenced** (behavioral intent only).
10. **OQ-Unresolved-Symbol** — Exact MVP UX for unresolved/ambiguous symbols — **Missing Evidence** (no/partial Proposed; no L1 expand).
11. **OQ-MCP-Fallback** — Confirmed regex/fallback product UX when Serena unavailable — **Missing Evidence** (BRD §13 risk noted; Proposed only).
12. **OQ-IDE-2s-Harness** — Verification harness for <2s symbol-accurate IDE context — **Missing Evidence** (blocks composed MVP exit Pass claims; shared with EP-004 US-008).
13. **OQ-01** — RBAC/authn schema — **Missing Evidence**.
14. Exact OTel metric names for L3; Serena/MCP SDK package pins — **Not evidenced** (correctly Proposed / open).
15. Spec **Status** remains `Draft` (hygiene gap vs Spec Gate claim).
16. Runtime Serena MCP availability in developer workspaces — **Not Verified** at planning time (A-EP003-1).

---

## Specification Findings

### Completeness vs Spec Kit / Constitution Specification Gate

| Check | Status | Evidence |
|-------|--------|----------|
| User scenarios prioritized & independently testable | **Met** | US-005, US-006, US-009, US-010 all P1 with Independent Test (`spec.md`) |
| FRs atomic & testable | **Met** | FR-001..FR-015 |
| NFRs measurable or labeled | **Met** | NFR-001..006; IDE <2s / 99% gaps labeled |
| Acceptance Given/When/Then | **Met** | All four user stories |
| Edge cases documented | **Met** | Edge Cases + OQs (unsupported language, unresolved, MCP down, empty filter, sandbox OOS, REST, safe-edit shape, citations, EP-004 boundary) |
| Assumptions explicit | **Met** | A-01, A-02, A-EP003-1..6 |
| Success criteria measurable or NEEDS CLARIFICATION | **Met** | SC-001..009; SC-002 OQ-12 Proposed only; SC-009 MCP-only OK |
| Requirement traceability | **Met** | Traceability + Scenario→FR map |
| Layer/surface impact | **Met** | L3 primary; L5 upstream cite-only; L1/L2/L4/L6 N/A |
| Security/privacy | **Met** | Ignore inheritance; no silent bypass; citations provenance; OQ-01 not invented |
| Template placeholders remaining | **None found** | Remaining NEEDS CLARIFICATION are intentional OQs |
| Blocking OQs visible | **Met** | Open Questions table; label rule forbids Confirmed freeze of OQ-12 method / Symbol REST / OQ-11 / safe-edit / language inventory |

### Gaps / issues (non-blocking unless noted)

1. **Status field** still `Draft` while Ready for Plan Generator claimed Yes — process hygiene gap (same pattern as EP-001/EP-002).
2. FR-003 / SC-002 cannot be verified as Pass until OQ-12 method agreed — correctly documented; **blocks verification pass claims**, not story implementation intent.
3. NFR-001 / composed <2s IDE SLA correctly deferred to shared harness with EP-004 — do not invent EP-003-only Pass.
4. A-EP003-5/6 correctly mark OQ-12 and schema/REST freezes as blocking Confirmed verification/schema, non-blocking for behavioral delivery under Proposed labels.

### Scope creep check (mandatory)

| Forbidden deliverable | Present as EP-003 acceptance? | Evidence |
|-----------------------|-------------------------------|----------|
| L1 blast / FalkorDB / `GET /blast` / `graph.html` | **No** | FR-015; Out Of Scope; ambiguous expand V1 |
| L4 Headroom product / compression dashboards | **No** | FR-015; ADR-006 cite |
| L2 / L6 | **No** | Explicit N/A |
| Full EP-004 CLI / Ask <3 clicks | **No** | US-010 conceptual dep only; Out Of Scope |
| Rename execution sandbox | **No** | FR-007; BRD §6 |
| Invented Confirmed Symbol REST | **No** | FR-012; api-contract §3 |
| Re-spec EP-001 indexing / EP-002 hybrid/phase | **No** | FR-010; cite-only |
| Confirmed freeze of OQ-12 method / OQ-11 / safe-edit schema | **No** | Explicit label rule |
| JetBrains | **No** | Out Of Scope |

**Scope verdict:** Pass — US-005/006/009/010 L3 Serena + Pack Context safe-edit surface only.

**Specification Gate verdict:** Met — with open questions carried (not invented).

---

## Planning Findings

### Completeness vs Planning Gate

| Check | Status | Evidence |
|-------|--------|----------|
| Every FR/NFR addressed | **Met** | Requirement Coverage Matrix FR-001..015 |
| Architecture defined | **Met** | Technical Approach; MCP-first Option A; Confirmed vs Proposed |
| Components identified | **Met** | Components table (Serena adapter, SymbolService, extension DX, Pack enrichment) |
| Data model changes | **Met** | Logical entities; OQ labels preserved |
| API changes | **Met** | Confirmed `POST /context` consume; Symbol REST Proposed only; no invented Appendix D |
| Security considerations | **Met** | Security Considerations + privacy inheritance |
| Performance considerations | **Met** | NFR-001 / IDE-2s harness gap; Proposed cache |
| Testing strategy | **Met** | Unit/Integration/E2E/Acceptance mapped to SC; OQ-12 Proposed only |
| Risks documented | **Met** | Risks table |
| Confirmed vs Proposed vs NEEDS CLARIFICATION | **Met** | Technical Context; Open Questions; transport Option A/B |
| Six-layer impact | **Met** | L3 primary; L5 cite-only; deferred layers explicit |
| Boundary discipline | **Met** | FastAPI orchestration; VS Code DX; MCP wiring OK; no policy reimplementation |
| Architecture deviations | **None unjustified** | Constitution Check Pass |
| Live tree grounding | **Met** | Plan inspected EP-001/EP-002 + vscode; validation re-confirmed no `l3_*` / `serena_mcp` |

### Gaps / issues

1. Dual path (extension MCP DX + optional orchestrator Serena in context pipeline) is ADR-005 Confirmed — not avoidable complexity; implementers must keep policy out of extension.
2. Safe-edit enrichment on `POST /context` is **Proposed** — must not invent Confirmed Appendix D response fields.
3. Serena/MCP SDK pins **NEEDS CLARIFICATION** — acceptable discovery in foundational tasks (T010).
4. Optional research/data-model/contracts adjuncts not generated — correct per lean Spec Kit.

**Planning Gate verdict:** Met — with OQs carried (not invented).

---

## Task Findings

### Completeness vs Task Gate

| Check | Status | Evidence |
|-------|--------|----------|
| Every requirement → impl + verification | **Met** | Task Traceability Matrix; FR→phase coverage |
| Grouped by independently deliverable stories | **Met** | Phase 3 US-005 → Phase 4 US-006 → Phase 5 US-009 → Phase 6 US-010 |
| Unique IDs | **Met** | T001–T082 |
| Exact paths when known | **Met** | `services/orchestrator/app/...` Proposed L3; `clients/vscode/...` Proposed DX |
| Discovery for unknowns | **Met** | T003–T004, T007, T018–T021, T022–T024, T029, T036, T046, T054–T056, T078–T079, T082 |
| L3 intelligence tests planned | **Met** | Definition attrs, refs ±2 + filter, rename analysis, safe-edit behavioral, citations attributes, boundary, MCP-first |
| Security / docs / telemetry / deployment | **Met** | Phases 2, 6, 7 |
| Definition of Done | **Met** | Includes OOS gate T081; OQ-12/IDE-2s no invented Pass |
| OQs not Confirmed-frozen | **Met** | Open Questions / Discovery Tasks table |
| Out-of-scope not scheduled as deliverables | **Met** | Path Conventions Out of scope; T046, T069, T081 |

### Gaps / issues

1. **SC-002** tasks T019/T024/T029/T078 correctly **blocked for Pass claims** until OQ-12 — must remain so; T029 placeholder must never be marked Passed without method + evidence.
2. **OQ-IDE-2s-Harness** tasks T020/T079 correctly block composed <2s Pass claims.
3. No tasks claim completion checkmarks filled — consistent with no EP-003 implementation (**Planned** only).
4. US-010 depends on EP-001/EP-002 upstream readiness (T009) — runtime acceptance still needs indexed fixture + working `POST /context` (A-EP003-2/3).
5. Exact Serena SDK package pin deferred to T010 — acceptable; do not invent Confirmed pin in OpenAPI.

**Task Gate verdict:** Met — ready for sequenced implementation with clarification and verification gates.

---

## Constitution Compliance

| Rule ID | Principle | Status | Notes |
|---------|-----------|--------|-------|
| I | Evidence-First | **Compliant** | Traceability to BRD/backlog/ADR-005/api-contract; OQs preserved; no invented Confirmed Symbol REST or accuracy Pass |
| II | Six-Layer Integrity | **Compliant** | L3 primary; L5 consume-only; L1/L2/L4/L6 explicit N/A; no client-side intelligence policy |
| III | Privacy / Local-First | **Compliant** | Inherit EP-001 exclusions; no cloud exfil invent for L3; provenance FR-009; RBAC schema not invented (OQ-01) |
| IV | Measurable Intelligence Claims | **Compliant** | SC-001..009 planned; OQ-12 / IDE-2s gaps labeled; no invented Pass |
| V | Surface Boundary Discipline | **Compliant** | FastAPI owns orchestration (+ optional Serena in context pipeline); VS Code owns DX; MCP wiring allowed; no silent bypass |
| Approved Tech Direction | Stack | **Compliant** | FastAPI 3.11; Serena MCP (ADR-005); VS Code first (ADR-007); OTel-compatible |
| Roadmap Governance | MVP L5+L3 | **Compliant** | Ships L3 after/with L5; does not pull L1/L4/L2/L6 |
| Specification Gate | — | **Met** (with OQs) | |
| Planning Gate | — | **Met** (with OQs) | |
| Task Gate | — | **Met** (with OQs) | |
| Verification Gate | Planned vs executed | **Compliant for this report** | Distinguishes Planned; **no Pass/Fail invented**; OQ-12 Proposed only |
| Implementation Gate | — | **N/A for EP-003 code** | Upstream EP-001/EP-002 present; EP-003 code not reviewed as delivery |

**Threat / risk notes (constitution III):** Extension reimplements symbol/search/index policy; client-side walks of excluded `.env`/ignored paths; inventing Symbol REST as Confirmed (ADR-009 drift); MCP unavailable without clear degraded UX; Pack Context consent bypass if later feeding external LLM; rename-execution creep claiming sandbox — documented in plan Risks / Security with mitigations. Path-RBAC enforcement detail remains open (OQ-01) — documented gap, not invented.

**Lean Spec Kit compliance:** Only required triad present prior to this report; no forbidden adjuncts generated. OQs carried inside triad + this report. **Constitution Applied:** Yes.

---

## Traceability Matrix

Legend — **Evidence**: Planned = artifact coverage only; Implemented = EP-001/EP-002 upstream only where noted; Verified = not claimed for EP-003.

| Requirement | Planned Component | Task Coverage | Evidence | Status |
|-------------|-------------------|---------------|----------|--------|
| FR-001 | `serena_mcp` + `l3_symbol` definition path; IDE presentation | T025–T027, T030, T032–T033 | ADR-005; Phase 3 | Covered (Planned) |
| FR-002 | Supported-language fixtures; inventory OQ-Lang-Set | T007, T022, T027, T035 | FR-04 “12+”; inventory open | Covered (Planned); matrix gated |
| FR-003 | 99% target; Proposed verification only (OQ-12) | T019, T024, T029, T078 | constitution IV; OQ-12 | Covered as **blocked verification** (Planned) |
| FR-004 | References + 2-line context | T037, T039, T042 | FR-05 | Covered (Planned) |
| FR-005 | File-type filter | T038, T040, T043 | FR-05 | Covered (Planned) |
| FR-006 | Rename scope + breaking-change count | T047–T048, T051 | FR-06 | Covered (Planned) |
| FR-007 | IDE review; no execution sandbox | T046, T049–T050, T052 | BRD §6 | Covered (Planned) |
| FR-008 | Pack Context + Serena-informed safe edit plan (behavioral) | T054, T057–T058, T060, T063–T066 | §11; OQ-Safe-Edit-Shape | Covered (Planned) |
| FR-009 | Citations file:line + confidence; no invented JSON | T055, T059, T067 | BRD §14; OQ-11 | Covered (Planned); schema freeze blocked |
| FR-010 | Consume EP-001/EP-002; do not re-spec | T009, T016, T056, T061, T064–T065 | EP-001/EP-002 cite | Covered (Planned) |
| FR-011 | FastAPI orchestration; VS Code DX | T011, T015–T017, T028, T060, T073 | constitution V; ADR-005 | Covered (Planned) |
| FR-012 | MCP-only OK; Symbol REST Proposed | T003, T021, T071 | api-contract §3 | Covered (Planned) |
| FR-013 | No silent policy bypass | T014, T017, T062, T072–T073 | constitution V | Covered (Planned) |
| FR-014 | Hover docs / document symbols | T026, T031–T032 | BRD L3; ADR-005 | Covered (Planned) |
| FR-015 | Out-of-scope layers/surfaces honored | T023, T046, T069, T081 | EP-003 brief; roadmap | Covered (Planned) |
| NFR-001 | Composed <2s IDE context | T020, T079 | BRD §15; OQ-IDE-2s-Harness | Covered (Planned); Pass blocked |
| NFR-002 | Same as FR-003 / OQ-12 | T019, T024, T029, T078 | constitution IV | Covered (Planned); Pass blocked |
| NFR-003/004 | No silent bypass; no cloud exfil invent | T014, T062, T072–T073 | constitution III | Covered (Planned) |
| NFR-005 | Authn for future Symbol REST open | T082 | api-contract | Covered (Planned) |
| NFR-006 | MCP fallback Proposed only | T018, T070 | BRD §13 | Covered (Planned) |
| SC-001 | Definition attributes | T025–T027, T030 | US-005 | Covered (Planned) |
| SC-002 | 99% accuracy | T019, T024, T029, T078 | OQ-12 | **Blocked for pass claims** |
| SC-003 | Refs + 2-line context | T037, T039, T042 | US-006 | Covered (Planned) |
| SC-004 | File-type filter | T038, T040, T043 | US-006 | Covered (Planned) |
| SC-005 | Rename analysis + IDE review | T047–T052 | US-009 | Covered (Planned) |
| SC-006 | Pack Context + safe edit plan | T057–T058, T060, T063–T066 | US-010 | Covered (Planned) |
| SC-007 | Citation attributes | T055, T059, T067 | OQ-11 open | Covered (Planned) |
| SC-008 | Boundary | T017, T028, T041, T060, T073 | constitution V | Covered (Planned) |
| SC-009 | MCP-only OK | T003, T021, T071 | api-contract §3 | Covered (Planned) |

### Orphan / missing coverage check

| Check | Result |
|-------|--------|
| Orphan requirements (no plan/tasks) | **None** |
| Orphan tasks (no requirement/OQ/setup) | **None** — Setup/Polish map to foundation, NFRs, docs, deploy, OQs |
| Missing coverage | **None** for behavioral FRs; verification of SC-002 / composed <2s explicitly gated |

---

## Risk Assessment

| Risk | Severity | Justification |
|------|----------|---------------|
| OQ-12 unresolved → cannot claim 99% Pass | **HIGH** (verification) | Story intent clear; functional definition still shippable; Pass claims blocked until method + evidence |
| Requirement ambiguity on Confirmed freezes (Symbol REST / OQ-11 / safe-edit / language set) | **MEDIUM** | Mitigated by Proposed-only implementations and MCP-first Option A |
| MCP ecosystem instability (BRD §13) | **MEDIUM** | Pin versions; Proposed error/degraded; do not Confirmed-freeze regex UX |
| Extension reimplements symbol policy | **MEDIUM** (governance) | Boundary tests T017/T073 planned; constitution V |
| Inventing Symbol REST as Confirmed | **MEDIUM** (contract) | Explicit Option A; T003/T021/T071 |
| Safe-edit schema invention | **MEDIUM** | Behavioral verification only (OQ-Safe-Edit-Shape) |
| Dependency on EP-001 index + EP-002 `POST /context` | **MEDIUM** | Upstream modules Confirmed present; runtime indexed fixture still required for US-006/010 |
| Serena local availability (A-EP003-1) | **MEDIUM** (ops) | Blocking for runtime L3 acceptance; test doubles allowed in plan |
| Performance / composed <2s harness missing | **MEDIUM** (verification) | Blocks composed MVP exit Pass only — L3 capability still shippable |
| Scope creep into L1/L4/L2/L6/EP-004/sandbox | **LOW** | Explicit OOS + T081 |
| Missing edge cases | **LOW** | Edge Cases + OQs cover primary gaps |
| Operational (Compose + Serena local) | **LOW–MEDIUM** | Compose present; Serena process config Proposed (T080) |

---

## Readiness Score

| Area | Score | Justification |
|------|-------|---------------|
| Specification Quality | **9 / 10** | Complete Spec Gate; atomic FRs; OQs explicit; Status still Draft (−0.5); residual SC-002 harness gap intentional (−0.5) |
| Planning Quality | **9 / 10** | Strong architecture, API, security, testing, risks; MCP-first Option A clear; minor SDK pin / metric-name opens |
| Task Coverage | **9 / 10** | T001–T082 map all FRs/SCs/NFRs; discovery + blocked-harness tasks correct; exact paths Proposed |
| Governance Compliance | **9.5 / 10** | Constitution I–V honored; no Confirmed freeze of OQ-12/Symbol REST/OQ-11/safe-edit; boundaries clean; lean artifacts only |
| Test Planning Readiness | **7.5 / 10** | Excellent planned coverage; SC-002 (OQ-12) + composed <2s (OQ-IDE-2s) block verification Pass readiness (planning only) |
| **Overall Readiness** | **8.5 / 10** | Triad implementation-ready under conditions; 99% accuracy and composed <2s not verifiable as Pass until methods agreed |

---

## Approval Decision

### **CONDITIONAL APPROVAL**

**Not APPROVED (unconditional)** because OQ-12 remains open and blocks SC-002 Pass claims; OQ-11 / OQ-Symbol-REST / OQ-Safe-Edit-Shape / OQ-Lang-Set block Confirmed schema/REST/inventory freezes; OQ-IDE-2s-Harness blocks composed <2s Pass claims.

**Not REJECTED** because:

- Spec / plan / tasks triad is complete, consistent, and L3-scoped (US-005/006/009/010 only).
- Every FR-001..FR-015 has planned implementation and verification (open items via discovery / Proposed / blocked-harness).
- Measurable L3 claims have planned acceptance/verification tasks with explicit **OQ-12 Proposed verification only** / no-invented-Pass rules.
- Scope does not creep into L1 blast, L4 product, L2/L6, full EP-004, rename execution sandbox, or invented Confirmed Symbol REST.
- Open questions are explicit with Proposed paths — not undocumented assumptions treated as Confirmed.
- Upstream EP-001/EP-002 L5 modules and VS Code indexing DX are Confirmed present; EP-003 L3 modules correctly absent (expected).
- Lean Spec Kit discipline honored (no forbidden adjuncts).
- No fabricated test Pass/Fail; Verification Gate honored.

### Conditions for implementation

1. May begin Phase 1–2 (setup/foundation) and US-005 definition lookup immediately on branch `feature/ep-003-l3-symbol-lsp-navigation`.
2. May proceed US-006 / US-009 / US-010 using **Proposed** MCP-first Option A, Proposed language subset fixtures, and Proposed interim safe-edit representation — must **not** Confirmed-freeze Symbol REST, OQ-11 citation JSON, safe-edit schema, or language inventory.
3. Must treat **OQ-12 as OPEN**: ship functional definition lookup; keep SC-002 verification design **Proposed only**; **do not** invent Pass/Fail or Confirmed measurement method.
4. Must **not** invent Confirmed Appendix D L3 symbol REST endpoints or new Confirmed `POST /context` fields for safe-edit enrichment.
5. Must **not** expand into L1 blast/FalkorDB, L4 Headroom product, L2/L6, rename execution sandbox, JetBrains, or full EP-004 CLI/Ask epic.
6. Must keep FastAPI↔VS Code boundary: extension owns DX only; no search/index/symbol-policy reimplementation.
7. SC-002 remains **Planned / blocked for Pass** until OQ-12 method + evidence; composed <2s remains **blocked for Pass** until OQ-IDE-2s-Harness; document scoped gaps per constitution IV if needed.
8. Update `spec.md` Status from `Draft` after PM accepts this report (hygiene; non-blocking).

### Ready for Implementation

**Yes** — under the conditions above (Conditional).

**Next agent:** `lead-developer-agent` (implementation orchestration after Spec Kit validation).

---

## Recommended Improvements

1. Set `spec.md` **Status** from `Draft` to `Approved (Conditional)` or equivalent after PM accepts this report.
2. Keep OQ-12 verification design note (T019) visible during implementation — never promote to Pass without agreed method + evidence.
3. Resolve or defer OQ-Symbol-REST explicitly as MCP-only MVP before any OpenAPI symbol router lands.
4. Lock Proposed AC language subset early (T007/T022); keep OQ-Lang-Set open for language-complete claims.
5. Choose Proposed interim safe-edit representation (T054) early; assert behavioral discriminator only (T057).
6. Produce pytest/vitest/CI execution evidence before any future PR-readiness claim of Passed tests.
7. When implementation starts, run `graphify update .` after substantial code lands (workspace rule) — N/A for this docs-only validation.
8. Confirm local Serena MCP availability (or test-double strategy) before claiming runtime L3 acceptance (A-EP003-1).

---

## Assumption Audit

### Valid Assumptions

| ID | Assumption | Why valid |
|----|------------|-----------|
| A-01 | Git SoT; monorepo ≤1M LOC for MVP | BRD §13 evidenced |
| A-02 | MVP ships VS Code first; JetBrains out | ADR-007 evidenced |
| A-EP003-3 | EP-002 `POST /context` available to consume | Live `api/context.py` + L5 modules Confirmed present |
| A-EP003-4 | US-008 conceptual dep; EP-003 does not own full Ask | EP-004 boundary explicit in brief/spec |
| A-EP003-7 | MCP-first Option A acceptable MVP pending OQ-Symbol-REST | api-contract §3 “may remain MCP-only” |

### Risky Assumptions

| ID | Assumption | Risk |
|----|------------|------|
| A-EP003-1 | Serena MCP available locally | Blocks runtime L3 acceptance if unavailable — mitigate with doubles + T080 smoke |
| A-EP003-2 | EP-001 indexing completed for indexed-workspace flows | US-006/010 runtime fail without indexed fixture |
| A-EP003-6 | Behavioral MCP delivery without Confirmed schemas | Rework if product freezes different shapes — mitigated by Proposed labels |
| Local loopback trust for API | Acceptable POC | Insecure if exposed beyond localhost (OQ-01 open) |
| Optional regex fallback | BRD §13 risk mention | Product UX Missing Evidence — keep Proposed |

### Blocking Assumptions

| Item | Assessment |
|------|------------|
| Invented Confirmed Symbol REST | **Avoided** — OQ-Symbol-REST / Option A Proposed only |
| Invented Confirmed safe-edit JSON schema | **Avoided** — OQ-Safe-Edit-Shape behavioral only |
| Invented Confirmed citation JSON | **Avoided** — OQ-11 attributes-only |
| Invented OQ-12 measure method / 99% Pass | **Avoided** — Proposed verification design only |
| Tests already Passed / CI green for EP-003 | **Not assumed** — Missing Evidence of execution |
| Serena already integrated in codebase | **Not assumed** — no `l3_*` / `serena_mcp` present |

**No blocking undocumented assumptions** that would force REJECTED. Remaining blockers are **explicit open questions** and **verification harness gaps**, not hidden assumptions.

---

## Measurable L3 Intelligence — Planning Only

| Claim | Planned tests | Executed? | Result |
|-------|---------------|-----------|--------|
| SC-001 definition file:line / signature / docstring | T025–T027, T030 | No | **Not Verified** |
| SC-002 99% definition accuracy | T019, T024, T029, T078 | No | **Blocked for pass claims** (OQ-12) |
| SC-003 refs + 2-line context | T037, T039, T042 | No | **Not Verified** |
| SC-004 file-type filter | T038, T040, T043 | No | **Not Verified** |
| SC-005 rename scope + breaking-change count; no sandbox | T047–T052 | No | **Not Verified** |
| SC-006 Pack Context + Serena-informed safe edit plan | T057–T058, T060, T063–T066 | No | **Not Verified** |
| SC-007 citations file:line + confidence | T055, T059, T067 | No | **Not Verified** |
| SC-008 FastAPI/extension boundary | T017, T028, T041, T060, T073 | No | **Not Verified** |
| SC-009 MCP-only OK (no Confirmed symbol REST) | T003, T021, T071 | No | **Not Verified** |
| NFR-001 composed <2s IDE context | T020, T079 | No | **Blocked for pass claims** (OQ-IDE-2s-Harness) |
| NFR-003/004 privacy / no silent bypass | T014, T062, T072–T073 | No | **Not Verified** |
| NFR-006 MCP unavailable degraded | T018, T070 | No | **Not Verified** (Proposed only) |

---

## Lean Artifact Check

| Artifact | Present? | Expected |
|----------|----------|----------|
| `spec.md` | **Yes** | Required |
| `plan.md` | **Yes** | Required |
| `tasks.md` | **Yes** | Required |
| `validation-report.md` | **This file** | Required after triad |
| `review-report.md` | **No** | Only after implementation + tests — correctly absent |
| `quickstart.md` | **No** | Forbidden unless asked — correctly absent |
| `open-questions.md` | **No** | Forbidden — OQs in triad + this report |
| `out-of-scope-notes.md` | **No** | Forbidden — correctly absent |
| `docs/design/ep-003-*` | **No** | Forbidden unless asked — correctly absent |

---

## Open Questions (carried — inside this report)

| ID | Topic | Blocking? | Validation handling |
|----|-------|-----------|---------------------|
| **OQ-12** | Serena 99% accuracy measurement method | Blocks verification Pass claims | **OPEN** — Proposed verification only; do not treat 99% as verifiable Pass |
| **OQ-11** | Citation JSON shape | Blocks Confirmed citation freeze | Attributes file:line + confidence; no invented keys |
| **OQ-Symbol-REST** | Symbol REST vs MCP-only | Blocks Confirmed REST | MCP-first Option A; REST Proposed/deferred |
| **OQ-Lang-Set** | Exact language inventory | Blocks language-complete matrix | Proposed subset fixtures |
| **OQ-Safe-Edit-Shape** | Safe edit plan machine shape | Blocks Confirmed schema | Behavioral intent only |
| **OQ-Unresolved-Symbol** | Unresolved/ambiguous MVP UX | Non-blocking | No/partial; no L1 expand |
| **OQ-MCP-Fallback** | Confirmed fallback UX | Non-blocking | Proposed error/degraded only |
| **OQ-IDE-2s-Harness** | <2s composed IDE harness | Blocks composed MVP exit Pass | Carry; shared with EP-004 |
| **OQ-01** | RBAC/authn schema | Non-blocking for MCP-local MVP | Do not invent; reserve hooks |

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
| OQ-12 not treated as verifiable Pass | Yes |
| No invented Confirmed Symbol REST | Yes |
| No L1 / L4 / L2 / L6 / full EP-004 expansion | Yes |
| Lean artifacts only | Yes |

**Validation iterations:** 1 (sufficient; no critical triad contradictions requiring rewrite).

---

## Return Summary (for Product Manager / Lead Developer)

| Item | Value |
|------|-------|
| Validation report path | `specs/ep-003-l3-symbol-lsp-navigation/validation-report.md` |
| Validation status | **Conditionally approved** |
| Overall readiness score | **8.5 / 10** |
| Blocking questions / issues | **OQ-12** (SC-002 Pass claims); **OQ-IDE-2s-Harness** (composed <2s Pass); Confirmed freezes blocked by **OQ-11**, **OQ-Symbol-REST**, **OQ-Safe-Edit-Shape**, **OQ-Lang-Set**. Non-blocking for story intent: OQ-Unresolved-Symbol, OQ-MCP-Fallback, OQ-01. Hygiene: spec Status still `Draft`. |
| Ready for implementation | **Yes** (conditional) |
| Constitution Applied | **Yes** |
| Next | **lead-developer-agent** |
| Issues found (summary) | Draft status hygiene; EP-003 modules not yet implemented (expected); no execution evidence (expected); OQ-12/IDE-2s verification gated; Serena runtime availability Not Verified |
| Branch / push | Still on `feature/ep-003-l3-symbol-lsp-navigation`; **only** `validation-report.md` added by this agent; **no push to main** |
