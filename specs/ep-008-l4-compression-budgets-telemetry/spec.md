# Feature Specification: EP-008 L4 Context Compression, Token Budgets & Cost Telemetry

**Feature Branch**: `feature/ep-008-l4-compression-budgets-telemetry`  
**Created**: 2026-07-29  
**Status**: Draft  
**Input**: User description: "Deliver EP-008 only: US-023 adaptive summarization with recall gate, US-022 per-phase token budget enforcement, US-024 compression telemetry and token cost dashboard — Headroom-style L4 on V1; do not redesign L1/OKF; retain OQ-07/08/09."

## Evidence Classification

| Label | Meaning in this specification |
|---|---|
| **Confirmed** | Supported by the BRD, approved ADRs, architecture, backlog, or current repository evidence. |
| **Proposed** | A documented direction that is not a frozen product contract. |
| **Missing Evidence** | A required detail not established by available sources; it is not treated as a Confirmed requirement. |

## Prerequisites (cite — do not redesign)

| Prerequisite | Boundary |
|---|---|
| **EP-001 / EP-002 packing & `POST /context`** | Confirmed metrics keys `tokens_before`, `tokens_after`, `saving_percent`, `trace` already exist as packing token estimates (`l5_phase_pack.py` semantics). **Not** full L4 Headroom compression. EP-008 must make these meaningful under L4 compress. Cite: api-contract §2.3; backlog A-06; ADR-006. |
| **L5 pack / hybrid search (US-003, US-004)** | Adaptive summarization and budgets operate on packs produced by existing packing/search; do not redesign Repomix-style packing or hybrid search. |
| **L3 symbols (US-005)** | Symbol/type preservation gates depend on existing symbol capability; do not redesign Serena contracts. |
| **US-016 query-time LLM consent** | External LLM summarization requires explicit consent/configuration; EP-008 enforces the gate, does not invent consent UX storage. |
| **EP-006 / EP-007 L1** | On main. Structural graph, blast, `graph.html` — **OUT OF SCOPE** to redesign. L4 may consume packed context that already includes L1 enrichment; it does not own blast/graph. |
| **EP-013 OKF** | On main. **OUT OF SCOPE** — do not touch OKF generate/retrieve. |

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Adaptive summarization with recall gate (Priority: P1)

As a Developer, I want low-relevance files compressed via adaptive summarization that preserves symbols, types, and TODOs, so that I pay far fewer tokens without losing critical detail.

**Why this priority**: US-023 is the L4 foundation (FR-12; BO-02). Budgets (US-022) and meaningful telemetry (US-024) depend on real compression. Dependency order: US-003 + US-005 → US-023.

**Independent Test**: On a large naive pack fixture, run L4 adaptive summarization and verify (a) token savings in 60–95% vs naive packing, (b) symbols/types/TODOs preserved per stated gates, (c) recall@10 >0.92 on an agreed harness — without claiming pass until harness execution.

**Acceptance Scenarios**:

1. **Given** a large naive pack, **When** L4 adaptive summarization runs, **Then** token savings versus naive packing are in the **60–95%** range (BRD FR-12; §10).
2. **Given** files scored low-relevance for the query / SDLC phase / recency, **When** summarization compresses them, **Then** symbols, types, and TODOs are preserved as stated in FR-12.
3. **Given** an agreed recall harness for compressed context utility, **When** recall@10 is measured, **Then** recall@10 is evaluated against **>0.92** (BRD §10); no pass claim is implied by this specification alone.
4. **Given** the BRD §13 risk that compression drops key symbols, **When** validation runs, **Then** symbol-preservation tests and the recall gate apply as mitigations.
5. **Given** summarization would send context to an **external** LLM provider, **When** consent/configuration is absent, **Then** the system MUST NOT send code/context to that provider (US-016; Constitution III). **Given** consent is present (or a local inference path is configured), **When** query-time summarization runs, **Then** only the allowed compressed/packed path may be used.
6. **Given** illustrative BRD examples (85k → 7.2k / 91% saving), **When** success narratives are written, **Then** those figures are treated as **illustrative KPI targets** (BRD §12), not separate features and not mandatory single-request exact values.

---

### User Story 2 — Per-phase token budget enforcement (Priority: P1)

As an AI Platform Lead, I want Headroom-style enforcement of per-phase token budgets with hard-fail and degradation policy, so that prompts stay within cost/context limits.

