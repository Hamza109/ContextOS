# Agile Product Backlog

**Product:** ContextOS — Six-Layer SDLC Intelligence Platform  
**Source of truth:** `docs/BRD_Context_OS.md` v0.9 Draft  
**Governance:** `.specify/memory/constitution.md` v1.0.0  
**Architecture constraints:** `docs/architecture/` (Architecture ready: Yes)  
**Backlog version:** Regenerated 2026-07-27 (continuity with prior handoff: 12 epics, US-001..US-045, 16 MVP)  
**Status:** Ready for Spec Writer on MVP epics EP-001..EP-005

---

## Executive Summary

This backlog converts the ContextOS BRD into a prioritized, Spec Kit–ready Agile backlog across the six SDLC intelligence layers, IDE/CLI/API surfaces, security, observability, and the BRD roadmap. Delivery order is fixed: **MVP = L5 + L3** (packing, hybrid search, Serena symbols, CLI, VS Code, indexing basics, privacy defaults) → **V1 = L1 + L4** (structural graph, blast radius, visualization, compression, telemetry, PR risk) → **V2 = L2 + L6** (multi-modal graph, persistent memory/governance, enterprise RBAC/VPC, onboarding) → **Future** (JetBrains, GitHub Action, SIP/marketplace).

**Counts:** 12 epics · 45 stories (US-001..US-045) · **16 MVP** · 11 V1/P2 · 14 V2/P3 · 4 Future. FR-01..FR-18 are fully traced. Personas used are only those evidenced in the BRD. Missing product detail is recorded as Open Questions / `[NEEDS CLARIFICATION]` — not invented.

---

## Evidence Reviewed

| Artifact | Path | Role |
|----------|------|------|
| Constitution v1.0.0 | `.specify/memory/constitution.md` | Evidence-first, six-layer integrity, privacy, roadmap, boundaries |
| BRD v0.9 Draft | `docs/BRD_Context_OS.md` | Sole product truth (objectives, FR-01..FR-18, NFRs, personas, roadmap, APIs) |
| Architecture overview | `docs/architecture/architecture-overview.md` | Layer/surface mapping, confirmed vs missing evidence |
| API contract | `docs/architecture/api-contract.md` | Evidenced Appendix D endpoints; Proposed labeled separately |
| Architecture decisions | `docs/architecture/architecture-decisions.md` | ADR-001..014 roadmap and stack constraints |
| Tech stack | `docs/architecture/tech-stack.md` | Approved technologies by phase |
| Implementation guidelines | `docs/architecture/implementation-guidelines.md` | Boundary and NFR budgets (constraints only; no tasks) |
| Remaining architecture set | `docs/architecture/*.puml`, `database-schema.md`, `frontend-architecture.puml`, etc. | Structural constraints |
| Prior handoff | `.cursor/agent-handoffs/handoff.md` | Continuity: 12 epics, 45 stories, 16 MVP |

---

## Confirmed Facts

1. ContextOS orchestrates six layers (L1–L6) as a sidecar between developer intent and LLMs; it does not replace IDEs or train LLMs (BRD §2, §6 OUT OF SCOPE).
2. Roadmap order is mandatory: MVP L5+L3 → V1 L1+L4 → V2 L2+L6 (BRD §15; constitution Roadmap Governance; ADR-001).
3. Business objectives BO-01..BO-05 and KPIs are defined in BRD §3 and §12.
4. Functional requirements FR-01..FR-18 are defined in BRD §9 and map to layers as in architecture overview §3.3.
5. NFR targets include: search p95 <800ms @ 500k LOC; blast p95 <2s @ 3-hop/10k nodes; compression 60–95% with recall@10 >0.92; full index <15 min @ 1M LOC; delta <60s; memory recall >90% with <1.2s p95; IDE <3 clicks to Ask ContextOS; indexer 99.5% uptime with degraded search (BRD §10).
6. Privacy defaults: respect `.gitignore`; ignore `.env`/secrets/build outputs/deps/binaries; no code exfil to external LLM during indexing; query-time LLM requires consent; RBAC per repo path; PII redaction on memory/multi-modal paths; provenance on outputs (BRD §10, Appendix C; constitution III).
7. Evidenced HTTP APIs (Appendix D): `GET /`, `POST /index`, `POST /context`, `GET /blast/{file_name}`, `GET /graph.html?repo=`.
8. Approved stack includes FastAPI/Python 3.11, Qdrant (384-dim), FalkorDB (V1), all-MiniLM-L6-v2 local, Serena MCP, Repomix/Headroom/Cognee-style components, React Flow/vis-network, OpenTelemetry, VS Code primary MVP IDE + CLI (constitution; ADR-002..014).
9. BRD personas/stakeholders for stories: Product Manager, Developer, QA Engineer, DevOps/SRE, Security, AI Platform Lead, Staff Engineer, CTO/VP Eng (BRD §7, §11).
10. MVP exit: symbol-accurate context <2s in IDE; search works; CLI `contextos ask 'where is X?'` (BRD §15).

---

## Assumptions

| ID | Assumption | Blocking? | Source |
|----|------------|-----------|--------|
| A-01 | Git is source of truth; monorepo ≤1M LOC for MVP | Non-blocking for backlog; may constrain index SLA stories | BRD §13 |
| A-02 | Teams use VS Code or JetBrains (80%+); MVP ships VS Code + CLI first | Non-blocking | BRD §13; ADR-007 |
| A-03 | LLM provider supports ~128k context; ContextOS compresses to fit (V1 L4) | Non-blocking | BRD §13 |
| A-04 | Qdrant available locally or in VPC via Docker Compose for POC | Non-blocking | BRD §13–§15; ADR-008/013 |
| A-05 | Local/dev API may be trusted loopback until authn is specified | Non-blocking for MVP stories; authn remains Missing Evidence | api-contract §1 |
| A-06 | MVP `/context` may return packing token counts; full compression metrics meaningful at V1 | Non-blocking | ADR-006; api-contract §2.3 |
| A-07 | FalkorDB may be unused/absent in MVP health without failing search | Non-blocking | api-contract §2.1 MVP note |
| A-08 | Pinecone is not the default vector store (Qdrant approved) | Non-blocking | ADR-008 |

---

## Open Questions

| ID | Question | Blocking? | Affects |
|----|----------|-----------|---------|
| OQ-01 | Exact RBAC roles, path patterns, and authn mechanism | **Blocking** for US-038 detail / enterprise authz AC | Security, US-038 |
| OQ-02 | JetBrains extension depth and timing vs VS Code-first MVP | Non-blocking (Future US-042) | US-042 |
| OQ-03 | External connector auth/scopes (Notion/Confluence/Jira/Figma/Slack/Loom) for L2 | **Blocking** for connector-specific AC | US-028..US-030 |
| OQ-04 | GitHub Action trigger contracts and CI payload schema | **Blocking** for US-043 | US-043 |
| OQ-05 | Role-based context pack schema (PM/Dev/QA/DevOps) | **Blocking** for US-041 pack content AC | US-041 |
| OQ-06 | codebase-memory-mcp ↔ FastAPI integration boundary (FR-10) | **Blocking** for US-021 contract detail | US-021 |
| OQ-07 | Canonical phase token budgets: Dev 8k (§5) vs Dev=12k (FR-11) | **Blocking** for US-022 numeric budget AC | US-022 |
| OQ-08 | Token dashboard serving mechanism (static HTML vs API-hosted) | Non-blocking | US-024 |
| OQ-09 | OpenTelemetry exporter / collector vendor | Non-blocking | US-024 |
| OQ-10 | CLI machine-readable output schema | Non-blocking | US-007 |
| OQ-11 | Citation JSON shape inside `final_context` | Non-blocking | US-015 |
| OQ-12 | Measurement method for Serena 99% definition accuracy | Non-blocking for story intent; blocks verification design | US-005 |
| OQ-13 | Enterprise air-gap / VPC tier boundaries | **Blocking** for US-039 tier boundary AC | US-039 |
| OQ-14 | Incremental delta index API beyond `POST /index` | Non-blocking | US-012 |
| OQ-15 | Blast response `owners` JSON field shape | Non-blocking | US-018, US-025 |
| OQ-16 | Phase parameter shape for FR-03 templates | Non-blocking | US-004 |
| OQ-17 | Memory pin/forget HTTP shapes; Copilot instructions write-back automation | Non-blocking | US-033 |
| OQ-18 | Deployment risk score algorithm weights | Non-blocking | US-037 |
| OQ-19 | PII classification taxonomy beyond BRD wording | Non-blocking | US-033, US-036 |
| OQ-20 | Onboarding agent UX depth | Non-blocking | US-040 |

---

## Epics

### EP-001 — L5 Repository Packing & Indexing

- **Epic ID:** EP-001  
- **Title:** L5 Repository Packing & Indexing  
- **Business Objective:** Enable local-first, privacy-respecting repo flatten/pack and embedding so teams can retrieve SDLC context without manual file pasting (BO-01, BO-04).  
- **Included Stories:** US-001, US-002, US-011, US-012, US-016  
- **Source Evidence:** BRD FR-01, §6 IN SCOPE, §10 indexing NFRs, §14–§15, Appendix C; ADR-003

### EP-002 — L5 Hybrid Search & Phase-Aware Packing

- **Epic ID:** EP-002  
- **Title:** L5 Hybrid Semantic Search & Phase-Aware Prompt Packing  
- **Business Objective:** Answer “where is X?” with high-recall hybrid search and assemble phase-scoped context packs (BO-01, BO-04).  
- **Included Stories:** US-003, US-004, US-015  
- **Source Evidence:** BRD FR-02, FR-03, §10 search NFR, §12 recall@10, §15 MVP

### EP-003 — L3 Symbol & LSP Navigation

