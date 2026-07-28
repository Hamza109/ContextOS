# Feature Specification: EP-013 OKF Primary Knowledge Format

**Feature Branch**: `feature/ep-013-okf-primary-knowledge`  
**Created**: 2026-07-28  
**Status**: Spec Kit draft — ready for validation  
**Input**: User direction: "Use Google Open Knowledge Format (OKF) as primary knowledge representation, with vector embeddings as fallback." Spec-first approach; first OKF source is a generated local bundle from existing ContextOS artifacts.

## Evidence Classification

| Label | Meaning in this specification |
|---|---|
| **Confirmed** | Supported by the BRD, approved ADRs, architecture, or current repository evidence. |
| **Proposed** | A documented direction that is not a frozen product contract. Includes this user-directed OKF extension. |
| **Missing Evidence** | A required detail not established by available sources; it is not treated as a requirement. |

## Confirmed Baseline (unchanged)

- Confirmed retrieval path today: `POST /context` uses L5 hybrid BM25 + vector search with MMR, optional L3 enrichment, and EP-006 L1 structural enrichment inside `final_context`.
- Confirmed stores remain FalkorDB (L1) and Qdrant (L5 vectors).
- Confirmed public API shapes for `POST /index` and `POST /context` must not gain new Confirmed fields without product confirmation.
- Confirmed privacy defaults: `.gitignore`, secrets/build/deps/binaries excluded; no index-time external LLM exfiltration.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Generate an OKF knowledge bundle (Priority: P1)

**Story ID**: US-046 (Proposed new backlog story; not yet in `docs/backlog/user-stories.md`)

As a Staff Engineer, I want ContextOS to generate a portable OKF v0.2 knowledge bundle from eligible local architecture docs, Spec Kit artifacts, backlog evidence, and selected L1 metadata during indexing, so that curated SDLC knowledge is available in a human- and agent-readable graph of concepts.

**Why this priority**: Without a generated bundle there is no primary OKF representation to query before vector fallback.

**Independent Test**: Index a fixture that includes architecture/spec markdown and eligible code metadata; inspect the generated OKF directory for concept files with required frontmatter, provenance, and markdown links; prove excluded/secret paths never appear as concept sources.

**Acceptance Scenarios**:

1. **Given** an eligible local repository containing architecture docs and Spec Kit artifacts, **When** indexing runs through Confirmed `POST /index`, **Then** FastAPI generates or updates a repository-scoped OKF bundle of markdown concepts with YAML frontmatter conforming to OKF v0.2 `type` requirements.
2. **Given** eligible docs/specs and available L1 structural metadata, **When** the bundle is generated, **Then** concepts include provenance (`sources` / `generated`) and markdown links between related architecture, epic, and structural concepts without storing full source-code bodies.
3. **Given** policy-excluded paths (`.gitignore`, `.env`, secrets, dependency/build output, binaries), **When** OKF generation runs, **Then** those paths contribute neither concept bodies nor source references derived from excluded content.
4. **Given** OKF generation fails after L5/L1 work, **When** the index request completes, **Then** existing Confirmed index behavior is preserved (no new Confirmed HTTP semantics) and the failure is recorded in non-sensitive telemetry/trace notes.

---

### User Story 2 — Answer with OKF-first retrieval (Priority: P1)

**Story ID**: US-047 (Proposed)

As a Developer, I want `POST /context` to prefer OKF concept lookup and linked-concept expansion before BM25/vector retrieval, so that architecture and curated-knowledge questions return cited OKF evidence first.

**Why this priority**: This is the primary product behavior change requested by the user.

**Independent Test**: Seed a generated OKF bundle with known architecture concepts; ask a matching natural-language question through `POST /context` with embeddings disabled or empty; verify cited OKF evidence appears in `final_context` and metrics/trace note the OKF hit.

**Acceptance Scenarios**:

1. **Given** a repository with a generated OKF bundle containing a matching concept, **When** a Developer asks a supported knowledge/architecture question via `POST /context`, **Then** FastAPI appends cited OKF evidence to `final_context` before relying on vector embeddings.
2. **Given** an OKF hit, **When** related concepts are linked by markdown relationships, **Then** retrieval MAY expand a bounded set of linked concepts and MUST cite concept IDs/paths and provenance.
3. **Given** `contextos_ask` invokes `POST /context`, **When** OKF evidence is returned, **Then** MCP remains a stateless pass-through with no OKF/cache ownership.
4. **Given** an OKF miss or low-confidence match, **When** the same query continues, **Then** ContextOS falls through to L1 structural enrichment (when applicable) and L5 BM25/vector fallback without inventing OKF evidence.

---

### User Story 3 — Preserve vector embeddings as fallback (Priority: P1)

**Story ID**: US-048 (Proposed)

As a Developer, I want hybrid BM25 + vector search to remain available when OKF cannot confidently answer, so that fuzzy code/discovery questions still work.

**Why this priority**: Explicit user requirement; OKF must not remove L5 semantic search.

**Independent Test**: Index a code-only fixture with no matching OKF concepts for a semantic query; call `POST /context`; verify hybrid search still returns relevant files and packed context.

