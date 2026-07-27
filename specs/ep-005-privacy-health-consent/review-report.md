# Project Governance Review Report

---

## Executive Summary

| Field | Value |
|-------|-------|
| **Feature Name** | EP-005 Privacy Defaults, Health & Consent (`ep-005-privacy-health-consent`) |
| **Review Date** | 2026-07-28 |
| **Reviewer** | review-pr-readiness-agent (ContextOS) |
| **Stories in scope** | US-013, US-014 only (US-016 **OOS**) |
| **Branch** | `feature/ep-005-privacy-health-consent` (uncommitted; no push) |
| **Overall Status** | 🟡 **APPROVED WITH CONCERNS** |
| **Overall Readiness Score** | **8.5 / 10** |
| **PR Readiness Verdict** | **Yes with conditions** (🟡 READY FOR PR WITH COMMENTS) |

### Executive Summary

EP-005 gap-fill for privacy defaults (US-013) and health/degraded search operability (US-014) is implementation- and test-backed: orchestrator IgnorePolicy/walker/health/degrade paths were already largely correct; this epic added acceptance fixtures, contract/negative tests, OpenAPI **Proposed** labels, and client boundary extensions. Testing handoff reports **orch 25 / vscode 8 / CLI 12 / regression 14 all passed**; **SC-001..SC-006, SC-008 Pass**; **SC-007 Skipped** (OQ-Uptime-Harness) by design. Open OQs remain **Proposed** (no Confirmed freeze). UI/UX N/A. **No HIGH blockers** for in-scope PR creation if conditions below are honored (notably: commit before PR; do not claim SC-007/99.5% Pass; carry OQs in PR description; remote CI for this branch not yet evidenced).

---

## Health Dashboard

| Area                    | Status | Score |
| ----------------------- | ------ | ----- |
| Constitution Compliance | 🟢     | 9 / 10 |
| Governance Compliance   | 🟢     | 9 / 10 |
| Requirements            | 🟢     | 9 / 10 |
| Architecture            | 🟢     | 9 / 10 |
| Task Coverage           | 🟡     | 8 / 10 |
| Security                | 🟢     | 9 / 10 |
| Performance             | 🟢     | 8 / 10 |
| Testing                 | 🟡     | 8.5 / 10 |
| Documentation           | 🟢     | 9 / 10 |
| Deployment Readiness    | 🟡     | 7.5 / 10 |
| Code Quality            | 🟢     | 8.5 / 10 |
| PR Readiness            | 🟡     | 8 / 10 |

---

# Constitution Compliance Review

**Status:** 🟢 Compliant (with documented caveats)

**Score:** 9 / 10

**Findings:**

| Principle | Assessment | Evidence |
|-----------|------------|----------|
| **I Evidence-First** | Compliant | Spec cites BRD §10, Appendix C/D, api-contract §2.1, ADR-012; OQs labeled Proposed; no invented Confirmed contracts in `health.py` OpenAPI text |
| **II Six-Layer Integrity** | Compliant | L5 primary (ignore + degrade operability); L1 Falkor report-only (A-07); no L2/L4/L6 product; no client-side orchestration of ignore |
| **III Privacy / Local-First** | Compliant | `IgnorePolicy` hard exclusions + gitignore; OQ-OVERRIDE open; defaults enforced (`test_no_override_api.py`); fixture placeholders only |
| **IV Measurable Intelligence** | Compliant w/ caveat | SC-001..SC-006, SC-008 verified per testing handoff; SC-007 / 99.5% correctly **not** Pass-claimed (OQ-Uptime-Harness) |
| **V Surface Boundary** | Compliant | FastAPI owns policy/health; VS Code + CLI boundary tests extended (SC-003); no DX rebuild |

**Violations:** None identified for in-scope delivery.

**Recommendations:** Keep Proposed labels on HTTP/degrade in PR description; do not market 99.5% until harness exists.

