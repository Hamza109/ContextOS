# Feature Specification: EP-003 L3 Symbol & LSP Navigation (Serena)

**Feature Branch**: `feature/ep-003-l3-symbol-lsp-navigation`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "EP-003 — L3 Symbol & LSP Navigation (Serena) (US-005, US-006, US-009, US-010): IDE-grade definition/references/rename-scope and Pack Context with Serena-informed safe edit plan so edits respect language semantics and reduce regressions (BO-03)."

**Stories Covered**: US-005, US-006, US-009, US-010

**Business Objectives**: BO-03 (primary); BO-01 contribution via Pack Context surface

**Source Evidence**: BRD FR-04..FR-06; §11 Developer Pack Context; §14 Pack & Cite; §15 MVP; ADR-005; architecture-overview §3.1/§3.3 L3; api-contract §3 Symbol proxy REST (**Proposed** / may remain MCP-only); constitution I–V; EP-001 indexing foundation; EP-002 `POST /context` packing + citations (cite only — do not re-spec)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Symbol Definition Lookup (Priority: P1)

As a **Developer**, I want ContextOS to resolve a symbol’s definition (file:line, signature, docstring) via Serena, so that AI and IDE workflows use IDE-grade precision instead of text similarity alone.

**Why this priority**: Foundation for safe edits and symbol-accurate context (US-005; FR-04; BO-03). Unlocks references, rename scope, and Pack Context composition. MVP — P0.

**Independent Test**: In a supported language from the Serena-backed set (BRD states 12+ languages; exact language inventory `[NEEDS CLARIFICATION]` if fixtures require enumeration), request definition lookup for a known symbol and verify returned location includes file:line, signature, and docstring when available. Accuracy vs BRD 99% target is verified only after a measurement method is agreed (`[NEEDS CLARIFICATION: OQ-12]` — Proposed verification only).

**Acceptance Scenarios**:

1. **Given** a supported language in the Serena-backed set (BRD states 12+ languages), **When** I request definition lookup for a symbol, **Then** the system returns definition location including file:line, signature, and docstring when available (illustrative shape: `PaymentService::authenticate() → payment.service.ts:42`).
2. **Given** a verification approach agreed for the 99% accuracy claim (`[NEEDS CLARIFICATION: OQ-12 measurement method]`), **When** accuracy is measured, **Then** results meet the BRD 99% accuracy target or the increment documents a scoped gap per constitution IV.
3. **Given** ADR-005 and constitution V boundaries, **When** definition lookup is surfaced in VS Code, **Then** the extension presents results via hover/commands (or equivalent IDE DX) without reimplementing symbol-resolution policy; orchestration/policy remains Serena MCP (+ orchestrator may call Serena in the context pipeline).

---

### User Story 2 — Find All References (Priority: P1)

As a **Developer**, I want all references of a symbol across the monorepo with call-site context, so that I can understand usage before changing code.

**Why this priority**: Direct FR-05 / BO-03 safe-change support for Development/Testing/Maintenance. Independently valuable once definition resolution (US-005) exists. MVP — P0.

**Independent Test**: For a resolved symbol in an indexed workspace, request find-all-references and verify monorepo references include 2 lines before/after call-site context; apply a file-type filter and verify filtered results.

**Acceptance Scenarios**:

1. **Given** a resolved symbol in an indexed workspace, **When** I request find-all-references, **Then** the system returns references across the monorepo including call-site context of 2 lines before/after (FR-05).
2. **Given** a file-type filter, **When** references are requested, **Then** results can be filtered by file type.
3. **Given** constitution V / ADR-005, **When** references are shown in the IDE, **Then** VS Code owns DX presentation; symbol policy is not reimplemented in the extension.

---

### User Story 3 — Rename Scope Analysis (Priority: P1)

As a **Developer**, I want ContextOS to compute safe rename scope and breaking-change count before rename execution, so that refactors do not silently break callers.

**Why this priority**: FR-06 / BO-03 regression reduction. Depends on definition + references (US-005, US-006) but independently testable as analysis-only output. MVP — P1 classification in backlog.

**Independent Test**: Select a symbol for rename analysis; run Serena-backed rename scope analysis; verify safe rename scope and breaking-change count are reported before any rename execution; confirm IDE surfaces allow review prior to execution. Execution sandbox is out of scope (BRD §6).