**Why this priority**: US-022 is the FR-11 control plane for BO-02 cost/context limits. Independently valuable once summarization exists; depends on US-004 and US-023.

**Independent Test**: Configure an SDLC phase budget; feed a pack/compression path that would exceed it; verify hard-fail and degradation behaviors per FR-11 intent. **Do not** treat Dev=8k or Dev=12k as Confirmed normative AC until OQ-07 is resolved.

**Acceptance Scenarios**:

1. **Given** a configured SDLC phase token budget, **When** context compression/packing would exceed that budget, **Then** the Headroom-style engine enforces the budget with **hard-fail** and **degradation** policy as required by FR-11.
2. **Given** FR-11 examples Dev=12k and Design=32k and §5 example Dev=8k, **When** budgets are configured or tests assert numeric ceilings, **Then** canonical Dev budget values are resolved only after OQ-07 — `[NEEDS CLARIFICATION: OQ-07]` — and MUST NOT be invented as Confirmed in this epic.
3. **Given** Design phase budget examples in FR-11 (Design=32k), **When** Design-phase enforcement is specified, **Then** Design=32k may be used as the evidenced example pending any future clarification that contradicts it; Dev remains blocked on OQ-07.
4. **Given** budget hard-fail, **When** the API responds, **Then** clients observe a documented failure/degraded outcome; exact HTTP codes remain **Proposed** (`413`/`422` hard-fail, `503` degraded per api-contract §2.3) — not Confirmed contracts.
5. **Given** A-03 (LLM ~128k context; ContextOS compresses to fit), **When** budgets are enforced, **Then** enforcement remains the product control plane even if the downstream model window is larger.

---

### User Story 3 — Compression telemetry & token cost dashboard (Priority: P2)

As an AI Platform Lead, I want compression ratio, recall@k, and cost-saved emitted to observability and shown on a token dashboard, so that savings are measurable.

**Why this priority**: US-024 makes BO-02 outcomes visible and is a V1 exit criterion (FR-13; §15). Depends on US-023 producing real L4 metrics.

**Independent Test**: After L4 compression requests, verify OpenTelemetry-compatible emission of compression ratio, recall@k, and cost-saved; verify `contextos_token_dashboard.html` (or equivalent evidenced dashboard) shows before/after token cost; verify `POST /context` metrics fields are meaningfully populated under L4. Serving mechanism and exporter vendor remain `[NEEDS CLARIFICATION: OQ-08]` / `[NEEDS CLARIFICATION: OQ-09]`.

**Acceptance Scenarios**:

1. **Given** L4 compression requests, **When** telemetry is emitted, **Then** metrics include **compression ratio**, **recall@k**, and **cost-saved** per request (FR-13) via **OpenTelemetry-compatible** instrumentation (ADR-011; BRD §10 Observability).
2. **Given** dashboard naming in the BRD, **When** operators view token costs, **Then** `contextos_token_dashboard.html` (or an equivalent evidenced dashboard) shows before/after token cost. Serving mechanism is `[NEEDS CLARIFICATION: OQ-08]` (static HTML vs API-hosted / Proposed `GET /metrics`).
3. **Given** Confirmed `POST /context` metrics keys, **When** V1 L4 compression runs, **Then** `tokens_before`, `tokens_after`, and `saving_percent` are populated **meaningfully** as L4 compression outcomes (not merely MVP packing estimates — A-06 / ADR-006).
4. **Given** Constitution V telemetry opt-out obligations, **When** telemetry is configured, **Then** clients MUST NOT silently bypass telemetry opt-out; concrete opt-out API remains **Missing Evidence** (backlog US-024 notes).
5. **Given** OQ-09 unresolved, **When** OTel exporters are chosen, **Then** the product remains OTel-compatible without inventing a Confirmed collector vendor (`[NEEDS CLARIFICATION: OQ-09]`).

### Edge Cases

