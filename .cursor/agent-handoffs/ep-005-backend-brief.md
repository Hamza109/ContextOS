# EP-005 Backend Brief — Orchestrator gap-fill (US-013 + US-014)

**Branch:** `feature/ep-005-privacy-health-consent`  
**Stories:** US-013, US-014 only. **OOS:** US-016 (cite only), JetBrains, L1/L4, L2/L6, EP-004 rebuild, RBAC invent.

## MANDATORY: Graphify first
BEFORE any Read/Grep/Glob of application code:
```
cd /Users/hamzahamal/ContextOS && graphify query "<focused question>" --budget 1500
```
AFTER code changes: `graphify update .` (may need unrestricted permissions). Prefer graph.json via query/explain/path — NOT graph.html dump.

## Authoritative
- `specs/ep-005-privacy-health-consent/{spec,plan,tasks,validation-report}.md`
- `.cursor/agent-handoffs/ep-005-brief.md`
- Constitution III privacy / V clients; api-contract §2.1; ADR-012
- Gap-fill only vs existing IgnorePolicy / health / l5_* / context

## Do NOT
- Invent APIs or Confirmed contracts; freeze OQ-OVERRIDE / OQ-HTTP-Health / OQ-Degraded-Shape
- Ship Confirmed override UX; claim SC-007 Pass (OQ-Uptime-Harness)
- Create quickstart / open-questions / out-of-scope-notes / ui-not-applicable / review-report (review agent owns review-report later)
- Rebuild L5/CLI/EP-004

## Task checklist (backend owns)

### Phase 1–2
- T001 Gap matrix vs plan Gap Analysis (cite only)
- T002 Inventory existing tests to extend
- T003 OOS boundaries noted in execution
- T004 Shared ignore-exclusion fixture under `tests/fixtures/` (gitignore, .env, secrets, node_modules, dist, .git, binary)
- T005–T007 Doc Proposed labels: HTTP/degraded Proposed; SC-007 blocked; no override API

### US-013 tests → gap-fill
- T008 `test_ignore_policy.py` — gitignore + hard exclusions
- T009 packer exclusions / binary skip
- T010 `test_fs_walker.py`
- T011 `test_index_exclusions_qdrant.py` e2e packs+embeddings
- T012 negative: no Confirmed override path
- T015–T017 gap-fill `ignore_policy.py`, `fs_walker.py`, index/pack path if tests fail
- T020 secret-glob inventory — no Confirmed UX
- Client T013/T014/T018/T019: extend boundary tests if feasible in same pass OR leave for light extension/CLI pass — thin clients only

### US-014 tests → gap-fill
- T021 health contract tests — Confirmed fields status/pipeline/falkor/qdrant
- T022 A-07 Falkor unused does not force error
- T023–T025 `test_context_degraded.py` partial failure; HTTP labels Proposed
- T026–T028 gap-fill `health.py`, `l5_search.py`/`context.py`; OpenAPI no Confirmed freeze
- T029 skip SC-007 Pass explicitly

## Gap Analysis targets (plan.md)
| Area | Action |
|------|--------|
| IgnorePolicy / walker / index scoped paths | Harden if SC-001 fails |
| Override | Must NOT ship Confirmed |
| GET / | Contract tests; HTTP codes Proposed |
| Degraded search | Behavioral harden; no Confirmed schema |

## Return to lead
- Files changed
- Tests added/run + Pass/Fail
- Gaps found vs already OK
- Blockers / open OQs untouched
- Confirm Graphify-first + `graphify update .` after code
- Stay on feature branch; leave uncommitted preferred
