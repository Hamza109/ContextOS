# Validation Report

## Executive Summary

| Field | Value |
|-------|-------|
| **Feature Name** | EP-004 — CLI & VS Code Developer Surfaces (`ep-004-cli-vscode-surfaces`) |
| **Review Date** | 2026-07-28 |
| **Reviewer** | ContextOS Test Validation Agent |
| **Overall Status** | Conditionally approved |
| **Overall Readiness Score** | **8.6 / 10** |
| **Implementation Readiness Decision** | **CONDITIONAL APPROVAL** |
| **Ready for Implementation** | **Conditional** — Yes for thin-client surfaces (US-007 human CLI ask + US-008 Ask &lt;3 clicks); **not** for Confirmed OQ-10 schema Pass or SC-004 MVP-exit Pass without harness evidence |
| **Recommended next** | **lead-developer-agent** |

EP-004 Spec Kit triad (`spec.md` → `plan.md` → `tasks.md`) is complete, lean, and evidence-traced to backlog US-007/US-008, BO-01/BO-04, BRD §5 / §10 / §15, ADR-007, api-contract §2.3 / §6, constitution I–V, and ep-004-brief. Scope is **surfaces only**: CLI `contextos ask` + VS Code Ask ContextOS; intelligence via existing Confirmed **`POST /context`** (cite EP-002/EP-003 — no L5/L3 rebuild). **OQ-10 remains OPEN / Proposed only** — not Confirmed-frozen. **No application code or tests were executed for this validation.**

**Verification Gate vocabulary for this report:** triad requirements and tests are **Planned** only. Upstream `POST /context` (`services/orchestrator/app/api/context.py`) and VS Code `contextClient` / Pack Context are **Implemented** (consume). EP-004 CLI package and Ask command are **Planned / not present**. Nothing for EP-004 is **Executed**, **Passed**, **Failed**, **Skipped**, or **Blocked** by runtime test evidence.

---

## Evidence Reviewed

| Artifact | Path | Role |
|----------|------|------|
| Feature specification | `specs/ep-004-cli-vscode-surfaces/spec.md` | Primary — Spec Gate (US-007/US-008; FR-001–FR-010) |
| Implementation plan | `specs/ep-004-cli-vscode-surfaces/plan.md` | Primary — Planning Gate |
| Task list | `specs/ep-004-cli-vscode-surfaces/tasks.md` | Primary — Task Gate (T001–T055) |
| Constitution | `.specify/memory/constitution.md` v1.0.0 | Governance I–V; Spec/Planning/Task/Verification Gates |
| Lean Spec Kit rule | `.cursor/rules/lean-spec-kit-artifacts.mdc` | Required vs forbidden adjuncts |
| EP-004 brief | `.cursor/agent-handoffs/ep-004-brief.md` | Scope lock; OQ-10 Proposed-only; POST /context reuse |
| Spec / plan / tasks templates | `.specify/templates/{spec,plan,tasks}-template.md` | Required-section baseline |
| Validation report template | — | **Missing Evidence** — no `validation-report-template.md` under `.specify/`; format follows agent instructions + prior epic reports |
| Lean reference validation | `specs/ep-003-l3-symbol-lsp-navigation/validation-report.md` | Report format / gate pattern |
| Backlog | `docs/backlog/user-stories.md` | EP-004; US-007; US-008; OQ-10; A-02; A-05 |
| API contract | `docs/architecture/api-contract.md` §2.3 / §6 | Confirmed `POST /context`; CLI ask mapping |
| Architecture (supporting) | `docs/architecture/architecture-overview.md` §2.3; `architecture-decisions.md` ADR-007 (+ ADR-001/002/009 as cited); `implementation-guidelines.md` §1 Proposed `clients/cli/` | Boundaries / MVP surfaces |
| Live source tree | `clients/vscode/` (`contextClient.ts`, `packContext.ts`, `package.json`); `services/orchestrator/app/api/context.py` | Confirmed present; Ask command **not** evidenced; `clients/cli/` **absent** |
| Branch | `feature/ep-004-cli-vscode-surfaces` | Confirmed via `git branch --show-current` |
| Spec folder listing (pre-report) | `specs/ep-004-cli-vscode-surfaces/` | `spec.md`, `plan.md`, `tasks.md` only |
| Test / CI execution | — | **None reviewed** |

