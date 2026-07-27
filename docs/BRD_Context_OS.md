# BRD — ContextOS: Six-Layer SDLC Intelligence Platform
**Version:** DRAFT v0.9 • **Date:** July 2026 • **Author:** Hamza Hamal • **Status:** CONFIDENTIAL • IN REVIEW

> An orchestration platform that composes 6 specialized context tooling layers to give AI coding assistants and engineering teams complete, compressed, and persistent understanding of the entire SDLC — from requirements to maintenance.

---

## 1. Document Control

| Field | Value |
|-------|-------|
| **Document** | BRD — ContextOS: Six-Layer SDLC Intelligence Platform |
| **Version** | v0.9 Draft |
| **Author** | Hamza Hamal |
| **Stakeholders** | CTO, VP Eng, AI Platform Lead, Staff Eng, DevOps, Security, PMO |
| **Approvers** | CTO, Head of Product |
| **Classification** | CONFIDENTIAL |

---

## 2. Executive Summary

**ContextOS** is a unified SDLC Intelligence platform that orchestrates six complementary context engineering layers to solve the fundamental limitation of LLM-based development: **insufficient, unstructured, and transient context**.

Today, developers lose 35% of their time re-establishing context when switching tasks, and AI assistants hallucinate because they see fragmented code slices. ContextOS replaces this with a persistent, compressed, graph-aware context fabric that adapts to each SDLC phase.

Each layer has a single responsibility:
- **L1 Structural Knowledge Graphs:** Dependency chains, call graphs, blast radius analysis across repos
- **L2 Multi-modal Project Graphs:** Code + docs + SQL + images + video unified graph (Graphify)
- **L3 Symbol & LSP Navigation:** IDE-grade symbol retrieval, definitions, references, refactoring scope (Serena)
- **L4 Context Compression:** 60-95% token savings via adaptive summarization & pruning (Headroom)
- **L5 Context Packing & Semantic Search:** Flatten/embed repos for high-recall retrieval and prompt assembly (Repomix, grepai, claude-context)
- **L6 Persistent Agent Memory:** Cross-session, entity-aware memory for agents and developers (Cognee)

**Outcome:**
- 60% faster onboarding, 40% fewer regression bugs via blast-radius awareness, and persistent memory across agent sessions.
- ContextOS does not replace IDEs or LLMs — it makes them SDLC-aware.

### Layer Legend
- **L1** - Structural Knowledge Graphs - CodeGraph, GitNexus
- **L2** - Multi-modal Project Graphs - Graphify
- **L3** - Symbol & LSP Navigation - Serena
- **L4** - Context Compression 60-95% - Headroom
- **L5** - Packing & Semantic Search - Repomix, grepai
- **L6** - Persistent Agent Memory - Cognee

---

## 3. Business Objectives

| Objective | KPI | Target | Layer |
|-----------|-----|--------|-------|
| **BO-01 Reduce SDLC context-switching overhead** | Time to first meaningful commit | ↓45% | L5+L3+L6 |
| **BO-02 Lower LLM inference cost** | Avg tokens / task, Cost / PR | 60-95% reduction via L4, $0.50 → $0.05 | L4 |
| **BO-03 Improve change safety** | Regression defects linked to missed deps | ↓40% | L1+L3 |
| **BO-04 Accelerate onboarding & discovery** | Time to answer 'where is X used?' | <5 sec vs 2 hrs, <8 sec | L1+L2+L5 |
| **BO-05 Enable persistent AI teammates** | Cross-session task continuity, Memory recall precision | >90% | L6 |

ROI Example (from Manager Pitch Deck):
- **Before:** 85k tokens / PR ($0.50), 2 hrs searching 6 tools, 3 weeks onboarding, 15% PRs break downstream
- **After ContextOS:** 7.2k tokens / PR ($0.05, 91% saving), 5 sec blast radius, 5 days onboarding, <1% breakage
- **Monthly saving:** $675/month for 10 devs asking 5 architecture questions/day

---

## 4. Problem Statement

Modern engineering teams run polyglot monorepos, distributed services, and documentation scattered across Notion, Confluence, Jira, SQL schemas, Figma, Loom, and Slack threads. LLMs see none of this as a coherent system.

