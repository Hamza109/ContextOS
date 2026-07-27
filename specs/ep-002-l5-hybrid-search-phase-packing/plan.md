# Implementation Plan: EP-002 L5 Hybrid Search & Phase-Aware Packing

**Branch**: `feature/ep-002-l5-hybrid-search-phase-packing` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/ep-002-l5-hybrid-search-phase-packing/spec.md`

**Stories**: US-003, US-004, US-015 only

---

## Summary

EP-002 delivers MVP L5 **query-time** intelligence: **hybrid BM25 + vector search with MMR re-ranking** over EP-001 packs/Qdrant index, **phase-scoped prompt/pack assembly** (Requirements / Design / Dev / Test / Deploy), and **provenance citations** (file:line + confidence) inside packed `final_context`. The **FastAPI orchestrator** owns search and packing via confirmed **`POST /context`**. Clients (CLI ask / extension Ask) may consume the same API later; full CLI (EP-004) and extension DX are **out of scope**. Full L4 Headroom product behavior is **not** an MVP gate (ADR-006). Upstream indexing remains EP-001 — this plan **consumes** packs/index and does **not** re-plan the indexing epic.

**Technical approach (Confirmed stack + Proposed gaps labeled):** FastAPI + Python 3.11 → embed query locally (`all-MiniLM-L6-v2`) → hybrid retrieve (vector from Qdrant `codebase` + BM25 over packs — BM25 store **Missing Evidence**) → MMR re-rank → phase-scoped template assembly → cite file:line + confidence → return Confirmed `POST /context` response fields. OpenTelemetry-compatible spans for `/context` latency (exporter vendor open per ADR-011).

---

## Technical Context

**Language/Version**: Python 3.11 (orchestrator — Confirmed constitution / BRD §14). Client TypeScript surfaces not primary deliverables for this epic.

**Primary Dependencies**:
| Dependency | Status | Evidence |
|------------|--------|----------|
| FastAPI | Confirmed | constitution; tech-stack |
| `sentence-transformers/all-MiniLM-L6-v2` (query embedding, 384-dim) | Confirmed | ADR-003; EP-001 reuse |
| Qdrant client (`codebase` collection) | Confirmed | ADR-008; database-schema §2; EP-001 |
| Hybrid BM25 + vector + MMR (grepai/claude-context **patterns**) | Confirmed behavior | FR-02; ADR-014; tech-stack |
| Concrete BM25 library / store product | **Missing Evidence** — **Proposed** options under OQ-BM25-store | ADR-014; database-schema §2 |
| code2prompt-**style** phase templates | Confirmed style; concrete package pin **NEEDS CLARIFICATION** | FR-03; tech-stack |
| OpenTelemetry-compatible SDK | Confirmed compatibility; exporter vendor **NEEDS CLARIFICATION** | ADR-011 |

**Storage**:
| Store | Role in EP-002 | Status |
|-------|----------------|--------|
| Qdrant `codebase` (384-dim HNSW) | Vector half of hybrid search; filter by `repo_name` | Confirmed consume (EP-001 writes) |
| EP-001 pack artifacts (`CONTEXTOS_PACK_CACHE_DIR` / orchestrator pack cache) | Pack text / BM25 corpus input; packing composition | **Proposed** handoff (OQ-PACK — do not Confirmed-freeze field inventory) |
| FalkorDB | N/A for EP-002 delivery | V1 / L1 |
| BM25 index location | Sidecar vs Qdrant payload vs in-memory over packs | **Missing Evidence** (OQ-BM25-store) |

**Testing**: **Proposed** pytest (unit / integration / contract) aligned to existing `services/orchestrator/tests/` layout from EP-001. Performance harness for p95 @ 500k LOC and recall@10 harness **availability/design** remain `[NEEDS CLARIFICATION: OQ-recall-harness]` — do not invent pass results.

**Target Platform**: Local/VPC Docker Compose POC (API + Qdrant — ADR-013); loopback trusted API may apply until authn clarified (A-05).

**Project Type**: FastAPI orchestrator service feature (L5 search/packing). CLI/extension are consumers only (not DX deliverables here).

**Performance Goals** (this feature):
- Semantic search p95 <800ms for a 500k LOC index (BRD §10; NFR-001; ADR-014) — **Confirmed target**
- recall@10 >0.92 where evaluation harness applies (BRD §12) — **Confirmed claim**; harness gap open
- IDE symbol-accurate <2s / demo <8s / BO-04 <5s — **not** claimed as EP-002-only Confirmed SLAs (spec NFR-002/NFR-003)

**Constraints**:
- Evidence-first: no invented Confirmed APIs, citation JSON, phase wire fields, status-code freezes, or pack schema fields (constitution I)
- FastAPI owns search/packing; clients MUST NOT bypass validation/policy (constitution V; ADR-002)
- Consume EP-001 ignore/exclusion boundaries; no re-index of excluded content; no index-path exfil assumption (constitution III; FR-018)
- Full L4 product out of MVP gate (ADR-006; FR-014)
- Pinecone not default (ADR-008)
- Appendix D surface only for Confirmed HTTP — no new Confirmed endpoints (ADR-009)

**Scale/Scope**: NFR reference 500k LOC index; MVP monorepo ≤1M LOC (A-01); stories US-003, US-004, US-015 only

---

## ContextOS Technical Impact

**Affected Layers**:

| Layer | Impact | Evidence |
|-------|--------|----------|
| L1 | N/A as deliverable — `blast_radius` MAY be empty/null (**Proposed** MVP) | Spec; api-contract §2.3; V1 |
| L2 | N/A | V2 |
| L3 | N/A as deliverable — Serena/EP-003 | Spec Out of Scope |
| L4 | N/A as product deliverable — basic packing only; no Headroom gate (ADR-006) | FR-014; ADR-006 |
| **L5** | **Primary** — hybrid BM25+vector+MMR, phase-aware assembly, citations | Spec; ADR-014; FR-02/03; §14 Pack & Cite |
| L6 | N/A — `memory` MAY be empty/null (**Proposed**) | Spec; V2 |

**Affected Surfaces**:

| Surface | Impact |
|---------|--------|
| FastAPI / API | **Affected** — owns `POST /context`, search, packing, policy |
| CLI | **Consumer note only** — `contextos ask` MAY call `POST /context` (api-contract §6); EP-004 out of scope |
| VS Code extension | **Out of scope as primary** — may call API later; DX stories not included |
| Dashboard / Webview / viz | N/A for EP-002 primary acceptance |
| GitHub Action | N/A |
| Background indexer | N/A as EP-002 deliverable — indexing remains EP-001; search **reads** index |
| Telemetry | **Affected** — OTel-compatible `/context` latency / search spans (ADR-011) |

**Data Stores / Services**: Qdrant `codebase` (read); EP-001 pack cache (read — Proposed shape); local query embedder; BM25 capability (**placement open**); ignore/consent security modules (reuse EP-001)

**Privacy / Security Controls**: Inherit EP-001 `.gitignore` / `.env` / secrets / binary / build / deps exclusions already applied to packs and embeddings; no assumption of index-time code exfil; search/packing retrieves local index/packs via FastAPI only; source provenance via citations (file:line + confidence); RBAC schema **NEEDS CLARIFICATION** (OQ-01) — do not invent; PII redaction N/A as primary (L2/L6); query-time external LLM consent owned by US-016 — clients MUST NOT bypass orchestrator if a later path would exfiltrate packed context

**Observability**: Instrument `POST /context` latency; **Proposed** spans for vector retrieve, BM25 retrieve, MMR, pack assemble (implementation-guidelines §7). Exact metric names and exporter backend **Missing Evidence** (ADR-011). Compression dashboard is V1/L4 — out of scope.

**Measurable Intelligence Claims** (this feature):
- Hybrid search returns ranked files with scores (SC-001)
- Search p95 <800ms @ 500k LOC (SC-002)
- recall@10 >0.92 where harness applies (SC-003) — harness gap documented
- Phase composition differs (SC-004)
- Citations file:line + confidence present (SC-005)
- Confirmed response field presence (SC-006)

---

## Constitution Check

*GATE: Planning Gate — evaluate before and after design.*

| Gate item | Status | Evidence / mitigation |
|-----------|--------|------------------------|
| Technical context evidence-based or marked Proposed / NEEDS CLARIFICATION | **Pass** | Technical Context; OQs carried |
| Affected layers, APIs, stores, surfaces, telemetry identified | **Pass** | ContextOS Technical Impact; Components; API Design |
| Security, privacy, performance, reliability documented | **Pass** | Security / Performance / Reliability sections |
| Testing covers measurable claims | **Pass** | Testing Strategy — p95 and recall@10 planned with harness gaps labeled; no invented pass results |
| Architecture deviations justified | **Pass** | None vs ADR-001..014 for EP-002 scope; Proposed extensions labeled |
| Evidence-first (constitution I) | **Pass** | No Confirmed freeze of OQ-11/16/PACK/top_k/MVP-metrics/HTTP/BM25 |
| Six-layer integrity (II) | **Pass** | L5 primary; L1/L3/L4/L2/L6 explicit N/A or deferred |
| Privacy/local-first (III) | **Pass** | FR-018; provenance FR-015; OQ-01 not invented |
| Measurable claims (IV) | **Pass** | SC-001..008; harness gap marked |
| Boundary discipline (V) | **Pass** | FastAPI owns search/packing; CLI/extension consumer-only |
| Roadmap order | **Pass** | MVP L5 search + basic phase packing; L4 not pulled forward as gate |

**Applicable governance rule IDs**: Constitution I–V; Approved Technical Direction; Planning Gate; ADR-001, ADR-002, ADR-006, ADR-008, ADR-009, ADR-011, ADR-012, ADR-013, ADR-014

**Required mitigations**:
- Carry OQ-16, OQ-11, OQ-PACK, OQ-top_k, OQ-MVP-metrics, OQ-recall-harness, OQ-BM25-store, OQ-HTTP-/context, OQ-01 without inventing Confirmed resolutions
- Until OQ-PACK resolves: consume EP-001 **Proposed** pack handoff (`PackResult` / cache keyed by `repo_name`) without freezing Confirmed pack schema fields
- Until OQ-16 resolves: support five named phases as product concepts; phase selection mechanism labeled **Proposed** only (not Confirmed request field)
- Until OQ-11 resolves: require file:line + confidence attributes in packed context; do not invent Confirmed citation JSON field names
- Until OQ-BM25-store resolves: implement hybrid **behavior**; choose one **Proposed** placement option explicitly in tasks without claiming Confirmed store product
- Until recall harness exists: implement search quality tests as **blocked/skipped** for SC-003 pass claims; document gap

### Constitution Check (re-check after design)

| Item | Post-design status |
|------|-------------------|
| Planning Gate | **Met** — ready for Task Generator with open questions carried |
| Deviations | None unjustified |
| Blocking for plan draft | **None** if OQs remain labeled |
| Blocking for Confirmed contract freezes | OQ-11 (citation schema), OQ-16 (phase wire), OQ-PACK (pack schema), OQ-top_k (bounds), OQ-MVP-metrics, OQ-HTTP-/context |
| Blocking for verification pass claims | OQ-recall-harness (SC-003); 500k LOC perf fixture availability for SC-002 |

---

## Project Structure

### Documentation (this feature)

```text
specs/ep-002-l5-hybrid-search-phase-packing/
├── spec.md              # Approved Spec Gate
├── plan.md              # This file
├── research.md          # Optional Phase 0 — not required for this plan drop
├── data-model.md        # Optional Phase 1 — logical model covered herein
├── quickstart.md        # Optional Phase 1
├── contracts/           # Optional OpenAPI excerpt — sync with orchestrator later
└── tasks.md             # NOT created by plan-generator
```

### Source Code (repository root)

**Confirmed present** (inspected 2026-07-27): EP-001 orchestrator foundation under `services/orchestrator/`. EP-002 extends this tree — does not invent a parallel service.

```text
ContextOS/
├── docs/
│   ├── architecture/
│   ├── backlog/user-stories.md
│   └── BRD_Context_OS.md
├── services/
│   └── orchestrator/                      # FastAPI + Python (EP-001 present)
│       ├── app/
│       │   ├── api/
│       │   │   ├── index.py               # EP-001 POST /index (reuse)
│       │   │   ├── health.py
│       │   │   ├── schemas_index.py
│       │   │   ├── context.py             # Proposed NEW — POST /context router
│       │   │   └── schemas_context.py     # Proposed NEW — request/response models
│       │   ├── services/
│       │   │   ├── l5_pack.py             # EP-001 — consume pack cache
│       │   │   ├── l5_chunk.py            # EP-001
│       │   │   ├── l5_index.py            # EP-001
│       │   │   ├── l5_search.py           # Proposed NEW — hybrid + MMR
│       │   │   ├── l5_phase_pack.py       # Proposed NEW — phase templates
│       │   │   └── l5_citations.py        # Proposed NEW — provenance attributes
│       │   ├── adapters/
│       │   │   ├── qdrant_store.py        # EP-001 — extend with search/query (Proposed)
│       │   │   ├── embeddings.py          # EP-001 — reuse for query vectors
│       │   │   ├── fs_walker.py
│       │   │   └── bm25_store.py          # Proposed NEW — placement per OQ-BM25-store
│       │   ├── security/                  # reuse ignore_policy, consent_gate
│       │   ├── telemetry/
│       │   │   ├── indexing.py            # EP-001
│       │   │   └── context.py             # Proposed NEW — /context spans
│       │   ├── config.py
│       │   └── main.py                    # register context router
│       └── tests/
│           ├── unit/
│           ├── integration/
│           └── contract/
├── clients/                               # CLI/extension — out of scope for EP-002 DX
├── deploy/
│   └── docker-compose.yml                 # Qdrant + API (reuse)
└── specs/
    ├── ep-001-l5-repository-packing-indexing/
    └── ep-002-l5-hybrid-search-phase-packing/
