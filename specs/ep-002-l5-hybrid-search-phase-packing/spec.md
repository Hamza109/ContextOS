# Feature Specification: EP-002 L5 Hybrid Search & Phase-Aware Packing

**Feature Branch**: `feature/ep-002-l5-hybrid-search-phase-packing`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "EP-002 — L5 Hybrid Search & Phase-Aware Packing (US-003, US-004, US-015): answer “where is X?” with high-recall hybrid BM25 + vector search (MMR) and assemble phase-scoped context packs with provenance citations (BO-01, BO-04)."

**Stories Covered**: US-003, US-004, US-015

**Business Objectives**: BO-01, BO-04

**Source Evidence**: BRD FR-02, FR-03; §8 phase mapping; §10 search NFR; §12 recall@10; §14 Pack & Cite; §15 MVP; ADR-014; ADR-006; api-contract `POST /context` §2.3; EP-001 pack/index foundation (Proposed OQ-PACK handoff); constitution I–V

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Hybrid Semantic Search with MMR (Priority: P1)

As a **Developer**, I want hybrid BM25 + vector search with MMR re-ranking over packed repos, so that I can find relevant files for questions like “where is payment retry logic?” quickly and accurately.

**Why this priority**: Primary MVP search outcome (BRD §15 “Search works”); directly supports BO-04 discovery and FR-02. Independently delivers “where is X?” retrieval without requiring phase templates or citation schema freeze.

**Independent Test**: Against an EP-001-indexed repository at the NFR reference scale (500k LOC index target), submit a natural-language search/ask via confirmed `POST /context` and verify relevant files returned via hybrid BM25 + vector retrieval with MMR re-ranking, with scores; measure semantic search p95 and recall@10 where the evaluation harness applies.

**Acceptance Scenarios**:

1. **Given** an indexed repository at the NFR reference scale (500k LOC index target), **When** I submit a natural-language search/ask via `POST /context` (or a CLI ask that consumes the same context retrieval path), **Then** the system returns relevant files using hybrid BM25 + vector retrieval with MMR re-ranking.
2. **Given** the same conditions, **When** latency is measured for semantic search, **Then** semantic search p95 is <800ms for a 500k LOC index (BRD §10).
3. **Given** a quality evaluation set aligned to BRD success metrics, **When** recall@10 is measured, **Then** relevant results in top 10 achieve >0.92 where the evaluation harness applies (BRD §12). **Harness availability/design gaps remain open** — see Open Questions / Success Criteria.
4. **Given** FR-02 example intent, **When** querying for payment-retry-logic style questions, **Then** results include top-ranked files with scores (illustrative example: top 8 files — exact `top_k` bounds `[NEEDS CLARIFICATION: OQ bounds for top_k]`).

---

### User Story 2 — Phase-Aware Prompt Templates (Priority: P1)

As a **Developer**, I want context packs assembled using templates scoped to SDLC phase (Requirements/Design/Dev/Test/Deploy), so that prompts match the work I am doing.

**Why this priority**: Phase-aware packing is an MVP deliverable (BRD §15 basic prompt packing; FR-03) reducing irrelevant context (BO-01). Independently testable once hybrid retrieval (US-003) can supply candidate files; does not require citation schema freeze.

**Independent Test**: For the same query/repo, assemble context under two different supported SDLC phases among Requirements, Design, Dev, Test, Deploy and verify phase-scoped (code2prompt-style) templates are used and pack composition differs by phase. Exact phase parameter wire shape remains `[NEEDS CLARIFICATION: OQ-16]`.

**Acceptance Scenarios**:

1. **Given** a supported SDLC phase selection among Requirements, Design, Dev, Test, Deploy, **When** context is assembled via the FastAPI packing path (`POST /context` pipeline), **Then** the system uses phase-scoped prompt/pack templates (code2prompt-style per FR-03).
2. **Given** two different phases for the same query/repo, **When** packs are compared, **Then** pack composition differs according to phase scoping (exact parameter wire shape `[NEEDS CLARIFICATION: OQ-16]`).
3. **Given** MVP scope and ADR-006, **When** phase-aware packing runs, **Then** full L4 token-budget enforcement / Headroom product behavior is **not** required as an MVP gate (owned by V1 / US-022); basic phase-scoped packing is sufficient for this story.

---