---

## Missing Evidence

1. **No test execution evidence reviewed; validation is limited to test planning readiness.**
2. No EP-004 CLI package yet (`clients/cli/` absent under `clients/` — only `vscode` present) — **Planned**, not Implemented.
3. No VS Code Ask command (`contextos.askContext` / ask* under `clients/vscode/`) — Pack Context (`contextos.packContext`) **Confirmed present**; Ask **not evidenced**.
4. No CI/build/lint artifacts for EP-004.
5. Optional Spec Kit adjuncts correctly absent (lean): `quickstart.md`, `open-questions.md`, `out-of-scope-notes.md`, `docs/design/ep-004-*`, `review-report.md` (review only after implementation + tests).
6. **OQ-10** — CLI machine-readable output schema — **Unresolved** (Proposed only; blocks Confirmed schema freeze / SC-002 Pass claims).
7. **OQ-IDE-2s-Harness** — Verification harness for &lt;2s symbol-accurate IDE Ask — **Missing Evidence** (blocks composed MVP exit / SC-004 Pass; shared with EP-003).
8. **OQ-Ask-DX** — Exact VS Code gesture sequence for &lt;3 clicks — **Proposed**; blocks UX fixture freeze only.
9. **OQ-CLI-Human-Format** — Exact human CLI layout — **Missing Evidence** for Confirmed formatting (intent “useful” Confirmed).
10. **OQ-CLI-Packaging** — CLI language / installer / module layout — **Proposed** (`clients/cli/`); discovery required before concrete paths freeze.
11. **OQ-01** — RBAC/authn mechanism — **Missing Evidence** (A-05 trusted loopback non-blocking for MVP).
12. HTTP status-code contract for `POST /context` — **Not evidenced** in api-contract (clients handle non-2xx visibly — Proposed UX).
13. Spec **Status** remains `Draft` while plan Project Structure labels `spec.md` as “approved” — process hygiene inconsistency.
14. `.specify/templates/validation-report-template.md` — **not present**.

---

## Specification Findings

### Completeness vs Spec Kit / Constitution Specification Gate

| Check | Status | Evidence |
|-------|--------|----------|
| User scenarios prioritized & independently testable | **Met** | US-007, US-008 both P1 with Independent Test (`spec.md`) |
| FRs atomic & testable | **Met** | FR-001..FR-010 |
| NFRs measurable or labeled | **Met** | NFR-001..006; CLI SLA not invented (FR-004); harness gap labeled |
| Acceptance Given/When/Then | **Met** | Both user stories |
| Edge cases documented | **Met** | Offline, unindexed, empty hits, OQ-10, A-05, other verbs OOS, JetBrains OOS, Pack vs Ask |
| Assumptions explicit | **Met** | A-02, A-05, A-EP004-1..4 |
| Success criteria measurable or NEEDS CLARIFICATION | **Met** | SC-001..006; SC-002 OQ-10 Proposed; SC-004 Pass gated |
| Requirement traceability | **Met** | Traceability + Scenario→FR map |
| Layer/surface impact | **Met** | Surfaces = CLI + VS Code; L5/L3 via `POST /context` cite-only; L1/L2/L4/L6 N/A |
| Security/privacy | **Met** | FR-010 / NFR-003..005; A-05; EP-005 out of scope cite |
| Template placeholders remaining | **None found** | Remaining NEEDS CLARIFICATION are intentional OQs (esp. OQ-10) |
| Blocking OQs visible | **Met** | Open Questions table; **OQ-10 label rule** forbids Confirmed freeze |

### Gaps / issues (non-blocking unless noted)