**Acceptance Scenarios**:

1. **Given** a symbol selected for rename analysis, **When** rename scope analysis runs via Serena-backed capabilities, **Then** the system reports safe rename scope and a breaking-change count before rename execution.
2. **Given** analysis completes, **When** results are shown in the IDE surface, **Then** the developer can review scope prior to executing rename (execution sandboxing remains out of scope per BRD §6; ContextOS does not claim a code-execution sandbox).

---

### User Story 4 — Pack Context & Safe Edit Plan (Priority: P1)

As a **Developer**, I want to right-click → Pack Context and receive a safe edit plan via Serena LSP, so that I get precise edits rather than whole-file rewrites.

**Why this priority**: Matches BRD §11 Developer use case; composes L3 with L5 packing for edit safety (BO-03). Depends on packing (US-004 / EP-002), definition (US-005), and Ask entry (US-008 / EP-004) conceptually — this Spec Kit specifies only the L3-informed Pack Context / safe edit plan behavior, not full CLI/Ask epic.

**Independent Test**: In VS Code with ContextOS installed, select a file/symbol, invoke Pack Context (right-click or equivalent command), and verify packed relevant context plus a Serena-informed safe edit plan (not an indiscriminate whole-file rewrite directive). When citations are present, verify file:line and confidence per BRD §14 without inventing citation JSON (`[NEEDS CLARIFICATION: OQ-11]`). Exact safe-edit-plan response shape is **Not evidenced** — Proposed verification of behavioral intent only.

**Acceptance Scenarios**:

1. **Given** a file/symbol selection in VS Code with ContextOS installed, **When** I invoke Pack Context (right-click or equivalent command), **Then** the system packs relevant context and provides a Serena-informed safe edit plan rather than an indiscriminate whole-file rewrite directive.
2. **Given** packed context is returned, **When** citations are present, **Then** provenance includes file:line and confidence as described in BRD §14 (exact JSON shape `[NEEDS CLARIFICATION: OQ-11]`).
3. **Given** EP-001 indexing and EP-002 `POST /context` packing are available as upstream, **When** Pack Context runs, **Then** this epic consumes those capabilities without re-specifying hybrid search, phase templates, or index policy (cite `specs/ep-001-*`, `specs/ep-002-*` / backlog EP-001/EP-002).
4. **Given** constitution V, **When** Pack Context is invoked from the extension, **Then** FastAPI owns packing/orchestration; the extension owns DX (command/context-menu) and MUST NOT reimplement backend search/index/symbol policy.

---

### Edge Cases

- Unsupported language / symbol outside Serena-backed set — BRD states 12+ languages; exact language inventory and failure UX **Not evidenced** (`[NEEDS CLARIFICATION: Serena language set]`).
- Symbol unresolved / ambiguous definition — L1 structural expand for ambiguous symbols is V1 (implementation-guidelines layer table); MVP behavior for unresolved symbols **Not evidenced** beyond returning no/partial definition (`[NEEDS CLARIFICATION]`).
- Workspace not indexed — US-006 assumes indexed workspace; indexing owned by EP-001 — do not re-spec; Pack Context / references may be unavailable until index exists.
- Serena MCP unavailable / MCP ecosystem instability — BRD §13 risk notes pin versions + regex fallback; exact fallback UX for this epic **Not evidenced** as Confirmed product behavior (`[NEEDS CLARIFICATION]` / Proposed only).
- File-type filter with no matching references — empty filtered set expected conceptually; exact empty-result contract **Not evidenced**.
- Rename analysis when no breaking changes — breaking-change count of zero is consistent with FR-06; do not invent additional risk enums.
- Rename **execution** / code-execution sandbox — **Out of scope** (BRD §6; US-009 Notes).
- Symbol proxy REST vs MCP-only — api-contract §3 **Proposed** / may remain MCP-only (`[NEEDS CLARIFICATION]`); do not invent Confirmed REST endpoints.
- Safe edit plan machine shape — **Not evidenced** (`[NEEDS CLARIFICATION]`); verify behavioral intent (Serena-informed plan vs whole-file rewrite) only.
- Citation JSON inside packed context — OQ-11 shared with EP-002; do not invent fields.
- Full Ask ContextOS <3 clicks / CLI ask surface — US-008/US-007 are EP-004; US-010 depends conceptually on US-008 for IDE entry — do not expand full EP-004 in this Spec Kit.
- JetBrains — Future (OQ-02 / ADR-007); out of scope for MVP VS Code-first.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST resolve symbol definitions via Serena MCP, returning definition location including file:line, signature, and docstring when available.  
  *Source: US-005; BRD FR-04; ADR-005*