**Fragmented context:** Symbol definitions live in LSP servers, deps in lockfiles, business rules in docs, data models in SQL — no unified view. Example: Devs search 6 tools: GitHub, Jira, Confluence, Figma, Slack, Notion. 2 hrs wasted per task.

**Token bloat:** Naively concatenating files exceeds context windows and inflates cost 10-20x without improving relevance. AI rebuilds context every time. 85k tokens per PR. No memory. $42k/month in LLM tokens and we still paste files manually.

**Amnesiac agents:** Every session starts blank; decisions, entity relationships, and tribal knowledge evaporate. We rejected Auth0 in Sprint 12, but AI suggests it again.

**Blind changes:** Engineers cannot answer "what breaks if I change this?" without manual grep, costing hours and regressions.

### Voice of Engineering - Q2'26
> "I spend more time finding code than writing it. grep is my architecture diagram." — Senior Engineer, Platform
> "Our AI assistant is confident and wrong. It doesn't know our service graph." — Tech Lead, Payments
> "$42k/month in LLM tokens and we still paste files manually."

---

## 5. Proposed Solution Overview - 6 Layers

### ContextOS Orchestration Model

```
User Query / SDLC Event
    ↓
L6 Recall (Cognee) → L2 Enrich (Graphify)
    ↓
L5 Pack (Repomix, grepai) → L3 Resolve (Serena) → L1 Expand (CodeGraph)
    ↓
L4 Compress (Headroom) 60-95%
    ↓
L3 Safe Edit Plan → PR
```

**Pipeline Details:**
1.  **L6 + L2:** Recall memory + enrich with multi-modal artifacts (Jira, Figma, schema)
2.  **L1 Blast Radius Filter:** Dependency chains • Call graphs • Blast radius
3.  **L5 Repomix Pack:** Flatten / embed for retrieval
4.  **L4 Headroom Compress 91%:** 85k → 7.2k tokens
5.  **L3 Serena Precise Edit → PR:** IDE-grade symbol editing

#### Layer Definitions

**L1 - Structural Knowledge Graphs (CodeGraph, GitNexus, FalkorDB)**
- Builds typed graph: File→Module→Class→Method→Call with incremental indexing <60s for 100-file delta
- Capabilities: Call graph traversal, Transitive dependency query, Blast radius diff, Hotspot detection
- Value: Find dependency chains, call graphs, blast radius in <100ms via pre-indexed edges. Critical for Requirements traceability, Design impact analysis, and Maintenance blast-radius.
- Example: `payment.service.ts → [auth.middleware.ts, checkout.controller.ts, order.service.ts]`

**L2 - Multi-modal Project Graphs (Graphify)**
- Graphify shall ingest markdown, ADRs, SQL DDL, OpenAPI, images, Loom transcripts into property graph with embeddings
- Multi-modal ingestion, Cross-artifact linking, Natural language to graph query, Video frame OCR
- Auto-links: `UserService ↔ users table ↔ ADR-014 ↔ Figma ↔ Jira-123`
- Value: Links Jira/PRD to code & past decisions; recall tribal knowledge. Answers "what services touch checkout?" with code + docs + diagram links

**L3 - Symbol & LSP Navigation (Serena)**
- Via Serena provides IDE-grade precision: go-to-definition, find-all-references, document symbols, hover docs, rename scope
- Capabilities: Definition / Reference, Symbol hover, Workspace rename scope, Token budget guard, Relevance scorer
- Value: Ensures LLM edits respect language semantics, not just text similarity. Foundation for safe refactoring and accurate test generation
- Example: `PaymentService::authenticate()` definition lookup 99% accuracy

**L4 - Context Compression (Headroom)**
- Applies semantic pruning, file-level summarization, dead-code elision, and relevance scoring to achieve 60-95% token savings while preserving recall >92%
- Enforces token budgets per SDLC phase (e.g., 8k for dev, 32k for design review)
- Capabilities: Summary cache, Diff-aware compression, Relevance scorer, Compression Telemetry
- Value: Shows before/after token cost in dashboard. Avg saving 60-95%. $0.50 → $0.05 per PR

**L5 - Context Packing & Semantic Search (Repomix, grepai, claude-context, Qdrant)**
- Repo Flattening & Packing: Flatten any repo (up to 500k LOC) into LLM-optimized XML with .gitignore respect, binary skip, and token count pre-calc
- Hybrid Semantic Search: BM25 + vector over flattened packs with <800ms p95 latency and MMR re-ranking
- Prompt packing, Embedding refresh
- Value: Answers "find the checkout flow" / "where is payment retry logic?" in <2 sec

