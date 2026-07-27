# UI Design — Not Applicable (EP-001)

**Feature:** `ep-001-l5-repository-packing-indexing`  
**Date:** 2026-07-27  
**Decision:** UI/UX design docs under `docs/design/<feature-name>/` are **not required** for EP-001.

## Rationale (from approved plan/tasks)

- Dashboard / Webview / visualization surfaces are **N/A** for EP-001 acceptance.
- User-facing work is limited to VS Code extension **progress notifications**, **cancellation**, and **Proposed** orchestrator base-URL settings — IDE-native UX, not a designed product UI.
- Consent UX/settings schema is **blocked** on **OQ-US016**; EP-001 ships **deny-by-default** behavioral gate only — do **not** invent consent UI.

## Frontend agent

**N/A** for this feature unless a later ADR adds a dashboard/Webview acceptance criterion.

## Extension UX ownership

Progress/cancel and settings live with `vscode-extension-engineer` per `tasks.md` Phase 5–6; no separate design package.