- **Epic ID:** EP-003  
- **Title:** L3 Symbol & LSP Navigation (Serena)  
- **Business Objective:** Provide IDE-grade symbol accuracy so AI/dev edits respect language semantics and reduce regressions (BO-03).  
- **Included Stories:** US-005, US-006, US-009, US-010  
- **Source Evidence:** BRD FR-04..FR-06, §11 Developer Pack Context, §15 MVP; ADR-005

### EP-004 — CLI & VS Code Developer Surfaces

- **Epic ID:** EP-004  
- **Title:** CLI & VS Code Developer Surfaces  
- **Business Objective:** Deliver scriptable and IDE entry points so developers reach ContextOS in under three clicks and via CLI ask (BO-01, BO-04).  
- **Included Stories:** US-007, US-008  
- **Source Evidence:** BRD §5 deliverables, §10 IDE integration, §15 MVP; ADR-007

### EP-005 — Privacy Defaults, Health & Consent

- **Epic ID:** EP-005  
- **Title:** Privacy Defaults, Health & Consent  
- **Business Objective:** Protect repository content by default and keep search available under partial failure (Security / DevOps trust for POC).  
- **Included Stories:** US-013, US-014  
- **Source Evidence:** BRD §10 Code access & PII, indexer availability; constitution III; Appendix C; ADR-012

### EP-006 — L1 Structural Graph Generation

- **Epic ID:** EP-006  
- **Title:** L1 Structural Knowledge Graph Generation  
- **Business Objective:** Pre-index typed dependency structure for change-safety analysis (BO-03).  
- **Included Stories:** US-017, US-021  
- **Source Evidence:** BRD FR-07, FR-10, §5 L1, §15 V1; ADR-004

### EP-007 — L1 Blast Radius & Visualization

- **Epic ID:** EP-007  
- **Title:** L1 Blast Radius Analysis & Dependency Visualization  
- **Business Objective:** Answer “what breaks if I change this?” with measurable latency and interactive graph views (BO-03, BO-04).  
- **Included Stories:** US-018, US-019, US-020, US-027  
- **Source Evidence:** BRD FR-08, FR-09, §10 blast/graph NFRs, §15 V1; ADR-010

### EP-008 — L4 Compression, Budgets & Telemetry

- **Epic ID:** EP-008  
- **Title:** L4 Context Compression, Token Budgets & Cost Telemetry  
- **Business Objective:** Cut LLM token cost 60–95% while preserving recall and making savings visible (BO-02).  
- **Included Stories:** US-022, US-023, US-024  
- **Source Evidence:** BRD FR-11..FR-13, §10 compression NFR, §12, §15 V1; ADR-006, ADR-011

### EP-009 — PR Risk & Regression Support

- **Epic ID:** EP-009  
- **Title:** PR Risk Bot & QA Regression Support  
- **Business Objective:** Surface affected tests/owners and regression suggestions to reduce breakage (BO-03).  
- **Included Stories:** US-025, US-026  
- **Source Evidence:** BRD §11 QA/Developer, §15 V1 PR risk bot, FR-08

### EP-010 — L2 Multi-modal Project Graphs

- **Epic ID:** EP-010  
- **Title:** L2 Multi-modal Ingestion & Cross-Artifact Linking  
- **Business Objective:** Unify code with docs/SQL/diagrams/transcripts for accurate discovery and PRDs (BO-04; PM use cases).  
- **Included Stories:** US-028, US-029, US-030, US-036  
- **Source Evidence:** BRD FR-14, FR-15, §8 Requirements/Design/Maintenance, §11 PM/QA

### EP-011 — L6 Persistent Memory & Governance

- **Epic ID:** EP-011  
- **Title:** L6 Persistent Agent Memory & Governance  
- **Business Objective:** Preserve cross-session tribal knowledge with explainable recall and governed retention (BO-05).  
- **Included Stories:** US-031, US-032, US-033, US-034, US-035  
- **Source Evidence:** BRD FR-16..FR-18, §11 PM/Developer, Appendix A/B, §15 V2

### EP-012 — Enterprise Hardening, Onboarding & Future Surfaces

- **Epic ID:** EP-012  
- **Title:** Enterprise Hardening, Onboarding Agent & Future Surfaces  
- **Business Objective:** Harden access/deployment for enterprise, accelerate onboarding, and stage long-horizon SIP/IDE/CI expansions.  
- **Included Stories:** US-037, US-038, US-039, US-040, US-041, US-042, US-043, US-044, US-045  
- **Source Evidence:** BRD §6, §10 RBAC, §11 SRE, §15 V2 + SIP Vision

---

## Prioritized User Stories

### MVP / P1

> MVP Classification uses **P0** (core MVP exit) and **P1** (required supporting MVP). Priority column uses roadmap **P1** for all MVP-required stories per agent format.

---

#### US-001 — Repo Flattening & Packing

| Field | Content |
|-------|---------|
| **Story ID** | US-001 |
| **Title** | Repo Flattening & Packing |
| **Epic** | EP-001 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P0 |
| **User Story** | As a **Developer**, I want the system to flatten my repository into an LLM-optimized packed representation with token count pre-calculation, so that I can obtain usable repo context without manually concatenating files. |
| **Business Value** | Unlocks L5 packing foundation for search and phase-aware prompts (BO-01; FR-01). |
| **Acceptance Criteria** | **Given** a local repository within BRD-stated scale (up to 500k LOC pack target) **When** indexing/packing is requested via the evidenced indexing path (`POST /index` or equivalent orchestrated pack) **Then** the system produces an LLM-optimized packed representation (XML-oriented per FR-01) with token count pre-calculation, skipping binaries as specified. **Given** packing completes **When** results are inspected **Then** pack outputs are available for subsequent hybrid search and prompt assembly. |
| **Dependencies** | None |
| **Source Evidence** | BRD FR-01; §5 L5; §14; Appendix C; api-contract `POST /index` |
| **Assumptions** | A-01 |
| **Open Questions** | None blocking |
| **Notes** | Repomix-style packing per constitution/BRD; no invented pack schema fields. |

---

#### US-002 — Privacy-Respecting Local Embedding Index

| Field | Content |
|-------|---------|
| **Story ID** | US-002 |
| **Title** | Privacy-Respecting Local Embedding Index |
| **Epic** | EP-001 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P0 |
| **User Story** | As a **Security** stakeholder, I want repository chunks embedded locally into the vector store without sending source code to external LLM providers during indexing, so that indexing does not exfiltrate code. |
| **Business Value** | Satisfies privacy NFR and enables semantic search without cloud embedding quota (BO-04; §10). |
| **Acceptance Criteria** | **Given** a repository is indexed **When** embeddings are created **Then** embeddings use local `all-MiniLM-L6-v2` (384-dim) into Qdrant and **no** source code is sent to an external LLM provider during indexing. **Given** indexing completes **When** `POST /index` response is returned **Then** it includes evidenced fields `files_indexed`, `embeddings`, `time_ms` (and `graph_nodes` may be zero until V1). |
| **Dependencies** | US-001 |
| **Source Evidence** | BRD §10 Embedding model / Code access; Appendix C; ADR-003; api-contract `POST /index` |
| **Assumptions** | A-04, A-08 |
| **Open Questions** | None blocking |
| **Notes** | Pinecone not default (ADR-008). |

---

#### US-003 — Hybrid Semantic Search with MMR

| Field | Content |
|-------|---------|
| **Story ID** | US-003 |
| **Title** | Hybrid Semantic Search with MMR |
| **Epic** | EP-002 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P0 |
| **User Story** | As a **Developer**, I want hybrid BM25 + vector search with MMR re-ranking over packed repos, so that I can find relevant files for questions like “where is payment retry logic?” quickly and accurately. |
| **Business Value** | Primary MVP search outcome; reduces discovery time (BO-04; FR-02). |
| **Acceptance Criteria** | **Given** an indexed repository at the NFR reference scale (500k LOC index target) **When** I submit a natural-language search/ask via `POST /context` or CLI ask **Then** the system returns relevant files using hybrid BM25 + vector retrieval with MMR re-ranking. **Given** the same conditions **When** latency is measured **Then** semantic search p95 is <800ms for a 500k LOC index (BRD §10). **Given** a quality evaluation set aligned to BRD success metrics **When** recall@10 is measured **Then** relevant results in top 10 achieve >0.92 where the evaluation harness applies (BRD §12). **Given** FR-02 example intent **When** querying for payment retry logic style questions **Then** results include top-ranked files with scores (example: top 8 files — exact `top_k` bounds `[NEEDS CLARIFICATION: OQ bounds for top_k]`). |
| **Dependencies** | US-001, US-002 |
| **Source Evidence** | BRD FR-02; §10; §12; §15 MVP; ADR-014 |
| **Assumptions** | A-01, A-06 |
| **Open Questions** | OQ-11 (citations may accompany results in packing story) |
| **Notes** | MVP exit: “Search works” (BRD §15). |

---

#### US-004 — Phase-Aware Prompt Templates

| Field | Content |
|-------|---------|
| **Story ID** | US-004 |
| **Title** | Phase-Aware Prompt Templates |
| **Epic** | EP-002 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P0 |
| **User Story** | As a **Developer**, I want context packs assembled using templates scoped to SDLC phase (Requirements/Design/Dev/Test/Deploy), so that prompts match the work I am doing. |
| **Business Value** | Phase-aware packing is an MVP deliverable reducing irrelevant context (BO-01; FR-03). |
| **Acceptance Criteria** | **Given** a supported SDLC phase selection among Requirements, Design, Dev, Test, Deploy **When** context is assembled **Then** the system uses phase-scoped prompt/pack templates (code2prompt-style per FR-03). **Given** two different phases for the same query/repo **When** packs are compared **Then** pack composition differs according to phase scoping (exact parameter wire shape `[NEEDS CLARIFICATION: OQ-16]`). |
| **Dependencies** | US-001, US-003 |
| **Source Evidence** | BRD FR-03; §8 phase mapping; §15 MVP basic prompt packing |
| **Assumptions** | A-06 |
| **Open Questions** | OQ-16 |
| **Notes** | Full L4 budget enforcement is V1 (US-022), not MVP gate (ADR-006). |