**L6 - Persistent Agent Memory (Cognee)**
- Entity Memory Store: Stores entities (Person, Service, Decision, Incident) with temporal edges and source provenance
- Example: "you were migrating auth-service to JWT, blocked on DB migration #341"
- Cross-session Recall: Recall relevant memories for a task query with <1.2s p95 and explain why recalled (source + timestamp)
- Memory Governance: TTL, decay, manual pin/forget, and PII redaction
- Value: Remembers "We rejected Auth0 in Sprint 12, use Passport.js" - from Cognee. Avoids rework. Explains architecture decisions.

### What ContextOS Delivers
- 6-layer orchestration service (API + MCP servers)
- VS Code / JetBrains extension + CLI (`contextos ask 'where is X?'`)
- Indexer for Git, local FS, Notion/Confluence, SQL, Loom transcripts
- Compression engine with budget policies per SDLC phase
- Persistent memory store with entity graph
- Role-based context packs for PM, Dev, QA, DevOps
- Observability: token usage, recall precision, latency, `graph.html` visualization
- Token cost dashboard - before/after L4
- Live blast radius visualization (React Flow / vis-network)

---

## 6. Scope

### IN SCOPE
- VS Code / JetBrains extension, CLI, GitHub Action
- Real file reading via AST parsing (tree-sitter), embedding via sentence-transformers (all-MiniLM-L6-v2, 384-dim)
- FalkorDB graph store, Qdrant vector DB, FastAPI orchestrator
- Auto-indexing on install, incremental delta indexing on file save (<60s for 100-file delta)
- `graph.html` live visualization (like Graphify but live from FalkorDB)
- Token compression 60-95% with budget policies

### OUT OF SCOPE
- LLM training / fine-tuning — bring your own model (Gemini, GPT-4, Ollama)
- Code execution sandbox (use existing CI)
- Full project management suite (integrates via Jira API)
- Real-time collaborative editing (OT/CRDT)
- Binary artifact analysis (Docker layers v1)
- On-prem air-gapped without explicit enterprise tier

---

## 7. Stakeholders

| Role | Responsibility |
|------|----------------|
| **Product Manager** | Define context packs for Requirements/Design |
| **Staff Engineer** | Graph schema & indexing SLAs |
| **AI Platform Lead** | Orchestrator, LLM routing, compression tuning |
| **DevOps / SRE** | Indexer scaling, vector DB, observability, deployment risk scoring |
| **Security** | PII scrubbing, code access controls, RBAC per repo path |
| **QA** | Validate recall precision & blast-radius accuracy |
| **CTO / VP Eng** | Final approval & rollout sponsorship |

---

## 8. SDLC Phase to Layer Mapping

| SDLC Phase | Primary Layers Active | Supporting Layers | ContextOS Value |
|------------|----------------------|-------------------|-----------------|
| **Requirements** | L2, L6, L5 | L1 | Link Jira/PRD to code & past decisions; recall tribal knowledge |
| **Design** | L1, L2, L6 | L5, L4 | Architecture impact: dependency chains, ADR + diagram linking |
| **Development** | L5, L3, L1, L4 | L6, L2 | Precise symbol navigation + compressed repo context for code gen |
| **Testing** | L1, L3, L5 | L4 | Blast radius → test selection; symbol-aware test generation |
| **Deployment** | L1, L2 | L6 | Change-risk graph, config + infra search, risk score from dependency depth + incident memory |
| **Maintenance** | L6, L2, L1 | L5 | Persistent memory of incidents, onboarding via multi-modal graph, 3x faster onboarding |

---

## 9. Functional Requirements (FR-01 → FR-18)

### L5 — Context Packing & Semantic Search

**FR-01 Repo Flattening & Packing**
- System shall flatten any repo (up to 500k LOC) into LLM-optimized XML with .gitignore respect, binary skip, and token count pre-calc via Repomix.
- Respects .env, node_modules, dist, .git. Token count pre-calc.

**FR-02 Hybrid Semantic Search**
- System shall provide hybrid search (BM25 + vector) over flattened packs using grepai/claude-context with <800ms p95 latency and MMR re-ranking.
- Query: "where is payment retry logic?" → Top 8 files with scores

