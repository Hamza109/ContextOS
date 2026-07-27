# Project Governance Review Report

---

## Executive Summary

| Field | Value |
|-------|-------|
| **Feature Name** | EP-004 — CLI & VS Code Developer Surfaces (`ep-004-cli-vscode-surfaces`) |
| **Branch** | `feature/ep-004-cli-vscode-surfaces` |
| **Review Date** | 2026-07-28 |
| **Reviewer** | ContextOS review-pr-readiness-agent |
| **Overall Status** | 🟡 **APPROVED WITH CONCERNS** |
| **Overall Readiness Score** | **7.8 / 10** |
| **PR Decision** | 🟡 **READY FOR PR WITH COMMENTS** (Conditional) |
| **PR Ready** | **Conditional** |
| **Verdict** | **Conditionally Ready** |

### Executive Summary

EP-004 delivers MVP **thin-client surfaces** for US-007 (`contextos ask` under `clients/cli/`) and US-008 (VS Code `contextos.askContext` + InputBox), both consuming Confirmed **`POST /context`** only. **No FastAPI / L5 / L3 rebuild**, **no JetBrains**, **no invented APIs or extra CLI verbs**. Reviewer re-ran tests: **CLI 11 passed** + **tsc lint Pass**; **VS Code 37 passed / 1 skipped**. Success criteria: **SC-001 / SC-003 / SC-005 / SC-006 Pass**; **SC-002 Skipped** (OQ-10 Proposed; `--json` flag smoke only); **SC-004 Skipped/Blocked** (OQ-IDE-2s-Harness). Live indexed-repo e2e **not run** (mocked only). Open OQs remain **Proposed** — must not be Confirmed-frozen. **Conditional PR Ready** if the PR body discloses SC-002 / SC-004 / live-e2e / OQ status; not ready for unconditional “all SC Passed” or MVP-exit &lt;2s claims.

---

## Health Dashboard

| Area                    | Status | Score |
| ----------------------- | ------ | ----- |
| Constitution Compliance | 🟢 | 9 / 10 |
| Governance Compliance   | 🟢 | 8.5 / 10 |
| Requirements            | 🟢 | 9 / 10 |
| Architecture            | 🟢 | 9 / 10 |
| Task Coverage           | 🟢 | 9 / 10 |
| Security                | 🟢 | 8 / 10 |
| Performance             | 🟡 | 5.5 / 10 |
| Testing                 | 🟡 | 7.5 / 10 |
| Documentation           | 🟢 | 8.5 / 10 |
| Deployment Readiness    | 🟡 | 6.5 / 10 |
| Code Quality            | 🟢 | 8.5 / 10 |
| PR Readiness            | 🟡 | 7.5 / 10 |

---

# Constitution Compliance Review

**Status:** 🟢 Compliant (with documented verification gaps)  
**Score:** 9 / 10

### Findings

| Principle | Assessment | Evidence |
|-----------|------------|----------|
| I Evidence-First | Compliant | Triad + validation-report + implementation traced to US-007/US-008, BO-01/BO-04, api-contract §2.3/§6, ADR-007; OQ-10 not Confirmed-frozen; no invented SC-002 schema Pass or SC-004 &lt;2s Pass |
| II Six-Layer Integrity | Compliant | Surfaces only; L5/L3 **cite-only** via `POST /context`; L1/L2/L4/L6 N/A; no orchestrator intelligence changes (`git diff` empty under `services/orchestrator`) |
| III Privacy / Local-First | Compliant | Clients inherit orchestrator policy; boundary tests forbid local ignore/consent/pack/search; A-05 loopback; OQ-01 open; no secrets in reviewed EP-004 paths |
| IV Measurable Claims | Compliant | SC-001/003 Pass with unit/fixture evidence; SC-002 Skipped (OQ-10); SC-004 Blocked placeholder in `ask_context_dx.test.ts` (T039) — no invented latency Pass |
| V Boundary Discipline | Compliant | CLI `postContext` + extension reuse of `contextClient.postContext`; DX/render only; `no_client_policy_bypass.test.ts` includes Ask paths |

### Violations

None critical. Minor process: Spec Status may still read `Draft` (validation-report hygiene); work largely **uncommitted** on feature branch.

### Recommendations

