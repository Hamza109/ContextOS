# Feature Specification: EP-005 Privacy Defaults, Health & Consent

**Feature Branch**: `feature/ep-005-privacy-health-consent`

**Created**: 2026-07-28

**Status**: Draft

**Input**: User description: "EP-005 — Privacy Defaults, Health & Consent (US-013, US-014 only): protect repository content by default and keep search available under partial failure (Security / DevOps trust for POC)."

**Stories Covered**: US-013, US-014

**Explicitly Out Of This Spec Kit**: US-016 (query-time external LLM consent) — backlog lists under EP-005; deferred per PM brief / this Spec Kit scope.

**Business Objectives**: Security / DevOps trust for POC (privacy defaults + indexer operability); supports BRD §10 Code access & PII and indexer availability NFRs.

**Source Evidence**: BRD §10 Code access & PII / indexer availability; Appendix C; Appendix D `GET /`; FR-01 ignore/exclusion constraints; constitution III & V; ADR-012; api-contract §2.1 / §2.2 ignore side effects; backlog EP-005 + A-07; ep-005-brief. Upstream cite-only: `specs/ep-001-*`, `specs/ep-002-*`, `specs/ep-004-*`.

**Label rule**: Items marked **Proposed** or `[NEEDS CLARIFICATION]` MUST NOT be Confirmed-frozen. Do not invent unsupported APIs, roles, metrics, or test Pass/Fail.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Indexing Ignore Rules & Secret Exclusion (Priority: P1)

As a **Security** stakeholder, I want indexing to respect `.gitignore` and exclude `.env`, secrets, build outputs, dependency folders, and binaries, so that sensitive and useless artifacts are not indexed.

**Why this priority**: Non-negotiable privacy default (constitution III; ADR-012). Trust prerequisite for any indexing/search POC. MVP — P1. Independently valuable once packing/index path (US-001 / EP-001) exists.

**Independent Test**: Index a fixture repository that contains ignored paths (e.g. `.env`, `node_modules`, `dist`, `.git`), secret-like files, build/dependency folders, and binaries; verify those paths are absent from packs and embeddings. Confirm VS Code / CLI clients do not supply or force-index excluded paths around the orchestrator policy.

**Acceptance Scenarios**:

1. **Given** a repository containing ignored paths (e.g. `.env`, `node_modules`, `dist`, `.git`) and binaries, **When** indexing runs via the orchestrated index path (`POST /index`), **Then** those paths are not included in packs/embeddings (US-013; FR-01; Appendix C).
2. **Given** an attempt to index excluded secret material, **When** the indexer walks the tree, **Then** `.env` and secret patterns remain excluded unless explicitly approved (BRD/constitution). Approval workflow / “approved override” UX is **Not evidenced** — `[NEEDS CLARIFICATION: OQ-OVERRIDE]` — **Proposed only**; until clarified, default exclusions MUST remain in force.
3. **Given** constitution V / implementation-guidelines §3 (“Ignore policy applied once”), **When** indexing is triggered from VS Code or CLI, **Then** clients MUST NOT bypass orchestrator ignore policy (US-013 Notes; EP-004 FR-010 cite).
4. **Given** EP-001 already specified ignore/exclusion constraints (EP-001 FR-010..FR-012), **When** this epic is delivered, **Then** EP-005 owns privacy-default acceptance for US-013 without re-specifying L5 packing/embedding product behavior (cite `specs/ep-001-*`).

---

### User Story 2 — Health Endpoint & Graceful Degraded Search (Priority: P1)

As a **DevOps/SRE**, I want a health endpoint reporting pipeline and store status with graceful degraded search on partial index, so that operators can detect failures without total outage of discovery.

**Why this priority**: Supports BRD §10 indexer availability (99.5% uptime target + graceful degraded search). Operability for POC. Independently testable once orchestrator + Qdrant path exist (US-002 / US-003 deps). MVP — P1.

**Independent Test**: With orchestrator running, call Confirmed `GET /` and verify health payload includes pipeline readiness and Qdrant status; Falkor may report absent/unused without failing MVP search (A-07). Induce partial index or partial dependency failure and verify search returns graceful degraded results when degradation is possible rather than hard-failing all discovery.