**FR-03 Phase-Aware Prompt Templates**
- System shall assemble context packs via code2prompt templates scoped to SDLC phase (Requirements/Design/Dev/Test/Deploy).

### L3 — Symbol & LSP Navigation

**FR-04 Symbol Definition Lookup**
- Via Serena MCP, system shall resolve symbol definition (file:line, signature, docstring) for 12+ languages with 99% accuracy.
- Example: `PaymentService::authenticate() → payment.service.ts:42`

**FR-05 Find All References**
- System shall return all references of a symbol across monorepo with call-site context (2 lines before/after) and filter by file type.
- Development, Testing, Maintenance

**FR-06 Rename Scope Analysis**
- System shall compute safe rename scope and breaking-change count before rename execution.

### L1 — Structural Knowledge Graphs

**FR-07 Structural Graph Generation**
- Using CodeGraph/GitNexus/FalkorDB, system shall build typed graph: File→Module→Class→Method→Call with incremental indexing <60s for 100-file delta.
- Parser: tree-sitter / regex for import extraction

**FR-08 Blast Radius Analysis**
- System shall compute transitive blast radius for a diff (N-hop) with affected services, tests, and owners list.
- API: `GET /blast/{file_name}` → `{direct_dependents, transitive, db_tables, risk: HIGH|MEDIUM|LOW, tests_to_run}`

**FR-09 Dependency Chain Visualization**
- System shall visualize dependency chain for a symbol/service as interactive subgraph (depth 1-5).
- Output: `graph.html` via vis-network, React Flow in VS Code WebView
- Endpoint: `GET /graph.html?repo=payment-service`

**FR-10 Codebase Memory Cache**
- codebase-memory-mcp shall cache hot entities and answer natural language structural queries: 'where is auth validated?' / 'what is blast radius of PaymentService.refund()'

### L4 — Context Compression

**FR-11 Token Budget Enforcement**
- Headroom engine shall enforce per-phase token budgets (e.g., Dev=12k, Design=32k) with hard fail and degradation policy.

**FR-12 Adaptive Summarization**
- System shall compress low-relevance files via LLM summarization preserving symbols, types, and TODOs, achieving 60-95% savings.
- Before: 85k tokens, After: 7.2k tokens (91% saving)

**FR-13 Compression Telemetry**
- System shall emit compression ratio, recall@k, and cost-saved per request to observability.
- Dashboard: `contextos_token_dashboard.html`

### L2 — Multi-modal Project Graphs

**FR-14 Multi-modal Ingestion**
- Graphify shall ingest markdown, ADRs, SQL DDL, OpenAPI, images, Loom transcripts into property graph with embeddings.
- Requirements, Design, Maintenance phases

**FR-15 Cross-artifact Linking**
- System shall auto-link code symbols to docs/diagrams/SQL tables via entity resolution (e.g., UserService ↔ users table ↔ ADR-014 ↔ JIRA-123 ↔ Figma).

### L6 — Persistent Agent Memory

**FR-16 Entity Memory Store**
- Cognee shall store entities (Person, Service, Decision, Incident) with temporal edges and source provenance.
- Example memory: "We rejected Auth0 in Sprint 12 due to pricing, use Passport.js + Google OAuth. Pattern: auth.middleware.ts"

**FR-17 Cross-session Recall**
- System shall recall relevant memories for a task query with <1.2s p95 and explain why recalled (source + timestamp).
- Maintenance, Development

**FR-18 Memory Governance**
- System shall support TTL, decay, manual pin/forget, and PII redaction for memory entries.
- Copilot instructions: `.github/copilot-instructions.md` → Passport.js guidance

---

## 10. Non-Functional Requirements

| NFR | Target | Layer |
|-----|--------|-------|
| **Semantic search latency** | p95 <800ms for 500k LOC index | L5 |
| **Graph query (blast radius)** | p95 <2s for 3-hop, 10k nodes, <5 sec for 5 sec demo | L1 |
| **Token compression** | 60-95% savings vs naive packing, recall@10 >0.92 | L4 |
| **Monorepo indexing** | 1M LOC full index <15 min, delta <60s, 200 files in 10 sec | L5+L1 |
| **Embedding model** | all-MiniLM-L6-v2, 384-dim, local CPU, no exfil | L5 |
| **Code access & PII** | RBAC per repo path, PII scrub, no code exfil to LLM provider without consent flag, respects .gitignore, ignores .env | All |
| **Indexer availability** | 99.5% uptime, graceful degraded search on partial index | - |
| **IDE integration** | VS Code & JetBrains, <3 clicks to 'Ask ContextOS', auto-index on install, re-index on file save | L3 |
| **Observability** | OpenTelemetry: token usage, recall precision, latency, memory recall rate, cost dashboard | L4 |
| **Graph visualization** | `graph.html` live via FalkorDB, interactive via vis-network / React Flow | L1+L2 |