1. PR body must label **SC-002 Skipped** and **SC-004 Blocked**.  
2. Keep **OQ-10**, **OQ-IDE-2s-Harness**, **OQ-Ask-DX**, **OQ-CLI-Human-Format**, **OQ-01**, **OQ-CLI-Packaging** OPEN / Proposed.  
3. Disclose live e2e as **Not Verified** (mocked coverage only).

---

# Governance Compliance Review

| Rule ID | Status | Severity | Finding |
| ------- | ------ | -------- | ------- |
| GR-CONST-I | 🟢 | LOW | Evidence-first; OQs and Missing Evidence labeled in code/tests/help |
| GR-CONST-II | 🟢 | LOW | Surfaces-only; no L5/L3 rebuild; no L1/L4/L2/L6 creep |
| GR-CONST-III | 🟢 | LOW | Thin clients; A-05; OQ-01 open; no silent policy bypass (SC-005 Pass) |
| GR-CONST-IV | 🟡 | MEDIUM | SC-004 &lt;2s Blocked; SC-002 schema Pass not claimed — correct, but BRD IDE exit unverified |
| GR-CONST-V | 🟢 | LOW | FastAPI owns intelligence; CLI + VS Code own DX only |
| GR-SPEC-GATE | 🟢 | LOW | Spec triad + validation-report present; lean adjuncts absent |
| GR-PLAN-GATE | 🟢 | LOW | Plan covers consume-only API, security, testing, OQ gates |
| GR-TASK-GATE | 🟢 | LOW | T001–T055 mapped; checkboxes marked `[x]` post-impl |
| GR-IMPL-GATE | 🟢 | LOW | `clients/cli/` ask + `askContext.ts` / presenter / package contributes present |
| GR-VERIFY-GATE | 🟢 | LOW | Reviewer re-ran: CLI 11p + lint; VS Code 37p/1s; vocabulary honored for SC-002/004 |
| GR-SEC-SECRETS | 🟢 | LOW | No `.env`/secrets in EP-004 client trees reviewed; base URL via env/settings |
| GR-CI | 🟡 | MEDIUM | `.github/workflows/ci.yml` present (untracked); **no CI run evidence** for this unpushed branch |
| GR-OQ-FREEZE | 🟢 | LOW | OQ-10 Proposed labels in CLI help / machineRenderer; no Confirmed schema freeze |
| GR-LEAN | 🟢 | LOW | No quickstart / open-questions.md / out-of-scope-notes / docs/design/ep-004-* |
| GR-SCOPE | 🟢 | LOW | No JetBrains; no extra CLI verbs; no new Appendix D endpoints |

## Governance Summary

| Metric | Value |
|--------|-------|
| Total Rules Evaluated | 15 |
| Passed | 13 |
| Warnings | 2 |
| Failures | 0 |
| Governance Compliance Score | **8.5 / 10** |

---

# Requirements Review

**Status:** 🟢 Good  
**Score:** 9 / 10

### Strengths

- US-007 / US-008 P1 with independent tests (`spec.md`).  
- FR-001..FR-010 atomic; SC-001..SC-006 measurable or explicitly gated.  
- Out-of-scope prevents JetBrains, extra verbs, L5/L3 rebuild, OQ-10 freeze, invent APIs.

### Concerns

- Spec Status still `Draft` while implementation complete (hygiene).  
- FR-003 / FR-007 cannot claim Confirmed schema / &lt;2s Pass until OQs resolve (correctly documented).

### Recommendations

- PR body: SC-001/003/005/006 Met (executed); SC-002 Skipped; SC-004 Blocked.

---

# Architecture Review

**Status:** 🟢 Good  
**Score:** 9 / 10

### Strengths

- Clear thin-client pattern: CLI `contextClient.ts` + VS Code reuse of `api/contextClient.ts`.  
- Ask distinct from Pack Context (`contextos.askContext` vs `contextos.packContext`).  
- No new stores; no new HTTP endpoints; ADR-001/002/007/009 aligned.  
- Machine mode explicitly Proposed (`machineRenderer.ts` schema note).

### Concerns

- CLI packaging (**OQ-CLI-Packaging**) remains Proposed (npm package under `clients/cli/` — not Confirmed installer story).  
- Duplicate thin HTTP clients (CLI vs extension) — acceptable for MVP; shared package not required by spec.

### Recommendations

- Do not invent PyPI/standalone Confirmed packaging in this PR.  
- Keep human format Proposed (**OQ-CLI-Human-Format**).

---

# Task Coverage Review