---

#### US-005 — Symbol Definition Lookup

| Field | Content |
|-------|---------|
| **Story ID** | US-005 |
| **Title** | Symbol Definition Lookup via Serena |
| **Epic** | EP-003 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P0 |
| **User Story** | As a **Developer**, I want ContextOS to resolve a symbol’s definition (file:line, signature, docstring) via Serena, so that AI and IDE workflows use IDE-grade precision instead of text similarity alone. |
| **Business Value** | Foundation for safe edits and symbol-accurate context (BO-03; FR-04). |
| **Acceptance Criteria** | **Given** a supported language in the Serena-backed set (BRD states 12+ languages) **When** I request definition lookup for a symbol **Then** the system returns definition location including file:line, signature, and docstring when available (example shape: `PaymentService::authenticate() → payment.service.ts:42`). **Given** a verification approach agreed for the 99% accuracy claim **When** accuracy is measured **Then** results meet the BRD 99% accuracy target or the increment documents a scoped gap per constitution IV (`[NEEDS CLARIFICATION: OQ-12 measurement method]`). |
| **Dependencies** | None (Serena MCP); complements US-003 for packed context |
| **Source Evidence** | BRD FR-04; §15 MVP; ADR-005 |
| **Assumptions** | None beyond BRD Serena dependency |
| **Open Questions** | OQ-12 |
| **Notes** | REST symbol proxy not evidenced — may remain MCP-only (api-contract §3). |

---

#### US-006 — Find All References

| Field | Content |
|-------|---------|
| **Story ID** | US-006 |
| **Title** | Find All References Across Monorepo |
| **Epic** | EP-003 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P0 |
| **User Story** | As a **Developer**, I want all references of a symbol across the monorepo with call-site context, so that I can understand usage before changing code. |
| **Business Value** | Supports Development/Testing/Maintenance safe change (FR-05; BO-03). |
| **Acceptance Criteria** | **Given** a resolved symbol in an indexed workspace **When** I request find-all-references **Then** the system returns references across the monorepo including call-site context of 2 lines before/after as specified in FR-05. **Given** a file-type filter **When** references are requested **Then** results can be filtered by file type. |
| **Dependencies** | US-005 |
| **Source Evidence** | BRD FR-05 |
| **Assumptions** | A-01 |
| **Open Questions** | None blocking |
| **Notes** | — |

---

#### US-007 — CLI Ask Workflow

| Field | Content |
|-------|---------|
| **Story ID** | US-007 |
| **Title** | CLI `contextos ask` Query Flow |
| **Epic** | EP-004 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P0 |
| **User Story** | As a **Developer**, I want to run `contextos ask 'where is X?'` from the CLI, so that I can query ContextOS outside the IDE in scripts and terminals. |
| **Business Value** | MVP scriptable surface for discovery (BO-04; §15). |
| **Acceptance Criteria** | **Given** the ContextOS CLI is installed and the orchestrator is reachable with an indexed repo **When** I run `contextos ask 'where is X?'` (or equivalent ask phrasing) **Then** I receive a useful human-readable answer grounded in retrieved context. **Given** the same ask **When** output modes are considered **Then** machine-readable output is provided when planned (`[NEEDS CLARIFICATION: OQ-10 exact schema]` — constitution: when planned). **Given** MVP performance expectations **When** ask completes for symbol-oriented discovery **Then** end-to-end experience aligns with MVP search/ask goals (IDE <2s exit is IDE-scoped; CLI should not invent a stricter unstated SLA). |
| **Dependencies** | US-003 |
| **Source Evidence** | BRD §5 deliverables; §15 MVP CLI; constitution V CLI; api-contract §6 |
| **Assumptions** | A-05 |
| **Open Questions** | OQ-10 |
| **Notes** | Other CLI verbs not evidenced — out of scope for this story. |

---

#### US-008 — VS Code Ask ContextOS Entry (<3 Clicks)

| Field | Content |
|-------|---------|
| **Story ID** | US-008 |
| **Title** | VS Code Ask ContextOS Under Three Clicks |
| **Epic** | EP-004 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P0 |
| **User Story** | As a **Developer**, I want to invoke Ask ContextOS from VS Code in fewer than three clicks, so that context retrieval fits daily IDE flow. |
| **Business Value** | Primary MVP IDE outcome (BO-01; §10 IDE integration). |
| **Acceptance Criteria** | **Given** the ContextOS VS Code extension is installed and connected to the orchestrator with an indexed workspace **When** I invoke Ask ContextOS **Then** I can complete the ask initiation in <3 clicks (BRD §10). **Given** a successful ask **When** context returns **Then** I receive symbol-accurate context suitable for MVP exit (<2s symbol-accurate context in IDE per BRD §15) under stated POC conditions. |
| **Dependencies** | US-003, US-005 |
| **Source Evidence** | BRD §10 IDE integration; §15 MVP; ADR-007 |
| **Assumptions** | A-02 |
| **Open Questions** | None blocking |
| **Notes** | Extension owns DX only; orchestration remains in FastAPI (constitution V). |

---

#### US-009 — Rename Scope Analysis

| Field | Content |
|-------|---------|
| **Story ID** | US-009 |
| **Title** | Safe Rename Scope Analysis |
| **Epic** | EP-003 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P1 |
| **User Story** | As a **Developer**, I want ContextOS to compute safe rename scope and breaking-change count before rename execution, so that refactors do not silently break callers. |
| **Business Value** | Reduces regression risk from renames (BO-03; FR-06). |
| **Acceptance Criteria** | **Given** a symbol selected for rename analysis **When** rename scope analysis runs via Serena-backed capabilities **Then** the system reports safe rename scope and a breaking-change count before rename execution. **Given** analysis completes **When** results are shown in the IDE surface **Then** the developer can review scope prior to executing rename (execution sandboxing remains out of scope per BRD §6). |
| **Dependencies** | US-005, US-006 |
| **Source Evidence** | BRD FR-06 |
| **Assumptions** | None |
| **Open Questions** | None blocking |
| **Notes** | Analysis only; ContextOS does not claim a code-execution sandbox. |

---

#### US-010 — Pack Context & Safe Edit Plan

| Field | Content |
|-------|---------|
| **Story ID** | US-010 |
| **Title** | Right-Click Pack Context & Serena Safe Edit Plan |
| **Epic** | EP-003 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P1 |
| **User Story** | As a **Developer**, I want to right-click → Pack Context and receive a safe edit plan via Serena LSP, so that I get precise edits rather than whole-file rewrites. |
| **Business Value** | Matches BRD §11 Developer use case; improves edit safety (BO-03). |
| **Acceptance Criteria** | **Given** a file/symbol selection in VS Code with ContextOS installed **When** I invoke Pack Context (right-click or equivalent command) **Then** the system packs relevant context and provides a Serena-informed safe edit plan rather than an indiscriminate whole-file rewrite directive. **Given** packed context is returned **When** citations are present **Then** provenance includes file:line and confidence as described in BRD §14 (exact JSON shape `[NEEDS CLARIFICATION: OQ-11]`). |
| **Dependencies** | US-004, US-005, US-008 |
| **Source Evidence** | BRD §11 Developer; §14 Pack & Cite; FR-03..FR-06 |
| **Assumptions** | None |
| **Open Questions** | OQ-11 |
| **Notes** | — |

---

#### US-011 — Auto-Index on Extension Install

| Field | Content |
|-------|---------|
| **Story ID** | US-011 |
| **Title** | Auto-Index Repository on VS Code Install |
| **Epic** | EP-001 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P1 |
| **User Story** | As a **Developer**, I want the extension to auto-index the repository on install, so that Ask ContextOS works without a manual indexing ceremony. |
| **Business Value** | MVP onboarding friction reduction (BO-01; §10/§14). |
| **Acceptance Criteria** | **Given** the VS Code extension is installed on a workspace **When** install/activation indexing runs **Then** the repository is indexed into the local stores used for MVP (Qdrant embeddings; graph nodes may be deferred to V1). **Given** BRD illustrative timing for small repos **When** indexing ~200 files **Then** experience aligns with BRD “10 sec for 200 files” illustrative target where hardware permits, without inventing a stricter global SLA beyond §10 monorepo targets. |
| **Dependencies** | US-001, US-002 |
| **Source Evidence** | BRD §10 IDE integration; §14 On Install; §15 |
| **Assumptions** | A-01, A-04 |
| **Open Questions** | None blocking |
| **Notes** | Progress/cancellation UX owned by extension (constitution V). |

---

#### US-012 — Incremental Re-Index on File Save

| Field | Content |
|-------|---------|
| **Story ID** | US-012 |
| **Title** | Incremental Re-Index on File Save |
| **Epic** | EP-001 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P1 |
| **User Story** | As a **Developer**, I want ContextOS to re-index on file save, so that search stays fresh as I edit. |
| **Business Value** | Keeps retrieval trustworthy during active development (BO-01; indexing SLAs). |
| **Acceptance Criteria** | **Given** an already indexed repository **When** I save a file in VS Code **Then** ContextOS triggers incremental re-index for the changed scope. **Given** BRD delta guidance **When** delta indexing runs for stated scales **Then** delta indexing targets include <60s for a 100-file delta and illustrative ~0.5s for single-file save where applicable (BRD §5 L1 / §10 / §14 — L5 path applies in MVP). **Given** trigger API detail **When** implementation is specified **Then** it may reuse `POST /index` with narrower scope (`[NEEDS CLARIFICATION: OQ-14]`). |
| **Dependencies** | US-011 |
| **Source Evidence** | BRD §6 auto/incremental indexing; §10; §14 On File Save |
| **Assumptions** | A-01 |
| **Open Questions** | OQ-14 |
| **Notes** | Mitigates index drift risk (BRD §13) for MVP search corpus. |

