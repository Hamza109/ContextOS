# ContextOS — Implementation Guidelines

**Audience:** Backend, Frontend/Extension, Data, DevOps, QA agents  
**Constraint:** Project-level guidance only — no feature backlog or application code in this document.  
**Sources:** Constitution v1.0.0; BRD v0.9 Draft; this architecture set.

---

## 1. Recommended Folder Structure (Proposed)

BRD does not prescribe a monorepo layout. The following is **Proposed** to enforce constitution boundary discipline. Adjust only via ADR.

```
ContextOS/
├── docs/
│   ├── BRD_Context_OS.md
│   ├── architecture/          # this document set
│   ├── backlog/               # later: user stories
│   └── design/                # later: UI design per feature
├── .specify/
│   └── memory/constitution.md
├── services/
│   └── orchestrator/          # FastAPI + Python 3.11
│       ├── app/
│       │   ├── api/           # routers: health, index, context, blast, graph
│       │   ├── services/      # L5/L3/L1/L4/L2/L6 domain services
│       │   ├── adapters/      # Qdrant, FalkorDB, Serena, embeddings, packers
│       │   ├── security/      # ignore rules, consent, RBAC, PII
│       │   ├── telemetry/     # OpenTelemetry
│       │   └── main.py
│       ├── tests/
│       ├── pyproject.toml / requirements
│       └── Dockerfile
├── clients/
│   ├── vscode/                # VS Code extension
│   ├── cli/                   # contextos CLI
│   └── jetbrains/             # later
├── deploy/
│   └── docker-compose.yml     # Qdrant + FalkorDB + API
└── specs/                     # Spec Kit feature specs (later)
```

**Confirmed ownership:** orchestrator owns intelligence; extension/CLI own DX; Webviews own presentation (constitution V).

---

## 2. Naming Conventions (Proposed where not evidenced)

| Area | Convention | Status |
|------|------------|--------|
| Python modules | `snake_case` | Proposed (Python norm) |
| API paths | As Appendix D (`/index`, `/context`, `/blast/{file_name}`, `/graph.html`) | Confirmed |
| Layers in code | Prefix or package by layer `l5_search`, `l3_symbol`, … | Proposed |
| Metrics | OTel names reflecting token/recall/latency/memory | Confirmed concerns; exact metric names **Missing Evidence** |
| Extension commands | Include `contextos.` prefix | Proposed |
| Feature specs | `specs/<feature-name>/` Spec Kit layout | constitution Documentation Requirements |

---

## 3. Coding Standards (Architecture-level)

1. **No intelligence orchestration in the extension** beyond API calls and MCP client wiring for Serena UX.
2. **No invented endpoints** — stick to Appendix D unless an ADR adds FR-implied Proposed APIs.
3. **Evidence-first** — if a field/workflow is unclear, mark `NEEDS CLARIFICATION` in specs; do not invent.
4. **Ignore policy applied once** in orchestrator security module; clients must not “helpfully” upload excluded paths.
5. **Provenance required** on context, graph, search, memory, compression outputs (constitution III).
6. **Measurable claims** need tests (constitution IV): search latency, compression recall, blast accuracy, memory recall.
7. **OpenAPI is source of truth** for HTTP; regenerate clients when contracts change.
8. **Do not commit secrets**; use secure storage / env outside repo.

---

## 4. Layer Responsibilities & Dependency Rules

```
Clients → API routers → security middleware → domain services → adapters → stores/MCP
```

| From \ To | L5 | L3 | L1 | L4 | L2 | L6 | Clients |
|-----------|----|----|----|----|----|----|---------|
| L5 | — | may call for symbol enrichment | V1 expand optional | provides chunks to L4 | — | — | never |
| L3 | — | — | may expand ambiguous symbols (V1) | — | — | — | MCP to IDE |
| L1 | — | — | — | — | V2 links | — | viz only via API |
| L4 | consumes L5 packs | should preserve symbols (L3) | may use blast filters | — | — | — | dashboard via API |
| L2 | embeddings may share model | — | link to code nodes | — | — | — | — |
| L6 | — | — | — | — | may cite artifacts | — | — |

**Roadmap rule:** Do not ship L1/L4 behavior as MVP blockers; do not require L2/L6 for V1 exit criteria (BRD §15).