**Status:** 🟢 Good  
**Score:** 9 / 10  
**Coverage Percentage:** ~100% of T001–T055 marked complete in `tasks.md` with matching implementation/test evidence

### Findings

| Phase | Status | Evidence |
|-------|--------|----------|
| Setup T001–T007 | Done | Inventory + OQs in triad |
| Foundation T008–T015 | Done | `clients/cli/` scaffold; boundary plan |
| US-007 T016–T031 | Done | `ask.ts`, renderers, `ask.test.ts` (11) |
| US-008 T032–T047 | Done | `askContext.ts`, presenter, package contributes, `ask_context_dx.test.ts` (10) |
| Polish T048–T055 | Done | Boundary + OQ carry-forward; README/--help only |

### Recommendations

- Keep T039/T023 as Skipped/Blocked documentation in PR — do not reclassify as Pass.

---

# Security Review

**Status:** 🟢 Acceptable for local MVP surfaces  
**Score:** 8 / 10

### Findings

- **Authn:** A-05 trusted loopback; **OQ-01** Missing Evidence — non-blocking for local MVP (NFR-004).  
- **Bypass:** CLI + extension boundary tests assert no local hybrid search / pack / symbol / ignore / consent engines (`ask.test.ts`, `no_client_policy_bypass.test.ts`).  
- **Secrets:** Base URL via `CONTEXTOS_ORCHESTRATOR_BASE_URL` / `contextos.orchestratorBaseUrl`; no secrets committed in reviewed paths.  
- **Validation:** Orchestrator-owned; clients surface non-2xx / network failures (NFR-006 Proposed copy).  
- **Webview/CSP:** N/A — no new Webview/dashboard for EP-004 (UI N/A one-liner).

### Violations

None HIGH for scoped MVP.

### Applicable Governance Rules

GR-CONST-III, GR-CONST-V, GR-SEC-SECRETS, FR-010 / NFR-003..005

### Recommendations

- Do not invent authn schemes in this PR.  
- Future non-loopback deployments need OQ-01 resolution.

---

# Performance Review

**Status:** 🟡 Partial — instrumentation only  
**Score:** 5.5 / 10

### Findings

- **NFR-001 / SC-004:** Target &lt;2s symbol-accurate IDE Ask — **Blocked** without **OQ-IDE-2s-Harness**. Latency log present (`ASK_LATENCY_LOG_PREFIX` / `[ContextOS][obs][ask]`) — Proposed instrumentation only; test explicitly forbids threshold Pass invent (`ask_context_dx.test.ts` T039).  
- **FR-004:** No invented CLI p95 — compliant.  
- **Live latency:** Not Verified (mocked unit only; live e2e not run).

### Recommendations

- PR must not claim IDE &lt;2s Pass.  
- Resolve OQ-IDE-2s-Harness with EP-002/EP-003 composed harness before MVP-exit Pass.

---

# Testing Review

**Status:** 🟡 Good for unit/mock surfaces; e2e gap  
**Score:** 7.5 / 10

### Coverage Summary

| Test Type         | Status |
| ----------------- | ------ |
| Unit Tests        | 🟢 Pass — CLI 11; Ask DX 10 within VS Code suite |
| Integration Tests | 🟡 Mocked HTTP only — no live orchestrator integration this session |
| E2E Tests         | 🔴 Missing Evidence — live indexed repo smoke **not run** (A-EP004-3) |
| Acceptance Tests  | 🟡 SC-001/003/005/006 Pass (unit/fixture); SC-002 Skipped; SC-004 Blocked |

### Findings

| SC | Status | Evidence |
|----|--------|----------|
| SC-001 | **Pass** | `clients/cli/tests/ask.test.ts` human renderer + mocked `POST /context` (reviewer: 11 passed) |
| SC-002 | **Skipped** | OQ-10 Proposed; `--json` flag smoke only; no Confirmed schema Pass |
| SC-003 | **Pass** | Proposed palette fixture 1–2 gestures &lt;3 in `ask_context_dx.test.ts` |
| SC-004 | **Skipped / Blocked** | OQ-IDE-2s-Harness; blocked placeholder test; latency log only |
| SC-005 | **Pass** | CLI boundary + `no_client_policy_bypass` Ask paths |
| SC-006 | **Pass** | Proposed labels in CLI help / `machineRenderer.ts`; no Confirmed freeze |

**Reviewer execution (2026-07-28):**

