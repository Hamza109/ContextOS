# Implementation Plan: EP-003 L3 Symbol & LSP Navigation (Serena)

**Branch**: `feature/ep-003-l3-symbol-lsp-navigation` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/ep-003-l3-symbol-lsp-navigation/spec.md`

**Stories**: US-005, US-006, US-009, US-010 only

---

## Summary

EP-003 delivers MVP **L3** IDE-grade symbol intelligence via **Serena MCP**: definition lookup (file:line, signature, docstring), find-all-references with 2-line call-site context + file-type filter, rename-scope **analysis** (safe scope + breaking-change count; no execution sandbox), and VS Code **Pack Context** that composes upstream L5 packing with a Serena-informed **safe edit plan** (behavioral intent — not whole-file rewrite). **FastAPI** owns orchestration (optional Serena calls in the context pipeline per ADR-005). **VS Code** owns DX (hover/commands/Pack Context entry). Extension MUST NOT reimplement search/index/symbol policy (constitution V; ADR-002). Symbol proxy REST remains **Proposed** / may stay MCP-only (api-contract §3). Upstream EP-001 indexing and EP-002 `POST /context` packing are **consumed by citation only** — not re-planned.

---

## Technical Context

**Language/Version**: Python 3.11 (orchestrator — Confirmed); TypeScript (VS Code extension DX — Confirmed primary IDE per ADR-007)

**Primary Dependencies**:

| Dependency | Status | Evidence |
|------------|--------|----------|
| Serena MCP | Confirmed L3 integration | ADR-005; tech-stack; BRD FR-04..06 |
| FastAPI + Python 3.11 | Confirmed orchestrator | constitution; ADR-002 |
| VS Code extension (`clients/vscode`) | Confirmed primary IDE surface | ADR-007; architecture-overview §3.3 |
| EP-001 pack/index | Upstream consume | FR-010; EP-001 specs |
| EP-002 `POST /context` hybrid + phase pack + citations | Upstream consume | FR-010; api-contract §2.3; EP-002 |
| Symbol proxy REST | **Proposed** / may remain MCP-only | api-contract §3; FR-012 |
| OpenTelemetry-compatible SDK | Confirmed compatibility; exporter vendor **NEEDS CLARIFICATION** | ADR-011 |

**Storage**: No new Confirmed datastore for L3. Serena/LSP is local MCP session (ADR-005). Qdrant/pack cache remain EP-001/EP-002 for Pack Context packing path only. FalkorDB N/A (V1/L1).

**Testing**: **Proposed** pytest under `services/orchestrator/tests/` for orchestrator Serena adapter/pipeline; **Proposed** vitest under `clients/vscode/tests/` for DX boundary (commands/hover wiring, no policy reimplementation). FR-04 99% accuracy verification design remains **Proposed only** (OQ-12) — do not invent Pass/Fail.

**Target Platform**: Local/VPC Docker Compose POC + local Serena MCP (ADR-013; deployment notes); VS Code workspace.

**Project Type**: L3 symbol/LSP feature spanning FastAPI orchestrator (optional Serena in context pipeline) + VS Code DX.

**Performance Goals** (this feature):
- BRD §15 “symbol-accurate context <2s in IDE” is a composed MVP exit goal — EP-003 contributes L3 precision; composed harness with Ask/Pack is `[NEEDS CLARIFICATION: OQ-IDE-2s-Harness]` shared with EP-004 US-008 — do not invent EP-003-only Confirmed SLA harness
- FR-04 99% definition accuracy — Confirmed **claim**; measurement method **OQ-12** (Proposed verification only)

**Constraints**:
- Evidence-first: no invented Confirmed symbol REST, safe-edit-plan schema, citation JSON, language inventory, or accuracy Pass results (constitution I)
- FastAPI owns intelligence orchestration; extension owns DX only (constitution V; ADR-002/005)
- Symbol REST not required for MVP if MCP-only satisfies FR-04..06 (FR-012)
- Rename execution sandbox out of scope (BRD §6)
- Do not re-plan EP-001/EP-002 or full EP-004
- Ignore/exclusion inherited from EP-001 — no second ignore engine in extension

**Scale/Scope**: Monorepo ≤1M LOC MVP (A-01); Serena-backed set “12+ languages” (exact inventory OQ-Lang-Set); stories US-005/006/009/010 only

---

## ContextOS Technical Impact

**Affected Layers**:

| Layer | Impact | Evidence |
|-------|--------|----------|
| L1 | N/A as deliverable — ambiguous-symbol expand is V1 | Spec; implementation-guidelines layer table |
| L2 | N/A | V2 |
| **L3** | **Primary** — definitions, references, hover docs, rename scope, symbol-aware edit planning | Spec; ADR-005; architecture-overview §3.1 |
| L4 | N/A as product | V1 / ADR-006 |
| L5 | **Upstream consumer only** (US-010 Pack Context) — cite EP-001/EP-002 | FR-010 |
| L6 | N/A | V2 |

**Affected Surfaces**:

| Surface | Impact |
|---------|--------|
| FastAPI / API | **Affected** — optional Serena in context pipeline (ADR-005); Symbol REST **Proposed** only (api-contract §3). Confirmed `POST /context` consumed for packing (EP-002) — not re-specified |
| Serena MCP | **Confirmed** L3 integration surface |
| VS Code extension | **Primary DX** — hover/commands, Pack Context (right-click or equivalent); MCP client wiring allowed; no intelligence policy reimplementation |
| CLI | N/A as primary — full CLI is EP-004; US-010 is VS Code Pack Context |
| Dashboard / Webview / viz | N/A as primary L3 acceptance |
| GitHub Action | N/A |
| Background indexer | N/A as EP-003 deliverable — indexing remains EP-001 |
| Telemetry | **Proposed** OTel-compatible spans for Serena/symbol ops + Pack Context composition (ADR-011; exact metric names Missing Evidence) |

**Data Stores / Services**: Serena MCP session (Confirmed); EP-001 pack/index + EP-002 `POST /context` (consume); reuse security ignore/consent modules; no FalkorDB/Qdrant writes for L3-only ops

**Privacy / Security Controls**: Inherit EP-001 ignore/exclusion; no index-time external LLM exfil; query-time external LLM (if Pack Context later feeds a model) requires consent — clients MUST NOT bypass orchestrator; provenance file:line + confidence on citations (BRD §14; OQ-11 shape open); RBAC schema OQ-01 — not invented; PII redaction N/A as primary for L3

**Observability**: **Proposed** spans for definition/references/rename-scope/Pack Context composition latency. Exporter vendor open (ADR-011). Do not invent Confirmed metric names.

**Measurable Intelligence Claims** (this feature):
- Definition returns file:line, signature, docstring when available (SC-001)
- 99% accuracy **when** OQ-12 method agreed (SC-002) — Proposed verification only until then
- References + 2-line context (SC-003); file-type filter (SC-004)
- Rename scope + breaking-change count; IDE review; no sandbox claim (SC-005)
- Pack Context + Serena-informed safe edit plan (behavioral) (SC-006)
- Citations attributes when present (SC-007); boundary review (SC-008); MCP-only OK (SC-009)

---

## Constitution Check

*GATE: Planning Gate — evaluate before and after design.*

| Gate item | Status | Evidence / mitigation |
|-----------|--------|------------------------|
| Technical context evidence-based or marked Proposed / NEEDS CLARIFICATION | **Pass** | Technical Context; OQs carried |
| Affected layers, APIs, stores, surfaces, telemetry identified | **Pass** | ContextOS Technical Impact; Components; API Design |
| Security, privacy, performance, reliability documented | **Pass** | Security / Performance / Risks |
| Testing covers measurable claims | **Pass** | Testing Strategy — OQ-12 Proposed only; no invented Pass |
| Architecture deviations justified | **Pass** | None vs ADR-001/002/005/007/009 for EP-003 scope |
| Evidence-first (I) | **Pass** | No Confirmed freeze of Symbol REST, OQ-11, OQ-12 method, safe-edit shape, language inventory |
| Six-layer integrity (II) | **Pass** | L3 primary; L5 cite-only; L1/L4/L2/L6 out |
| Privacy/local-first (III) | **Pass** | Inherit EP-001 ignore; provenance; no silent bypass |
| Measurable claims (IV) | **Pass** | SC-001..009; OQ-12 / IDE-2s harness gaps labeled |
| Boundary discipline (V) | **Pass** | FastAPI orchestration; VS Code DX; MCP wiring OK |
| Roadmap order | **Pass** | MVP L5+L3; does not pull L1/L4/L2/L6 |

**Applicable governance rule IDs**: Constitution I–V; Planning Gate; ADR-001, ADR-002, ADR-005, ADR-007, ADR-009, ADR-011, ADR-012, ADR-013

**Required mitigations**:
- OQ-12: verification designs **Proposed only** — no Confirmed measurement method or Pass/Fail claims
- Symbol REST: remain MCP-first; any REST labeled Proposed (api-contract §3)
- OQ-11 / OQ-Safe-Edit-Shape: require behavioral attributes only; no Confirmed schema freeze
- OQ-Lang-Set: fixture languages Proposed subset until inventory confirmed
- OQ-MCP-Fallback: BRD §13 risk noted; product fallback UX Proposed only
- Do not re-spec EP-001/EP-002 packing/search

### Constitution Check (re-check after design)

| Item | Post-design status |
|------|-------------------|
| Planning Gate | **Met** — ready for Task Generator with OQs carried |
| Deviations | None unjustified |
| Blocking for plan draft | **None** if OQs remain labeled |
| Blocking for Confirmed contract freezes | OQ-Symbol-REST; OQ-11; OQ-Safe-Edit-Shape; OQ-Lang-Set |
| Blocking for verification pass claims | OQ-12 (99%); OQ-IDE-2s-Harness (composed <2s) |

---

## Project Structure

### Documentation (this feature)

```text
specs/ep-003-l3-symbol-lsp-navigation/
├── spec.md              # Spec Gate input
├── plan.md              # This file
└── tasks.md             # NOT created by plan-generator
```

Lean Spec Kit: do **not** create `quickstart.md`, standalone `open-questions.md`, or `out-of-scope-notes.md`.

### Source Code (repository root)

**Confirmed present** (inspected 2026-07-27 via graphify + tree): EP-001/EP-002 orchestrator L5 modules under `services/orchestrator/`; VS Code indexing DX under `clients/vscode/`. **No** `l3_*` / Serena adapter modules present yet — L3 modules below are **Proposed**.

```text
ContextOS/
├── docs/
│   ├── architecture/          # overview, api-contract, ADRs, tech-stack, implementation-guidelines, backend-architecture.puml
│   ├── backlog/user-stories.md
│   └── BRD_Context_OS.md
├── services/
│   └── orchestrator/
│       ├── app/
│       │   ├── api/
│       │   │   ├── context.py             # EP-002 — Pack Context consumes; may enrich via L3 (Proposed)
│       │   │   └── …                      # No Confirmed symbol REST router required
│       │   ├── services/
│       │   │   ├── l5_*                   # EP-001/EP-002 — reuse for Pack Context packing
│       │   │   └── l3_symbol.py           # Proposed NEW — SymbolService (FR-04..06); backend-architecture.puml
│       │   ├── adapters/
│       │   │   └── serena_mcp.py          # Proposed NEW — Serena MCP client adapter
│       │   ├── security/                  # reuse ignore/consent — no second ignore engine
│       │   └── telemetry/
│       │       └── symbol.py              # Proposed NEW — L3 spans (names open)
│       └── tests/
│           ├── unit/
│           ├── integration/
│           └── contract/
├── clients/
│   └── vscode/                            # Confirmed present — extend DX
│       ├── src/
│       │   ├── extension.ts               # register symbol/Pack Context commands (Proposed)
│       │   ├── api/                       # indexClient present; contextClient Proposed for Pack Context
│       │   ├── providers/                 # Proposed — hover / references presentation
│       │   ├── commands/                  # Proposed — definition, references, rename-scope, packContext
│       │   └── mcp/                       # Proposed — Serena MCP client wiring (DX only)
│       └── tests/                         # vitest — boundary + command smoke
├── deploy/
│   └── docker-compose.yml                 # reuse; Serena local process config Proposed
└── specs/
    ├── ep-001-l5-repository-packing-indexing/   # cite only
    ├── ep-002-l5-hybrid-search-phase-packing/   # cite only
    └── ep-003-l3-symbol-lsp-navigation/
