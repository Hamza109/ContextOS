# ContextOS — API Contract

**Sources:** BRD Appendix D (evidenced); BRD FR-08/FR-09; constitution V  
**Classification:** Confirmed endpoints vs Proposed extensions clearly labeled  

---

## 1. Authentication

| Item | Status |
|------|--------|
| Authn mechanism (API key, SSO, mTLS, local trust) | **Not evidenced in provided inputs.** |
| Authz / RBAC per repo path | **Confirmed requirement** (BRD §10; constitution III); **role/path schema Missing Evidence** |
| Query-time external LLM | Requires **explicit consent/configuration** (constitution III; BRD Appendix C) |
| Telemetry opt-out | Clients must not silently bypass (constitution V); **opt-out API Missing Evidence** |

Until auth is specified, treat local/dev as trusted loopback for POC only (**Assumption** from Docker Compose POC narrative, BRD §15).

---

## 2. Confirmed Endpoints (BRD Appendix D)

### 2.1 `GET /`

**Purpose:** Health and dependency status.  
**Roadmap:** MVP+  

**Response (Confirmed fields from Appendix D intent):**

```json
{
  "status": "ok | degraded | error",
  "pipeline": "string — pipeline readiness summary",
  "falkor": "status object or string — connectivity",
  "qdrant": "status object or string — connectivity"
}
```

| Aspect | Detail |
|--------|--------|
| Auth | **NEEDS CLARIFICATION** |
| Validation | None beyond GET |
| Status codes | **Not evidenced** — **Proposed:** `200` healthy/degraded body; `503` if critical deps down |

**MVP note:** Falkor may be unused until V1; health should still report presence/absence without failing MVP search (**Proposed** degraded semantics).

---

### 2.2 `POST /index`

**Purpose:** Index a repository (L5 embeddings MVP; L1 graph nodes V1; L2/L6 V2).  
**Roadmap:** MVP (L5); extends in V1/V2  

**Request (Confirmed):**

```json
{
  "repo_path": "string — local path to repository",
  "repo_name": "string — logical repository name"
}
```

**Response (Confirmed):**

```json
{
  "files_indexed": 0,
  "graph_nodes": 0,
  "embeddings": 0,
  "time_ms": 0
}
```

| Aspect | Detail |
|--------|--------|
| Side effects | Respect `.gitignore`; ignore `.env`, `node_modules`, `dist`, `.git`, binaries (FR-01, Appendix C, constitution III) |
| Embedding | Local `all-MiniLM-L6-v2`, 384-dim; **no code exfil to LLM during indexing** |
| Status codes | **Not evidenced** — **Proposed:** `200` success; `400` invalid path; `403` RBAC denial; `409` index in progress; `500` failure |
| Incremental | Auto/delta on save described in BRD §14 — **trigger API beyond POST /index Not evidenced** (extension may call same endpoint with narrower scope — **Proposed**) |

**OQ-14 status (EP-001 sync note — 2026-07-27):** Still **Unresolved**. Product has not Confirmed incremental fields. Backend implementation may accept **Proposed** optional request fields `paths` / `files` on `POST /index` for narrower-scope re-index; these MUST remain labeled Proposed in OpenAPI and MUST NOT be treated as Appendix D Confirmed. No new Confirmed endpoints. See `specs/ep-001-l5-repository-packing-indexing/open-questions.md`.

**EP-006 implementation note:** The existing route now performs FastAPI-owned L1 extraction
after the shared ignore/no-exfiltration boundary, persists repository-isolated structural
metadata in FalkorDB, and reports the distinct persisted request-node count through the
existing `graph_nodes` field. L1 failure uses the existing generic index failure path; no
request field, response field, endpoint, or graph-specific HTTP contract was added.

**EP-013 Proposed implementation note:** After the same eligibility boundary (and after L1
when present), FastAPI may generate a repository-scoped OKF v0.2 markdown bundle under a
Proposed cache directory. Concept counts are **not** added to the Confirmed `/index`
response. OKF generation failure must preserve existing Confirmed index outcomes.

---

### 2.3 `POST /context`

