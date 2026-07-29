# Feature Specification: EP-007 L1 Blast Radius & Visualization

**Feature Branch**: `feature/ep-007-l1-blast-visualization`  
**Created**: 2026-07-28  
**Status**: Draft  
**Input**: User description: "Deliver EP-007 only: US-018 blast radius, US-019 graph.html, US-020 VS Code React Flow panel, US-027 index/graph staleness signaling — reusing EP-006 L1; excluding OKF and L1 redesign."

## Evidence Classification

| Label | Meaning in this specification |
|---|---|
| **Confirmed** | Supported by the BRD, approved ADRs, architecture, or current repository evidence. |
| **Proposed** | A documented direction that is not a frozen product contract. |
| **Missing Evidence** | A required detail not established by available sources; it is not treated as a requirement. |

## Prerequisites (cite — do not redesign)

| Prerequisite | Boundary |
|---|---|
| **EP-006 L1 Structural Graph** (`specs/ep-006-l1-structural-graph/`) | On main. FalkorDB persist, tree-sitter generate, hot-entity cache, structural `/context` enrichment. Reuse L1 nodes/edges for blast and graph. Do **not** redesign indexing/parser. Cite orchestrator paths: `l1_graph.py`, `falkordb_store.py`, `l1_parser.py`, `l1_structural_query.py`, `l1_entity_cache.py`. |
| **EP-013 OKF** | On main. **OUT OF SCOPE** — do not touch OKF generate/retrieve or invent OKF changes. |

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Transitive blast radius analysis (Priority: P1)

As a Developer, I want transitive blast radius for a change (affected services, tests, owners, risk), so that I know what breaks before I merge.

**Why this priority**: US-018 is the core change-safety outcome (BO-03; FR-08) and the API foundation for visualization and staleness UX.

**Independent Test**: With an EP-006 L1-indexed fixture, call Confirmed `GET /blast/{file_name}?repo=` and verify Confirmed FR-08 fields; where applicable, verify `POST /context` returns a populated V1 `blast_radius` payload without inventing Confirmed owners schema.

**Acceptance Scenarios**:

1. **Given** an L1-indexed repository, **When** a Developer calls `GET /blast/{file_name}?repo=`, **Then** the response includes Confirmed fields `direct_dependents`, `transitive`, `db_tables`, `risk` in `{HIGH, MEDIUM, LOW}`, and `tests_to_run` per FR-08 / api-contract §2.4.
2. **Given** FR-08 prose requires owners, **When** the blast response is designed, **Then** owners appear only as **Proposed** `owners: []` pending OQ-15 — no Confirmed owners element schema is asserted.
3. **Given** a blast-relevant ask on an L1-indexed repo, **When** `POST /context` runs in V1, **Then** FastAPI populates the existing `blast_radius` response field when applicable (MVP empty/null remains **Proposed** baseline; V1 populate is the EP-007 obligation).
4. **Given** NFR conditions (3-hop, 10k nodes) and an agreed harness, **When** blast latency is measured, **Then** the observed p95 is evaluated against `<2s` (BRD §10); no pass claim is implied by this specification alone.
5. **Given** an agreed accuracy harness, **When** blast accuracy is evaluated, **Then** correct affected tests predicted is evaluated against `>95%` where the harness applies (BRD §12); no pass claim is implied until harness execution.
6. **Given** an unknown repo/file or pre-V1 capability, **When** blast is requested, **Then** behavior follows documented Proposed status codes (`404` / `501`) without inventing new Confirmed HTTP semantics.

---

### User Story 2 — Interactive `graph.html` visualization (Priority: P1)

As a Developer, I want an interactive dependency graph page for a repo, so that I can explore structural relationships visually.

**Why this priority**: US-019 makes L1 actionable for design/maintenance (FR-09; BO-04) and is the Confirmed FastAPI visualization surface.

**Independent Test**: Open Confirmed `GET /graph.html?repo=` against an L1-indexed fixture and verify vis-network rendering contracts (nodes=files, edges=IMPORTS, visual defaults, depth 1–5).

**Acceptance Scenarios**:

1. **Given** an L1-indexed repository, **When** a Developer opens `GET /graph.html?repo=`, **Then** they receive an interactive vis-network graph with nodes as files and edges as IMPORTS (FR-09; ADR-010; BRD §14).
2. **Given** BRD visual guidance, **When** the page renders, **Then** physics is disabled, arrows are shown, node color `#64748b`, and background `#0f172a`.
3. **Given** depth exploration needs, **When** viewing a symbol/service subgraph, **Then** interactive depth 1–5 is supported per FR-09.
4. **Given** an unknown repository, **When** `graph.html` is requested, **Then** behavior follows Proposed `404` without inventing Confirmed auth semantics (auth for HTML embedding remains **NEEDS CLARIFICATION**).

---

### User Story 3 — VS Code React Flow graph / blast panel (Priority: P2)

As a Developer, I want blast radius and dependency views inside VS Code via React Flow Webviews, so that I can inspect risk without leaving the IDE.

**Why this priority**: US-020 is a V1 IDE visualization deliverable (BRD §5, §15; ADR-010). It depends on US-018/US-019 data and may be phased after FastAPI blast/graph surfaces land, but remains in epic scope.

**Independent Test**: With V1 extension features enabled and L1/blast/graph data available, open the ContextOS graph/blast Webview panel and verify React Flow interaction over FastAPI-owned data without client-side policy bypass.

**Acceptance Scenarios**:

1. **Given** V1 extension features enabled and L1 data available, **When** a Developer opens the ContextOS graph/blast panel, **Then** they can interact with dependency/blast visualization powered by React Flow in a VS Code Webview (ADR-010).
2. **Given** graph data may be stale after large PRs, **When** staleness is known, **Then** the panel UX can surface staleness (paired with US-027).
3. **Given** Webview IPC, **When** messages and backend responses are exchanged, **Then** they are sanitized per Constitution III; the extension does not silently bypass FastAPI validation, ignore policy, or invent blast computation.

**Phaseability note (non-blocking)**: FastAPI `GET /blast` and `GET /graph.html` may ship first; the React Flow panel remains an epic deliverable and may follow once those contracts are available.

---

### User Story 4 — Index / graph staleness signaling (Priority: P2)

As a Developer, I want a staleness badge when the graph/index may have drifted after large PRs, so that I do not trust outdated blast-radius results blindly.

**Why this priority**: US-027 mitigates BRD §13 graph index drift risk and pairs with blast/graph surfaces.

**Independent Test**: Show graph/blast/search UI when freshness metadata indicates possible drift and verify a clear staleness warning; after delta indexing restores freshness, verify the warning clears. Exact freshness threshold remains **NEEDS CLARIFICATION**.

**Acceptance Scenarios**:

1. **Given** index freshness metadata is available, **When** graph/blast/search UI is shown and data may be stale, **Then** a staleness badge (or equivalent clear warning) is displayed.
2. **Given** delta indexing completes and freshness is restored, **When** the UI refreshes, **Then** the staleness warning clears.
3. **Given** the freshness threshold is not evidenced, **When** implementing signaling, **Then** the product does not invent a Confirmed numeric threshold; threshold choice is tracked as Open Question / **NEEDS CLARIFICATION**.

### Edge Cases