**Acceptance Scenarios**:

1. **Given** the orchestrator is running, **When** I call `GET /`, **Then** I receive health information including Confirmed fields `status` (`ok | degraded | error`), `pipeline`, `falkor`, and `qdrant` (Appendix D; api-contract §2.1).
2. **Given** MVP without L1 Falkor product usage, **When** health is inspected, **Then** Falkor status MAY report absent/unused without failing MVP search (**A-07**; api-contract MVP note — **Proposed** degraded semantics for Falkor absence).
3. **Given** a partial index or partial dependency failure, **When** search is requested (`POST /context` / hybrid search path owned by EP-002), **Then** the system provides graceful degraded search rather than hard-failing all discovery when degradation is possible (BRD §10; US-014). Exact degraded response shape / operator UX beyond behavioral intent is `[NEEDS CLARIFICATION]` — do not invent Confirmed fields.
4. **Given** HTTP status codes for `GET /` are **Not evidenced** as Confirmed, **When** implementing/verifying health, **Then** status mapping remains **Proposed** only (api-contract §2.1: Proposed `200` healthy/degraded body; `503` if critical deps down) — MUST NOT Confirmed-freeze.

---

### Edge Cases

| Case | Expected / label |
|------|------------------|
| `.gitignore`-matched paths present | Excluded from packs/embeddings (Confirmed intent) |
| `.env` / secret patterns / binaries / build / deps (evidenced examples: `node_modules`, `dist`, `.git`) | Excluded (Confirmed intent); secret-pattern inventory beyond BRD examples may extend in implementation without inventing Confirmed product UX |
| Explicit “approved override” to include excluded secrets | **Not evidenced** — OQ-OVERRIDE; defaults stay enforced |
| Client attempts to upload/index excluded paths | Must not bypass orchestrator policy (constitution V) |
| Falkor absent / unused in MVP | Report presence/absence; do not fail MVP search (A-07) |
| Qdrant unavailable / partial failure | Health reflects degradation; search degrades when possible rather than total discovery outage (BRD §10) |
| Partial index (incomplete embeddings) | Graceful degraded search when possible (US-014); exact UX **Not evidenced** |
| Exact `GET /` / `POST /context` HTTP status mapping | **Proposed** only (api-contract) |
| Auth on `GET /` | **NEEDS CLARIFICATION** (api-contract §2.1) — non-blocking for local POC (A-05) |
| US-016 consent gate | **Out of this Spec Kit** (cite only; EP-001 may carry related FRs historically) |

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST respect `.gitignore` when walking, packing, and indexing a repository.  
  *Source: US-013; BRD FR-01; §10; Appendix C; constitution III; ADR-012*

- **FR-002**: System MUST exclude `.env`, secrets, build outputs, dependency folders (evidenced examples include `node_modules`, `dist`), `.git`, and binary artifacts from packs and embeddings unless explicitly approved.  
  *Source: US-013; FR-01; Appendix C; constitution III; ADR-012*

- **FR-003**: Explicit “approved override” / approval workflow UX to include normally excluded secret material is `[NEEDS CLARIFICATION: OQ-OVERRIDE — Not evidenced]`. Until clarified, System MUST keep default exclusions in force. MUST NOT Confirmed-freeze an override UX.  
  *Source: US-013 Open Questions; constitution III*

- **FR-004**: Ignore / hard-exclusion policy MUST be owned and enforced by the FastAPI orchestrator (security module). VS Code extension and CLI MUST be thin clients and MUST NOT silently bypass orchestrator ignore policy (including “helpfully” uploading excluded paths).  
  *Source: US-013 Notes; constitution V; implementation-guidelines §3; ADR-002; EP-004 FR-010 cite*

- **FR-005**: Indexing privacy defaults apply on the confirmed `POST /index` path and any orchestrated pack/walk used for L5 indexing. This epic MUST NOT re-specify EP-001 packing/embedding product requirements (cite `specs/ep-001-*`).  
  *Source: US-013 Dependencies US-001; EP-001; api-contract §2.2 side effects*