---

# Governance Compliance Review

| Rule ID | Status | Severity | Finding |
| ------- | ------ | -------- | ------- |
| GR-001 (Evidence-First / no invent) | 🟢 | LOW | Pass/Fail only from testing handoff + spot-checked artifacts; OQs not Confirmed-frozen |
| GR-020 (Input / API validation) | 🟢 | LOW | Health Confirmed fields asserted; IndexRequest has no override props (`test_no_override_api.py`) |
| GR-032 (Secrets in repo) | 🟢 | LOW | Fixture uses placeholder secrets only (`ignore_exclusion_repo.py` docstring + contents) |
| GR-042 (E2E / acceptance coverage) | 🟡 | MEDIUM | Acceptance via unit/integration/contract + client boundary; no Extension Host E2E (N/A for this Spec Kit; UI N/A) |
| GR-074 (Traceability) | 🟢 | LOW | FR/SC → plan → tasks → impl/tests mapped; see Traceability Matrix |
| Lean Spec Kit | 🟢 | LOW | Only triad + validation + this review-report; no adjunct Spec Kit files |
| ADR-012 | 🟢 | LOW | Privacy controls Confirmed; RBAC schema not invented |
| api-contract §2.1 | 🟢 | LOW | Confirmed fields present; HTTP codes remain Proposed (OQ-HTTP-Health) |
| Constitution Verification Gate (SC-007) | 🟢 | LOW | SC-007 Skipped with reason — correct gate behavior |

## Governance Summary

| Metric | Value |
|--------|-------|
| Total Rules Evaluated | 9 |
| Passed | 8 |
| Warnings | 1 (GR-042 — no IDE E2E; acceptable for API/privacy epic) |
| Failures | 0 |
| Governance Compliance Score | **9 / 10** |

---

# Requirements Review

**Status:** 🟢 Good

**Score:** 9 / 10

**Strengths:**

- FR-001..FR-011 complete; US-016 explicitly OOS (FR-011).
- SC-001..SC-008 measurable with SC-007 correctly blocked on harness.
- Proposed vs Confirmed labeling consistent across spec/plan/tasks/code/tests.

**Concerns:**

- `spec.md` Status still `Draft` (non-blocking for PR if PM accepts Conditional Approval chain).
- Backlog US-016 epic-field inconsistency noted in validation-report (external).

**Recommendations:** Promote spec Status when PM confirms; keep OQs in PR body.

---

# Architecture Review

**Status:** 🟢 Good

**Score:** 9 / 10

**Strengths:**

- Gap-fill only — reuses `IgnorePolicy`, `walk_allowed_files`, `health.py`, L5 pack/index/search (EP-001/002 cite).
- Single ignore engine in orchestrator; clients thin (constitution V).
- OpenAPI documents Proposed HTTP / degrade without freezing contracts.

**Concerns:**

- Health currently returns HTTP 200 for degraded Qdrant cases (body `status=degraded`) — aligned with **Proposed** mapping but not Confirmed `503` emission (documented in OpenAPI as not currently emitted by default).

**Recommendations:** Resolve OQ-HTTP-Health / OQ-Degraded-Shape in a follow-up before treating status codes as Confirmed.

---

# Task Coverage Review

**Status:** 🟡 Acceptable

**Score:** 8 / 10

**Coverage Percentage:** ~100% of T001–T036 **intent** covered per backend + testing handoffs; `tasks.md` checkboxes remain unchecked (documentation lag).

**Findings:**

- Backend handoff: T001–T029 gap-fill + acceptance; core impl already OK.
- Testing handoff: T030–T036; T032/T033 Pass; SC matrix executed.
- **Gap:** `tasks.md` still shows `[ ]` for all tasks — Missing Evidence that task list was formally closed in-file (handoffs substitute).

**Recommendations:** Optionally mark tasks complete in `tasks.md` before merge (non-blocking if PR cites handoffs).

