<!-- Deprecated: do not extend. UI N/A belongs in handoffs only (lean Spec Kit). -->
# UI Design — Not Applicable

## EP-001 — L5 Repository Packing & Indexing

**Feature:** `ep-001-l5-repository-packing-indexing`  
**Date:** 2026-07-27  
**Decision:** UI/UX design docs under `docs/design/<feature-name>/` are **not required** for EP-001.

### Rationale (from approved plan/tasks)

- Dashboard / Webview / visualization surfaces are **N/A** for EP-001 acceptance.
- User-facing work is limited to VS Code extension **progress notifications**, **cancellation**, and **Proposed** orchestrator base-URL settings — IDE-native UX, not a designed product UI.
- Consent UX/settings schema is **blocked** on **OQ-US016**; EP-001 ships **deny-by-default** behavioral gate only — do **not** invent consent UI.

### Frontend agent

**N/A** for this feature unless a later ADR adds a dashboard/Webview acceptance criterion.

### Extension UX ownership

Progress/cancel and settings live with `vscode-extension-engineer` per `tasks.md` Phase 5–6; no separate design package.

---

## EP-002 — L5 Hybrid Search & Phase-Aware Packing

**Feature:** `ep-002-l5-hybrid-search-phase-packing`  
**Date:** 2026-07-27  
**Decision:** UI/UX design docs under `docs/design/ep-002-l5-hybrid-search-phase-packing/` are **not required**.

### Rationale (from approved plan/tasks)

- EP-002 delivery is **FastAPI `POST /context`** (hybrid BM25+vector+MMR, phase-aware packing, citation attributes).
- Dashboard / Webview / browser frontend surfaces are **out of scope** (no frontend tasks in `tasks.md`).
- VS Code extension Ask / Pack Context UX is **out of scope** (FR-019 consumer note only; T068/T069).
- No user-facing product UI requires wireframes or a design package.

### Frontend agent

**N/A** for EP-002.

### Extension agent

**N/A** for EP-002 DX beyond documenting that future clients SHOULD call `POST /context`.