### User Story 3 — Provenance Citations in Packed Context (Priority: P1)

As a **Developer**, I want packed context to include citations with file:line and confidence, so that I can verify where AI context came from.

**Why this priority**: Trust and auditability of SDLC intelligence outputs (constitution III provenance; BRD §14 Pack & Cite). Depends on search + packing (US-003, US-004) but is independently verifiable by inspecting `final_context` / packed output for citation presence of file:line and confidence.

**Independent Test**: Perform a successful `POST /context` (or IDE/CLI ask that returns packed context from that API) and inspect `final_context` for citations that include file:line and confidence per BRD §14, without inventing an exact JSON citation schema (`[NEEDS CLARIFICATION: OQ-11]`).

**Acceptance Scenarios**:

1. **Given** a successful `POST /context` (or IDE/CLI ask) response, **When** `final_context` is inspected, **Then** citations include file:line and confidence as described in BRD §14.
2. **Given** citation machine shape is not fully specified, **When** this specification is applied, **Then** exact JSON citation schema inside `final_context` remains `[NEEDS CLARIFICATION: OQ-11]` — requirements MUST NOT invent undocumented citation fields.

---

### Edge Cases

- Repository not indexed / unknown `repo` — api-contract Proposed `404`; Confirmed status-code mapping **Not evidenced** (`[NEEDS CLARIFICATION]`).
- Empty or invalid `query` / invalid `top_k` — Proposed `400` validation; Confirmed mapping **Not evidenced**.
- Partial index / degraded search availability — BRD §10 graceful degraded search is evidenced for platform reliability; primary ownership of health/degraded UX is US-014 (EP-005). EP-002 SHOULD NOT invent operator UX beyond noting search may degrade rather than hard-fail when degradation is possible.
- `top_k` bounds beyond “positive integer” / FR-02 illustrative top 8 — **Missing Evidence** (`[NEEDS CLARIFICATION: OQ bounds for top_k]`).
- Phase parameter absent or unsupported value — wire shape and defaulting **Not evidenced** (`[NEEDS CLARIFICATION: OQ-16]`). Until clarified, System MUST still support the five named phases conceptually (FR-03) without inventing a Confirmed request field.
- Exact pack schema field inventory from EP-001 — **Proposed handoff only** (`[NEEDS CLARIFICATION: OQ-PACK]`); do not Confirmed-freeze pack fields.
- MVP `metrics` compression semantics (`tokens_before` / `tokens_after` / `saving_percent`) — Meaningful with L4 (V1); MVP may return packing token counts only (`[NEEDS CLARIFICATION: MVP metric semantics]` per api-contract §2.3; A-06).
- `blast_radius` / `memory` on `POST /context` — empty/null in MVP (**Proposed**); not EP-002 deliverables.
- BM25 storage placement — ADR-014 trade-off: **Missing Evidence**; hybrid behavior is required without inventing a Confirmed BM25 store design.
- CLI ask / extension Ask as consumers of `POST /context` — allowed as consumer notes (US-003 AC); CLI full surface (EP-004) and extension DX (EP-004/extension stories) are **out of scope** for this Spec Kit.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide hybrid search combining BM25 and vector retrieval over flattened/packed repository content.  
  *Source: US-003; BRD FR-02; ADR-014*

- **FR-002**: System MUST apply MMR re-ranking to hybrid search results.  
  *Source: US-003; BRD FR-02; ADR-014*

- **FR-003**: System MUST expose hybrid search / context retrieval via confirmed `POST /context` with Confirmed request fields `query`, `file` (optional), `repo`, and `top_k`.  
  *Source: US-003; api-contract §2.3; BRD Appendix D*

- **FR-004**: System MUST return Confirmed response fields from `POST /context`: `final_context`, `metrics` (object with `tokens_before`, `tokens_after`, `saving_percent`, `trace`), `blast_radius`, `memory`, `relevant_files`, and `is_real`.  
  *Source: US-003, US-015; api-contract §2.3*

- **FR-005**: For MVP, `final_context`, `relevant_files`, and `is_real` MUST be meaningful search/packing outputs; `blast_radius` and `memory` MAY be empty/null (**Proposed** MVP behavior per api-contract — not Confirmed product features of EP-002).  
  *Source: api-contract §2.3 phase notes; EP-002 scope*