- Pack already under phase budget: enforcement MUST allow success without hard-fail; degradation MUST NOT be applied spuriously.
- Summarization with consent denied for external LLM: MUST fall back to non-exfiltrating behavior (local summarization if configured, or skip external summarize) without silent exfil.
- Empty / tiny packs: savings percent and recall harness applicability may be undefined — do not invent Confirmed minimum pack size; mark harness scoping in validation.
- Policy-excluded paths (`.gitignore`, `.env`, secrets, build outputs, dependency folders, binaries) MUST NOT contribute source bytes to summarization or telemetry payloads beyond allowed metadata (Constitution III).
- MVP packing-only metrics remain valid when L4 is disabled or unavailable; V1 obligation is meaningful L4 metrics when compression runs (A-06).
- Exact degradation algorithm (what is dropped/summarized further under budget pressure) is **Missing Evidence** beyond FR-11 “hard fail and degradation policy” — do not invent Confirmed step tables.
- Telemetry opt-out API shape is **Missing Evidence** — enforce non-bypass of any configured opt-out without inventing the API.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: ContextOS MUST apply Headroom-style adaptive summarization to low-relevance pack content so that token savings versus naive packing fall in the **60–95%** range under agreed fixtures. *(US-023; BRD FR-12; §10)*
- **FR-002**: Adaptive summarization MUST preserve **symbols**, **types**, and **TODOs** as stated for compressed files. *(US-023; BRD FR-12)*
- **FR-003**: Compressed-context utility MUST be gated by **recall@10 >0.92** on an agreed measurement harness; symbol-preservation tests MUST apply as BRD §13 mitigation. *(US-023; BRD §10; §13)*
- **FR-004**: Query-time use of an **external** LLM for summarization MUST require explicit consent/configuration; without it, ContextOS MUST NOT send code/context to that provider. *(US-023 assumption; US-016; Constitution III)*
- **FR-005**: ContextOS MUST enforce **per-phase token budgets** via a Headroom-style engine with **hard-fail** and **degradation** policy when compression/packing would exceed the configured phase budget. *(US-022; BRD FR-11)*
- **FR-006**: Canonical numeric Dev phase budget used as normative AC MUST NOT be asserted until OQ-07 is resolved (`[NEEDS CLARIFICATION: OQ-07]` — §5 Dev=8k vs FR-11 Dev=12k). Design=32k remains the FR-11 evidenced example. *(US-022; OQ-07; api-contract §5)*
- **FR-007**: When L4 compression runs on `POST /context`, response `metrics` MUST populate `tokens_before`, `tokens_after`, and `saving_percent` with **meaningful L4 compression outcomes** (not packing-estimate-only semantics). `trace` remains available for pipeline observability. *(US-024; api-contract §2.3; A-06; ADR-006)*
- **FR-008**: ContextOS MUST emit per-request **compression ratio**, **recall@k**, and **cost-saved** via **OpenTelemetry-compatible** instrumentation. *(US-024; BRD FR-13; §10 Observability; ADR-011)*
- **FR-009**: ContextOS MUST provide a token cost dashboard artifact named `contextos_token_dashboard.html` (or equivalent evidenced dashboard) showing before/after token cost. Serving mechanism is `[NEEDS CLARIFICATION: OQ-08]`; Proposed alternatives include static HTML or API-hosted / `GET /metrics`. *(US-024; BRD FR-13; api-contract §3)*
- **FR-010**: FastAPI MUST own L4 compression, budget enforcement, ignore/consent policy, OpenAPI/`POST /context` metrics semantics, and telemetry emission; CLI / VS Code / other clients MUST remain thin consumers and MUST NOT silently bypass backend validation, consent, ignore policy, or telemetry opt-out. *(Governance; Constitution V)*
- **FR-011**: L4 paths MUST respect IgnorePolicy (`.gitignore`, `.env`, secrets, build outputs, dependency folders, binaries) and MUST preserve **source provenance** on compressed/packed outputs. *(Governance; Constitution III; BRD §10)*
- **FR-012**: EP-008 MUST NOT redesign L1 blast/graph (EP-006/007) or OKF (EP-013); it consumes packs/context from existing pipeline stages only. *(Roadmap; ep-008-brief; ADR-001)*

### Key Entities