---

## 11. User Stories / Use Cases

### Product Manager
- As a PM, I want to ask 'what services touch checkout?' and get code + docs + diagram links, so I can write accurate PRDs.
- As a PM, I want ContextOS to recall past decision 'why we rejected Kafka for checkout' during spec review. (L6)

### Developer
- As a dev, I want to ask 'Add Google SSO to Payment Service' and get Passport.js (not Auth0) with blast radius of 3 services, 12 tests, so I don't break QA. (L1+L6)
- As a dev, I want compressed repo context (12k tokens, 7.2k after compression) that still contains relevant symbols for my ticket, so I pay $0.05 not $0.50. (L4+L5)
- As a dev, I want to right-click → Pack Context and get safe edit plan via Serena LSP, not whole file rewrite. (L3)

### QA Engineer
- As QA, I want ContextOS to suggest regression tests based on L1 graph diff between main and PR. (L1)
- As QA, I want to query 'show flows that read PII' via L2 graph linking code ↔ SQL ↔ OpenAPI. (L2)

### DevOps / SRE
- As SRE, I want deployment risk score computed from L1 dependency depth + L6 incident memory. (L1+L6)
- As SRE, I want to search infra as code + runbooks + past incidents in one hybrid search (L5+L6).

---

## 12. Success Metrics / KPIs

| Metric | Measurement | Target |
|--------|-------------|--------|
| **Avg compression ratio (L4)** | tokens_before vs tokens_after | 91% (85k → 7.2k) |
| **Relevant results in top 10 (L5)** | recall@10, precision | >0.92 |
| **'Where is X used?' query latency** | time to answer | <5 sec (vs 2 hrs before) |
| **Correct affected tests predicted** | blast radius accuracy | >95%, <1% breakage vs 15% before |
| **Time to first meaningful PR (onboarding)** | new joiner | 5 days vs 3 weeks (-60%) |
| **Token cost / PR** | $ cost | $0.05 vs $0.50 (-90%) |
| **Bug RCA time** | hours | 1 hr vs 4 hrs (-75%) |
| **Cross-session memory recall** | L6 | >90% recall, <1.2s p95 |

---

## 13. Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| **Graph index drift on large PRs** | Delta indexing + staleness badge |
| **Compression hallucinates away key symbol** | Symbol-preservation tests + recall gate |
| **Memory bloat / PII leak (L6)** | TTL, RBAC, scrub pipeline, manual pin/forget |
| **MCP ecosystem stability (Serena, CodeGraph, Cognee)** | Pin versions, fallback to regex parsing |
| **Embedding model quota** | Use local all-MiniLM-L6-v2, no API quota |
| **GitHub/GitLab API rate limits for indexer** | Cache + incremental indexing |
| **Security approval for code indexing in VPC** | Local FalkorDB + Qdrant, no code exfil, .gitignore respect |

**Assumptions:**
- Git is source of truth; monorepo ≤1M LOC for MVP
- Teams use VS Code or JetBrains (80%+ coverage)
- LLM provider supports 128k context; we compress to fit
- Vector DB (Qdrant/Pinecone) available in VPC or local Docker

---

## 14. Architecture

**ContextOS sits as a sidecar between developer intent and LLM.**