- **FR-006**: System MUST return top-ranked relevant files with scores suitable for “where is X?” discovery (FR-02 illustrative intent: payment retry logic → top files with scores; illustrative top 8). Exact `top_k` bounds are `[NEEDS CLARIFICATION: OQ bounds for top_k]`. Until clarified, System MUST accept `top_k` as a positive integer per api-contract validation notes without inventing min/max as Confirmed.  
  *Source: US-003; FR-02; api-contract §5*

- **FR-007**: Semantic search latency MUST target p95 <800ms for a 500k LOC index (BRD §10).  
  *Source: US-003; BRD §10; ADR-014; constitution IV*

- **FR-008**: Where a quality evaluation harness aligned to BRD success metrics applies, System MUST achieve recall@10 >0.92 for relevant results in top 10 (BRD §12). Harness design/coverage gaps MUST be documented rather than inventing pass evidence.  
  *Source: US-003; BRD §12; constitution IV*

- **FR-009**: FastAPI orchestrator MUST own search and packing orchestration; clients MUST NOT silently bypass backend validation, indexing policy, consent checks, or RBAC (where applicable).  
  *Source: constitution V; ADR-001/002 boundary discipline; US-003 Notes*

- **FR-010**: System MUST consume EP-001 L5 pack and Qdrant index outputs as upstream inputs for hybrid search and packing. Exact pack schema field inventory remains `[NEEDS CLARIFICATION: OQ-PACK]` (Proposed handoff only — do not Confirmed-freeze).  
  *Source: EP-001 open-questions OQ-PACK; EP-001 FR-004; US-003 Dependencies US-001/US-002*

- **FR-011**: System MUST assemble context packs using phase-scoped prompt/pack templates (code2prompt-style) for SDLC phases Requirements, Design, Dev, Test, and Deploy.  
  *Source: US-004; BRD FR-03; §8; §15 MVP basic prompt packing*

- **FR-012**: For the same query and repository, packs assembled under different supported phases MUST differ in composition according to phase scoping.  
  *Source: US-004*

- **FR-013**: Exact phase parameter wire shape on `POST /context` (or related packing API) is `[NEEDS CLARIFICATION: OQ-16]`. Until resolved, System MUST NOT invent a Confirmed request field name/enum beyond the five named phases as product concepts.  
  *Source: US-004; OQ-16; api-contract §2.3 Confirmed request lacks phase field*

- **FR-014**: Full L4 Headroom token-budget enforcement, adaptive summarization product behavior, and compression telemetry dashboards are **out of scope** for EP-002 (V1; ADR-006; US-022). MVP ships basic phase-aware packing without full L4 gate.  
  *Source: US-004 Notes; ADR-006; roadmap*

- **FR-015**: Packed context in successful `POST /context` responses MUST include provenance citations with file:line and confidence as described in BRD §14.  
  *Source: US-015; BRD §14; constitution III*

- **FR-016**: Exact JSON citation schema inside `final_context` is `[NEEDS CLARIFICATION: OQ-11]`. System MUST NOT invent undocumented citation fields as Confirmed requirements.  
  *Source: US-015; OQ-11; api-contract §2.3 Citations note*

- **FR-017**: MVP semantics for `metrics.tokens_before`, `metrics.tokens_after`, and `metrics.saving_percent` are `[NEEDS CLARIFICATION: MVP metric semantics]` — Meaningful with L4 (V1); MVP MAY return packing token counts only (A-06; api-contract §2.3).  
  *Source: A-06; ADR-006; api-contract §2.3*

- **FR-018**: Search and packing MUST operate only over content already permitted by EP-001 ignore/exclusion policy (`.gitignore`, `.env`, secrets, build outputs, dependency folders, binaries). EP-002 MUST NOT re-index excluded content and MUST NOT assume index-time code exfiltration.  
  *Source: constitution III; EP-001 FR-010/FR-011; US-002; Appendix C*

- **FR-019**: CLI `contextos ask` MAY consume the `POST /context` retrieval path as an API consumer (US-003 AC / api-contract §6). Full CLI surface, machine-readable ask schema (OQ-10), and extension DX (Ask ContextOS clicks, Pack Context command UX) are **out of scope** for this Spec Kit.  
  *Source: US-003 AC consumer note; EP-004 boundary; PM scope*