| Entity | Conceptual attributes / relationship | Evidence status |
|---|---|---|
| Phase token budget | SDLC phase → max tokens; hard-fail + degradation when exceeded | Confirmed capability (FR-11); Dev canonical value Missing Evidence (OQ-07); Design=32k evidenced example |
| Compression result | `tokens_before`, `tokens_after`, `saving_percent`, compressed context, provenance | Confirmed response metric keys (api-contract §2.3); L4-meaningful population is EP-008 obligation |
| Relevance score | Scores chunks/files by query + SDLC phase + recency (BRD §14 narrative) | Confirmed intent in BRD pipeline prose; exact scoring algorithm Missing Evidence |
| Recall gate | recall@10 on compressed context utility; symbol-preservation checks | Confirmed targets (BRD §10; §13) |
| Compression telemetry event | compression ratio, recall@k, cost-saved per request | Confirmed FR-13 metric names; OTel exporter vendor Missing Evidence (OQ-09) |
| Token cost dashboard | Before/after token cost view; artifact name `contextos_token_dashboard.html` | Confirmed name (FR-13); serving mechanism Missing Evidence (OQ-08) |

## ContextOS Impact *(mandatory for this project)*

### Affected Layers

| Layer | Impact | Evidence |
|---|---|---|
| **L1 Structural Knowledge Graphs** | **N/A to redesign.** May appear inside packs already enriched by EP-006/007; L4 does not own blast/graph. | ep-008-brief; ADR-001 |
| **L2 Multi-modal Project Graphs** | **N/A.** V2. | Roadmap |
| **L3 Symbol & LSP Navigation** | **Dependency only.** Symbol/type preservation relies on existing L3 capability; no Serena redesign. | US-023 deps US-005 |
| **L4 Context Compression** | **Affected — Confirmed.** Budgets, adaptive summarization, relevance scoring, recall gate, compression telemetry. | BRD §5 L4; FR-11..13; ADR-006 |
| **L5 Context Packing & Semantic Search** | **Dependency / integration.** L4 consumes naive packs; `POST /context` metrics become L4-meaningful. Do not redesign packing/search. | api-contract §2.3; architecture-overview L4 row |
| **L6 Persistent Agent Memory** | **N/A.** V2. | Roadmap |

### Affected Surfaces

| Surface | Impact | Evidence |
|---|---|---|
| **FastAPI / API** | **Affected — Confirmed.** Owns L4 in `POST /context` path, budget enforcement, OTel emission, dashboard artifact delivery (serving TBD). | architecture-overview FR-11..13 mapping; Constitution V |
| **CLI** | **Optional consumer.** Existing `contextos ask` continues to call context path; no new Confirmed CLI verb required by these stories. | api-contract §6; US-022..024 |
| **VS Code extension** | **Optional consumer / thin client.** Must not bypass consent, ignore, or telemetry opt-out; no Confirmed new Webview required for token dashboard in this epic (dashboard may be minimal HTML). | Constitution V; ep-008-brief |
| **Dashboard / Webview / Visualization** | **Affected — Confirmed minimal.** `contextos_token_dashboard.html` (or equivalent); **no full UI design suite**. | FR-13; lean Spec Kit brief |
| **GitHub Action / CI** | **N/A.** | User scope |

### Privacy And Security

| Control | Status | Evidence |
|---|---|---|
| IgnorePolicy (`.gitignore`, `.env`, secrets, binaries, build outputs, deps) | **Confirmed** — MUST apply on L4 summarize/pack paths | Constitution III; BRD §10 |
| Consent before query-time **external** LLM summarization | **Confirmed** | US-016; US-023 assumptions; Constitution III |
| Source provenance on compressed outputs | **Confirmed** | Constitution III |
| No silent telemetry opt-out bypass | **Confirmed** obligation; opt-out API **Missing Evidence** | Constitution V; US-024 notes |
| RBAC per repo path | **Confirmed** platform control; concrete authn/RBAC schema **Missing Evidence** for dashboard/API | Constitution III; ADR-012 |
| No code exfil during indexing | **Confirmed** (unchanged); L4 summarization is query-time | BRD §10; Appendix C |

## Non-Functional Requirements

### Performance

| NFR | Target | Status |
|---|---|---|
| Token compression savings | 60–95% vs naive packing | **Confirmed** BRD §10 / FR-12 |
| recall@10 on compressed utility | >0.92 | **Confirmed** BRD §10 |
| Avg compression ratio KPI | Illustrative 91% (85k → 7.2k) | **Confirmed** as KPI narrative (BRD §12), not a per-request hard AC |
| Token cost / PR KPI | $0.50 → $0.05 | **Confirmed** business KPI (BO-02 / §12); pricing model details Missing Evidence for exact $ computation |
| End-to-end ask latency under L4 | Not newly Confirmed beyond existing ask/demo narratives | Do not invent a new L4-only p95 |

