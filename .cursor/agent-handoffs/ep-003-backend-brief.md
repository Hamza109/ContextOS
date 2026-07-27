# Backend Agent Brief — EP-003 L3 Symbol & LSP Navigation

You are the ContextOS Backend Engineering Agent. Implement EP-003 backend on REQUIRED branch `feature/ep-003-l3-symbol-lsp-navigation` under `/Users/hamzahamal/ContextOS`. Do NOT push/merge to main. Prefer no commits unless needed. Do NOT rewrite specs/plans/tasks.

## MANDATORY Graphify

- BEFORE any Read/Grep/Glob to explore app code: `graphify query "Serena MCP symbol definition references rename"`
- AFTER code changes: `graphify update .`

## Read first

- `specs/ep-003-l3-symbol-lsp-navigation/{spec,plan,tasks,validation-report}.md`
- `.cursor/agent-handoffs/ep-003-brief.md` + this brief
- `.specify/memory/constitution.md`
- `.cursor/rules/lean-spec-kit-artifacts.mdc` — NO quickstart/open-questions/out-of-scope/ui-not-applicable files
- `docs/architecture/` ADR-005, api-contract §3 Symbol REST NEEDS CLARIFICATION, Appendix D Confirmed only
- Existing `services/orchestrator/` — extend EP-001/002; do not duplicate L5 search/index

## Stories (backend ownership)

| Story | Backend tasks |
|-------|---------------|
| Setup | T001–T005, T007–T009 (API/L3) |
| Foundational | T010–T014, T018–T021 |
| US-005 | T022–T027, T029–T031, T034–T035 |
| US-006 | T036–T040, T042–T043, T045 |
| US-009 | T046–T048, T050–T051, T053 |
| US-010 | T054–T059, T061–T062, T065, T067–T069 |
| Polish | T070–T075, T077–T082 (backend) |

**Skip:** VS Code tasks (T006, T015–T017, T028, T032–T033, T041, T044, T049, T052, T060, T063–T064, T066, T076) — extension engineer.

## Hard constraints (MUST)

1. Do NOT Confirmed-freeze OQ-12, OQ-Symbol-REST, OQ-Safe-Edit-Shape, OQ-Lang-Set, OQ-11 — **Proposed only**.
2. Do NOT claim 99% Pass or composed <2s Pass — document gaps; OQ-12 placeholder blocked/skipped.
3. No L1 blast, L4 product, L2/L6, full CLI beyond US-010 needs; no rename **execution** sandbox.
4. FastAPI owns orchestration; no Confirmed symbol REST for MVP (MCP-first Option A). OpenAPI must not invent Appendix D L3 endpoints.
5. No invented requirements/APIs/fake Pass-Fail.
6. Lean: no adjunct Spec Kit files.

## Proposed modules (create)

```text
services/orchestrator/app/adapters/serena_mcp.py
services/orchestrator/app/services/l3_symbol.py
services/orchestrator/app/telemetry/symbol.py
```

Config: Proposed Serena MCP knobs in `config.py` (not Confirmed freeze).

## Transport

- IDE FR-04..06: MCP-first (extension). Orchestrator MAY call Serena for Pack Context enrichment.
- Symbol proxy REST: deferred — do not add Confirmed router under `app/api/`.

## Safe edit plan (US-010)

- Proposed interim (structured text / delimited block in/alongside `final_context`) — behavioral discriminator vs “rewrite entire file”.
- Must not break Confirmed `POST /context` fields; do not invent Confirmed Appendix D response fields.
- Citations: assert file:line + confidence attributes only (OQ-11 open).

## Tests (pytest)

Unit/integration/contract paths named in tasks.md. Write tests; use Serena test doubles where live MCP unavailable. OQ-12 accuracy harness: blocked placeholder documenting Missing Evidence — never invent Pass.

## Out of scope for you

- `clients/vscode/**` implementation
- `docs/design/**`
- JetBrains; Confirmed symbol REST invention

## Report back

Files changed; tests added/run/pass/fail/skip; OQ gaps; blockers; graphify update done.