- **FR-020**: Confirmed HTTP status codes for `POST /context` are **Not evidenced**. Proposed mappings (`200`, `400`, `403`, `404`, `413`/`422` budget hard-fail V1, `503` degraded) MAY be used only as Proposed labels until product confirms — MUST NOT be treated as Confirmed contract freeze.  
  *Source: api-contract §2.3*

### Key Entities

- **Context Request**: Logical ask identified by `query`, optional `file` (cursor/file context), `repo`, and `top_k` (Confirmed api-contract fields). Phase selection is a product concept (FR-03) with wire shape `[NEEDS CLARIFICATION: OQ-16]`.
- **Hybrid Search Result**: Ranked files/chunks from BM25 + vector retrieval after MMR, including scores; contributes to `relevant_files` and packing inputs.
- **Phase-Scoped Pack**: Assembled prompt/context using templates scoped to one of Requirements / Design / Dev / Test / Deploy; materializes as `final_context` (packed XML/context string per api-contract).
- **Citation / Provenance**: Reference within packed context including file:line and confidence (BRD §14); exact JSON shape `[NEEDS CLARIFICATION: OQ-11]`.
- **Upstream Pack / Index**: EP-001 LLM-optimized packed representation and Qdrant `codebase` embeddings consumed as inputs; exact pack field inventory `[NEEDS CLARIFICATION: OQ-PACK]` (Proposed only).
- **Context Metrics**: Confirmed response object fields `tokens_before`, `tokens_after`, `saving_percent`, `trace`; MVP meaning `[NEEDS CLARIFICATION]`.

---

## ContextOS Impact *(mandatory for this project)*

### Affected Layers

- **L1 Structural Knowledge Graphs**: N/A as EP-002 deliverable — blast radius / structural expand is V1; `blast_radius` may be empty/null in MVP (**Proposed**).
- **L2 Multi-modal Project Graphs**: N/A — V2.
- **L3 Symbol & LSP Navigation**: N/A as EP-002 deliverable — Serena/L3 owned by EP-003. MVP pipeline may later compose with L3; this Spec Kit does not specify L3 behavior.
- **L4 Context Compression**: N/A as product deliverable — full L4 not MVP gate (ADR-006). Note only: `/context` metrics foreshadow compression; MVP metric semantics open. Phase budgets (FR-11) are V1.
- **L5 Context Packing & Semantic Search**: **Primary** — hybrid BM25 + vector + MMR, phase-aware prompt assembly, provenance citations in packed context.
- **L6 Persistent Agent Memory**: N/A — V2; `memory` may be empty/null earlier (**Proposed**).

### Affected Surfaces

- **FastAPI / API**: **Affected** — owns search and packing; Confirmed `POST /context` (constitution V; api-contract §2.3).
- **CLI**: **Consumer note only** — `contextos ask` may call `POST /context` (US-003 AC; api-contract §6). Full CLI epic (EP-004) out of scope.
- **VS Code Extension**: **Out of scope as primary** for this Spec Kit — may call APIs later; extension DX stories not included (PM scope).
- **Dashboard / Webview / Visualization**: N/A for EP-002 primary acceptance — compression dashboard is L4/V1.
- **GitHub Action / CI**: N/A — Future; out of scope.
- **Qdrant / EP-001 index packs**: **Affected as upstream stores** consumed by search (not re-specified as indexing epic).

### Privacy And Security

- **Repository content handling**: Search/packing MUST respect EP-001 `.gitignore` / `.env` / secret / binary exclusions already applied to packs and embeddings (constitution III). Index path remains local / no external LLM exfil (EP-001 US-002).
- **Consent / exfiltration**: EP-002 search/packing itself retrieves local index content via FastAPI. Query-time external LLM exfiltration consent is owned by US-016 / EP-001 gate — not re-specified here; clients MUST NOT bypass orchestrator consent policy if a later ask path sends packed context externally.
- **RBAC / PII**: RBAC per repo path is a constitution/BRD control; exact RBAC schema Missing Evidence (OQ-01) — **not invented**. PII redaction primary for L2/L6 paths — N/A as primary for EP-002.
- **Source provenance**: MUST preserve file:line + confidence citations on packed context (US-015; BRD §14; constitution III).

---

## Non-Functional Requirements

### Performance