| Command | Result |
|---------|--------|
| `cd clients/cli && npm test` | **11 passed** |
| `cd clients/cli && npm run lint` | **Pass** (`tsc --noEmit`) |
| `cd clients/vscode && npm test` | **37 passed, 1 skipped** |

Also consistent with `.cursor/agent-handoffs/ep-004-testing-brief.md`.

### Missing Coverage

1. Live e2e against indexed orchestrator.  
2. Confirmed machine-schema acceptance (blocked on OQ-10).  
3. Composed &lt;2s IDE harness (blocked on OQ-IDE-2s-Harness).  
4. CI pipeline green for this branch.

### Recommendations

- Optional follow-up: loopback smoke once EP-001 index + orchestrator available.  
- Do not invent Pass for SC-002 / SC-004.

---

# Documentation Review

**Status:** 🟢 Good (lean)  
**Score:** 8.5 / 10

### Findings

- Spec Kit complete: `spec.md`, `plan.md`, `tasks.md`, `validation-report.md`, this `review-report.md`.  
- Lean: no `quickstart.md`, `open-questions.md`, `out-of-scope-notes.md`, `docs/design/ep-004-*`.  
- CLI: `clients/cli/README.md` + `--help` only (T031/T053).  
- UI/UX dashboard design: **N/A** (one-liner; no design suite) — correct for non-Webview epic.  
- Open Questions listed in-file in triad (not adjunct files).

### Recommendations

- Optionally flip Spec Status from Draft → Implemented after PR open (hygiene).

---

# Deployment Readiness Review

**Status:** 🟡 Local loopback ready; CI/ops incomplete  
**Score:** 6.5 / 10

### Findings

- **Env:** `CONTEXTOS_ORCHESTRATOR_BASE_URL` (CLI); `contextos.orchestratorBaseUrl` (extension) — patterned.  
- **Monitoring:** Proposed client latency log only; orchestrator OTel remains EP-002/003 cite.  
- **Rollback:** Client-only change — remove Ask command / CLI package; no store migrations.  
- **CI/CD:** Workflow file present under `.github/` (untracked in status); **no run evidence** for feature branch.  
- **Packaging:** OQ-CLI-Packaging open — Proposed npm package.

### Recommendations

- Commit + push + obtain CI before merge confidence.  
- Document loopback assumptions in PR (A-05).

---

# Code Quality Review

**Status:** 🟢 Good  
**Score:** 8.5 / 10

### Implementation files reviewed

| Area | Paths |
|------|-------|
| CLI | `clients/cli/src/{ask,cli,contextClient,humanRenderer,machineRenderer,types,bin,index}.ts`, `tests/ask.test.ts`, `package.json`, `README.md` |
| VS Code | `src/commands/askContext.ts`, `src/providers/askContextPresenter.ts`, `commands/index.ts`, `providers/index.ts`, `extension.ts`, `package.json`, `tests/ask_context_dx.test.ts`, `tests/no_client_policy_bypass.test.ts` |
| Orchestrator | **No changes** in working tree for EP-004 |

### Findings

- Maintainable mirrors of Pack Context patterns; injectable `fetchImpl` / deps for tests.  
- Error paths visible (Proposed copy).  
- Type-safe Confirmed `ContextRequest` / `ContextResponse` field usage.  
- OQ-10 labeled in help and machine renderer (`_schema` Proposed note).  
- Click fixture and SC-004 gate documented in source comments + tests.

### Code Smells

- Two parallel HTTP thin clients (CLI vs extension) — acceptable MVP duplication.  
- Human CLI layout Proposed only — intentional.

### Recommendations

- Keep Proposed labels if refining `--json` envelope before OQ-10 resolution.

### Scope confirmation (mandatory)

| Forbidden | Present? | Evidence |
|-----------|----------|----------|
| JetBrains | **No** | No JetBrains paths/refs under `clients/cli`; extension VS Code only |
| L5/L3 rebuild | **No** | No orchestrator diff; boundary tests forbid local search/pack/symbol |
| Invented APIs / new Appendix D routes | **No** | Consume `POST /context` only |
| Extra CLI verbs | **No** | `ask` only (FR-005); help documents ask |

---

# Traceability Matrix

