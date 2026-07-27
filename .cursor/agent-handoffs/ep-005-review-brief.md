# EP-005 Review Brief — PR readiness

**Branch:** `feature/ep-005-privacy-health-consent`  
**After:** backend + testing handoffs complete; UI/UX N/A; clients boundary done in backend pass

## MANDATORY: Graphify first
BEFORE any Read/Grep/Glob of application code:
```
cd /Users/hamzahamal/ContextOS && graphify query "<focused question>" --budget 1500
```
Prefer graph.json via query/explain/path — NOT graph.html.

## Produce ONLY
`specs/ep-005-privacy-health-consent/review-report.md`

Do NOT create quickstart / open-questions / out-of-scope-notes / ui-not-applicable.

## Evidence cites
- Testing: SC-001..SC-006, SC-008 Pass; SC-007 Skipped (OQ-Uptime-Harness)
- Orch 25 / VS Code 8 / CLI 12 / regression 14 — all passed
- Backend: gap-fill acceptance; core IgnorePolicy/health/degrade already OK
- UI/UX: N/A
- Open OQs Proposed: OVERRIDE, HTTP-Health, Degraded-Shape, Uptime-Harness
- US-016 OOS

## Constraints
- No invent Pass/Fail; no Confirmed freeze of open OQs
- Stay on feature branch; leave uncommitted; no push/main
- Append ≤40 line handoff when done

## Return
- review-report path + verdict (PR ready Yes/No with conditions)
- Gaps / OQs
- Branch status
