# Feature Specification: EP-001 L5 Repository Packing & Indexing

**Feature Branch**: `001-ep-001-l5-repository-packing-indexing`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "EP-001 — L5 Repository Packing & Indexing (US-001, US-002, US-011, US-012, US-016): enable local-first, privacy-respecting repo flatten/pack and embedding so teams can retrieve SDLC context without manual file pasting (BO-01, BO-04)."

**Stories Covered**: US-001, US-002, US-011, US-012, US-016

**Business Objectives**: BO-01, BO-04

**Source Evidence**: BRD FR-01; §6 IN SCOPE (auto/incremental indexing); §10 indexing NFRs / embedding / code access; §14–§15; Appendix C/D; ADR-003; ADR-012; api-contract `POST /index`; constitution I–V

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Repo Flattening & Packing (Priority: P1)

As a **Developer**, I want the system to flatten my repository into an LLM-optimized packed representation with token count pre-calculation, so that I can obtain usable repo context without manually concatenating files.

**Why this priority**: Foundational L5 packing capability (FR-01); unlocks subsequent embedding and MVP retrieval. Independently delivers pack value without requiring search UI.

**Independent Test**: Request packing/indexing for a local repository within the BRD pack scale (up to 500k LOC) via `POST /index` and verify an LLM-optimized packed representation (XML-oriented per FR-01) with token count pre-calculation and binary skip, available for later hybrid search and prompt assembly (EP-002).

**Acceptance Scenarios**:

1. **Given** a local repository within BRD-stated pack scale (up to 500k LOC), **When** indexing/packing is requested via the evidenced indexing path (`POST /index` or equivalent orchestrated pack), **Then** the system produces an LLM-optimized packed representation (XML-oriented per FR-01) with token count pre-calculation, skipping binaries as specified.
2. **Given** packing completes, **When** results are inspected, **Then** pack outputs are available for subsequent hybrid search and prompt assembly (consumers out of scope for this feature).
3. **Given** a repository containing binary artifacts, **When** packing runs, **Then** binaries are skipped from the packed representation.

---

### User Story 2 — Privacy-Respecting Local Embedding Index (Priority: P1)

As a **Security** stakeholder, I want repository chunks embedded locally into the vector store without sending source code to external LLM providers during indexing, so that indexing does not exfiltrate code.

**Why this priority**: Privacy NFR and local embedding foundation for semantic search without cloud embedding quota (BO-04; §10; ADR-003). Blocks trustworthy MVP indexing.

**Independent Test**: Index a repository via `POST /index` and verify local `all-MiniLM-L6-v2` (384-dim) embeddings are stored in Qdrant with response fields `files_indexed`, `embeddings`, `time_ms` (`graph_nodes` may be 0 until V1), and assert no source code is sent to an external LLM provider during indexing.

**Acceptance Scenarios**:

1. **Given** a repository is indexed, **When** embeddings are created, **Then** embeddings use local `all-MiniLM-L6-v2` (384-dim) into Qdrant and **no** source code is sent to an external LLM provider during indexing.
2. **Given** indexing completes, **When** `POST /index` response is returned, **Then** it includes evidenced fields `files_indexed`, `embeddings`, `time_ms` (and `graph_nodes` may be zero until V1).
3. **Given** indexing is in progress, **When** network/egress to external LLM providers is monitored, **Then** no repository source content is transmitted to those providers on the index path.

---

### User Story 3 — Auto-Index on Extension Install (Priority: P2)

As a **Developer**, I want the extension to auto-index the repository on install, so that Ask ContextOS works without a manual indexing ceremony.

**Why this priority**: Reduces MVP onboarding friction (BO-01; §10/§14). Depends on packing + embedding (US-001, US-002) but is independently testable as an install/activation trigger.

**Independent Test**: Install/activate the VS Code extension on a workspace and verify the repository is indexed into local MVP stores (Qdrant embeddings; graph nodes may be deferred to V1) via backend orchestration, with progress/cancellation owned by the extension surface.

**Acceptance Scenarios**:

1. **Given** the VS Code extension is installed on a workspace, **When** install/activation indexing runs, **Then** the repository is indexed into the local stores used for MVP (Qdrant embeddings; graph nodes may be deferred to V1).
2. **Given** BRD illustrative timing for small repos, **When** indexing ~200 files, **Then** experience aligns with BRD “10 sec for 200 files” illustrative target where hardware permits, without inventing a stricter global SLA beyond §10 monorepo targets.
3. **Given** auto-index is triggered from the extension, **When** indexing executes, **Then** orchestration and policy enforcement occur in the FastAPI backend (extension does not silently bypass indexing policy).

---

### User Story 4 — Incremental Re-Index on File Save (Priority: P2)

As a **Developer**, I want ContextOS to re-index on file save, so that search stays fresh as I edit.

**Why this priority**: Keeps retrieval trustworthy during active development and mitigates index drift (BRD §13) for the MVP search corpus. Depends on prior index (US-011 path).

**Independent Test**: With an already indexed repository, save a file in VS Code and verify ContextOS triggers incremental re-index for the changed scope within BRD delta timing targets; API shape beyond `POST /index` remains `[NEEDS CLARIFICATION: OQ-14]`.

**Acceptance Scenarios**:

1. **Given** an already indexed repository, **When** I save a file in VS Code, **Then** ContextOS triggers incremental re-index for the changed scope.
2. **Given** BRD delta guidance, **When** delta indexing runs for stated scales, **Then** delta indexing targets include <60s for a 100-file delta and illustrative ~0.5s for single-file save where applicable (BRD §5 L1 / §10 / §14 — L5 path applies in MVP).
3. **Given** trigger API detail is not fully specified, **When** implementation is planned, **Then** incremental re-index may reuse `POST /index` with narrower scope (`[NEEDS CLARIFICATION: OQ-14]`) — no additional invented endpoints.

---

### User Story 5 — Query-Time External LLM Consent Gate (Priority: P2)

As a **Security** stakeholder, I want query-time use of external LLM providers to require explicit consent/configuration, so that compressed context is not sent to third parties without agreement.

**Why this priority**: Completes the privacy model alongside local indexing (Appendix C). Included in EP-001 per epic list / PM handoff as a cross-cutting consent constraint; primary ownership of broader privacy epic remains EP-005 for US-013/US-014. Index path remains no-exfil (US-002).

**Independent Test**: Attempt a query-time flow that would send context to an external LLM without consent/configuration and verify it is blocked; with consent present, only the allowed compressed/packed context path may be used; local inference (e.g., Ollama) may operate without external exfil when configured.

**Acceptance Scenarios**:

1. **Given** a user/workspace without consent/configuration for external LLM, **When** a flow would send context to an external provider, **Then** the system does not send code/context to that provider.
2. **Given** explicit consent/configuration is present, **When** query-time LLM use is invoked, **Then** only the allowed compressed/packed context path may be used (BRD Appendix C privacy narrative).
3. **Given** local options such as Ollama are configured, **When** users choose local inference, **Then** ContextOS may operate without external exfil (BRD Appendix C).
4. **Given** indexing is running (US-002 path), **When** consent is absent or present, **Then** the index path still does not send source code to external LLM providers.

---

### Edge Cases

- Repository contains `.gitignore`-matched paths, `.env`, `node_modules`, `dist`, `.git`, secrets, build outputs, dependency folders, or binaries — these MUST NOT be included in packs/embeddings (constitution III; FR-01; US-013 constraints for indexing; Appendix C).
- Explicit “approved override” to include normally excluded secret material — approval workflow detail **Not evidenced** (`[NEEDS CLARIFICATION]`).
- `graph_nodes` in `POST /index` response may be `0` until V1 L1 graph indexing (api-contract; US-002).
- Incremental delta indexing API beyond `POST /index` is **Not evidenced** (`[NEEDS CLARIFICATION: OQ-14]`).
- Consent UX/storage mechanism beyond “consent flag/configuration” is **Not evidenced** (`[NEEDS CLARIFICATION]` for US-016).
- Exact pack schema fields beyond FR-01 XML-oriented representation and token pre-calc — **do not invent** (`[NEEDS CLARIFICATION]`).
- Invalid / unreadable `repo_path` — status code mapping **Not evidenced** (api-contract Proposed only; do not invent as confirmed).
- Concurrent index-in-progress behavior — **Not evidenced** beyond Proposed `409` in api-contract.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST flatten a local repository (pack target up to 500k LOC per FR-01) into an LLM-optimized packed representation that is XML-oriented per FR-01.  
  *Source: US-001; BRD FR-01*

