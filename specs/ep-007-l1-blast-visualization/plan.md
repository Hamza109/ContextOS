# Implementation Plan: EP-007 L1 Blast Radius & Visualization

**Branch**: `feature/ep-007-l1-blast-visualization` | **Date**: 2026-07-28 | **Spec**: [spec.md](./spec.md)

**Input**: Approved feature specification for US-018, US-019, US-020, and US-027 only.

## Summary

EP-007 delivers V1 blast-radius analysis and dependency visualization over the existing EP-006 FalkorDB L1 graph. FastAPI owns Confirmed `GET /blast/{file_name}?repo=`, Confirmed `GET /graph.html?repo=` (vis-network), and V1 population of the existing `POST /context` field `blast_radius`. MCP stays a thin client. US-020 React Flow Webview and US-027 staleness signaling remain in epic scope; React Flow may ship after FastAPI blast/graph contracts land. No L1 parser/index redesign; no OKF, L2, L4, or L6 work.

## Technical Context

**Language/Version**: Python 3.11 / FastAPI (Confirmed orchestrator). VS Code extension TypeScript for US-020/US-027 (Confirmed EP-004 shell).

**Primary Dependencies**: Existing FalkorDB L1 stack from EP-006 (`falkordb_store.py`, `l1_graph.py`, `l1_structural_query.py`, `l1_entity_cache.py`, `l1_parser.py` — reuse only). vis-network for `graph.html` (ADR-010). React Flow for VS Code Webview (ADR-010; phaseable). OpenTelemetry via existing telemetry paths.

**Storage**: FalkorDB L1 nodes/edges (Confirmed EP-006). Freshness / staleness metadata storage remains **Proposed** (database-schema §6) — do not invent a Confirmed table.

**Testing**: pytest (orchestrator unit/integration/contract/opt-in perf). Extension vitest for Webview/staleness DX where applicable. Blast latency/accuracy are validation targets until harnesses execute.

**Target Platform**: Local/VPC Docker Compose POC with existing FalkorDB + API. Extension Webview for IDE surfaces.

**Project Type**: FastAPI orchestrator + VS Code extension in monorepo. CLI not required by these stories.

**Performance Goals**: Validation targets only — blast p95 `<2s` @ 3-hop / 10k nodes (BRD §10); affected-tests accuracy `>95%` where harness applies (BRD §12). No pass claim without executed evidence.

**Constraints**: Reuse EP-006 L1; IgnorePolicy / no source-byte exfil on blast/graph payloads; FastAPI owns policy; OQ-15 owners Proposed `owners: []` only; do not invent Confirmed risk scoring, `db_tables`/`tests_to_run` linkage, graph.html auth, or freshness threshold.

**Scale/Scope**: US-018 (P1), US-019 (P1), US-020 (P2, phaseable), US-027 (P2). Excludes EP-013 OKF, EP-008 L4, EP-010 L2, EP-011 L6, L1 redesign, EP-009 PR bot beyond blast fields.

## ContextOS Technical Impact

**Affected Layers**:

| Layer | Plan impact |
|---|---|
| L1 | **Affected.** Blast traversal, graph viz payloads, staleness signaling over EP-006 evidence. |
| L5 | Dependency only — existing `POST /context` carries `blast_radius`; no L5 search redesign. |
| L3 | Dependency only — no Serena contract change. |
| L2 / L4 / L6 | **N/A** — EP-010 / EP-008 / EP-011 explicitly excluded. |

**Affected Surfaces**:

| Surface | Plan impact |
|---|---|
| FastAPI | **Affected.** New Confirmed routes `GET /blast`, `GET /graph.html`; V1 `blast_radius` populate; policy owner. |
| VS Code extension | **Affected** for US-020/US-027 (phaseable after FastAPI). |
| MCP | Thin pass-through only — no blast/graph policy. |
| CLI / GitHub Action | N/A for these stories. |

**Data Stores / Services**: FalkorDB (read/query for IMPORTS and structural neighbors). Process-local EP-006 entity cache may inform freshness revision awareness (**Proposed** reuse); no new Confirmed store schema.