```
Request (IDE action, CLI query, CI webhook) → FastAPI Orchestrator

1. Ingest & Normalize (L5):
   Repomix flattens repo, respecting .gitignore. grepai + claude-context embed chunks and maintain HNSW index in Qdrant. Change events trigger delta re-index. SentenceTransformer local.

2. Resolve & Expand (L3 → L1):
   Serena resolves symbols at cursor. If ambiguous, L1 structural graph expands to callers/callees, owners, and downstream services via CodeGraph/FalkorDB. Query: MATCH (a)-[:IMPORTS*1..3]->(b)

3. Compress & Budget (L4):
   Headroom scores chunks by relevance (query + SDLC phase + recency), summarizes low-score files, and enforces token budget. Emits metrics to dashboard. 85k → 7.2k.

4. Enrich & Recall (L2 + L6):
   Graphify links code nodes to docs/SQL/diagrams. Cognee injects pinned memories: "We rejected Auth0 in Sprint 12, use Passport.js" with provenance link.

5. Pack & Cite (L5+L3):
   Final packed context (XML) + citations + graph preview sent to LLM or IDE hover. All citations include file:line and confidence. <context files='8'>...

Stack:
- API: FastAPI + Python 3.11
- Graph DB: FalkorDB (redis://localhost:6379) - L1
- Vector DB: Qdrant (http://localhost:6333, collection=codebase, 384-dim) - L5
- Embed Model: sentence-transformers/all-MiniLM-L6-v2 (local)
- LLM: Gemini 1.5 Flash / GPT-4 / Ollama (configurable via GEMINI_API_KEY)
- IDE: VS Code Extension (auto-index on install, re-index on save)
- Viz: vis-network for graph.html, React Flow for VS Code WebView
- Compression: Headroom logic (90% saving)
```

**Real Extension Layers:**
- **On Install:** Auto-indexes repo (10 sec for 200 files) → FalkorDB + Qdrant
- **On File Save:** Re-indexes only that file (0.5 sec)
- **On Query:** L6→L2→L1→L5→L4→L3 pipeline (3 sec total) → Copilot gets compressed 7.2k context
- **Outputs:** `graph.html` live, token dashboard, blast radius panel, Copilot instructions `.github/copilot-instructions.md`

**Graph.html Example:**
- Endpoint `GET /graph.html?repo=payment-service` returns interactive vis-network with nodes = files, edges = IMPORTS, physics disabled, arrows to, color #64748b, background #0f172a

---

## 15. Roadmap

| Phase | Timeline | Layers | Deliverables | Exit Criteria |
|-------|----------|--------|--------------|---------------|
| **MVP** | 2 Weeks | L5 + L3 | Repo flatten + hybrid search (Repomix, grepai, claude-context), Serena symbol navigation in VS Code, Basic prompt packing per phase, CLI: `contextos ask 'where is X?'` | Dev can get symbol-accurate context <2s in IDE, Search works |
| **V1** | 4 Weeks | L1 + L4 | Structural graph + blast radius (CodeGraph, FalkorDB, GitNexus), Headroom compression 60-95% with budget policies, PR risk bot: auto affected tests + owners, Telemetry + cost dashboard, graph.html live | 90% token save, accurate blast radius on 1 repo, Token cost $0.50→$0.05, 40% fewer regressions, $ saved measurable |
| **V2** | 6 Weeks | L2 + L6 | Multi-modal graph (docs, SQL, diagrams, Loom via Graphify), Persistent memory (Cognee) with governance, Enterprise RBAC + VPC deployment, Onboarding agent | 3x faster onboarding, 90% memory recall, 60% faster onboarding (3 weeks→5 days) |
| **SIP - Vision** | 6-12 Months | All + RBAC | Docs Engine, Timeline, Plugin Marketplace, 8 agents (PM, Architect, QA, DevOps), RBAC per path, VPC, Observability | OS for SE, SIP = Car, ContextOS = Battery |

**What I Need - Zero Risk POC (from Manager Deck):**
- Time: 2-3 weeks, Solo dev, after hours + 20% work time
- Cost: $0 Infra - FalkorDB, Qdrant, Serena - all open-source, Docker Compose
- Stack: FastAPI + Qdrant + FalkorDB + Serena MCP + Headroom + Repomix
- Deliverable in 2 weeks: VS Code extension on OUR repo, Live blast radius visualization (React Flow), Token cost dashboard - before/after L4, Demo: "Explain payment service" in <8 sec
- Success Criteria: 60%+ token saving + accurate blast radius on 1 repo. If fails, we kill it.

---

## 16. Traceability & Approval

