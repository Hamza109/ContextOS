# Open Questions — EP-001 L5 Repository Packing & Indexing
# Status: unresolved unless product confirms. Do NOT treat Proposed paths as Confirmed.

Last updated: 2026-07-27 (backend-agent discovery notes)

---

## OQ-PACKER — Concrete Repomix package vs in-house adapter

| Field | Value |
|-------|-------|
| Status | **Unresolved** — clarification requested |
| Blocking? | Non-blocking if FR-01 behavioral requirements met |
| Decision for EP-001 MVP | **Proposed**: in-house Repomix-style adapter (`services/orchestrator/app/services/l5_pack.py`) matching FR-01 XML-oriented pack, token pre-calc, binary skip |
| Not Confirmed | No specific Repomix npm/PyPI package is Confirmed-pinned in contracts |
| Rationale | Constitution/tech-stack require Repomix-*style* packing; concrete package pin is Missing Evidence. In-house adapter satisfies FR-001/002/003 without inventing a Confirmed dependency. |

---

## OQ-14 — Incremental delta index API beyond confirmed `POST /index`

| Field | Value |
|-------|-------|
| Status | **Unresolved** — **blocks US-012 OpenAPI / Confirmed contract freeze** |
| Proposed path (implementation only) | Reuse confirmed `POST /index` with **optional** narrower-scope fields (e.g. `paths`, `files`) labeled **Proposed** in OpenAPI descriptions — not Appendix D Confirmed |
| Forbidden | Inventing new Confirmed endpoints without ADR/product confirmation (ADR-009) |
| Discovery record (T058) | Product has not confirmed; backend ships Proposed optional fields only |

---

## OQ-US016 — Consent UX and storage mechanism

| Field | Value |
|-------|-------|
| Status | **Unresolved** — **blocks consent UX/storage/CRUD implementation** |
| Shipped for EP-001 | Deny-by-default gate only (`consent_gate.py`) when consent/configuration absent |
| Not implemented | Settings UI schema, secure-storage layout, consent CRUD REST APIs |

---

## OQ-PACK — Exact pack schema field inventory

| Field | Value |
|-------|-------|
| Status | **Unresolved** — **blocks pack contract freeze / EP-002 schema handoff** |
| Behavioral (shippable) | XML-oriented packed content + token pre-calculation (FR-001, FR-002); binary skip (FR-003) |
| Persistence (T018 provisional) | **Proposed** orchestrator-managed pack cache keyed by `repo_name` under `CONTEXTOS_PACK_CACHE_DIR` — retrieval shape not Confirmed |
| Forbidden | Inventing documented pack fields beyond FR-01 as requirements |

---

## OQ-OVERRIDE — Explicit approved override UX for excluded secrets/paths

| Field | Value |
|-------|-------|
| Status | **Unresolved** |
| EP-001 behavior | Default exclusions remain in force; **no** override path |

---

## OQ-01 — Exact RBAC roles/path/authn schema

| Field | Value |
|-------|-------|
| Status | **Unresolved** — Missing Evidence |
| EP-001 MVP | POC may defer path-RBAC enforcement detail; do not invent roles/authn |

---

## OQ-HTTP — Confirmed HTTP status codes for `POST /index`

| Field | Value |
|-------|-------|
| Status | **Unresolved** (api-contract Proposed only) |
| Proposed (labeled, not Confirmed) | `200` success; `400` invalid/unreadable path; `403` RBAC (when exists); `409` index in progress; `500` failure |

---

## OQ-OTEL — OpenTelemetry exporter vendor

| Field | Value |
|-------|-------|
| Status | **Unresolved** |
| EP-001 | OTel-compatible no-op / exporter-agnostic helpers only |

---

## Related

| ID | Status |
|----|--------|
| OQ-CANCEL | Server-side cancel Not evidenced; client cancel Proposed (extension) |