---

# Security Review

**Status:** 🟢 Good

**Score:** 9 / 10

**Findings:**

| Topic | Evidence |
|-------|----------|
| Ignore / hard exclusions | `ignore_policy.py` HARD_EXCLUDE_* + SECRET_FILE_GLOBS; OQ-OVERRIDE docstring |
| No override API | `test_no_override_api.py` OpenAPI + IndexRequest + IgnorePolicy attrs |
| Client no-bypass | Extended `no_client_policy_bypass.test.ts` (8 passed); CLI ask boundary (12 passed) |
| Secrets in fixtures | Placeholders only (`API_KEY=fixture-not-real`) |
| Auth on GET / | OQ-Health-Auth open; A-05 loopback OK for POC |
| RBAC | ADR-012 Missing Evidence — not invented |
| US-016 consent | OOS — not implemented in this epic |

**Violations:** None for in-scope controls.

**Applicable Governance Rules:** GR-032, constitution III/V, ADR-012.

**Recommendations:** Keep override product blocked until OQ-OVERRIDE; do not invent RBAC.

---

# Performance Review

**Status:** 🟢 Acceptable (cite-only)

**Score:** 8 / 10

**Findings:**

- No new latency SLAs in EP-005; search p95 / index SLAs remain EP-001/002 ownership.
- Degrade path prefers partial discovery over total outage (behavioral; SC-006 Pass per testing).
- SC-007 99.5% uptime **not** verified — harness Missing Evidence.

**Recommendations:** Do not claim indexer uptime % in release notes until OQ-Uptime-Harness.

---

# Testing Review

**Status:** 🟡 Good with conditions

**Score:** 8.5 / 10

### Coverage Summary

| Test Type         | Status |
| ----------------- | ------ |
| Unit Tests        | 🟢 Pass (reported) — ignore_policy, fs_walker, packer, no_override |
| Integration Tests | 🟢 Pass (reported) — index exclusions Qdrant, context degraded |
| Contract Tests    | 🟢 Pass (reported) — `test_health_contract.py` present |
| Client boundary   | 🟢 Pass (reported) — vscode 8, CLI 12 |
| Regression        | 🟢 Pass (reported) — 14 tests |
| E2E (IDE Host)    | ⚪ N/A — UI/UX N/A; not in Spec Kit |
| Acceptance (SC)   | 🟢 SC-001..006, SC-008 Pass; SC-007 Skipped |

### SC Matrix (from testing-agent handoff — not re-executed in this review)

| SC | Result | Evidence (cited) |
|----|--------|------------------|
| SC-001 | **Pass** | Shared fixture packs + embeddings exclusions |
| SC-002 | **Pass** | No override API / OQ-OVERRIDE open |
| SC-003 | **Pass** | vscode 8 + CLI boundary |
| SC-004 | **Pass** | GET / Confirmed fields (`test_health_contract.py`) |
| SC-005 | **Pass** | A-07 Falkor unused ≠ error |
| SC-006 | **Pass** | Degraded POST /context + BM25 path |
| SC-007 | **Skipped** | **OQ-Uptime-Harness** — no 99.5% Pass |
| SC-008 | **Pass** | HTTP/degraded asserts labeled **Proposed** |

### Counts (testing-agent)

| Suite | Result |
|-------|--------|
| Orchestrator EP-005 | 25 passed |
| VS Code bypass | 8 passed |
| CLI ask | 12 passed |
| Regression | 14 passed |
| Failed | 0 |
| Skipped | SC-007 only |

**T032 / T033:** Pass per testing handoff (privacy checklist; scope audit — no US-016 product / RBAC invent / rebuilds).

**Findings:**

- This review **did not re-run** pytest/vitest; evidence is the testing-agent handoff + spot-check of test files and Graphify links (`materialize_ignore_exclusion_repo` → packer/walker/index tests).
- Remote GitHub Actions run for **this branch** = **Missing Evidence** (workflow file exists as untracked `.github/workflows/ci.yml`; no PR CI result reviewed).

