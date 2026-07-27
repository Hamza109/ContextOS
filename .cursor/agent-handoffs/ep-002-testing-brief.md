# Testing Agent Brief — EP-002

You are the ContextOS Testing & Quality Assurance Agent. Validate EP-002 implementation AFTER backend evidence exists.

## Workspace

`/Users/hamzahamal/ContextOS`

**Git branch (REQUIRED):** `feature/ep-002-l5-hybrid-search-phase-packing` — stay on this branch; do NOT push/merge to main.

## MANDATORY Graphify

- BEFORE any Read/Grep/Glob to explore code: `graphify query "..."`
- AFTER any test code changes: `graphify update .`

## Context

Backend agent completed T001–T070. Lead developer marked UI/UX and VS Code extension **N/A**.

Read:

- `specs/ep-002-l5-hybrid-search-phase-packing/{spec,plan,tasks,validation-report,open-questions,quickstart}.md`
- `.specify/memory/constitution.md` (Verification Gate)
- Backend handoff at end of `.cursor/agent-handoffs/handoff.md`
- Existing tests under `services/orchestrator/tests/`

## Stories / acceptance

- US-003 hybrid BM25+vector+MMR via POST /context
- US-004 phase-aware packing (5 phases; Proposed OQ-16)
- US-015 citations file:line + confidence (Proposed OQ-11; no Confirmed JSON freeze)

## MUST honor

1. Do NOT invent Pass/Fail — run pytest and report honestly
2. SC-002 p95 @ 500k: blocked/skipped if fixture missing — document gap
3. SC-003 recall@10: blocked until OQ-recall-harness — do NOT claim Pass
4. Do not Confirmed-freeze OQ-PACK / OQ-11 / OQ-16
5. No scope expansion (Serena, L1, L4 product, L2/L6, CLI, extension DX)
6. Distinguish: Tests planned / implemented / executed / passed / failed / blocked / skipped

## Your job

1. Inventory EP-002 tests vs tasks.md verification matrix (T023–T030, T041–T044, T051–T053, T058–T063, etc.)
2. Execute the test suite (`services/orchestrator` pytest); capture commands + results
3. Confirm EP-001 regression still green
4. Verify SC-001, SC-004, SC-005, SC-006, SC-007 coverage with evidence; keep SC-002/SC-003 gated
5. Security: exclusions / no re-read of secrets paths covered
6. If gaps exist that are implementable without inventing requirements, add missing tests; if blocked by OQ/fixture, document only
7. Append handoff to `.cursor/agent-handoffs/handoff.md` (do not overwrite)

## Handoff format

```markdown
---

## Handoff: testing-agent

Date:

Feature:

Task IDs:

Source Input:

Artifacts Reviewed:

Artifacts Created or Updated:

### What was completed

-

### What failed

-

### Next instructions

-

### Blocking questions

-
```

Include: tests planned/implemented/executed/passed/failed/skipped/blocked; commands; constitution Verification Gate status; readiness for PR review.

## Return summary

1. Test inventory vs tasks
2. Commands run + honest results
3. SC status (met/partial/blocked)
4. Gaps remaining
5. Ready for review-pr-readiness-agent: Yes/No
