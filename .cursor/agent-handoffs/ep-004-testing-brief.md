# EP-004 Testing Brief

**Agent:** testing-agent  
**Branch:** `feature/ep-004-cli-vscode-surfaces`  
**Date:** 2026-07-28  
**Scope:** US-007 CLI `contextos ask`; US-008 VS Code Ask ContextOS

## Commands run

| Command | Result |
|---------|--------|
| `cd clients/cli && npm test` | **11 passed** / 0 failed (1 file) |
| `cd clients/cli && npm run lint` | **Pass** (`tsc --noEmit`) |
| `cd clients/vscode && npm test` | **37 passed**, **1 skipped**, 0 failed (10 files) |
| Focused: `npx vitest run tests/ask_context_dx.test.ts tests/pack_context_dx.test.ts tests/no_client_policy_bypass.test.ts` | **20 passed** |
| `cd clients/vscode && npm run lint` | **Pass** |
| Manual: `npx tsx src/bin.ts ask 'where is X?' --repo demo --base-url http://127.0.0.1:9` | Visible fail + **exit 1** (NFR-006 smoke) |

## Test vocabulary (Verification Gate)

| Layer | Planned | Implemented | Executed | Passed | Failed | Blocked/Skipped |
|-------|---------|-------------|----------|--------|--------|-----------------|
| CLI unit/boundary (`ask.test.ts`) | T019–T024 | Yes | Yes | **11** | 0 | — |
| VS Code Ask DX (`ask_context_dx`) | T035–T039 | Yes | Yes | **10** | 0 | SC-004 assert intentionally blocked (T039 doc) |
| VS Code boundary (+ Ask) | T037 | Yes | Yes | **7** in file | 0 | — |
| Pack Context regression | T047 | Yes | Yes | **3** | 0 | — |
| Full vscode suite | EP-001/003 + EP-004 | Yes | Yes | **37** | 0 | **1** skipped (observational timing — pre-existing) |
| Live e2e indexed ask | T051 | Partial (mocked) | **Not run** | — | — | **Blocked** A-EP004-3 / no live harness this session |
| SC-002 Confirmed schema Pass | T023 | Flag smoke only | Yes (smoke) | N/A | N/A | **Skipped/Blocked** OQ-10 |
| SC-004 &lt;2s Pass | T039 | Instrumentation only | Yes (doc) | N/A | N/A | **Skipped/Blocked** OQ-IDE-2s-Harness |

## Per-SC status

| SC | Status | Reason / evidence |
|----|--------|-------------------|
| **SC-001** human CLI ask | **Pass** (unit/mock) | `ask.test.ts` T020/T024: mocked `POST /context` → human report contains grounded `final_context` + `relevant_files`. Live indexed e2e **not** executed. |
| **SC-002** machine-readable schema | **Skipped/Blocked** | OQ-10 Proposed only. `--json` wiring + Proposed envelope smoke **Pass as Proposed** (`T023`); **no** Confirmed schema Pass invented. |
| **SC-003** Ask &lt;3 clicks | **Pass** (Proposed fixture) | `ask_context_dx.test.ts`: palette → Ask = 1–2 gestures &lt;3; `package.json` contributes command + keybinding + context menu. OQ-Ask-DX still open (fixture not Confirmed-frozen). |
| **SC-004** IDE &lt;2s | **Skipped/Blocked** | OQ-IDE-2s-Harness. `ASK_LATENCY_LOG_PREFIX` instrumentation OK; T039 explicitly blocks Pass/Fail invent. |
| **SC-005** thin-client boundary | **Pass** | CLI forbidden-pattern scan + Confirmed body keys; vscode `no_client_policy_bypass` Ask files; both call `postContext` only. |
| **SC-006** no OQ-10 freeze | **Pass** | Help/`machineRenderer` label Proposed; tests assert OQ-10 note, not field inventory Pass. |

## Gaps / blockers

1. **OQ-10** — blocks Confirmed SC-002 schema Pass (non-blocking for human ask).
2. **OQ-IDE-2s-Harness** — blocks SC-004 Pass.
3. **Live e2e** against indexed orchestrator — not run (A-EP004-3); mocked coverage only.
4. **OQ-Ask-DX** — SC-003 Pass uses Proposed fixture; UX freeze still open.
5. Minor: `npm run contextos` may mask process exit code; direct `tsx src/bin.ts` correctly exits **1** on failure.

## Ready for PR readiness review?

**Yes — Conditional.** Surface stories (SC-001/003/005/006) evidenced by executed unit tests. Do **not** claim SC-002 schema Pass or SC-004 &lt;2s Pass. Prefer review-report.md next; no push/main.