1. **Status field** still `Draft` while Ready for Plan Generator claimed Yes — process hygiene gap (same pattern as prior epics).
2. Plan Project Structure says `spec.md # approved` while Status = Draft — documentation inconsistency only.
3. SC-002 / FR-003 cannot claim Pass until OQ-10 resolved — correctly documented; **blocks schema Pass claims**, not human-readable CLI delivery.
4. SC-004 / NFR-001 Pass correctly deferred to OQ-IDE-2s-Harness — do not invent Pass without evidence.
5. OQ-Ask-DX leaves exact click path Proposed — NFR intent (&lt;3 clicks) Confirmed; fixture freeze open.

### Scope creep check (mandatory)

| Forbidden deliverable | Present as EP-004 acceptance? | Evidence |
|-----------------------|-------------------------------|----------|
| Rebuild L5 hybrid / phase / OQ-11 citation freeze | **No** | FR-009; Out Of Scope; cite EP-002 |
| Rebuild L3 Serena / Pack Context acceptance | **No** | FR-009; Pack leave-as-is; Ask entry only |
| JetBrains Ask parity | **No** | A-02 / ADR-007 / Out Of Scope |
| Other CLI verbs beyond `ask` | **No** | FR-005; api-contract §6 Missing Evidence taxonomy |
| L1 blast / L4 product / L2 / L6 | **No** | Explicit Out Of Scope |
| Full EP-005 privacy epic | **No** | Cite EP-001 defaults only |
| Confirmed freeze of OQ-10 schema | **No** | Explicit label rule across triad |
| New Appendix D HTTP endpoints | **No** | Out Of Scope; ADR-009 cite |
| Invented CLI p95 SLA | **No** | FR-004 |

**Scope verdict:** Pass — US-007 + US-008 thin clients of `POST /context` only.

**Specification Gate verdict:** Met — with OQs carried (not invented). **OQ-10 remains open / Proposed.**

---

## Planning Findings

### Completeness vs Planning Gate

| Check | Status | Evidence |
|-------|--------|----------|
| Technical context evidence-based or Proposed | **Met** | Technical Context table; CLI toolchain Proposed |
| Layers, APIs, stores, surfaces, telemetry identified | **Met** | ContextOS Technical Impact |
| Security, privacy, performance, reliability | **Met** | Dedicated sections; A-05; no silent bypass |
| Testing covers measurable claims | **Met** | Unit / integration / e2e / acceptance; SC-002 Proposed; SC-004 Pass gated |
| Architecture deviations | **None** | ADR-001/002/007/009 aligned |
| Every FR addressed | **Met** | Requirement Coverage Matrix FR-001..010 + NFRs |
| Components / data / API | **Met** | Components; Data Model none; API consume-only |
| Risks documented | **Met** | OQ-10, harness, packaging, upstream, UX confusion, policy creep |
| Planning assumptions reasonable | **Met** | A-02, A-05, A-EP004-1..6 labeled |

### Gaps / issues (non-blocking)

1. CLI packaging (OQ-CLI-Packaging) remains discovery — plan correctly requires Phase 0 before concrete toolchain Confirmed.
2. Ask command ID `contextos.askContext` is **Proposed** — appropriate; do not treat as Confirmed contract.
3. Optional Proposed machine mode (`--json` / `--format`) correctly non-frozen.

**Planning Gate verdict:** Met.

---

## Task Findings

### Completeness vs Task Gate

| Check | Status | Evidence |
|-------|--------|----------|
| Every requirement has implementation + verification | **Met** | Task Traceability Matrix; T016–T047 cover FR/SC |
| Components have tasks | **Met** | CLI scaffold T008–T009; ask T025–T030; Ask DX T040–T047 |
| Testing tasks exist | **Met** | T019–T024 (CLI); T035–T039 (VS Code); boundary T022/T037/T048 |
| Documentation tasks | **Met** | T031, T053 — help/README only; no adjunct Spec Kit files |
| Deployment tasks | **Met** | T054 loopback / secrets / base URL |
| Actionable, granular, unique IDs | **Met** | T001–T055; story labels `[US007]`/`[US008]` |
| Grouped by independently deliverable stories | **Met** | Phase 3 US-007 ∥ Phase 4 US-008 after foundation |
| Exact paths when known | **Met** | Confirmed vscode paths; Proposed `clients/cli/` |
| Definition of Done complete | **Met** | SC-001..006 rules; OQ-10 non-freeze |
| OQ-10 not Confirmed-frozen in tasks | **Met** | T012, T017, T023, T028, T049, T055 |