- **FR-002**: System MUST support definition lookup for languages in the Serena-backed set (BRD states 12+ languages). Exact language inventory for AC fixtures is `[NEEDS CLARIFICATION: Serena language set]` — Missing Evidence beyond “12+”.  
  *Source: US-005; FR-04*

- **FR-003**: Definition accuracy MUST target BRD 99% when measured. Measurement method is `[NEEDS CLARIFICATION: OQ-12]`. Until resolved, verification designs MUST remain **Proposed only** and MUST NOT claim a Confirmed measurement method or invent Pass/Fail evidence. If the increment cannot yet meet 99%, scoped gap MUST be documented per constitution IV.  
  *Source: US-005; FR-04; OQ-12; constitution IV*

- **FR-004**: System MUST return all references of a resolved symbol across the monorepo with call-site context of 2 lines before and 2 lines after.  
  *Source: US-006; BRD FR-05*

- **FR-005**: System MUST allow find-all-references results to be filtered by file type.  
  *Source: US-006; FR-05*

- **FR-006**: System MUST compute safe rename scope and a breaking-change count for a selected symbol before rename execution (analysis only).  
  *Source: US-009; BRD FR-06*

- **FR-007**: System MUST present rename-scope analysis results on an IDE surface so the developer can review scope prior to executing rename. Rename execution sandboxing is **out of scope** (BRD §6).  
  *Source: US-009; BRD §6*

- **FR-008**: From VS Code, given a file/symbol selection, System MUST support Pack Context (right-click or equivalent command) that packs relevant context and provides a Serena-informed safe edit plan rather than an indiscriminate whole-file rewrite directive. Exact safe-edit-plan response shape is `[NEEDS CLARIFICATION: safe edit plan shape]` — **Not evidenced**; behavioral intent is required.  
  *Source: US-010; BRD §11 Developer; FR-03..FR-06 composition*

- **FR-009**: When packed context from Pack Context includes citations, provenance MUST include file:line and confidence as described in BRD §14. Exact JSON citation schema is `[NEEDS CLARIFICATION: OQ-11]` — MUST NOT invent undocumented citation fields.  
  *Source: US-010; BRD §14; OQ-11; EP-002 FR-015/FR-016 (cite)*

- **FR-010**: Pack Context MUST consume EP-001 indexing/pack foundation and EP-002 `POST /context` hybrid search + phase packing + citation behavior as upstream. This epic MUST NOT re-specify EP-001/EP-002 requirements.  
  *Source: US-010 Dependencies US-004/US-005; EP-001; EP-002; PM brief*

- **FR-011**: FastAPI orchestrator MUST own intelligence orchestration (including optional Serena calls in the context pipeline per ADR-005). VS Code extension MUST own DX (hover, commands, Pack Context entry) and MUST NOT reimplement backend search, index, or symbol policy.  
  *Source: constitution V; ADR-002/ADR-005; implementation-guidelines §3; US-005/US-006/US-010*

- **FR-012**: Symbol capabilities MAY be exposed via Serena MCP only. Symbol proxy REST is **Proposed** and may remain MCP-only (`[NEEDS CLARIFICATION: Symbol REST vs MCP]` per api-contract §3). System MUST NOT treat invented symbol REST paths as Confirmed Appendix D contracts. Confirmed HTTP remains: `GET /`, `POST /index`, `POST /context`, `GET /blast`, `GET /graph.html` (blast/graph are V1 — not EP-003 deliverables).  
  *Source: api-contract §3; Appendix D; US-005 Notes*

- **FR-013**: Extension hover/commands for definitions, references, rename scope, and Pack Context MUST surface Serena-backed results consistent with FR-001..FR-008 without silently bypassing backend validation, consent checks, RBAC (where applicable), or indexing policy.  
  *Source: constitution V; ADR-005; architecture-overview FR-04..06 surfaces*

