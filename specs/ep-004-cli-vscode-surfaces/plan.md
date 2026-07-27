# Implementation Plan: EP-004 CLI & VS Code Developer Surfaces

**Branch**: `feature/ep-004-cli-vscode-surfaces` | **Date**: 2026-07-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/ep-004-cli-vscode-surfaces/spec.md`

**Stories**: US-007, US-008 only

---

## Summary

EP-004 delivers MVP **developer surfaces**: scriptable **`contextos ask`** (US-007 / BO-04) and VS Code **Ask ContextOS** initiation in **&lt;3 clicks** (US-008 / BO-01; BRD §10 / §15). Both are **thin clients** of Confirmed **`POST /context`** (api-contract §2.3 / §6). **FastAPI owns** hybrid search, phase packing, and symbol enrichment (cite EP-002 / EP-003 — **do not re-plan**). CLI/extension own DX, rendering, and failure surfacing only (constitution V; architecture-overview §2.3).

**Approach**: Scaffold **Proposed** `clients/cli/` (`contextos ask` → HTTP `POST /context`); add VS Code Ask command reusing `clients/vscode/src/api/contextClient.ts` + Pack Context patterns. Machine-readable CLI schema remains **OQ-10 Proposed only** — no Confirmed freeze.

---

## Technical Context

| Field | Value | Status |
|-------|-------|--------|
| Language/Version | TypeScript (extension — Confirmed); CLI language/runtime | Extension Confirmed; CLI toolchain **Proposed** (discovery) |
| Primary Dependencies | FastAPI `POST /context`; existing `contextClient.ts`; VS Code `^1.85` | Confirmed consume |
| Storage | N/A new stores — clients call orchestrator | Confirmed |
| Testing | vitest under `clients/vscode/tests/`; CLI tests | Extension pattern Confirmed; CLI layout **Proposed** |
| Target Platform | Local/VPC loopback API (A-05); VS Code workspace; terminal | Confirmed posture |
| Project Type | Client surfaces (CLI + VS Code) over existing orchestrator | Confirmed |
| Performance Goals | IDE Ask &lt;2s symbol-accurate (BRD §15 / NFR-001); no invented CLI p95 (FR-004) | Confirmed IDE target; CLI SLA N/A invent |
| Constraints | Thin clients; Appendix D only; OQ-10 not frozen; no JetBrains / L1–L4 product / L2/L6 / EP-005 | Confirmed |
| Scale/Scope | US-007 + US-008 only | Confirmed |

---

## ContextOS Technical Impact

| Layer | Impact |
|-------|--------|
| L1 / L2 / L4 / L6 | **N/A** — out of scope |
| L3 / L5 | **Upstream consume only** via `POST /context` — cite `specs/ep-002-*`, `specs/ep-003-*`; no re-plan |

| Surface | Impact |
|---------|--------|
| FastAPI / `POST /context` | **Consume** Confirmed contract — owner `services/orchestrator/app/api/context.py`; no new Appendix D endpoints (ADR-009) |
| **CLI** | **Primary** — `contextos ask` (FR-001..005) |
| **VS Code extension** | **Primary** — Ask ContextOS entry (FR-006..008); Pack Context already exists — Ask may be missing |
| Dashboard / Webview / GitHub Action / indexer | N/A as EP-004 deliverables |
| Telemetry | **Proposed** client-side latency logging only; orchestrator OTel remains EP-002/003 |

**Privacy / Security**: No silent bypass (FR-010 / NFR-003); A-05 trusted loopback; inherit EP-001 ignore/consent via orchestrator; full EP-005 out of scope.

**Measurable claims**: SC-001 human CLI ask; SC-003 &lt;3 clicks; SC-004 IDE &lt;2s target (harness **OQ-IDE-2s-Harness**); SC-002 machine CLI **Proposed** (OQ-10); SC-005 boundary review.

---

## Constitution Check

*GATE: Planning Gate — before and after design.*

| Gate item | Status | Evidence / mitigation |
|-----------|--------|------------------------|
| Technical context evidence-based or Proposed / NEEDS CLARIFICATION | **Pass** | Technical Context; OQs carried |
| Layers, APIs, stores, surfaces, telemetry identified | **Pass** | ContextOS Technical Impact |
| Security, privacy, performance, reliability documented | **Pass** | Security / Performance / Risks |
| Testing covers measurable claims | **Pass** | Testing Strategy — no invented Pass/Fail |
| Architecture deviations | **Pass** | None vs ADR-001/002/007/009 |
| Evidence-first (I) | **Pass** | OQ-10 not Confirmed-frozen; no invented APIs/verbs |
| Six-layer integrity (II) | **Pass** | Surfaces only; L5/L3 cite-only |
| Privacy/local-first (III) | **Pass** | Orchestrator policy; no client bypass |
| Measurable claims (IV) | **Pass** | SC-001..006; harness/schema gaps labeled |
| Boundary discipline (V) | **Pass** | FastAPI owns intelligence; clients DX only |
| Roadmap order | **Pass** | MVP CLI + VS Code (ADR-007) |

**Applicable governance**: Constitution I–V; Planning Gate; ADR-001, ADR-002, ADR-007, ADR-009, ADR-011, ADR-012, ADR-013

**Required mitigations**:
- **OQ-10**: machine-readable format **Proposed only** — ship human-readable first; no schema Pass claims
- **OQ-IDE-2s-Harness**: composed MVP exit Pass blocked without evidence
- **OQ-Ask-DX**: gesture sequence Proposed until UX fixture freeze
- CLI package path / packaging: discovery tasks — mark Proposed until scaffold lands

**Post-design re-check**: **Pass** — design stays within Confirmed `POST /context` + thin clients; no new intelligence layer.

---

## Project Structure

### Documentation (this feature)

```text
specs/ep-004-cli-vscode-surfaces/
├── spec.md              # approved
├── plan.md              # this file
├── tasks.md             # task-generator (not this agent)
└── validation-report.md # after Spec Kit triad
```

Lean Spec Kit: do **not** create quickstart / open-questions / out-of-scope-notes / ui-not-applicable adjuncts.

### Source Code (evidenced + Proposed)

```text
# Confirmed present
clients/vscode/
├── package.json                    # commands: packContext exists; Ask NOT evidenced
├── src/api/contextClient.ts        # POST /context thin client
├── src/api/types.ts                # ContextRequest / ContextResponse
├── src/commands/packContext.ts     # Pack Context pattern to reuse for Ask
├── src/commands/index.ts
├── src/extension.ts
├── src/providers/packContextPresenter.ts
└── tests/                          # vitest DX / boundary tests

