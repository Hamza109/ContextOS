# ContextOS — Technology Stack

**Sources:** BRD §6, §14–§15; constitution “Approved Technical Direction”  
**Rule:** Do not substitute without an ADR + Missing Evidence marking.

---

## 1. Backend / Orchestrator

| Technology | Role | Phase | Evidence |
|------------|------|-------|----------|
| **Python 3.11** | Runtime | All | BRD §14; constitution |
| **FastAPI** | API orchestrator, OpenAPI | All | BRD §14; constitution |
| **tree-sitter / regex** | Import/AST extraction for L1 | V1 | BRD FR-07, Appendix C |
| **sentence-transformers / all-MiniLM-L6-v2** | Local CPU embeddings, 384-dim | MVP+ | BRD §10, §14 |
| **Repomix-style packing** | Repo flatten to LLM-optimized XML | MVP | FR-01; constitution |
| **grepai / claude-context patterns** | Hybrid BM25 + vector, MMR | MVP | FR-02; BRD §14 |
| **Headroom-style compression** | Budgets, summarization, telemetry | V1 | FR-11..13; constitution |
| **CodeGraph / GitNexus** | Structural graph builders | V1 | FR-07; BRD §5 |
| **Graphify-style** | Multi-modal ingestion | V2 | FR-14; constitution |
| **Cognee-style** | Persistent entity memory | V2 | FR-16..18; constitution |
| **Serena MCP** | Symbol/LSP navigation | MVP | FR-04..06; constitution |
| **codebase-memory-mcp** | Hot entity / NL structural queries | V1 | FR-10; integration **NEEDS CLARIFICATION** |

**LLM providers (BYO, not trained by ContextOS):** Gemini 1.5 Flash / GPT-4 / Ollama; example env `GEMINI_API_KEY` (BRD §14). Query-time only with consent.

---

## 2. Data Stores

| Technology | Role | Phase | Evidence |
|------------|------|-------|----------|
| **Qdrant** | Vector DB, collection `codebase`, `:6333` | MVP | BRD §14; constitution |
| **FalkorDB** | Structural (± multi-modal) graph, `redis://localhost:6379` | V1 (+V2 artifacts) | BRD §14; constitution |
| **Pinecone** | Mentioned only in BRD §13 assumptions as alternative | — | **Not in constitution approved stack.** Using Pinecone requires ADR. Prefer Qdrant. |
| Cognee persistence engine | Memory | V2 | Style confirmed; engine **Missing Evidence** |

---

## 3. Frontend / Client Surfaces

| Technology | Role | Phase | Evidence |
|------------|------|-------|----------|
| **VS Code Extension** | Primary IDE: commands, Webviews, hover, settings, progress | MVP | BRD §15; constitution |
| **CLI** (`contextos ask`) | Scriptable ask/index workflows | MVP | BRD §15 |
| **vis-network** | `graph.html` interactive graph | V1 | FR-09; BRD §14 |
| **React Flow** | VS Code Webview graph / blast viz | V1 | FR-09; BRD §14 |
| **JetBrains Extension** | IDE parity | Later | BRD §6 IN SCOPE; MVP roadmap does not list — **NEEDS CLARIFICATION** |
| Token dashboard HTML | Compression cost UX | V1 | FR-13 `contextos_token_dashboard.html` |

**UI framework choices inside Webviews (React version, bundler):** **Not evidenced** beyond React Flow usage — **Proposed** align with VS Code Webview norms when implementing.

---

## 4. Authentication / Security Tooling

| Concern | Direction | Status |
|---------|-----------|--------|
| Secrets storage | Approved secure storage only (extension secure storage; no secrets in repo) | constitution III |
| Indexing policy | `.gitignore`, exclude `.env`, secrets, build outputs, dependency folders, binaries | constitution III; FR-01 |
| RBAC | Per repo path | Confirmed requirement; **mechanism Missing Evidence** |
| PII | Scrub on memory + multi-modal paths | FR-18; constitution III |
| Webview IPC | Validate/sanitize messages and responses | constitution III |
| Encryption at rest / in transit | **Not evidenced** beyond local/VPC-friendly posture | **Missing Evidence** |

---

## 5. Storage / Artifacts

| Artifact | Role | Phase |
|----------|------|-------|
| Local repo FS / Git | Source of truth for indexing | All |
| `.github/copilot-instructions.md` | Guidance surface linked to memory/decisions | V2 example in FR-18 / Appendix B |
| Docker volumes for Qdrant/FalkorDB | Local POC | BRD §15 Zero Risk POC |

Notion/Confluence/Jira/Figma/Loom connectors: IN SCOPE conceptually; **auth SDKs / protocols Missing Evidence**; multi-modal depth **V2**.

---

## 6. Infrastructure

| Technology | Role | Evidence |
|------------|------|----------|
| **Docker Compose** | Local POC: FalkorDB + Qdrant + API | BRD §15 Zero Risk POC ($0 infra OSS) |
| VPC deployment | Enterprise / V2 hardening | BRD §15 V2; air-gap without enterprise tier OUT OF SCOPE (§6) |
| Kubernetes / reverse proxy / CDN | **Not evidenced** for MVP | Mark **Proposed** only if ops requires; otherwise later ADRs |
| GitHub Action runner | CI webhook integration | BRD §6; payload **Missing Evidence** |

---

## 7. CI/CD

| Item | Status |
|------|--------|
| GitHub Action as product feature | Confirmed IN SCOPE |
| ContextOS’s own build/test/release pipeline | **Not evidenced in provided inputs** |
| Extension marketplace publishing | **Not evidenced** |

---

## 8. Monitoring / Logging / Observability

| Technology | Role | Evidence |
|------------|------|----------|
| **OpenTelemetry-compatible** | Token usage, recall precision, latency, memory recall rate, cost | BRD §10 NFR; constitution |
| Compression telemetry | ratio, recall@k, cost-saved | FR-13 |
| Staleness badge | UX for index drift | BRD §13 mitigation |
| Log aggregation product | **Not evidenced** | **Missing Evidence** |
| APM vendor | **Not evidenced** | Prefer OTel exporter flexibility (**Proposed**) |

---

## 9. Stack by Roadmap Slice

### MVP (L5 + L3)

FastAPI, Qdrant, all-MiniLM-L6-v2, Repomix-style, hybrid search, Serena MCP, VS Code extension, CLI.

### V1 (adds L1 + L4)

FalkorDB, CodeGraph/GitNexus/tree-sitter, Headroom-style, graph.html/React Flow, blast API, token dashboard, OTel compression metrics, PR risk support.

### V2 (adds L2 + L6)

Graphify-style multi-modal, Cognee-style memory + governance, enterprise RBAC + VPC hardening, broader ingest sources.

---

## 10. Explicit Non-Stack (Out of Scope / Do Not Assume)

- LLM fine-tuning stacks
- Code execution sandboxes
- OT/CRDT collaborative editors
- Binary/Docker layer analysis (per BRD §6)
- Pinecone as default (assumption only — not approved without ADR)