- Policy-excluded paths (`.gitignore`, `.env`, secrets, dependency folders, build outputs, binaries) MUST NOT contribute source bytes to blast or graph payloads; IgnorePolicy remains FastAPI-owned.
- Blast/graph responses MUST NOT exfiltrate full source bodies; provenance remains metadata-oriented (repo, path, revision, structural identity) consistent with EP-006 FR-007.
- `db_tables` and `tests_to_run` are Confirmed response fields; population rules for table linkage and test linkage remain partially Missing Evidence — do not invent L2/SQL or L4 contracts.
- Risk scoring algorithm for `HIGH|MEDIUM|LOW` is Missing Evidence beyond the Confirmed enum.
- Unknown repo/file, empty graph, or unavailable FalkorDB degrade without inventing Confirmed error schemas beyond api-contract Proposed codes.
- OQ-15 owners shape unresolved: only Proposed `owners: []` until confirmed.
- Auth for embedding `graph.html` in Webviews is **NEEDS CLARIFICATION**.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: ContextOS MUST compute transitive blast radius for a named file in a repository via Confirmed `GET /blast/{file_name}?repo=` and return Confirmed fields `direct_dependents`, `transitive`, `db_tables`, `risk` ∈ `{HIGH, MEDIUM, LOW}`, and `tests_to_run`. *(US-018; BRD FR-08; api-contract §2.4)*
- **FR-002**: Blast computation MUST reuse EP-006 FalkorDB L1 structural nodes/edges (including IMPORTS traversals); it MUST NOT redesign L1 indexing or the tree-sitter parser. *(US-018; EP-006 prerequisite; database-schema §3)*
- **FR-003**: Until OQ-15 is resolved, blast responses MAY include **Proposed** `owners: []` only; the system MUST NOT treat any owners element schema as Confirmed. *(US-018; OQ-15; api-contract §2.4)*
- **FR-004**: In V1, FastAPI MUST populate the existing `POST /context` response field `blast_radius` when blast analysis applies; MVP empty/null behavior remains the documented **Proposed** baseline, not a permanent V1 outcome. *(US-018; api-contract §2.3)*
- **FR-005**: ContextOS MUST serve Confirmed `GET /graph.html?repo=` as an interactive vis-network page with file nodes, IMPORTS edges, physics disabled, arrows, node color `#64748b`, background `#0f172a`, and interactive depth 1–5. *(US-019; BRD FR-09, §14; ADR-010; api-contract §2.5)*
- **FR-006**: The VS Code extension MUST provide a React Flow Webview panel for dependency/blast visualization that consumes FastAPI-owned blast/graph data and sanitizes Webview messages. *(US-020; BRD FR-09, §15; ADR-010; Constitution III, V)*
- **FR-007**: Graph/blast/search developer surfaces MUST display a clear staleness badge (or equivalent warning) when index/graph freshness metadata indicates possible drift, and MUST clear the warning when freshness is restored after delta indexing. *(US-027; BRD §13)*
- **FR-008**: FastAPI MUST own blast computation, graph.html serving, ignore/exfiltration policy, and OpenAPI contracts; MCP and other clients MUST remain thin pass-through consumers and MUST NOT reimplement blast/graph policy. *(Governance; Constitution V)*
- **FR-009**: Blast and graph payloads MUST NOT include full source-byte exfiltration; indexing/query paths MUST continue to respect IgnorePolicy (`.gitignore`, `.env`, secrets, build outputs, dependency folders, binaries). *(Governance; Constitution III; EP-006 FR-006/FR-007)*

### Key Entities

| Entity | Conceptual attributes / relationship | Evidence status |
|---|---|---|
| Blast result | `direct_dependents`, `transitive`, `db_tables`, `risk`, `tests_to_run`; optional Proposed `owners` | Confirmed FR-08 fields; owners Proposed / OQ-15 |
| Graph visualization document | HTML vis-network view over file nodes and IMPORTS edges; depth 1–5 | Confirmed FR-09 / §14 |
| IDE graph/blast panel | React Flow Webview presentation over FastAPI blast/graph data | Confirmed ADR-010 / US-020 |
| Freshness / staleness signal | Metadata indicating possible index/graph drift; badge clear on restore | Confirmed mitigation intent (BRD §13); threshold Missing Evidence |
| L1 structural node/edge | EP-006 File→Module→Class→Method→Call and IMPORTS | Confirmed prerequisite — reuse only |

## ContextOS Impact *(mandatory for this project)*

### Affected Layers

| Layer | Impact | Evidence |
|---|---|---|
| **L1 Structural Knowledge Graphs** | **Affected — Confirmed.** Blast radius, dependency visualization, staleness signaling over L1 evidence. | BRD §5 L1, FR-08, FR-09; §10; §13 |
| **L2 Multi-modal Project Graphs** | **N/A.** No multi-modal ingestion or linking; do not pull EP-010. | User scope |
| **L3 Symbol & LSP Navigation** | **Dependency only.** Existing L3 may coexist; no Serena contract change. | User scope |
| **L4 Context Compression** | **N/A.** Do not pull EP-008. | User scope |
| **L5 Context Packing & Semantic Search** | **Dependency only.** Existing `POST /context` / index paths may carry `blast_radius` and staleness UX; L5 search not re-specified. | api-contract §2.3 |
| **L6 Persistent Agent Memory** | **N/A.** Do not pull EP-011. | User scope |

### Affected Surfaces