**Missing Coverage:** SC-007 Pass (intentional); Confirmed HTTP/degrade schema (OQs); auth on GET /.

**Recommendations:** After commit/push, rely on CI workflow for orchestrator + vscode jobs; keep SC-007 skip visible in PR.

---

# Documentation Review

**Status:** 🟢 Good

**Score:** 9 / 10

**Findings:**

- Lean Spec Kit complete: `spec.md`, `plan.md`, `tasks.md`, `validation-report.md`, this `review-report.md`.
- No forbidden adjuncts (quickstart / open-questions / out-of-scope-notes / ui-not-applicable).
- OpenAPI health description documents Proposed labels (OQ-HTTP-Health, OQ-Degraded-Shape, OQ-Uptime-Harness).
- Feature briefs under `.cursor/agent-handoffs/ep-005-*.md`.

**Recommendations:** Update `tasks.md` checkboxes; optionally set spec Status from Draft.

---

# Deployment Readiness Review

**Status:** 🟡 Acceptable for local POC

**Score:** 7.5 / 10

**Findings:**

- Local POC: Compose/Qdrant as today; Falkor may be absent (A-07) — T035 intent.
- CI workflow present (untracked) for orchestrator pytest + vscode vitest on PR/push.
- Auth on GET / open (OQ-Health-Auth); A-05 non-blocking.
- Rollback: standard git revert — no special migration (no data model changes).
- **Missing Evidence:** Successful CI green on this feature branch remote; production deploy plan N/A for POC.

**Recommendations:** Commit `.github/workflows/ci.yml` with the feature if intended; verify CI on PR.

---

# Code Quality Review

**Status:** 🟢 Good (spot-checked)

**Score:** 8.5 / 10

**Implementation files reviewed (Graphify-first, then spot-check):**

| Path | Role |
|------|------|
| `services/orchestrator/app/api/health.py` | GET / Confirmed fields + Proposed OpenAPI |
| `services/orchestrator/app/security/ignore_policy.py` | Defaults + OQ-OVERRIDE docstring |
| `services/orchestrator/tests/fixtures/ignore_exclusion_repo.py` | SC-001 shared fixture |
| `services/orchestrator/tests/contract/test_health_contract.py` | SC-004/005 + SC-007 skip doc |
| `services/orchestrator/tests/unit/test_no_override_api.py` | SC-002 |
| Diffs (stat): health, ignore_policy, degraded/exclusions/packer/walker tests, client boundary tests | Gap-fill + acceptance |

**Findings:**

- Small, focused diffs (~632 insertions across modified tracked files + new tests/fixtures).
- Proposed vs Confirmed discipline visible in code comments and OpenAPI.
- No Confirmed override surface; Graphify shows `IgnorePolicy` connected to walker/pack/index paths.

**Code Smells:** None material in spot-check.

**Recommendations:** None blocking.

---

# Traceability Matrix