---

#### US-013 — Indexing Ignore Rules & Secret Exclusion

| Field | Content |
|-------|---------|
| **Story ID** | US-013 |
| **Title** | Respect `.gitignore`, Exclude `.env` & Secrets |
| **Epic** | EP-005 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P1 |
| **User Story** | As a **Security** stakeholder, I want indexing to respect `.gitignore` and exclude `.env`, secrets, build outputs, dependency folders, and binaries, so that sensitive and useless artifacts are not indexed. |
| **Business Value** | Non-negotiable privacy default for trust and compliance posture (constitution III). |
| **Acceptance Criteria** | **Given** a repository containing ignored paths (e.g., `.env`, `node_modules`, `dist`, `.git`) and binaries **When** indexing runs **Then** those paths are not included in packs/embeddings. **Given** an attempt to index excluded secret material **When** the indexer walks the tree **Then** `.env` and secret patterns remain excluded unless explicitly approved (BRD/constitution — approval workflow detail Not evidenced in provided inputs). |
| **Dependencies** | US-001 |
| **Source Evidence** | BRD FR-01; §10; Appendix C; constitution III; ADR-012 |
| **Assumptions** | None |
| **Open Questions** | Explicit “approved override” UX Not evidenced |
| **Notes** | Clients must not bypass orchestrator ignore policy. |

---

#### US-014 — Health Endpoint & Degraded Search

| Field | Content |
|-------|---------|
| **Story ID** | US-014 |
| **Title** | Orchestrator Health & Graceful Degraded Search |
| **Epic** | EP-005 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P1 |
| **User Story** | As a **DevOps/SRE**, I want a health endpoint reporting pipeline and store status with graceful degraded search on partial index, so that operators can detect failures without total outage of discovery. |
| **Business Value** | Supports 99.5% indexer availability target and operability (BRD §10). |
| **Acceptance Criteria** | **Given** the orchestrator is running **When** I call `GET /` **Then** I receive health information including pipeline readiness and Qdrant status (Falkor status may report absent/unused in MVP without failing search — A-07). **Given** a partial index or partial dependency failure **When** search is requested **Then** the system provides graceful degraded search rather than hard-failing all discovery when degradation is possible (BRD §10). |
| **Dependencies** | US-002, US-003 |
| **Source Evidence** | BRD Appendix D `GET /`; §10 indexer availability; api-contract §2.1 |
| **Assumptions** | A-07 |
| **Open Questions** | Exact HTTP status code mapping Not evidenced (Proposed in api-contract) |
| **Notes** | — |

---

#### US-015 — Provenance Citations in Packed Context

| Field | Content |
|-------|---------|
| **Story ID** | US-015 |
| **Title** | Provenance Citations on Packed Context |
| **Epic** | EP-002 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P1 |
| **User Story** | As a **Developer**, I want packed context to include citations with file:line and confidence, so that I can verify where AI context came from. |
| **Business Value** | Trust and auditability of SDLC intelligence outputs (constitution III provenance). |
| **Acceptance Criteria** | **Given** a successful `POST /context` (or IDE/CLI ask) response **When** `final_context` is inspected **Then** citations include file:line and confidence as described in BRD §14. **Given** citation machine shape is not fully specified **When** specs are written **Then** exact JSON citation schema is marked `[NEEDS CLARIFICATION: OQ-11]` without inventing fields. |
| **Dependencies** | US-003, US-004 |
| **Source Evidence** | BRD §14 Pack & Cite; constitution III |
| **Assumptions** | None |
| **Open Questions** | OQ-11 |
| **Notes** | — |

---

#### US-016 — Query-Time External LLM Consent

| Field | Content |
|-------|---------|
| **Story ID** | US-016 |
| **Title** | Query-Time External LLM Consent Gate |
| **Epic** | EP-005 |
| **Priority** | P1 |
| **MVP Classification** | MVP — P1 |
| **User Story** | As a **Security** stakeholder, I want query-time use of external LLM providers to require explicit consent/configuration, so that compressed context is not sent to third parties without agreement. |
| **Business Value** | Completes privacy model: local index, consented query-time LLM (Appendix C). |
| **Acceptance Criteria** | **Given** a user/workspace without consent/configuration for external LLM **When** a flow would send context to an external provider **Then** the system does not send code/context to that provider. **Given** explicit consent/configuration is present **When** query-time LLM use is invoked **Then** only the allowed compressed/packed context path may be used (BRD Appendix C privacy narrative). **Given** local options such as Ollama are configured **When** users choose local inference **Then** ContextOS may operate without external exfil (BRD Appendix C). |
| **Dependencies** | US-003 |
| **Source Evidence** | BRD Appendix C; §10; constitution III; ADR-012 |
| **Assumptions** | A-03 |
| **Open Questions** | Exact consent UX/storage mechanism Not evidenced beyond “consent flag/configuration” |
| **Notes** | Index path remains no-exfil (US-002). |

---

### P2 (V1)

---

#### US-017 — Structural Graph Generation

| Field | Content |
|-------|---------|
| **Story ID** | US-017 |
| **Title** | Typed Structural Graph Generation (L1) |
| **Epic** | EP-006 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **Staff Engineer**, I want ContextOS to build a typed structural graph (File→Module→Class→Method→Call) with incremental indexing, so that dependency analysis meets indexing SLAs. |
| **Business Value** | Enables blast radius and safer changes (BO-03; FR-07). |
| **Acceptance Criteria** | **Given** a repository indexed for L1 **When** structural graph generation runs **Then** a typed graph File→Module→Class→Method→Call is stored in FalkorDB using tree-sitter/regex import extraction as evidenced. **Given** a 100-file delta **When** incremental indexing runs **Then** incremental indexing completes in <60s (BRD FR-07 / §10). **Given** full monorepo indexing targets **When** measuring 1M LOC **Then** full index <15 minutes where L5+L1 apply (BRD §10). |
| **Dependencies** | US-011, US-012 |
| **Source Evidence** | BRD FR-07; §10; §15 V1; ADR-004 |
| **Assumptions** | A-01 |
| **Open Questions** | None blocking |
| **Notes** | — |

---

#### US-018 — Blast Radius Analysis

| Field | Content |
|-------|---------|
| **Story ID** | US-018 |
| **Title** | Transitive Blast Radius Analysis |
| **Epic** | EP-007 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **Developer**, I want transitive blast radius for a change (affected services, tests, owners, risk), so that I know what breaks before I merge. |
| **Business Value** | Core change-safety outcome; supports ↓40% regression objective (BO-03; FR-08). |
| **Acceptance Criteria** | **Given** an L1-indexed repo **When** I call `GET /blast/{file_name}?repo=` **Then** the response includes `direct_dependents`, `transitive`, `db_tables`, `risk` in {HIGH, MEDIUM, LOW}, and `tests_to_run` per FR-08. **Given** owners are required by FR-08 prose **When** response is designed **Then** owners are included with shape `[NEEDS CLARIFICATION: OQ-15]`. **Given** NFR conditions (3-hop, 10k nodes) **When** latency is measured **Then** blast-radius graph query p95 is <2s (BRD §10). **Given** success metrics **When** blast accuracy is evaluated **Then** correct affected tests predicted >95% where harness applies (BRD §12). |
| **Dependencies** | US-017 |
| **Source Evidence** | BRD FR-08; §10; §12; Appendix D; §11 Developer |
| **Assumptions** | None |
| **Open Questions** | OQ-15 |
| **Notes** | Also available via `POST /context` `blast_radius` field in V1 (api-contract). |

---

#### US-019 — Interactive `graph.html` Visualization

| Field | Content |
|-------|---------|
| **Story ID** | US-019 |
| **Title** | Live Dependency Graph via `graph.html` |
| **Epic** | EP-007 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **Developer**, I want an interactive dependency graph page for a repo, so that I can explore structural relationships visually. |
| **Business Value** | Makes L1 actionable for design/maintenance (FR-09; BO-04). |
| **Acceptance Criteria** | **Given** an L1-indexed repo **When** I open `GET /graph.html?repo=` **Then** I receive an interactive vis-network graph with nodes as files and edges as IMPORTS. **Given** BRD visual guidance **When** the page renders **Then** physics is disabled, arrows are shown, node color `#64748b`, background `#0f172a` as evidenced. **Given** depth exploration needs **When** viewing a symbol/service subgraph **Then** interactive depth 1–5 is supported per FR-09. |
| **Dependencies** | US-017 |
| **Source Evidence** | BRD FR-09; §14 graph.html example; ADR-010 |
| **Assumptions** | None |
| **Open Questions** | Auth for HTML embedding NEEDS CLARIFICATION (api-contract) |
| **Notes** | — |

---

#### US-020 — VS Code React Flow Graph / Blast Panel

| Field | Content |
|-------|---------|
| **Story ID** | US-020 |
| **Title** | VS Code Webview Graph & Blast Visualization |
| **Epic** | EP-007 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **Developer**, I want blast radius and dependency views inside VS Code via React Flow Webviews, so that I can inspect risk without leaving the IDE. |
| **Business Value** | V1 IDE visualization deliverable (BRD §5, §15). |
| **Acceptance Criteria** | **Given** V1 extension features enabled and L1 data available **When** I open the ContextOS graph/blast panel **Then** I can interact with dependency/blast visualization powered by React Flow in a VS Code Webview. **Given** graph data may be stale after large PRs **When** staleness is known **Then** UX can surface staleness (paired with US-027). |
| **Dependencies** | US-018, US-019 |
| **Source Evidence** | BRD FR-09; §14; §15 live blast radius visualization |
| **Assumptions** | None |
| **Open Questions** | None blocking |
| **Notes** | Sanitize Webview messages (constitution III). |