- **FR-006**: System MUST expose Confirmed health endpoint `GET /` returning fields `status` (`ok | degraded | error`), `pipeline`, `falkor`, and `qdrant`.  
  *Source: US-014; BRD Appendix D; api-contract §2.1*

- **FR-007**: Health MUST report pipeline readiness and Qdrant connectivity status. Falkor MAY report absent/unused in MVP without failing MVP search (**A-07**).  
  *Source: US-014; A-07; api-contract §2.1 MVP note*

- **FR-008**: Exact HTTP status-code mapping for `GET /` is **Not evidenced** as Confirmed. Proposed mapping (`200` for healthy/degraded body; `503` if critical deps down) MAY be used only as **Proposed** until product confirms — MUST NOT Confirmed-freeze. Auth on `GET /` remains `[NEEDS CLARIFICATION]` (api-contract).  
  *Source: US-014 Open Questions; api-contract §2.1*

- **FR-009**: Given partial index or partial dependency failure, System MUST provide graceful degraded search rather than hard-failing all discovery when degradation is possible (BRD §10). Hybrid search product behavior remains owned by EP-002 — this epic owns degradation/operability acceptance, not re-specification of BM25/vector/MMR.  
  *Source: US-014; BRD §10; EP-002 cite; Dependencies US-002, US-003*

- **FR-010**: Exact degraded-search response shape, operator-facing copy, and Confirmed `POST /context` status codes (including Proposed `503` degraded) are `[NEEDS CLARIFICATION]` / **Proposed** per api-contract — MUST NOT invent Confirmed fields or freeze status codes.  
  *Source: api-contract §2.3; US-014; EP-002 FR-020 cite*

- **FR-011**: Query-time external LLM consent (US-016), full RBAC/enterprise consent schemas, JetBrains, L1/L4 (V1), L2/L6 (V2), and EP-004 surface rebuild are **out of scope** for this Spec Kit. Index-time no-exfil to external LLMs remains a constitution III / EP-001 constraint (cite only).  
  *Source: ep-005-brief; ADR-012 RBAC Missing Evidence; roadmap; constitution III*

### Key Entities

| Entity | Conceptual attributes |
|--------|----------------------|
| **Ignore Policy** | Orchestrator-owned rules: `.gitignore` respect + hard exclusions (`.env`/secrets/build/deps/binaries). No Confirmed override entity until OQ-OVERRIDE. |
| **Allowed File Set** | Files eligible for pack/embed after policy walk (docs cite: `IgnorePolicy`, `walk_allowed_files`). |
| **Health Report** | `status`, `pipeline`, `falkor`, `qdrant` (Confirmed field names from Appendix D / api-contract §2.1). |
| **Degraded Search Result** | Behavioral: partial/available discovery under partial failure; machine shape **Not evidenced** as Confirmed. |
| **Index Request** | Upstream EP-001: `repo_path`, `repo_name` via `POST /index` — cited, not re-specified. |

---

## ContextOS Impact *(mandatory for this project)*

### Affected Layers

| Layer | Impact |
|-------|--------|
| **L1** | N/A as deliverable — V1; Falkor health reporting only (presence/absence). |
| **L2** | N/A — V2. |
| **L3** | N/A as primary — cite only that symbol paths MUST reuse orchestrator ignore policy (no second ignore engine). |
| **L4** | N/A — V1. |
| **L5** | **Affected** — ignore/exclusion on pack/index walk; degraded search operability over EP-002 hybrid retrieval (cite, don’t re-spec search/MMR). |
| **L6** | N/A — V2; PII redaction primary for L2/L6 (ADR-012) — not this epic’s product. |

### Affected Surfaces

| Surface | Impact |
|---------|--------|
| **FastAPI / API** | **Primary** — `GET /` health; ignore policy on index/pack; degraded search orchestration hooks. |
| **CLI** | Thin consumer — MUST NOT bypass ignore policy (EP-004 cite; no CLI rebuild). |
| **VS Code Extension** | Thin consumer — MUST NOT bypass ignore policy; may surface health/offline states as DX without owning policy. |
| **Dashboard / Webview** | N/A as primary acceptance for this Spec Kit. |
| **GitHub Action / CI** | N/A — Future. |

### Privacy And Security

