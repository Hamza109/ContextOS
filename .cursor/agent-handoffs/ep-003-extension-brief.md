# VS Code Extension Brief — EP-003 L3 Symbol & LSP Navigation

You are the ContextOS VS Code Extension Engineer. Implement EP-003 extension DX on REQUIRED branch `feature/ep-003-l3-symbol-lsp-navigation` under `/Users/hamzahamal/ContextOS`. Do NOT push/merge to main. Prefer no commits. Do NOT rewrite specs/plans/tasks.

## MANDATORY Graphify

- BEFORE exploring app/extension code: `graphify query "VS Code extension MCP hover definition Pack Context"`
- AFTER code changes: `graphify update .`

## Read first

- `specs/ep-003-l3-symbol-lsp-navigation/{spec,plan,tasks,validation-report}.md`
- `.cursor/agent-handoffs/ep-003-brief.md` + this brief
- `.specify/memory/constitution.md`
- Lean Spec Kit rule — NO quickstart/open-questions/out-of-scope/ui-not-applicable/docs/design
- ADR-005, ADR-002: extension owns DX only; FastAPI owns orchestration
- Existing `clients/vscode/` EP-001 indexing patterns — extend; never reimplement search/index/symbol policy

## Stories (extension ownership)

| Story | Extension tasks |
|-------|-----------------|
| Setup | T001 (verify), T006 |
| Foundational | T015–T017 |
| US-005 | T028, T032–T033 |
| US-006 | T041, T044 |
| US-009 | T049–T050 (DX/security assert), T052 |
| US-010 | T060, T062–T064, T066 |
| Polish | T070 (IDE error), T072–T073, T076 |

Coordinate with backend modules under `services/orchestrator/app/{adapters/serena_mcp,services/l3_symbol}.py` — call MCP/backend; do not duplicate SymbolService policy.

## Hard constraints (MUST)

1. Thin client only: MCP for FR-04..06; `contextClient` → Confirmed `POST /context` for Pack Context.
2. No local symbol graph, search, index, ignore-policy, or rename-execution sandbox.
3. Do NOT Confirmed-freeze OQs; Proposed command IDs (e.g. `contextos.packContext`).
4. No invented Confirmed REST; no fake Pass for OQ-12 / <2s.
5. Webview optional for Pack Context presentation — if used, sanitize CSP/messages (constitution III).
6. Extend `tests/no_client_policy_bypass.test.ts` for symbol-policy boundary (SC-008).

## Proposed modules

```text
clients/vscode/src/providers/     # hover / refs presentation
clients/vscode/src/commands/      # definition, references, rename-scope, packContext
clients/vscode/src/mcp/           # Serena MCP wiring (DX only)
clients/vscode/src/api/contextClient.ts  # POST /context only
```

Register from `extension.ts`. Reuse `indexClient` patterns for HTTP.

## Tests (vitest)

- `definition_lookup_dx.test.ts`, `find_references_dx.test.ts`, `rename_scope_dx.test.ts`, `pack_context_dx.test.ts`
- Extend `no_client_policy_bypass.test.ts`
- Keep existing indexing tests green

## Out of scope

- Backend Serena adapter / SymbolService implementation (backend-agent)
- `docs/design/**`; frontend dashboard; JetBrains

## Report back

Files changed; tests added/run/pass/fail; boundary evidence; blockers; graphify update done.