### Security

- FR-004, FR-010, FR-011 apply.
- Dashboard auth model **Missing Evidence** / OQ-08 adjacent — do not invent Confirmed auth for the HTML artifact.
- External summarization without consent is forbidden.

### Reliability

- Hard-fail when budget cannot be met after degradation attempts (FR-11 intent).
- Exact degradation steps **Missing Evidence**.
- Proposed API status codes for hard-fail/degraded: `413`/`422` / `503` (api-contract §2.3) — **Proposed**, not Confirmed.
- When L4 is unavailable, MVP packing path may still serve context with packing-estimate metrics (A-06) without inventing a Confirmed fallback schema.

### Accessibility

- Not evidenced for the minimal token dashboard beyond operator readability; no invented a11y numeric targets. Full UI design suite is out of scope.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 — Validation target, not achieved**: On agreed large-pack fixtures, L4 adaptive summarization achieves **60–95%** token savings vs naive packing while preserving symbols/types/TODOs. *(US-023; BRD FR-12; §10)*
- **SC-002 — Validation target, not achieved**: On an agreed harness, compressed-context **recall@10 >0.92**; symbol-preservation tests pass as §13 mitigation. *(US-023; BRD §10; §13)*
- **SC-003 — Functional acceptance (numeric Dev AC blocked)**: Per-phase budget hard-fail + degradation demonstrable for configured budgets; **Dev canonical numeric AC blocked on OQ-07**; Design=32k example may be used in fixtures as evidenced. *(US-022; FR-11; OQ-07)*
- **SC-004 — Functional acceptance**: After L4 compress, `POST /context` `metrics.tokens_before` / `tokens_after` / `saving_percent` reflect meaningful compression outcomes. *(US-024; api-contract §2.3)*
- **SC-005 — Observability acceptance**: OTel-compatible emission includes compression ratio, recall@k, and cost-saved per request; exporter vendor remains `[NEEDS CLARIFICATION: OQ-09]`. *(US-024; FR-13; ADR-011)*
- **SC-006 — Dashboard acceptance**: `contextos_token_dashboard.html` (or equivalent) shows before/after token cost; serving mechanism remains `[NEEDS CLARIFICATION: OQ-08]`. *(US-024; FR-13)*

## Confirmed Facts

| Fact | Source |
|---|---|
| EP-008 = US-022, US-023, US-024; V1 L1+L4 roadmap slice for L4 | backlog EP-008; BRD §15; ADR-001 |
| L4 is Headroom-style compression in **V1**, not MVP gate | ADR-006 |
| BRD FR-11 / FR-12 / FR-13 define budgets, adaptive summarization, telemetry + dashboard name | BRD §9 L4 |
| Compression NFR: 60–95% savings, recall@10 >0.92 | BRD §10 |
| `POST /context` Confirmed metric keys: `tokens_before`, `tokens_after`, `saving_percent`, `trace` | api-contract §2.3; BRD Appendix D |
| Today those metrics are packing estimates (EP-001/002), not full L4 Headroom | ep-008-brief; A-06; ADR-006 |
| OTel-compatible observability is Confirmed direction; exporter vendor not Confirmed | ADR-011; OQ-09 |
| Query-time external LLM requires consent | US-016; Constitution III |
| L1 (EP-006/007) and OKF (EP-013) are done prerequisites — out of redesign scope | ep-008-brief; roadmap |

## Assumptions

| ID | Assumption | Blocking? | Evidence |
|---|---|---|---|
| A-03 | LLM provider supports ~128k context; ContextOS compresses to fit (V1 L4) | Non-blocking | backlog; BRD §13 |
| A-06 | MVP `/context` may return packing token counts; full compression metrics meaningful at V1 | Non-blocking | backlog; ADR-006 |
| A-EP008-1 | L4 runs after L5 packing (and any L1 enrichment already in the pack) without redesigning those stages | Non-blocking | architecture-overview pipeline; brief |
| A-EP008-2 | Token dashboard may be minimal HTML; no full design-system UI suite in this epic | Non-blocking | ep-008-brief; lean Spec Kit |
| A-EP008-3 | “Cost-saved” is computable from token deltas and/or configured rate tables; exact $ rate table is not Confirmed in sources | Non-blocking — rates Missing Evidence | FR-13 name only |

## Dependencies