| Topic | Requirement |
|-------|-------------|
| **Repository content** | `.gitignore` + `.env`/secrets/build/deps/binaries excluded (constitution III; US-013). |
| **Override** | Not evidenced — OQ-OVERRIDE; defaults enforced. |
| **Consent / exfil** | Index-time: no code to external LLM (cite EP-001 / Appendix C). Query-time LLM consent = **US-016 out of scope** here. |
| **RBAC / PII** | RBAC schema Missing Evidence (OQ-01; ADR-012) — **not invented**. PII redaction L2/L6 — N/A primary. |
| **Client boundary** | No silent bypass of indexing policy (constitution V). |
| **Provenance** | Not primary deliverable (US-015 / EP-002 cite). |

---

## Non-Functional Requirements

### Performance

- Search p95 &lt;800ms @ 500k LOC remains EP-002 ownership — **not** re-gated here.
- Indexing time SLAs remain EP-001 ownership — cite only.

### Security

- **NFR-001**: Orchestrator-enforced ignore/exclusion policy (constitution III; ADR-012 Confirmed controls).
- **NFR-002**: Clients MUST NOT bypass ignore policy (constitution V; implementation-guidelines §3).
- **NFR-003**: No Confirmed override path until OQ-OVERRIDE resolved.
- **NFR-004**: Authn/RBAC schemas remain Missing Evidence (OQ-01; A-05) — non-blocking for local health/index privacy defaults.

### Reliability

- **NFR-005**: Indexer availability target **99.5% uptime** (BRD §10) — measurable outcome for this epic; measurement method/harness `[NEEDS CLARIFICATION: OQ-Uptime-Harness]` — do not claim Pass without evidence (constitution IV / Verification Gate).
- **NFR-006**: Graceful degraded search on partial index / partial dependency failure when degradation is possible (BRD §10; US-014).
- **NFR-007**: Falkor unused/absent MUST NOT alone fail MVP search (A-07).

### Accessibility