- **NFR-001**: Semantic search p95 <800ms for a 500k LOC index (BRD §10; US-003; ADR-014).
- **NFR-002**: `POST /context` contributes to search p95 and overall ask goals; IDE symbol-accurate context <2s is MVP exit scoped to IDE+L3 composition (BRD §15) — **not** claimed as a CLI-only SLA for EP-002 (US-007 note pattern). Demo explain <8s is POC/demo context (implementation-guidelines) — observational, not invented stricter EP-002 gate.
- **NFR-003**: BO-04 “where is X used?” time-to-answer <5 sec is a business KPI (BRD §12 / BO-04) spanning L1+L2+L5 in full platform; for EP-002 L5 search increment, primary hard NFR remains search p95 <800ms @ 500k LOC — do not invent a separate Confirmed E2E SLA beyond evidenced search NFR without harness definition.

### Security

- **NFR-004**: No assumption of index-time code exfil; consume local Qdrant/packs only (EP-001; Appendix C; constitution III).
- **NFR-005**: Orchestrator enforces ignore/exclusion boundaries already established upstream; EP-002 MUST NOT pack excluded paths from disk bypassing the index policy.
- **NFR-006**: Authn for API is `[NEEDS CLARIFICATION]` (api-contract); local/dev trusted loopback may apply per A-05 — non-blocking for story intent.

### Reliability

- **NFR-007**: Graceful degraded search on partial index is evidenced (BRD §10); primary health/degraded story ownership is US-014 (EP-005). EP-002 SHOULD allow degraded retrieval when possible rather than inventing hard-fail-all discovery behavior.

### Accessibility

