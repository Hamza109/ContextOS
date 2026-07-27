# ContextOS — Architecture Decision Records

**Sources cited:** `docs/BRD_Context_OS.md` sections as noted; `.specify/memory/constitution.md` principles I–V and Approved Technical Direction.

Each ADR: Problem → Decision → Alternatives → Trade-offs → Reasoning → Evidence → Status.

---

## ADR-001 — Six-Layer Model with Fixed Roadmap Order

| Field | Content |
|-------|---------|
| **Problem** | SDLC context needs are heterogeneous (structure, docs, symbols, tokens, search, memory). A monolith “context blob” would mix concerns and block incremental delivery. |
| **Decision** | Adopt BRD six-layer model L1–L6 with delivery order **MVP = L5+L3 → V1 = L1+L4 → V2 = L2+L6**. |
| **Alternatives** | (a) Build all six layers in one release; (b) Start with L1 graph-first; (c) Memory-first L6. |
| **Trade-offs** | Delayed blast-radius and compression value until V1; delayed tribal-knowledge/multi-modal until V2. Faster path to searchable, symbol-accurate IDE context. |
| **Reasoning** | Search + symbols unblock daily “where is X?” and safe edits first; graph/compression monetize change safety and token cost next; multi-modal/memory need richer governance. |
| **Evidence** | BRD §5, §15; constitution II & Roadmap Governance. |
| **Status** | **Confirmed** |

---

## ADR-002 — FastAPI Orchestrator Owns Intelligence; Clients Own DX

| Field | Content |
|-------|---------|
| **Problem** | Risk of duplicating indexing/search/compression logic inside VS Code extension or Webviews, causing policy bypass and drift. |
| **Decision** | FastAPI + Python 3.11 orchestrator owns indexing, graph, search, compression, memory, security policy, OpenAPI. Extension/CLI/Webviews own DX and presentation only. |
| **Alternatives** | (a) Extension-embedded local-only engine; (b) Multiple microservices per layer from day one. |
| **Trade-offs** | Requires local/VPC service process; not a pure extension. Single orchestrator is simpler for POC than many services. |
| **Reasoning** | Matches BRD sidecar model and constitution boundary discipline; enables shared CLI + IDE + Action clients. |
| **Evidence** | BRD §14; constitution V. |
| **Status** | **Confirmed** |

---

## ADR-003 — Local Embeddings + Qdrant for L5; No Index-Time LLM Exfil

| Field | Content |
|-------|---------|
| **Problem** | Semantic search needs vectors; cloud embedding APIs create exfil and quota risk. |
| **Decision** | Use `sentence-transformers/all-MiniLM-L6-v2` (384-dim) on local CPU; store in Qdrant collection `codebase`; never send source to external LLM during indexing. |
| **Alternatives** | (a) Hosted embedding APIs; (b) Pinecone as primary vector DB; (c) Larger GPU models. |
| **Trade-offs** | Lower embedding quality than larger models; CPU latency bounded by NFR design; ops must ship model weights (~90MB). |
| **Reasoning** | Satisfies privacy NFR and “$0 infra / no API quota” POC; constitution forbids unauthorized exfil. |
| **Evidence** | BRD §10, §13–§15, Appendix C; constitution III & Approved Technical Direction. |
| **Status** | **Confirmed** (Pinecone only as unapproved assumption — see ADR-008) |

---

## ADR-004 — FalkorDB for Structural Graph (V1)

| Field | Content |
|-------|---------|
| **Problem** | Blast radius and dependency visualization need pre-indexed typed edges with low-latency multi-hop queries. |
| **Decision** | Persist L1 structural graph in FalkorDB; build via CodeGraph/GitNexus/tree-sitter/regex; expose `/blast` and `/graph.html`. |
| **Alternatives** | (a) Compute blast via on-the-fly grep only; (b) Other graph DBs (Neo4j, etc.). |
| **Trade-offs** | Additional datastore in Compose; index drift risk (mitigate delta + staleness badge). |
| **Reasoning** | Explicit BRD stack choice; supports Cypher-style traversals shown in BRD. |
| **Evidence** | BRD §5 L1, FR-07..09, §14, Appendix C/D. |
| **Status** | **Confirmed** for V1 |

---

## ADR-005 — Serena MCP for L3 Symbol Navigation (MVP)