| Requirement | Plan Coverage | Task Coverage | Implementation Coverage | Status |
| ----------- | ------------- | ------------- | ----------------------- | ------ |
| FR-001 | 🟢 Gap-fill IgnorePolicy/walker | T008, T010, T015–T016 | `ignore_policy.py`, `fs_walker.py` + tests | 🟢 |
| FR-002 | 🟢 Hard exclusions | T008–T011, T015–T017, T020 | HARD_EXCLUDE_* + fixture e2e | 🟢 |
| FR-003 | 🟢 No override | T007, T012, T020 | `test_no_override_api.py`; OQ-OVERRIDE open | 🟢 |
| FR-004 | 🟢 Client boundary | T013–T014, T018–T019 | vscode + CLI boundary tests | 🟢 |
| FR-005 | 🟢 Cite EP-001 index | T011, T017 | Index + pack apply policy (verified via exclusions tests) | 🟢 |
| FR-006 | 🟢 GET / fields | T021, T026 | `health.py` + contract tests | 🟢 |
| FR-007 | 🟢 A-07 Falkor | T022, T026 | `falkor: unused`; SC-005 Pass | 🟢 |
| FR-008 | 🟢 Proposed HTTP | T005, T024, T028 | OpenAPI + test comments | 🟢 |
| FR-009 | 🟢 Degrade operability | T023, T025, T027 | `test_context_degraded.py`; SC-006 Pass | 🟢 |
| FR-010 | 🟢 Shape Proposed | T005, T023–T025 | OQ-Degraded-Shape labels | 🟢 |
| FR-011 | 🟢 OOS audit | T003, T033 | US-016 not shipped; T033 Pass | 🟢 |
| SC-001 | 🟢 | T004, T008–T011 | Fixture e2e | 🟢 Verified* |
| SC-002 | 🟢 | T012 | No override | 🟢 Verified* |
| SC-003 | 🟢 | T013–T014 | Client tests | 🟢 Verified* |
| SC-004 | 🟢 | T021 | Health contract | 🟢 Verified* |
| SC-005 | 🟢 | T022 | A-07 | 🟢 Verified* |
| SC-006 | 🟢 | T023–T025 | Degraded context | 🟢 Verified* |
| SC-007 | 🟢 Blocked Pass | T006, T029 | Explicit skip | 🟡 Skipped (by design) |
| SC-008 | 🟢 Proposed labels | T024, T028 | Tests + OpenAPI | 🟢 Verified* |

\*Verified = testing-agent execution evidence cited; this review spot-checked artifacts, did not re-execute suites.

---

# Risk Assessment

## 🔴 High Risks

No High Risks Found for in-scope US-013/US-014 PR **provided** SC-007 is not Pass-claimed and OQs stay Proposed.

---

## 🟡 Medium Risks

1. **Remote CI not yet evidenced** for this branch (workflow untracked; no PR Actions result reviewed).
2. **Uncommitted working tree** — PR cannot ship until commit (and push if creating remote PR).
3. **OQ-HTTP-Health / OQ-Degraded-Shape** — risk of reviewers treating Proposed codes/fields as Confirmed.
4. **`tasks.md` checkboxes unchecked** — audit trail lag vs handoffs.
5. **Gitignore negation edge cases** — plan Risks; mitigated if SC-001 Pass holds on fixture set (not a full git engine).

---

## 🟢 Low Risks

1. Spec Status still Draft.
2. Backlog US-016 epic-field inconsistency (external).
3. UI/UX N/A — correctly out of Spec Kit.
4. Auth on GET / open (A-05 POC).

---

# Action Items

## 🔴 Must Fix Before PR

No Blocking Issues Found for **in-scope** acceptance **if** the following process conditions are met at PR creation time:

1. **Commit** (user-requested) relevant EP-005 changes on `feature/ep-005-privacy-health-consent` before opening PR — currently uncommitted.
2. **Do not claim SC-007 / 99.5% Pass** in PR summary or release notes.
3. **Do not Confirmed-freeze** OQ-OVERRIDE, OQ-HTTP-Health, OQ-Degraded-Shape, OQ-Uptime-Harness.

*(If those conditions are violated, treat as 🔴 blockers.)*

---

## 🟡 Recommended Improvements

1. Mark T001–T036 complete in `tasks.md` or cite handoffs in PR.
2. Include `.github/workflows/ci.yml` in the PR if CI is intended for this branch.
3. PR description: SC matrix + open OQs + US-016 OOS.
4. After push, confirm GitHub Actions green.
5. PM: promote `spec.md` Status; align backlog US-016 epic field.

---

## 🟢 Future Enhancements