- **FR-014**: Document symbols and hover docs are evidenced L3 Serena capabilities (BRD §5 L3; ADR-005). Where IDE hover is used for definition-related DX, System MUST present available hover/doc information from Serena without inventing undocumented hover schema fields.  
  *Source: BRD L3 capabilities; ADR-005; architecture-overview L3*

- **FR-015**: L1 blast-radius expand for ambiguous symbols, L4 Headroom compression product, L2/L6, JetBrains, and full EP-004 CLI/Ask epic beyond what US-010 requires for Pack Context / safe edit plan surface are **out of scope** for this Spec Kit.  
  *Source: EP-003 brief; roadmap; ADR-006/007; US-010 Notes boundary*

### Key Entities

- **Symbol**: Named code entity subject to definition/reference/rename analysis (illustrative: `PaymentService::authenticate()`).
- **Definition Result**: Conceptual result including file:line, signature, and docstring when available (FR-04 example shape). Exact transport schema beyond these attributes **Not evidenced** as Confirmed REST.
- **Reference Hit**: Occurrence of a symbol with call-site context (2 lines before/after); optionally constrained by file-type filter.
- **Rename Scope Analysis**: Pre-execution report of safe rename scope plus breaking-change count (analysis only).
- **Safe Edit Plan**: Serena-informed edit guidance produced with Pack Context; machine shape `[NEEDS CLARIFICATION]` — behavioral entity only.
- **Packed Context / Citation**: Upstream EP-002 packing output with file:line + confidence provenance (OQ-11); consumed, not re-specified.
- **Serena MCP Session**: Local MCP/LSP bridge used for L3 operations (ADR-005 Confirmed integration choice).

---

## ContextOS Impact *(mandatory for this project)*

### Affected Layers

- **L1 Structural Knowledge Graphs**: N/A as EP-003 deliverable — ambiguous-symbol expand via L1 is V1 (implementation-guidelines); blast/`GET /blast` owned elsewhere.
- **L2 Multi-modal Project Graphs**: N/A — V2.
- **L3 Symbol & LSP Navigation**: **Primary** — Serena-backed definitions, references, hover docs, rename scope, symbol-aware edit planning (ADR-005; BRD L3).
- **L4 Context Compression**: N/A as product deliverable — V1 / ADR-006; not re-specified.
- **L5 Context Packing & Semantic Search**: **Upstream consumer only** for US-010 Pack Context — cite EP-001/EP-002; do not re-spec hybrid search or phase packing.
- **L6 Persistent Agent Memory**: N/A — V2.

### Affected Surfaces

- **FastAPI / API**: **Affected** — may call Serena in context pipeline (ADR-005). Symbol proxy REST is **Proposed** / optional (api-contract §3). Confirmed `POST /context` owned by EP-002 — consumed for packing, not re-specified.
- **CLI**: N/A as primary for this Spec Kit — full CLI epic is EP-004; US-010 is VS Code Pack Context.
- **VS Code Extension**: **Primary DX** — hover/commands, Pack Context (right-click or equivalent); MCP client wiring for Serena UX allowed; no intelligence policy reimplementation (constitution V; implementation-guidelines §3).
- **Dashboard / Webview / Visualization**: N/A as primary L3 acceptance — graph viz is L1/V1.
- **GitHub Action / CI**: N/A — Future / Missing Evidence.
- **Serena MCP**: **Confirmed** integration surface for L3 (ADR-005; tech-stack).

### Privacy And Security

- **Repository content handling**: Symbol operations MUST respect repository ignore/exclusion policy established by indexing (`.gitignore`, `.env`, secrets, binaries — constitution III; EP-001). Do not invent a second ignore engine in the extension.
- **Consent / exfiltration**: Index-time code must not be sent to external LLM providers (constitution III). Query-time external LLM use (if Pack Context later feeds an external model) requires consent/configuration — owned by privacy/consent stories; clients MUST NOT bypass orchestrator policy.
- **RBAC / PII**: RBAC per repo path where authorization applies (constitution III); exact RBAC schema Missing Evidence (OQ-01) — **not invented**. PII redaction primary for L2/L6 — N/A as primary for L3 symbol navigation.
- **Source provenance**: Pack Context citations MUST preserve file:line + confidence (BRD §14; constitution III); OQ-11 for JSON shape.
- **Webview / messages**: If Webview is used for presenting plans/results, validate/sanitize messages (constitution III) — no invented Webview product for this epic beyond existing extension patterns.