---

#### US-021 — Codebase Memory Cache for Structural NL Queries

| Field | Content |
|-------|---------|
| **Story ID** | US-021 |
| **Title** | Hot Entity Cache & Natural-Language Structural Queries |
| **Epic** | EP-006 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **Developer**, I want natural-language structural queries such as “where is auth validated?” answered from a hot-entity codebase memory cache, so that structural questions are fast. |
| **Business Value** | FR-10 structural NL answers; supports BO-04. |
| **Acceptance Criteria** | **Given** L1 graph and codebase-memory-mcp capabilities **When** I ask structural NL questions like “where is auth validated?” or “what is blast radius of PaymentService.refund()” **Then** the system answers using cached hot entities / structural knowledge as described in FR-10. **Given** integration boundary is unclear **When** specifying the feature **Then** FastAPI vs MCP ownership is clarified (`[NEEDS CLARIFICATION: OQ-06]`) without inventing APIs. |
| **Dependencies** | US-017, US-018 |
| **Source Evidence** | BRD FR-10 |
| **Assumptions** | None |
| **Open Questions** | **OQ-06 (blocking for contract detail)** |
| **Notes** | — |

---

#### US-022 — Per-Phase Token Budget Enforcement

| Field | Content |
|-------|---------|
| **Story ID** | US-022 |
| **Title** | Per-Phase Token Budget Enforcement |
| **Epic** | EP-008 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As an **AI Platform Lead**, I want Headroom-style enforcement of per-phase token budgets with hard-fail and degradation policy, so that prompts stay within cost/context limits. |
| **Business Value** | Directly supports BO-02 token/cost reduction control plane (FR-11). |
| **Acceptance Criteria** | **Given** a configured SDLC phase budget **When** context compression/packing would exceed the budget **Then** the Headroom engine enforces the budget with hard-fail and degradation policy as stated in FR-11. **Given** FR-11 examples Dev=12k and Design=32k and §5 example Dev=8k **When** budgets are configured **Then** canonical values are resolved (`[NEEDS CLARIFICATION: OQ-07]`) before treating a specific number as normative in tests. |
| **Dependencies** | US-004, US-023 |
| **Source Evidence** | BRD FR-11; §5 L4; §15 V1 |
| **Assumptions** | A-03, A-06 |
| **Open Questions** | **OQ-07 (blocking for numeric AC)** |
| **Notes** | — |

---

#### US-023 — Adaptive Summarization with Recall Gate

| Field | Content |
|-------|---------|
| **Story ID** | US-023 |
| **Title** | Adaptive Summarization Preserving Symbols |
| **Epic** | EP-008 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **Developer**, I want low-relevance files compressed via adaptive summarization that preserves symbols, types, and TODOs, so that I pay far fewer tokens without losing critical detail. |
| **Business Value** | 60–95% token savings / illustrative 85k→7.2k (BO-02; FR-12). |
| **Acceptance Criteria** | **Given** a large naive pack **When** L4 adaptive summarization runs **Then** token savings are in the 60–95% range versus naive packing while preserving symbols, types, and TODOs as stated. **Given** quality gates **When** recall@10 is measured on compressed context utility **Then** recall@10 >0.92 (BRD §10). **Given** compression risk of dropping key symbols **When** validation runs **Then** symbol-preservation tests / recall gate apply (BRD §13 mitigation). |
| **Dependencies** | US-003, US-005 |
| **Source Evidence** | BRD FR-12; §10; §12; §13; §15 V1 |
| **Assumptions** | A-03; query-time LLM summarization requires consent (US-016) when external |
| **Open Questions** | None blocking |
| **Notes** | Illustrative 91% saving is success metric, not a separate feature. |

---

#### US-024 — Compression Telemetry & Token Cost Dashboard

| Field | Content |
|-------|---------|
| **Story ID** | US-024 |
| **Title** | Compression Telemetry & Token Cost Dashboard |
| **Epic** | EP-008 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As an **AI Platform Lead**, I want compression ratio, recall@k, and cost-saved emitted to observability and shown on a token dashboard, so that savings are measurable. |
| **Business Value** | Makes BO-02 outcomes visible; V1 exit criterion (FR-13; §15). |
| **Acceptance Criteria** | **Given** L4 compression requests **When** telemetry is emitted **Then** metrics include compression ratio, recall@k, and cost-saved per request (FR-13) via OpenTelemetry-compatible instrumentation. **Given** dashboard artifact naming in BRD **When** operators view costs **Then** `contextos_token_dashboard.html` (or equivalent evidenced dashboard) shows before/after token cost (`[NEEDS CLARIFICATION: OQ-08 serving mechanism]`; `[NEEDS CLARIFICATION: OQ-09 exporter vendor]`). **Given** `POST /context` metrics fields **When** V1 compression runs **Then** `tokens_before`, `tokens_after`, `saving_percent` are populated meaningfully. |
| **Dependencies** | US-023 |
| **Source Evidence** | BRD FR-13; §10 Observability; Appendix D metrics fields; ADR-011 |
| **Assumptions** | None |
| **Open Questions** | OQ-08, OQ-09 |
| **Notes** | Telemetry opt-out must not be silently bypassed (constitution V); opt-out API Missing Evidence. |

---

#### US-025 — PR Risk Bot Basics

| Field | Content |
|-------|---------|
| **Story ID** | US-025 |
| **Title** | PR Risk Bot: Affected Tests & Owners |
| **Epic** | EP-009 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **Developer**, I want a PR risk bot that automatically surfaces affected tests and owners from blast-radius analysis, so that reviews catch downstream breakage earlier. |
| **Business Value** | V1 deliverable for change safety (BRD §15 PR risk bot; BO-03). |
| **Acceptance Criteria** | **Given** a PR/diff against an L1-indexed repo **When** PR risk analysis runs **Then** ContextOS reports affected tests and owners derived from blast-radius capabilities (FR-08 / §15). **Given** risk classification exists **When** results are shown **Then** risk is communicated using the evidenced HIGH\|MEDIUM\|LOW model where applicable. **Given** CI delivery mechanism **When** GitHub Action is not yet specified **Then** this story may deliver bot/analysis via evidenced API/IDE surfaces first; Action-specific wiring is US-043. |
| **Dependencies** | US-018 |
| **Source Evidence** | BRD §15 V1; FR-08; §11 Developer |
| **Assumptions** | None |
| **Open Questions** | OQ-15; Action payload deferred to OQ-04/US-043 |
| **Notes** | — |

---

#### US-026 — QA Regression Test Suggestions from Graph Diff

| Field | Content |
|-------|---------|
| **Story ID** | US-026 |
| **Title** | Suggest Regression Tests from L1 Graph Diff |
| **Epic** | EP-009 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **QA Engineer**, I want ContextOS to suggest regression tests based on L1 graph diff between main and PR, so that test selection follows real dependencies. |
| **Business Value** | BRD §11 QA use case; supports ↓40% regression defects (BO-03). |
| **Acceptance Criteria** | **Given** main and PR revisions with L1 graphs available **When** QA requests regression suggestions **Then** ContextOS suggests tests based on L1 graph diff / blast-radius affected tests. **Given** suggestions are produced **When** QA reviews them **Then** provenance ties suggestions to graph/diff evidence (not opaque lists). |
| **Dependencies** | US-018, US-025 |
| **Source Evidence** | BRD §11 QA Engineer; FR-08; §8 Testing phase |
| **Assumptions** | None |
| **Open Questions** | Exact diff API Not evidenced — use blast/graph capabilities without inventing endpoints |
| **Notes** | — |

---

#### US-027 — Index Staleness Badge

| Field | Content |
|-------|---------|
| **Story ID** | US-027 |
| **Title** | Graph/Search Index Staleness Badge |
| **Epic** | EP-007 |
| **Priority** | P2 |
| **MVP Classification** | Not MVP — V1 |
| **User Story** | As a **Developer**, I want a staleness badge when the graph/index may have drifted after large PRs, so that I do not trust outdated blast-radius results blindly. |
| **Business Value** | Mitigates BRD §13 graph index drift risk. |
| **Acceptance Criteria** | **Given** index freshness metadata is available **When** graph/blast/search UI is shown and data may be stale **Then** a staleness badge (or equivalent clear warning) is displayed. **Given** delta indexing completes **When** freshness is restored **Then** the staleness warning clears. |
| **Dependencies** | US-012, US-018, US-020 |
| **Source Evidence** | BRD §13 Risks mitigation “Delta indexing + staleness badge” |
| **Assumptions** | None |
| **Open Questions** | Exact freshness threshold Not evidenced |
| **Notes** | — |

---

### P3 (V2)

---

#### US-028 — Multi-modal Artifact Ingestion