### Gaps / issues (non-blocking)

1. Several Phase 1–2 tasks are discovery/documentation (T005 OQ register) — appropriate for open OQs; not product scope creep.
2. T023/T028 allow Proposed machine-mode stub — **must not** be interpreted as schema freeze during implementation review.
3. SC-004 Pass remains blocked (T039) — correct; instrumentation (T046) allowed without inventing Pass.

**Task Gate verdict:** Met.

---

## Constitution Compliance

| Rule / Gate | Status | Evidence |
|-------------|--------|----------|
| **I Evidence-First** | **Pass** | Cites backlog, BRD, ADRs, api-contract; OQ-10 not invented/frozen; Proposed vs Confirmed labeled |
| **II Six-layer integrity** | **Pass** | Surfaces only; L5/L3 cite-only via `POST /context`; no client intelligence |
| **III Privacy / local-first** | **Pass** | No silent bypass; A-05 loopback; secrets/settings patterns; EP-005 OOS |
| **IV Measurable intelligence** | **Pass** | &lt;3 clicks (SC-003); IDE &lt;2s target (SC-004) with harness gap; no invented CLI p95 |
| **V Boundary discipline** | **Pass** | FastAPI owns orchestration; CLI/extension DX only; boundary tests planned |
| Specification Gate | **Pass** | See Specification Findings |
| Planning Gate | **Pass** | See Planning Findings |
| Task Gate | **Pass** | See Task Findings |
| Verification Gate | **N/A (planning only)** | No executed tests claimed |
| Roadmap (MVP CLI + VS Code) | **Pass** | ADR-007; EP-004 MVP exit stories |
| Lean Spec Kit artifacts | **Pass** | Only triad + this report; no adjunct files |
| ADR-007 / ADR-001 / ADR-009 | **Pass** | VS Code+CLI MVP; thin clients; no new Confirmed routes |

**Constitution Applied:** **Yes**

**Violations:** None evidenced. Residual risk = client “helpful” local search/policy during implementation — mitigated by planned boundary tests (T022/T037/T048) and review checklist.

---

## Traceability Matrix