---

## Non-Functional Requirements

### Performance

- **NFR-001**: MVP exit includes symbol-accurate context in IDE under stated POC conditions (BRD §15 “Dev can get symbol-accurate context <2s in IDE”). This is an IDE+L3 composition goal; EP-003 contributes L3 precision and MUST NOT invent a stricter unstated CLI SLA. Exact harness for the <2s claim when composed with Ask/Pack is `[NEEDS CLARIFICATION]` shared with EP-004 US-008 — carry as open for verification design.
- **NFR-002**: Definition 99% accuracy is a BRD FR-04 quality claim; measurement method OQ-12 blocks verification design, not story intent (constitution IV).

### Security

- **NFR-003**: No silent bypass of orchestrator validation, consent, RBAC (when defined), or indexing policy from the extension (constitution V).
- **NFR-004**: Secrets remain outside repo; MCP/local Serena operation MUST NOT invent cloud exfil of source for symbol lookup.
- **NFR-005**: Authn for any future Symbol REST proxy is `[NEEDS CLARIFICATION]` (api-contract) — non-blocking while MCP-only remains valid.

### Reliability

- **NFR-006**: MCP ecosystem stability risk is evidenced (BRD §13 — pin versions, regex fallback). Exact Confirmed fallback product behavior for EP-003 is **Not evidenced** — document as Proposed in plan/verification; do not claim Pass without design.

### Accessibility

