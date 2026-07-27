# ContextOS — Architecture Overview

**Document status:** Project-level architecture (pre–user-story)  
**Sources:** `docs/BRD_Context_OS.md` v0.9 Draft; `.specify/memory/constitution.md` v1.0.0  
**Date:** 2026-07-27  

---

## Evidence Classification Legend

| Label | Meaning |
|-------|---------|
| **Confirmed** | Explicitly stated in BRD and/or constitution |
| **Proposed** | Strongly implied by FRs; not fully specified — implementers must treat as provisional |
| **Assumption** | BRD §13 assumptions or constitution defaults |
| **Risk** | BRD §13 risks or constitution-mandated threat notes |
| **Missing Evidence / NEEDS CLARIFICATION** | Required for implementation detail but not evidenced |

---

## 1. Executive Summary

ContextOS is a **six-layer SDLC intelligence orchestration platform** that sits as a **sidecar between developer intent and LLMs**. It composes specialized context tooling so AI assistants and engineering teams receive complete, compressed, provenance-backed understanding of the codebase and related SDLC artifacts — without replacing IDEs or LLM providers (BRD §2, §14).

The platform delivers:

- A **FastAPI + Python 3.11 orchestrator** owning indexing, graph, search, compression, memory, security policy, and OpenAPI contracts (constitution V; BRD §14).
- **Client surfaces:** VS Code extension (primary MVP IDE), CLI, later JetBrains; GitHub Action for CI-oriented workflows (BRD §6, §15).
- **Stores:** FalkorDB (L1 structural graph), Qdrant 384-dim vectors (L5), Cognee-style entity memory (L6, V2) (BRD §14; constitution Approved Technical Direction).
- **Local-first indexing:** `sentence-transformers/all-MiniLM-L6-v2` on CPU; no code exfiltration to external LLM providers during indexing (BRD §10 NFR; constitution III).

**Roadmap (must not be reordered without explicit plan rationale):**

| Phase | Layers | Primary surfaces |
|-------|--------|------------------|
| **MVP** | L5 + L3 | CLI + VS Code; repo flatten, hybrid search, Serena symbols, basic phase-aware packing |
| **V1** | L1 + L4 | Structural graph, blast radius, graph.html / React Flow, Headroom compression, telemetry/cost dashboard, PR risk support |
| **V2** | L2 + L6 | Multi-modal graph, persistent memory + governance, enterprise RBAC + VPC hardening |

---

## 2. System Overview

### 2.1 Problem addressed (Confirmed — BRD §4)

Fragmented SDLC context (LSP, lockfiles, docs, SQL, design tools), token bloat from naive packing, amnesiac agent sessions, and blind changes without blast-radius awareness.

### 2.2 Orchestration model (Confirmed — BRD §5, §14)

Logical pipeline (full platform; phase availability follows roadmap):

```
Request (IDE / CLI / CI webhook)
  → L6 Recall (Cognee) → L2 Enrich (Graphify)     [V2]
  → L5 Pack / Search (Repomix, grepai, Qdrant)    [MVP+]
  → L3 Resolve (Serena)                             [MVP+]
  → L1 Expand (CodeGraph / FalkorDB)                [V1+]
  → L4 Compress (Headroom)                          [V1+]
  → Packed context + citations → LLM / IDE
```

**MVP subset:** Ingest & pack (L5) → Symbol resolve (L3) → Basic phase-aware prompt assembly.  
**V1 adds:** Structural expand (L1) → Compress & budget (L4) → graph/blast/telemetry surfaces.  
**V2 adds:** Multi-modal enrich (L2) → Memory recall/governance (L6).

### 2.3 Boundary discipline (Confirmed — constitution V)

| Surface | Owns | Must not own |
|---------|------|--------------|
| **FastAPI orchestrator** | Indexing, graph, search, compression, memory, security policy, OpenAPI | DX chrome, Webview presentation logic that bypasses backend validation |
| **VS Code extension** | Commands, sidebar, Webviews, CodeLens, hover, status bar, settings, progress/cancel, offline, secure API client | Backend orchestration duplicated locally |
| **CLI** | Scriptable workflows; human- and machine-readable output when planned | Silent bypass of consent/RBAC/indexing policy |
| **Dashboards / Webviews** | Presentation, filtering, exploration; provenance, staleness, confidence, errors, safety warnings | Authoritative policy decisions |

---

## 3. Major Components & Responsibilities

### 3.1 Layer components