| Requirement | Plan Coverage | Task Coverage | Implementation Coverage | Status |
| ----------- | ------------- | ------------- | ----------------------- | ------ |
| FR-001 Human `contextos ask` | ✅ | T025–T027, T020, T024 | `ask.ts`, `humanRenderer.ts` | 🟢 |
| FR-002 Thin → `POST /context` | ✅ | T019, T026, T022 | `contextClient.ts` | 🟢 |
| FR-003 Machine when planned (OQ-10) | ✅ Proposed | T023, T028, T049 | `machineRenderer.ts`, `--json` | 🟡 Proposed / SC-002 Skipped |
| FR-004 No invented CLI SLA | ✅ | T024 | No CLI p95 asserts | 🟢 |
| FR-005 No other verbs | ✅ | T018, T030, T052 | CLI ask-only | 🟢 |
| FR-006 Ask &lt;3 clicks | ✅ | T032, T036, T043 | package.json + fixture | 🟢 SC-003 Pass (Proposed fixture) |
| FR-007 IDE &lt;2s symbol-accurate | ✅ gated | T034, T039, T046 | latency log only | 🔴 SC-004 Blocked |
| FR-008 Extension DX + `postContext` | ✅ | T035, T040–T045 | `askContext.ts` | 🟢 |
| FR-009 Cite EP-002/003 only | ✅ | T007, T050 | consume-only | 🟢 |
| FR-010 No silent bypass | ✅ | T022, T037, T048 | boundary tests | 🟢 |
| SC-001 | ✅ | T020, T024 | ask.test.ts | 🟢 Pass |
| SC-002 | ✅ Proposed | T023 | flag smoke | 🟡 Skipped |
| SC-003 | ✅ | T036 | ask_context_dx | 🟢 Pass |
| SC-004 | ✅ gated | T039 | blocked placeholder | 🔴 Blocked |
| SC-005 | ✅ | T022/T037/T048 | CLI + extension | 🟢 Pass |
| SC-006 | ✅ | T049 | Proposed labels | 🟢 Pass |

---

# Risk Assessment

## 🔴 High Risks

1. **SC-004 / NFR-001 unverified** — composed IDE &lt;2s symbol-accurate Pass blocked (**OQ-IDE-2s-Harness**). Claiming MVP-exit Pass would violate constitution IV.  
2. **Live e2e Missing Evidence** — human/IDE ask against indexed orchestrator not executed; production DX path Not Verified beyond mocks.

*These block unconditional “fully verified / all SC Pass” approval; they do **not** block a conditional feature-branch PR when disclosed.*

## 🟡 Medium Risks

1. **OQ-10** open — machine-readable schema not Confirmed; SC-002 Skipped.  
2. **OQ-Ask-DX** — gesture fixture Proposed (palette 1–2); UX freeze open.  
3. **OQ-CLI-Human-Format** / **OQ-CLI-Packaging** — layout and installer Proposed.  
4. **OQ-01** — authn Missing Evidence beyond A-05.  
5. **CI** — no green run evidence for this branch (unpushed / uncommitted).  
6. Spec Status still Draft (process hygiene).

## 🟢 Low Risks

1. Duplicate HTTP clients CLI vs extension.  
2. VS Code suite 1 skipped (pre-existing observational timing — unrelated to Ask).  
3. UI/UX design N/A correctly omitted.

---

# Action Items

## 🔴 Must Fix Before PR

No **code** blockers for opening a **conditional** feature-branch PR **if** the PR body honors:

1. Label **SC-002** as **Skipped** (OQ-10) — do not claim Confirmed schema Pass.  
2. Label **SC-004** as **Blocked** (OQ-IDE-2s-Harness) — do not claim &lt;2s Pass.  
3. Keep listed OQs **OPEN / Proposed**.  
4. State live indexed e2e as **Not Verified** (mocked only).  
5. Do not expand into JetBrains / L5-L3 rebuild / invent APIs / extra CLI verbs.

*If product requires SC-002 Pass, SC-004 Pass, or live e2e Pass before any PR: those remain reject conditions for unconditional readiness.*

## 🟡 Recommended Improvements

1. Commit EP-004 artifacts on feature branch; push; obtain CI evidence before merge.  
2. Optional loopback smoke when indexed orchestrator available (A-EP004-3).  
3. Resolve OQ-10 / OQ-IDE-2s-Harness / OQ-Ask-DX for future Confirmed Pass claims.  
4. Flip Spec Status Draft → Implemented when desired.

## 🟢 Future Enhancements

1. Confirmed CLI machine schema after OQ-10.  
2. Shared client package for CLI + extension HTTP.  
3. Authn/RBAC (OQ-01) for non-loopback.  
4. JetBrains Ask parity (out of scope — ADR-007 Future).

