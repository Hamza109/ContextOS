# Feature Specification: EP-004 CLI & VS Code Developer Surfaces

**Feature Branch**: `feature/ep-004-cli-vscode-surfaces`

**Created**: 2026-07-28

**Status**: Draft

**Input**: User description: "EP-004 — CLI & VS Code Developer Surfaces (US-007, US-008): scriptable `contextos ask` and VS Code Ask ContextOS in under three clicks (BO-01, BO-04; MVP exit)."

**Stories Covered**: US-007, US-008

**Business Objectives**: BO-01 (IDE Ask / reduce context-switching); BO-04 (CLI/scriptable discovery)

**Source Evidence**: BRD §5 CLI deliverable; §10 IDE &lt;3 clicks; §15 MVP exit; ADR-007; api-contract §2.3 `POST /context`, §6 CLI mapping; architecture-overview §2.3 / §3.3; constitution I–V; backlog EP-004 + OQ-10, A-02, A-05; EP-002 / EP-003 cite-only (do not re-spec)

**Layer / Surface Impact**: Surfaces = CLI + VS Code extension (thin clients). Intelligence = L5 search/packing + L3 symbol enrichment via existing `POST /context` (EP-002 / EP-003). No new orchestrator intelligence layer in this epic.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — CLI `contextos ask` (Priority: P1)

As a **Developer**, I want to run `contextos ask 'where is X?'` from the CLI, so that I can query ContextOS outside the IDE in scripts and terminals.

**Why this priority**: MVP — P0 scriptable surface (US-007; BRD §5 / §15; BO-04). Independently valuable once hybrid search / context retrieval (US-003 / EP-002) exists.

**Independent Test**: With CLI installed and orchestrator reachable against an indexed repo, run `contextos ask 'where is X?'` (or equivalent ask phrasing) and verify a useful human-readable answer grounded in retrieved context. Machine-readable mode is verified only as **Proposed** until OQ-10 schema is agreed — do not Confirmed-freeze or invent Pass/Fail on schema fields.

**Acceptance Scenarios**:

1. **Given** the ContextOS CLI is installed and the orchestrator is reachable with an indexed repo, **When** I run `contextos ask 'where is X?'` (or equivalent ask phrasing), **Then** I receive a useful human-readable answer grounded in retrieved context (US-007).
2. **Given** the same ask, **When** output modes are considered, **Then** machine-readable output is provided when planned (`[NEEDS CLARIFICATION: OQ-10 exact schema]` — constitution V: when planned; **Proposed only**).
3. **Given** MVP performance expectations, **When** ask completes for symbol-oriented discovery, **Then** end-to-end experience aligns with MVP search/ask goals without inventing a stricter unstated CLI SLA (US-007 Notes: IDE &lt;2s exit is IDE-scoped).
4. **Given** constitution V / api-contract §6, **When** CLI ask runs, **Then** it maps to the context retrieval path (`POST /context` or equivalent Confirmed contract) as a thin client — FastAPI owns search/context; CLI does not reimplement L5/L3 policy.

---

### User Story 2 — VS Code Ask ContextOS &lt;3 Clicks (Priority: P1)

As a **Developer**, I want to invoke Ask ContextOS from VS Code in fewer than three clicks, so that context retrieval fits daily IDE flow.

**Why this priority**: Primary MVP IDE outcome (US-008; BRD §10; §15; BO-01). ADR-007 Confirmed VS Code-first. Independently testable once extension can call `POST /context` (existing `clients/vscode/` `contextClient` / Pack Context pattern).

**Independent Test**: With ContextOS VS Code extension installed and connected to the orchestrator with an indexed workspace, invoke Ask ContextOS and verify ask initiation completes in &lt;3 clicks (BRD §10). On success, verify returned context is suitable for MVP exit symbol-accurate IDE context (&lt;2s under stated POC conditions per BRD §15) without re-specifying L3/L5 internals.

**Acceptance Scenarios**:

1. **Given** the ContextOS VS Code extension is installed and connected to the orchestrator with an indexed workspace, **When** I invoke Ask ContextOS, **Then** I can complete ask initiation in &lt;3 clicks (BRD §10; US-008).
2. **Given** a successful ask, **When** context returns, **Then** I receive symbol-accurate context suitable for MVP exit (&lt;2s symbol-accurate context in IDE per BRD §15) under stated POC conditions.
3. **Given** constitution V / ADR-007, **When** Ask is invoked from the extension, **Then** FastAPI owns packing/search/symbol orchestration via `POST /context`; the extension owns DX only and MUST NOT reimplement pack/search/symbol policy (US-008 Notes).
4. **Given** EP-002 / EP-003 upstream, **When** Ask runs, **Then** this epic consumes Confirmed `POST /context` and existing context-client patterns without re-specifying hybrid search, phase templates, or Serena symbol policy (cite `specs/ep-002-*`, `specs/ep-003-*`).

---

### Edge Cases

| Case | Expected / status |
|------|-------------------|
| Orchestrator unreachable / offline | Clients must surface failure; exact CLI/IDE error copy **Not evidenced** — Proposed UX only |
| Repo / workspace not indexed | Ask depends on indexed repo/workspace (US-007/US-008 AC); indexing owned by EP-001 — cite only |
| Empty / no-hit retrieval | Useful empty/degraded presentation expected conceptually; exact empty-result CLI/IDE contract **Not evidenced** |
| Machine-readable CLI schema | **OQ-10** open — Proposed only; do not Confirmed-freeze |
| Authn on local/dev API | **A-05**: trusted loopback until authn specified — non-blocking; authn remains Missing Evidence |
| Other CLI verbs beyond `ask` | **Out of scope** (US-007 Notes; api-contract §6 Missing Evidence for taxonomy) |
| JetBrains Ask parity | **Out of scope** (A-02 / ADR-007 / OQ-02 Future) |
| Pack Context vs Ask | Pack Context exists under EP-003 (`contextos.packContext`); Ask ContextOS command may be missing today — this epic owns Ask entry, not re-spec Pack Context |

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a CLI command `contextos ask` that accepts a natural-language query (illustrative: `contextos ask 'where is X?'`) and returns a useful human-readable answer grounded in retrieved context.  
  *Source: US-007; BRD §5, §15; api-contract §6*

- **FR-002**: CLI ask MUST invoke the Confirmed context retrieval path (`POST /context` request fields `query`, optional `file`, `repo`, `top_k` per api-contract §2.3) as a thin client; MUST NOT reimplement hybrid search, phase packing, or symbol policy.  
  *Source: US-007; api-contract §2.3 / §6; constitution V; ADR-001/002*

- **FR-003**: System MUST provide machine-readable CLI output for ask **when planned** (`[NEEDS CLARIFICATION: OQ-10 exact schema]`). Until OQ-10 is resolved, any machine-readable format remains **Proposed only** and MUST NOT be Confirmed-frozen in this specification.  
  *Source: US-007; OQ-10; constitution V; architecture-overview §5 Proposed CLI JSON+text*

- **FR-004**: CLI ask MUST NOT invent a stricter end-to-end latency SLA than evidenced for CLI; IDE &lt;2s MVP exit remains IDE-scoped (US-007). Alignment with MVP search/ask goals is required without inventing numeric CLI targets.  
  *Source: US-007 AC; BRD §15; constitution IV*

- **FR-005**: Other CLI verbs beyond `ask` MUST NOT be required for this epic (Missing Evidence / out of scope for US-007).  
  *Source: US-007 Notes; api-contract §6*

- **FR-006**: System MUST provide a VS Code Ask ContextOS entry such that ask initiation completes in fewer than three clicks when the extension is installed and connected to an indexed workspace.  
  *Source: US-008; BRD §10; ADR-007*

