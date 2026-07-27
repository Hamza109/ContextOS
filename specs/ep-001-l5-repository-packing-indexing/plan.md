# Implementation Plan: EP-001 L5 Repository Packing & Indexing

**Branch**: `001-ep-001-l5-repository-packing-indexing` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/ep-001-l5-repository-packing-indexing/spec.md`

---

## Summary

EP-001 delivers the MVP L5 foundation: **Repomix-style repository packing** with token pre-calculation and binary skip, plus **local `all-MiniLM-L6-v2` (384-dim) embeddings** stored in **Qdrant `codebase`**, orchestrated exclusively by **FastAPI** via confirmed **`POST /index`**. The VS Code extension triggers auto-index on install/activation and incremental re-index on file save, owning progress/cancellation UX only — never indexing policy. Query-time external LLM use is deny-by-default without consent (US-016); the index path never exfiltrates source to external LLM providers. Hybrid search, Serena, L1 graph population, L4 compression, and L2/L6 are **out of scope**.

**Technical approach (Confirmed stack):** FastAPI + Python 3.11 orchestrator → security ignore/exclusion → packer → ~500-token chunker → local embedder → Qdrant; extension calls `POST /index`; OpenTelemetry-compatible spans/metrics for indexing duration and counts.

---

## Technical Context

**Language/Version**: Python 3.11 (orchestrator — Confirmed); TypeScript for VS Code extension (Confirmed surface; exact VS Code API / bundler versions **Not evidenced** — **Proposed** align with current VS Code extension norms when scaffolding)

**Primary Dependencies**: FastAPI; sentence-transformers/`all-MiniLM-L6-v2`; Qdrant client; Repomix-style packing (style Confirmed; library pin **NEEDS CLARIFICATION** if using a specific package vs in-house adapter); OpenTelemetry-compatible SDK (**Proposed** exporter destination **NEEDS CLARIFICATION** per ADR-011)

**Storage**: Qdrant collection `codebase` (384-dim HNSW — Confirmed); local filesystem/Git as source of truth; FalkorDB **not written** for EP-001 MVP (`graph_nodes` MAY be `0`); pack artifact persistence location beyond “available for downstream” — **Proposed** local orchestrator-managed artifact/cache keyed by `repo_name` (**NEEDS CLARIFICATION** exact path/schema per OQ-PACK)

**Testing**: **Proposed** pytest for orchestrator (architecture guidelines); VS Code extension test runner **Not evidenced** — **Proposed** `@vscode/test-electron` or equivalent when scaffolding; network/exfil assertions on `/index` (Confirmed test expectation in implementation-guidelines)

**Target Platform**: Local/VPC Docker Compose POC (API + Qdrant; FalkorDB may be present in Compose but unused for EP-001 graph writes — ADR-013); VS Code on developer workstations (ADR-007)

**Project Type**: Multi-surface platform — FastAPI orchestrator service + VS Code extension client (CLI not primary acceptance for EP-001)

**Performance Goals** (indexing only — Confirmed BRD §10 / §14):
- Full monorepo index <15 minutes for 1M LOC (NFR-001)
- Delta index <60 seconds for 100-file delta (NFR-002)
- Single-file save re-index illustrative ~0.5s (NFR-003 — hardware-gated)
- Auto-index ~200 files illustrative ~10s (NFR-004 — hardware-gated)
- Search p95 / recall@k **out of scope** (EP-002)

**Constraints**:
- Constitution III privacy defaults on every index walk
- No index-time external LLM exfil (ADR-003)
- No invented HTTP endpoints beyond Appendix D; OQ-14 incremental API remains Proposed/NEEDS CLARIFICATION
- Clients MUST NOT bypass orchestrator policy (constitution V; ADR-002)
- Pinecone not default (ADR-008)

**Scale/Scope**: Pack target up to 500k LOC (FR-01); MVP monorepo assumption ≤1M LOC (A-01); stories US-001, US-002, US-011, US-012, US-016

---

## ContextOS Technical Impact

**Affected Layers**:
| Layer | Impact | Evidence |
|-------|--------|----------|
| L1 | N/A for delivery — reserve `graph_nodes=0` | Spec; api-contract; V1 roadmap |
| L2 | N/A | V2; out of scope |
| L3 | N/A | EP-003 |
| L4 | N/A as primary — referenced only as allowed compressed/packed path narrative for US-016 | Appendix C; ADR-006 |
| **L5** | **Primary** — packing + embedding index | Spec; ADR-003; FR-01 |
| L6 | N/A | V2 |

**Affected Surfaces**:
| Surface | Impact |
|---------|--------|
| FastAPI / API | **Affected** — owns `POST /index`, packing, embedding, policy |
| VS Code extension | **Affected** — install/activation + save triggers; progress/cancel UX |
| CLI | N/A as EP-001 primary acceptance (EP-004) |
| Dashboard / Webview / viz | N/A for EP-001 acceptance |
| GitHub Action | N/A (Future) |
| Background indexer | **Affected** as backend indexing behavior invoked by API/extension (not a separate product surface) |
| Telemetry | **Affected** — OTel-compatible indexing instrumentation (ADR-011; implementation-guidelines §7) |

**Data Stores / Services**: Qdrant `codebase`; local embedder; local FS/Git; FalkorDB unused for writes in this feature

**Privacy / Security Controls**: `.gitignore`; exclude `.env`, secrets, build/deps (`node_modules`, `dist`), `.git`, binaries; no index-time LLM exfil; query-time consent deny-by-default; path provenance on chunks (`file_path` / `repo_name`); RBAC schema **NEEDS CLARIFICATION** (OQ-01) — do not invent enforcement detail; PII redaction N/A as primary (L2/L6)

**Observability**: Instrument `/index` duration, `files_indexed`, `embeddings`, `graph_nodes` (implementation-guidelines §7). Exact metric names and exporter backend **Missing Evidence** — **Proposed** spans/attributes aligned to response fields only

**Measurable Intelligence Claims** (this feature): Indexing speed NFRs (SC-005, SC-006, observational SC-008 timings); pack correctness; exclusion correctness; zero index-time exfil. **Not** search recall/p95, blast accuracy, compression recall, memory recall

---

## Constitution Check

*GATE: Planning Gate — evaluate before and after design.*

| Gate item | Status | Evidence / mitigation |
|-----------|--------|------------------------|
| Technical context evidence-based or marked Proposed / NEEDS CLARIFICATION | **Pass** | Technical Context section |
| Affected layers, APIs, stores, extension, telemetry identified | **Pass** | ContextOS Technical Impact; Components; API Design |
| Security, privacy, performance, reliability documented | **Pass** | Security / Performance / Reliability sections |
| Testing covers measurable claims | **Pass** | Testing Strategy — indexing NFRs only |
| Architecture deviations justified | **Pass** | None vs ADR-001..014 for EP-001 scope; OQ-14 reuse of `POST /index` labeled Proposed |
| Evidence-first (constitution I) | **Pass** | No invented endpoints/metrics/schemas; OQs carried |
| Six-layer integrity (II) | **Pass** | L5 primary; deferred layers explicit |
| Privacy/local-first (III) | **Pass** | FR-009..012, FR-018..021; ADR-012 |
| Measurable claims (IV) | **Pass** | SC-001..010 mapped; search metrics excluded |
| Boundary discipline (V) | **Pass** | FastAPI owns policy; extension triggers only |
| Roadmap order | **Pass** | MVP L5 indexing; no L1/L4/L2/L6 pull-forward |

**Applicable governance rule IDs**: Constitution I–V; Approved Technical Direction; Planning Gate; ADR-001, ADR-002, ADR-003, ADR-008, ADR-009, ADR-011, ADR-012, ADR-013

**Required mitigations**:
- Carry OQ-14, OQ-US016, OQ-PACK, OQ-OVERRIDE, OQ-01, OQ-HTTP without inventing resolutions
- Until OQ-14 resolves: **Proposed** reuse `POST /index` with optional narrower scope fields — not confirmed contract
- Until consent UX clarified: deny-by-default gate only (behavioral), no invented settings UI schema
- Until pack schema freeze: implement FR-01 behavioral XML-oriented pack + token pre-calc only

### Constitution Check (re-check after design)

| Item | Post-design status |
|------|-------------------|
| Planning Gate | **Met** — ready for Task Generator with open questions carried |
| Deviations | None unjustified |
| Blocking for plan draft | None if OQs remain labeled; **blocking for US-012 API contract freeze** = OQ-14; **blocking for consent UX detail** = OQ-US016; **blocking for pack contract freeze** = OQ-PACK |

---

## Project Structure

### Documentation (this feature)

```text
specs/ep-001-l5-repository-packing-indexing/
├── spec.md              # Approved Spec Gate
├── plan.md              # This file
├── research.md          # Optional Phase 0 — not required for this plan drop
├── data-model.md        # Optional Phase 1 — logical model covered herein
├── quickstart.md        # Optional Phase 1
├── contracts/           # Optional OpenAPI excerpt — sync with orchestrator later
└── tasks.md             # NOT created by plan-generator
```

### Source Code (repository root)

**Source structure not present in repository** (as of 2026-07-27: `docs/`, `.specify/`, `specs/`, `.cursor/` only).

**Proposed** structure (from `docs/architecture/implementation-guidelines.md` §1 — Proposed layout):

```text
ContextOS/
├── docs/
│   ├── architecture/
│   └── backlog/
├── services/
│   └── orchestrator/                 # FastAPI + Python 3.11
│       ├── app/
│       │   ├── api/                  # routers: index (+ health if shared)
│       │   ├── services/             # l5_pack, l5_embed/index orchestration
│       │   ├── adapters/             # qdrant, embeddings, packer, fs walker
│       │   ├── security/             # ignore rules, consent gate, exclusions
│       │   ├── telemetry/            # OpenTelemetry
│       │   └── main.py
│       ├── tests/
│       │   ├── unit/
│       │   ├── integration/
│       │   └── contract/
│       ├── pyproject.toml / requirements
│       └── Dockerfile
├── clients/
│   └── vscode/                       # extension: activate, save, progress/cancel
│       ├── src/
│       └── tests/                    # Proposed when scaffolding
├── deploy/
│   └── docker-compose.yml            # Qdrant (+ API); FalkorDB optional unused writes
└── specs/
    └── ep-001-l5-repository-packing-indexing/