| Surface | Impact | Evidence |
|---|---|---|
| **FastAPI / API** | **Affected — Confirmed.** Owns `GET /blast/{file_name}`, `GET /graph.html?repo=`, V1 `blast_radius` population on `POST /context`, and policy. | api-contract §2.3–2.5; Constitution V |
| **MCP integration** | **Dependency only.** Thin client; no blast/graph state or policy ownership. | Constitution V |
| **CLI** | **N/A / optional consumer.** No new CLI contract required by these stories. | User stories US-018–027 |
| **VS Code extension** | **Affected — Confirmed for US-020/US-027.** React Flow Webview + staleness badge UX. | US-020, US-027; ADR-010 |
| **Webview / dashboard / visualization** | **Affected — Confirmed.** `graph.html` (vis-network) and IDE React Flow panel. | FR-09; ADR-010 |
| **GitHub Action / CI** | **N/A.** | User scope excludes it |

### Privacy And Security

- **Confirmed**: IgnorePolicy and no source-byte exfiltration apply to blast/graph payloads (Constitution III).
- **Confirmed**: Webview messages and backend responses MUST be sanitized (Constitution III; US-020 notes).
- **Confirmed governance, out of scope for redesign**: RBAC per repo path remains a platform requirement; concrete auth for `graph.html` embedding is **NEEDS CLARIFICATION** (api-contract §2.5).
- **Confirmed**: Query-time external LLM use still requires consent/configuration; blast/graph themselves are local structural analysis over FalkorDB metadata.

## Non-Functional Requirements

### Performance

- **Confirmed target, not a pass claim**: Blast-radius graph query p95 `<2s` for 3-hop / 10k nodes (BRD §10; api-contract §2.4).
- **Demo context (not a separate Confirmed API SLA)**: BRD also references <5 sec demo blast; measurement remains harness-bound.
- **Missing Evidence**: No verified EP-007 harness result yet supports a latency pass assertion.

### Security

- FR-009 ignore/exfiltration controls apply.
- `graph.html` auth/embedding model is **NEEDS CLARIFICATION** — do not invent Confirmed auth.
- Webview sanitization required (FR-006).

### Reliability

- Unavailable L1/FalkorDB or unknown repo/file MUST degrade via documented Proposed status behavior without inventing new Confirmed error contracts.
- Staleness signaling depends on freshness metadata; storage of freshness flags is **Proposed** in database-schema §6 — do not invent a Confirmed table schema here.

### Accessibility

- Not evidenced for `graph.html` or React Flow panel beyond general IDE usability; no invented a11y numeric targets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 — Validation target, not achieved**: With an agreed blast harness at 3-hop / 10k nodes, blast query p95 is measured against `<2s`. (BRD §10)
- **SC-002 — Validation target, not achieved**: With an agreed accuracy harness, correct affected tests predicted is measured against `>95%` where the harness applies. (BRD §12)
- **SC-003 — Functional acceptance**: Confirmed blast response fields and `graph.html` visual/depth contracts are demonstrable on an L1-indexed fixture.
- **SC-004 — UX acceptance**: Staleness warning appears when drift is indicated and clears when freshness is restored; threshold numeric value remains **NEEDS CLARIFICATION**.
- **SC-005 — Surface acceptance**: React Flow Webview panel interacts with FastAPI blast/graph data without client-owned policy (may be phased after FR-001/FR-005).

## Confirmed Facts

- EP-007 includes US-018, US-019, US-020, and US-027 only; V1 (not MVP).
- Confirmed blast route: `GET /blast/{file_name}?repo=` with FR-08 fields above; Confirmed graph route: `GET /graph.html?repo=`.
- ADR-010 Confirmed: vis-network for `graph.html`; React Flow for VS Code Webviews.
- EP-006 L1 on FalkorDB is the structural evidence source; blast/graph reuse it.
- `POST /context` includes `blast_radius` as V1 field (empty/null MVP **Proposed**).
- Blast NFR: p95 <2s @ 3-hop / 10k nodes; accuracy >95% where harness applies.
- FastAPI owns blast/graph policy; MCP stays thin.

## Assumptions

| ID | Assumption | Blocking? | Rationale |
|---|---|---|---|
| A-001 | EP-006 L1 graph data for eligible repos is available via existing index/persist paths. | Non-blocking | US-018/019 depend on US-017; EP-006 is on main. |
| A-002 | Freshness metadata of some form can be exposed to UI for US-027 even if storage remains Proposed. | Non-blocking for signaling intent | BRD §13; database-schema §6 Proposed |
| A-003 | US-020 may ship after FastAPI blast/graph surfaces without removing it from epic scope. | Non-blocking | Dependencies US-018, US-019; phaseability noted |