| SDLC Artifact | ContextOS Layer | BRD Section | Status |
|---------------|-----------------|-------------|--------|
| Requirements / Jira | L2 Graphify, L6 Cognee | 8,9,11 | Draft |
| Design / ADR | L1 CodeGraph, L2 | 8,9 | Draft |
| Code | L5 Repomix, L3 Serena, L1 | 9 | POC Done |
| Test | L1 Blast Radius, L3 | 9 | POC Done |
| Deploy | L1 Risk Score, L6 Incidents | 11 | Planned |
| Maintenance | L6 Memory, L2 Multi-modal | 8,9 | Planned |

**By approving, stakeholders confirm scope, layers, and roadmap priorities.**

**Business Objectives Traceability:**
- BO-01 Reduce context-switching → L5+L3+L6 → Time to first commit ↓45%
- BO-02 Lower LLM cost → L4 → $0.50→$0.05, 91% saving
- BO-03 Improve change safety → L1+L3 → Regression defects ↓40%, breakage <1%
- BO-04 Accelerate onboarding → L1+L2+L5 → Time to answer 'where is X?' <5 sec
- BO-05 Persistent teammates → L6 → Cross-session continuity

---

## Appendices

### A. Demo Scenario: "Add Google SSO to Payment Service"

**Before (Today):**
- Dev searches 4 repos, 2 Confluence pages - 2 hours
- Packs entire repo - 85k tokens ($0.50)
- LLM hallucinates, misses auth.middleware, suggests Auth0
- Breaks 3 downstream services - found in QA

**After (With ContextOS):**
- L1 CodeGraph: Shows blast radius in 5 sec - 3 services, 12 tests, HIGH risk
- L2 Graphify: Pulls Jira + Figma + schema - full context
- L4 Headroom: 85k → 7.2k tokens - 91% saving ($0.05)
- L6 Memory: "We rejected Auth0 in Sprint 12, use Passport.js" - from Cognee. Avoids rework.
- L3 Serena: Precise edit → PR, no breakage

### B. Copilot Instructions Test

Simple question to test `copilot-instructions.md` approach:

**Test Query:** `What auth library should I use for Google SSO in this repo?`

- Without ContextOS: `Use Auth0` (generic, wrong)
- With ContextOS: `Use Passport.js for Google SSO in this repo. The workspace guidance explicitly points to Passport.js rather than Auth0 for this integration.`

Proof that L6 memory + copilot instructions work.

### C. How ContextOS Reads Files (Real Implementation)

**Local Indexing (One-time):**
1. Clones / reads repo folder `./repos/payment-service`, respects .gitignore (ignores node_modules, .env, dist)
2. L1: Parses AST via tree-sitter / regex, extracts import statements, builds graph in FalkorDB: `(File{name})-[:IMPORTS]->(File{name})`
3. L5: Chunks files 500 tokens, embeds locally via all-MiniLM-L6-v2 (90MB, CPU, no API), stores in Qdrant

**On-Demand Query:**
- Question embedded locally → vector search Qdrant → top 8 files
- L1 queries FalkorDB: `MATCH (f)-[:IMPORTS*1..3]->(dep) WHERE f.name="payment.service.ts"`
- Only compressed 7.2k context sent to LLM (or local Ollama for 100% local)

**Privacy:** No code sent during indexing. Only compressed 7.2k chunk sent at query time, optional local Ollama.

### D. API Endpoints (Real)

- `GET /` → Health, pipeline, falkor/qdrant status
- `POST /index` → Index repo: `{repo_path, repo_name}` → `{files_indexed, graph_nodes, embeddings, time_ms}`
- `POST /context` → Get compressed context: `{query, file, repo, top_k}` → `{final_context, metrics{tokens_before, tokens_after, saving_percent, trace}, blast_radius, memory, relevant_files, is_real}`
- `GET /blast/{file_name}?repo=` → Blast radius
- `GET /graph.html?repo=` → Interactive vis-network graph (like Graphify but live)

### E. References

- Industry: Qodo raised $40M for Context Engine, Augment Code, Sourcegraph betting on same stack
- Tools: CodeGraph, GitNexus, Graphify, Serena, Headroom, Repomix, grepai, Cognee, FalkorDB, Qdrant
- Artifacts: ContextOS_Manager_Pitch_Deck.html, contextos-REAL-FILE-READING.zip, contextos-vscode-COMPLETE-MAC.zip

---

**CONFIDENTIAL • ContextOS BRD v0.9-draft • Author: Hamza Hamal • July 2026 • Generated from Brd-Contextos-Sdlc-Platform.html + Manager Pitch Deck + Real Implementation**