1. Resolve OQ-Uptime-Harness → enable SC-007 measurement.
2. Product-confirm HTTP status mapping (OQ-HTTP-Health) and degrade schema (OQ-Degraded-Shape).
3. Separate Spec Kit for US-016 consent when scheduled.
4. OQ-OVERRIDE product design if Security requires approved include path.

---

# Pull Request Readiness Assessment

## PR Readiness Status

🟡 **READY FOR PR WITH COMMENTS**

**Plain verdict:** **Yes with conditions**

---

## PR Gate Checklist

| Check                       | Status |
| --------------------------- | ------ |
| Constitution Compliant      | 🟢 Yes |
| Governance Rules Compliant  | 🟢 Yes (1 MEDIUM warning GR-042 E2E N/A) |
| Requirements Covered        | 🟢 Yes (in-scope FRs) |
| Acceptance Criteria Covered | 🟡 SC-001..006, SC-008 Yes; SC-007 Skipped |
| Architecture Approved       | 🟢 Gap-fill approved (validation Conditional → impl) |
| Tasks Completed             | 🟡 Done per handoffs; tasks.md boxes open |
| Unit Tests Passing          | 🟢 Reported Pass (testing-agent) |
| Integration Tests Passing   | 🟢 Reported Pass |
| E2E Tests Passing           | ⚪ N/A (UI N/A) |
| Security Review Completed   | 🟢 This report |
| Documentation Updated       | 🟢 Spec Kit + OpenAPI Proposed labels |
| No High Risks Remaining     | 🟢 Yes (under conditions) |
| CI/CD Checks Passing        | 🟡 Local suites Pass; **remote CI Missing Evidence** |
| Deployment Ready            | 🟡 Local POC Yes |

---

## Blocking Issues

No Blocking Issues Found for in-scope US-013/US-014 **when PR conditions are honored**.

---

## PR Recommendation

**Ready with Comments** because:

- Implementation + acceptance evidence exist for privacy defaults, health Confirmed fields, A-07, degraded search behavior, and client no-bypass (SC-001..SC-006, SC-008).
- Constitution III/V and ADR-012 privacy controls aligned; GR-032 satisfied (fixture placeholders).
- SC-007 correctly gated (constitution IV / Verification Gate) — **not** a delivery blocker if labeled Skipped.
- Conditions: commit uncommitted work; carry open OQs; no Confirmed freeze; no 99.5% Pass claim; expect remote CI after push.

Not **Ready Yes (unconditional)** due to uncommitted tree, SC-007 open harness, Proposed HTTP/degrade contracts, and missing remote CI evidence.

Not **No** — no HIGH governance/security/acceptance failures for in-scope stories.

---

# Final Verdict

| Field | Value |
|-------|-------|
| Approval Status | 🟡 **APPROVED WITH CONCERNS** |
| PR Decision | 🟡 **READY FOR PR WITH COMMENTS** |
| **PR Ready?** | **Yes with conditions** |
| Overall Readiness Score | **8.5 / 10** |

### Issue Summary

| Severity | Count |
|----------|-------|
| High Risks | 0 |
| Medium Risks | 5 |
| Low Risks | 4 |
| Governance Violations | 0 |
| Constitution Violations | 0 |

### Conditions / Blockers

**Conditions (must honor):**

1. Commit before PR; stay on `feature/ep-005-privacy-health-consent`; no merge to main without review.
2. SC-007 remains **Skipped** — no 99.5% Pass claim (OQ-Uptime-Harness).
3. Open OQs stay **Proposed**: OVERRIDE, HTTP-Health, Degraded-Shape, Uptime-Harness (+ Health-Auth / OQ-01 non-blocking).
4. US-016 remains OOS.
5. Call out remote CI verification after push.

**Blockers:** None for in-scope PR under those conditions.

### Open OQs (Proposed)