**Privacy / Security Controls**: Reuse IgnorePolicy; blast/graph payloads are metadata/path/revision only — no full source bodies. Sanitize Webview messages (Constitution III). `graph.html` auth remains **NEEDS CLARIFICATION**.

**Observability**: Blast query latency, hop depth, node counts, graph.html serve timing, staleness badge state — non-sensitive attributes only. Exact attribute names **Proposed**.

**Measurable Intelligence Claims**: SC-001 latency and SC-002 accuracy require agreed fixtures + executed harnesses; plan defines measurement method, not pass results.

## Constitution Check

| Gate | Status | Evidence / mitigation |
|---|---|---|
| I — Evidence-first | Pass | FR-001–FR-009 mapped below; OQ-15 / auth / threshold / scoring labeled NEEDS CLARIFICATION or Missing Evidence. |
| II — Six-layer integrity | Pass | L1 delivery only; L5/L3 dependencies; L2/L4/L6 excluded. |
| III — Privacy/security | Pass with obligations | No source-byte exfil; IgnorePolicy; Webview sanitize; no invented auth. |
| IV — Measurable claims | Conditional | p95/accuracy are validation targets with harness plan; no pass assertion until execution. |
| V — Surface boundaries | Pass | FastAPI owns blast/graph/policy; MCP thin; extension presents FastAPI data only. |
| Roadmap governance | Pass | V1 L1 blast/viz; does not pull V2 L2/L6 or L4 product. |

**Post-design re-check**: Plan reuses EP-006 store/parser boundary; adds Confirmed Appendix D routes only; phases US-020 without dropping epic scope. No constitution violation.

## Project Structure

### Documentation

```text
specs/ep-007-l1-blast-visualization/
├── spec.md
├── plan.md
├── tasks.md                 # task-generator (not this artifact)
├── validation-report.md
└── review-report.md         # after implementation + tests
```

### Source Code (Confirmed / Proposed touchpoints)

```text
services/orchestrator/
├── app/
│   ├── api/                 # Proposed: blast.py, graph.py (+ schemas); extend context.py
│   ├── services/            # Proposed: l1_blast.py (or equivalent); reuse l1_graph / structural_query / entity_cache
│   ├── adapters/falkordb_store.py   # reuse; Proposed read/query helpers only — no schema redesign
│   ├── security/ignore_policy.py    # reuse
│   ├── main.py              # register blast/graph routers
│   └── telemetry/           # extend with blast/graph timings (Proposed attrs)
└── tests/
    ├── unit/ integration/ contract/
    └── perf/                # opt-in blast latency + accuracy harnesses

clients/vscode/              # US-020 / US-027 (Phase 3)
├── src/                     # Proposed Webview panel + API client for blast/graph + staleness UX
└── tests/

clients/mcp/                 # regression only — remain thin; no blast policy
```

**Structure Decision**: Follow `api → service → adapter → FalkorDB` (implementation-guidelines). Do not redesign `l1_parser.py` or EP-006 persist labels/edges.

## Complexity Tracking

Not applicable. No constitution violation. US-020 phasing is delivery sequencing, not architectural complexity debt.

## Technical Approach

### Confirmed architecture (cite — do not redesign)

| Prerequisite | Reuse boundary |
|---|---|
| EP-006 L1 | `specs/ep-006-l1-structural-graph/`; FalkorDB `File→Module→Class→Method→Call` + `IMPORTS` |
| Store / services | `falkordb_store.py`, `l1_graph.py`, `l1_structural_query.py`, `l1_entity_cache.py` |
| Parser | `l1_parser.py` — **out of scope** for redesign |
| Contracts | api-contract §2.3–2.5; ADR-004; ADR-010; database-schema §3 blast logical outputs |
| Context field | Existing `blast_radius` on `POST /context` (empty/null MVP **Proposed**; V1 populate is EP-007) |

### Proposed implementation — US-018 (P1)