| Requirement | Planned Component | Task Coverage | Evidence | Status |
|-------------|-------------------|---------------|----------|--------|
| FR-001 Human `contextos ask` | CLI ask + human renderer | T016, T020, T024–T027, T031 | US-007; api-contract §6 | **Covered (Planned)** |
| FR-002 Thin client → `POST /context` | CLI HTTP client | T004, T019, T022, T026 | api-contract §2.3; constitution V | **Covered (Planned)** |
| FR-003 Machine-readable when planned | Optional Proposed mode | T012, T017, T023, T028, T049 | **OQ-10 Proposed** | **Covered (Proposed; no schema freeze)** |
| FR-004 No invented CLI SLA | Performance / acceptance notes | T024 | US-007 Notes | **Covered (Planned)** |
| FR-005 No other CLI verbs | Scope lock | T018, T030, T052 | US-007 Notes | **Covered (Planned)** |
| FR-006 Ask initiation &lt;3 clicks | Ask command + contributes | T013, T032, T036, T040, T043 | BRD §10; US-008 | **Covered (Planned; OQ-Ask-DX Proposed)** |
| FR-007 Symbol-accurate IDE &lt;2s target | Ask success path + instrument | T014, T034, T039, T046 | BRD §15; OQ-IDE-2s-Harness | **Covered (target; Pass gated)** |
| FR-008 Extension DX; reuse contextClient | Ask command / presenter | T010, T035, T037, T040–T045 | constitution V; Pack patterns | **Covered (Planned)** |
| FR-009 Cite EP-002/EP-003; no re-spec | Consume `/context` only | T007, T015, T047, T050 | ep-004-brief | **Covered (Planned)** |
| FR-010 No silent policy bypass | Boundary + error surfacing | T011, T022, T029, T037, T045, T048 | constitution III/V | **Covered (Planned)** |
| NFR-001 IDE &lt;2s | Telemetry hook; harness later | T039, T046 | SC-004 | **Covered (Pass gated)** |
| NFR-002 Search p95 cite EP-002 | Cite only | Plan Performance; T007 | api-contract §2.3 | **Covered (cite)** |
| NFR-003..005 Security / A-05 / secrets | Security tasks | T011, T048, T054 | A-05; OQ-01 | **Covered (Planned)** |
| NFR-006 Visible offline/unindexed failure | CLI + VS Code error UX | T021, T029, T038, T045 | Spec Edge Cases | **Covered (Planned)** |
| SC-001 Human CLI grounded output | US-007 acceptance | T024, T051 | US-007 AC | **Covered (Planned)** |
| SC-002 Machine CLI | Proposed stub only | T023, T028, T049 | **OQ-10 open** | **Covered (Proposed)** |
| SC-003 &lt;3 clicks | Gesture fixture | T032, T036, T043 | BRD §10 | **Covered (Planned)** |
| SC-004 &lt;2s MVP exit | Blocked Pass | T039, T055 | Harness Missing Evidence | **Covered (gated)** |
| SC-005 Thin-client boundary | Boundary tests + review | T022, T037, T048, T050 | constitution V | **Covered (Planned)** |
| SC-006 No OQ-10 freeze | Governance tasks | T012, T017, T049, T055 | constitution I | **Covered (Planned)** |

### Orphans

| Type | Finding |
|------|---------|
| Orphan Requirements | **None** — all FR/NFR/SC map to plan + tasks |
| Orphan Tasks | **None material** — discovery/setup tasks map to Phase 0 / governance / OQs |
| Missing Coverage | **None blocking** for story intent |

---

## Risk Assessment

| Risk | Level | Justification |
|------|-------|---------------|
| Requirement ambiguity | **LOW** | US-007/US-008 AC clear; Proposed vs Confirmed labeled |
| Missing edge cases | **LOW** | Offline, unindexed, empty, Pack vs Ask, OQ-10 documented |
| Technical complexity (CLI scaffold from zero) | **MEDIUM** | No `clients/cli/` yet; OQ-CLI-Packaging discovery required early (T006/T008) |
| Security (client policy creep) | **MEDIUM** | Classic constitution V risk; mitigated by planned boundary tests + review |
| Performance (SC-004 Pass invent) | **MEDIUM** | Target Confirmed; Pass blocked without OQ-IDE-2s-Harness — risk is false Pass claims |
| Dependency (EP-001/002/003) | **MEDIUM** | e2e AC needs indexed repo + `POST /context` quality; surface build can use mocks (A-EP004-1..3) |
| OQ-10 schema pressure | **MEDIUM** | Temptation to Confirmed-freeze `--json` schema mid-impl — governance tasks T049/T055 required |
| Operational (loopback-only auth) | **LOW** for MVP | A-05 explicit; OQ-01 non-blocking for local stories |
| Ask vs Pack UX confusion | **LOW–MEDIUM** | Mitigated by distinct command + OQ-Ask-DX |

**Overall residual risk for implementation start:** **MEDIUM** (packaging discovery + upstream e2e + OQ-10 discipline) — acceptable under Conditional Approval.

---

## Readiness Score