- **FR-007**: On successful VS Code Ask, the developer MUST receive symbol-accurate context suitable for MVP exit (&lt;2s symbol-accurate context in IDE under stated POC conditions per BRD §15). Measurement harness details shared with composed MVP exit may remain open — do not invent Pass/Fail without evidence.  
  *Source: US-008; BRD §15; constitution IV*

- **FR-008**: VS Code Ask MUST call FastAPI `POST /context` (reuse existing extension context client patterns under `clients/vscode/`); the extension MUST own DX (command / palette / menu) only and MUST NOT reimplement pack, search, or symbol policy.  
  *Source: US-008 Notes; constitution V; ADR-007; ep-004-brief*

- **FR-009**: This epic MUST consume EP-002 hybrid search / phase packing and EP-003 symbol enrichment as upstream via `POST /context` without re-specifying those behaviors.  
  *Source: EP-004 brief; US-007 dep US-003; US-008 deps US-003, US-005*

- **FR-010**: Clients (CLI and extension) MUST NOT silently bypass orchestrator validation, consent checks, RBAC (when defined), or indexing/privacy policy (constitution III/V; cite EP-001 privacy defaults — full EP-005 privacy epic out of scope).  
  *Source: constitution III/V; ADR-012 controls; A-05*

### Key Entities

| Entity | Conceptual attributes | Notes |
|--------|----------------------|-------|
| Ask query | Natural-language question string | Maps to `POST /context` `query` (**Confirmed**) |
| Context pack result | Packed context text, relevant files, provenance when present | Response fields per api-contract §2.3 (**Confirmed** shape); citation JSON inside `final_context` = OQ-11 (EP-002 — cite only) |
| CLI human output | Developer-readable rendering of context result | **Confirmed** intent; exact formatting **Proposed** |
| CLI machine output | Structured serialization of ask result | **Proposed**; schema = **OQ-10** |
| IDE Ask initiation | Gesture sequence to start Ask ContextOS | Must satisfy &lt;3 clicks (**Confirmed** NFR) |

---

## Non-Functional Requirements

### Performance

- **NFR-001**: VS Code Ask success path MUST target BRD §15 MVP exit — symbol-accurate context &lt;2s in IDE under stated POC conditions (US-008). If increment cannot meet target, plan/validation MUST document scoped gap (constitution IV).
- **NFR-002**: `POST /context` contributes to search p95 &lt;800ms @ 500k LOC (BRD §10; api-contract §2.3) — owned by EP-002; this epic MUST NOT invent a separate Confirmed CLI p95. Demo explain &lt;8s remains POC narrative (implementation-guidelines §8).

### Security

- **NFR-003**: No silent client bypass of orchestrator validation, consent, RBAC (when defined), or indexing policy (constitution V/III).
- **NFR-004**: Local/dev API may be trusted loopback until authn is specified (**A-05** — non-blocking; authn Missing Evidence).
- **NFR-005**: Secrets remain outside repo; extension uses approved secure storage / settings for API base URL as already patterned — do not invent new auth schemes here.

### Reliability

- **NFR-006**: When orchestrator is unreachable or repo unindexed, clients MUST fail visibly (exact copy **Proposed** / Not evidenced). Degraded search behavior remains orchestrator-owned (EP-001/EP-005 cite).

### Accessibility