1. Add FastAPI-owned blast service that resolves `repo` + `file_name` against EP-006 revision-scoped FalkorDB graph (path / File identity matching **Proposed** normalization consistent with EP-006 `source_path` / entity IDs).
2. Traverse reverse/forward `IMPORTS` (and Confirmed structural neighbors as needed) for `direct_dependents` (1-hop) and `transitive` (bounded N-hop; BRD pattern `IMPORTS*1..3` for latency target context).
3. Return Confirmed fields: `direct_dependents`, `transitive`, `db_tables`, `risk` ∈ `{HIGH,MEDIUM,LOW}`, `tests_to_run`. Include **Proposed** `owners: []` only (OQ-15 — no Confirmed owners schema).
4. Population rules for `db_tables` / `tests_to_run` / risk scoring remain partially Missing Evidence: return Confirmed fields with **Proposed** conservative L1-only heuristics (e.g. empty arrays or path-derived test candidates) without inventing L2 SQL or ownership models. Document heuristic as Proposed in validation report.
5. Wire `POST /context` to populate `blast_radius` when blast intent applies (replace EP-006 `blast_declined` empty behavior for V1). Non-blast asks keep prior L5/L1 enrichment behavior.
6. Errors: Proposed `404` unknown repo/file; Proposed `501` only if capability gated pre-delivery — do not invent new Confirmed HTTP envelopes.
7. MCP: no new ownership; any Ask path that surfaces blast does so via FastAPI response only.

### Proposed implementation — US-019 (P1)

1. Serve Confirmed `GET /graph.html?repo=` as HTML + vis-network over file nodes and `IMPORTS` edges from FalkorDB.
2. Visual defaults (Confirmed): physics off; arrows; node `#64748b`; background `#0f172a`; interactive depth 1–5.
3. Payload to the page must be structural metadata (paths/ids/edges) — no source bodies; respect IgnorePolicy for any server-side graph serialization.
4. Auth/embedding for Webview: **NEEDS CLARIFICATION** — local same-origin/trusted-client draft is non-blocking; do not claim Confirmed auth.

### Proposed implementation — US-020 (P2, phaseable)

1. After FastAPI blast/graph contracts exist, add VS Code React Flow Webview panel consuming FastAPI data (ADR-010).
2. Sanitize Webview↔extension messages; no client-side blast computation or IgnorePolicy bypass (`no_client_policy_bypass` regression pattern).
3. Surface US-027 staleness in panel UX when freshness metadata indicates drift.
4. Keep in `tasks.md` even if sequenced after Phase 1–2 API delivery.

### Proposed implementation — US-027 (P2)

1. Expose or reuse available freshness signals (e.g. index_revision, last index timestamps from existing index flows) as **Proposed** metadata to UI — do not invent Confirmed DB table.
2. Show clear staleness badge/warning on graph/blast/search developer surfaces when drift indicated; clear after delta/full index restores freshness.
3. Numeric threshold: **NEEDS CLARIFICATION** — implement presence/clear of warning behind a configurable Proposed threshold or boolean flag without asserting a Confirmed constant.

### Explicit exclusions

EP-013 OKF · EP-008 L4 · EP-010 L2 · EP-011 L6 · L1 parser/index redesign · inventing Confirmed owners / auth / risk algorithm / freshness threshold.

## Architecture Impact

| Area | Impact |
|---|---|
| Frontend | **Affected** for US-020/US-027 (React Flow Webview + staleness). Lean notes only — no full `docs/design` suite. `graph.html` is API-served HTML (US-019), not a separate design system. |
| Backend | **Affected.** New blast/graph routers + blast service; extend `context` for V1 `blast_radius`. |
| Database | **Read path** on existing FalkorDB L1. No Confirmed new labels required for MVP blast; Test/Owner/DbTable remain Missing Evidence — do not invent. |
| Infrastructure | Reuse existing Compose FalkorDB. No new service required. |
| AI Components | None. Local structural traversal only. |

## Components