| Field | Content |
|-------|---------|
| **Problem** | Text/embedding similarity alone is insufficient for IDE-grade definitions, references, and rename scope. |
| **Decision** | Integrate Serena MCP for definition/references/hover/rename-scope; extension surfaces results; orchestrator may call Serena in context pipeline. |
| **Alternatives** | (a) Custom LSP client per language; (b) Regex-only symbols. |
| **Trade-offs** | Dependency on MCP ecosystem stability (BRD risk → pin versions, regex fallback). |
| **Reasoning** | Directly maps FR-04..06 and MVP exit criteria for symbol-accurate context. |
| **Evidence** | BRD FR-04..06, §15 MVP; constitution Approved Technical Direction. |
| **Status** | **Confirmed** |

---

## ADR-006 — Headroom-Style Compression in V1 (Not MVP Gate)

| Field | Content |
|-------|---------|
| **Problem** | Naive packs inflate tokens/cost; need 60–95% savings with recall preservation. |
| **Decision** | Implement L4 Headroom-style relevance scoring, summarization, phase budgets, and telemetry in **V1**; MVP ships basic packing without full L4 gate. |
| **Alternatives** | (a) Full compression in MVP; (b) Always send top_k files uncompressed. |
| **Trade-offs** | MVP token cost higher until V1; avoids blocking search/symbol delivery on summarization quality. |
| **Reasoning** | Roadmap places L4 in V1; `/context` metrics fields foreshadow compression but MVP exit criteria emphasize search + symbols. |
| **Evidence** | BRD §15; FR-11..13; constitution Roadmap Governance. |
| **Status** | **Confirmed** roadmap split; MVP metric semantics for `/context` **NEEDS CLARIFICATION** |

---

## ADR-007 — VS Code First; CLI in MVP; JetBrains Later

| Field | Content |
|-------|---------|
| **Problem** | Multiple IDE surfaces dilute POC focus. |
| **Decision** | Primary IDE for MVP = VS Code extension + CLI; JetBrains remains IN SCOPE but scheduled later unless clarified. |
| **Alternatives** | (a) JetBrains simultaneous MVP; (b) CLI-only MVP. |
| **Trade-offs** | JetBrains users wait; aligns with 2-week POC narrative. |
| **Reasoning** | BRD roadmap MVP deliverables list VS Code + CLI; constitution names VS Code as primary MVP IDE. |
| **Evidence** | BRD §15; constitution Approved Technical Direction; §6 lists JetBrains IN SCOPE. |
| **Status** | **Confirmed** for VS Code+CLI MVP; JetBrains timing **NEEDS CLARIFICATION** |

---

## ADR-008 — Qdrant as Approved Vector Store (Not Pinecone by Default)

| Field | Content |
|-------|---------|
| **Problem** | BRD §13 assumptions mention “Qdrant/Pinecone”, creating ambiguity vs approved stack. |
| **Decision** | **Qdrant is the approved vector store.** Pinecone is not default; requires a future ADR covering privacy, cost, and VPC. |
| **Alternatives** | Dual-support abstraction immediately. |
| **Trade-offs** | Less portability short-term; clearer security/ops story for POC. |
| **Reasoning** | Constitution Approved Technical Direction and BRD §14 primary stack specify Qdrant. |
| **Evidence** | Constitution Approved Technical Direction; BRD §14; §13 assumption conflict noted as Missing Evidence if product insists on Pinecone. |
| **Status** | **Confirmed** (Qdrant) |

---

## ADR-009 — Evidenced HTTP API Surface (Appendix D)

| Field | Content |
|-------|---------|
| **Problem** | Clients need a stable contract; inventing endpoints violates evidence-first governance. |
| **Decision** | Commit only: `GET /`, `POST /index`, `POST /context`, `GET /blast/{file_name}`, `GET /graph.html`. Mark any additional routes Proposed and FR-justified. |
| **Alternatives** | Rich CRUD API for memory/graph from day one. |
| **Trade-offs** | Some V2 governance UX may lack REST until specified; MCP may cover symbols without REST. |
| **Reasoning** | Constitution I evidence-first; Appendix D is the only concrete HTTP list. |
| **Evidence** | BRD Appendix D; constitution I. |
| **Status** | **Confirmed** |

---

## ADR-010 — Visualization: vis-network for `graph.html`; React Flow in VS Code