| Field | Content |
|-------|---------|
| **Story ID** | US-028 |
| **Title** | Multi-modal Ingestion (Docs, SQL, OpenAPI, Images, Transcripts) |
| **Epic** | EP-010 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Staff Engineer**, I want Graphify-style ingestion of markdown, ADRs, SQL DDL, OpenAPI, images, and Loom transcripts into a property graph with embeddings, so that non-code SDLC artifacts participate in retrieval. |
| **Business Value** | Enables Requirements/Design/Maintenance multi-modal intelligence (FR-14; BO-04). |
| **Acceptance Criteria** | **Given** supported artifact types listed in FR-14 **When** multi-modal ingestion runs **Then** artifacts are ingested into a property graph with embeddings. **Given** external systems (Notion/Confluence/Jira/Figma/Slack/Loom) **When** connectors are enabled **Then** auth/scopes must be defined (`[NEEDS CLARIFICATION: OQ-03]`) — do not invent OAuth details. **Given** PII may appear in transcripts/docs **When** ingesting **Then** PII redaction controls apply on multi-modal paths (constitution III). |
| **Dependencies** | US-017 (code graph anchoring preferred) |
| **Source Evidence** | BRD FR-14; §5 L2; §15 V2 |
| **Assumptions** | None |
| **Open Questions** | **OQ-03 (blocking for connector-specific AC)** |
| **Notes** | Video frame OCR mentioned in L2 capabilities — in scope as FR-14/L2 capability language. |

---

#### US-029 — Cross-Artifact Entity Linking

| Field | Content |
|-------|---------|
| **Story ID** | US-029 |
| **Title** | Auto-Link Code Symbols to Docs, SQL, Diagrams, Tickets |
| **Epic** | EP-010 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Product Manager**, I want code symbols auto-linked to docs/diagrams/SQL/tickets, so that discovery spans the full SDLC graph. |
| **Business Value** | FR-15 tribal knowledge linking; BO-04. |
| **Acceptance Criteria** | **Given** ingested code and multi-modal entities **When** entity resolution runs **Then** the system auto-links examples of the form UserService ↔ users table ↔ ADR-014 ↔ JIRA-123 ↔ Figma as stated in FR-15. **Given** a linked entity **When** inspected **Then** links are explorable in graph experiences without inventing unsupported tools. |
| **Dependencies** | US-028 |
| **Source Evidence** | BRD FR-15; §5 L2 |
| **Assumptions** | None |
| **Open Questions** | OQ-03 may limit which external nodes appear |
| **Notes** | — |

---

#### US-030 — PM Multi-Modal Discovery Query

| Field | Content |
|-------|---------|
| **Story ID** | US-030 |
| **Title** | PM Query: Services Touching Checkout with Docs & Diagrams |
| **Epic** | EP-010 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Product Manager**, I want to ask “what services touch checkout?” and receive code + docs + diagram links, so that I can write accurate PRDs. |
| **Business Value** | Direct BRD §11 PM use case; onboarding/discovery acceleration (BO-04). |
| **Acceptance Criteria** | **Given** L2 links and searchable packs available **When** a PM asks what services touch checkout **Then** results include code plus docs/diagram links as available in the graph. **Given** answer latency goals for discovery **When** measuring “where is X used?” class questions **Then** time-to-answer targets <5 sec vs prior 2 hrs where platform SLAs apply (BRD §12 / BO-04). |
| **Dependencies** | US-003, US-029 |
| **Source Evidence** | BRD §11 Product Manager; §3 BO-04 |
| **Assumptions** | None |
| **Open Questions** | OQ-03 |
| **Notes** | — |

---

#### US-031 — Entity Memory Store

| Field | Content |
|-------|---------|
| **Story ID** | US-031 |
| **Title** | Persistent Entity Memory Store |
| **Epic** | EP-011 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As an **AI Platform Lead**, I want entities (Person, Service, Decision, Incident) stored with temporal edges and source provenance, so that agents retain durable SDLC knowledge. |
| **Business Value** | Foundation for BO-05 persistent teammates (FR-16). |
| **Acceptance Criteria** | **Given** memory write events **When** entities are stored via Cognee-style memory **Then** entity types include Person, Service, Decision, Incident with temporal edges and source provenance. **Given** an example decision memory **When** stored **Then** content of the form “We rejected Auth0 in Sprint 12…” with provenance is representable (FR-16 example). |
| **Dependencies** | None beyond V2 platform readiness |
| **Source Evidence** | BRD FR-16; §5 L6; §15 V2 |
| **Assumptions** | None |
| **Open Questions** | Underlying Cognee persistence engine detail Missing Evidence (tech-stack) |
| **Notes** | — |

---

#### US-032 — Cross-Session Memory Recall

| Field | Content |
|-------|---------|
| **Story ID** | US-032 |
| **Title** | Cross-Session Memory Recall with Explanation |
| **Epic** | EP-011 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Developer**, I want relevant memories recalled for my task with an explanation of why (source + timestamp), so that agents do not repeat rejected decisions. |
| **Business Value** | BO-05; FR-17; Appendix A/B demo outcomes. |
| **Acceptance Criteria** | **Given** stored memories relevant to a task query **When** recall runs **Then** relevant memories are returned with explanation including source and timestamp. **Given** NFR/KPI targets **When** measured **Then** cross-session memory recall is >90% with p95 <1.2s (BRD §10, §12). **Given** `POST /context` **When** V2 is enabled **Then** the `memory` response field is populated (api-contract). |
| **Dependencies** | US-031 |
| **Source Evidence** | BRD FR-17; §10; §12; Appendix A/B |
| **Assumptions** | None |
| **Open Questions** | None blocking |
| **Notes** | — |

---

#### US-033 — Memory Governance (TTL, Pin/Forget, PII)

| Field | Content |
|-------|---------|
| **Story ID** | US-033 |
| **Title** | Memory Governance: TTL, Decay, Pin/Forget, PII Redaction |
| **Epic** | EP-011 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Security** stakeholder, I want TTL, decay, manual pin/forget, and PII redaction for memory entries, so that memory does not become a PII or bloat liability. |
| **Business Value** | FR-18; mitigates BRD §13 memory PII/bloat risk. |
| **Acceptance Criteria** | **Given** memory entries **When** governance policies apply **Then** TTL, decay, manual pin, and forget are supported, and PII redaction is applied. **Given** BRD references `.github/copilot-instructions.md` guidance patterns **When** governance links to workspace guidance **Then** Passport.js-style guidance can be reflected as evidenced in FR-18/Appendix B without inventing write-back automation (`[NEEDS CLARIFICATION: OQ-17]`). |
| **Dependencies** | US-031 |
| **Source Evidence** | BRD FR-18; §13; Appendix B; constitution III |
| **Assumptions** | None |
| **Open Questions** | OQ-17; OQ-19 |
| **Notes** | HTTP shapes for pin/forget Not evidenced — Proposed only. |

---

#### US-034 — PM Recall of Past Decisions

| Field | Content |
|-------|---------|
| **Story ID** | US-034 |
| **Title** | Recall Past Architecture Decisions During Spec Review |
| **Epic** | EP-011 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Product Manager**, I want ContextOS to recall past decisions such as “why we rejected Kafka for checkout” during spec review, so that PRDs respect prior choices. |
| **Business Value** | BRD §11 PM L6 use case; reduces rework (BO-05). |
| **Acceptance Criteria** | **Given** a stored Decision entity about a past rejection/choice **When** a PM asks during spec review **Then** ContextOS recalls the decision with provenance explanation (source + timestamp). |
| **Dependencies** | US-032 |
| **Source Evidence** | BRD §11 Product Manager (L6) |
| **Assumptions** | None |
| **Open Questions** | None blocking |
| **Notes** | — |

---

#### US-035 — Developer Task Ask with Memory + Blast Context

| Field | Content |
|-------|---------|
| **Story ID** | US-035 |
| **Title** | Task Ask Returning Preferred Pattern, Blast Radius, and Tests |
| **Epic** | EP-011 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Developer**, I want to ask “Add Google SSO to Payment Service” and get the preferred library from memory plus blast radius (services/tests), so that I do not break QA or revive rejected vendors. |
| **Business Value** | BRD §11 Developer + Appendix A end-to-end outcome (BO-03, BO-05). |
| **Acceptance Criteria** | **Given** L6 memory contains an Auth0 rejection / Passport.js preference and L1 blast data exists **When** I ask to add Google SSO to Payment Service **Then** results prefer the remembered pattern (e.g., Passport.js not Auth0) and include blast-radius style impact (illustrative: 3 services, 12 tests) when graph data supports it. **Given** compressed context is also requested **When** L4 is enabled **Then** token cost narrative aligns with compression stories without duplicating US-023. |
| **Dependencies** | US-018, US-023, US-032 |
| **Source Evidence** | BRD §11 Developer; Appendix A |
| **Assumptions** | None |
| **Open Questions** | None blocking |
| **Notes** | Composite story; still independently testable with fixtures for memory + graph. |

---

#### US-036 — QA Query for PII-Reading Flows

| Field | Content |
|-------|---------|
| **Story ID** | US-036 |
| **Title** | Query Flows that Read PII via L2 Links |
| **Epic** | EP-010 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **QA Engineer**, I want to query “show flows that read PII” via L2 graph linking code ↔ SQL ↔ OpenAPI, so that privacy-sensitive paths are testable. |
| **Business Value** | BRD §11 QA L2 use case; security/quality intersection. |
| **Acceptance Criteria** | **Given** linked code/SQL/OpenAPI artifacts **When** QA queries for flows that read PII **Then** ContextOS returns flows grounded in L2 links across code ↔ SQL ↔ OpenAPI. **Given** PII taxonomy is not fully specified **When** classifying PII **Then** use `[NEEDS CLARIFICATION: OQ-19]` rather than inventing categories. |
| **Dependencies** | US-029 |
| **Source Evidence** | BRD §11 QA Engineer |
| **Assumptions** | None |
| **Open Questions** | OQ-19 |
| **Notes** | — |

---

#### US-037 — SRE Deployment Risk & Unified Ops Search