**Purpose:** Retrieve compressed / packed context for a query (pipeline depth depends on roadmap phase).  
**Roadmap:** MVP returns L5+L3 oriented payload; V1 adds blast/metrics depth; V2 adds memory  

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

| Field | Phase notes |
|-------|-------------|
| `final_context`, `relevant_files`, `is_real` | MVP+ |
| `metrics` compression ratios | Meaningful with L4 (**V1**); MVP may return packing token counts only — **NEEDS CLARIFICATION** for MVP metric semantics |
| `blast_radius` | **V1** (FR-08); empty/null in MVP — **Proposed** |
| `memory` | **V2** (FR-17); empty/null earlier — **Proposed** |

| Aspect | Detail |
|--------|--------|
| Performance | Contributes to search p95 <800ms (L5) and overall ask <2s MVP exit / <8s demo (BRD §15) |
| Citations | BRD §14: file:line + confidence in packed context — **exact JSON shape for citations inside final_context Missing Evidence** |
| Status codes | **Not evidenced** — **Proposed:** `200`; `400` validation; `403` RBAC/consent; `404` unknown repo; `413`/`422` budget hard-fail (FR-11 V1); `503` degraded |

**EP-006 implementation note:** For supported structural location/ownership questions,
FastAPI may append a delimited, cited L1 evidence block inside the existing `final_context`
string and add non-sensitive cache/status/timing values inside the existing `metrics.trace`.
The response shape is unchanged. Cache miss, stale revision, unsupported intent, or
unavailable L1 preserves the existing L5 context. `contextos_ask` remains a stateless thin
client. Blast-radius computation is delivered in EP-007 (`GET /blast`, V1 `blast_radius`
populate) — see §2.4.

**EP-013 Proposed implementation note:** FastAPI may attempt OKF concept/link lookup before
L1 structural enrichment and L5 BM25/vector fallback. Cited OKF evidence may appear only
inside existing `final_context`, with non-sensitive `okf_status` / timing notes inside
existing `metrics.trace`. No new Confirmed request/response fields or endpoints. Miss or
error preserves hybrid search. MCP remains a stateless pass-through.

**EP-008 Proposed implementation note:** When L4 compression is enabled (`CONTEXTOS_L4_ENABLED`),
Confirmed `metrics.tokens_before` / `tokens_after` / `saving_percent` are **L4-meaningful**
(pre-L4 vs post-L4). When L4 is off, those keys remain packing-estimate semantics from
`pack_for_phase`. Proposed `metrics.trace` notes only: `l4_gate`, `l4_stage_order`,
`budget_status`, `degraded`. Proposed HTTP `413`/`422` for budget hard-fail are **not
Confirmed** — soft-degrade on `200` with `trace.budget_status` is preferred. Dev phase
canonical token ceiling remains **[NEEDS CLARIFICATION: OQ-07]** (injectable budgets only).

---

### 2.4 `GET /blast/{file_name}`

**Purpose:** Blast-radius analysis (FR-08).  
**Roadmap:** **V1**  

**Query params (Confirmed):** `repo`  

**Response (Confirmed shape from FR-08):**

```json
{
  "direct_dependents": [],
  "transitive": [],
  "db_tables": [],
  "risk": "HIGH | MEDIUM | LOW",
  "tests_to_run": []
}
```

**Owners list** mentioned in FR-08 prose — include as **Proposed** field `owners: []` until schema confirmed (OQ-15 — **no** Confirmed element schema).

**EP-007 implementation notes (Proposed — not Confirmed):**
- Hop bound default **3** (BRD `IMPORTS*1..3` context); optional Proposed `max_hops` query 1–5.
- Reverse `IMPORTS` dependents (files that import the target); paths/ids only — no source bodies.
- `db_tables`: V1 always `[]` (L2 Missing Evidence).
- `tests_to_run`: path-derived conservative candidates from existing File nodes under `tests/` only — **not** Confirmed L2 linkage.
- `risk`: conservative L1-only heuristic (documented in `l1_blast.py`) — **not** a Confirmed scoring algorithm.
- `index_revision`: **Proposed** optional freshness field on the JSON response (US-027); threshold remains **NEEDS CLARIFICATION**.
- `POST /context` populates existing Confirmed `blast_radius` with the same field set when blast intent applies + resolvable file; without file → Proposed empty `{}` (`blast_intent_no_file`). Status codes for `/context` unchanged.
- IgnorePolicy hard-exclude reuse on path serialization (FastAPI-owned; MCP thin).