| Layer | Responsibility | Primary tech (Confirmed) | Roadmap |
|-------|----------------|--------------------------|---------|
| **L5** | Repo flatten/pack, hybrid BM25+vector search, MMR, phase-aware prompt assembly, embedding refresh | Repomix-style, grepai/claude-context, Qdrant, all-MiniLM-L6-v2 | MVP |
| **L3** | Definition, references, hover docs, rename scope, symbol-aware edit planning | Serena MCP | MVP |
| **L1** | Typed structural graph, blast radius, dependency visualization, hot entities / NL structural queries | CodeGraph/GitNexus, FalkorDB, tree-sitter/regex, codebase-memory-mcp | V1 |
| **L4** | Token budgets, adaptive summarization, relevance scoring, compression telemetry | Headroom-style | V1 |
| **L2** | Multi-modal ingestion & cross-artifact linking | Graphify-style | V2 |
| **L6** | Entity memory, temporal edges, recall explainability, TTL/decay/pin/forget, PII redaction | Cognee-style | V2 |

### 3.2 Cross-cutting components (Confirmed)

- **Indexer:** Local FS / Git; auto-index on install; incremental on file save; respects `.gitignore`; excludes `.env`, secrets, build outputs, dependency folders, binaries unless approved (BRD §6, §10, Appendix C; constitution III).
- **Observability:** OpenTelemetry-compatible metrics — token usage, recall precision, latency, memory recall rate, cost dashboard (BRD §10 NFR; constitution Approved Technical Direction).
- **Security / governance:** RBAC per repo path; PII scrubbing; consent flag for query-time external LLM; provenance on all intelligence outputs (BRD §10; constitution III).
- **Visualization:** `graph.html` (vis-network); React Flow in VS Code Webview (BRD §9 FR-09, §14).
- **GitHub Action:** In scope (BRD §6); contract detail **Missing Evidence**.

### 3.3 FR → Layer → Surface mapping (Confirmed)

| FR | Layer | Primary phase | Surfaces (Confirmed / Proposed) |
|----|-------|---------------|----------------------------------|
| FR-01 Repo packing | L5 | MVP | API `POST /index`, CLI, extension auto-index |
| FR-02 Hybrid search | L5 | MVP | API `POST /context`, CLI `contextos ask` |
| FR-03 Phase-aware templates | L5 | MVP | API packing path; extension Pack Context |
| FR-04 Definition lookup | L3 | MVP | Serena MCP; extension hover/commands |
| FR-05 Find references | L3 | MVP | Serena MCP; extension |
| FR-06 Rename scope | L3 | MVP | Serena MCP; extension |
| FR-07 Structural graph | L1 | V1 | Indexer → FalkorDB; `POST /index` graph_nodes |
| FR-08 Blast radius | L1 | V1 | `GET /blast/{file_name}`; `POST /context` blast_radius field |
| FR-09 Graph visualization | L1 | V1 | `GET /graph.html?repo=`; React Flow Webview |
| FR-10 Codebase memory cache | L1 | V1 | codebase-memory-mcp (**integration contract NEEDS CLARIFICATION**) |
| FR-11 Token budgets | L4 | V1 | Headroom in `POST /context` path |
| FR-12 Adaptive summarization | L4 | V1 | Headroom in context pipeline |
| FR-13 Compression telemetry | L4 | V1 | OTel + `contextos_token_dashboard.html` |
| FR-14 Multi-modal ingestion | L2 | V2 | Graphify ingest (**auth/scope NEEDS CLARIFICATION**) |
| FR-15 Cross-artifact linking | L2 | V2 | Graphify entity resolution |
| FR-16 Entity memory store | L6 | V2 | Cognee-style store |
| FR-17 Cross-session recall | L6 | V2 | Memory in `POST /context` response field `memory` |
| FR-18 Memory governance | L6 | V2 | TTL/decay/pin/forget/PII; copilot-instructions link |

---

## 4. Design Principles

1. **Evidence-first** — No invented APIs, roles, or compliance claims (constitution I).
2. **Layer integrity** — Single responsibility per layer; no duplicate orchestration in clients (constitution II).
3. **Local-first privacy** — Index without external LLM exfil; consent for query-time LLM (constitution III; BRD Appendix C).
4. **Provenance everywhere** — Citations with file:line and confidence on packed context (BRD §14).
5. **Measurable intelligence** — Search, compression, blast radius, memory, and latency claims require measurable acceptance criteria (constitution IV; BRD §10, §12).
6. **Roadmap governance** — MVP → V1 → V2 layer order preserved (constitution Roadmap Governance; BRD §15).
7. **Degraded operation** — Graceful degraded search on partial index; 99.5% indexer availability target (BRD §10).

---

## 5. Confirmed vs Proposed vs Assumptions vs Risks vs Open Questions

### Confirmed architecture

- Six layers L1–L6 with responsibilities as in BRD §5 / constitution II.
- Stack: FastAPI/Python 3.11, FalkorDB, Qdrant 384-dim, all-MiniLM-L6-v2 local, Serena, Repomix/Headroom/Cognee-style components, React Flow/vis-network, OpenTelemetry.
- Evidenced APIs (Appendix D): `GET /`, `POST /index`, `POST /context`, `GET /blast/{file_name}`, `GET /graph.html?repo=`.
- MVP = L5+L3; V1 = L1+L4; V2 = L2+L6.
- Security defaults: `.gitignore`, `.env` exclusion, no index-time LLM exfil, RBAC per path, PII redaction (L2/L6 paths), provenance.