- Not evidenced for health/privacy operator flows — **N/A** (`Not evidenced in provided inputs.`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

| ID | Outcome | Notes |
|----|---------|-------|
| **SC-001** | Ignored/excluded paths (`.gitignore`, `.env`, secrets, build/deps, binaries, evidenced `node_modules`/`dist`/`.git`) absent from packs/embeddings after index | US-013 |
| **SC-002** | Default exclusions remain in force; no Confirmed override UX shipped as required | OQ-OVERRIDE open |
| **SC-003** | VS Code / CLI cannot bypass orchestrator ignore policy (boundary review / negative tests) | constitution V |
| **SC-004** | `GET /` returns Confirmed fields `status`, `pipeline`, `falkor`, `qdrant` | US-014; Appendix D |
| **SC-005** | Falkor absent/unused does not alone fail MVP search | A-07 |
| **SC-006** | Under partial index/dependency failure, search degrades gracefully when possible (not total discovery hard-fail) | BRD §10; US-014 |
| **SC-007** | Indexer availability advances toward **99.5%** uptime target | Harness `[NEEDS CLARIFICATION: OQ-Uptime-Harness]` — no Pass claim without method + evidence |
| **SC-008** | HTTP status mappings for health/degraded remain labeled **Proposed** until product Confirms | api-contract §2.1/§2.3 |

---

## Confirmed Facts

| Fact | Evidence |
|------|----------|
| This Spec Kit covers **US-013, US-014 only**; US-016 out | ep-005-brief; backlog EP-005 story list vs PM scope |
| Privacy defaults: `.gitignore`; ignore `.env`/secrets/build/deps/binaries | BRD §10; Appendix C; constitution III; ADR-012 |
| Clients must not bypass orchestrator ignore policy | US-013 Notes; constitution V |
| Confirmed `GET /` fields: `status`, `pipeline`, `falkor`, `qdrant` | Appendix D; api-contract §2.1 |
| Indexer availability: 99.5% uptime; graceful degraded search on partial index | BRD §10 |
| Falkor unused/absent OK for MVP search | A-07; api-contract MVP note |
| ADR-012 privacy controls Confirmed; RBAC schema Missing Evidence | architecture-decisions.md |
| FastAPI owns policy/health; clients thin | constitution V; ADR-002 |
| Existing code cites (docs-first OK): `services/orchestrator/app/security/ignore_policy.py`, `adapters/fs_walker.py`, `api/health.py`, `api/index.py`, `services/l5_index.py`, `l5_pack.py`, `l5_search.py`; clients under `clients/vscode/`, `clients/cli/` | ep-005-brief; codebase |
| Upstream EP-001 ignore foundation; EP-002 hybrid search; EP-004 thin clients — cite, don’t re-spec | specs/ep-001-*, ep-002-*, ep-004-* |

---

## Assumptions

| ID | Assumption | Blocking? | Source |
|----|------------|-----------|--------|
| **A-07** | Falkor may be unused/absent in MVP health without failing search | Non-blocking | backlog; api-contract §2.1 |
| **A-05** | Local/dev API may be trusted loopback until authn specified | Non-blocking | backlog; api-contract |
| **A-EP005-1** | EP-001 pack/index path (`POST /index`) available for ignore-policy enforcement | Non-blocking | US-013 deps US-001 |
| **A-EP005-2** | EP-002 hybrid search (`POST /context`) available as degradation target | Non-blocking | US-014 deps US-002/US-003 |
| **A-EP005-3** | EP-004 clients remain thin; no surface rebuild in this epic | Non-blocking | ep-005-brief |
| **A-EP005-4** | OQ-OVERRIDE unresolved — implementation keeps defaults; override UX not Confirmed | Blocking for Confirmed override product | US-013 OQ |
| **A-EP005-5** | Exact health/search HTTP status mapping Proposed only | Blocking for Confirmed status-code freeze | US-014 OQ; api-contract |
| **A-EP005-6** | 99.5% uptime harness not specified — Pass claims blocked until method agreed | Blocking for SC-007 Pass claims | constitution IV |

---

## Dependencies

| Dependency | Role |
|------------|------|
| EP-001 (`specs/ep-001-*`) | Pack/index foundation; prior ignore FR cite; index-time no-exfil |
| EP-002 (`specs/ep-002-*`) | Hybrid search / `POST /context` — degradation builds on |
| EP-004 (`specs/ep-004-*`) | Thin CLI/VS Code — must not bypass policy |
| FastAPI orchestrator | Policy + health owner |
| Qdrant | Health + search dependency |
| FalkorDB | Health report only in MVP (unused OK) |
| `.gitignore` + hard-exclusion sets | Policy inputs |

---

## Out Of Scope

- **US-016** query-time external LLM consent gate (even though backlog lists under EP-005)
- Inventing Confirmed “approved override” UX (OQ-OVERRIDE)
- Full RBAC / enterprise authn schemas (OQ-01; ADR-012 open)
- Re-specifying L5 hybrid BM25/vector/MMR, phase packing, citations (EP-002)
- Re-specifying L3 Serena product (EP-003)
- EP-004 CLI/Ask surface rebuild
- L1 blast / Falkor product, L4 compression, L2/L6 (V1/V2)
- JetBrains, GitHub Action, SIP/marketplace
- Inventing Confirmed HTTP status codes or degraded payload schemas
- Inventing Pass/Fail evidence or unsupported numeric targets beyond BRD-cited 99.5%

---

## Open Questions

| ID | Question | Blocking? | Source |
|----|----------|-----------|--------|
| **OQ-OVERRIDE** | Explicit “approved override” UX / workflow to include excluded secrets | Non-blocking for default exclusions; **blocks Confirmed override product** | US-013 |
| **OQ-HTTP-Health** | Exact HTTP status mapping for `GET /` (Proposed `200`/`503`) | Non-blocking for field payload; **blocks Confirmed status freeze** | US-014; api-contract §2.1 |
| **OQ-Degraded-Shape** | Exact degraded-search response / operator UX fields | Non-blocking for behavioral graceful degrade; **blocks Confirmed schema freeze** | US-014; BRD §10 |
| **OQ-Uptime-Harness** | Measurement method for 99.5% indexer availability | Non-blocking for story intent; **blocks SC-007 Pass claims** | BRD §10; constitution IV |
| **OQ-Health-Auth** | Auth requirement on `GET /` | Non-blocking for local POC (A-05) | api-contract §2.1 |
| **OQ-01** | Exact RBAC roles/path/authn schema | Non-blocking for this epic’s ignore/health intent; Missing Evidence | ADR-012; backlog |
| **US-016** | Consent UX/storage (deferred Spec Kit) | Out of scope here; remains open product-wide | backlog US-016 |

**Label rule**: OQ-OVERRIDE, HTTP status mappings, degraded shape, and uptime harness remain **Proposed / open**. Do **not** Confirmed-freeze them in this specification.

---

## Requirement Traceability

| Requirement ID | Source | Evidence |
| -------------- | ------ | -------- |
| FR-001 | US-013; FR-01; constitution III; ADR-012 | `.gitignore` respect |
| FR-002 | US-013; Appendix C; constitution III | `.env`/secrets/build/deps/binaries |
| FR-003 | US-013 OQ; constitution III | Override Not evidenced; defaults force |
| FR-004 | US-013 Notes; constitution V; impl-guidelines §3 | Orchestrator owns; clients no bypass |
| FR-005 | US-013 ↔ EP-001 | Cite pack/index; don’t re-spec L5 product |
| FR-006 | US-014; Appendix D; api-contract §2.1 | `GET /` Confirmed fields |
| FR-007 | US-014; A-07 | Pipeline + Qdrant; Falkor unused OK |
| FR-008 | US-014 OQ; api-contract §2.1 | Status codes Proposed only |
| FR-009 | US-014; BRD §10; EP-002 cite | Graceful degraded search |
| FR-010 | api-contract §2.3; US-014 | Degraded shape / status Proposed |
| FR-011 | ep-005-brief; roadmap | Explicit OOS incl. US-016 |

### Acceptance Scenario → Requirement Mapping

| Scenario | Story | Requirements |
| -------- | ----- | ------------ |
| Ignored/excluded paths not in packs/embeddings | US-013 | FR-001, FR-002, FR-005 |
| Secrets stay excluded; no Confirmed override | US-013 | FR-002, FR-003 |
| Clients cannot bypass ignore policy | US-013 | FR-004 |
| `GET /` health fields incl. pipeline + Qdrant | US-014 | FR-006, FR-007 |
| Falkor unused without failing MVP search | US-014 | FR-007 |
| Graceful degraded search on partial failure | US-014 | FR-009, FR-010 |
| HTTP status mapping stays Proposed | US-014 | FR-008, FR-010 |
| US-016 / RBAC / layer rebuild out of scope | brief | FR-011 |

---

## Code / Artifact Citations (non-normative)

| Path | Relevance |
|------|-----------|
| `services/orchestrator/app/security/ignore_policy.py` | `IgnorePolicy` — orchestrator ignore/hard-exclusion |
| `services/orchestrator/app/adapters/fs_walker.py` | `walk_allowed_files` |
| `services/orchestrator/app/api/health.py` | `GET /` health |
| `services/orchestrator/app/api/index.py` | Index entry; must apply policy |
| `services/orchestrator/app/services/l5_index.py` / `l5_pack.py` | Index/pack consumers of policy |
| `services/orchestrator/app/services/l5_search.py` | Degraded/partial search hooks (cite; EP-002 owns hybrid product) |
| `clients/vscode/`, `clients/cli/` | Thin clients — no policy bypass |
| Tests (examples): `test_ignore_policy.py`, `test_packer_exclusions.py`, `test_index_exclusions_qdrant.py` | Verification cites for plan/tasks |

---

## Governance Notes

- Constitution Applied: **Yes** (I Evidence-First; II layer integrity via L5 cite-only for search; III privacy defaults; IV measurable 99.5% with open harness; V FastAPI policy/health ownership, thin clients).
- Layer/surface impact documented; security/privacy documented; US-016 explicitly out.
- Blocking items for override UX, HTTP freeze, degraded schema, and uptime Pass claims are visible; story intent remains plannable under Proposed labels.
- Ready for Plan Generator: **Yes, with open questions carried forward** — especially OQ-OVERRIDE, OQ-HTTP-Health, OQ-Degraded-Shape, OQ-Uptime-Harness. Do not treat those as Confirmed.