| Aspect | Detail |
|--------|--------|
| Latency target | p95 <2s for 3-hop / 10k nodes (BRD §10) — validation harness opt-in; no pass without evidence |
| Status codes | **Not evidenced** — **Proposed:** `200`; `404` file/repo; `503` store unavailable |

---

### 2.5 `GET /graph.html?repo=`

**Purpose:** Interactive dependency graph page (FR-09).  
**Roadmap:** **V1**  

| Aspect | Detail |
|--------|--------|
| Format | HTML with vis-network; nodes=files, edges=IMPORTS; physics disabled; arrows; color `#64748b`; background `#0f172a` (BRD §14) |
| Depth | Interactive **1–5** (Confirmed FR-09); server clamps query `depth` |
| Auth | **NEEDS CLARIFICATION** (static HTML may embed in Webview) — local trusted-client draft only for V1 |
| Freshness | **Proposed** `data-index-revision` / HTML comment; `data-stale="false"` default — numeric threshold **NEEDS CLARIFICATION** |
| Status codes | **Not evidenced** — **Proposed:** `200` text/html; `404` unknown repo; `503` store unavailable |
| Privacy | Metadata/paths only; IgnorePolicy hard-excludes filtered; no source bodies |

**EP-007 note:** CDN vis-network is acceptable for local trusted draft. Payload size capped. No Confirmed auth claim.

---

## 3. Proposed Endpoints (FR-implied only)

Do **not** implement as committed contract without product confirmation. Label as Proposed:

| Proposed endpoint | Implied by | Rationale |
|-------------------|------------|-----------|
| `GET /metrics` or static `contextos_token_dashboard.html` | FR-13 | Dashboard named; **serving mechanism Missing Evidence [OQ-08]**. **Proposed** local draft: `GET /contextos_token_dashboard.html` (graph.html-style; no Confirmed auth / no Confirmed `GET /metrics`) |
| Memory CRUD (`pin` / `forget`) | FR-18 | Governance required; **HTTP shapes Not evidenced** |
| Multi-modal ingest trigger | FR-14 | Ingestion required V2; may reuse `POST /index` — **NEEDS CLARIFICATION** |
| Symbol proxy REST | FR-04..06 | May remain Serena MCP-only without REST — **NEEDS CLARIFICATION** |

Any other endpoints: **Not evidenced in provided inputs.**

---

## 4. Error Response Envelope (Proposed)

**Not evidenced** in BRD. Proposed for OpenAPI consistency:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "correlation_id": "string"
  }
}
```

---

## 5. Validation Rules (Confirmed + Proposed)

| Input | Rule | Evidence |
|-------|------|----------|
| `repo_path` | Must be readable local path; indexing respects ignore policy | FR-01, Appendix C |
| `.env` / secrets | Never indexed | constitution III, BRD §10 |
| `top_k` | Positive integer; example top 8 in FR-02 | FR-02 example; bounds **Missing Evidence** |
| Phase budgets | Dev/Design budgets enforced V1 | FR-11 examples Dev=12k / Design=32k (also Dev=8k in §5 — **NEEDS CLARIFICATION** which canonical) |
| Webview messages | Sanitize | constitution III |

---

## 6. CLI Mapping (Confirmed intent)

| CLI | Maps to | Notes |
|-----|---------|-------|
| `contextos ask 'where is X?'` | Context retrieval path (`POST /context` or equivalent) | BRD §15 MVP |
| Other verbs | **Missing Evidence** exact taxonomy | |

---

## 7. OpenAPI Ownership

FastAPI orchestrator **owns** OpenAPI contracts; extension/CLI consume synchronized clients (constitution V, Implementation Gate).