### Proposed architecture (implied, not fully specified)

- Internal module split inside FastAPI (indexing / search / graph / compression / memory / security / telemetry packages) — **Proposed** for implementability; package names not in BRD.
- CLI JSON + text dual output modes — constitution says “when planned”; exact schema **NEEDS CLARIFICATION**.
- Authentication mechanism for API (API key, SSO, local-only trust) — **Not evidenced in provided inputs.**
- Exact HTTP error model beyond REST norms — **Not evidenced**; propose standard FastAPI/OpenAPI error envelope as **Proposed**.

### Assumptions (BRD §13)

- Git is source of truth; monorepo ≤1M LOC for MVP.
- Teams use VS Code or JetBrains (80%+ coverage).
- LLM provider supports 128k context; ContextOS compresses to fit.
- Vector DB available in VPC or local Docker (BRD mentions Qdrant/Pinecone; **approved stack is Qdrant** — see ADR / open questions).

### Risks (BRD §13)

- Graph index drift on large PRs → delta indexing + staleness badge.
- Compression drops key symbols → symbol-preservation tests + recall gate.
- Memory bloat / PII leak → TTL, RBAC, scrub, pin/forget.
- MCP ecosystem instability → pin versions; fallback to regex parsing.
- GitHub/GitLab API rate limits → cache + incremental indexing.
- VPC security approval for indexing → local stores, no exfil, `.gitignore`.

### Open questions / Missing Evidence

1. JetBrains: MVP depth vs post-MVP — BRD IN SCOPE both; roadmap MVP names VS Code + CLI only.
2. Notion/Confluence/Jira/Figma/Slack/Loom indexer auth, scopes, and MVP cut — IN SCOPE broadly; multi-modal is V2.
3. Pinecone vs Qdrant-only — BRD assumption lists Pinecone; constitution/BRD primary stack is Qdrant.
4. Enterprise air-gap / VPC tier boundaries beyond “out of scope without enterprise tier”.
5. Exact RBAC model (roles, path patterns, authn) — required, schema not specified.
6. GitHub Action triggers and CI payload schema — mentioned, not specified.
7. Role-based context packs (PM/Dev/QA/DevOps) content schema — mentioned, not specified.
8. codebase-memory-mcp API surface relative to FastAPI — integration boundary **NEEDS CLARIFICATION**.
9. Token dashboard hosting (static from API vs separate asset) — filename evidenced; delivery mechanism partial.
10. LLM routing config surface beyond `GEMINI_API_KEY` example — partial evidence only.

---

## 6. Non-Functional Architecture Implications

| NFR (BRD §10) | Architectural implication |
|---------------|---------------------------|
| Search p95 <800ms @ 500k LOC | Qdrant HNSW + BM25 hybrid; keep embedding local CPU; index freshness for MVP search path |
| Blast p95 <2s @ 3-hop / 10k nodes | Pre-indexed FalkorDB edges; depth-bounded queries (V1) |
| Compression 60–95%, recall@10 >0.92 | L4 relevance scorer + symbol preservation gates (V1) |
| Full index <15 min / 1M LOC; delta <60s | Incremental indexer; tree-sitter/regex parsers |
| 99.5% indexer availability | Health endpoint reports falkor/qdrant; degraded search mode |
| IDE <3 clicks to Ask ContextOS | Extension command/UX budget (design later) |
| OpenTelemetry | Instrument orchestrator request path + compression/memory metrics |

---

## 7. Out of Scope (Confirmed — BRD §6)

- LLM training / fine-tuning (BYO: Gemini, GPT-4, Ollama).
- Code execution sandbox.
- Full project management suite (integrate via Jira API — detail **NEEDS CLARIFICATION** for V2).
- Real-time collaborative editing (OT/CRDT).
- Binary artifact analysis (Docker layers “v1” note in BRD — treat as out of scope for current roadmap unless clarified).
- On-prem air-gapped without explicit enterprise tier.

---

## 8. Architecture readiness gate

| Gate item | Status |
|-----------|--------|
| Business objectives mapped to layers | Yes (BRD §3, §16) |
| Components & boundaries identified | Yes |
| Evidenced APIs documented | Yes (Appendix D) |
| Store models sketched with Missing Evidence marked | Yes |
| Security posture documented | Yes |
| Deployment pattern (local Docker Compose POC) documented | Yes |
| MVP / V1 / V2 separation explicit | Yes |
| Implementation guidelines for teams | Yes |
| User stories / backlog | **Not this agent’s deliverable** |

**Architecture ready for user-story generation:** Yes — subject to documented open questions remaining non-blocking for backlog drafting.