---

# Pull Request Readiness Assessment

## PR Readiness Status

🟡 **READY FOR PR WITH COMMENTS** (Conditional)

**PR Ready:** **Conditional**  
**Verdict:** **Conditionally Ready**

### Conditions

1. PR description discloses SC-002 Skipped and SC-004 Blocked.  
2. OQs remain Proposed (no Confirmed freezes).  
3. Live e2e called out as Not Verified.  
4. CI must be run after push before merge confidence.  
5. Scope lock: no JetBrains / L5-L3 rebuild / invent APIs.

## PR Gate Checklist

| Check                       | Status |
| --------------------------- | ------ |
| Constitution Compliant      | 🟢 |
| Governance Rules Compliant  | 🟡 (warnings: CI evidence, SC-004 measurable claim) |
| Requirements Covered        | 🟢 behavioral surfaces; 🟡 schema/&lt;2s verify |
| Acceptance Criteria Covered | 🟡 SC-001/003/005/006 Pass; SC-002 Skipped; SC-004 Blocked |
| Architecture Approved       | 🟢 (thin clients; consume-only) |
| Tasks Completed             | 🟢 T001–T055 `[x]` with impl evidence |
| Unit Tests Passing          | 🟢 CLI 11; VS Code suite includes Ask (10) |
| Integration Tests Passing   | 🟡 Mocked HTTP; live integration Missing Evidence |
| E2E Tests Passing           | 🔴 Live indexed e2e not run |
| Security Review Completed   | 🟢 (this report) |
| Documentation Updated       | 🟢 lean Spec Kit + README/--help |
| No High Risks Remaining     | 🔴 High risks remain on SC-004 / live e2e — **accepted as conditions**, not silent Pass |
| CI/CD Checks Passing        | 🔴 Missing Evidence (branch not pushed / no CI run reviewed) |
| Deployment Ready            | 🟡 Local loopback assumptions; packaging Proposed |

## Blocking Issues

- **Not blocking conditional PR open:** SC-002 Skipped; SC-004 Blocked; open OQs; live e2e Not Verified — when disclosed.  
- **Blocking unconditional “fully approved / all SC Passed” claim:** SC-002 schema Pass, SC-004 &lt;2s Pass, live e2e Pass, CI green evidence.  
- **Process:** Commit + push required before remote PR/CI evidence exists.  
- **This agent did not commit, push, or open a PR** (per instructions).

## PR Recommendation

**Ready for PR with comments** — same conditional pattern as EP-002 / EP-003 surface/intel gates.

- GR-VERIFY-GATE satisfied for executed suites (CLI 11p + lint; VS Code 37p/1s).  
- GR-CONST-IV satisfied by **not** inventing Pass for OQ-10 schema or &lt;2s.  
- GR-OQ-FREEZE / SC-006 / FR-003 satisfied (Proposed `--json` only).  
- GR-SCOPE satisfied (no JetBrains / L5-L3 rebuild / invent APIs).  
- GR-CI warning: obtain CI after push before merge.

Do **not** merge claiming Confirmed OQ-10 schema or BRD IDE &lt;2s Pass.

---

# Final Verdict

| Field | Value |
|-------|-------|
| **Approval Status** | 🟡 **APPROVED WITH CONCERNS** |
| **PR Decision** | 🟡 **READY FOR PR WITH COMMENTS** |
| **PR Ready** | **Conditional** |
| **Verdict** | **Conditionally Ready** |
| **Overall Readiness Score** | **7.8 / 10** |

### Issue Summary

| Severity | Count | Themes |
|----------|-------|--------|
| High Risks | 2 | SC-004 &lt;2s Blocked; live e2e Missing Evidence |
| Medium Risks | 6 | OQ-10; OQ-Ask-DX; human format/packaging; OQ-01; CI; Spec Draft |
| Low Risks | 3 | Dual HTTP clients; pre-existing vitest skip; UI N/A |
| Governance Violations | 0 Failures | 2 Warnings (CI, measurable IDE claim) |
| Constitution Violations | 0 critical | Verification gaps documented |

### Open Questions (must remain OPEN / Proposed)