- **FR-002**: System MUST pre-calculate token counts for the packed representation.  
  *Source: US-001; BRD FR-01*

- **FR-003**: System MUST skip binary artifacts during packing.  
  *Source: US-001; BRD FR-01*

- **FR-004**: System MUST make pack outputs available for subsequent hybrid search and prompt assembly consumers (delivery of search/packing UX is out of scope for this feature).  
  *Source: US-001*

- **FR-005**: System MUST expose repository indexing via confirmed `POST /index` with request body fields `repo_path` and `repo_name`.  
  *Source: US-001, US-002; BRD Appendix D; api-contract §2.2*

- **FR-006**: System MUST return `POST /index` response fields `files_indexed`, `embeddings`, `time_ms`, and `graph_nodes` (where `graph_nodes` MAY be 0 until V1).  
  *Source: US-002; BRD Appendix D; api-contract §2.2*

- **FR-007**: System MUST create embeddings using local `sentence-transformers/all-MiniLM-L6-v2` at 384 dimensions on local CPU.  
  *Source: US-002; BRD §10; ADR-003*

- **FR-008**: System MUST store embeddings in the Qdrant `codebase` collection for MVP.  
  *Source: US-002; ADR-003; database-schema §2*

- **FR-009**: System MUST NOT send repository source code to external LLM providers during indexing.  
  *Source: US-002; US-016 Notes; constitution III; ADR-003; Appendix C*

- **FR-010**: System MUST respect `.gitignore` when walking/packing/indexing a repository.  
  *Source: US-001; FR-01; constitution III; ADR-012; indexing constraints from US-013*

- **FR-011**: System MUST exclude `.env`, secrets, build outputs, dependency folders (including evidenced examples `node_modules`, `dist`), `.git`, and binary artifacts from packs and embeddings unless explicitly approved.  
  *Source: FR-01; constitution III; ADR-012; Appendix C; US-013 constraints (EP-001 does not own full US-013)*

- **FR-012**: Explicit approval workflow / UX to override secret/exclusion policy is `[NEEDS CLARIFICATION: approval workflow Not evidenced]`. Until clarified, System MUST keep default exclusions in force.  
  *Source: US-013 Open Questions; constitution III*

- **FR-013**: VS Code extension MUST trigger auto-index of the workspace repository on install/activation.  
  *Source: US-011; BRD §10; §14 On Install*

- **FR-014**: Auto-index MUST orchestrate indexing through the FastAPI backend; the extension MUST NOT silently bypass backend indexing policy, consent checks, or ignore rules.  
  *Source: US-011; constitution V; ADR-001 boundary discipline*

- **FR-015**: Extension surface MAY own progress and cancellation UX for indexing operations.  
  *Source: US-011 Notes; constitution V*

- **FR-016**: Given an already indexed repository, System MUST trigger incremental re-index for the changed scope when a file is saved in VS Code.  
  *Source: US-012; BRD §6; §14 On File Save*

- **FR-017**: Incremental re-index API shape beyond confirmed `POST /index` is `[NEEDS CLARIFICATION: OQ-14]`. Implementation MUST NOT invent additional confirmed endpoints; reuse of `POST /index` with narrower scope is permitted only as a clarified/proposed approach until OQ-14 is resolved.  
  *Source: US-012; OQ-14; api-contract §2.2 Incremental*

- **FR-018**: System MUST NOT send code/context to an external LLM provider at query time when consent/configuration for that provider is absent.  
  *Source: US-016; constitution III; ADR-012; Appendix C*

- **FR-019**: When explicit consent/configuration for external LLM use is present, System MUST restrict external transmission to the allowed compressed/packed context path described by BRD Appendix C privacy narrative.  
  *Source: US-016*

