# Implementation Plan: EP-005 Privacy Defaults, Health & Consent

**Branch**: `feature/ep-005-privacy-health-consent` | **Date**: 2026-07-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/ep-005-privacy-health-consent/spec.md`

**Stories**: US-013, US-014 only (US-016 **OOS**)

---

## Summary

EP-005 owns **privacy-default acceptance** (US-013) and **indexer operability** (US-014): orchestrator-enforced `.gitignore` + hard exclusions on pack/index, Confirmed `GET /` health (pipeline + Qdrant; Falkor unused OK per **A-07**), and **graceful degraded search** under partial index/dependency failure — without rebuilding L5 packing/search (EP-001/EP-002) or client surfaces (EP-004).

**Approach**: Gap-fill and acceptance-harden existing code. Do **not** invent Confirmed override UX, HTTP status freezes, degraded payload schemas, or 99.5% Pass claims.

---

## Technical Context

| Field | Value | Label |
|-------|-------|-------|
| Language/Version | Python 3.11 (orchestrator); TypeScript clients (thin) | Confirmed stack |
| Primary Dependencies | FastAPI; Qdrant; existing `IgnorePolicy` / L5 index+search | Confirmed |
| Storage | Qdrant `codebase` (health + search); Falkor report-only MVP | Confirmed; A-07 |
| Testing | pytest under `services/orchestrator/tests/`; client boundary/negative tests **Proposed** where missing | Proposed runners as needed |
| Target Platform | Local/VPC Docker Compose POC; loopback API (A-05) | Confirmed |
| Project Type | Orchestrator gap-fill + acceptance; thin client boundary review | — |
| Performance Goals | Search p95 / index SLAs remain EP-002 / EP-001 — **not** re-gated | Cite only |
| Constraints | Constitution III/V; ADR-012; no Confirmed freeze of open OQs; no US-016 / RBAC invent | — |
| Scale/Scope | US-013 + US-014 only | — |

---

## ContextOS Technical Impact

| Layer | Impact |
|-------|--------|
| L1 | N/A deliverable — Falkor **presence/absence** in health only (A-07) |
| L2 / L4 / L6 | N/A (V1/V2) |
| L3 | Cite only: reuse orchestrator `IgnorePolicy` — no second ignore engine |
| **L5** | **Affected** — ignore on pack/index walk; degraded-search **operability** over EP-002 hybrid (cite, don’t re-spec BM25/vector/MMR) |

| Surface | Impact |
|---------|--------|
| **FastAPI** | **Primary** — policy + `GET /` + degradation hooks |
| CLI / VS Code | Thin; **MUST NOT** bypass ignore (EP-004 cite; no rebuild) |
| Dashboard / GHA / JetBrains | N/A |

**Privacy / Security**: Constitution III defaults; no Confirmed override (OQ-OVERRIDE); RBAC Missing Evidence (ADR-012) — not invented; US-016 OOS.

**Observability**: Health + existing search degrade notes; 99.5% uptime measurement harness **open** (OQ-Uptime-Harness).

**Measurable claims this epic**: SC-001..SC-006, SC-008; SC-007 advances toward 99.5% **without Pass** until harness agreed.

---

## Constitution Check

| Gate | Status | Evidence / mitigation |
|------|--------|----------------------|
| I Evidence-First | Pass | Cite FR/SC; Proposed OQs not frozen |
| II Layer integrity | Pass | L5 cite EP-001/002; no L1/L4/L2/L6 product |
| III Privacy | Pass | Defaults enforced; override Not evidenced |
| IV Measurable claims | Pass w/ caveat | SC-007 blocked on OQ-Uptime-Harness |
| V Client boundaries | Pass | FastAPI owns policy/health; clients thin |

**Re-check after design**: Same — gap-fill only; no new Confirmed contracts.

---

## Project Structure

### Documentation (this feature)

```text
specs/ep-005-privacy-health-consent/
├── spec.md   # approved
├── plan.md   # this file
├── tasks.md  # next (task-generator)
└── validation-report.md  # after triad
```

Lean Spec Kit only — no quickstart / open-questions / out-of-scope adjunct files.

### Source (gap-fill targets — Confirmed present)

```text
services/orchestrator/app/
├── security/ignore_policy.py      # IgnorePolicy — US-013 core
├── adapters/fs_walker.py          # walk_allowed_files
├── api/health.py                  # GET /
├── api/index.py + services/l5_index.py / l5_pack.py
├── api/context.py + services/l5_search.py  # degrade hooks (EP-002)
clients/vscode/src/api/indexClient.ts      # thin POST /index
clients/cli/                               # thin; no local ignore engine
services/orchestrator/tests/
├── unit/test_ignore_policy.py
├── unit/test_packer_exclusions.py
├── unit/test_fs_walker.py
├── integration/test_index_exclusions_qdrant.py
├── integration/test_context_exclusions.py
└── integration/test_context_degraded.py
```

**Structure Decision**: Reuse EP-001/002 layout; EP-005 adds/extends tests and small gap-fills only.

---

## Complexity Tracking

None — no constitution violations; complexity is acceptance/gap-fill, not new subsystems.

---

## Gap Analysis (vs existing code)

| Area | Evidence (exists) | Gap for EP-005 | Action |
|------|-------------------|----------------|--------|
| `.gitignore` + hard exclusions | `IgnorePolicy`, `walk_allowed_files`, pack/index apply policy; scoped `paths`/`files` filtered **after** allow-list | US-013 **acceptance ownership**; fixture e2e for packs **and** embeddings; secret-glob inventory may extend without inventing override UX | Harden tests / minor policy fixes only |
| Override UX | Docstring: no override until OQ-OVERRIDE | Must stay **Proposed**; defaults force (FR-003) | Do **not** ship Confirmed override |
| Client no-bypass | VS Code `indexClient` / CLI call orchestrator only; comments cite FR-010 | Explicit **negative/boundary** review + tests that clients don’t invent local pack/upload of excluded paths | Review + tests; no DX rebuild |
| `GET /` fields | `health.py` returns `status`, `pipeline`, `falkor`, `qdrant` | Dedicated contract/unit tests sparse; always HTTP 200 today | Add contract tests; status codes stay **Proposed** (OQ-HTTP-Health) |
| Falkor unused | `falkor: "unused"`; status `ok` when Qdrant ok | Align acceptance with A-07 / SC-005 | Verify search not failed by Falkor alone |
| Degraded search | `hybrid_search` `degraded` + `trace_notes`; `context.py` prefers partial; `test_context_degraded.py` | Exact response shape / when to `503` vs `200` **Proposed** (OQ-Degraded-Shape); strengthen partial-index / Qdrant-down cases | Behavioral harden; **no** Confirmed schema invent |
| 99.5% uptime | BRD §10 target | Harness Missing Evidence | Track only; block SC-007 Pass (OQ-Uptime-Harness) |

---

## Technical Approach

### Confirmed

- Orchestrator owns ignore + health (constitution V; ADR-012 privacy controls).
- `GET /` field names: `status` (`ok|degraded|error`), `pipeline`, `falkor`, `qdrant` (api-contract §2.1).
- Index path: `POST /index` → `IgnorePolicy` → walk → pack/embed (EP-001 cite).
- Search path: `POST /context` hybrid owned by EP-002; EP-005 owns degrade/operability acceptance.
- Clients thin; no silent bypass of indexing policy.

### Proposed (do not Confirmed-freeze)

- HTTP: `GET /` → `200` healthy/degraded body; `503` if critical deps down (OQ-HTTP-Health).
- `POST /context` Proposed `503` when discovery impossible; else `200` with **Proposed** `metrics.trace.degraded` / `notes` (OQ-Degraded-Shape) — fields already used in code remain **Proposed**, not Appendix D Confirmed.
- Optional VS Code health/offline DX surfacing — not primary acceptance.
- Uptime measurement method (OQ-Uptime-Harness).

### Missing Evidence

- Approved-override product (OQ-OVERRIDE).
- Auth on `GET /` (OQ-Health-Auth); RBAC schema (OQ-01).
- Confirmed degraded machine schema beyond behavioral intent.

---

## Architecture Impact

| Area | Impact |
|------|--------|
| Frontend / Webview | N/A primary — optional health DX only |
| Backend | Gap-fill `health.py`, policy edges, context degrade paths |
| Database | No new stores; Qdrant health probe reuse |
| Infrastructure | Compose as today; Falkor may be absent |
| AI | No new models; no index-time LLM exfil (cite EP-001) |

---

## Components

| Component | Change type |
|-----------|-------------|
| `ignore_policy.py` / `fs_walker.py` | Gap-fill only if acceptance fails |
| `l5_index.py` / `l5_pack.py` | Verify policy on full + scoped index |
| `health.py` | Ensure Confirmed fields + A-07 semantics; Proposed status codes only |
| `l5_search.py` / `context.py` | Operability acceptance; no hybrid rebuild |
| VS Code / CLI | Boundary review + negative tests; no rebuild |
| Tests | Extend unit/integration/contract for SC-001..SC-006, SC-008 |

---

## Data Model Changes

None required for Confirmed product entities. No Confirmed override entity. Health / degrade shapes stay within existing dict/trace **Proposed** fields.

---

## API Design

| Endpoint | Plan |
|----------|------|
| `GET /` | Keep Confirmed body fields; document Proposed HTTP mapping only (FR-006..FR-008) |
| `POST /index` | Cite EP-001; enforce ignore (FR-001, FR-002, FR-005); no new Confirmed fields |
| `POST /context` | Cite EP-002; graceful degrade when possible (FR-009); shape/status **Proposed** (FR-010) |

No new Confirmed endpoints (ADR-009).

---

## UI / UX Changes

N/A as primary acceptance. Clients may show offline/health DX without owning policy. No Confirmed override UX. No dashboard/Webview requirement for this Spec Kit.

---

## Security Considerations

| Topic | Plan |
|-------|------|
| Authn | A-05 loopback OK; OQ-Health-Auth open |
| Authorization / RBAC | Not invented (ADR-012 Missing Evidence) |
| Ignore enforcement | Single orchestrator module; scoped index must not reintroduce excluded paths |
| Sensitive data | Defaults force; OQ-OVERRIDE open |
| Secrets | No secrets in repo; clients don’t upload excluded content |
| Risks | Client “helpful” upload; Incomplete gitignore edge cases; Over-claiming 99.5% / Confirmed HTTP |

---

## Performance Considerations

No new latency SLAs. Degrade path should prefer partial results over total discovery outage when any modality remains usable. Search p95 remains EP-002 ownership.

---

## Testing Strategy

### Unit

- `IgnorePolicy` / walker: `.gitignore`, `.env`/secrets, build/deps, binaries (FR-001, FR-002).
- Health payload field presence + Falkor unused → not alone `error` for MVP search readiness (FR-006, FR-007).

### Integration

- Fixture repo → `POST /index` → excluded paths absent from pack + Qdrant payloads (SC-001; existing `test_index_exclusions_qdrant` / packer tests — extend as needed).
- Partial failure → `POST /context` returns usable degraded discovery when possible (SC-006; extend `test_context_degraded`).
- Qdrant down / pack miss: assert behavioral degrade vs hard-fail-all; HTTP codes labeled Proposed in assertions comments.

### Client / boundary

- VS Code / CLI: no local ignore engine; index/ask only via orchestrator (SC-003 / FR-004). Negative static or unit checks as **Proposed**.

### Acceptance

- Map to SC-001..SC-006, SC-008. **SC-007**: document blocked until OQ-Uptime-Harness.

### Regression

- EP-001 exclusion tests; EP-002 hybrid happy path still works when healthy.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Treat existing degrade `trace` fields as Confirmed | Contract drift | Keep OQ-Degraded-Shape Proposed |
| Ship override UX | Constitution III violation | Block on OQ-OVERRIDE |
| Claim 99.5% Pass without harness | Verification Gate fail | OQ-Uptime-Harness |
| Rebuild L5/CLI | Scope creep | Cite EP-001/002/004; gap-fill only |
| gitignore negation edge incomplete | False include/exclude | Fix only if SC-001 fails; no full git engine invent |

---

## Dependencies

| Dep | Role |
|-----|------|
| EP-001 | Pack/index + ignore foundation |
| EP-002 | Hybrid `POST /context` |
| EP-004 | Thin clients — no bypass |
| Qdrant | Health + search |
| FalkorDB | Health report only (unused OK) |

---

## Implementation Phases

1. **Foundation** — Inventory + gap matrix vs cited modules/tests (this plan).
2. **US-013 (P1)** — Policy acceptance: fixture exclusions in packs/embeddings; no override; client no-bypass review/tests.
3. **US-014 (P1)** — Health contract tests (Confirmed fields + A-07); degrade operability tests; Proposed HTTP/shape labels preserved.
4. **Polish** — OpenAPI descriptions stay Proposed where open; no SC-007 Pass; docs cite only.

---

## Evidence Reviewed

- `specs/ep-005-privacy-health-consent/spec.md`
- `.cursor/agent-handoffs/ep-005-brief.md`; latest plan-generator handoff
- `.specify/memory/constitution.md` (III, V); `.specify/templates/plan-template.md`
- `docs/backlog/user-stories.md` (EP-005, US-013, US-014, A-07)
- `docs/architecture/api-contract.md` §2.1 / index ignore side effects / §2.3 Proposed codes
- ADR-012; `tech-stack.md`; `implementation-guidelines.md` §3 ignore-once
- Code: `ignore_policy.py`, `fs_walker.py`, `health.py`, `index.py`, `l5_index.py`, `l5_pack.py`, `l5_search.py`, `context.py`
- Clients: `clients/vscode/src/api/indexClient.ts`, CLI ask/context clients
- Tests: `test_ignore_policy`, `test_packer_exclusions`, `test_index_exclusions_qdrant`, `test_context_degraded`, `test_fs_walker`
- Cite-only: `specs/ep-001-*`, `ep-002-*`, `ep-004-*`

---

## Planning Assumptions

| ID | Assumption | Blocking? |
|----|------------|-----------|
| A-07 | Falkor unused/absent OK for MVP search | No |
| A-05 | Local loopback trusted until authn | No |
| A-EP005-1..3 | EP-001/002/004 available; no client rebuild | No |
| A-EP005-4 | OQ-OVERRIDE unresolved — defaults only | Blocks Confirmed override |
| A-EP005-5 | Health/search HTTP mapping Proposed | Blocks status freeze |
| A-EP005-6 | No uptime harness → no SC-007 Pass | Blocks Pass claim |
| P-1 | Existing `metrics.trace.degraded`/`notes` remain Proposed observability, not Appendix D Confirmed | No |

---

## Open Questions (carry-forward — Proposed)

| ID | Blocking for |
|----|----------------|
| **OQ-OVERRIDE** | Confirmed override product |
| **OQ-HTTP-Health** | Confirmed `GET /` status-code freeze |
| **OQ-Degraded-Shape** | Confirmed degrade schema / UX freeze |
| **OQ-Uptime-Harness** | SC-007 Pass claims |
| OQ-Health-Auth | Auth on `GET /` (non-blocking POC) |
| OQ-01 | RBAC schema (not this epic’s invent) |
| US-016 | Deferred Spec Kit |

---

## Requirement Coverage Matrix

| Requirement ID | Planned Implementation | Evidence | Status |
| -------------- | ---------------------- | -------- | ------ |
| FR-001 | Keep/fix `IgnorePolicy` gitignore on walk/pack/index | `ignore_policy.py`, walker | Gap-fill + accept |
| FR-002 | Hard exclusions + secret/binary globs | same + packer tests | Gap-fill + accept |
| FR-003 | No override path | OQ-OVERRIDE | Proposed open |
| FR-004 | Client boundary review/tests | vscode/cli thin clients | Gap-fill |
| FR-005 | Enforce on `POST /index` / L5 pack; cite EP-001 | `l5_index`/`l5_pack` | Cite + accept |
| FR-006 | `GET /` Confirmed fields | `health.py` | Contract tests |
| FR-007 | Pipeline + Qdrant; Falkor unused OK | `health.py`; A-07 | Accept |
| FR-008 | HTTP mapping Proposed only | api-contract §2.1 | Proposed |
| FR-009 | Degrade when possible via EP-002 path | `l5_search`/`context` | Accept + extend tests |
| FR-010 | Degraded shape/status Proposed | OQ-Degraded-Shape | Proposed |
| FR-011 | OOS: US-016, RBAC invent, L1/L4/L2/L6, JetBrains, EP-004 rebuild | brief | Out of scope |

---

## Ready for Task Generator

**Yes** — with Proposed OQs carried; no Confirmed freeze of override / HTTP / degrade schema / uptime Pass.
