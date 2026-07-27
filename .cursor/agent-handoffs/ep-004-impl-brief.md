# EP-004 Implementation Brief (Lead)

**Branch:** `feature/ep-004-cli-vscode-surfaces`  
**Stories:** US-007 CLI ask, US-008 VS Code Ask  
**UI/UX:** N/A for new dashboard — extension command DX only

## Task checklist (T001–T055)

| Track | Tasks | Owner |
|-------|-------|-------|
| Setup/Foundation | T001–T015 | Lead (inventory done via plan) |
| CLI US-007 | T016–T031 | Lead (scaffold `clients/cli/`) |
| VS Code US-008 | T032–T047 | vscode-extension-engineer |
| Polish | T048–T055 | Lead + testing + review |
| Testing | T019–T024, T035–T039, T051 | testing-agent after impl |
| Review | review-report.md | review-pr-readiness-agent |

## Decisions (Proposed vs Confirmed)

| Item | Status |
|------|--------|
| POST /context consume | Confirmed |
| CLI home `clients/cli/` TypeScript+vitest | Proposed (OQ-CLI-Packaging) |
| Human output layout | Proposed (OQ-CLI-Human-Format) |
| `--json` machine mode | Proposed only (OQ-10) — no schema freeze |
| Ask ID `contextos.askContext` | Proposed |
| Ask gesture: palette + InputBox | Proposed (OQ-Ask-DX); &lt;3 clicks |
| SC-004 Pass | Blocked (OQ-IDE-2s-Harness) |
| Orchestrator changes | None required |

## Do not create

quickstart / open-questions / out-of-scope-notes / docs/design/ui-not-applicable.md / docs/design/ep-004-*