- Not evidenced for L3 IDE symbol surfaces beyond standard VS Code DX — **N/A** (`Not evidenced in provided inputs.`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a supported-language symbol, definition lookup returns file:line, signature, and docstring when available (US-005; FR-04).
- **SC-002**: Definition accuracy meets BRD 99% **when** an agreed measurement method exists (OQ-12). Until then, success is presence of Proposed verification design only — **do not claim Pass/Fail** on 99% without method + evidence (constitution IV / Verification Gate).
- **SC-003**: Find-all-references returns monorepo references with 2 lines before/after call-site context (US-006; FR-05).
- **SC-004**: References can be filtered by file type (US-006; FR-05).
- **SC-005**: Rename scope analysis reports safe rename scope and breaking-change count before execution; developer can review in IDE; no execution sandbox claimed (US-009; FR-06; BRD §6).
- **SC-006**: Pack Context from VS Code yields packed relevant context plus Serena-informed safe edit plan (not whole-file rewrite directive) (US-010; §11).
- **SC-007**: When citations are present on packed Pack Context output, they include file:line and confidence (BRD §14); exact JSON remains OQ-11.
- **SC-008**: Extension does not reimplement search/index/symbol policy; FastAPI (+ Serena MCP) owns orchestration (constitution V; ADR-005) — verifiable by architecture/boundary review, not invented metrics.
- **SC-009**: No Confirmed symbol REST endpoints are required for MVP acceptance if MCP-only path satisfies FR-04..06 (api-contract §3) — REST remains Proposed until clarified.

---

## Confirmed Facts

- EP-003 includes US-005, US-006, US-009, US-010 only (backlog; ep-003-brief).
- Business objective: IDE-grade symbol accuracy to reduce regressions (BO-03).
- L3 via Serena MCP: definitions, references, hover docs, rename scope, symbol-aware edit planning (BRD L3; ADR-005 **Confirmed**).
- FR-04: file:line, signature, docstring; 12+ languages; 99% accuracy claim with OQ-12 open.
- FR-05: monorepo references + 2 lines before/after + file-type filter.
- FR-06: safe rename scope + breaking-change count before execution; analysis only.
- BRD §11: right-click → Pack Context + safe edit plan via Serena (not whole-file rewrite).
- Citations: file:line + confidence (BRD §14); OQ-11 for JSON shape.
- FastAPI owns orchestration; VS Code owns DX (constitution V; ADR-002/005).
- Symbol proxy REST is Proposed / may remain MCP-only (api-contract §3).
- Confirmed Appendix D HTTP does **not** include L3 symbol REST.
- Rename execution sandbox out of scope (BRD §6).
- Upstream: EP-001 indexing; EP-002 `POST /context` packing (cite, don’t re-spec).
- US-008 Ask <3 clicks is EP-004; US-010 depends conceptually — do not expand full EP-004.
- MVP ships L5+L3 (roadmap; ADR-001).

---

## Assumptions

- **A-01** (non-blocking): Git is source of truth; monorepo ≤1M LOC for MVP (BRD §13) — constrains scale of monorepo reference stories.
- **A-02** (non-blocking): Teams use VS Code or JetBrains (80%+); MVP ships VS Code first (ADR-007) — JetBrains out of this epic.
- **A-EP003-1** (non-blocking): Serena MCP is available locally for developer workspaces (ADR-005; tech-stack; deployment diagram).
- **A-EP003-2** (non-blocking): EP-001 indexing for the target workspace has completed sufficiently for “indexed workspace” reference/Pack Context flows (US-006; US-010 deps).
- **A-EP003-3** (non-blocking): EP-002 packing path (`POST /context`) is available for Pack Context to consume without redefining search/phase behavior.
- **A-EP003-4** (non-blocking): US-008 Ask entry exists or will exist for conceptual dependency; EP-003 delivers Pack Context / safe edit plan surface without owning full Ask epic acceptance.
- **A-EP003-5** (blocking for Confirmed verification of FR-04 99%): OQ-12 remains unresolved — implementation of definition lookup may proceed; accuracy Pass claims blocked until method agreed.
- **A-EP003-6** (blocking for Confirmed safe-edit-plan schema / Symbol REST freeze): Safe edit plan shape and Symbol REST vs MCP remain open — behavioral delivery may proceed under MCP + Proposed labels.

---

## Dependencies

- Serena MCP (Confirmed stack; ADR-005).
- VS Code extension surface for hover/commands/Pack Context (ADR-007 VS Code first).
- FastAPI orchestrator (Python 3.11) — optional Serena calls in context pipeline.
- EP-001: repository packing & indexing foundation (US-010 / indexed workspace).
- EP-002: `POST /context` hybrid search + phase packing + citations (US-004 / US-015 behavior cited via US-010).
- US-008 (EP-004): conceptual dependency for IDE Ask entry — not re-specified here.
- Upstream ignore/exclusion policy from EP-001 / constitution III.

---

## Out Of Scope

- L1 blast radius, FalkorDB product, `GET /blast`, `graph.html` (V1).
- L4 Headroom compression product / token-budget dashboards (V1; ADR-006).
- L2 multi-modal graphs and L6 persistent memory (V2).
- Rename **execution** and code-execution sandbox (BRD §6; US-009).
- Inventing Confirmed Symbol proxy REST endpoints (api-contract §3).
- Re-specification of EP-001 indexing/packing or EP-002 hybrid search / phase templates / citation schema freeze.
- Full EP-004 CLI epic and Ask ContextOS <3 clicks acceptance (US-007/US-008) beyond US-010 Pack Context / safe edit plan surface needs.
- JetBrains extension (OQ-02 / ADR-007 Future).
- Exact Confirmed measurement method for Serena 99% (OQ-12) — Proposed verification only.
- Invented safe-edit-plan JSON schema or citation field names (OQ-11).
- RBAC role/schema design (OQ-01).

---

## Open Questions

| ID | Question | Blocking? | Source |
|----|----------|-----------|--------|
| **OQ-12** | Measurement method for Serena 99% definition accuracy | Non-blocking for story intent; **blocks verification design / Pass claims** | US-005; backlog OQ-12; constitution IV |
| **OQ-11** | Citation JSON shape inside `final_context` / packed Pack Context output | Non-blocking for story intent (file:line + confidence required); **blocks Confirmed citation schema freeze** | US-010; EP-002; BRD §14 |
| **OQ-Symbol-REST** | Symbol proxy REST vs MCP-only for FR-04..06 | Non-blocking if MCP-only satisfies DX; **blocks Confirmed REST contract** | api-contract §3; US-005 Notes |
| **OQ-Lang-Set** | Exact Serena language inventory beyond “12+” for AC fixtures | Non-blocking for story intent; **blocks language-complete fixture matrix** | FR-04; Missing Evidence |
| **OQ-Safe-Edit-Shape** | Exact safe edit plan response / machine shape | Non-blocking for behavioral intent; **blocks Confirmed schema freeze** | US-010; **Not evidenced** |
| **OQ-Unresolved-Symbol** | MVP behavior when symbol is unresolved/ambiguous (without V1 L1 expand) | Non-blocking; Missing Evidence for exact UX | implementation-guidelines L3→L1 V1 note |
| **OQ-MCP-Fallback** | Confirmed regex/fallback UX when Serena MCP unavailable | Non-blocking; BRD risk mentions fallback — product detail Missing Evidence | BRD §13 |
| **OQ-IDE-2s-Harness** | Verification harness for <2s symbol-accurate IDE context (composed with Ask/Pack) | Non-blocking for L3 capability delivery; **blocks composed MVP exit Pass claims** | BRD §15; US-008 shared |
| **OQ-01** | Exact RBAC roles/path/authn schema | Non-blocking for L3 MCP-local MVP intent; Missing Evidence | constitution III |

**Label rule**: OQ-12 verification remains **Proposed only**. Do **not** Confirmed-freeze Symbol REST, citation JSON (OQ-11), language inventory, or safe-edit-plan schema in this specification.

---

## Requirement Traceability

| Requirement ID | Source | Evidence |
| -------------- | ------ | -------- |
| FR-001 | US-005; FR-04; ADR-005 | Definition file:line, signature, docstring |
| FR-002 | US-005; FR-04 | 12+ languages; inventory OQ |
| FR-003 | US-005; FR-04; OQ-12; constitution IV | 99% target; Proposed verification only |
| FR-004 | US-006; FR-05 | References + 2-line context |
| FR-005 | US-006; FR-05 | File-type filter |
| FR-006 | US-009; FR-06 | Rename scope + breaking-change count |
| FR-007 | US-009; BRD §6 | IDE review; no execution sandbox |
| FR-008 | US-010; §11 | Pack Context + safe edit plan |
| FR-009 | US-010; §14; OQ-11 | Citations file:line + confidence |
| FR-010 | US-010; EP-001; EP-002 | Consume packing/index; don’t re-spec |
| FR-011 | constitution V; ADR-005 | FastAPI orchestration; VS Code DX |
| FR-012 | api-contract §3; Appendix D | Symbol REST Proposed / MCP-only OK |
| FR-013 | constitution V; ADR-005 | No silent policy bypass |
| FR-014 | BRD L3; ADR-005 | Hover docs / document symbols DX |
| FR-015 | EP-003 brief; roadmap | Explicit out-of-scope layers/surfaces |

### Acceptance Scenario → Requirement Mapping

| Scenario | Stories | Requirements |
| -------- | ------- | ------------ |
| Definition lookup returns location attributes | US-005 | FR-001, FR-002, FR-011, FR-013, FR-014 |
| 99% accuracy when method agreed / scoped gap | US-005 | FR-003 |
| Find-all-references + 2-line context | US-006 | FR-004, FR-011 |
| File-type filter on references | US-006 | FR-005 |
| Rename scope + breaking-change count; review before execute | US-009 | FR-006, FR-007 |
| Pack Context + Serena safe edit plan | US-010 | FR-008, FR-010, FR-011 |
| Citations file:line + confidence; no invented JSON | US-010 | FR-009 |
| No Confirmed invented symbol REST | US-005 Notes | FR-012 |
| Out-of-scope layers/CLI/sandbox | EP-003 brief | FR-015 |

---

## Governance Notes

- Constitution Applied: **Yes** (I Evidence-First; II L3 integrity; III privacy/provenance; IV measurable claims with OQ-12 open; V API/extension/MCP boundaries).
- Layer impact documented (L3 primary; L5 upstream cite-only).
- Security/privacy documented (ignore inheritance; no silent bypass; citations provenance).
- Blocking items for verification/schema freezes are visible; story intent remains plannable under Proposed labels.
- Ready for Plan Generator: **Yes, with open questions carried forward** — especially OQ-12 (Proposed verification only), OQ-11, Symbol REST vs MCP, safe-edit-plan shape. Do not treat those as Confirmed.