- **FR-020**: When local inference options such as Ollama are configured and selected, System MAY operate query-time inference without external exfil.  
  *Source: US-016; Appendix C*

- **FR-021**: Consent UX and storage mechanism beyond “consent flag/configuration” is `[NEEDS CLARIFICATION: US-016 consent UX/storage Not evidenced]`. Until clarified, System MUST treat absence of explicit consent/configuration as deny-by-default for external LLM query-time use.  
  *Source: US-016 Open Questions; constitution III*

- **FR-022**: Exact pack schema field inventory beyond FR-01 XML-oriented representation and token pre-calc is `[NEEDS CLARIFICATION: pack schema fields Not evidenced]` — System MUST NOT invent undocumented pack fields as requirements.  
  *Source: US-001 Notes; PM handoff*

- **FR-023**: Chunking for embedding SHOULD align with evidenced Appendix C guidance of approximately 500-token chunks when producing vectors for Qdrant.  
  *Source: Appendix C; database-schema §2*

### Key Entities

- **Repository Index Request**: Logical request identified by `repo_path` (local readable path) and `repo_name` (logical name).
- **Packed Representation**: LLM-optimized, XML-oriented flatten of allowed repository content with token count pre-calculation; excludes ignored/secret/binary paths.
- **Embedding Chunk**: Segment of allowed file content (~500 tokens per Appendix C) with local 384-dim vector stored in Qdrant `codebase`, associated with repository and file path concepts.
- **Index Result**: Counts and timing — `files_indexed`, `embeddings`, `time_ms`, `graph_nodes` (may be 0 until V1).
- **Consent Configuration**: Explicit user/workspace consent or configuration gate for query-time external LLM use (`[NEEDS CLARIFICATION]` on UX/storage shape).

---

## ContextOS Impact *(mandatory for this project)*

### Affected Layers

- **L1 Structural Knowledge Graphs**: N/A for MVP delivery of this feature — `graph_nodes` may be 0; L1 build is V1 (roadmap; api-contract). Response field reserved only.
- **L2 Multi-modal Project Graphs**: N/A — V2 (constitution roadmap; EP-001 scope).
- **L3 Symbol & LSP Navigation**: N/A — owned by EP-003 (Serena).
- **L4 Context Compression**: N/A as primary scope — V1; query-time compressed path referenced only as privacy boundary for US-016 / Appendix C.
- **L5 Context Packing & Semantic Search**: **Primary** — repo packing and embedding index foundation. Hybrid BM25/vector search, MMR, and phase-aware prompt assembly are **out of scope** (EP-002).
- **L6 Persistent Agent Memory**: N/A — V2.

### Affected Surfaces

- **FastAPI / API**: **Affected** — owns indexing orchestration and `POST /index` (constitution V; ADR-001).
- **CLI**: N/A as primary EP-001 story surface — CLI ask/index workflows belong to EP-004 / later stories unless separately specified. Not invented here.
- **VS Code Extension**: **Affected** — may trigger auto-index on install/activation and incremental re-index on save; progress/cancellation UX; MUST call backend (US-011, US-012; constitution V).
- **Dashboard / Webview / Visualization**: N/A for this feature’s primary acceptance — not required by EP-001 stories.
- **GitHub Action / CI**: N/A — Future (US-043); out of scope.
- **Qdrant**: **Affected** — MVP vector store for embeddings (ADR-003).
- **Background indexer**: **Affected** as backend indexing behavior invoked by API/extension triggers (not a separate invented product surface).

### Privacy And Security

- **Repository content handling**: Respect `.gitignore`; exclude `.env`, secrets, build outputs, dependency folders, binaries, and evidenced paths (`node_modules`, `dist`, `.git`) from packs/embeddings (constitution III; FR-01; ADR-012; US-013 constraints applied to indexing).
- **Consent / exfiltration**: No code exfil during indexing (US-002; ADR-003). Query-time external LLM requires explicit consent/configuration (US-016); local Ollama path allowed per Appendix C. Clients MUST NOT bypass orchestrator ignore/consent policy (constitution V).
- **RBAC / PII**: RBAC per repo path is a constitution/BRD control; exact RBAC schema is Missing Evidence (OQ-01) — **not invented** here. PII redaction applies to L2/L6 paths per ADR-012 — **N/A as primary for EP-001** unless overlapping memory/multi-modal ingestion (out of scope).
- **Source provenance**: Constitution III requires provenance on context/search outputs; pack/index foundation SHOULD preserve path association for chunks (`file_path` / repo concepts in schema). Full citation UX is EP-002 / US-015 — out of scope as primary.