| Field | Content |
|-------|---------|
| **Story ID** | US-037 |
| **Title** | Deployment Risk Score & Hybrid Search over Infra, Runbooks, Incidents |
| **Epic** | EP-012 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **DevOps/SRE**, I want a deployment risk score from L1 dependency depth plus L6 incident memory, and hybrid search across infra-as-code, runbooks, and past incidents, so that releases and ops discovery use structural and historical context together. |
| **Business Value** | Covers both BRD §11 SRE use cases; Deployment phase value (BRD §8). |
| **Acceptance Criteria** | **Given** L1 dependency depth signals and L6 incident memories **When** deployment risk is requested **Then** ContextOS computes a deployment risk score from those evidenced inputs. **Given** scoring weights are not specified **When** implementing **Then** mark `[NEEDS CLARIFICATION: OQ-18]` rather than inventing a proprietary formula as BRD fact. **Given** infra-as-code, runbooks, and incident artifacts are indexed/linked (L5+L6; L2 where ingested) **When** an SRE runs hybrid search **Then** results can span infra + runbooks + past incidents in one search experience as stated in §11. |
| **Dependencies** | US-003, US-018, US-028, US-032 |
| **Source Evidence** | BRD §11 DevOps/SRE; §8 Deployment |
| **Assumptions** | None |
| **Open Questions** | OQ-18 |
| **Notes** | Combines §11 risk + unified ops search without inventing new HTTP endpoints. |

---

#### US-038 — Enterprise RBAC per Repo Path

| Field | Content |
|-------|---------|
| **Story ID** | US-038 |
| **Title** | RBAC Enforcement per Repository Path |
| **Epic** | EP-012 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Security** stakeholder, I want RBAC enforced per repository path for ContextOS operations, so that sensitive paths are not globally readable via search/graph/memory. |
| **Business Value** | BRD §10 / V2 enterprise hardening; constitution III. |
| **Acceptance Criteria** | **Given** RBAC policies per repo path **When** a user lacks access to a path **Then** indexing/search/graph/memory results for that path are denied or omitted according to policy. **Given** role/path/authn schema is unspecified **When** writing detailed AC/tests **Then** treat as `[NEEDS CLARIFICATION: OQ-01]` — do not invent roles. |
| **Dependencies** | US-013 |
| **Source Evidence** | BRD §10 Code access & PII; §15 V2 Enterprise RBAC; ADR-012 |
| **Assumptions** | A-05 until authn defined |
| **Open Questions** | **OQ-01 (blocking)** |
| **Notes** | — |

---

#### US-039 — VPC Deployment Hardening

| Field | Content |
|-------|---------|
| **Story ID** | US-039 |
| **Title** | VPC-Friendly Enterprise Deployment Hardening |
| **Epic** | EP-012 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **DevOps/SRE**, I want ContextOS deployable with VPC-oriented hardening using local FalkorDB + Qdrant and no unauthorized code exfil, so that Security can approve enterprise indexing. |
| **Business Value** | Addresses BRD §13 VPC security approval risk; V2 enterprise exit. |
| **Acceptance Criteria** | **Given** enterprise/VPC deployment mode **When** ContextOS is deployed **Then** graph/vector stores run in the approved local/VPC-friendly pattern and indexing still performs no unauthorized external LLM exfil. **Given** air-gapped on-prem without enterprise tier is out of scope **When** scoping tiers **Then** boundaries are clarified (`[NEEDS CLARIFICATION: OQ-13]`) without claiming air-gap support prematurely (BRD §6). |
| **Dependencies** | US-002, US-016, US-038 |
| **Source Evidence** | BRD §6 OUT OF SCOPE air-gap clause; §13; §15 V2; ADR-013 |
| **Assumptions** | A-04 |
| **Open Questions** | **OQ-13 (blocking for tier boundary AC)** |
| **Notes** | Kubernetes Not evidenced for MVP/V1. |

---

#### US-040 — Onboarding Agent

| Field | Content |
|-------|---------|
| **Story ID** | US-040 |
| **Title** | Onboarding Agent for Faster Time-to-Productivity |
| **Epic** | EP-012 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **CTO/VP Eng**, I want an onboarding agent that leverages multi-modal graph and memory, so that new joiners reach first meaningful contribution faster. |
| **Business Value** | V2 exit: 3x / 60% faster onboarding (3 weeks → 5 days) per BRD §15/§12. |
| **Acceptance Criteria** | **Given** L2+L6 capabilities available **When** a new joiner uses the onboarding agent **Then** ContextOS helps answer discovery questions using multi-modal graph and persistent memory. **Given** success metrics **When** onboarding is measured **Then** targets align with 5 days vs 3 weeks (−60%) as organizational KPI (BRD §12) — measurement study design `[NEEDS CLARIFICATION: OQ-20 UX depth]`. |
| **Dependencies** | US-030, US-032 |
| **Source Evidence** | BRD §15 V2 Onboarding agent; §12 time to first meaningful PR; §8 Maintenance |
| **Assumptions** | None |
| **Open Questions** | OQ-20 |
| **Notes** | — |

---

#### US-041 — Role-Based Context Packs

| Field | Content |
|-------|---------|
| **Story ID** | US-041 |
| **Title** | Role-Based Context Packs for PM, Dev, QA, DevOps |
| **Epic** | EP-012 |
| **Priority** | P3 |
| **MVP Classification** | Not MVP — V2 |
| **User Story** | As a **Product Manager**, I want role-based context packs for PM, Dev, QA, and DevOps, so that each role receives SDLC context tuned to their responsibilities. |
| **Business Value** | Evidenced deliverable in BRD §5 “What ContextOS Delivers”. |
| **Acceptance Criteria** | **Given** role-based pack feature is enabled **When** a user selects or is mapped to PM, Dev, QA, or DevOps **Then** ContextOS assembles a role-oriented context pack. **Given** pack content schema is not specified **When** detailing AC **Then** mark `[NEEDS CLARIFICATION: OQ-05]` — do not invent field lists. |
| **Dependencies** | US-004, US-029, US-032 |
| **Source Evidence** | BRD §5 role-based context packs |
| **Assumptions** | None |
| **Open Questions** | **OQ-05 (blocking for pack schema AC)** |
| **Notes** | — |

---

### Future / Later

---

#### US-042 — JetBrains Extension Parity

| Field | Content |
|-------|---------|
| **Story ID** | US-042 |
| **Title** | JetBrains Extension Parity |
| **Epic** | EP-012 |
| **Priority** | Future |
| **MVP Classification** | Future — not MVP |
| **User Story** | As a **Developer**, I want ContextOS in JetBrains IDEs with comparable ask/index entry points, so that non-VS Code users gain SDLC intelligence. |
| **Business Value** | BRD §6 IN SCOPE IDE coverage; assumption 80%+ IDE coverage. |
| **Acceptance Criteria** | **Given** JetBrains extension is delivered post-MVP **When** a developer invokes Ask ContextOS equivalents **Then** core ask/index flows work against the same FastAPI orchestrator. **Given** timing ambiguity **When** planning **Then** respect `[NEEDS CLARIFICATION: OQ-02]` vs VS Code-first ADR-007. |
| **Dependencies** | US-007, US-008 (behavioral parity reference) |
| **Source Evidence** | BRD §6; §10 IDE integration; ADR-007 |
| **Assumptions** | A-02 |
| **Open Questions** | OQ-02 |
| **Notes** | Not an MVP blocker. |

---

#### US-043 — GitHub Action Integration

| Field | Content |
|-------|---------|
| **Story ID** | US-043 |
| **Title** | GitHub Action for CI Context / PR Risk Hooks |
| **Epic** | EP-012 |
| **Priority** | Future |
| **MVP Classification** | Future — not MVP |
| **User Story** | As a **DevOps/SRE**, I want a GitHub Action that invokes ContextOS in CI, so that PR risk and context checks run in pipelines. |
| **Business Value** | BRD §6 IN SCOPE; extends US-025 into CI. |
| **Acceptance Criteria** | **Given** a GitHub Action is configured **When** a supported CI event occurs **Then** ContextOS analysis is invoked for the repository/PR. **Given** trigger/payload schema is unspecified **When** specifying the Action **Then** mark `[NEEDS CLARIFICATION: OQ-04]` — do not invent webhook contracts. |
| **Dependencies** | US-025 |
| **Source Evidence** | BRD §6 GitHub Action; §14 CI webhook mention |
| **Assumptions** | None |
| **Open Questions** | **OQ-04 (blocking)** |
| **Notes** | — |

---

#### US-044 — SIP Docs Engine & Timeline

| Field | Content |
|-------|---------|
| **Story ID** | US-044 |
| **Title** | SIP Vision: Docs Engine & Timeline |
| **Epic** | EP-012 |
| **Priority** | Future |
| **MVP Classification** | Future — SIP Vision |
| **User Story** | As a **CTO/VP Eng**, I want a Docs Engine and Timeline as part of the longer SIP vision, so that ContextOS evolves toward an OS for software engineering. |
| **Business Value** | Long-term platform vision (BRD §15 SIP). |
| **Acceptance Criteria** | **Given** SIP vision timeframe (6–12 months in BRD) **When** Docs Engine and Timeline initiatives are funded **Then** capabilities align to BRD SIP deliverables without pulling them into MVP/V1/V2 exit criteria. **Given** detail is visionary **When** specifying now **Then** treat deep AC as Not evidenced beyond BRD §15 naming. |
| **Dependencies** | V2 platform foundation |
| **Source Evidence** | BRD §15 SIP - Vision |
| **Assumptions** | None |
| **Open Questions** | Scope depth Not evidenced |
| **Notes** | Explicitly long-term. |

---

#### US-045 — Plugin Marketplace & Multi-Agent Suite