```

**Structure Decision**: Adopt the architecture-guidelines **Proposed** `services/orchestrator` + `clients/vscode` layout when implementation begins. No alternate option trees. Adjust only via ADR if a different monorepo layout is chosen.

---

## Complexity Tracking

> No constitution violations requiring justification for EP-001.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |

---

## Technical Approach

### Confirmed architecture

1. **Orchestrator ownership**: FastAPI indexes, packs, embeds, enforces ignore/consent policy, owns OpenAPI (ADR-002, constitution V).
2. **API**: Confirmed `POST /index` with `{repo_path, repo_name}` → `{files_indexed, graph_nodes, embeddings, time_ms}` (Appendix D; api-contract §2.2).
3. **Embeddings**: Local `sentence-transformers/all-MiniLM-L6-v2`, 384-dim, CPU; store in Qdrant `codebase`; no index-time LLM exfil (ADR-003).
4. **Packing**: Repomix-style LLM-optimized XML-oriented flatten; token pre-calc; binary skip (FR-01; constitution Approved Tech).
5. **Chunking**: ~500-token chunks for vectors (Appendix C; database-schema §2; FR-023).
6. **Privacy walk**: Respect `.gitignore`; exclude `.env`, secrets, build outputs, dependency folders, `.git`, binaries (ADR-012; FR-010, FR-011).
7. **Extension**: Trigger on install/activation and on save; progress/cancellation; call backend only (US-011, US-012; constitution V).
8. **Deploy**: Docker Compose local/VPC-friendly with Qdrant (ADR-013).
9. **Observability**: OpenTelemetry-compatible instrumentation of `/index` (ADR-011; guidelines §7).
10. **`graph_nodes`**: May return `0` until V1 L1 (api-contract).

### Proposed architecture (implementability; not fully specified in BRD)

1. **Internal packages**: `api/index`, `services/l5_*`, `adapters/{qdrant,embeddings,packer,fs}`, `security/{ignore,consent}`, `telemetry` — package names Proposed per implementation-guidelines.
2. **Incremental indexing (OQ-14)**: Prefer **Proposed** reuse of `POST /index` with optional narrower scope (e.g., changed paths) until product confirms — **do not invent** additional confirmed endpoints (ADR-009).
3. **Qdrant payload**: Logical fields `repo_name`, `file_path`, chunk content, 384-dim vector; Recommended `token_count`, `indexed_at`; Optional `content_hash` for delta skip (database-schema §2 — Proposed/Recommended as labeled).
4. **Index metadata store**: Proposed ops record for freshness/partial index (database-schema §6) — optional for EP-001 if response counts suffice; degraded-search UX owned by EP-005.
5. **Consent configuration**: Deny-by-default boolean/config gate in orchestrator; UX/storage **NEEDS CLARIFICATION** (OQ-US016). Extension settings may surface a consent toggle later — not invented as confirmed schema.
6. **HTTP status codes**: Proposed `200` / `400` / `403` / `409` / `500` per api-contract — **not confirmed** (OQ-HTTP).
7. **Pack persistence**: Store pack artifact such that EP-002 can consume later (FR-004); exact filesystem/API retrieval shape **NEEDS CLARIFICATION** (OQ-PACK) — behavioral availability required, not invented field inventory.
8. **Cancellation**: Extension cancellation cancels in-flight client request; server-side cancel semantics **Not evidenced** — **Proposed** best-effort abort of request context without inventing a cancel endpoint.

### Missing evidence

- OQ-14 incremental API fields
- OQ-US016 consent UX/storage
- OQ-PACK exact pack schema fields
- OQ-OVERRIDE approval workflow
- OQ-01 RBAC roles/path/authn
- OQ-HTTP confirmed status codes
- Authn mechanism for API (api-contract §1) — treat local loopback trust for POC (**Assumption**)
- Exact OTel exporter vendor
- Specific Repomix package vs in-house adapter
- Extension ↔ orchestrator base URL discovery/config (**Proposed** settings)

---

## Architecture Impact

| Area | Impact | Evidence |
|------|--------|----------|
| **Frontend** | VS Code extension triggers + progress/cancel; no Webview requirement for EP-001 acceptance | Spec Affected Surfaces; constitution V |
| **Backend** | New/updated FastAPI `POST /index` pipeline: walk → filter → pack → chunk → embed → upsert Qdrant | ADR-002, ADR-003; api-contract §2.2 |
| **Database / stores** | Qdrant `codebase` collection create/upsert; no FalkorDB graph writes required | database-schema §2; ADR-004 V1 |
| **Infrastructure** | Docker Compose: API + Qdrant (+ model weights volume); Falkor optional | ADR-013 |
| **AI Components** | Local sentence-transformers only on index path; optional Ollama is query-time local inference narrative (US-016), not indexing | ADR-003; Appendix C |

If “None” were claimed for backend/stores/extension, that would contradict the spec — **not applicable**.

---

## Components

| Component | Create / Modify | Responsibility |
|-----------|-----------------|----------------|
| `api` router `POST /index` | Create (source absent) | Validate request; return Index Result; OpenAPI |
| L5 pack service | Create | Repomix-style XML-oriented pack; token pre-calc; binary skip |
| L5 index/embed orchestration service | Create | Chunk ~500 tokens; call embedder; upsert Qdrant; timing |
| FS / gitignore walker adapter | Create | Walk `repo_path`; apply ignore + hard exclusions |
| Embedding adapter | Create | Load local all-MiniLM-L6-v2; encode on CPU; no external LLM |
| Qdrant adapter | Create | Ensure `codebase` collection 384-dim; upsert/delete by file scope |
| Security — ignore/exclusion policy | Create | Single enforcement point (guidelines §3.4); clients must not bypass |
| Security — consent gate | Create | Deny external LLM query-time without consent; index path always no-exfil |
| Telemetry module | Create | OTel spans/metrics for `/index` duration and counts |
| VS Code activation index trigger | Create | On install/activation call `POST /index` |
| VS Code save listener | Create | On save trigger incremental re-index (OQ-14 Proposed shape) |
| Extension progress / cancellation UX | Create | Progress notification; cancel token on client request |
| Extension API client | Create | Secure communication to orchestrator; no local policy reimplementation |
| Docker Compose / Dockerfile | Create | Qdrant + API for POC |
| Configuration | Create | Model path, Qdrant URL, orchestrator URL (extension settings) — exact keys **Proposed** |
| Shared OpenAPI / types | Create | Sync clients to orchestrator contract |
| Background index job (in-process) | Create as behavior | Indexing executed in backend when API invoked — not a separate product surface |

**Validators / Middleware**: Request body validation for `repo_path`/`repo_name`; path readability checks; **Proposed** concurrent-index guard (409 Proposed).

**Repositories**: Qdrant as vector repository; optional Proposed index-metadata repository.

---

## Data Model Changes

### New logical entities (from spec Key Entities + database-schema)

| Entity | Fields (Confirmed / Proposed) | Notes |
|--------|-------------------------------|-------|
| Repository Index Request | `repo_path`, `repo_name` (Confirmed) | API input |
| Packed Representation | XML-oriented content + token count (Confirmed behavior); field inventory **NEEDS CLARIFICATION** (OQ-PACK) | FR-001, FR-002, FR-022 |
| Embedding Chunk / Qdrant point | `repo_name`, `file_path`, content, embedding[384] (Confirmed concepts); `point_id` Proposed; `token_count` Recommended; `indexed_at` Recommended; `content_hash` Optional Proposed | database-schema §2 |
| Index Result | `files_indexed`, `embeddings`, `time_ms`, `graph_nodes` (Confirmed) | Response |
| Consent Configuration | Explicit consent/config flag (Confirmed requirement); storage/UX **NEEDS CLARIFICATION** | FR-021 |

### Modified entities

None preexisting in code (greenfield).

### Relationships

- Repository 1—* Embedding Chunks (by `repo_name` + `file_path`)
- Pack artifact associated with repository for EP-002 consumption (FR-004)

### Validation rules

- `repo_path` must be readable local path (api-contract §5)
- Ignore/exclusion applied **before** pack and embed persistence
- Default exclusions remain in force until OQ-OVERRIDE clarified (FR-012)

### Migration requirements

- Create Qdrant collection `codebase` with 384-dim vectors (HNSW mentioned — Confirmed mention)
- No RDBMS migration evidenced
- Re-index on file save replaces/updates chunks for that file (database-schema §2 Confirmed intent)

---

## API Design

### Confirmed: `POST /index`

**Request** (Confirmed):

```json
{
  "repo_path": "string",
  "repo_name": "string"
}
```

**Response** (Confirmed):

```json
{
  "files_indexed": 0,
  "graph_nodes": 0,
  "embeddings": 0,
  "time_ms": 0
}
```

**Side effects (Confirmed)**: Respect `.gitignore`; ignore `.env`, `node_modules`, `dist`, `.git`, binaries; local embeddings only; no code exfil to external LLM during indexing.

### Proposed / NEEDS CLARIFICATION: Incremental scope (OQ-14)

| Approach | Status |
|----------|--------|
| Reuse `POST /index` with additional optional fields for changed paths / delta mode | **Proposed only** — not confirmed |
| New dedicated delta endpoint | **Not permitted** as confirmed without ADR/product confirmation (ADR-009) |

Until OQ-14 resolves, implementation tasks MUST treat narrower-scope fields as provisional and document them as Proposed in OpenAPI.

### Out of scope APIs for this plan

- `POST /context` (EP-002) — may be stubbed later for consent tests only if needed; not EP-001 delivery
- `GET /blast/*`, `GET /graph.html` (V1)
- Invented cancel/status endpoints — **Not evidenced**

### Validation

| Input | Rule | Status |
|-------|------|--------|
| `repo_path` | Readable local path; policy applied server-side | Confirmed intent |
| `repo_name` | Non-empty logical name | Confirmed field; format bounds **Not evidenced** |
| Excluded paths | Never indexed | Confirmed |

### Error Handling

| Case | Status |
|------|--------|
| Invalid / unreadable path | Status mapping **Not evidenced** — Proposed `400` |
| RBAC denial | Proposed `403` when RBAC exists (OQ-01 open) |
| Index in progress | Proposed `409` |
| Failure | Proposed `500` |
| Error envelope | Proposed per api-contract §4 |

Do **not** treat Proposed codes as Confirmed acceptance until OQ-HTTP resolves.

### Consent-related API behavior (US-016)

- Index path: no external LLM calls regardless of consent (FR-009, FR-018 note).
- Query-time external provider calls: blocked without consent (FR-018); when consent present, only allowed compressed/packed context path (FR-019); local Ollama may avoid external exfil (FR-020).
- Exact consent read/write API **Not evidenced** — enforce as orchestrator security check wherever query-time LLM would be invoked; do not invent REST for consent CRUD.

---

## UI / UX Changes

| Item | Detail |
|------|--------|
| New Screens | None required for EP-001 primary acceptance |
| Extension UX | Progress indicator during index; cancellation control (FR-015) |
| Navigation | N/A |
| Forms | Consent UX **NEEDS CLARIFICATION** (OQ-US016) — deny-by-default without inventing UI |
| Accessibility | Not evidenced for EP-001 — N/A |
| Responsive | N/A (IDE extension) |

Webviews/dashboards not in EP-001 acceptance scope.

---

## Security Considerations

| Topic | Plan |
|-------|------|
| **Authentication** | Mechanism **Not evidenced** — POC Assumption: trusted local loopback (api-contract §1). Do not invent API keys/SSO as confirmed. |
| **Authorization** | RBAC per repo path required by constitution; schema **NEEDS CLARIFICATION** (OQ-01). MVP POC may defer path-RBAC enforcement detail while documenting gap. |
| **Input Validation** | Validate `repo_path`/`repo_name`; sanitize any future Webview messages (constitution III) — Webview not primary here. |
| **Sensitive Data** | Never pack/embed `.env`, secrets, ignored paths, binaries, `node_modules`, `dist`, `.git` (FR-010, FR-011). |
| **Secrets Management** | No secrets in repo; extension secure storage for any tokens when auth exists (constitution III). |
| **Index-time exfil** | Hard guarantee: embedding adapter and index service MUST NOT call external LLM APIs (NFR-005; ADR-003). |
| **Query-time consent** | Deny-by-default external LLM (NFR-007; FR-018..021). |
| **Client bypass** | Extension MUST NOT upload excluded paths or skip consent checks (FR-014; constitution V). |
| **Override of exclusions** | Not implemented until OQ-OVERRIDE clarified (FR-012). |
| **Security risks** | See Risks — path traversal via `repo_path`, accidental secret indexing, extension misconfiguration pointing at remote exfil endpoints (mitigate: allowlist local embedder only on index path). |

---

## Performance Considerations

| Concern | Plan |
|---------|------|
| **Caching** | Optional `content_hash` to skip unchanged files on delta (**Proposed**); not a Confirmed requirement |
| **Pagination** | N/A for `POST /index` response |
| **Database / store optimization** | Qdrant HNSW; batch upserts **Proposed** for throughput toward NFR-001 |
| **Scalability** | Target monorepo ≤1M LOC (A-01); CPU embedding is throughput bottleneck — measure against NFR-001/002 |
| **Load expectations** | Interactive IDE: install once + save-triggered deltas; concurrent index Proposed `409` |
| **Illustrative timings** | ~10s/200 files and ~0.5s single-file are hardware-gated observational targets (NFR-003, NFR-004) — do not invent stricter SLAs |

Search latency budgets are EP-002 — excluded.

---

## Reliability Considerations

- Indexer availability 99.5% and graceful degraded search are **adjacent** (EP-005 / US-014) — reference only.
- EP-001 SHOULD return accurate completion counts so downstream degraded mode can reason about partial indexes (**Proposed** partial failure reporting — exact operator UX EP-005).
- `graph_nodes=0` is success for MVP, not a failure.

---

## Observability

**Confirmed direction (ADR-011; implementation-guidelines §7):**

Instrument orchestrator `/index` with OpenTelemetry-compatible telemetry for:
- Duration / latency (`time_ms` aligned)
- `files_indexed`, `embeddings`, `graph_nodes`

**Not invented**: Exact metric names, dashboards, or recall/token cost metrics for this feature (token/cost dashboard is V1 FR-13). Exporter vendor **NEEDS CLARIFICATION**.

**Proposed**: Trace span `index.repository` with attributes `repo_name`, counts; log policy exclusion counts for audit without logging secret file contents.

---

## Testing Strategy

### Unit Tests

- Ignore / `.gitignore` / hard-exclusion walker (fixture trees with `.env`, `node_modules`, `dist`, `.git`, binaries)
- Binary skip during packing
- Token pre-calculation present on pack output (FR-002)
- Chunk sizing approximates ~500 tokens (FR-023) — tolerance **Proposed** unless BRD states exact
- Embedder produces 384-dim vectors; mock model optional for speed
- Consent gate: deny external provider call when consent absent; allow path when present (behavioral)
- Index path never invokes external LLM client (mock assert zero calls)

### Integration Tests

- `POST /index` against real or testcontainer Qdrant: upserts into `codebase`; response fields present; `graph_nodes` may be 0
- End-to-end pack → chunk → embed → Qdrant payload includes `repo_name` + `file_path`
- Docker Compose smoke: API reachable + Qdrant healthy (health endpoint ownership EP-005; may use minimal dependency check **Proposed**)

### End-to-End Tests

- Extension activation triggers backend `POST /index` (mock server acceptable)
- File save triggers incremental re-index call (assert client invokes orchestrator; OQ-14 shape marked provisional)
- Progress/cancellation UX cancels in-flight request

### Acceptance Tests (map to SC / NFRs)

| Claim | Test | Must not invent |
|-------|------|-----------------|
| SC-001 pack + tokens + binary skip | Fixture repo pack inspection | Pack field invention |
| SC-002 response fields | Contract assert on `POST /index` | Extra response fields |
| SC-003 local 384-dim + zero exfil | Dimensionality + network/LLM mock | Hosted embed APIs |
| SC-004 exclusions | Forbidden paths absent from pack and Qdrant | — |
| SC-005 <15 min / 1M LOC | Perf harness when corpus available | Search p95 |
| SC-006 <60s / 100-file delta | Perf harness | — |
| SC-007 auto-index on activate | Extension E2E / integration | Manual ceremony requirement |
| SC-008 save delta + illustrative timings | Trigger test + optional timing observe | Stricter global SLAs |
| SC-009 consent deny + index no-exfil | Security tests | Consent UX pass criteria (SC-010) |

### Regression Tests

- Re-run exclusion + no-exfil tests on every change to walker/embedder/index router
- OpenAPI contract snapshot for confirmed `POST /index` fields

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OQ-14 unresolved at task freeze | US-012 API drift / rework | Plan marks Proposed reuse; discovery task before contract freeze; no invented endpoints |
| CPU embedding too slow for NFR-001 on large repos | Miss <15 min / 1M LOC | Batch encode; measure early; document gap per constitution IV if unmet |
| Accidental secret indexing via incomplete ignore | Security incident | Central security module; fixture tests; never trust client filters |
| Extension bypasses policy by packing locally | Constitution V violation | Extension only calls API; code review gate |
| Model weights missing (~90MB) | Index failures | Document model download in deploy; fail clearly |
| Concurrent overlapping indexes | Corrupt/partial Qdrant state | Proposed single-flight / 409; **Not evidenced** as confirmed |
| Index drift if save trigger fails | Stale corpus for EP-002 | Retry/backoff **Proposed**; staleness badge is V1/EP-005 adjacent |
| Consent UX unclear | Partial US-016 delivery | Ship deny-by-default gate; defer UX to clarification |
| Pack schema churn (OQ-PACK) | Downstream EP-002 breakage | Keep minimal FR-01 behavior; freeze fields only after clarification |

---

## Dependencies

### Internal Dependencies

- Approved `spec.md` (this feature)
- Architecture: ADR-002, ADR-003, ADR-008, ADR-009, ADR-011, ADR-012, ADR-013; api-contract; database-schema; implementation-guidelines
- Downstream consumers EP-002 (not blocking EP-001 acceptance)
- Adjacent EP-005 for full privacy epic / health — EP-001 applies indexing constraints only

### External Services

- None required for indexing (local embeddings). Query-time external LLM is BYO and consent-gated (out of index path).

### Third-party Libraries (Confirmed direction / Proposed pins)

| Library / tech | Status |
|----------------|--------|
| FastAPI, Python 3.11 | Confirmed |
| sentence-transformers / all-MiniLM-L6-v2 | Confirmed |
| Qdrant client / server | Confirmed |
| Repomix-style packer | Style Confirmed; concrete package **NEEDS CLARIFICATION** |
| OpenTelemetry SDK | Confirmed compatible; exporter **NEEDS CLARIFICATION** |
| VS Code Extension API | Confirmed surface |

### Infrastructure Dependencies

- Docker Compose with Qdrant (ADR-013)
- Local disk for repos + model weights
- VS Code extension host for US-011/US-012

---

## Implementation Phases

### Phase 0 — Setup / Foundation

- Scaffold **Proposed** `services/orchestrator` and `clients/vscode` (source absent today)
- Docker Compose: Qdrant + API skeleton
- Security ignore/exclusion module (shared by all later stories)
- Telemetry bootstrap (OTel-compatible no-op exporter acceptable until vendor clarified)
- OpenAPI stub for confirmed `POST /index`

### Phase 1 — User Story 1 (P1) — Repo Flattening & Packing (US-001)

- Implement walker + packer + token pre-calc + binary skip
- Persist/expose pack for downstream (FR-004) without inventing schema fields
- Wire into `POST /index` at least through pack stage
- Tests: SC-001, SC-004 (pack side)

### Phase 2 — User Story 2 (P1) — Local Embedding Index (US-002)

- Chunk ~500 tokens; local embed; Qdrant upsert
- Complete `POST /index` response fields; `graph_nodes=0`
- Enforce no external LLM on index path
- Tests: SC-002, SC-003, SC-004 (embed side); start SC-005 harness

### Phase 3 — User Story 3 (P2) — Auto-Index on Install (US-011)

- Extension activate → `POST /index`
- Progress/cancellation UX
- Policy remains backend-owned (FR-014)
- Tests: SC-007; observational SC-008 ~200-file timing where hardware permits

### Phase 4 — User Story 4 (P2) — Incremental Re-Index on Save (US-012)

- Save listener → incremental trigger
- **Discovery / clarification gate for OQ-14** before locking request shape
- Delta performance toward SC-006 / NFR-002; illustrative single-file timing
- Tests: SC-006, SC-008 trigger behavior

### Phase 5 — User Story 5 (P2) — Query-Time Consent Gate (US-016)

- Orchestrator consent check deny-by-default for external LLM
- Document local Ollama path as allowed non-exfil option when configured
- Index path regression: still no exfil with or without consent
- Consent UX/storage: **blocked on OQ-US016** for detail; behavioral gate ships
- Tests: SC-009; SC-010 limited to deny-by-default (no invented UI criteria)

### Phase 6 — Polish / Cross-cutting

- Perf validation NFR-001/002
- OTel attributes aligned to response counts
- Contract tests; documentation of open questions remaining
- No EP-002 search / EP-003 Serena / L1 graph population

---

## Evidence Reviewed

| Artifact | Path / ID |
|----------|-----------|
| Feature spec | `specs/ep-001-l5-repository-packing-indexing/spec.md` |
| Constitution | `.specify/memory/constitution.md` v1.0.0 |
| Plan template | `.specify/templates/plan-template.md` |
| Architecture overview | `docs/architecture/architecture-overview.md` |
| API contract | `docs/architecture/api-contract.md` (§2.2 `POST /index`) |
| ADRs | ADR-001, ADR-002, ADR-003, ADR-008, ADR-009, ADR-011, ADR-012, ADR-013 (and related boundary ADRs) |
| Tech stack | `docs/architecture/tech-stack.md` |
| Database schema | `docs/architecture/database-schema.md` |
| Implementation guidelines | `docs/architecture/implementation-guidelines.md` |
| Backlog | `docs/backlog/user-stories.md` (EP-001; US-001, US-002, US-011, US-012, US-016) |
| PM handoff | `.cursor/agent-handoffs/handoff.md` (product-manager → plan-generator) |
| Source code | **Not present** in repository (structure Proposed) |

---

## Planning Assumptions

| ID | Assumption | Label |
|----|------------|-------|
| A-01 | Git is SoT; monorepo ≤1M LOC for MVP SLA applicability | Spec / BRD §13 |
| A-03 | LLM ~128k context; compression V1 — relevant to US-016 narrative only | Spec |
| A-04 | Qdrant available locally/VPC via Docker Compose | Spec / ADR-013 |
| A-08 | Pinecone not default vector store | Spec / ADR-008 |
| A-EP001-1 | Pack/embeddings from EP-001 consumable by EP-002 without shipping search here | Spec |
| A-EP001-2 | Extension can reach FastAPI in MVP topology | Spec |
| A-PLAN-1 | Local/dev API auth = trusted loopback until authn specified | api-contract §1 Assumption |
| A-PLAN-2 | Proposed monorepo layout from implementation-guidelines will be used unless ADR changes it | Proposed |
| A-PLAN-3 | Until OQ-14 resolves, incremental indexing will attempt Proposed reuse of `POST /index` | Proposed |
| A-PLAN-4 | pytest will be the orchestrator test runner | Proposed (common for FastAPI; not BRD-mandated) |

---

## Open Questions

| ID | Question | Blocking? | Impact |
|----|----------|-----------|--------|
| OQ-14 | Incremental delta index API beyond confirmed `POST /index` | **Blocking for US-012 API contract freeze**; non-blocking for plan draft | FR-017; Phase 4 |
| OQ-US016 | Consent UX and storage mechanism | **Blocking for consent UX implementation detail**; non-blocking for deny-by-default | FR-021; Phase 5 |
| OQ-PACK | Exact pack schema fields beyond FR-01 XML + token pre-calc | **Blocking for pack contract freeze** | FR-022; EP-002 handoff |
| OQ-OVERRIDE | Explicit approved override UX for excluded secrets/paths | Non-blocking while defaults exclude-all | FR-012 |
| OQ-01 | Exact RBAC roles/path/authn schema | Non-blocking for POC indexing defaults; blocking for path-RBAC detail | Security |
| OQ-HTTP | Confirmed HTTP status codes for `POST /index` | Non-blocking for functional draft | API errors |
| OQ-OTEL | OTel exporter vendor / backend | Non-blocking if compatible SDK used | Observability |
| OQ-PACKER | Concrete Repomix package vs in-house adapter | Non-blocking if behavior matches FR-01 | Phase 1 |
| OQ-CANCEL | Server-side index cancellation semantics | Non-blocking; client cancel Proposed | FR-015 |

---

## Requirement Coverage Matrix

| Requirement ID | Planned Implementation | Evidence | Status |
| -------------- | ---------------------- | -------- | ------ |
| FR-001 | L5 pack service XML-oriented flatten | Spec; FR-01; Phase 1 | Covered |
| FR-002 | Token pre-calc in packer | Spec; Phase 1 | Covered |
| FR-003 | Binary skip in walker/packer | Spec; Phase 1 | Covered |
| FR-004 | Persist/expose pack for EP-002 consumers | Spec; OQ-PACK limits field freeze | Covered (behavioral); schema open |
| FR-005 | `POST /index` `{repo_path, repo_name}` | api-contract §2.2 | Covered |
| FR-006 | Response `files_indexed`, `embeddings`, `time_ms`, `graph_nodes` | api-contract §2.2 | Covered |
| FR-007 | Local all-MiniLM-L6-v2 384-dim CPU | ADR-003; Phase 2 | Covered |
| FR-008 | Qdrant `codebase` collection | ADR-003; database-schema §2 | Covered |
| FR-009 | No external LLM on index path | ADR-003; security tests | Covered |
| FR-010 | `.gitignore` respected | ADR-012; security module | Covered |
| FR-011 | Exclude `.env`/secrets/build/deps/`.git`/binaries | ADR-012; FR-01 | Covered |
| FR-012 | No override until clarified; defaults force | OQ-OVERRIDE | Covered (default-only) |
| FR-013 | Extension auto-index on install/activation | US-011; Phase 3 | Covered |
| FR-014 | Backend orchestration; no client policy bypass | ADR-002; constitution V | Covered |
| FR-015 | Extension progress/cancellation UX | constitution V; Phase 3 | Covered |
| FR-016 | Save triggers incremental re-index | US-012; Phase 4 | Covered |
| FR-017 | No invented endpoints; OQ-14 Proposed reuse | ADR-009; OQ-14 | Covered (Proposed path) |
| FR-018 | Deny external LLM without consent | US-016; Phase 5 | Covered |
| FR-019 | Consented path = allowed packed/compressed context only | Appendix C; Phase 5 | Covered (behavioral) |
| FR-020 | Local Ollama option without external exfil | Appendix C; Phase 5 | Covered (config path) |
| FR-021 | Deny-by-default until UX clarified | OQ-US016 | Covered (gate only) |
| FR-022 | Do not invent pack fields | OQ-PACK | Covered |
| FR-023 | ~500-token chunks | Appendix C; Phase 2 | Covered |
| NFR-001 | Perf harness <15 min / 1M LOC | BRD §10; Phase 6 | Covered |
| NFR-002 | Delta <60s / 100 files | BRD §10; Phase 4 | Covered |
| NFR-003 | ~0.5s single-file illustrative | BRD §14; observational | Covered |
| NFR-004 | ~10s / 200 files illustrative | BRD §14; observational | Covered |
| NFR-005 | Local embeddings; no index exfil | ADR-003 | Covered |
| NFR-006 | Ignore/exclusion in orchestrator | ADR-012 | Covered |
| NFR-007 | Query-time deny-by-default | US-016 | Covered |
| SC-001..010 | Mapped in Testing Strategy | Spec Success Criteria | Covered |

---

## Planning Gate Summary

| Planning Gate criterion | Met? |
|-------------------------|------|
| Technical context evidence-based or Proposed/NEEDS CLARIFICATION | Yes |
| Layers, APIs, stores, extension, telemetry identified | Yes |
| Security, privacy, performance, reliability documented | Yes |
| Testing covers measurable indexing claims | Yes |
| Architecture deviations justified | Yes (none unjustified) |

**Planning Gate**: **Yes** — ready for Task Generator with open questions carried (do not invent OQ resolutions in tasks).