---

## 5. Module Boundaries

| Module | May depend on | Must not |
|--------|---------------|----------|
| `api/*` | services, security, telemetry | direct DB drivers (prefer services) — Proposed |
| `services/l5_*` | Qdrant adapter, packer, embedder | FalkorDB writes in MVP unless shared metadata |
| `services/l3_*` | Serena adapter | reimplement LSP |
| `services/l1_*` | FalkorDB, parsers | call external LLM for graph build |
| `services/l4_*` | pack results; optional LLM summarization **with consent** | index-time exfil |
| `services/l2_*` / `l6_*` | Graphify/Cognee adapters; PII scrubber | skip redaction |
| VS Code Webview | host bridge messages | trust unsanitized backend HTML/JS blindly |

---

## 6. Security Implementation Checklist

- [ ] `.gitignore` respected during walk
- [ ] `.env` and secret patterns excluded
- [ ] No external LLM calls in `/index` path
- [ ] Consent gate before query-time provider calls
- [ ] RBAC path checks when auth model defined (**Blocked on Missing Evidence for schema**)
- [ ] PII scrubber on L2 ingest and L6 write
- [ ] Webview message schema validation
- [ ] Audit/provenance fields on returned context
- [ ] Telemetry respects opt-out when defined

---

## 7. Observability Guidelines

Instrument at orchestrator boundaries:

- `/index` duration, files, embeddings, graph_nodes
- `/context` latency; search vs compress vs memory spans (phase-dependent)
- Compression ratio / tokens_before / tokens_after (V1)
- Blast query latency (V1)
- Memory recall latency (V2)
- Health of Qdrant / FalkorDB

Export via OpenTelemetry-compatible pipeline (BRD §10). Backend choice for metrics UI beyond `contextos_token_dashboard.html`: **Missing Evidence**.

---

## 8. Performance Budgets (from BRD — do not silently weaken)

| Budget | Target | Phase |
|--------|--------|-------|
| Hybrid search p95 | <800ms @ 500k LOC | MVP+ |
| Ask in IDE | <2s symbol-accurate context (MVP exit) | MVP |
| Demo explain | <8s | POC |
| Blast p95 | <2s @ 3-hop / 10k nodes | V1 |
| Full index | <15 min @ 1M LOC | L5+L1 |
| Delta index | <60s (100-file); ~0.5s single file save | L5+L1 |
| Memory recall p95 | <1.2s | V2 |
| Compression | 60–95% savings; recall@10 >0.92 | V1 |

If an increment cannot meet a target, Spec Kit plan must state scoped target and gap (constitution IV).

---

## 9. Testing Expectations (Architecture-level)

| Claim | Test type |
|-------|-----------|
| Ignore / .env exclusion | Fixture repos with forbidden paths |
| No index-time exfil | Network allowlist / mock asserts zero LLM calls on `/index` |
| Search quality | recall@10 harness (FR-02 / §12) |
| Symbol accuracy | Serena integration tests (FR-04 99% claim — measure method **NEEDS CLARIFICATION**) |
| Blast accuracy | Graph fixtures vs expected dependents/tests (FR-08 / §12 >95%) |
| Compression | tokens_before/after + symbol preservation + recall gate (FR-12..13, §13 risk) |
| Memory | recall precision + PII redaction (FR-17..18) |
| Degraded mode | Partial Qdrant/Falkor failure still serves reduced results |

Validation reports must distinguish planned/implemented/executed/passed/failed/skipped/blocked (constitution Verification Gate).

---

## 10. Documentation & Handoff

- Architecture lives under `docs/architecture/`.
- After code changes that affect structure, keep graphify graph updated when exploring code (workspace rule) — N/A for this docs-only drop.
- Agent handoffs append to `.cursor/agent-handoffs/handoff.md`.
- Next workflow agent: user-story generation — **not** started by this architecture pass.

---

## 11. What Implementers Must Not Do

- Reorder MVP → V1 → V2 layers without plan rationale.
- Add Pinecone (or other hosts) without ADR vs Qdrant default.
- Invent RBAC roles, GitHub Action payloads, or connector auth.
- Generate user stories inside architecture docs.
- Ship UI that hides staleness, missing provenance, or consent warnings.