| Component | Action | Boundary |
|---|---|---|
| Proposed `app/api/blast.py` + schemas | `GET /blast/{file_name}?repo=` | Confirmed route; FR-08 fields |
| Proposed `app/api/graph.py` (or static HTML route) | `GET /graph.html?repo=` | Confirmed vis-network contract |
| Proposed `app/services/l1_blast.py` | Traversal + response assembly | Reuse FalkorDB; no parser redesign |
| `app/api/context.py` / schemas | Populate `blast_radius` in V1 | Existing field |
| `app/adapters/falkordb_store.py` | Proposed read/query helpers | No persist schema change |
| EP-006 `l1_structural_query.py` | Replace/adjust `blast_declined` for V1 populate path | Do not break non-blast L1 enrichment |
| `app/main.py` | Register routers; update description | Confirmed Appendix D routes |
| `app/security/ignore_policy.py` | Reuse — no bypass | FR-009 |
| Telemetry | Blast/graph timings | Proposed attributes |
| `clients/vscode` | React Flow panel + staleness UX | Phase 3; FastAPI-owned data |
| `clients/mcp` | Regression only | Thin client |
| Tests + harnesses | Contract, privacy, latency, accuracy | Required before claims |

## Data Model Changes

| Change | Status |
|---|---|
| New FalkorDB labels/edges for blast | **Not required** for Confirmed FR-08 field presence if L1-only heuristics + empty arrays are used |
| Test / Owner / DbTable nodes | Missing Evidence — **do not invent** Confirmed schema |
| Freshness metadata store | **Proposed** (database-schema §6); may derive from existing `index_revision` / index response timing |
| Blast response document | Confirmed fields + Proposed `owners: []` |
| Migration | None relational; repos need prior EP-006 L1 index |

## API Design

| Endpoint | Plan |
|---|---|
| `GET /blast/{file_name}?repo=` | **New Confirmed.** Response: `direct_dependents`, `transitive`, `db_tables`, `risk`, `tests_to_run`; Proposed `owners: []`. Latency target p95 `<2s` @ 3-hop/10k (validation). Proposed statuses `200` / `404` / `501`. |
| `GET /graph.html?repo=` | **New Confirmed.** `text/html` vis-network; Proposed `404` unknown repo. Auth **NEEDS CLARIFICATION**. |
| `POST /context` | **No new field.** Populate existing `blast_radius` when applicable (V1). |
| MCP / CLI | No new Confirmed blast routes required. |

**Validation**: path/repo non-empty; unknown entity → Proposed 404. **Error handling**: degrade without inventing Confirmed error schemas beyond api-contract Proposed codes.

## UI / UX Changes

| Surface | Notes |
|---|---|
| `graph.html` | Confirmed visual defaults + depth 1–5; lean API-served page — no full design suite. |
| VS Code React Flow panel | US-020; phaseable after API; sanitize IPC; optional staleness badge. |
| Staleness badge | US-027 on graph/blast/search DX surfaces; threshold NEEDS CLARIFICATION. |
| Accessibility | Not evidenced — no invented numeric a11y targets. |

## Security Considerations

| Topic | Plan |
|---|---|
| Authn/Authz | RBAC remains platform requirement; `graph.html` embedding auth **NEEDS CLARIFICATION**. |
| Input validation | Validate `repo` / `file_name`; bound hop depth. |
| Sensitive data / exfil | No full source in blast/graph payloads; IgnorePolicy on any file inclusion path. |
| Webview | Sanitize messages and backend responses (Constitution III). |
| Secrets | No new secret storage. |
| Risks | Client bypass of policy; over-broad graph serialization — mitigate with FastAPI ownership + tests. |

## Performance Considerations

| Topic | Plan |
|---|---|
| Blast latency | Bound hops; Prefer Cypher-style IMPORTS traversal (database-schema §3 pattern); instrument p50/p95. |
| Scale target | Opt-in harness: synthetic or fixture graph ≈10k nodes, 3-hop queries; measure against `<2s` p95. |
| graph.html | Cap initial payload / depth slider 1–5; avoid shipping source text. |
| Caching | May reuse EP-006 revision-scoped cache for entity lookup (**Proposed**); FalkorDB remains SoT. |
| Accuracy | Opt-in harness: fixture with expected affected tests; measure precision/recall vs `>95%` where rules apply — report skips if linkage rules Incomplete. |

