# Backend Agent Brief — EP-002

You are the ContextOS Backend Engineering Agent. Implement EP-002 L5 Hybrid Search & Phase-Aware Packing on the REQUIRED git branch `feature/ep-002-l5-hybrid-search-phase-packing` under workspace `/Users/hamzahamal/ContextOS`. Do NOT push or merge to main. Prefer leaving commits for parent unless useful for handoffs. Do NOT rewrite requirements/specs/plans/tasks.

## MANDATORY Graphify

- BEFORE any Read/Grep/Glob to explore code: run `graphify query "..."` with a relevant query (e.g. hybrid search, l5_pack, qdrant, POST context).
- AFTER code changes: run `graphify update .`

## Feature path (read first)

`specs/ep-002-l5-hybrid-search-phase-packing/`

- spec.md, plan.md, tasks.md, validation-report.md (Conditionally approved ~8.6/10)

Also read:

- `.specify/memory/constitution.md`
- `docs/architecture/api-contract.md` §2.3 POST /context (Confirmed fields ONLY)
- ADR-014 (hybrid BM25+vector+MMR), ADR-006 (no L4 gate), ADR-011 (OTel)
- EP-001: `specs/ep-001-l5-repository-packing-indexing/open-questions.md` (OQ-PACK)
- Existing `services/orchestrator/` — REUSE, do not duplicate EP-001 indexing/pack
- Lead handoff in `.cursor/agent-handoffs/handoff.md` (latest lead-developer + backend-agent pre-delegation)

## Stories

- US-003: hybrid BM25+vector+MMR search via POST /context
- US-004: phase-aware packing (Requirements/Design/Dev/Test/Deploy)
- US-015: provenance citations file:line + confidence (Proposed representation)

## Validation conditions (MUST honor)

1. Do NOT Confirmed-freeze OQ-PACK, OQ-11 (citation JSON), OQ-16 (phase parameter) — Proposed paths only.
2. Do NOT expand into Serena (EP-003), L1 blast, L4 compression product, L2/L6, full CLI epic, extension DX.
3. Reuse EP-001 Qdrant/index/pack foundation; extend FastAPI for search/context packing.
4. Measurable search claims (p95, recall@10) remain Planned until harnesses execute; if unmet, document gap (constitution IV). Create blocked/skipped placeholders — NEVER invent Pass/Fail.
5. Do not invent unsupported requirements, APIs, or fake results.

## Confirmed API contract (api-contract §2.3)

Request Confirmed: `query`, `file` (optional), `repo`, `top_k`

Response Confirmed: `final_context`, `metrics` (tokens_before, tokens_after, saving_percent, trace), `blast_radius`, `memory`, `relevant_files`, `is_real`

- MVP: blast_radius/memory MAY be empty/null (Proposed)
- Optional Proposed request field `phase` for OQ-16 — label Proposed in OpenAPI; do NOT claim Appendix D Confirmed
- Citations inside final_context: file:line + confidence attributes; exact JSON schema OQ-11 OPEN — use Proposed interim (e.g. XML attributes) and document

## Implementation order (follow tasks.md IDs)

### Phase 1 Setup T001–T007

- Verify EP-001 modules exist; inventory PackResult Proposed fields (do not freeze)
- Scaffold: `api/context.py`, `api/schemas_context.py`, `services/l5_search.py`, `services/l5_phase_pack.py`, `services/l5_citations.py`, `adapters/bm25_store.py`, `telemetry/context.py`
- Create `specs/ep-002-l5-hybrid-search-phase-packing/open-questions.md` with OQ register (OQ-16, OQ-11, OQ-PACK, OQ-top_k, OQ-MVP-metrics, OQ-recall-harness, OQ-BM25-store, OQ-HTTP-/context, OQ-01) — Proposed Option A for BM25; do not invent resolutions
- Pytest layout stubs under `services/orchestrator/tests/{unit,integration,contract}/`

### Phase 2 Foundational T008–T020

- Confirmed Pydantic models in schemas_context.py
- Stub then register POST /context in main.py
- Proposed config knobs (MMR λ, fusion weights, default phase, candidate pool, pack cache reuse)
- Telemetry stubs; pack-loader helper from EP-001 PackResult/cache (Proposed)
- Reuse ignore_policy + consent_gate; RBAC hook comment only (OQ-01)
- Contract test skeleton for Confirmed field names
- Document OQ discoveries; assess 500k fixture availability (likely missing → mark perf blocked)

### Phase 3 US-003 T021–T038

- Tests first (expect red then green): unit MMR fusion, validation, contract, integration hybrid search + hybrid signals + exclusions, perf harness SKIPPED if no 500k fixture, recall@10 placeholder BLOCKED
- Extend qdrant_store with filtered search by repo_name
- Reuse embeddings for query encode
- BM25 Option A in-process over pack/chunk texts (e.g. rank_bm25 Proposed)
- l5_search: hybrid fusion + MMR → ranked hits with scores
- Wire context router: validate → load pack/index → hybrid+MMR → relevant_files, minimal final_context, metrics skeleton, is_real=true
- Proposed 404/400 status labels; degraded partial results preferred
- Telemetry spans; OpenAPI Proposed labels

### Phase 4 US-004 T039–T049

- Choose Proposed OQ-16 mechanism (recommend optional Proposed `phase` field labeled Proposed, default Dev)
- Implement 5 phase templates in l5_phase_pack.py; composition MUST differ by phase
- Integrate after hybrid; MVP metrics packing token counts only; no L4 gate
- Tests: phase templates unit, integration two-phase difference, no L4 gate, metrics keys present
- Optional quickstart.md

### Phase 5 US-015 T050–T057

- Document Proposed citation representation (OQ-11 open)
- l5_citations.py attach file:line + confidence into packed string
- Integrate into phase pack pipeline
- Unit + integration + contract regression — assert attribute presence NOT invented Confirmed JSON keys

### Phase 6 Polish T058–T070

- Degraded index tests; OpenAPI review; document SC-002/SC-003 gaps; EP-001 regression green; security no disk re-read of excluded paths; telemetry verify; quickstart; Compose smoke if feasible; FR-019 consumer note only; confirm OOS; OQ-01 hook note

## Path conventions

```
services/orchestrator/app/
  api/{context.py, schemas_context.py}
  services/{l5_search.py, l5_phase_pack.py, l5_citations.py}  # NEW
  services/{l5_pack.py, l5_chunk.py, l5_index.py}  # EXTEND/REUSE
  adapters/{qdrant_store.py, embeddings.py, bm25_store.py}
  telemetry/context.py
  config.py, main.py
```

## Handoff

Append (do NOT overwrite) to `.cursor/agent-handoffs/handoff.md` when done using the exact format:

```markdown
---

## Handoff: backend-agent

Date:

Feature:

Task IDs:

Source Input:

Artifacts Reviewed:

Artifacts Created or Updated:

### What was completed

-

### What failed

-

### Next instructions

-

### Blocking questions

-
```

Include: files changed, tests added, tests run (commands + honest Pass/Fail/Skip/Blocked), OQ status, any blockers.

## Return to lead developer

Provide a concise completion summary:

1. Phases/tasks completed vs remaining
2. Key paths created/updated
3. Tests run + results (honest)
4. OQ Proposed choices used (phase wire, citation shape, BM25 Option A)
5. Blockers / remaining work for testing-agent