---

## Non-Functional Requirements

### Performance

- **NFR-001**: Full monorepo indexing MUST target <15 minutes for 1M LOC (BRD §10 Monorepo indexing). MVP repos constrained by assumption A-01 (monorepo ≤1M LOC).
- **NFR-002**: Delta indexing MUST target <60 seconds for a 100-file delta (BRD §10; US-012).
- **NFR-003**: Single-file save re-index illustrative target ~0.5 seconds where applicable (BRD §14; US-012) — not a stricter invented global SLA.
- **NFR-004**: Auto-index of ~200 files illustrative target ~10 seconds where hardware permits (BRD §14; US-011) — not a stricter invented global SLA beyond §10 monorepo targets.
- Search p95 latency and recall@k are **out of scope** (EP-002 / FR-02) and MUST NOT be used as acceptance for this feature.

### Security

- **NFR-005**: Local embeddings only during indexing; no index-time external LLM exfil (BRD §10 Embedding model; ADR-003).
- **NFR-006**: Ignore and secret-exclusion policy enforced in orchestrator (constitution III; ADR-012).
- **NFR-007**: Query-time external LLM deny-by-default without consent/configuration (US-016; constitution III).

### Reliability

- Indexer availability 99.5% and graceful degraded search on partial index are evidenced in BRD §10 / US-014 (EP-005) — **referenced as adjacent**, not owned as primary acceptance by EP-001 unless needed for index completion signaling. Exact partial-index operator UX is EP-005.

### Accessibility