**Acceptance Scenarios**:

1. **Given** no confident OKF match, **When** a semantic code-discovery question is asked, **Then** existing hybrid BM25 + vector + MMR retrieval still produces `relevant_files` and packed `final_context`.
2. **Given** Qdrant/embedding degradation, **When** OKF has a confident hit, **Then** OKF evidence may still be returned; when both OKF and vector paths fail, existing degraded L5 pack behavior is preserved.
3. **Given** both OKF and vector evidence exist, **When** packing completes, **Then** the response shape remains Confirmed (`final_context`, `metrics`, `blast_radius`, `memory`, `relevant_files`, `is_real`) with OKF/vector status only inside `final_context` and/or `metrics.trace`.

### Edge Cases

- Empty or missing OKF bundle after index MUST NOT break Confirmed search; treat as OKF miss.
- Malformed OKF concept files MUST be skipped with counts only; consumers MUST tolerate unknown concept `type` values per OKF v0.2.
- Concept IDs are OKF paths without `.md`; they MUST be stable for the same source artifact identity and index revision.
- Attested Computation (`type: Attested Computation`) is **out of scope** for the first increment; reserve as optional later evidence for generated metrics.
- Blast-radius computation remains EP-007; OKF must not invent blast answers.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: FastAPI MUST generate or update a repository-scoped OKF v0.2 bundle during Confirmed `POST /index` after the existing ignore/no-exfiltration eligibility boundary. *(US-046; Proposed user-directed extension; OKF SPEC §3–§4)*
- **FR-002**: The first OKF source set MUST be generated from eligible local artifacts: `docs/architecture/`, `docs/backlog/user-stories.md`, `specs/*/{spec,plan,tasks,validation-report,review-report}.md`, and selected L1 structural metadata already produced by EP-006. *(US-046; user scope)*
- **FR-003**: Each generated concept MUST include required OKF frontmatter `type`, plus Proposed ContextOS fields for provenance (`sources` and/or `generated`), repository identity, and index revision; bodies MUST be metadata/summary oriented and MUST NOT duplicate full source-code bodies. *(US-046; OKF SPEC §4–§5; Constitution III)*
- **FR-004**: Concept relationships MUST be expressed with standard markdown links compatible with OKF graph consumption. *(US-046; OKF SPEC §2 Link, §4.2)*
- **FR-005**: `POST /context` MUST attempt OKF concept/entity/link lookup before BM25/vector fallback for eligible queries, then MAY apply existing L1 structural enrichment, then MUST fall back to existing L5 hybrid search on miss/low confidence. *(US-047, US-048; user scope; existing `POST /context`)*
- **FR-006**: OKF retrieval evidence MUST be appended only inside existing `final_context` and non-sensitive notes inside existing `metrics.trace`; no new Confirmed request/response field or endpoint is authorized. *(US-047; API contract §2.3; Constitution V)*
- **FR-007**: Vector embeddings and BM25 MUST remain installed fallback dependencies; EP-013 MUST NOT remove Qdrant indexing or hybrid search. *(US-048; BRD FR-02; ADR-014)*
- **FR-008**: FastAPI MUST own OKF generation, indexing, and query composition; MCP/CLI/VS Code MUST remain thin clients. *(Governance; Constitution V)*
- **FR-009**: OKF generation and retrieval MUST reuse Confirmed privacy controls: respect `.gitignore`; exclude `.env`, secrets, build outputs, dependency folders, and binaries; no index-time external LLM source exfiltration. *(US-046; Constitution III; EP-005)*
- **FR-010**: On OKF miss, stale revision, malformed bundle, or generator failure, ContextOS MUST preserve existing L5/L1 behavior and MUST NOT fabricate OKF concepts. *(US-047, US-048)*

### Key Entities

| Entity | Conceptual attributes / relationship | Evidence status |
|---|---|---|
| OKF bundle | Repository-scoped directory of markdown concepts; optional `index.md` / `log.md`. | Proposed; OKF SPEC §3 |
| OKF concept | Markdown file with required `type` frontmatter; Concept ID = path without `.md`. | Proposed; OKF SPEC §2–§4 |
| Concept link | Markdown link between concepts forming a traversable graph. | Proposed; OKF SPEC |
| Retrieval router | FastAPI composition order: OKF → L1 (existing) → L5 BM25/vector. | Proposed |
| Index result | Unchanged Confirmed fields `files_indexed`, `graph_nodes`, `embeddings`, `time_ms`. | Confirmed |

## ContextOS Impact *(mandatory for this project)*

### Affected Layers

| Layer | Impact | Evidence |
|---|---|---|
| **L1** | **Dependency / enrichment.** Consume selected L1 metadata into OKF concepts; do not replace FalkorDB. | EP-006; user scope |
| **L2** | **Adjacent Proposed.** Generated docs/spec concepts resemble curated multi-modal knowledge without external connectors. Full L2 (US-028..) remains V2. | BRD FR-14/15; roadmap governance |
| **L3** | **N/A / dependency only.** No Serena contract change. | Upstream EP-003 |
| **L4** | **N/A.** | User scope |
| **L5** | **Affected — Proposed retrieval precedence.** Pack/index remain upstream; hybrid search becomes fallback after OKF. | BRD FR-01/02; user scope |
| **L6** | **N/A** beyond future-compatible provenance notes. No persistent memory store. | BRD FR-16–18; user scope |

