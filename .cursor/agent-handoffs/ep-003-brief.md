# EP-003 Brief — L3 Symbol & LSP Navigation (Serena)

**Branch:** `feature/ep-003-l3-symbol-lsp-navigation` (off main @ 188a0a5 with EP-001+EP-002)  
**Folder:** `specs/ep-003-l3-symbol-lsp-navigation/`  
**Stories:** US-005, US-006, US-009, US-010 only  
**Lean artifacts ONLY:** spec.md → plan.md → tasks.md → validation-report.md  
**Do NOT generate:** quickstart.md, open-questions.md, out-of-scope-notes.md, docs/design/*

## Traceability checklist

| ID | Title | FR / evidence | Notes |
|----|-------|---------------|-------|
| US-005 | Symbol Definition Lookup | FR-04; §15; ADR-005 | OQ-12 (99% measure) open — Proposed verification only |
| US-006 | Find All References | FR-05 | 2 lines before/after; file-type filter; dep US-005 |
| US-009 | Rename Scope Analysis | FR-06 | Analysis only; no execution sandbox (BRD §6) |
| US-010 | Pack Context & Safe Edit Plan | §11 Dev; §14; FR-03..06 | Deps US-004/005/008; cite EP-001/002, don’t re-spec |

## Architecture boundaries (Confirmed)

- ADR-005: Serena MCP for definition/references/hover/rename-scope; extension surfaces; orchestrator may call Serena in context pipeline.
- ADR-002 / constitution V: FastAPI owns orchestration; VS Code owns DX (hover/commands). Extension must NOT reimplement search/index/symbol policy.
- api-contract §3: Symbol proxy REST is Proposed / may remain MCP-only — `[NEEDS CLARIFICATION]`; do not invent Confirmed REST.
- Appendix D Confirmed HTTP: GET /, POST /index, POST /context, GET /blast, GET /graph.html — no invented L3 REST.

## Upstream deps (cite, don’t re-spec)

- EP-001: indexing / pack foundation
- EP-002: `POST /context` hybrid search + phase packing + citations (OQ-11 shared)
- US-008 (Ask <3 clicks / <2s) is EP-004 surface — US-010 depends conceptually; do not expand full CLI/Ask epic

## Out of scope for this Spec Kit

- L1 blast / FalkorDB product, L4 Headroom product, L2/L6
- Full EP-004 CLI epic beyond what US-010 needs for Pack Context / safe edit plan surface
- Rename execution sandbox; JetBrains; inventing Confirmed symbol REST

## Open questions to carry (label Proposed / NEEDS CLARIFICATION)

| OQ | Topic | Blocking? |
|----|-------|-----------|
| OQ-12 | Serena 99% accuracy measurement method | Non-blocking for story intent; blocks verification design |
| OQ-11 | Citation JSON shape in final_context | Non-blocking; shared with EP-002 |
| — | Symbol REST vs MCP-only | NEEDS CLARIFICATION (api-contract §3) |
| — | Exact Serena language set beyond “12+” | Missing Evidence if needed for AC fixtures |
| — | Safe edit plan response shape | Not evidenced — Proposed only |

## Mandatory reads for agents

1. `.specify/memory/constitution.md`
2. `.cursor/rules/lean-spec-kit-artifacts.mdc`
3. `docs/backlog/user-stories.md` (EP-003 + US-005/006/009/010)
4. `docs/architecture/` overview, api-contract, ADR-005, tech-stack, implementation-guidelines
5. `docs/BRD_Context_OS.md` FR-04..06 / L3 only as cited
6. `.specify/templates/` + lean style from `specs/ep-002-l5-hybrid-search-phase-packing/`

## Graphify

Docs-only Spec Kit OK. Before app-code exploration: `graphify query`. After code changes: `graphify update .` (unlikely this phase).