| ID | Blocking impact |
|----|-----------------|
| **OQ-10** | Blocks Confirmed machine-schema freeze / SC-002 Pass |
| **OQ-IDE-2s-Harness** | Blocks SC-004 / composed MVP-exit &lt;2s Pass |
| **OQ-Ask-DX** | Blocks Confirmed UX gesture freeze (fixture Proposed) |
| **OQ-CLI-Human-Format** | Exact human layout Missing Evidence |
| **OQ-01** | Authn/RBAC Missing Evidence (A-05 non-blocking local) |
| **OQ-CLI-Packaging** | Installer/runtime Confirmed freeze open |

### Final Summary

EP-004 CLI & VS Code Developer Surfaces implements and unit-tests US-007 human `contextos ask` and US-008 Ask ContextOS (&lt;3-click Proposed fixture) as thin clients of Confirmed `POST /context`. Boundary and governance checks pass; **SC-002 and SC-004 remain Skipped/Blocked**; live e2e and CI are Missing Evidence. **No JetBrains, no L5/L3 rebuild, no invented APIs.** **Conditional PR Ready** on `feature/ep-004-cli-vscode-surfaces` with disclosure conditions; not ready for unconditional merge or BRD-scale Pass claims.

---

## Evidence Reviewed

| Artifact | Path / Source |
|----------|---------------|
| Constitution | `.specify/memory/constitution.md` v1.0.0 |
| Spec triad | `specs/ep-004-cli-vscode-surfaces/{spec,plan,tasks}.md` |
| Validation report | `specs/ep-004-cli-vscode-surfaces/validation-report.md` |
| Testing brief | `.cursor/agent-handoffs/ep-004-testing-brief.md` |
| Feature / impl briefs | `.cursor/agent-handoffs/ep-004-brief.md`, `ep-004-impl-brief.md` |
| Handoffs | `.cursor/agent-handoffs/handoff.md` (EP-004 blocks) |
| Lean rule | `.cursor/rules/lean-spec-kit-artifacts.mdc` |
| CLI impl + tests | `clients/cli/**` (ask, renderers, contextClient, ask.test.ts) |
| VS Code Ask | `askContext.ts`, `askContextPresenter.ts`, `package.json`, `extension.ts`, indexes |
| Boundary / DX tests | `ask_context_dx.test.ts`, `no_client_policy_bypass.test.ts` |
| Test execution | Reviewer: CLI 11p + lint Pass; VS Code 37p/1s |
| Orchestrator | Confirmed **no** EP-004 diff under `services/orchestrator` |
| CI file | `.github/workflows/ci.yml` (presence only — no run) |
| Git | branch `feature/ep-004-cli-vscode-surfaces`; dirty/untracked EP-004 tree; **not pushed** |
| Format reference | `specs/ep-003-l3-symbol-lsp-navigation/review-report.md` |
| Lean check | no quickstart / open-questions.md / out-of-scope-notes / docs/design/ep-004-* |

## Missing Evidence

1. CI run results for this feature branch.  
2. Live e2e against indexed orchestrator (A-EP004-3).  
3. SC-002 Confirmed schema Pass (OQ-10).  
4. SC-004 &lt;2s Pass (OQ-IDE-2s-Harness).  
5. Confirmed CLI packaging / human-format / Ask-DX freeze.  
6. Authn beyond A-05 (OQ-01).  
7. Remote push / PR URL (intentionally not created by this agent).

## Planned vs Implemented vs Verified

| Requirement | Planned | Implemented | Verified | Evidence |
|-------------|---------|-------------|----------|----------|
| US-007 human CLI ask (SC-001) | ✅ | ✅ | ✅ Pass | ask.test.ts; npm test 11p |
| US-007 machine schema (SC-002) | ✅ Proposed | ✅ `--json` smoke | ❌ Skipped | OQ-10 |
| US-008 Ask &lt;3 clicks (SC-003) | ✅ | ✅ | ✅ Pass (Proposed fixture) | ask_context_dx; package.json |
| US-008 IDE &lt;2s (SC-004) | ✅ gated | ✅ latency log | ❌ Blocked | T039 placeholder |
| Thin clients (SC-005) | ✅ | ✅ | ✅ Pass | CLI + no_client_policy_bypass |
| OQ-10 not frozen (SC-006) | ✅ | ✅ | ✅ Pass | help + machineRenderer labels |
| Live indexed e2e | ✅ | — | ❌ Not Verified | testing brief |
| No JetBrains / no invent APIs | ✅ | ✅ | ✅ | scope review |
| FastAPI changes | ❌ N/A | ✅ none | ✅ | no orchestrator diff |
