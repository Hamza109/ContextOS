# EP-004 Brief — CLI & VS Code Developer Surfaces

**Branch:** `feature/ep-004-cli-vscode-surfaces` (off main @ bf1e6c8)  
**Feature folder:** `specs/ep-004-cli-vscode-surfaces/`  
**Stories:** US-007, US-008 only  
**Business:** BO-01, BO-04; MVP exit (IDE Ask &lt;3 clicks; CLI ask)

## Mandatory cites (do not re-spec)

| Source | What to use |
|--------|-------------|
| `docs/backlog/user-stories.md` | EP-004, US-007, US-008, OQ-10, A-02, A-05 |
| `docs/BRD_Context_OS.md` | §5 CLI deliverable; §10 IDE &lt;3 clicks; §15 MVP exit |
| `docs/architecture/api-contract.md` | §2.3 POST /context; §6 CLI mapping |
| ADR-007 | VS Code + CLI MVP; JetBrains later |
| ADR-001 / constitution V | FastAPI owns orchestration; clients thin |
| EP-002 specs | Hybrid search + phase packing + POST /context |
| EP-003 specs | Symbol/pack DX; Pack Context already uses contextClient |
| EP-001 | Privacy/indexing defaults — cite only |

## Existing code (cite, don’t rebuild)

- `clients/vscode/` — extension; `api/contextClient.ts` POST /context; Pack Context command exists
- **No CLI package yet** under `clients/` — discovery for plan/tasks
- `services/orchestrator/app/api/context.py` — POST /context owner

## Hard constraints

- OQ-10 machine-readable CLI schema: **Proposed only** — do not Confirmed-freeze
- Reuse POST /context; do not rebuild L5/L3
- No JetBrains, L1 blast, L4 product, L2/L6, EP-005 full privacy epic
- Extension must not reimplement pack/search/symbol policy
- Lean Spec Kit ONLY: spec.md, plan.md, tasks.md, validation-report.md
- No quickstart / open-questions / out-of-scope-notes / ui-not-applicable files
- Label Proposed vs Confirmed; no invented Pass/Fail

## Workflow

1. spec-writer → spec.md  
2. plan-generator → plan.md  
3. task-generator → tasks.md  
4. test-validation-agent → validation-report.md  
Next after validation: lead-developer-agent (not this PM run)