| Field | Content |
|-------|---------|
| **Story ID** | US-045 |
| **Title** | Plugin Marketplace & Role Agents (SIP) |
| **Epic** | EP-012 |
| **Priority** | Future |
| **MVP Classification** | Future — SIP Vision |
| **User Story** | As a **CTO/VP Eng**, I want a plugin marketplace and expanded agent suite (PM, Architect, QA, DevOps, etc.), so that ContextOS becomes an extensible SIP battery for the engineering OS. |
| **Business Value** | BRD §15 SIP marketplace and 8 agents vision. |
| **Acceptance Criteria** | **Given** SIP phase **When** marketplace/agents are pursued **Then** delivery matches BRD vision naming (Plugin Marketplace; agents including PM, Architect, QA, DevOps among the stated eight) without inventing agent behaviors not in the BRD. **Given** MVP/V1/V2 **When** prioritizing **Then** this story remains Future and must not block earlier exits. |
| **Dependencies** | US-044 (vision sequencing) |
| **Source Evidence** | BRD §15 SIP - Vision |
| **Assumptions** | None |
| **Open Questions** | Exact eight-agent list beyond named examples Not fully enumerated in BRD prose |
| **Notes** | — |

---

## Story Dependencies

```text
MVP core:
  US-001 → US-002 → US-003 → US-004 → US-015
  US-001 → US-013
  US-005 → US-006 → US-009
  US-003 + US-005 → US-008 → US-010
  US-003 → US-007
  US-001 + US-002 → US-011 → US-012
  US-002 + US-003 → US-014
  US-003 → US-016
  US-004 + US-005 → US-010

V1:
  US-011/US-012 → US-017 → US-018 → US-019/US-020/US-025
  US-017 + US-018 → US-021
  US-018 → US-026
  US-012 + US-018 + US-020 → US-027
  US-003 + US-005 → US-023 → US-022
  US-023 → US-024
  US-018 → US-025 → US-026

V2:
  US-017 → US-028 → US-029 → US-030 / US-036
  US-031 → US-032 → US-033 / US-034
  US-018 + US-023 + US-032 → US-035
  US-003 + US-018 + US-028 + US-032 → US-037
  US-013 → US-038 → US-039
  US-030 + US-032 → US-040
  US-004 + US-029 + US-032 → US-041

Future:
  US-007/US-008 → US-042
  US-025 → US-043
  V2 foundation → US-044 → US-045
```

**Dependency rules:** Later-phase stories must not block MVP exit. Clarification-blocked stories (OQ-01, OQ-03..OQ-07, OQ-13) remain backlog-ready as drafts with explicit NEEDS CLARIFICATION in AC.

---

## Traceability Matrix

| Story ID | BRD Source | Requirement / Business Rule | Evidence | Status |
| -------- | ---------- | --------------------------- | -------- | ------ |
| US-001 | §9 FR-01; §5 L5 | Repo flattening & packing | FR-01; Appendix C | Covered |
| US-002 | §10; Appendix C | Local embeddings; no index-time LLM exfil | §10 Embedding; ADR-003 | Covered |
| US-003 | §9 FR-02; §10; §12 | Hybrid BM25+vector+MMR; p95 <800ms; recall@10 >0.92 | FR-02; NFR; KPI | Covered |
| US-004 | §9 FR-03; §15 | Phase-aware prompt templates | FR-03; MVP packing | Covered |
| US-005 | §9 FR-04; §15 | Symbol definition lookup; 99% accuracy claim | FR-04 | Covered (measure method OQ-12) |
| US-006 | §9 FR-05 | Find all references + call-site context | FR-05 | Covered |
| US-007 | §5; §15 | CLI `contextos ask` | MVP CLI | Covered |
| US-008 | §10; §15 | VS Code Ask <3 clicks; <2s symbol-accurate context | IDE NFR; MVP exit | Covered |
| US-009 | §9 FR-06 | Rename scope + breaking-change count | FR-06 | Covered |
| US-010 | §11 Developer; §14 | Pack Context + safe edit plan; citations | §11; Pack & Cite | Covered |
| US-011 | §10; §14 | Auto-index on install | IDE integration | Covered |
| US-012 | §6; §10; §14 | Incremental re-index on save; delta SLAs | Indexing NFR | Covered |
| US-013 | §9 FR-01; §10; constitution III | `.gitignore` / `.env` / secrets exclusion | Privacy NFR | Covered |
| US-014 | Appendix D; §10 | Health; degraded search; 99.5% availability target | `GET /` | Covered |
| US-015 | §14; constitution III | Provenance file:line + confidence | Pack & Cite | Covered |
| US-016 | Appendix C; §10 | Query-time LLM consent | Privacy | Covered |
| US-017 | §9 FR-07; §10; §15 | Structural graph; incremental <60s; full index SLA | FR-07 | Covered |
| US-018 | §9 FR-08; §10; §12 | Blast radius API; p95 <2s; >95% test prediction | FR-08 | Covered |
| US-019 | §9 FR-09; §14 | `graph.html` vis-network | FR-09 | Covered |
| US-020 | §9 FR-09; §15 | React Flow VS Code visualization | FR-09; V1 | Covered |
| US-021 | §9 FR-10 | Codebase memory cache / NL structural queries | FR-10 | Covered (OQ-06) |
| US-022 | §9 FR-11 | Per-phase token budgets | FR-11 | Covered (OQ-07) |
| US-023 | §9 FR-12; §10 | Adaptive summarization 60–95%; recall@10 >0.92 | FR-12 | Covered |
| US-024 | §9 FR-13; §10 | Compression telemetry + token dashboard | FR-13 | Covered |
| US-025 | §15 V1; FR-08 | PR risk bot affected tests + owners | V1 deliverable | Covered |
| US-026 | §11 QA; FR-08 | Regression tests from graph diff | §11 | Covered |
| US-027 | §13 | Staleness badge | Risk mitigation | Covered |
| US-028 | §9 FR-14; §15 | Multi-modal ingestion | FR-14 | Covered (OQ-03) |
| US-029 | §9 FR-15 | Cross-artifact linking | FR-15 | Covered |
| US-030 | §11 PM; BO-04 | Services+docs+diagrams query | §11 | Covered |
| US-031 | §9 FR-16 | Entity memory store | FR-16 | Covered |
| US-032 | §9 FR-17; §10; §12 | Cross-session recall >90%, <1.2s p95 | FR-17 | Covered |
| US-033 | §9 FR-18; §13 | Memory governance + PII | FR-18 | Covered |
| US-034 | §11 PM | Recall past decisions | §11 | Covered |
| US-035 | §11 Dev; Appendix A | Memory + blast task ask | §11; App A | Covered |
| US-036 | §11 QA | PII flows via L2 | §11 | Covered |
| US-037 | §11 SRE; §8 | Deployment risk score + hybrid ops search | §11 | Covered |
| US-038 | §10; §15 V2 | RBAC per repo path | NFR; V2 | Covered (OQ-01) |
| US-039 | §6; §13; §15 V2 | VPC hardening; air-gap boundary | Enterprise | Covered (OQ-13) |
| US-040 | §15 V2; §12 | Onboarding agent; 5 days vs 3 weeks | V2 exit | Covered |
| US-041 | §5 | Role-based context packs | Deliverables | Covered (OQ-05) |
| US-042 | §6; §10 | JetBrains extension | IN SCOPE | Covered (Future) |
| US-043 | §6; §14 | GitHub Action | IN SCOPE | Covered (Future; OQ-04) |
| US-044 | §15 SIP | Docs Engine & Timeline | SIP Vision | Covered (Future) |
| US-045 | §15 SIP | Marketplace & agents | SIP Vision | Covered (Future) |

### FR coverage check

| FR | Stories | Phase |
|----|---------|-------|
| FR-01 | US-001, US-013 | MVP |
| FR-02 | US-003 | MVP |
| FR-03 | US-004 | MVP |
| FR-04 | US-005 | MVP |
| FR-05 | US-006 | MVP |
| FR-06 | US-009 | MVP |
| FR-07 | US-017 | V1 |
| FR-08 | US-018, US-025, US-026 | V1 |
| FR-09 | US-019, US-020 | V1 |
| FR-10 | US-021 | V1 |
| FR-11 | US-022 | V1 |
| FR-12 | US-023 | V1 |
| FR-13 | US-024 | V1 |
| FR-14 | US-028 | V2 |
| FR-15 | US-029, US-030, US-036 | V2 |
| FR-16 | US-031 | V2 |
| FR-17 | US-032, US-034, US-035 | V2 |
| FR-18 | US-033 | V2 |

### §11 persona use-case coverage

| Persona use case | Story |
|------------------|-------|
| PM services+docs+diagrams | US-030 |
| PM recall past decisions | US-034 |
| Dev SSO ask with blast + memory | US-035 |
| Dev compressed context cost | US-023 / US-024 |
| Dev Pack Context / Serena | US-010 |
| QA regression from graph diff | US-026 |
| QA PII flows | US-036 |
| SRE deployment risk | US-037 |
| SRE infra+runbooks+incidents search | US-037 |

---

## Quality Validation (Internal)

- INVEST: stories are independently deliverable/testable; broad FRs split across US-001..US-045.
- No duplicate FR ownership conflicts; composite §11 stories reference dependencies rather than redefining FRs.
- MVP minimal coherent slice: L5+L3+CLI+VS Code+indexing+privacy+health (16 stories).
- No invented roles, endpoints, or metrics beyond BRD; Missing Evidence preserved as OQs.
- Roadmap order preserved; Future items explicitly BRD-supported.

---

## Completion Summary

| Metric | Value |
|--------|-------|
| Epics | 12 |
| User stories | 45 (US-001..US-045) |
| MVP stories | 16 (US-001..US-016; 8 P0 + 8 P1) |
| V1 / P2 | 11 (US-017..US-027) |
| V2 / P3 | 14 (US-028..US-041) |
| Future | 4 (US-042..US-045) |
| Ready for Spec Writer | **Yes** (start EP-001..EP-005); V1/V2 drafts usable with clarification notes |
