# ContextOS Agent Fit Analysis

## Source Reviewed

- `docs/BRD_Context_OS.md`
- `.cursor/agents/*.md`

## BRD Summary

ContextOS is a six-layer SDLC intelligence platform that gives AI coding assistants persistent, compressed, graph-aware project context.

The BRD defines these core layers:

- L1 Structural Knowledge Graphs for dependency chains, call graphs, blast radius, and affected tests.
- L2 Multi-modal Project Graphs for code, docs, SQL, OpenAPI, diagrams, and transcripts.
- L3 Symbol & LSP Navigation through Serena for definitions, references, hover docs, and safe refactoring scope.
- L4 Context Compression for token budgets, summarization, recall preservation, and cost telemetry.
- L5 Context Packing & Semantic Search for repo packing, hybrid BM25/vector search, Qdrant retrieval, and prompt assembly.
- L6 Persistent Agent Memory for entity memory, temporal edges, provenance, TTL, pin/forget, and PII redaction.

The roadmap is:

- MVP: L5 + L3, CLI, VS Code extension, basic prompt packing.
- V1: L1 + L4, blast radius, graph visualization, compression telemetry, PR risk support.
- V2: L2 + L6, multi-modal graph, persistent memory, RBAC/VPC hardening.

## Most Useful Agents

### Required Planning Agents

- `brd-analysis-agent`: useful as the entry-point coordinator for BRD analysis, architecture creation, and backlog generation.
- `solution-architect-agent`: essential for six-layer architecture, FastAPI orchestration, graph/vector/memory stores, API contracts, security, deployment, and observability.
- `user-story-generator`: essential for converting BRD requirements into traceable epics and user stories.
- `product-manager-agent`: useful after backlog approval to coordinate Spec Kit specs, plans, tasks, and validation.
- `spec-writer-agent`: useful for converting approved user stories into feature specs.
- `plan-generator-agent`: useful for turning specs into implementation plans.
- `task-generator-agent`: useful for producing traceable implementation tasks.
- `test-validation-agent`: useful for checking planning readiness before implementation.

### Required Implementation Agents

- `lead-developer-agent`: useful as implementation coordinator once `spec.md`, `plan.md`, and `tasks.md` exist.
- `backend-agent`: essential for FastAPI, indexing, Qdrant, FalkorDB, Serena integration, compression, memory, API contracts, security, and telemetry.
- `vscode-extension-engineer`: essential because the BRD makes VS Code a primary MVP surface.
- `frontend-agent`: useful for Webviews, graph explorer, token dashboard, search panels, and memory explorer.
- `ui-ux-design-agent`: useful for implementation-ready designs for operational developer tooling, dashboards, and extension surfaces.
- `testing-agent`: essential for validating search relevance, graph accuracy, symbol resolution, compression recall, memory governance, extension behavior, API contracts, security, and performance.
- `review-pr-readiness-agent`: useful for final evidence-based PR readiness review.

## Lower-Priority Or Conditional Agents

No current agent is useless, but some are conditional:

- `frontend-agent` is only needed for dashboard/Webview/browser UI work.
- `ui-ux-design-agent` is only needed when a feature has a user-facing UI.
- `review-pr-readiness-agent` should run only after implementation and test evidence exist.
- `test-validation-agent` validates planning only; it must not be treated as executed test proof.

## Adjustments Made

- Added ContextOS-specific guardrails to planning, architecture, spec, plan, task, backend, frontend, extension, UI/UX, testing, validation, and PR review agents.
- Added six-layer terminology and responsibilities across relevant agents.
- Added BRD-approved stack guidance: FastAPI, Python 3.11, FalkorDB, Qdrant, local `all-MiniLM-L6-v2` embeddings, Serena, Repomix-style packing, Headroom-style compression, Cognee-style memory, React Flow/vis-network, and OpenTelemetry.
- Added security constraints: `.gitignore` respect, `.env` exclusion, RBAC per repo path, PII scrubbing, source provenance, and no code exfiltration without consent.
- Added roadmap guidance so agents preserve MVP L5+L3, V1 L1+L4, and V2 L2+L6.
- Updated `lead-developer-agent` to include `vscode-extension-engineer` as a first-class implementation sub-agent.
- Fixed the BRD analysis agent's solution architect handoff path from `.cursor/rules/...` to `.cursor/agents/...`.
- Replaced the placeholder Spec Kit constitution at `.specify/memory/constitution.md` with ContextOS-specific governance.
- Updated Spec Kit spec, plan, and tasks templates to include ContextOS layer impact, affected surfaces, privacy/security controls, observability, and measurable intelligence validation.

## Constitution Review

The original `.specify/memory/constitution.md` was still the default placeholder and was not suitable for this project.

It has been replaced with a ContextOS constitution covering:

- Evidence-first requirements and anti-hallucination rules.
- Six-layer architecture integrity.
- Privacy, security, local-first indexing, RBAC, PII redaction, and no code exfiltration without consent.
- Measurable acceptance criteria for search, graph, compression, memory, indexing, latency, and blast-radius claims.
- Backend/API, CLI, VS Code extension, dashboard, and Webview responsibility boundaries.
- Spec Kit quality gates for specification, planning, tasks, implementation, and verification.

## Recommended Workflow

1. Run `brd-analysis-agent` on `docs/BRD_Context_OS.md`.
2. Let it generate architecture artifacts through `solution-architect-agent`.
3. Let it generate `docs/backlog/user-stories.md` through `user-story-generator`.
4. Use `product-manager-agent` for one approved story at a time.
5. Use `lead-developer-agent` only after spec, plan, tasks, and planning validation exist.
6. Route extension-specific work to `vscode-extension-engineer`, backend orchestration to `backend-agent`, dashboard/Webview work to `frontend-agent`, and validation to `testing-agent`.