```

**Structure Decision**: Extend existing orchestrator + `clients/vscode`. Package names `l3_symbol`, `serena_mcp`, extension `providers/`/`commands/`/`mcp/` are **Proposed** (implementation-guidelines §1–2; backend-architecture SymbolService). Prefer MCP-first path; do not invent Confirmed symbol REST routers.

---

## Complexity Tracking

> No constitution violations requiring justification. Dual path (extension MCP DX + optional orchestrator Serena in context pipeline) is **Confirmed** by ADR-005, not avoidable complexity.

| Item | Notes |
|------|-------|
| Avoidable complexity | None — do not add Symbol REST unless product confirms (OQ-Symbol-REST) |
| Regex fallback | BRD §13 risk — **Proposed** only; do not Confirmed-freeze product UX |

---

## Technical Approach

### Confirmed architecture

1. **Serena MCP for L3** — definitions, references, hover docs, rename-scope, symbol-aware edit planning (ADR-005; BRD L3; architecture-overview §3.1).
2. **Boundary** — FastAPI owns orchestration/policy; VS Code owns DX; extension may use MCP client wiring for Serena UX but MUST NOT reimplement search/index/symbol policy (ADR-002; constitution V; implementation-guidelines §3).
3. **Orchestrator may call Serena** in the context pipeline for symbol-aware packing / safe edit plan composition (ADR-005).
4. **FR-04** — definition location includes file:line, signature, docstring when available; 12+ languages claimed; 99% accuracy claim with OQ-12 open.
5. **FR-05** — monorepo references + 2 lines before/after + file-type filter.
6. **FR-06** — safe rename scope + breaking-change count before execution; **analysis only** (BRD §6 sandbox out).
7. **BRD §11** — Pack Context from IDE + Serena-informed safe edit plan (not whole-file rewrite).
8. **Citations** — file:line + confidence when present (BRD §14); JSON shape OQ-11.
9. **Confirmed HTTP** (Appendix D / ADR-009): `GET /`, `POST /index`, `POST /context`, `GET /blast`, `GET /graph.html` — **no** Confirmed L3 symbol REST. Blast/graph are V1 — not EP-003 deliverables.
10. **Upstream**: EP-001 indexing; EP-002 `POST /context` packing — consume, do not re-plan.
11. **MVP roadmap**: L5+L3 (ADR-001).

### Proposed architecture (implementability — not Confirmed freeze)

1. **Modules (Proposed names)**: `adapters/serena_mcp`, `services/l3_symbol` (SymbolService per backend-architecture.puml), optional `telemetry/symbol`; extension `commands/*`, `providers/*`, `mcp/*`, `api/contextClient`.
2. **Capability flow (Proposed)**:
   ```
   IDE symbol request (hover/command)
     → Serena MCP (primary) OR orchestrator SymbolService → Serena adapter
     → Definition / References / Rename-scope analysis / Hover docs
     → Extension presents results (DX only)

   Pack Context (VS Code command / context menu)
     → FastAPI POST /context (EP-002 packing + citations)  [Confirmed consume]
     → Orchestrator MAY call Serena for symbol-aware safe edit plan enrichment (ADR-005)
     → Return packed context + Serena-informed safe edit plan (shape Proposed / OQ-Safe-Edit-Shape)
     → Extension presents plan; MUST NOT pack/search/index locally
   ```
3. **Transport strategy (OQ-Symbol-REST)**:
   | Option | Description | Status |
   |--------|-------------|--------|
   | **A (recommended MVP)** | MCP-only for FR-04..06 IDE paths; orchestrator calls Serena internally for Pack Context enrichment | Aligns with api-contract §3 “may remain MCP-only” |
   | **B** | Add Symbol proxy REST | **Proposed only** — requires product confirmation; never treat as Appendix D Confirmed |

   **Recommendation (Proposed, not Confirmed)**: Ship **Option A** for MVP acceptance (SC-009). Document Option B as deferred.
4. **Safe edit plan (OQ-Safe-Edit-Shape)**: Deliver **behavioral** content: symbol-scoped edit guidance derived from Serena (definition/refs/rename signals) rather than “rewrite entire file”. Machine schema **Not evidenced** — do not invent Confirmed JSON fields. **Proposed** interim: structured text section or clearly delimited block alongside `final_context` / IDE presentation until product freezes shape.
5. **Citation (OQ-11)**: When Pack Context returns citations, require file:line + confidence attributes; reuse EP-002 citation behavior without freezing field names.
6. **Language fixtures (OQ-Lang-Set)**: Until inventory confirmed, AC fixtures use a **Proposed** small subset of Serena-supported languages evidenced in test setup — do not claim language-complete matrix Pass.
7. **Unresolved / ambiguous symbols (OQ-Unresolved-Symbol)**: MVP returns no/partial definition; L1 expand is V1 — do not invent blast expand in EP-003.
8. **MCP unavailable (OQ-MCP-Fallback)**: BRD §13 mentions pin versions + regex fallback — product UX **Missing Evidence**. **Proposed**: surface clear IDE/orchestrator error; optional regex fallback only if labeled Proposed and tested as degraded — do not claim Confirmed product behavior.
9. **Rename execution**: Out of scope — analysis + IDE review only (FR-007).

### Missing evidence (do not invent)

- Symbol proxy REST contract (OQ-Symbol-REST)
- OQ-12 accuracy measurement method
- Exact Serena language inventory (OQ-Lang-Set)
- Safe edit plan machine schema (OQ-Safe-Edit-Shape)
- Citation JSON field names (OQ-11)
- Confirmed MCP fallback UX (OQ-MCP-Fallback)
- Unresolved-symbol UX beyond no/partial (OQ-Unresolved-Symbol)
- Composed <2s IDE harness (OQ-IDE-2s-Harness)
- RBAC/authn schema (OQ-01)
- Exact OTel metric names for L3

---

## Architecture Impact

| Area | Impact | Evidence |
|------|--------|----------|
| **Frontend / Extension** | **Affected** — hover/commands, Pack Context DX, MCP wiring | architecture-overview §3.3 FR-04..06; US-010 |
| **Backend** | **Affected** — Proposed SymbolService + Serena adapter; optional enrichment on Pack Context / `POST /context` path | ADR-005; backend-architecture.puml SymbolService |
| **Database / stores** | No new Confirmed store; no FalkorDB; Qdrant/pack read-only via EP-002 for Pack Context | Spec; FR-010 |
| **Infrastructure** | Reuse Compose; **Proposed** local Serena process/config docs — no new Confirmed infra product | ADR-013 |
| **AI Components** | Serena MCP/LSP (Confirmed); no index-time LLM; query-time LLM consent not EP-003 UX deliverable | ADR-005; constitution III |
| **CLI** | N/A primary (EP-004) | Spec Out of Scope |

---

## Components

| Component | Action | Responsibility |
|-----------|--------|----------------|
| Serena MCP adapter | Create (**Proposed**) | Call Serena for definition/references/hover/rename-scope; pin versions where feasible |
| SymbolService (`l3_symbol`) | Create (**Proposed**) | Orchestrator-side FR-04..06 ops; used when pipeline needs symbols (Pack Context enrichment) |
| Extension hover provider | Create (**Proposed**) | Present Serena hover/doc + definition attributes without inventing schema fields (FR-014) |
| Extension commands | Create (**Proposed**) | Definition lookup, find references (+ file-type filter UX), rename-scope analysis review, Pack Context |
| Extension MCP wiring | Create (**Proposed**) | Thin client to Serena for IDE DX paths (ADR-005) |
| Context / Pack client | Create (**Proposed**) | Call Confirmed `POST /context` for packing; display safe edit plan; no local pack/search |
| `POST /context` enrichment | Modify (**Proposed**) | Optional Serena-informed safe edit plan composition — must not re-spec EP-002 hybrid/phase |
| Symbol proxy REST | **Optional / Deferred** | Only if OQ-Symbol-REST resolves to REST — label Proposed; not MVP-required |
| Ignore / consent security | Reuse | No second ignore engine; no silent bypass |
| L3 telemetry | Create (**Proposed**) | Spans for symbol ops / Pack Context composition |
| Boundary tests | Extend | Extension must not reimplement search/index/symbol policy (pattern: `no_client_policy_bypass`) |

**Background Jobs**: None required for L3 query path. Index freshness remains EP-001.

**Configuration**: **Proposed** Serena MCP endpoint/command settings; reuse `contextos.orchestratorBaseUrl` for Pack Context API calls. Keys not Confirmed product freeze.

**Shared modules**: EP-002 context path; EP-001 ignore/consent; extension `api/` patterns.

---

## Data Model Changes

### Logical entities (this feature)

| Entity | Notes | Status |
|--------|-------|--------|
| Symbol | Named code entity | Confirmed concept |
| Definition Result | file:line, signature, docstring when available | Confirmed attributes (FR-04); transport schema beyond MCP **Not evidenced** as Confirmed REST |
| Reference Hit | Occurrence + 2 lines before/after; optional file-type filter | Confirmed behavior (FR-05) |
| Rename Scope Analysis | Safe scope + breaking-change count | Confirmed behavior (FR-06); analysis only |
| Safe Edit Plan | Serena-informed edit guidance with Pack Context | Behavioral entity; machine shape **OQ-Safe-Edit-Shape** |
| Packed Context / Citation | EP-002 output; file:line + confidence | Consume; JSON **OQ-11** |
| Serena MCP Session | Local MCP/LSP bridge | Confirmed integration choice (ADR-005) |

### Modified entities

| Entity | Change | Status |
|--------|--------|--------|
| `POST /context` response | MAY include Serena-informed safe edit plan content | **Proposed** enrichment — do not invent Confirmed new Appendix D fields |
| Extension contributes | Commands / menus / hover | **Proposed** `contextos.*` command IDs (implementation-guidelines §2) |

### Relationships

- Symbol → Definition Result; Symbol → many Reference Hits; Symbol → Rename Scope Analysis
- Pack Context → Packed Context (EP-002) + Safe Edit Plan (L3) for selection

### Validation rules

- Require workspace/symbol selection for IDE ops; unsupported language → clear failure (**Proposed** UX; inventory open)
- File-type filter: empty filtered set allowed conceptually; exact empty contract **Not evidenced**
- Breaking-change count ≥ 0; zero is valid (spec edge case)
- Do not invent Confirmed REST validators for undeclared symbol endpoints

### Migration requirements

- None for Qdrant/FalkorDB.
- Serena local install/config is operational dependency (A-EP003-1) — document in tasks as setup, not schema migration.

---

## API Design

### Confirmed HTTP (consume / do not invent L3 REST)

| Endpoint | EP-003 role |
|----------|-------------|
| `POST /context` | **Consume** for Pack Context packing + citations (EP-002 Confirmed fields) — may **Proposed**-enrich with safe edit plan content without claiming new Confirmed Appendix D fields |
| `POST /index`, `GET /` | Upstream/health only — not L3 deliverables |
| `GET /blast`, `GET /graph.html` | V1 — **out of scope** |

### Symbol capabilities transport

| Path | Status | Rule |
|------|--------|------|
| Serena MCP tools/session for FR-04..06 | Confirmed integration choice | Primary MVP path (FR-012; SC-009) |
| Symbol proxy REST | **Proposed** / NEEDS CLARIFICATION | Do **not** treat as Confirmed; do not invent paths/schemas as Appendix D |

### Pack Context composition (Proposed orchestration)

- Extension invokes Pack Context → FastAPI `POST /context` with selection-derived `query`/`file`/`repo` (Confirmed request fields only unless OQ-16 phase field separately Proposed by EP-002 — do not invent here)
- Orchestrator MAY call SymbolService/Serena to attach safe edit plan guidance
- Response must satisfy behavioral FR-008/FR-009; safe-edit machine shape remains open

### Validation / errors

- MCP/Serena unavailable: **Proposed** clear error to IDE; fallback UX Proposed only (OQ-MCP-Fallback)
- Unindexed workspace: Pack Context / references may be unavailable — indexing owned by EP-001
- Authn for any future Symbol REST: `[NEEDS CLARIFICATION]` (api-contract) — non-blocking while MCP-only

### Non-goals for API in this epic

- No Confirmed symbol REST
- No re-specification of `POST /context` Confirmed field inventory
- No Confirmed CLI machine schema (EP-004)

---

## UI / UX Changes

**Primary surface: VS Code extension** (`clients/vscode`).

| Change | Notes | Status |
|--------|-------|--------|
| Hover / definition presentation | Show file:line, signature, docstring when available; hover docs from Serena (FR-014) | Proposed DX |
| Find references command/UI | Show refs + 2-line context; file-type filter control | Proposed DX |
| Rename scope analysis view | Show safe scope + breaking-change count; review before execute; **no** execution sandbox UI claiming ContextOS sandbox | Proposed DX |
| Pack Context command / context menu | Right-click or equivalent → packed context + safe edit plan presentation | Proposed DX (`contextos.packContext` or equivalent — Proposed ID) |
| Webview | Not required as primary acceptance; if used for plan presentation, sanitize messages (constitution III) | Optional Proposed |

**Accessibility**: N/A beyond standard VS Code DX (`Not evidenced in provided inputs.`).

**Out of scope UX**: Full Ask <3 clicks (US-008 / EP-004); JetBrains; blast/graph visualization; L4 dashboards.

---

## Security Considerations

| Concern | Plan |
|---------|------|
| **Authentication** | Local MCP + trusted loopback API MAY apply until authn clarified — non-blocking for MCP-local MVP |
| **Authorization / RBAC** | OQ-01 open — reserve hooks; do not invent roles |
| **Input validation** | Validate symbol/file selection paths; do not read excluded content via client-side “helpful” walks |
| **Sensitive data** | Inherit EP-001 ignore/`.env`/secrets exclusions; no second ignore engine in extension |
| **Exfil** | Symbol lookup via local Serena MCP — MUST NOT invent cloud exfil of source for L3 ops (NFR-004) |
| **Consent** | Query-time external LLM (if Pack Context later feeds model) via orchestrator consent gate — clients MUST NOT bypass |
| **Provenance** | Citations file:line + confidence when present (FR-009) |
| **Webview messages** | Validate/sanitize if Webview used |
| **Policy bypass** | Extend boundary tests: no client-side search/index/symbol policy reimplementation (FR-011, FR-013) |

---

## Performance Considerations

| Concern | Plan |
|---------|------|
| **IDE latency** | Contribute L3 precision toward BRD §15 <2s composed goal; harness **OQ-IDE-2s-Harness** — do not invent Pass |
| **Caching** | **Proposed** short-lived in-process cache of recent definition/refs keyed by symbol+file revision — not Confirmed |
| **Pagination** | File-type filter reduces reference set; full pagination API **Not evidenced** |
| **Scalability** | Monorepo references within ≤1M LOC MVP assumption (A-01) |
| **Load** | POC/local — multi-tenant load Not evidenced |
| **Degraded** | MCP down → Proposed error/fallback (OQ-MCP-Fallback); partial index → Pack Context may fail/unavailable until EP-001 index exists |

---

## Testing Strategy

### Unit Tests

- SymbolService mapping of Serena payloads → Definition Result attributes (file:line, signature, docstring when available) without inventing Confirmed REST schema
- Reference context window = 2 lines before/after; file-type filter behavior
- Rename analysis produces scope + breaking-change count (including zero)
- Safe edit plan behavioral discriminator: plan is symbol-scoped / not “rewrite entire file” directive (assert intent markers — **Proposed**; no invented schema keys)
- Extension static boundary: no pack/search/index/symbol-policy reimplementation (extend `no_client_policy_bypass` patterns for symbol policy)

### Integration Tests

- Serena MCP (or test double) → definition / references / rename-scope for fixture symbol in supported language (**Proposed** fixture language subset until OQ-Lang-Set)
- Pack Context path: extension → `POST /context` returns packed context; when citations present, file:line + confidence attributes exist (no invented JSON key asserts — OQ-11)
- Orchestrator optional Serena enrichment path for safe edit plan when implemented
- Unavailable Serena → Proposed error path (no Confirmed fallback Pass unless designed)

### End-to-End Tests

- VS Code command smoke (vitest/integration harness as available): Pack Context, definition, references, rename-scope review
- Full Ask <3 clicks E2E **not** required (EP-004)
- Docker Compose + Serena local smoke **Proposed** for orchestrator enrichment path

### Acceptance Tests (map to SC)

| Success criterion | Test approach | Gap / rule |
|-------------------|---------------|------------|
| SC-001 definition attributes | Integration / E2E fixture | — |
| SC-002 99% accuracy | **Proposed verification design only** | **OQ-12** — no Pass/Fail until method + evidence |
| SC-003 refs + 2-line context | Integration | — |
| SC-004 file-type filter | Integration | Empty filter set conceptual |
| SC-005 rename analysis + IDE review | Integration + DX smoke; assert no execution sandbox claim | BRD §6 |
| SC-006 Pack Context + safe edit plan | E2E behavioral | OQ-Safe-Edit-Shape — behavioral only |
| SC-007 citations attributes | Inspect packed output | OQ-11 — no invented keys |
| SC-008 boundary | Architecture/static review + tests | — |
| SC-009 MCP-only OK | No Confirmed symbol REST required | api-contract §3 |

### Regression Tests

- EP-001 `POST /index` / ignore / no-exfil remain green
- EP-002 `POST /context` hybrid/phase/citation tests remain green
- Extension indexing DX (US-011/012) remains green

### Harness gaps (explicit)

- **OQ-12**: Measurement method Missing Evidence — accuracy Pass claims **blocked**
- **OQ-IDE-2s-Harness**: Composed <2s Pass claims **blocked** until harness agreed
- **OQ-Lang-Set**: Language-complete matrix **blocked**; use Proposed subset fixtures

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| MCP ecosystem instability (BRD §13) | L3 DX/pipeline failures | Pin Serena/MCP versions; Proposed degraded error/fallback; do not claim Confirmed regex UX |
| OQ-12 unresolved | Cannot claim 99% Pass | Ship functional definition lookup; Proposed verification design only; document scoped gap if needed (constitution IV) |
| Extension reimplements symbol policy | Constitution V violation | MCP/API-thin clients; boundary tests; code review checklist |
| Inventing Symbol REST as Confirmed | Contract drift (ADR-009) | MCP-first Option A; REST labeled Proposed only |
| Safe-edit-plan schema invention | False Confirmed freeze | Behavioral verification only (OQ-Safe-Edit-Shape) |
| Re-planning EP-001/EP-002 | Scope creep / duplicate packing | Cite specs only; consume `POST /context` |
| Pulling EP-004 Ask into EP-003 | Scope creep | Pack Context surface only; US-008 conceptual dep |
| Serena language gaps | Fixture/AC failures | Proposed subset; carry OQ-Lang-Set |
| Rename execution creep | Safety/scope violation | Analysis + review only; no sandbox claim |

---

## Dependencies

### Internal Dependencies

| Dependency | Nature |
|------------|--------|
| EP-001 indexing / pack foundation | Indexed workspace for US-006/US-010 (cite `specs/ep-001-*`) |
| EP-002 `POST /context` hybrid + phase + citations | Pack Context packing (cite `specs/ep-002-*`) |
| `clients/vscode` EP-001 indexing DX | Extend; do not break boundary tests |
| `services/orchestrator` L5 modules | Reuse for Pack Context; add Proposed L3 modules |
| US-008 (EP-004) | Conceptual IDE entry dependency — not re-specified |

### External Services

| Service | Role |
|---------|------|
| Serena MCP (local) | L3 symbol/LSP operations |
| FastAPI orchestrator | Pack Context + optional Serena enrichment |

### Third-party Libraries

| Library | Status |
|---------|--------|
| Serena / MCP client SDKs | Confirmed integration choice; exact package pins **NEEDS CLARIFICATION** in tasks |
| FastAPI / Pydantic | Confirmed |
| VS Code Extension API | Confirmed |
| OpenTelemetry SDK | Compatibility Confirmed; exporter open |
| Regex fallback library | **Proposed only** if implementing BRD §13 fallback — not Confirmed product |

### Infrastructure Dependencies

- Docker Compose API (+ Qdrant for Pack Context via EP-002)
- Local Serena MCP available in developer workspaces (A-EP003-1)

---

## Implementation Phases

### Phase 0 — Setup / Foundation

- Confirm branch `feature/ep-003-l3-symbol-lsp-navigation`
- Verify Serena MCP availability locally (or documented test double strategy)
- Scaffold Proposed `adapters/serena_mcp`, `services/l3_symbol`, extension command/provider/mcp folders
- Confirm EP-001 index + EP-002 `POST /context` usable for Pack Context fixtures (cite only)
- Carry all OQs into task notes (no silent freeze)
- Telemetry skeleton for L3 (**Proposed**)

### Phase 1 — User Story 1 / US-005 (P1) — Symbol Definition Lookup

**Goal**: Resolve definition via Serena (file:line, signature, docstring when available); IDE hover/commands present results; no policy reimplementation.

- Implement Serena adapter definition path + SymbolService mapping
- Extension hover/command DX
- Language fixtures: Proposed subset (OQ-Lang-Set)
- OQ-12: document **Proposed** verification approach only — no Pass claims
- Tests: SC-001, SC-008; SC-002 design note only

**Independent deliverable**: Definition lookup works without references/rename/Pack Context.

### Phase 2 — User Story 2 / US-006 (P1) — Find All References

**Goal**: Monorepo references with 2-line call-site context + file-type filter; IDE presentation.

- Implement references via Serena; apply file-type filter
- Extension DX for results
- Tests: SC-003, SC-004
- Depends on: US-005 resolution identity

### Phase 3 — User Story 3 / US-009 (P1) — Rename Scope Analysis

**Goal**: Safe rename scope + breaking-change count; IDE review prior to execution; no execution sandbox.

- Implement rename-scope analysis via Serena-backed capabilities
- Extension review surface
- Explicitly exclude rename execution / sandbox
- Tests: SC-005
- Depends on: US-005, US-006

### Phase 4 — User Story 4 / US-010 (P1) — Pack Context & Safe Edit Plan

**Goal**: VS Code Pack Context → EP-002 packing + Serena-informed safe edit plan (behavioral); citations attributes when present.

- Extension Pack Context command/context-menu
- Call Confirmed `POST /context` (no local pack/search)
- Orchestrator **Proposed** Serena enrichment for safe edit plan
- Citations: file:line + confidence (OQ-11 — no invented JSON)
- Do not expand full EP-004 Ask/CLI
- Tests: SC-006, SC-007, SC-008, SC-009
- Depends on: EP-001/EP-002 upstream + US-005

### Phase 5 — Polish / Cross-cutting

- MCP unavailable Proposed error/fallback notes (OQ-MCP-Fallback)
- Boundary/regression vs EP-001/EP-002 + extension indexing
- OpenAPI: ensure no invented Confirmed symbol REST; label any Proposed proxy
- OQ-12 / OQ-IDE-2s harness status documented for later validation-report (not Pass invention)
- Docs: none beyond plan/tasks/validation path — no quickstart / design suite

---

## Evidence Reviewed

| Artifact | Use |
|----------|-----|
| `specs/ep-003-l3-symbol-lsp-navigation/spec.md` | Primary requirements US-005/006/009/010 |
| `.specify/memory/constitution.md` v1.0.0 | Governance I–V; Planning Gate |
| `.cursor/rules/lean-spec-kit-artifacts.mdc` | Lean artifact discipline |
| `.cursor/agent-handoffs/ep-003-brief.md` | Scope lock; OQ checklist |
| `.cursor/agent-handoffs/handoff.md` | Latest plan-generator handoff context |
| `.specify/templates/plan-template.md` | Required plan structure |
| `specs/ep-002-l5-hybrid-search-phase-packing/plan.md` | Lean cite-heavy style model |
| `docs/architecture/architecture-overview.md` §3.1/§3.3 | L3 surfaces FR-04..06 |
| `docs/architecture/api-contract.md` §3 | Symbol REST Proposed / MCP-only |
| `docs/architecture/architecture-decisions.md` ADR-002, ADR-005 (+ ADR-001/007/009/011/012/013) | Boundaries; Serena |
| `docs/architecture/tech-stack.md` | Serena MCP Confirmed |
| `docs/architecture/implementation-guidelines.md` | `l3_*`, no intelligence in extension, testing notes |
| `docs/architecture/backend-architecture.puml` | SymbolService → Serena MCP client |
| `docs/BRD_Context_OS.md` FR-04..06; §6; §11; §13–§15; Pack & Cite | Product evidence |
| `docs/backlog/user-stories.md` EP-003 + US-005/006/009/010; OQ-12 | AC alignment |
| `specs/ep-001-*`, `specs/ep-002-*` | Upstream cite-only for US-010 |
| Live tree `services/orchestrator/app/**`, `clients/vscode/**` | Confirmed present modules; L3 not yet implemented |
| `graphify query` (L3/Serena/Symbol) | Pre-exploration graph; docs + EP-001/002 nodes; no existing `l3_*` code |

---

## Planning Assumptions

| ID | Assumption | Blocking? |
|----|------------|-----------|
| A-01 | Git source of truth; monorepo ≤1M LOC for MVP (BRD §13) | Non-blocking |
| A-02 | MVP ships VS Code first (ADR-007); JetBrains out | Non-blocking |
| A-EP003-1 | Serena MCP available locally for developer workspaces | Non-blocking for plan; **blocking for runtime L3 acceptance** |
| A-EP003-2 | EP-001 indexing completed sufficiently for indexed-workspace flows | Non-blocking for plan; blocking for US-006/010 runtime |
| A-EP003-3 | EP-002 `POST /context` available for Pack Context consume | Non-blocking for plan; blocking for US-010 packing |
| A-EP003-4 | US-008 conceptual dep; EP-003 does not own full Ask acceptance | Non-blocking |
| A-EP003-5 | OQ-12 unresolved — definition delivery may proceed; accuracy Pass blocked | Blocks Confirmed 99% verification |
| A-EP003-6 | Safe-edit shape + Symbol REST open — behavioral MCP delivery may proceed | Blocks Confirmed schema/REST freeze |
| A-EP003-7 (**Proposed**) | MCP-first Option A is acceptable MVP transport pending OQ-Symbol-REST | Non-blocking |

---

## Open Questions

| ID | Question | Blocking? | Plan handling |
|----|----------|-----------|---------------|
| **OQ-12** | Measurement method for Serena 99% definition accuracy | Blocks verification Pass claims | **Proposed verification only** — no invented method/Pass |
| **OQ-11** | Citation JSON shape in packed context | Blocks Confirmed citation schema freeze | Require file:line + confidence attributes; cite EP-002 |
| **OQ-Symbol-REST** | Symbol proxy REST vs MCP-only | Blocks Confirmed REST contract | MCP-first Option A; REST Proposed only |
| **OQ-Lang-Set** | Exact Serena language inventory beyond “12+” | Blocks language-complete fixture matrix | Proposed subset fixtures |
| **OQ-Safe-Edit-Shape** | Exact safe edit plan machine shape | Blocks Confirmed schema freeze | Behavioral intent only |
| **OQ-Unresolved-Symbol** | MVP UX for unresolved/ambiguous symbols | Non-blocking | No/partial definition; no L1 expand |
| **OQ-MCP-Fallback** | Confirmed regex/fallback UX when Serena unavailable | Non-blocking | Proposed error/degraded only |
| **OQ-IDE-2s-Harness** | Harness for <2s symbol-accurate IDE context | Blocks composed MVP exit Pass claims | Carry; shared with EP-004 |
| **OQ-01** | RBAC roles/path/authn schema | Non-blocking for MCP-local MVP | Do not invent; reserve hooks |

**Label rule**: All remain **OPEN**. Do **not** Confirmed-freeze Symbol REST, OQ-11, OQ-12 method, language inventory, or safe-edit-plan schema in this plan.

---

## Out Of Scope (explicit)

- L1 blast radius, FalkorDB product, `GET /blast`, `graph.html` (V1)
- L4 Headroom compression product / token-budget dashboards (ADR-006)
- L2 multi-modal graphs and L6 persistent memory (V2)
- Rename **execution** and code-execution sandbox (BRD §6)
- Inventing Confirmed Symbol proxy REST endpoints (api-contract §3)
- Re-planning EP-001 indexing/packing or EP-002 hybrid search / phase templates / citation schema freeze
- Full EP-004 CLI epic and Ask ContextOS <3 clicks acceptance beyond US-010 Pack Context surface
- JetBrains extension (ADR-007 Future)
- Exact Confirmed measurement method for Serena 99% (OQ-12) — Proposed verification only
- Invented safe-edit-plan JSON schema or citation field names
- RBAC role/schema design (OQ-01)
- UI design suite under `docs/design/` (lean Spec Kit — N/A unless asked)

---

## Requirement Coverage Matrix

| Requirement ID | Planned Implementation | Evidence | Status |
| -------------- | ---------------------- | -------- | ------ |
| FR-001 | Serena adapter + SymbolService definition path; IDE presentation | ADR-005; Phase 1 | Covered |
| FR-002 | Supported-language fixtures (12+ claim); inventory OQ-Lang-Set | Phase 1; OQ-Lang-Set | Covered (inventory open) |
| FR-003 | 99% target; Proposed verification only (OQ-12) | Testing; constitution IV | Covered (verify design Proposed) |
| FR-004 | References + 2-line context | Phase 2 | Covered |
| FR-005 | File-type filter on references | Phase 2 | Covered |
| FR-006 | Rename scope + breaking-change count (analysis) | Phase 3 | Covered |
| FR-007 | IDE review surface; no execution sandbox | Phase 3; Out of Scope | Covered |
| FR-008 | Pack Context DX + Serena-informed safe edit plan (behavioral) | Phase 4; OQ-Safe-Edit-Shape | Covered |
| FR-009 | Citations file:line + confidence; no invented JSON | Phase 4; OQ-11; EP-002 cite | Covered |
| FR-010 | Consume EP-001/EP-002; do not re-spec | Phase 0/4; Dependencies | Covered |
| FR-011 | FastAPI orchestration; VS Code DX; no policy reimplementation | Components; boundary tests | Covered |
| FR-012 | MCP-only OK; Symbol REST Proposed | API Design Option A | Covered |
| FR-013 | Extension surfaces without silent policy bypass | Security; Phase 5 | Covered |
| FR-014 | Hover docs / document symbols from Serena | Phase 1 hover provider | Covered |
| FR-015 | Explicit out-of-scope layers/surfaces honored | Out of Scope; phases | Covered |

---

## Governance Notes

- Constitution Applied: **Yes** (I–V)
- Planning Gate: **Met** with open questions carried
- Ready for Task Generator: **Yes**, provided tasks preserve Proposed vs Confirmed labels, MCP-first transport, OQ-12 Proposed verification only, and cite-only EP-001/EP-002 deps