## Dependencies

| Dependency | Status | Boundary |
|---|---|---|
| EP-006 L1 Structural Graph | Prerequisite on main | Reuse FalkorDB L1; no parser/index redesign |
| EP-001 / EP-005 indexing & privacy | Upstream | IgnorePolicy, local index, health baselines |
| EP-004 CLI & VS Code surfaces | Upstream for IDE shell | Extend with React Flow panel + staleness UX only as specified |
| EP-013 OKF | On main — **out of scope** | Do not modify OKF generate/retrieve |
| OQ-15 | Open | Owners shape Proposed only |

## Out Of Scope

- EP-013 OKF generate/retrieve or any OKF contract changes.
- Redesign of L1 indexing, tree-sitter parsing, or hot-entity cache internals.
- EP-008 L4 compression; EP-010 L2 multi-modal; EP-011 L6 memory.
- EP-009 PR risk bot (owners/tests surfacing in PR workflows) beyond blast fields needed by US-018.
- Inventing Confirmed owners schema, risk scoring algorithm, `db_tables`/`tests_to_run` linkage rules, or `graph.html` auth model.
- New Confirmed HTTP endpoints beyond Appendix D blast/graph routes.
- Claiming NFR pass results without executed harnesses.

## Open Questions

| ID | Question | Status | Blocking impact |
|---|---|---|---|
| **OQ-15** | What is the Confirmed JSON shape for blast response `owners`? | **NEEDS CLARIFICATION** — Proposed `owners: []` only until resolved | Non-blocking for Confirmed FR-08 fields; blocks Confirmed owners contract |
| **graph.html auth** | What auth/embedding model applies when `graph.html` is embedded (e.g. Webview)? | **NEEDS CLARIFICATION** (api-contract §2.5) | Blocking for Confirmed auth design; non-blocking for local V1 viz draft if served same-origin to trusted clients |
| **Freshness threshold** | What exact freshness threshold triggers the staleness badge? | **NEEDS CLARIFICATION** — Not evidenced | Blocking for a Confirmed numeric threshold; non-blocking for presence/clear of a warning once metadata exists |
| **db_tables / tests linkage** | How are `db_tables` and `tests_to_run` populated from L1-only evidence? | Missing Evidence / partial clarification | Non-blocking for field presence; blocks claiming full linkage accuracy without harness rules |
| **Risk scoring** | How is `risk` HIGH\|MEDIUM\|LOW computed? | Missing Evidence | Non-blocking for enum presence; blocks scoring correctness claims |

## Requirement Traceability

| Requirement ID | Source | Evidence |
|---|---|---|
| FR-001 | US-018 | `docs/backlog/user-stories.md` US-018; BRD FR-08; `api-contract.md` §2.4 |
| FR-002 | US-018 + EP-006 prerequisite | `specs/ep-006-l1-structural-graph/`; `database-schema.md` §3; ADR-004 |
| FR-003 | US-018 / OQ-15 | Backlog OQ-15; `api-contract.md` §2.4 owners note |
| FR-004 | US-018 | `api-contract.md` §2.3 `blast_radius` V1; US-018 notes |
| FR-005 | US-019 | BRD FR-09, §14; ADR-010; `api-contract.md` §2.5 |
| FR-006 | US-020 | BRD FR-09, §15; ADR-010; Constitution III, V |
| FR-007 | US-027 | BRD §13; backlog US-027 |
| FR-008 | Governance | Constitution V; architecture-overview ownership |
| FR-009 | Governance + EP-006 | Constitution III; EP-006 FR-006/FR-007; IgnorePolicy |

## Specification Validation

- **Coverage**: FR-001–FR-009 are atomic and traceable; scenarios cover US-018, US-019, US-020, US-027.
- **Boundary check**: L1/FastAPI/VS Code viz affected; EP-006 reused; EP-013/OKF, L2/L4/L6, and L1 parser redesign excluded.
- **Evidence check**: Confirmed vs Proposed vs Missing Evidence labeled; OQ-15, graph.html auth, and freshness threshold are explicit Open Questions — no invented Confirmed contracts.
- **Blocker check**: Draft is ready for plan generation; Confirmed owners schema, auth, and freshness threshold remain clarification items (not silent assumptions).