| ID | Blocks |
|----|--------|
| **OQ-OVERRIDE** | Confirmed override product |
| **OQ-HTTP-Health** | Confirmed GET / status-code freeze |
| **OQ-Degraded-Shape** | Confirmed degrade schema/UX freeze |
| **OQ-Uptime-Harness** | SC-007 / 99.5% Pass claims |
| OQ-Health-Auth | Auth on GET / (POC non-blocking) |
| OQ-01 | RBAC schema (not invented here) |

### Final Summary

EP-005 (US-013/US-014) is **approved with concerns** and **PR-ready with conditions**. Privacy defaults and health/degrade operability are backed by local test evidence (25/8/12/14 passed; SC-001..006 & SC-008 Pass; SC-007 Skipped). Ship the PR after commit, with OQs and SC-007 skip explicit in the description; do not Confirmed-freeze open contracts or claim indexer uptime %.

---

## Evidence Reviewed

| Artifact | Role |
|----------|------|
| `.cursor/agent-handoffs/ep-005-review-brief.md` | Review mandate |
| `.cursor/agent-handoffs/ep-005-brief.md`, `ep-005-testing-brief.md`, `ep-005-backend-brief.md` | Scope / evidence cites |
| `.cursor/agent-handoffs/handoff.md` (latest backend + testing blocks) | Execution evidence |
| `specs/ep-005-privacy-health-consent/{spec,plan,tasks,validation-report}.md` | Spec Kit triad + planning gate |
| `.specify/memory/constitution.md` | Principles I–V |
| `docs/architecture/api-contract.md` §2.1 | Confirmed health fields; Proposed status codes |
| `docs/architecture/architecture-decisions.md` ADR-012 | Privacy Confirmed; RBAC open |
| Graphify queries/explain (`IgnorePolicy`, `health()`, fixture, tests) | Pre-Read codebase map |
| Spot-check: `health.py`, `ignore_policy.py`, `test_health_contract.py`, `test_no_override_api.py`, `ignore_exclusion_repo.py`, degraded test headers | Impl/test evidence |
| `git status` / `git diff --stat` / branch tip | Uncommitted feature branch state |
| `.github/workflows/ci.yml` (untracked) | CI definition present; remote run Missing Evidence |

## Missing Evidence

| Item | Impact |
|------|--------|
| Re-execution of pytest/vitest in this review session | Relies on testing-agent counts |
| Remote GitHub Actions green for this branch | Medium — verify after push |
| SC-007 / 99.5% measurement harness | Intentional skip |
| Confirmed HTTP / degrade schema | Open OQs |
| Confirmed override UX | OQ-OVERRIDE |
| `tasks.md` checkbox closure | Documentation lag |
| Committed tree | Must commit before PR |

## Planned vs Implemented vs Verified

| Requirement | Planned | Implemented | Verified | Evidence |
| ----------- | ------- | ----------- | -------- | -------- |
| FR-001..FR-002 ignore/exclusions | ✅ | ✅ | ✅* | Fixture + unit/integration tests; testing Pass |
| FR-003 no Confirmed override | ✅ | ✅ | ✅* | `test_no_override_api.py` |
| FR-004 client no-bypass | ✅ | ✅ | ✅* | vscode 8 / CLI 12 |
| FR-005 index path cite EP-001 | ✅ | ✅ (pre-existing + accept) | ✅* | exclusions Qdrant tests |
| FR-006..FR-007 health + A-07 | ✅ | ✅ | ✅* | `health.py` + contract tests |
| FR-008 / FR-010 Proposed labels | ✅ | ✅ | ✅* | OpenAPI + test comments; SC-008 |
| FR-009 degrade | ✅ | ✅ (pre-existing + extend) | ✅* | `test_context_degraded.py`; SC-006 |
| FR-011 OOS | ✅ | ✅ (audit) | ✅* | T033 Pass |
| SC-007 99.5% | ✅ (blocked) | ⚪ N/A | 🟡 Skipped | OQ-Uptime-Harness |

\*Verified via testing-agent handoff + artifact spot-check (not re-run here).