### Affected Surfaces

| Surface | Impact | Evidence |
|---|---|---|
| **FastAPI / API** | **Affected — Proposed.** Generate OKF on `POST /index`; compose OKF-first evidence on `POST /context` without new Confirmed fields. | API contract §2.2–§2.3 |
| **MCP** | **Dependency only.** Stateless pass-through of enriched `/context`. | Constitution V |
| **CLI / VS Code** | **N/A** for this Spec Kit increment. | User scope |
| **Visualization / blast** | **N/A.** Remain EP-007. | BRD FR-08/09 |

### Privacy And Security

- **Confirmed**: Existing ignore/no-exfil controls apply before OKF generation.
- **Proposed**: Generated concepts store metadata, summaries, and provenance only — not full source bodies.
- **Out of scope**: RBAC schema (OQ-01), external OKF catalog connectors, Attested Computation executors.

## Non-Functional Requirements

### Performance

- **Proposed scoped target**: OKF lookup for a warm local bundle SHOULD add low overhead relative to existing `/context` path; measure p50/p95 on a fixture harness. No BRD pass claim until executed.
- **Confirmed L5 target remains**: semantic search p95 <800ms @ 500k LOC where the L5 harness applies; OKF must not remove that path.
- **Missing Evidence**: No executed OKF latency/quality harness yet.

### Security

- FR-009 privacy controls are mandatory.
- Threat note: generated knowledge could over-claim if provenance is omitted — mitigated by required `sources`/`generated` and no fabricated concepts on miss.

### Reliability

- OKF miss/failure MUST degrade to existing L5/L1 paths (FR-010).
- Malformed concepts are skipped with counts; bundle remains partially usable.

## Success Criteria

- **SC-001**: Generated fixture bundle contains ≥1 concept per eligible architecture/spec source class with valid `type` frontmatter and provenance.
- **SC-002**: OKF-first query over known concepts returns cited OKF evidence with embeddings disabled or unused.
- **SC-003**: Semantic code query without OKF match still returns L5 hybrid results.
- **SC-004**: Excluded/secret paths never appear as OKF concept sources.
- **SC-005**: Public OpenAPI `/index` and `/context` Confirmed response properties remain unchanged.

## Assumptions

| ID | Assumption | Blocking? |
|---|---|---|
| A-OKF-1 | Google OKF v0.2 markdown+YAML frontmatter is the target interchange format. | Non-blocking once labeled Proposed |
| A-OKF-2 | First increment generates a local bundle under a Proposed cache/path (e.g. pack-cache sibling or repo-local `.contextos/okf/`) without a new Confirmed API field. | Non-blocking |
| A-OKF-3 | Epic ID EP-013 / stories US-046–US-048 are Proposed backlog extensions pending backlog sync. | Non-blocking for Spec Kit |
| A-OKF-4 | Roadmap: this feature is user-directed and may precede full V2 L2 connectors; it must not claim BRD L2 connector completion. | Non-blocking if labeled |

## Dependencies

- Upstream EP-001/EP-002 L5 pack + hybrid search.
- Upstream EP-005 privacy/health/consent.
- Upstream EP-006 L1 structural graph metadata (optional enrichment source).
- External reference: [OKF SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) v0.2.

## Out Of Scope

- Replacing FalkorDB or Qdrant.
- External OKF catalog connectors / multi-tenant exchange.
- New Confirmed public endpoints or response fields.
- UI graph viewer / `graph.html` / blast.
- Attested Computation executor/attester runtime.
- L6 governed memory pin/forget.
- Full V2 L2 connector auth (OQ-03).

## Open Questions

| ID | Question | Blocking for Spec Kit? | Affects |
|---|---|---|---|
| OQ-OKF-01 | Exact on-disk bundle root path and whether it is repo-local vs orchestrator cache. | Non-blocking if Proposed default chosen in plan | FR-001 |
| OQ-OKF-02 | Confidence threshold / matching algorithm for OKF hit vs miss. | Non-blocking if Proposed exact/token match first | FR-005 |
| OQ-OKF-03 | Whether `graph_nodes` or a Proposed metric should count OKF concepts (default: no Confirmed field change). | Non-blocking — default no | FR-006 |
| OQ-OKF-04 | Backlog promotion of EP-013 / US-046–US-048 into `docs/backlog/user-stories.md`. | Non-blocking for Spec Kit | Governance |

## Traceability

| Requirement | Stories | Source |
|---|---|---|
| FR-001–FR-004, FR-009 | US-046 | User direction; OKF SPEC; Constitution III |
| FR-005–FR-006, FR-008, FR-010 | US-047 | User direction; API contract §2.3; Constitution V |
| FR-007, FR-010 | US-048 | User direction; BRD FR-02; ADR-014 |