- Not evidenced for EP-002 API packing/search flows — **N/A** (`Not evidenced in provided inputs.`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For an indexed repository at 500k LOC reference scale, hybrid BM25 + vector search with MMR returns relevant ranked files with scores via `POST /context` (US-003; FR-02; ADR-014).
- **SC-002**: Semantic search p95 <800ms @ 500k LOC index (BRD §10; US-003).
- **SC-003**: recall@10 >0.92 where the evaluation harness applies (BRD §12; US-003). **Harness gap**: If no evaluation set/harness exists yet, treat as blocked for verification design — do not claim pass without evidence (constitution IV/Verification Gate). Mark `[NEEDS CLARIFICATION: recall harness availability/design]`.
- **SC-004**: Phase-scoped packing for Requirements, Design, Dev, Test, Deploy produces distinct pack composition across phases for the same query/repo (US-004; FR-03). Phase wire shape remains OQ-16.
- **SC-005**: Successful packed `final_context` includes citations with file:line and confidence (US-015; BRD §14). Exact JSON schema remains OQ-11 — success is presence of those citation attributes, not invented field names.
- **SC-006**: `POST /context` returns Confirmed fields `final_context`, `metrics`, `blast_radius`, `memory`, `relevant_files`, `is_real` (api-contract §2.3); MVP emptiness of `blast_radius`/`memory` allowed as Proposed.
- **SC-007**: MVP “Search works” exit contribution satisfied for L5 hybrid retrieval (BRD §15) without requiring full L4 compression product (ADR-006).
- **SC-008**: MVP `metrics` compression-ratio meaning remains `[NEEDS CLARIFICATION]` — do not invent pass thresholds for `saving_percent` in EP-002 (A-06).

---

## Confirmed Facts

- EP-002 includes stories US-003, US-004, US-015 only (backlog epic list; PM scope).
- Business objective: answer “where is X?” with high-recall hybrid search and assemble phase-scoped context packs (BO-01, BO-04).
- Hybrid BM25 + vector over packs with MMR; p95 <800ms @ 500k LOC (FR-02; §10; ADR-014).
- Phase-aware templates for Requirements / Design / Dev / Test / Deploy (FR-03; §8; §15).
- Citations in packed context: file:line + confidence (BRD §14; US-015).
- Confirmed `POST /context` request: `query`, `file`, `repo`, `top_k`; Confirmed response fields listed in api-contract §2.3.
- FastAPI owns search/packing; clients consume API (constitution V).
- Upstream: EP-001 Qdrant embeddings + pack foundation; exact pack schema Proposed (OQ-PACK) — not Confirmed.
- Full L4 compression not MVP gate (ADR-006).
- MVP exit includes “Search works” and basic prompt packing per phase (BRD §15).
- recall@10 >0.92 is BRD §12 L5 success metric (also appears with L4 compression NFR in §10 — EP-002 applies the L5 search quality claim per US-003).

---

## Assumptions

- **A-01** (non-blocking): Git is source of truth; monorepo ≤1M LOC for MVP (BRD §13) — constrains scale applicability of index/search NFRs.
- **A-06** (non-blocking): MVP `/context` may return packing token counts; full compression metrics meaningful at V1 (ADR-006; api-contract §2.3).
- **A-04** (non-blocking): Qdrant available locally or via Docker Compose for POC (BRD; ADR-013) — required upstream for vector half of hybrid search.
- **A-05** (non-blocking): Local/dev API may be trusted loopback until authn is specified (api-contract §1).
- **A-EP002-1** (non-blocking): EP-001 indexing/packing for the target repo has completed sufficiently for search (US-003 dependencies US-001/US-002).
- **A-EP002-2** (non-blocking): CLI ask and extension ask, when present, call the same FastAPI `POST /context` path rather than reimplementing search (constitution V) — consumer note only.
- **A-EP002-3** (blocking for Confirmed pack contract): OQ-PACK remains unresolved; implementation may proceed against Proposed EP-001 pack handoff without freezing Confirmed pack schema fields.

---

## Dependencies

- EP-001 L5 repository packing & local Qdrant embedding index (US-001, US-002) as upstream.
- FastAPI orchestrator (Python 3.11 per approved stack).
- Qdrant `codebase` collection (384-dim local embeddings already produced by EP-001).
- BM25 retrieval capability over packs — storage placement **Missing Evidence** (ADR-014); dependency is behavioral hybrid retrieval, not a Confirmed store product name.
- Confirmed api-contract `POST /context` field set.
- Downstream consumers (not EP-002 deliverables): CLI ask (EP-004), VS Code Ask/Pack Context DX, EP-003 Serena composition, V1 L4 budgets.

---

## Out Of Scope

- Serena / L3 symbol navigation (EP-003).
- L1 blast radius, structural graph, `GET /blast`, `graph.html` (V1).
- L4 Headroom compression product, FR-11 budget enforcement, FR-12 adaptive summarization, FR-13 compression telemetry dashboard (V1; ADR-006 — note only that full L4 is not MVP gate).
- L2 multi-modal graphs and L6 persistent memory (V2).
- Full CLI surface and CLI machine-readable schema freeze (EP-004; OQ-10) — CLI ask may appear only as `POST /context` consumer note.
- Extension DX (Ask ContextOS <3 clicks, Pack Context command UX, auto-index/save triggers) — may call APIs later; not this Spec Kit.
- Re-specification of EP-001 packing/indexing epic (ignore rules, embedding model, `POST /index`).
- Inventing Confirmed pack schema fields (OQ-PACK), citation JSON schema (OQ-11), or phase wire field (OQ-16).
- Confirmed HTTP status-code freeze for `POST /context`.
- Query-time external LLM consent UX (US-016) beyond respecting deny-by-default if a later path would exfiltrate.
- RBAC role/schema design (OQ-01).

---

## Open Questions

| ID | Question | Blocking? | Source |
|----|----------|-----------|--------|
| **OQ-16** | Phase parameter shape for FR-03 templates (how phase is selected on/with `POST /context`) | Non-blocking for story intent; **blocks Confirmed wire freeze** | US-004; backlog OQ-16 |
| **OQ-11** | Citation JSON shape inside `final_context` | Non-blocking for story intent (file:line + confidence required); **blocks Confirmed citation schema freeze** | US-015; backlog OQ-11; api-contract §2.3 |
| **OQ-PACK** | Exact pack schema field inventory (EP-001 Proposed handoff) | Non-blocking for behavioral search/packing; **blocks Confirmed pack contract / schema handoff freeze** | EP-001 open-questions.md |
| **OQ-top_k** | Exact `top_k` bounds (min/max/default) beyond positive integer / FR-02 illustrative top 8 | Non-blocking for story intent; **blocks numeric AC freeze** | US-003 AC; api-contract §5 |
| **OQ-MVP-metrics** | MVP semantics for `metrics.tokens_before` / `tokens_after` / `saving_percent` on `POST /context` | Non-blocking (A-06); **blocks Confirmed MVP metric interpretation** | api-contract §2.3; ADR-006 |
| **OQ-recall-harness** | Evaluation harness / dataset for recall@10 >0.92 measurement | Non-blocking for implementation intent; **blocks verification pass claims** | US-003; BRD §12; constitution IV |
| **OQ-BM25-store** | BM25 storage placement | Non-blocking (ADR-014 Confirmed hybrid decision); design detail Missing Evidence | ADR-014 |
| **OQ-HTTP-/context** | Confirmed HTTP status codes for `POST /context` | Non-blocking (Proposed labels exist) | api-contract §2.3 |
| **OQ-01** | Exact RBAC roles/path/authn schema | Non-blocking for EP-002 MVP search intent; Missing Evidence | constitution III; EP-001 |

**Label rule**: All items above remain **OPEN** with Proposed labels only where architecture offers proposals. Do **not** Confirmed-freeze OQ-11, OQ-16, OQ-PACK, top_k bounds, or MVP metrics semantics in this specification.

---

## Requirement Traceability

| Requirement ID | Source | Evidence |
| -------------- | ------ | -------- |
| FR-001 | US-003; FR-02; ADR-014 | Hybrid BM25 + vector over packs |
| FR-002 | US-003; FR-02; ADR-014 | MMR re-ranking |
| FR-003 | US-003; api-contract §2.3 | Confirmed `POST /context` request fields |
| FR-004 | US-003, US-015; api-contract §2.3 | Confirmed response fields |
| FR-005 | api-contract §2.3; EP-002 scope | MVP meaningful vs empty/null fields |
| FR-006 | US-003; FR-02; api-contract §5 | Ranked files with scores; top_k OQ |
| FR-007 | US-003; BRD §10; ADR-014; constitution IV | p95 <800ms @ 500k LOC |
| FR-008 | US-003; BRD §12; constitution IV | recall@10 >0.92 where harness applies |
| FR-009 | constitution V; US-003 | FastAPI owns search/packing |
| FR-010 | EP-001 OQ-PACK; US-001/US-002 | Consume upstream packs/index; Proposed schema |
| FR-011 | US-004; FR-03; §8; §15 | Phase-scoped templates (5 phases) |
| FR-012 | US-004 | Pack composition differs by phase |
| FR-013 | US-004; OQ-16 | Phase wire shape open |
| FR-014 | US-004 Notes; ADR-006 | L4 product out of MVP gate |
| FR-015 | US-015; BRD §14; constitution III | Citations file:line + confidence |
| FR-016 | US-015; OQ-11 | Citation JSON shape open |
| FR-017 | A-06; ADR-006; api-contract §2.3 | MVP metrics semantics open |
| FR-018 | constitution III; EP-001 | Privacy/ignore inheritance; no index exfil assumption |
| FR-019 | US-003 AC; EP-004 boundary | CLI/extension consumer note only |
| FR-020 | api-contract §2.3 | Status codes Proposed, not Confirmed |

### Acceptance Scenario → Requirement Mapping

| Scenario | Stories | Requirements |
| -------- | ------- | ------------ |
| Hybrid retrieve via `POST /context` / CLI ask consumer | US-003 | FR-001, FR-002, FR-003, FR-004, FR-006, FR-009, FR-010, FR-019 |
| Search p95 <800ms @ 500k LOC | US-003 | FR-007 |
| recall@10 >0.92 where harness applies | US-003 | FR-008 |
| Top-ranked files with scores / top_k OQ | US-003 | FR-006 |
| Phase-scoped templates for 5 phases | US-004 | FR-011, FR-013 |
| Pack composition differs by phase | US-004 | FR-012 |
| No full L4 MVP gate | US-004 | FR-014, FR-017 |
| Citations file:line + confidence | US-015 | FR-015, FR-016 |
| Do not invent citation JSON | US-015 | FR-016 |

---

## Governance Notes

- Constitution Applied: **Yes** (I Evidence-First; II L5 integrity; III privacy/provenance; IV measurable claims; V API/CLI/extension boundaries).
- Layer impact documented (L5 primary).
- Security/privacy documented (inherit EP-001 exclusions; provenance citations).
- Blocking open questions for Confirmed contract freezes are visible; story intent remains plannable under Proposed labels.
- Ready for Plan Generator: **Yes, with open questions carried forward** (do not treat OQ-11 / OQ-16 / OQ-PACK / top_k / MVP metrics as Confirmed).