## Testing Strategy

### Unit Tests

- Blast traversal: 1-hop vs transitive; depth bounds; empty graph; unknown file.
- Response shape: Confirmed fields present; `owners` Proposed empty-only; risk enum.
- No source-byte fields in payloads; excluded paths never appear.
- graph.html builder: visual defaults, IMPORTS-only edges, depth clamp 1–5.
- Staleness signal: warn when Proposed freshness flag/revision drift set; clear when restored.

### Integration Tests

- Index EP-006 fixture → `GET /blast` returns Confirmed fields from FalkorDB.
- `GET /graph.html?repo=` returns HTML/vis-network for indexed repo; Proposed 404 for unknown.
- `POST /context` blast-intent populates `blast_radius` (not permanently `{}` for applicable V1 cases).
- Unavailable FalkorDB degrades per Proposed status behavior without new Confirmed envelopes.

### End-to-End Tests

- Compose smoke: API + FalkorDB serve blast + graph.html for fixture.
- Extension (Phase 3): Webview opens against FastAPI mocks; no policy bypass.

### Acceptance Tests

- US-018 / SC-003: Confirmed blast fields on fixture.
- US-019 / SC-003: Confirmed visual/depth contracts.
- US-020 / SC-005: React Flow interacts with FastAPI data (may follow API phases).
- US-027 / SC-004: badge appear/clear; threshold remains unlabeled Confirmed.

### Regression Tests

- EP-006 index/`graph_nodes`/structural enrichment non-blast paths.
- Context contract field set unchanged except `blast_radius` population behavior.
- MCP thin-client / no client policy bypass.
- OKF paths untouched (EP-013 out of scope).

### Performance and evaluation harnesses (measurable validation)

| Harness | Method | Target | Claim rule |
|---|---|---|---|
| Blast latency | Opt-in pytest/perf: 3-hop queries on ~10k-node L1 graph; record machine, revision, cold/warm, p50/p95 | p95 `<2s` (BRD §10) | Report measurement; pass only with executed evidence |
| Blast accuracy | Opt-in fixture with expected `tests_to_run` / affected set; compute correct-predicted rate | `>95%` where harness rules apply (BRD §12) | Skip or partial if linkage Missing Evidence; no silent pass |
| Demo context | Optional observational <5s demo blast | BRD demo note | Not a separate Confirmed API SLA |

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Incomplete `db_tables` / `tests_to_run` / risk scoring evidence | Hollow Confirmed fields or false accuracy claims | Return fields with Proposed L1-only heuristics; harness documents applicability; no invented L2 |
| OQ-15 owners pressure | Premature Confirmed schema | Ship Proposed `owners: []` only |
| graph.html auth unclear | Embedding/security gap | Local trusted draft; block Confirmed auth claims; track OQ |
| Freshness threshold unknown | Inconsistent badge UX | Boolean/revision drift signal first; configurable Proposed threshold |
| US-020 slips | Epic incomplete | Keep tasks; phase after API; SC-005 allows sequence |
| Large graph payload latency | Miss p95 | Bound depth, project file-level IMPORTS, instrument harness |
| Client reimplements blast | Constitution V violation | Extension/MCP regression tests |

## Dependencies

| Dependency | Relationship |
|---|---|
| EP-006 L1 | **Prerequisite on main** — FalkorDB graph + services cited above |
| EP-001 / EP-005 | IgnorePolicy, index, health, privacy baselines |
| EP-004 | VS Code shell for US-020/US-027 |
| EP-013 OKF | On main — **out of scope** (do not modify) |
| ADR-010 / api-contract §2.4–2.5 | Confirmed viz and blast contracts |
| OQ-15 | Open — owners Proposed only |

## Implementation Phases

### Phase 0 — Foundation

Confirm EP-006 fixture availability; agree blast/graph OpenAPI sketches against api-contract; define Proposed heuristics for incomplete linkage fields; sketch opt-in harness fixtures (10k-node / accuracy).

