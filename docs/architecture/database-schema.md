# ContextOS — Database / Store Schema

**Sources:** BRD §5, §9 FR-07..10, FR-14..18, §14, Appendix C/D  
**Note:** ContextOS uses **graph + vector + memory** stores, not a single relational RDBMS. Relational-style tables below are **logical** models for implementers.

---

## 1. Store Inventory by Roadmap

| Store | Technology (Confirmed) | Layer | Phase | Purpose |
|-------|------------------------|-------|-------|---------|
| Vector index | Qdrant `http://localhost:6333`, collection `codebase`, 384-dim | L5 | MVP | Hybrid semantic search |
| Structural graph | FalkorDB `redis://localhost:6379` | L1 | V1 | IMPORTS / typed graph / blast |
| Multi-modal graph | FalkorDB and/or Graphify property graph (**co-location Missing Evidence**) | L2 | V2 | Docs/SQL/images/transcripts links |
| Entity memory | Cognee-style store (**physical engine Missing Evidence**) | L6 | V2 | Cross-session entities + temporal edges |
| Index metadata | **Not evidenced** — Proposed ops records | Cross-cutting | MVP+ | Freshness, partial index, counts |

---

## 2. Qdrant — `codebase` collection (MVP / L5)

### Confirmed

| Attribute | Value | Evidence |
|-----------|-------|----------|
| Dimensions | 384 | BRD §14, §10 |
| Model | `sentence-transformers/all-MiniLM-L6-v2` local CPU | BRD §14 |
| Chunking | ~500 tokens | Appendix C |
| Index type | HNSW mentioned with grepai/claude-context | BRD §14 |

### Logical payload fields

| Field | Type | Required | Status |
|-------|------|----------|--------|
| `point_id` | UUID/string | Yes | Proposed PK |
| `repo_name` | string | Yes | Confirmed concept via API |
| `file_path` | string | Yes | Appendix C |
| `content` / chunk text | string | Yes | Appendix C |
| `embedding` | float[384] | Yes | Confirmed |
| `token_count` | int | Recommended | FR-01 token pre-calc |
| `indexed_at` | timestamp | Recommended | Freshness / staleness |
| `content_hash` | string | Optional | Proposed for delta skip |

### Indexes / constraints

- Vector index: HNSW (Confirmed mention).
- Payload indexes on `repo_name`, `file_path`: **Proposed** for filtered search.
- BM25 corpus: **Confirmed** hybrid search requirement; whether BM25 lives in Qdrant payload, sidecar, or grepai index — **Missing Evidence**.

### Normalization

- One point per chunk; file may map to many chunks.
- Re-index on file save replaces/updates chunks for that file (BRD §14 timing claims).

---

## 3. FalkorDB — Structural graph (V1 / L1)

### Confirmed node chain

`File → Module → Class → Method → Call` (FR-07)  
Edge (Appendix C): `(File)-[:IMPORTS]->(File)`

### Confirmed / FR-derived node types

| Node | Key properties | Status |
|------|----------------|--------|
| File | name/path, repo | Confirmed |
| Module | name | Confirmed in typed chain |
| Class | name, file ref | Confirmed |
| Method | name, signature | Confirmed |
| Call | callee linkage | Confirmed |
| Test | identity for `tests_to_run` | Implied by FR-08 — property schema **Missing Evidence** |
| Owner | for owners list | Implied by FR-08 — model **Missing Evidence** (property vs node) |
| DbTable | for `db_tables` in blast | Implied by FR-08 |

### Confirmed query pattern

```cypher
MATCH (f)-[:IMPORTS*1..3]->(dep) WHERE f.name="payment.service.ts"
```

(BRD §14)

### Blast radius outputs (FR-08) — logical

| Output | Backing | Status |
|--------|---------|--------|
| `direct_dependents` | 1-hop reverse IMPORTS / calls | Confirmed |
| `transitive` | N-hop | Confirmed |
| `db_tables` | File/symbol↔table edges | Confirmed field; edge population timing may need L2 — **NEEDS CLARIFICATION** |
| `risk` | HIGH\|MEDIUM\|LOW | Confirmed enum; scoring algorithm **Missing Evidence** |
| `tests_to_run` | test linkage | Confirmed field; linkage rules **Missing Evidence** |
| owners | FR-08 prose | Schema **Missing Evidence** |

### Indexes / constraints (Proposed)

- Index on `File.name` / path unique per repo.
- Bound traversal depth (1–5 viz FR-09; blast N-hop with p95 target).