| Area | Score | Justification |
|------|-------|---------------|
| Specification Quality | **9 / 10** | Complete Spec Gate; OQs explicit; OQ-10 correctly open; Status still Draft (−0.5 hygiene) |
| Planning Quality | **9 / 10** | Clear thin-client design; consume-only API; risks/testing solid; packaging Proposed |
| Task Coverage | **9 / 10** | FR↔task complete; story parallelism; tests-first; T055 OQ carry-forward |
| Governance Compliance | **9 / 10** | Constitution I–V + lean artifacts + ADR-007; no invented Confirmed contracts |
| Test Planning Readiness | **8 / 10** | Strong unit/boundary/acceptance plan; SC-004 Pass gated; no execution evidence (expected) |
| **Overall Readiness** | **8.6 / 10** | Ready to implement surfaces under documented conditions |

---

## Approval Decision

### **CONDITIONAL APPROVAL**

**Rationale:** Spec, plan, and tasks are complete, consistent, and implementation-ready for **US-007 human-readable CLI ask** and **US-008 VS Code Ask &lt;3 clicks** as thin clients of Confirmed `POST /context`. Governance correctly keeps **OQ-10 open / Proposed-only**. Gaps that remain are **non-blocking for surface delivery** but **blocking for specific Pass claims** (machine schema Pass; composed &lt;2s MVP-exit Pass). No REJECTED-level missing triad artifact, scope creep, or Confirmed invention of OQ-10.

### Conditions (must hold through implementation + review)

1. **OQ-10 stays open** — machine-readable mode may ship as **Proposed** stub only; **no** Confirmed schema freeze; **no** invented SC-002 schema Pass.
2. **SC-004 / NFR-001** — deliver Ask surface + optional latency instrumentation; **do not** claim Pass without OQ-IDE-2s-Harness evidence.
3. **CLI packaging** — complete discovery (T006/T008) before treating toolchain as Confirmed; keep `clients/cli/` Proposed until scaffold lands.
4. **Boundary discipline** — no client-side pack/search/symbol/ignore/consent engines (SC-005).
5. **No new Confirmed HTTP endpoints**; no JetBrains; no other CLI verbs; no L5/L3 rebuild; no EP-005 expansion.
6. Spec Status hygiene: promote from `Draft` when PM accepts triad (optional process fix).

### Blocking OQs (for Confirmed Pass / freeze — not for starting surface implementation)

| OQ | Blocks | Blocks implementation of story intent? |
|----|--------|----------------------------------------|
| **OQ-10** | Confirmed machine-readable schema; SC-002 Pass | **No** (human ask ships) |
| **OQ-IDE-2s-Harness** | SC-004 / composed MVP exit Pass | **No** (Ask DX ships) |
| **OQ-Ask-DX** | UX fixture freeze | **No** (NFR intent clear; Proposed gesture OK) |
| **OQ-CLI-Human-Format** | Exact layout Confirmed | **No** (“useful” AC) |
| **OQ-CLI-Packaging** | Concrete toolchain Confirmed | **No** (discovery Phase 0 first) |
| **OQ-01** | Authn/RBAC Confirmed | **No** under A-05 for local MVP |

**No OQs block starting lead-developer implementation of human CLI ask + VS Code Ask thin clients**, provided the conditions above are respected.

---

## Recommended Improvements

1. Update `spec.md` Status from `Draft` → `Validated` / `Ready for Implementation` after PM acceptance (align with plan “approved” wording).
2. During Phase 0, record the chosen **Proposed** CLI toolchain in handoff (not a Confirmed freeze of OQ-10).
3. Prefer one documented Proposed gesture for SC-003 fixtures (e.g. Command Palette → Ask → InputBox) without closing OQ-Ask-DX as Confirmed product UX forever.
4. Keep review-report.md gated until implementation + test evidence exists (lean rule).
5. Lead-dev handoff: one line that UI design suite is N/A (command/CLI DX) — do not create `docs/design/ui-not-applicable.md`.

---

## Assumption Audit

### Valid Assumptions