### Phase 1 — US-018 (P1) MVP for epic

Blast service + `GET /blast`; V1 `POST /context` `blast_radius` populate; privacy/contract tests; start latency harness scaffolding.

### Phase 2 — US-019 (P1)

`GET /graph.html` vis-network; depth 1–5; no-exfil payload tests; Compose smoke.

### Phase 3 — US-020 (P2, may follow Phase 1–2)

React Flow Webview panel over FastAPI blast/graph; IPC sanitize; wire staleness display.

### Phase 4 — US-027 (P2) + polish

Staleness signaling across graph/blast/search DX; clear-on-reindex; execute/document latency + accuracy harness results in validation-report (no pass without evidence). Cross-cut: telemetry, MCP regression, OKF non-touch verification.

## Evidence Reviewed

- `specs/ep-007-l1-blast-visualization/spec.md`
- `specs/ep-006-l1-structural-graph/spec.md` + `plan.md` (prerequisite style/reuse)
- `.specify/memory/constitution.md`; `.specify/templates/plan-template.md`
- `.cursor/rules/lean-spec-kit-artifacts.mdc`
- `docs/architecture/api-contract.md` §2.3–2.5; ADR-004; ADR-010; database-schema §3/§6; architecture-overview; tech-stack; implementation-guidelines
- Current orchestrator: `main.py`, `context.py`, `l1_structural_query.py` (`blast_declined`), `falkordb_store.py`, EP-006 L1 services
- Graphify query: EP-007 blast L1 FalkorDB graph.html React Flow

## Planning Assumptions

| ID | Assumption | Status |
|---|---|---|
| A-001 | EP-006 L1 data available via existing index/persist for eligible repos. | Non-blocking (EP-006 on main) |
| A-002 | Some freshness signal (revision/timestamp/flag) can drive US-027 without Confirmed metadata table. | Non-blocking for signaling intent |
| A-003 | US-020 may ship after FastAPI blast/graph without leaving epic. | Non-blocking (spec phaseability) |
| A-004 | Proposed L1-only heuristics for empty/partial `db_tables`/`tests_to_run`/risk are acceptable until linkage clarified. | Non-blocking for field presence; blocks full accuracy claims |

## Open Questions

| ID | Status | Blocking impact |
|---|---|---|
| **OQ-15** owners JSON shape | **NEEDS CLARIFICATION** — Proposed `owners: []` only | Blocks Confirmed owners contract only |
| **graph.html auth** | **NEEDS CLARIFICATION** | Blocks Confirmed auth; local viz draft OK |
| **Freshness threshold** | **NEEDS CLARIFICATION** | Blocks Confirmed numeric threshold |
| **db_tables / tests linkage** | Missing Evidence / partial | Blocks full accuracy claims |
| **Risk scoring** | Missing Evidence | Blocks scoring correctness claims |

## Requirement Coverage Matrix

| Requirement ID | Planned Implementation | Evidence | Status |
|---|---|---|---|
| FR-001 | `GET /blast` Confirmed FR-08 fields | api-contract §2.4; US-018 | Planned |
| FR-002 | Reuse EP-006 FalkorDB L1 IMPORTS/structural edges | EP-006; database-schema §3 | Planned |
| FR-003 | Proposed `owners: []` only (OQ-15) | api-contract owners note | Planned |
| FR-004 | V1 populate `POST /context.blast_radius` | api-contract §2.3 | Planned |
| FR-005 | `GET /graph.html` vis-network defaults + depth 1–5 | ADR-010; FR-09 | Planned |
| FR-006 | React Flow Webview (Phase 3) over FastAPI data | ADR-010; US-020 | Planned (phaseable) |
| FR-007 | Staleness badge appear/clear | US-027; BRD §13 | Planned |
| FR-008 | FastAPI owns blast/graph/policy; MCP thin | Constitution V | Planned |
| FR-009 | IgnorePolicy + no source-byte exfil on payloads | Constitution III; EP-006 FR-006/007 | Planned |