### Incremental indexing

- Delta <60s for 100-file delta (FR-07); 0.5s single-file save claim (BRD §14).
- Staleness badge mitigation (BRD §13) implies a freshness flag — storage **Proposed**.

---

## 4. Multi-modal graph (V2 / L2)

### Confirmed artifact types (FR-14)

Markdown, ADRs, SQL DDL, OpenAPI, images, Loom transcripts — property graph **with embeddings**.

### Confirmed linking examples (FR-15)

`UserService ↔ users table ↔ ADR-014 ↔ JIRA-123 ↔ Figma`

### Logical entities

| Entity | Status |
|--------|--------|
| DocArtifact (markdown/ADR/OpenAPI) | Confirmed types |
| SqlArtifact | Confirmed |
| ImageArtifact (+ OCR) | Confirmed capability |
| TranscriptArtifact | Confirmed |
| ExternalRef (Jira/Figma/…) | Confirmed examples; auth **Missing Evidence** |

### Relationships

- Entity resolution links between code symbols and artifacts (FR-15).
- Exact edge type names: **Not evidenced in provided inputs.**

### PII

- Redact PII in multi-modal ingestion paths (constitution III; FR-18 related).

---

## 5. Persistent agent memory (V2 / L6)

### Confirmed entity types (FR-16)

`Person`, `Service`, `Decision`, `Incident`

### Confirmed properties / behaviors

| Concern | Requirement | Evidence |
|---------|-------------|---------|
| Temporal edges | Yes | FR-16 |
| Source provenance | Yes | FR-16, constitution III |
| Recall explainability | source + timestamp | FR-17 |
| TTL | Yes | FR-18 |
| Decay | Yes | FR-18 |
| Pin / forget | Manual | FR-18 |
| PII redaction | Yes | FR-18, constitution III |
| Latency | <1.2s p95 recall | FR-17, §10 |
| Precision | >90% recall | §12 |

### Physical storage engine

**Not evidenced** beyond “Cognee-style”. May be separate DB or graph-backed — **NEEDS CLARIFICATION**.

### Logical tables (for implementers)

**MemoryEntity**

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| type | enum | Person\|Service\|Decision\|Incident |
| label / content | text | |
| provenance_source | string | |
| created_at / updated_at | timestamps | |
| ttl | timestamp nullable | |
| decay_score | float | algorithm **Missing Evidence** |
| pinned | bool | |
| forgotten | bool | soft delete semantics **Proposed** |
| pii_redacted | bool | |

**TemporalEdge**

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| from_entity / to_entity | FK | |
| relation | string | vocabulary **Missing Evidence** |
| valid_from / valid_to | timestamps | |
| provenance | string | |

---

## 6. Index metadata (Proposed)

Supports NFRs (availability, degraded search, staleness):

| Column | Purpose |
|--------|---------|
| repo_name PK | |
| repo_path | |
| last_full_index_at / last_delta_at | |
| files_indexed / graph_nodes / embeddings_count | Aligns with `POST /index` response |
| partial_index / staleness_flag | Degraded mode + badge |

**Not evidenced** as a concrete table — Proposed only.

---

## 7. Relationships Summary

```
RepositoryIndex 1—* codebase_chunk (Qdrant)
RepositoryIndex 1—* File (FalkorDB)
File -[:IMPORTS]-> File
File contains Module contains Class contains Method invokes Call
File/Method associated with Test, Owner, DbTable (blast — details Missing Evidence)
Code symbols *—* Doc/SQL/Image/Transcript/ExternalRef (V2)
MemoryEntity *—* MemoryEntity via TemporalEdge (V2)
```

---

## 8. Normalization Recommendations

1. Keep **vector chunks** separate from **structural graph nodes** (different stores; join by `repo_name` + `file_path`).
2. Do not duplicate full file text in FalkorDB if Qdrant/FS already holds content — store paths/symbols in graph (**Proposed**).
3. Memory entities reference code via provenance paths/patterns (example `auth.middleware.ts` in FR-16), not by copying entire files.
4. Apply ignore/PII policies **before** persistence in all stores.

---

## 9. Missing Evidence Checklist

- Full Qdrant payload & BM25 placement
- FalkorDB property keys, uniqueness, owner/test edge semantics
- Risk score algorithm for HIGH/MEDIUM/LOW
- Whether `db_tables` edges require L2 SQL ingest
- Cognee physical DB choice and multi-tenancy
- RBAC policy store schema
- Retention for OpenTelemetry / audit logs
