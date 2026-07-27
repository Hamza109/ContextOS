# EP-005 Testing Brief

**Branch:** `feature/ep-005-privacy-health-consent`  
**After:** backend-agent gap-fill (US-013/US-014 acceptance harden)

## MANDATORY: Graphify first
BEFORE any Read/Grep/Glob of application code:
```
cd /Users/hamzahamal/ContextOS && graphify query "<focused question>" --budget 1500
```
Prefer graph.json via query/explain/path — NOT graph.html.

## Scope
Validate SC-001..SC-006, SC-008 evidence. **SC-007 = Skipped** with reason **OQ-Uptime-Harness** (do NOT Pass-claim 99.5%).

US-016 OOS — cite only. No Confirmed freeze of OQ-OVERRIDE / OQ-HTTP-Health / OQ-Degraded-Shape.

## Backend reported (verify, do not invent)
- Orchestrator EP-005 suite: 24 passed
- VS Code no_client_policy_bypass: 8 passed
- CLI ask.test: 12 passed
- Regression hybrid+ignore+index: 9 passed
- Core logic already OK; fixture+tests+OpenAPI Proposed labels added

## Tasks
T030–T036 polish/regression/smoke + map evidence to SCs. Confirm privacy checklist T032; scope audit T033.

## Do NOT
- Create quickstart/open-questions/out-of-scope-notes/ui-not-applicable
- Write review-report.md (review agent owns that)
- Claim SC-007 Pass

## Return
- Tests planned / implemented / executed / passed / failed / skipped (+ reasons)
- SC-001..SC-008 matrix
- Commands + evidence
- Blockers
- Append ≤40 line handoff