services/orchestrator/app/api/context.py   # POST /context owner (consume only)

# Proposed (not present — implementation-guidelines §1)
clients/cli/                        # contextos CLI package — discovery/scaffold
├── (entrypoint / ask command)      # Proposed layout
└── tests/                          # Proposed
```

**Structure Decision**: Extend **Confirmed** `clients/vscode/` for Ask DX. Scaffold **Proposed** `clients/cli/` per `docs/architecture/implementation-guidelines.md` §1 — exact packaging (PyPI vs npm vs standalone) = discovery (**Missing Evidence**). No orchestrator intelligence changes required for MVP surfaces if `POST /context` already satisfies EP-002/003.

---

## Complexity Tracking

| Item | Why Needed | Simpler Alternative Rejected Because |
|------|------------|-------------------------------------|
| New CLI package (`clients/cli/`) | US-007 / BRD §5 / ADR-007 MVP; none exists under `clients/` | Extension-only fails BO-04 / SC-001 |
| Separate Ask vs Pack Context commands | Spec edge: Pack exists; Ask is distinct entry for &lt;3-click NFR | Reusing Pack alone may not satisfy Ask phrasing / click budget without UX decision (OQ-Ask-DX) |

---

## Technical Approach

| Area | Decision | Status |
|------|----------|--------|
| Context retrieval | `POST /context` with `query`, optional `file`, `repo`, `top_k` | **Confirmed** (api-contract §2.3) |
| CLI mapping | `contextos ask '…'` → same path | **Confirmed intent** (§6) |
| Orchestrator ownership | Search/pack/symbol policy in FastAPI | **Confirmed** (constitution V; ADR-001/002) |
| Extension HTTP | Reuse `postContext` in `contextClient.ts` | **Confirmed** pattern |
| CLI HTTP | Thin HTTP client to same contract | **Proposed** implementation |
| Human CLI output | Render `final_context` / relevant files usefully | **Confirmed** intent; format **Proposed** (OQ-CLI-Human-Format) |
| Machine CLI output | Flag/mode when planned | **Proposed**; schema = **OQ-10** (do not freeze) |
| Ask command ID | e.g. `contextos.askContext` | **Proposed** (implementation-guidelines: `contextos.` prefix) |
| Ask gesture | Palette / keybinding / menu to meet &lt;3 clicks | **Proposed** (OQ-Ask-DX) |
| CLI package path | `clients/cli/` | **Proposed** |
| Authn | Trusted loopback | **A-05**; mechanism Missing Evidence (OQ-01) |
| New HTTP endpoints | None | **Confirmed** constraint (ADR-009; spec Out of Scope) |

---

## Architecture Impact

| Area | Impact | Evidence |
|------|--------|----------|
| Frontend / IDE | **Affected** — Ask command + contributes in `clients/vscode/` | FR-006..008; ADR-007 |
| Backend | **Consume only** — no new Confirmed routes; optional client-facing error UX only | `context.py`; ADR-009 |
| Database / stores | **None** for this epic | Thin clients |
| Infrastructure | **None** new — reuse local Compose / loopback | ADR-013 |
| AI / L5 / L3 | **Cite-only** EP-002 / EP-003 | FR-009 |

---

## Components

| Component | Action | Path / note |
|-----------|--------|-------------|
| CLI package scaffold | **Create** (Proposed) | `clients/cli/` — discovery for language, entrypoint, install story |
| `contextos ask` command | **Create** | Maps query → `POST /context`; human output (FR-001, FR-002) |
| CLI machine-readable mode | **Optional / Proposed** | Behind flag when planned; schema OQ-10 (FR-003) |
| `contextClient` | **Reuse** | `clients/vscode/src/api/contextClient.ts` |
| Ask command + presenter | **Create** | Parallel to `packContext.ts` / `packContextPresenter.ts` — DX only |
| `package.json` contributes | **Modify** | Add Ask command (+ optional menu/keybinding per OQ-Ask-DX) |
| `extension.ts` / `commands/index.ts` | **Modify** | Register Ask |
| Orchestrator `context.py` | **No intelligence change required** | Consume; bugfix only if contract broken |
| Config | **Reuse** | `contextos.orchestratorBaseUrl` (Proposed setting key — already patterned) |

---

## Data Model Changes

**None** in stores. Clients consume Confirmed `ContextRequest` / `ContextResponse` (api-contract §2.3; `clients/vscode/src/api/types.ts`). Citation JSON inside `final_context` = OQ-11 (EP-002 — cite only). CLI machine DTO = **OQ-10 Proposed** — not a Confirmed entity in this plan.

---

## API Design

**No new Confirmed HTTP endpoints.**

| Item | Detail | Status |
|------|--------|--------|
| Endpoint | `POST /context` | Confirmed |
| Request | `query` (required), `file?`, `repo`, `top_k` | Confirmed |
| Response | `final_context`, `metrics`, `blast_radius`, `memory`, `relevant_files`, `is_real` | Confirmed fields |
| Status codes | Not evidenced in contract — clients handle non-2xx visibly | **Proposed** UX |
| CLI flags | e.g. `--json` / `--format` for machine mode | **Proposed**; fields per OQ-10 |
| Validation | Orchestrator-owned; clients must not bypass | Confirmed (FR-010) |

---

## UI / UX Changes

| Surface | Change | Status |
|---------|--------|--------|
| VS Code Ask | Command (+ optional keybinding/context menu) so initiation &lt;3 clicks | Confirmed NFR; gesture **Proposed** (OQ-Ask-DX) |
| Ask result presentation | Output channel / editor report pattern like Pack Context | **Proposed** reuse |
| Pack Context | Out of scope to re-spec — leave as-is (EP-003) | Confirmed boundary |
| CLI human output | Useful grounded text | Confirmed intent; layout **Proposed** |
| JetBrains | Out of scope | ADR-007 / A-02 |
| Accessibility | N/A — Not evidenced | Spec NFR |

**UI design suite** (`docs/design/ep-004-*`): not required for command/CLI DX beyond existing extension patterns (lean Spec Kit).

---

## Security Considerations

| Topic | Plan |
|-------|------|
| Authentication | A-05 trusted loopback; no invented auth scheme (NFR-004/005; OQ-01) |
| Authorization / RBAC | Orchestrator-owned when defined; clients must not bypass (FR-010) |
| Input validation | Pass query/repo/file/top_k to API; no local policy engine |
| Sensitive data | No secrets in repo; reuse extension settings / secure storage patterns |
| Consent / indexing policy | Server-side; clients surface 4xx/5xx — no silent upload of excluded paths |
| Risks | Client-side “helpful” filtering or local search would violate constitution V — forbid in review |

---

## Performance Considerations

| Concern | Plan |
|---------|------|
| IDE Ask &lt;2s | Target NFR-001 / SC-004; measurement = **OQ-IDE-2s-Harness** (composed with EP-002/003) — do not invent Pass |
| Search p95 &lt;800ms | Owned by EP-002 — cite only (NFR-002) |
| CLI latency | No invented Confirmed CLI p95 (FR-004) |
| Caching / pagination | N/A client-side intelligence cache |
| Scalability | Thin clients; scale follows orchestrator |

---

## Testing Strategy

### Unit Tests

| Focus | Location | Notes |
|-------|----------|-------|
| Ask command builds `ContextRequest` / calls `postContext` only | `clients/vscode/tests/` | Mirror `pack_context_dx.test.ts` / `no_client_policy_bypass.test.ts` |
| CLI ask maps args → request; formats human output | **Proposed** `clients/cli/tests/` | No schema Pass on OQ-10 |

### Integration Tests

| Focus | Notes |
|-------|-------|
| CLI / extension → live or mocked `POST /context` | Happy path + unreachable orchestrator surfaces error |
| Indexed-repo prerequisite | EP-001 — e2e AC blocked if unindexed |

### End-to-End Tests

| Focus | Notes |
|-------|-------|
| `contextos ask 'where is X?'` human-readable grounded output | SC-001 |
| VS Code Ask initiation click count | SC-003 — fixture per OQ-Ask-DX |
| Symbol-accurate &lt;2s | SC-004 — **blocked** for Pass until OQ-IDE-2s-Harness |

### Acceptance Tests

Map to spec AC / FR-001..010; machine-readable AC = Proposed only (FR-003 / SC-002).

### Regression Tests

Boundary: no pack/search/symbol policy in clients (SC-005); Pack Context + L3 commands unchanged; no new Confirmed endpoints.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OQ-10 unresolved | Cannot Confirmed-freeze machine CLI / schema Pass | Ship human-readable; keep `--json` Proposed |
| OQ-IDE-2s-Harness open | Cannot claim composed MVP exit Pass | Deliver Ask surface; document gap |
| CLI package/tooling Missing Evidence | Scaffold delay | Early discovery task; Proposed `clients/cli/` |
| EP-002/003 not ready | e2e ask fails | A-EP004-1/2; surface build can proceed against mocks |
| Ask vs Pack UX confusion | Miss &lt;3 clicks or wrong mental model | OQ-Ask-DX; distinct command title |
| Client policy creep | Constitution V violation | Boundary tests + review checklist |

---

## Dependencies

| Dependency | Role | Status |
|------------|------|--------|
| EP-002 / US-003 (+ US-004) | Hybrid search + phase packing via `POST /context` | Cite — do not re-plan |
| EP-003 / US-005 (+ Pack DX) | Symbol-accurate composition; `contextClient` / Pack patterns | Cite — do not re-plan |
| EP-001 | Indexed repo/workspace | Prerequisite for e2e AC |
| `services/orchestrator/app/api/context.py` | API owner | Confirmed |
| `clients/vscode/` | Ask DX | Confirmed present |
| CLI package | Not present | **Proposed** scaffold |
| Privacy defaults EP-001 | Cite; EP-005 full epic out of scope | Confirmed constraint |

---

## Implementation Phases

### Phase 0 — Setup / Discovery

- Confirm `POST /context` contract vs `contextClient` / OpenAPI sync (consume only)
- Discover CLI language, packaging, entrypoint under **Proposed** `clients/cli/`
- Inventory Ask vs Pack Context gaps in `package.json` / commands

### Phase 1 — US-007 CLI `contextos ask` (P1 / MVP)

- Scaffold CLI; implement `ask` → `POST /context` (FR-001, FR-002, FR-005, FR-010)
- Human-readable renderer (FR-001; OQ-CLI-Human-Format Proposed)
- Optional machine mode stub **Proposed only** (FR-003 / OQ-10) — no Confirmed schema
- Tests: mapping, errors, no local search policy
- **Do not** invent other verbs or CLI p95 (FR-004, FR-005)

### Phase 2 — US-008 VS Code Ask &lt;3 clicks (P1)

- Add Ask command reusing `postContext` (FR-006, FR-008)
- Wire contributes (palette ± keybinding/menu) to meet &lt;3 clicks (OQ-Ask-DX Proposed)
- Present result via existing DX patterns; visible failure when offline/unindexed (NFR-006)
- Tests: click-path / command registration; boundary no policy reimplementation (FR-008..010)
- Latency: instrument for SC-004; Pass claims gated on OQ-IDE-2s-Harness

### Phase 3 — Polish / Cross-cutting

- Boundary review (SC-005, SC-006)
- Docs: command help / extension contribution titles only as needed — no adjunct Spec Kit files
- Carry OQ-10 / harness / Ask-DX open in validation-report

---

## Evidence Reviewed

| Artifact | Use |
|----------|-----|
| `specs/ep-004-cli-vscode-surfaces/spec.md` | Requirements / OQs |
| `.specify/memory/constitution.md` | Gates I–V |
| `.cursor/rules/lean-spec-kit-artifacts.mdc` | Lean output only |
| `.specify/templates/plan-template.md` | Structure |
| `.cursor/agent-handoffs/ep-004-brief.md` | Scope / constraints |
| `docs/architecture/architecture-overview.md` §2.3 / §3.3 | Boundaries / FR mapping |
| `docs/architecture/api-contract.md` §2.3 / §6 | `POST /context` + CLI mapping |
| `docs/architecture/architecture-decisions.md` ADR-007 (+ ADR-001/002/009) | VS Code + CLI MVP |
| `docs/architecture/tech-stack.md` | Client surfaces |
| `docs/architecture/implementation-guidelines.md` | Proposed `clients/cli/`; budgets §8 |
| `clients/vscode/` (`contextClient.ts`, `packContext.ts`, `package.json`, `extension.ts`) | Existing DX; Ask absent |
| `services/orchestrator/app/api/context.py` | Orchestrator owner |
| `specs/ep-002-*`, `specs/ep-003-*` | Cite-only L5/L3 |

---

## Planning Assumptions

| ID | Assumption | Blocking? |
|----|------------|-----------|
| A-02 | VS Code + CLI MVP; JetBrains later | Non-blocking |
| A-05 | Trusted loopback until authn specified | Non-blocking |
| A-EP004-1 | EP-002 `POST /context` available for consume | Blocks e2e if missing |
| A-EP004-2 | EP-003 symbol enrichment on path for IDE symbol-accurate claim | Material for SC-004 |
| A-EP004-3 | Indexed workspace via EP-001 | Blocks e2e AC |
| A-EP004-4 | OQ-10 unresolved — human CLI shippable | Blocks Confirmed machine-schema freeze |
| A-EP004-5 | **Proposed** `clients/cli/` is correct monorepo home | Non-blocking; adjust if discovery finds better evidenced path |
| A-EP004-6 | Ask can reuse Pack Context HTTP + presentation patterns without reimplementing L5/L3 | Non-blocking |

---

## Open Questions

| ID | Question | Blocking? | Affects |
|----|----------|-----------|---------|
| **OQ-10** | CLI machine-readable output schema | Non-blocking for human ask; **blocks Confirmed schema freeze / schema Pass** | FR-003; SC-002 |
| **OQ-IDE-2s-Harness** | Verification harness for &lt;2s symbol-accurate IDE Ask | Non-blocking for Ask DX; **blocks composed MVP exit Pass** | FR-007; SC-004 |
| **OQ-Ask-DX** | Exact gesture sequence for &lt;3 clicks | Non-blocking for NFR intent; blocks UX fixture freeze | FR-006; SC-003 |
| **OQ-CLI-Human-Format** | Exact human CLI layout | Non-blocking for “useful” AC | FR-001 |
| **OQ-01** | RBAC/authn mechanism | Non-blocking under A-05 | NFR-004 |
| **OQ-CLI-Packaging** | CLI language, installer, module layout under `clients/cli/` | Non-blocking for plan; blocks concrete task paths until discovery | Phase 0 |

**Label rule**: **OQ-10 remains open.** Machine-readable CLI schema is **Proposed only**. Do **not** Confirmed-freeze OQ-10 fields.

---

## Requirement Coverage Matrix

| Requirement ID | Planned Implementation | Evidence | Status |
| -------------- | ---------------------- | -------- | ------ |
| FR-001 | CLI `ask` + human renderer | Phase 1; api-contract §6 | Covered |
| FR-002 | Thin HTTP → `POST /context` | Phase 1; no local L5/L3 | Covered |
| FR-003 | Optional machine mode Proposed; schema OQ-10 | Phase 1 optional | Covered (Proposed) |
| FR-004 | No invented CLI p95 | Performance; Risks | Covered |
| FR-005 | Only `ask` required | Phase 1 scope | Covered |
| FR-006 | Ask entry &lt;3 clicks | Phase 2; OQ-Ask-DX | Covered |
| FR-007 | Symbol-accurate IDE context target | Phase 2; harness OQ open | Covered (target; Pass gated) |
| FR-008 | Reuse `contextClient`; DX only | Phase 2; Components | Covered |
| FR-009 | Cite EP-002/EP-003; consume `/context` | Technical Approach; deps | Covered |
| FR-010 | No silent policy bypass | Security; boundary tests | Covered |
| NFR-001 | IDE &lt;2s target | Performance; SC-004 | Covered |
| NFR-002 | Search p95 cite EP-002 | Performance | Covered (cite) |
| NFR-003..005 | Security / A-05 / secrets | Security | Covered |
| NFR-006 | Visible failure offline/unindexed | Phase 1–2 error UX | Covered |
| SC-001..006 | Testing + governance | Testing; Open Questions | Covered |

---

## Out Of Scope (plan reminder)

JetBrains; other CLI verbs; L1 blast; L4 product; L2/L6; full EP-005 privacy; re-planning EP-002/EP-003; Confirmed OQ-10 freeze; new Appendix D endpoints; inventing Pass/Fail without evidence.
