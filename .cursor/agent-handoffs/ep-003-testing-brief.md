# Testing Agent Brief — EP-003

Workspace `/Users/hamzahamal/ContextOS`. Branch `feature/ep-003-l3-symbol-lsp-navigation`. Do NOT push/merge. Do NOT invent Pass/Fail for OQ-12 or composed <2s.

## Graphify
- Before explore: `graphify query "EP-003 L3 symbol tests Serena Pack Context"`
- After any test/code fixes: `graphify update .`

## Read
- `specs/ep-003-l3-symbol-lsp-navigation/{spec,plan,tasks,validation-report}.md`
- `.cursor/agent-handoffs/ep-003-brief.md` + latest handoffs in `handoff.md`
- Constitution Verification Gate

## Implementation status (already done)
- Backend: Serena adapter, SymbolService, telemetry, safe-edit enrichment on POST /context
- Extension: MCP DX, hover/commands, Pack Context via contextClient, boundary tests
- UI/UX N/A; Frontend N/A

## Your job
1. Run full backend pytest (unit/integration/contract/eval) and record honest results
2. Run clients/vscode vitest + tsc if needed
3. Confirm SC coverage vs tasks: SC-001/003/004/005/006/007/008/009 as evidenced; SC-002 and <2s **blocked/skipped** only
4. Fill any missing test gaps from tasks.md if clearly absent — do not invent Confirmed schemas
5. Extend/fix only if regressions fail due to EP-003
6. Append ≤40 line handoff; optionally create `ep-003-testing-brief` results notes in handoff only (no new Spec Kit adjuncts)

## Must NOT
- Claim 99% Pass or composed <2s Pass
- Confirmed-freeze OQs
- Create quickstart/open-questions/out-of-scope/ui-not-applicable

## Return
Commands run; pass/fail/skip counts; gaps; AC evidence map; blockers.