| Field | Content |
|-------|---------|
| **Problem** | Engineers need interactive blast/dependency views. |
| **Decision** | Serve `graph.html` via vis-network from API; use React Flow inside VS Code Webviews for panels. |
| **Alternatives** | Single viz library everywhere; desktop-only Graphviz. |
| **Trade-offs** | Two viz technologies to maintain; matches BRD explicitly. |
| **Reasoning** | FR-09 and §14 specify both. |
| **Evidence** | BRD FR-09, §14. |
| **Status** | **Confirmed** for V1 |

---

## ADR-011 — OpenTelemetry-Compatible Observability

| Field | Content |
|-------|---------|
| **Problem** | Compression savings, latency, and recall claims must be measurable and operable. |
| **Decision** | Instrument orchestrator with OpenTelemetry-compatible telemetry for token usage, recall, latency, memory recall rate; expose cost dashboard artifact in V1. |
| **Alternatives** | Ad-hoc logging only; vendor-specific APM hard-wire. |
| **Trade-offs** | Requires collector/backend choice later (**Missing Evidence** on vendor). |
| **Reasoning** | NFR and constitution mandate OTel-compatible observability. |
| **Evidence** | BRD §10 NFR Observability; FR-13; constitution Approved Technical Direction & IV. |
| **Status** | **Confirmed** (exporter destination **NEEDS CLARIFICATION**) |

---

## ADR-012 — Privacy Defaults: Ignore Rules, Consent, RBAC, PII

| Field | Content |
|-------|---------|
| **Problem** | Indexing source code is security-sensitive; memory/multi-modal paths risk PII leakage. |
| **Decision** | Enforce `.gitignore` + `.env`/secrets/binary exclusions; consent for query-time LLM; RBAC per repo path; PII redaction on L2/L6; provenance on outputs; sanitize Webview IPC. |
| **Alternatives** | Trust client-side filtering only; cloud-index by default. |
| **Trade-offs** | RBAC schema still unspecified — implementation of enforcement points proceeds, policy model blocked on clarification. |
| **Reasoning** | Non-negotiable constitution III and BRD NFRs. |
| **Evidence** | Constitution III; BRD §10 Code access & PII; §13; FR-18. |
| **Status** | **Confirmed** controls; **Missing Evidence** for concrete RBAC/authn schemas |

---

## ADR-013 — Docker Compose Local/VPC-Friendly Deployment First

| Field | Content |
|-------|---------|
| **Problem** | Need zero-risk POC infrastructure without cloud lock-in. |
| **Decision** | Default deploy = Docker Compose hosting API + Qdrant + FalkorDB (+ local Serena/embeddings). VPC/enterprise hardening in V2; air-gap without enterprise tier out of scope. |
| **Alternatives** | Kubernetes-first; SaaS-only. |
| **Trade-offs** | HA/multi-tenant patterns deferred; fits solo POC cost $0 OSS. |
| **Reasoning** | BRD Zero Risk POC and V2 enterprise notes. |
| **Evidence** | BRD §15, §6 OUT OF SCOPE air-gap clause. |
| **Status** | **Confirmed** for POC; K8s **Not evidenced** |

---

## ADR-014 — Hybrid Search with MMR (L5)

| Field | Content |
|-------|---------|
| **Problem** | Pure vector or pure keyword miss different query classes. |
| **Decision** | Hybrid BM25 + vector over packs with MMR re-ranking; target p95 <800ms @ 500k LOC. |
| **Alternatives** | Vector-only; BM25-only. |
| **Trade-offs** | Two retrieval paths to tune; BM25 storage placement **Missing Evidence**. |
| **Reasoning** | Explicit FR-02 / NFR. |
| **Evidence** | BRD FR-02, §10. |
| **Status** | **Confirmed** |

---

## Summary Table

| ADR | Title | Status |
|-----|-------|--------|
| 001 | Six-layer roadmap order | Confirmed |
| 002 | Orchestrator vs client boundaries | Confirmed |
| 003 | Local embeddings + Qdrant | Confirmed |
| 004 | FalkorDB L1 | Confirmed (V1) |
| 005 | Serena MCP L3 | Confirmed |
| 006 | Headroom L4 in V1 | Confirmed |
| 007 | VS Code + CLI MVP | Confirmed; JB timing open |
| 008 | Qdrant not Pinecone default | Confirmed |
| 009 | Appendix D API surface | Confirmed |
| 010 | vis-network + React Flow | Confirmed (V1) |
| 011 | OpenTelemetry | Confirmed; backend open |
| 012 | Privacy defaults | Confirmed; RBAC schema open |
| 013 | Docker Compose first | Confirmed |
| 014 | Hybrid BM25+vector+MMR | Confirmed |