- Not evidenced for EP-001 indexing flows — **N/A** (`Not evidenced in provided inputs.`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Packing/indexing of a repository within FR-01 pack scale produces an LLM-optimized packed representation with token count pre-calculation and binary skip (US-001; FR-01).
- **SC-002**: `POST /index` returns `files_indexed`, `embeddings`, `time_ms`, and `graph_nodes` (allowing `graph_nodes = 0` until V1) (US-002; Appendix D).
- **SC-003**: Embeddings are 384-dim from local `all-MiniLM-L6-v2` stored in Qdrant; verification shows zero source-code exfil to external LLM providers on the index path (US-002; §10; ADR-003).
- **SC-004**: Ignored and excluded paths (`.gitignore`, `.env`, secrets, build/deps/binaries, evidenced `node_modules`/`dist`/`.git`) are absent from packs and embeddings (FR-01; constitution III; Appendix C).
- **SC-005**: Full index completes in <15 minutes for a 1M LOC corpus under BRD monorepo indexing NFR (BRD §10; A-01).
- **SC-006**: Delta index for a 100-file change set completes in <60 seconds (BRD §10; US-012).
- **SC-007**: Extension install/activation triggers backend indexing into Qdrant for the workspace repo without requiring a separate manual indexing ceremony (US-011).
- **SC-008**: File save triggers incremental re-index for changed scope (US-012); single-file illustrative ~0.5s and ~200-file/~10s install timings are observational/hardware-gated targets, not invented stricter SLAs.
- **SC-009**: Without external-LLM consent/configuration, query-time flows do not send code/context to external providers; index path remains no-exfil regardless of consent state (US-016; US-002).
- **SC-010**: Consent UX/storage details remain `[NEEDS CLARIFICATION]` — success is deny-by-default behavior until UX/storage is specified; do not invent pass criteria for unstated UI.

---

## Confirmed Facts

- EP-001 includes stories US-001, US-002, US-011, US-012, US-016 (backlog epic list). US-016 story table Epic field says EP-005; included here per epic list + PM handoff as cross-cutting consent gate.
- MVP roadmap = L5 + L3; this feature is MVP L5 packing/indexing foundation (constitution IV/V roadmap; BRD §15).
- Confirmed API: `POST /index` `{repo_path, repo_name}` → `{files_indexed, graph_nodes, embeddings, time_ms}` (Appendix D; api-contract).
- Local embeddings: `all-MiniLM-L6-v2`, 384-dim, CPU; Qdrant collection `codebase` (ADR-003).
- Repomix-style packing; FR-01 XML-oriented pack with token pre-calc; `.gitignore` / `.env` / `node_modules` / `dist` / `.git` / binary skip (FR-01; Appendix C).
- No code sent during indexing; query-time external LLM requires consent (Appendix C; constitution III).
- FastAPI owns indexing orchestration; VS Code extension owns DX triggers and progress/cancellation (constitution V).
- `graph_nodes` may be 0 until V1 (api-contract; US-002).
- Pinecone is not the default vector store (A-08; ADR-008).

---

## Assumptions

- **A-01** (non-blocking): Git is source of truth; monorepo ≤1M LOC for MVP (BRD §13) — constrains index SLA applicability.
- **A-03** (non-blocking): LLM provider supports ~128k context; compression to fit is V1 L4 — relevant to US-016 query-time narrative only.
- **A-04** (non-blocking): Qdrant available locally or in VPC via Docker Compose for POC (BRD §13–§15; ADR-013).
- **A-08** (non-blocking): Pinecone is not the default vector store (ADR-008).
- **A-EP001-1** (non-blocking): Pack outputs from EP-001 are consumable by EP-002 hybrid search / prompt assembly without requiring those features to ship inside EP-001.
- **A-EP001-2** (non-blocking): Extension can reach the FastAPI orchestrator for install/save indexing triggers in the MVP deploy topology.

---

## Dependencies

- Local filesystem / Git repository readable at `repo_path`.
- FastAPI orchestrator runtime (Python 3.11 per approved stack).
- Qdrant with `codebase` collection (384-dim).
- Local `sentence-transformers/all-MiniLM-L6-v2` model weights available on CPU (~90MB per ADR-003 trade-off note).
- VS Code extension host for US-011 / US-012 triggers.
- Privacy default constraints aligned with constitution III / ADR-012 (full US-013/US-014 owned by EP-005).
- Downstream (not blocking EP-001 acceptance): EP-002 for hybrid search consumption of packs/embeddings; EP-003 Serena; V1 L1 for non-zero `graph_nodes`.

---

## Out Of Scope

- Hybrid BM25 + vector search, MMR ranking, phase-aware prompt assembly (EP-002 / US-003, US-004, US-015).
- Serena / L3 symbol navigation (EP-003).
- L1 blast radius, graph visualization, structural graph population beyond optional `graph_nodes = 0` (V1).
- L4 compression implementation and token-budget telemetry (V1).
- L2 multi-modal ingestion and L6 persistent memory (V2).
- Full ownership of US-013 / US-014 as primary stories (EP-005), except indexing-time ignore/exclusion and no-exfil constraints required here.
- Invented incremental index endpoints beyond OQ-14 clarification.
- Invented consent UX/storage designs.
- Invented pack schema fields beyond FR-01.
- Search p95 <800ms and recall@k metrics (EP-002).
- JetBrains extension, GitHub Action CI indexing (Future).
- CLI as primary acceptance surface for this epic (EP-004).

---

## Open Questions

| ID | Question | Blocking? | Impact |
|----|----------|-----------|--------|
| OQ-14 | Incremental delta index API beyond confirmed `POST /index` (narrower scope reuse Proposed only) | Non-blocking for draft spec; **blocking for locking US-012 API contract in plan/tasks** | US-012; FR-017 |
| OQ-US016 | Exact consent UX and storage mechanism beyond consent flag/configuration | Non-blocking for deny-by-default requirement; **blocking for consent UX implementation detail** | US-016; FR-021 |
| OQ-PACK | Exact pack schema fields beyond FR-01 XML-oriented + token pre-calc | Non-blocking for behavioral FR-01 acceptance; **blocking for pack contract freeze** | US-001; FR-022 |
| OQ-OVERRIDE | Explicit “approved override” UX for excluded secrets/paths | Non-blocking while defaults remain exclude-all | FR-012; US-013 note |
| OQ-01 | Exact RBAC roles/path/authn schema | Non-blocking for MVP POC indexing defaults; blocking for path-RBAC enforcement detail | constitution III; ADR-012 |
| OQ-HTTP | Confirmed HTTP status codes for `POST /index` (api-contract Proposed only) | Non-blocking for functional draft | api-contract §2.2 |

---

## Requirement Traceability

| Requirement ID | Source | Evidence |
| -------------- | ------ | -------- |
| FR-001 | US-001 | BRD FR-01; §5 L5 |
| FR-002 | US-001 | BRD FR-01 token pre-calc |
| FR-003 | US-001 | BRD FR-01 binary skip |
| FR-004 | US-001 | US-001 AC (downstream availability) |
| FR-005 | US-001, US-002 | Appendix D; api-contract `POST /index` |
| FR-006 | US-002 | Appendix D; api-contract response |
| FR-007 | US-002 | BRD §10; ADR-003; constitution Approved Tech |
| FR-008 | US-002 | ADR-003; database-schema Qdrant `codebase` |
| FR-009 | US-002, US-016 | Appendix C; constitution III; ADR-003 |
| FR-010 | US-001 + indexing privacy | FR-01; constitution III; ADR-012 |
| FR-011 | Indexing privacy constraints (US-013 referenced) | FR-01; Appendix C; constitution III; ADR-012 |
| FR-012 | US-013 OQ / Missing Evidence | Backlog US-013 Open Questions |
| FR-013 | US-011 | BRD §10 IDE; §14 On Install |
| FR-014 | US-011 | constitution V; ADR-001 |
| FR-015 | US-011 Notes | constitution V |
| FR-016 | US-012 | BRD §6; §14 On File Save |
| FR-017 | US-012 / OQ-14 | api-contract Incremental note; backlog OQ-14 |
| FR-018 | US-016 | Appendix C; constitution III; ADR-012 |
| FR-019 | US-016 | Appendix C privacy narrative |
| FR-020 | US-016 | Appendix C optional local Ollama |
| FR-021 | US-016 Open Questions | Backlog; PM handoff |
| FR-022 | US-001 Notes | PM handoff pack schema |
| FR-023 | Embedding path | Appendix C ~500 token chunks; database-schema |
| NFR-001..004 | US-011, US-012 | BRD §10 Monorepo indexing; §14 timings |
| NFR-005..007 | US-002, US-016 | BRD §10; constitution III |
| SC-001..010 | Stories above | Mapped ACs + evidenced indexing NFRs only |

### Acceptance Scenario → FR Map

| Scenario | Maps to |
|----------|---------|
| US-001 pack + token + binary skip | FR-001, FR-002, FR-003, FR-005 |
| US-001 pack available downstream | FR-004 |
| US-002 local embed + no exfil | FR-007, FR-008, FR-009 |
| US-002 response fields | FR-006 |
| Indexing ignore/exclusion | FR-010, FR-011, FR-012 |
| US-011 auto-index + backend ownership | FR-013, FR-014, FR-015 |
| US-012 save delta + OQ-14 | FR-016, FR-017 |
| US-016 consent gate + local option | FR-018, FR-019, FR-020, FR-021 |
| Chunk sizing | FR-023 |

---

## Constitution Compliance (Specification Gate)

| Gate Check | Status |
|------------|--------|
| User scenarios prioritized and independently testable | Met |
| Functional requirements atomic and traceable | Met |
| ContextOS layer and surface impact documented | Met |
| Security/privacy implications documented | Met |
| Success criteria measurable or marked NEEDS CLARIFICATION | Met (indexing NFRs evidenced; consent UX/pack schema/OQ-14 clarified as open) |
| Blocking open questions visible | Met (OQ-14, consent UX, pack schema, override UX, RBAC, HTTP codes) |

**Specification Gate**: **Yes** (ready for Plan Generator with open questions carried forward; do not invent answers in planning).