| ID | Assessment |
|----|------------|
| **A-02** | Valid — ADR-007 Confirmed VS Code + CLI MVP; JetBrains later |
| **A-05** | Valid for local MVP — api-contract §1 / backlog; authn Missing Evidence acknowledged |
| **A-EP004-6** | Valid — Pack Context + `contextClient` Confirmed present for reuse patterns |
| Thin-client → `POST /context` | Valid — api-contract §2.3 / §6 Confirmed intent |
| Ask command currently absent | Valid — repo inspection: `packContext` only; no ask* |

### Risky Assumptions

| ID | Assessment |
|----|------------|
| **A-EP004-1** | Risky for e2e — EP-002 `POST /context` quality assumed; mocks OK for surface build |
| **A-EP004-2** | Risky for SC-004 — symbol-accurate claim needs EP-003 enrichment on path |
| **A-EP004-3** | Risky for e2e AC — indexed workspace via EP-001 required |
| **A-EP004-5** | Risky only if discovery finds better home than Proposed `clients/cli/` — plan allows adjust |

### Blocking Assumptions

| ID | Assessment |
|----|------------|
| **A-EP004-4** (OQ-10 unresolved) | **Blocks Confirmed machine-schema freeze / SC-002 Pass** — does **not** block human-readable CLI implementation |
| None other | No assumption blocks starting US-007 human ask + US-008 Ask DX under Conditional Approval |

---

## Open Questions (carried — no separate open-questions.md)

| ID | Question | Blocking for surface impl? | Blocks Confirmed Pass / freeze? | Affects |
|----|----------|----------------------------|----------------------------------|---------|
| **OQ-10** | CLI machine-readable output schema | **No** | **Yes** — schema freeze / SC-002 Pass | FR-003; SC-002; SC-006 |
| **OQ-IDE-2s-Harness** | &lt;2s symbol-accurate IDE Ask harness | **No** | **Yes** — SC-004 / NFR-001 Pass | FR-007; SC-004 |
| **OQ-Ask-DX** | Exact &lt;3-click gesture sequence | **No** | UX fixture freeze only | FR-006; SC-003 |
| **OQ-CLI-Human-Format** | Exact human CLI layout | **No** | Layout Confirmed only | FR-001 |
| **OQ-CLI-Packaging** | CLI language / installer / layout | **No** (do discovery first) | Toolchain Confirmed only | Phase 0; A-EP004-5 |
| **OQ-01** | RBAC/authn mechanism | **No** under A-05 | Authn Confirmed | NFR-004 |

**Label rule (reaffirmed):** **OQ-10 remains open.** Machine-readable CLI schema is **Proposed only**. Do **not** Confirmed-freeze OQ-10 fields.

---

## Lean Artifact Set Confirmation

| Artifact | Present after this validation? |
|----------|--------------------------------|
| `specs/ep-004-cli-vscode-surfaces/spec.md` | **Yes** |
| `specs/ep-004-cli-vscode-surfaces/plan.md` | **Yes** |
| `specs/ep-004-cli-vscode-surfaces/tasks.md` | **Yes** |
| `specs/ep-004-cli-vscode-surfaces/validation-report.md` | **Yes** (this file) |
| Forbidden adjuncts (`quickstart.md`, `open-questions.md`, `out-of-scope-notes.md`, `docs/design/ep-004-*`) | **Absent** (correct) |

**Only the four lean Spec Kit artifacts exist for this feature** (plus upstream cite-only specs elsewhere).

---

## PM Return Summary

| Field | Value |
|-------|-------|
| **validation-report.md path** | `specs/ep-004-cli-vscode-surfaces/validation-report.md` |
| **Validation status** | **Conditionally Approved** |
| **Numeric score** | **8.6 / 10** |
| **Blocking OQs** | **OQ-10** (schema Pass/freeze only); **OQ-IDE-2s-Harness** (SC-004 Pass only). None block starting surface implementation. |
| **Ready for implementation** | **Conditional** |
| **Lean four-artifact set** | **Confirmed** (spec, plan, tasks, validation-report only) |
| **Constitution Applied** | **Yes** |
| **Recommend next** | **lead-developer-agent** |