- Not evidenced beyond standard VS Code / terminal DX — **N/A** (`Not evidenced in provided inputs.`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

| ID | Outcome | Status |
|----|---------|--------|
| **SC-001** | `contextos ask 'where is X?'` yields useful human-readable, context-grounded output | Confirmed intent (US-007) |
| **SC-002** | Machine-readable CLI ask output available when planned | **Proposed**; blocked on **OQ-10** for Confirmed schema / Pass claims |
| **SC-003** | Ask initiation in VS Code completes in &lt;3 clicks | Confirmed NFR (US-008; BRD §10) |
| **SC-004** | Successful IDE Ask returns symbol-accurate context meeting &lt;2s MVP exit under POC conditions | Confirmed target (US-008; BRD §15); verification harness may be composed — do not invent Pass without evidence |
| **SC-005** | CLI and extension are thin clients of `POST /context`; no client-side pack/search/symbol policy reimplementation | Verifiable by boundary review (constitution V) |
| **SC-006** | No Confirmed freeze of OQ-10 schema or invented CLI verbs / APIs | Governance (constitution I) |

---

## Confirmed Facts

| Fact | Evidence |
|------|----------|
| EP-004 = US-007 + US-008 only | backlog; ep-004-brief |
| BO-01 + BO-04; MVP exit includes CLI ask + IDE Ask | BRD §3, §15; backlog EP-004 |
| CLI maps `contextos ask` → `POST /context` (or equivalent) | api-contract §6; BRD §15 |
| `POST /context` request/response Confirmed fields | api-contract §2.3 |
| VS Code primary MVP IDE + CLI; JetBrains later | ADR-007; A-02 |
| FastAPI owns orchestration; CLI/extension own DX | constitution V; ADR-001/002 |
| IDE &lt;3 clicks to Ask ContextOS | BRD §10 |
| IDE symbol-accurate context &lt;2s MVP exit | BRD §15; US-008 |
| Existing: `clients/vscode/` contextClient + Pack Context; Ask command may be absent | codebase cite; package.json has `contextos.packContext`, no Ask command evidenced |
| No CLI package under `clients/` yet | codebase cite; implementation-guidelines Proposed `clients/cli/` |
| Orchestrator owner: `services/orchestrator/app/api/context.py` | ep-004-brief |

---

## Assumptions

| ID | Assumption | Blocking? | Source |
|----|------------|-----------|--------|
| **A-02** | Teams use VS Code or JetBrains (80%+); MVP ships VS Code + CLI first | Non-blocking | BRD §13; ADR-007 |
| **A-05** | Local/dev API may be trusted loopback until authn is specified | Non-blocking for MVP stories; authn Missing Evidence | api-contract §1; backlog |
| **A-EP004-1** | EP-002 `POST /context` (hybrid search + phase packing) available for clients to consume | Non-blocking if upstream delivered; else blocks e2e ask | US-007→US-003; US-008→US-003 |
| **A-EP004-2** | EP-003 symbol enrichment on context path available where “symbol-accurate” IDE Ask is claimed | Non-blocking for CLI human ask intent; material for US-008 &lt;2s symbol-accurate claim | US-008→US-005 |
| **A-EP004-3** | Indexed repo/workspace exists via EP-001 before ask AC | Non-blocking for surface build; blocks e2e AC | US-007/US-008 Given clauses |
| **A-EP004-4** | OQ-10 unresolved — human-readable CLI shippable; machine-readable remains Proposed | **Blocks Confirmed machine-schema freeze / Pass claims on schema** | OQ-10 |

---

## Dependencies

| Dependency | Role |
|------------|------|
| EP-002 / US-003 (+ phase packing US-004) | Confirmed `POST /context` retrieval — cite, do not re-spec |
| EP-003 / US-005 (+ packing DX) | Symbol-accurate IDE context composition — cite, do not re-spec |
| EP-001 indexing | Indexed repo/workspace prerequisite |
| FastAPI orchestrator `POST /context` | OpenAPI owner; `services/orchestrator/app/api/context.py` |
| VS Code extension `clients/vscode/` | Ask DX surface; reuse `api/contextClient.ts` patterns |
| CLI package | **Not present yet** — Proposed path `clients/cli/` per implementation-guidelines |
| Privacy defaults (EP-001 / constitution III) | Cite only; full EP-005 out of scope |

---

## Out Of Scope

- Rebuilding L5 hybrid search, phase templates, citation schema freeze (EP-002 / OQ-11)
- Rebuilding L3 Serena symbol policy / Pack Context acceptance (EP-003) — Ask entry only
- JetBrains extension (OQ-02 / ADR-007 Future)
- Other CLI verbs beyond `ask`
- L1 blast, L4 product compression/dashboards, L2/L6
- Full EP-005 privacy/consent/health epic (cite EP-001 privacy defaults only)
- Inventing Confirmed machine-readable CLI schema (**OQ-10**)
- Inventing authn/RBAC schemas (OQ-01; A-05)
- New HTTP endpoints beyond Appendix D / Confirmed `POST /context` consumption

---

## Open Questions

| ID | Question | Blocking? | Affects |
|----|----------|-----------|---------|
| **OQ-10** | CLI machine-readable output schema | Non-blocking for human-readable ask / story intent; **blocks Confirmed schema freeze and schema Pass claims** | US-007; FR-003; SC-002 |
| **OQ-IDE-2s-Harness** | Verification harness for &lt;2s symbol-accurate IDE Ask (composed with EP-002/EP-003) | Non-blocking for Ask surface delivery; **blocks composed MVP exit Pass claims** without evidence | US-008; SC-004 |
| **OQ-Ask-DX** | Exact VS Code gesture sequence (command palette vs keybinding vs menu) that satisfies &lt;3 clicks | Non-blocking for NFR intent; **blocks UX fixture freeze** | US-008; FR-006 |
| **OQ-CLI-Human-Format** | Exact human-readable CLI formatting (sections, citations display) | Non-blocking for “useful” AC; Missing Evidence for layout | US-007 |
| **OQ-01** | Exact RBAC/authn mechanism | Non-blocking under A-05 for local MVP; Missing Evidence | NFR-004 |

**Label rule**: **OQ-10 remains open.** Machine-readable CLI schema is **Proposed only**. Do **not** Confirmed-freeze OQ-10 fields, invent CLI verbs, or invent APIs in this specification.

---

## Requirement Traceability

| Requirement ID | Source | Evidence |
| -------------- | ------ | -------- |
| FR-001 | US-007; BRD §5/§15 | Human-readable `contextos ask` |
| FR-002 | US-007; api-contract §2.3/§6; constitution V | Thin client → `POST /context` |
| FR-003 | US-007; OQ-10; constitution V | Machine-readable when planned — Proposed |
| FR-004 | US-007 AC; BRD §15 | No invented CLI SLA |
| FR-005 | US-007 Notes; api-contract §6 | No other CLI verbs required |
| FR-006 | US-008; BRD §10; ADR-007 | Ask initiation &lt;3 clicks |
| FR-007 | US-008; BRD §15 | Symbol-accurate IDE context &lt;2s target |
| FR-008 | US-008 Notes; constitution V | Extension DX only; reuse context client |
| FR-009 | EP-004 brief; deps US-003/US-005 | Cite EP-002/EP-003; do not re-spec |
| FR-010 | constitution III/V; A-05 | No silent policy bypass |

### Acceptance Scenario → Requirement Mapping

| Scenario | Story | Requirements |
| -------- | ----- | ------------ |
| Human-readable CLI ask grounded in context | US-007 | FR-001, FR-002, FR-004, FR-010 |
| Machine-readable when planned (OQ-10 Proposed) | US-007 | FR-003 |
| No other CLI verbs required | US-007 | FR-005 |
| Ask initiation &lt;3 clicks | US-008 | FR-006, FR-008 |
| Symbol-accurate IDE context / MVP exit target | US-008 | FR-007, FR-009 |
| Thin clients; no L5/L3 reimplementation | US-007/US-008 | FR-002, FR-008, FR-009, FR-010 |

---

## Governance Notes

- Constitution Applied: **Yes** (I Evidence-First; II layer integrity via cite-only L5/L3; III privacy cite; IV measurable IDE &lt;2s / &lt;3 clicks with open harness; V CLI/extension thin-client boundaries).
- Layer/surface impact documented (CLI + VS Code; intelligence via existing `POST /context`).
- Security/privacy: no silent bypass; A-05 local trust; full EP-005 out of scope.
- **OQ-10** visible and **not** Confirmed-frozen.
- Ready for Plan Generator: **Yes, with OQ-10 carried forward as Proposed-only machine schema.**