| Dependency | Relationship |
|---|---|
| US-003, US-005 | Upstream for US-023 (pack + symbols) |
| US-004 | Upstream for US-022 (phase-aware packing path) |
| US-023 | Upstream for US-022 and US-024 |
| US-016 | Consent gate for external summarization |
| EP-006/007, EP-013 | Exist on main; consume only — do not redesign |
| OTel collector/backend | Required for production telemetry sink — vendor OQ-09 |

## Out Of Scope

- Redesign of L1 blast radius, `graph.html`, React Flow panel, or OKF retrieval
- Full UI/design-system suite for the token dashboard
- L2 multi-modal ingestion and L6 memory governance
- JetBrains IDE, GitHub Action PR risk bot (EP-009), or new Confirmed CLI verbs beyond existing ask path
- Inventing Confirmed Dev budget numbers, dashboard auth, or OTel vendor contracts
- Changing MVP packing-estimate behavior when L4 is not enabled (A-06)

## Open Questions

| ID | Question | Blocking? | Affects |
|---|---|---|---|
| **OQ-07** | Canonical Dev phase token budget: **8k** (BRD §5) vs **12k** (FR-11)? | **Yes — blocking** for numeric US-022 AC / SC-003 Dev fixtures | US-022; FR-006; SC-003 |
| **OQ-08** | Token dashboard serving: static `contextos_token_dashboard.html` vs API-hosted / Proposed `GET /metrics`? | No | US-024; FR-009; SC-006 |
| **OQ-09** | OpenTelemetry exporter / collector vendor? | No | US-024; FR-008; SC-005 |
| OQ-EP008-a | Exact hard-fail vs degradation algorithm steps and when each applies | Yes for precise degradation AC detail — treat detailed steps as Missing Evidence until clarified | US-022 |
| OQ-EP008-b | Telemetry opt-out API / configuration surface | No for epic draft; Confirmed non-bypass only | US-024; Constitution V |
| OQ-EP008-c | Cost-saved dollar rate table / pricing model for KPI $0.50→$0.05 | No | SC business KPI vs FR-13 metric name |

## Requirement Traceability

| Requirement ID | Source | Evidence |
|---|---|---|
| FR-001 | US-023 AC; BRD FR-12; §10 | Adaptive summarization 60–95% |
| FR-002 | US-023 AC; BRD FR-12 | Preserve symbols/types/TODOs |
| FR-003 | US-023 AC; BRD §10; §13 | recall@10 >0.92; symbol-preservation / recall gate |
| FR-004 | US-023 assumptions; US-016; Constitution III | Consent before external LLM summarization |
| FR-005 | US-022 AC; BRD FR-11 | Per-phase budgets; hard-fail + degradation |
| FR-006 | US-022 AC; OQ-07; api-contract §5 | Dev budget canonical value unresolved |
| FR-007 | US-024 AC; api-contract §2.3; A-06; ADR-006 | Meaningful L4 `tokens_*` / `saving_percent` |
| FR-008 | US-024 AC; BRD FR-13; ADR-011 | OTel compression ratio, recall@k, cost-saved |
| FR-009 | US-024 AC; BRD FR-13; OQ-08; api-contract §3 | Token dashboard artifact |
| FR-010 | Constitution V; governance | FastAPI owns L4; no client policy bypass |
| FR-011 | Constitution III; BRD §10 | IgnorePolicy + provenance |
| FR-012 | ep-008-brief; roadmap; ADR-001 | No L1/OKF redesign |

### Acceptance → Requirement map

| Acceptance scenario | Requirements |
|---|---|
| US-023 scenarios 1–4, 6 | FR-001, FR-002, FR-003 |
| US-023 scenario 5 | FR-004, FR-011 |
| US-022 scenarios 1–5 | FR-005, FR-006, FR-010 |
| US-024 scenarios 1–5 | FR-007, FR-008, FR-009, FR-010 |

---

## Spec readiness notes

- **Constitution applied**: Yes (I–V; L4 layer integrity; measurable claims; privacy; surface boundaries).
- **Blocking for Plan Generator numeric budget AC**: OQ-07 (and degradation-step detail as Missing Evidence).
- **Ready for Plan Generator**: **Yes** — with OQ-07 explicitly retained as blocking for Dev numeric AC; plan MUST NOT invent Confirmed Dev=8k or Dev=12k.