```

**Structure Decision**: Extend existing `services/orchestrator` (Confirmed present from EP-001). Package names `l5_search`, `l5_phase_pack`, `l5_citations`, `api/context` are **Proposed** per implementation-guidelines §1–2. Do not duplicate orchestration in `clients/`.

---

## Complexity Tracking

> No constitution violations requiring justification. BM25 placement and phase/citation wire shapes remain open by design (Missing Evidence), not complexity escapes.

| Item | Notes |
|------|-------|
| Avoidable complexity | None introduced — hybrid + MMR is Confirmed ADR-014 |
| Dual retrieval paths | Required by FR-02 / ADR-014; tune under NFR-001 |

---

## Technical Approach

### Confirmed architecture

1. **Orchestrator ownership**: FastAPI owns hybrid search, phase packing, citations, OpenAPI for `POST /context` (ADR-002; constitution V; FR-009).
2. **Hybrid retrieval**: BM25 + vector over flattened/packed content with **MMR** re-ranking; p95 <800ms @ 500k LOC (ADR-014; FR-001, FR-002, FR-007).
3. **Vector path**: Query embedded with local `all-MiniLM-L6-v2` (384-dim); search Qdrant collection `codebase` filtered by `repo` / `repo_name` (EP-001; database-schema §2; ADR-008).
4. **API contract**: Confirmed request fields `query`, `file` (optional), `repo`, `top_k`; Confirmed response fields `final_context`, `metrics` (`tokens_before`, `tokens_after`, `saving_percent`, `trace`), `blast_radius`, `memory`, `relevant_files`, `is_real` (api-contract §2.3; FR-003, FR-004).
5. **MVP field meaning**: `final_context`, `relevant_files`, `is_real` meaningful; `blast_radius` / `memory` MAY be empty/null (**Proposed**) (FR-005).
6. **Phase concepts**: Five SDLC phases Requirements / Design / Dev / Test / Deploy with code2prompt-**style** templates (FR-011; BRD FR-03; §8 mapping informs intent but MVP does not require L1/L2/L6 layers active).
7. **Citations**: Packed context includes file:line and confidence (BRD §14 Pack & Cite; FR-015; constitution III).
8. **L4 deferral**: No full Headroom / FR-11 budgets / compression dashboard as EP-002 gate (ADR-006; FR-014).
9. **Privacy inheritance**: Operate only over EP-001-permitted content; no index-time exfil assumption (FR-018; ADR-012).
10. **Observability**: OTel-compatible instrumentation; exporter vendor open (ADR-011).
11. **Deploy**: Docker Compose local/VPC-friendly with Qdrant (ADR-013).

### Proposed architecture (implementability — not Confirmed freeze)

1. **Internal modules**: `api/context`, `services/l5_search`, `services/l5_phase_pack`, `services/l5_citations`, `adapters/bm25_store`, `telemetry/context` — names Proposed.
2. **Pipeline** (Proposed orchestration order):
   ```
   POST /context
     → validate query/repo/top_k (positive integer; bounds OQ-top_k)
     → resolve pack + index for repo (EP-001 artifacts)
     → embed query (local MiniLM)
     → parallel/sequential: vector search (Qdrant) + BM25 over pack/chunks
     → fuse scores → MMR diversify/re-rank → top_k relevant_files with scores
     → select phase template (OQ-16 mechanism Proposed)
     → assemble final_context (phase-scoped) + citations (file:line + confidence)
     → populate metrics (MVP packing token counts per A-06 / OQ-MVP-metrics)
     → return Confirmed response shape (blast_radius/memory empty/null Proposed)
   ```
3. **BM25 placement options** (choose one in implementation tasks; label **Proposed**; OQ-BM25-store remains open):
   | Option | Description | Trade-off |
   |--------|-------------|-----------|
   | **A** | In-process BM25 over EP-001 pack XML / chunk texts loaded for `repo` | Simple POC; may pressure p95 at 500k LOC |
   | **B** | Persist BM25 sidecar index at index time (EP-001 write path extension) | Better latency; **crosses into EP-001** — prefer read-time build or deferred write unless EP-001 change approved |
   | **C** | Store searchable text in Qdrant payload + use Qdrant sparse/hybrid if available | Couples to Qdrant capabilities — **Missing Evidence** whether sparse/BM25 in approved Qdrant usage is Confirmed |

   **Recommendation (Proposed, not Confirmed)**: Start with **Option A** for MVP behavioral delivery; measure against NFR-001; escalate to B/C only if p95 fails with evidence. Do not claim any option Confirmed.
4. **Phase selection (OQ-16 — Proposed only)**: Until product confirms wire shape, **Proposed** non-Confirmed mechanisms (pick one in tasks without freezing contract):
   - Optional **Proposed** request field (e.g. `phase`) **not** in Appendix D Confirmed set — must remain labeled Proposed in OpenAPI descriptions; **OR**
   - Config/default phase (e.g. Dev) when absent; **OR**
   - Derive from query heuristics — **weaker**; avoid inventing as Confirmed product behavior

   Confirmed request remains `query`/`file`/`repo`/`top_k` only until OQ-16 resolves.
5. **Citation representation (OQ-11 — Proposed only)**: Ensure packed `final_context` string (and/or structured side-channel if later confirmed) includes **file path, line reference, and confidence**. Exact JSON schema inside `final_context` **not invented**. **Proposed** interim: XML/attributes or clearly delimited citation blocks inside the packed string satisfying BRD §14 attributes without claiming Confirmed field names.
6. **Pack consumption (OQ-PACK)**: Load EP-001 `PackResult` / cache under `pack_cache_dir` keyed by `repo_name` (Proposed persistence from EP-001). Treat `xml_content`, `token_count`, `artifact_path` as **Proposed** handoff fields evidenced in current `l5_pack.py` — **not** a Confirmed frozen schema.
7. **Score fusion**: Exact BM25/vector fusion weights **Not evidenced** — **Proposed** tunable weights with defaults documented as Proposed; must still produce ranked `relevant_files` with scores (FR-006).
8. **Degraded search**: On partial index, prefer reduced results over hard-fail-all discovery when possible (BRD §10); operator UX owned by US-014/EP-005 — do not invent health UI here (NFR-007).
9. **HTTP status codes**: Use api-contract **Proposed** labels (`200`, `400`, `403`, `404`, `503`, …) only as Proposed — not Confirmed freeze (FR-020; OQ-HTTP-/context).

### Missing evidence (do not invent)

- BM25 storage product/placement (OQ-BM25-store)
- Phase parameter Confirmed wire shape (OQ-16)
- Citation JSON schema (OQ-11)
- Pack schema Confirmed field inventory (OQ-PACK)
- `top_k` min/max/default beyond positive integer (OQ-top_k); FR-02 “top 8” is illustrative
- MVP `metrics` compression semantics (OQ-MVP-metrics; A-06)
- recall@10 evaluation harness/dataset (OQ-recall-harness)
- Confirmed HTTP status codes for `/context` (OQ-HTTP-/context)
- Authn / RBAC schema (OQ-01; api-contract)
- Exact MMR λ / fusion weights
- OTel exporter vendor (ADR-011)

---

## Architecture Impact

| Area | Impact | Evidence |
|------|--------|----------|
| **Frontend** | N/A as EP-002 deliverable — extension DX out of scope; may call API later | Spec Out of Scope; PM scope |
| **Backend** | New/updated FastAPI `POST /context` pipeline: hybrid search → MMR → phase pack → citations | ADR-002; api-contract §2.3; FR-003..016 |
| **Database / stores** | **Read** Qdrant `codebase`; **read** EP-001 pack cache; **Proposed** BM25 corpus/index (no FalkorDB writes) | database-schema §2; OQ-BM25-store; EP-001 |
| **Infrastructure** | Reuse Docker Compose API + Qdrant; no new Confirmed infra product | ADR-013 |
| **AI Components** | Local MiniLM query embeddings; no index-time LLM; query-time external LLM not EP-002 deliverable (US-016) | ADR-003; FR-018 |
| **CLI / Extension** | Consumer notes only — not DX implementation in this epic | FR-019 |

---

## Components

| Component | Action | Responsibility |
|-----------|--------|----------------|
| `POST /context` router | Create | Validate Confirmed request; orchestrate search/pack; return Confirmed response |
| Context request/response schemas | Create | Pydantic models matching api-contract §2.3 Confirmed fields; Proposed extensions labeled |
| L5 hybrid search service | Create | BM25 + vector retrieve; score fusion; MMR; `relevant_files` with scores |
| Qdrant adapter search API | Modify | Add filtered vector query by `repo_name` (and optional `file` bias — Proposed) |
| Embeddings adapter | Reuse | Encode query to 384-dim vector |
| BM25 adapter/store | Create (**Proposed** placement) | Keyword retrieval over pack/chunk text |
| Phase pack service | Create | code2prompt-style templates for 5 phases; composition differs by phase |
| Citation / provenance helper | Create | Attach file:line + confidence into packed context (schema open) |
| Pack loader | Reuse/extend | Load EP-001 pack artifact by `repo_name` without freezing OQ-PACK |
| Ignore / consent security | Reuse | Do not re-pack excluded paths from disk bypassing index; honor consent gate on any future external send |
| Context telemetry | Create | OTel-compatible `/context` latency spans |
| OpenAPI / main registration | Modify | Mount context router |
| CLI / VS Code | N/A (out of scope DX) | Documented as future consumers of same API |
| Evaluation harness (recall@10) | Discovery / Proposed | Create only if product supplies dataset; else document blocked verification |

**Repositories**: Qdrant as vector repository (read); pack cache as artifact repository (read — Proposed); BM25 as Proposed keyword repository.

**Validators / Middleware**: Request validation for `query`/`repo`/`top_k` (positive integer); Proposed status mapping; RBAC hook points reserved but schema not invented (OQ-01).

**Background Jobs**: None required for EP-002 query path. Index freshness remains EP-001 responsibility.

**Configuration**: Reuse Qdrant URL, pack cache dir, embedding model settings; **Proposed** knobs for MMR λ, fusion weights, default phase — keys not Confirmed.

**Shared modules**: EP-001 `l5_pack`, `embeddings`, `qdrant_store`, `ignore_policy`, `consent_gate`, `config`.

---

## Data Model Changes

### New / logical entities (this feature)

| Entity | Fields / notes | Status |
|--------|----------------|--------|
| Context Request | `query`, `file?`, `repo`, `top_k` | Confirmed (api-contract) |
| Phase selection | One of Requirements/Design/Dev/Test/Deploy | Confirmed concept; wire **OQ-16** |
| Hybrid Search Hit | file path, score(s), optional chunk refs | Proposed structure for `relevant_files` elements — exact item schema **Not evidenced** beyond “files with scores” |
| Phase-Scoped Pack | Assembled string → `final_context` | Confirmed response field; internal template inventory Proposed |
| Citation / Provenance | file:line + confidence inside packed context | Confirmed attributes (BRD §14); JSON shape **OQ-11** |
| Context Metrics | `tokens_before`, `tokens_after`, `saving_percent`, `trace` | Confirmed fields; MVP meaning **OQ-MVP-metrics** |
| Upstream Pack / Index | EP-001 pack + Qdrant points | Consume; pack inventory **OQ-PACK** |

### Modified entities

| Entity | Change | Status |
|--------|--------|--------|
| Qdrant points | No required schema change for EP-002 if payload already has `repo_name`, `file_path`, content | Confirmed concepts from EP-001 / database-schema; payload index on `repo_name` **Proposed** for filtered search |
| Pack cache | Read path only; no Confirmed new fields | OQ-PACK |

### Relationships

- `Context Request` → many `Hybrid Search Hit` → assembled into `Phase-Scoped Pack` with `Citation`s
- Join key: `repo` / `repo_name` (+ `file_path`)

### Validation rules

- `query`: non-empty string (Proposed `400` if invalid — not Confirmed status freeze)
- `repo`: required; unknown/not indexed → Proposed `404`
- `top_k`: positive integer (Confirmed validation note); min/max/default **OQ-top_k**
- Phase: if Proposed field used, reject unsupported values without inventing Confirmed enum wire name

### Migration requirements

- None for FalkorDB.
- Qdrant: ensure collection exists (EP-001); **Proposed** payload index on `repo_name` if missing for latency.
- BM25: if Option B chosen, may require EP-001 write-path change — treat as cross-epic dependency; prefer Option A first.

---

## API Design

### Confirmed endpoint (primary)

**`POST /context`** — api-contract §2.3

**Request (Confirmed):**

```json
{
  "query": "string",
  "file": "string — optional cursor/file context",
  "repo": "string",
  "top_k": 0
}
```

**Response (Confirmed fields):**

```json
{
  "final_context": "string — packed XML/context",
  "metrics": {
    "tokens_before": 0,
    "tokens_after": 0,
    "saving_percent": 0,
    "trace": "string | object — pipeline trace"
  },
  "blast_radius": {},
  "memory": {},
  "relevant_files": [],
  "is_real": true
}
```

| Field | EP-002 expectation |
|-------|-------------------|
| `final_context` | Phase-scoped packed context including citation attributes (file:line + confidence) |
| `relevant_files` | Top-ranked files with scores from hybrid+MMR |
| `is_real` | Meaningful boolean for real retrieval (not stub) |
| `metrics` | Present; MVP may be packing token counts only (**OQ-MVP-metrics** / A-06) |
| `blast_radius` | Empty/null allowed (**Proposed** MVP) |
| `memory` | Empty/null allowed (**Proposed** MVP) |

### Proposed extensions (must not Confirmed-freeze)

| Extension | Purpose | Rule |
|-----------|---------|------|
| Optional `phase` (or equivalent) on request | OQ-16 | Label Proposed in OpenAPI; Confirmed request remains without it until product confirms |
| `relevant_files[]` item shape `{path, score, ...}` | FR-006 | Scores required behaviorally; exact keys **Proposed** until evidenced |
| Citation JSON objects parallel to string pack | OQ-11 | Do not invent as Confirmed; attributes must appear in packed context |
| Status codes `200`/`400`/`403`/`404`/`503` | api-contract Proposed | FR-020 — not Confirmed freeze |
| Error envelope | api-contract §4 Proposed | Use if implementing errors; label Proposed |

### Validation

- Confirmed fields validated; `top_k` positive integer without inventing Confirmed bounds (OQ-top_k).
- Do not silently accept packing from raw disk of ignored paths.

### Error handling

- Unknown repo / not indexed: Proposed `404`
- Empty/invalid query or invalid `top_k`: Proposed `400`
- Degraded partial index: prefer partial `relevant_files` + trace note when possible; Proposed `503` only if search cannot proceed — do not invent hard-fail-all as Confirmed
- RBAC/consent deny: Proposed `403` when auth model exists (OQ-01 / US-016)

### Non-goals for API in this epic

- No new Confirmed endpoints (`GET /blast`, symbol REST, memory CRUD, etc.)
- No Confirmed CLI machine-readable schema (OQ-10 / EP-004)
- No re-specification of `POST /index`

---

## UI / UX Changes

**N/A as EP-002 primary deliverable.**

Evidence: Spec marks VS Code extension DX and dashboard/Webview out of scope; CLI ask is consumer note only. Accessibility N/A (`Not evidenced in provided inputs.` for API packing/search flows).

Future consumers (not implemented here):
- CLI `contextos ask` → `POST /context`
- Extension Ask / Pack Context → same API (EP-004 / other stories)

---

## Security Considerations

| Concern | Plan |
|---------|------|
| **Authentication** | `[NEEDS CLARIFICATION]` (api-contract); local/dev trusted loopback MAY apply (A-05) — non-blocking for story intent |
| **Authorization / RBAC** | Constitution III / ADR-012 require path RBAC where applicable; exact schema **OQ-01** — reserve enforcement hook; do not invent roles |
| **Input validation** | Sanitize/validate `query`, `repo`, `top_k`, optional `file`; reject path traversal into excluded content |
| **Sensitive data** | Search/pack only EP-001-permitted content; MUST NOT re-read `.env`/ignored/secrets/binaries from disk to “help” packing (FR-018) |
| **Index exfil** | No assumption of index-time code exfil; vector/pack reads are local (NFR-004) |
| **Query-time LLM** | Not EP-002 deliverable; if later path sends packed context externally, orchestrator consent gate applies (US-016); clients MUST NOT bypass |
| **Secrets management** | No new secrets in repo; reuse secure env for Qdrant/API URLs |
| **Provenance** | Citations file:line + confidence mandatory on successful packs (FR-015) |
| **PII** | Primary N/A for EP-002 (L2/L6); do not invent scrubbing requirements beyond constitution note |
| **Security risks** | See Risks — prompt injection via query string is general LLM concern; EP-002 returns context to caller — do not invent unstated mitigations as Confirmed |

---

## Performance Considerations

| Concern | Plan |
|---------|------|
| **Caching** | Reuse EP-001 pack cache reads; **Proposed** per-process BM25 corpus cache keyed by `repo_name` + content hash if Option A |
| **Pagination** | `top_k` limits result count; no separate pagination API evidenced |
| **Store optimization** | Qdrant HNSW + **Proposed** payload index on `repo_name`; batch/limit vector candidates before MMR |
| **Scalability** | Target NFR-001 at 500k LOC index; fusion/MMR over bounded candidate set (**Proposed** candidate pool size — not Confirmed) |
| **Load expectations** | POC/local Compose; multi-tenant load **Not evidenced** |
| **Latency budget** | Instrument search vs pack spans; fail NFR tasks with measured evidence if p95 ≥800ms — do not silently weaken (constitution IV) |
| **Degraded mode** | Partial index → reduced results when possible (NFR-007) |

---

## Testing Strategy

### Unit Tests

- Score fusion + MMR ordering/diversity behavior (FR-002)
- Phase templates: each of 5 phases produces distinct composition for fixed candidate set (FR-011, FR-012)
- Citation attribute presence (file:line + confidence) without asserting invented JSON keys (FR-015, FR-016)
- Request validation: empty query, non-positive `top_k` (FR-006, FR-020 Proposed)
- Metrics object always present with Confirmed keys; MVP values may be packing counts (FR-017)

### Integration Tests

- Against EP-001-indexed fixture repo + Qdrant: `POST /context` returns Confirmed fields; `relevant_files` ranked with scores; `is_real` true; `blast_radius`/`memory` empty/null allowed
- Hybrid path uses both BM25 and vector signals (behavioral — e.g. keyword-heavy vs semantic-heavy queries) without requiring Confirmed BM25 product name
- Privacy: packing response MUST NOT introduce excluded paths absent from index/pack (FR-018)
- No requirement to call external LLM on `/context` for EP-002 acceptance

### End-to-End Tests

- Docker Compose smoke: API + Qdrant; index via EP-001 `POST /index` then `POST /context` ask (“where is …”) returns files
- CLI ask / extension Ask **not** required E2E for this epic (consumer note only)

### Acceptance Tests (map to SC)

| Success criterion | Test approach | Gap / rule |
|-------------------|---------------|------------|
| SC-001 hybrid ranked files | Integration against indexed repo | — |
| SC-002 p95 <800ms @ 500k LOC | Performance harness at NFR scale | If 500k fixture unavailable, mark **blocked/skipped** with gap note — do not invent pass |
| SC-003 recall@10 >0.92 | Quality harness | **OQ-recall-harness** — blocked for pass claims until harness/dataset exists |
| SC-004 phase composition differs | Same query/repo, two phases | Phase selection via Proposed OQ-16 mechanism |
| SC-005 citations attributes | Inspect `final_context` | No invented schema assert |
| SC-006 response fields | Contract test vs api-contract §2.3 | — |
| SC-007 Search works without full L4 | Assert no Headroom gate dependency | ADR-006 |
| SC-008 MVP metrics | Do not invent `saving_percent` pass thresholds | OQ-MVP-metrics |

### Regression Tests

- EP-001 `POST /index` / pack / exclusion / no-exfil tests remain green
- Consent gate deny-by-default still holds for external send hooks (US-016 boundary)

### Harness gaps (explicit)

- **OQ-recall-harness**: Evaluation set/design **Missing Evidence** — verification of SC-003 cannot claim pass without evidence (constitution Verification Gate).
- **500k LOC perf corpus**: Availability for SC-002 **Not evidenced** in repo at plan time — tasks MUST include discovery or fixture acquisition; mark blocked if unavailable.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| BM25 placement choice misses p95 @ 500k LOC | NFR-001 fail; MVP “Search works” threatened | Start Proposed Option A with candidate limits; measure early; escalate Option B/C with evidence; do not weaken target silently |
| OQ-PACK pack shape drift vs EP-001 | Search/pack breaks or invents fields | Consume Proposed `PackResult`/cache only; adapter isolation; carry OQ-PACK |
| OQ-16 unresolved | Phase AC hard to wire via Confirmed request | Use Proposed mechanism labeled; still prove 5-phase composition difference |
| OQ-11 unresolved | Citation machine interoperability delayed | Require attributes in packed string; no Confirmed JSON freeze |
| recall harness missing | Cannot claim SC-003 pass | Document blocked; still ship functional hybrid search |
| Score fusion / MMR tuning poor | Low recall or redundant results | Tunable Proposed weights; quality tests when harness exists; FR-02 illustrative queries as fixtures |
| Clients reimplement search | Constitution V violation | No CLI/extension search logic in this epic; API-only |
| Pulling L4 into MVP | Roadmap violation (ADR-006) | Explicit out of scope; metrics packing-only |
| Partial index hard-fail | Reliability regression vs BRD §10 | Prefer degraded results; defer operator UX to EP-005 |
| Cross-epic BM25 write (Option B) | Scope creep into EP-001 | Prefer read-time BM25 first |

---

## Dependencies

### Internal Dependencies

| Dependency | Nature |
|------------|--------|
| EP-001 US-001 / US-002 | Pack + Qdrant index must exist for target repo (A-EP002-1) |
| EP-001 Proposed pack cache / `l5_pack.PackResult` | Consume without Confirmed schema freeze (OQ-PACK) |
| FastAPI orchestrator skeleton | Present under `services/orchestrator` |
| Consent gate / ignore policy | Reuse; do not re-specify US-016 UX |

### External Services

| Service | Role |
|---------|------|
| Qdrant | Vector search (local/Compose) |
| Local embedder model weights | Query encoding |

### Third-party Libraries

| Library | Status |
|---------|--------|
| FastAPI / Pydantic | Confirmed stack |
| qdrant-client | Confirmed via EP-001 |
| sentence-transformers / all-MiniLM-L6-v2 | Confirmed |
| BM25 implementation library | **Missing Evidence** — Proposed pick in tasks (e.g. rank_bm25 or equivalent) without claiming BRD pin |
| code2prompt package | Style Confirmed; pin **NEEDS CLARIFICATION** — in-house templates acceptable (**Proposed**) |
| OpenTelemetry SDK | Confirmed compatibility; exporter open |

### Infrastructure Dependencies

- Docker Compose with Qdrant + API (ADR-013)
- EP-001 index completed for acceptance repos

### Downstream (not EP-002 deliverables)

- CLI ask (EP-004), extension Ask/Pack DX, EP-003 Serena composition, V1 L4 budgets, EP-005 health/degraded UX

---

## Implementation Phases

### Phase 0 — Setup / Foundation

- Confirm branch `feature/ep-002-l5-hybrid-search-phase-packing`
- Verify EP-001 index path + Qdrant `codebase` + pack cache readable for a fixture repo
- Scaffold Proposed modules (`api/context`, `l5_search`, etc.) and register router
- Contract stubs for Confirmed request/response fields
- Carry all OQs into task notes (no silent freeze)
- Telemetry helper skeleton for `/context` (exporter-agnostic)

### Phase 1 — User Story 1 / US-003 (P1) — Hybrid Semantic Search with MMR

**Goal**: “Where is X?” via `POST /context` with hybrid BM25 + vector + MMR; ranked `relevant_files` with scores.

- Implement query embedding + Qdrant filtered search
- Implement BM25 retrieval (**Proposed** Option A first; document OQ-BM25-store)
- Fuse + MMR → `relevant_files` / packing candidates
- Return Confirmed response skeleton (`final_context` may be minimal pack of top files before full phase templates)
- `top_k` as positive integer; bounds remain OQ-top_k
- Tests: SC-001, partial SC-006; performance harness tasks for SC-002 (block if no 500k fixture); SC-003 harness discovery (block pass claims)
- Observability: search latency span

**Independent deliverable**: Hybrid retrieval works without phase template matrix or citation schema freeze.

### Phase 2 — User Story 2 / US-004 (P1) — Phase-Aware Prompt Templates

**Goal**: Phase-scoped packing for Requirements / Design / Dev / Test / Deploy; composition differs by phase.

- Implement code2prompt-style templates for five phases
- Assemble `final_context` from hybrid candidates under selected phase
- Phase selection via **Proposed** OQ-16 mechanism (not Confirmed field freeze)
- Explicitly skip full L4 budgets / Headroom (FR-014)
- MVP metrics as packing token counts (A-06 / OQ-MVP-metrics)
- Tests: SC-004, SC-007

**Depends on**: US-003 candidate retrieval.

### Phase 3 — User Story 3 / US-015 (P1) — Provenance Citations

**Goal**: Successful packs include file:line + confidence citations.

- Attach citation attributes into packed `final_context` (BRD §14)
- Do not invent Confirmed JSON schema (OQ-11)
- Ensure `is_real` / Confirmed fields remain coherent
- Tests: SC-005, SC-006 regression

**Depends on**: US-003 + US-004 packing path.

### Phase 4 — Polish / Cross-cutting

- Degraded/partial-index behavior note + tests where feasible (no EP-005 UX)
- OpenAPI descriptions: label all Proposed extensions
- Performance measurement attempt at NFR scale; document gap if blocked
- Recall harness status documented in validation later (not this artifact)
- Regression vs EP-001
- Privacy inheritance checks
- Documentation: quickstart optional; do not invent Confirmed contracts

---

## Evidence Reviewed

| Artifact | Use |
|----------|-----|
| `specs/ep-002-l5-hybrid-search-phase-packing/spec.md` | Primary requirements US-003/004/015 |
| `.specify/memory/constitution.md` v1.0.0 | Governance I–V; Planning Gate |
| `.specify/templates/plan-template.md` | Required plan structure |
| `docs/architecture/architecture-overview.md` | Six-layer model; MVP subset; boundaries |
| `docs/architecture/api-contract.md` §2.3 | Confirmed `POST /context` fields; citations/status notes |
| `docs/architecture/architecture-decisions.md` ADR-006, ADR-011, ADR-014 (+ ADR-001/002/008/009/012/013) | Compression deferral; OTel; hybrid MMR |
| `docs/architecture/tech-stack.md` | FastAPI, Qdrant, MiniLM, grepai/claude-context patterns |
| `docs/architecture/database-schema.md` §2 | Qdrant payload; BM25 placement Missing Evidence |
| `docs/architecture/implementation-guidelines.md` | Folder layout Proposed; testing/OTel budgets |
| `docs/BRD_Context_OS.md` FR-02, FR-03, §8, §10, §12, §14 Pack & Cite, §15 MVP | Product evidence |
| `docs/backlog/user-stories.md` EP-002, US-003, US-004, US-015, OQ-11, OQ-16 | AC alignment |
| `specs/ep-001-l5-repository-packing-indexing/open-questions.md` | OQ-PACK Proposed only |
| `specs/ep-001-l5-repository-packing-indexing/plan.md` / `spec.md` | Qdrant/pack consumption patterns |
| Live tree `services/orchestrator/app/**` | Confirmed EP-001 modules to reuse/extend |

---

## Planning Assumptions

| ID | Assumption | Blocking? |
|----|------------|-----------|
| A-01 | Git source of truth; monorepo ≤1M LOC for MVP (BRD §13) | Non-blocking |
| A-04 | Qdrant available locally or via Docker Compose | Non-blocking (required for vector half) |
| A-05 | Local/dev API may be trusted loopback until authn specified | Non-blocking |
| A-06 | MVP `/context` may return packing token counts; full compression metrics at V1 | Non-blocking |
| A-EP002-1 | EP-001 indexing/packing completed sufficiently for target repo | Non-blocking for plan; **blocking for runtime acceptance** of search |
| A-EP002-2 | CLI/extension ask, when present, call same `POST /context` (consumer note) | Non-blocking |
| A-EP002-3 | OQ-PACK unresolved; proceed against Proposed EP-001 pack handoff without Confirmed freeze | Non-blocking for behavioral delivery; blocks Confirmed pack contract |
| A-EP002-4 (**Proposed**) | BM25 Option A (in-process over pack/chunks) is acceptable initial placement pending OQ-BM25-store / NFR evidence | Non-blocking |
| A-EP002-5 (**Proposed**) | Until OQ-16 resolves, default phase Dev (or test-injected phase) is acceptable for proving composition differences | Non-blocking for story intent |

---

## Open Questions

| ID | Question | Blocking? | Plan handling |
|----|----------|-----------|---------------|
| **OQ-16** | Phase parameter shape on/with `POST /context` | Blocks Confirmed wire freeze | Proposed mechanism only; five phases still required |
| **OQ-11** | Citation JSON shape inside `final_context` | Blocks Confirmed citation schema freeze | Require file:line + confidence attributes |
| **OQ-PACK** | Exact pack schema field inventory | Blocks Confirmed pack contract | Consume EP-001 Proposed handoff |
| **OQ-top_k** | min/max/default beyond positive integer | Blocks numeric AC freeze | Accept positive integer; illustrative top 8 not bound |
| **OQ-MVP-metrics** | MVP `tokens_*` / `saving_percent` meaning | Blocks Confirmed metric interpretation | Packing counts only (A-06) |
| **OQ-recall-harness** | Evaluation harness/dataset for recall@10 | Blocks verification pass claims | Document blocked; no invented results |
| **OQ-BM25-store** | BM25 storage placement | Design Missing Evidence | Proposed options A/B/C; recommend A first |
| **OQ-HTTP-/context** | Confirmed HTTP status codes | Non-blocking | Proposed labels only |
| **OQ-01** | RBAC roles/path/authn schema | Non-blocking for MVP search intent | Do not invent; reserve hooks |

**Label rule**: All remain **OPEN**. Do **not** Confirmed-freeze OQ-11, OQ-16, OQ-PACK, top_k bounds, MVP metrics, HTTP codes, or BM25 placement in this plan.

---

## Out Of Scope (explicit)

- Serena / L3 symbol navigation (EP-003)
- L1 blast radius, structural graph, `GET /blast`, `graph.html`
- L4 Headroom product, FR-11 budgets, FR-12 adaptive summarization, FR-13 compression dashboard (ADR-006)
- L2 multi-modal graphs and L6 persistent memory
- Full CLI surface and machine-readable ask schema (EP-004; OQ-10)
- Extension DX (Ask <3 clicks, Pack Context UX, auto-index/save triggers)
- Re-planning EP-001 packing/indexing (`POST /index`, ignore rules, embedding model)
- Inventing Confirmed pack fields, citation JSON, or phase wire fields
- Confirmed HTTP status-code freeze for `POST /context`
- Query-time external LLM consent UX (US-016) beyond deny-by-default respect
- RBAC role/schema design (OQ-01)

---

## Requirement Coverage Matrix

| Requirement ID | Planned Implementation | Evidence | Status |
| -------------- | ---------------------- | -------- | ------ |
| FR-001 | Hybrid BM25 + vector over packs/index via `l5_search` | ADR-014; Phase 1 | Covered |
| FR-002 | MMR re-ranking in search service | ADR-014; Phase 1 | Covered |
| FR-003 | `POST /context` Confirmed request fields | api-contract §2.3; API Design | Covered |
| FR-004 | Confirmed response fields populated | api-contract §2.3; Phases 1–3 | Covered |
| FR-005 | Meaningful search/pack fields; blast/memory empty/null Proposed | FR-005; Phase 1 | Covered |
| FR-006 | Ranked files with scores; top_k positive int; bounds OQ | Phase 1; OQ-top_k | Covered (bounds open) |
| FR-007 | p95 <800ms @ 500k LOC performance tests | NFR-001; Testing | Covered (fixture gap labeled) |
| FR-008 | recall@10 >0.92 where harness applies | SC-003; OQ-recall-harness | Covered (harness gap labeled) |
| FR-009 | FastAPI owns orchestration; no client bypass | ADR-002; Components | Covered |
| FR-010 | Consume EP-001 packs/Qdrant; OQ-PACK Proposed | EP-001; Phase 0–1 | Covered |
| FR-011 | Phase templates for 5 phases | Phase 2 | Covered |
| FR-012 | Composition differs by phase | Phase 2 tests | Covered |
| FR-013 | No Confirmed phase field invent | OQ-16 Proposed only | Covered |
| FR-014 | L4 product out of scope | ADR-006; Out of Scope | Covered |
| FR-015 | Citations file:line + confidence | Phase 3 | Covered |
| FR-016 | No invented Confirmed citation JSON | OQ-11 | Covered |
| FR-017 | MVP metrics semantics open; packing counts Proposed | A-06; OQ-MVP-metrics | Covered |
| FR-018 | Inherit EP-001 exclusions; no index exfil assumption | Security; Phase 1 privacy tests | Covered |
| FR-019 | CLI/extension consumer note only | Out of Scope DX | Covered |
| FR-020 | Status codes Proposed not Confirmed | API Design; OQ-HTTP | Covered |

---

## Governance Notes

- Constitution Applied: **Yes** (I–V)
- Planning Gate: **Met** with open questions carried
- Ready for Task Generator: **Yes**, provided tasks preserve Proposed vs Confirmed labels and do not invent harness pass results
)
