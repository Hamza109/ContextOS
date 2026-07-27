# ContextOS Constitution

## Core Principles

### I. Evidence-First SDLC Intelligence

Every feature MUST trace back to documented evidence from `docs/BRD_Context_OS.md`, approved backlog items, architecture documents, specifications, or explicit user direction.

Agents and contributors MUST NOT invent product roles, workflows, integrations, APIs, metrics, implementation status, or compliance obligations. Missing facts MUST be marked as `NEEDS CLARIFICATION`, `Not evidenced in provided inputs.`, or `Missing Evidence`.

Each specification, plan, task list, validation report, and review report MUST preserve traceability from requirement to plan, task, implementation, and verification evidence.

### II. Six-Layer Architecture Integrity

ContextOS MUST preserve the six-layer model defined by the BRD:

- L1 Structural Knowledge Graphs: dependency chains, call graphs, blast radius, affected tests, owners, and graph visualization.
- L2 Multi-modal Project Graphs: markdown, ADRs, SQL DDL, OpenAPI, diagrams, images, transcripts, and cross-artifact links.
- L3 Symbol & LSP Navigation: Serena-backed definitions, references, hover docs, rename scope, and symbol-aware edit planning.
- L4 Context Compression: token budgets, adaptive summarization, relevance scoring, recall preservation, and compression telemetry.
- L5 Context Packing & Semantic Search: repo packing, hybrid BM25/vector search, Qdrant retrieval, MMR ranking, and phase-aware prompt assembly.
- L6 Persistent Agent Memory: entity memory, temporal edges, provenance, recall explanation, TTL, decay, pin/forget, and PII redaction.

Plans and tasks MUST explicitly identify affected layers. Implementation MUST keep layer responsibilities separate and MUST NOT duplicate backend orchestration logic inside the VS Code extension or UI.

### III. Privacy, Security, And Local-First Indexing

ContextOS MUST protect repository content by default.

Mandatory controls:

- Respect `.gitignore`.
- Exclude `.env`, secrets, build outputs, dependency folders, and binary artifacts unless explicitly approved.
- Do not send source code to external LLM providers during indexing.
- Query-time external LLM use requires explicit consent/configuration.
- Preserve source provenance for context, graph, search, memory, and compression outputs.
- Support RBAC per repo path where authorization applies.
- Redact PII in memory and multi-modal ingestion paths.
- Store secrets only through approved secure storage.
- Validate and sanitize Webview messages and backend responses.

Security-sensitive features MUST include threat/risk notes in plans and validation reports.

### IV. Measurable Intelligence Claims

Any feature that claims search quality, graph accuracy, compression savings, memory recall, token savings, latency, indexing speed, or blast-radius correctness MUST define measurable acceptance criteria and validation tasks.

BRD targets SHOULD be used when applicable:

- Semantic search p95 <800ms for a 500k LOC index.
- Blast-radius graph query p95 <2s for 3-hop / 10k nodes where applicable.
- Token compression 60-95% with recall@10 >0.92 where applicable.
- Full index <15 minutes for 1M LOC and delta index <60s where applicable.
- Cross-session memory recall >90% with <1.2s p95 where applicable.
- IDE workflow under 3 clicks to Ask ContextOS where applicable.

If a feature cannot yet meet the BRD target, the spec and plan MUST state the scoped target for the increment and explain the gap.

### V. Extension, API, CLI, And UI Boundary Discipline

The FastAPI orchestrator owns indexing, graph, search, compression, memory, security policy enforcement, and OpenAPI contracts.

The VS Code extension owns developer experience: commands, sidebar, Webviews, CodeLens, hover providers, status bar, settings, progress/cancellation, offline states, and secure API communication.

The CLI owns scriptable developer workflows and MUST return useful human-readable output and machine-readable output when planned.

Dashboards and Webviews own presentation, filtering, exploration, and feedback states. They MUST show provenance, freshness/staleness, confidence, error states, and safety warnings where relevant.

No client surface may silently bypass backend validation, consent checks, RBAC, indexing policy, or telemetry opt-out.

## Project Constraints

### Approved Technical Direction

Unless superseded by an approved architecture decision, ContextOS uses:

- FastAPI + Python 3.11 for the orchestrator/API.
- FalkorDB for structural graph storage.
- Qdrant for vector search.
- `sentence-transformers/all-MiniLM-L6-v2` local CPU embeddings.
- Serena MCP for LSP/symbol navigation.
- Repomix-style repository packing.
- Headroom-style context compression.
- Cognee-style persistent memory.
- React Flow or vis-network for graph visualization.
- OpenTelemetry-compatible observability.
- VS Code extension as the primary IDE surface for MVP.

New frameworks, stores, hosted services, or LLM providers require an explicit architecture decision and must document privacy, security, cost, and operational impact.

### Roadmap Governance

Delivery SHOULD follow the BRD roadmap:

- MVP: L5 + L3, CLI, VS Code extension, basic prompt packing, indexing basics.
- V1: L1 + L4, graph/blast-radius, graph visualization, compression telemetry, PR risk support.
- V2: L2 + L6, multi-modal graph, persistent memory, memory governance, RBAC/VPC hardening.

Changing this order requires an explicit rationale in the plan and validation report.

### Documentation And Artifact Requirements

Planning artifacts MUST use Spec Kit structure:

- `specs/<feature-name>/spec.md`
- `specs/<feature-name>/plan.md`
- `specs/<feature-name>/tasks.md`
- `specs/<feature-name>/validation-report.md`

Architecture artifacts SHOULD live under `docs/architecture/`.

Backlog artifacts SHOULD live under `docs/backlog/`.

Design artifacts SHOULD live under `docs/design/<feature-name>/` when user-facing UI exists.

Agent handoffs SHOULD be appended to `.cursor/agent-handoffs/handoff.md` when agent workflows delegate work.

## Development Workflow And Quality Gates

### Specification Gate

A feature specification is ready only when:

- User scenarios are prioritized and independently testable.
- Functional requirements are atomic and traceable.
- ContextOS layer and surface impact are documented.
- Security/privacy implications are documented or marked not applicable.
- Success criteria are measurable or marked `NEEDS CLARIFICATION`.
- Blocking open questions are visible.

### Planning Gate

An implementation plan is ready only when:

- Technical context is based on evidence or clearly marked as proposed.
- Affected layers, APIs, stores, extension surfaces, UI surfaces, and telemetry are identified.
- Security, privacy, performance, and reliability considerations are documented.
- Testing strategy covers the feature's measurable claims.
- Architecture deviations are justified.

### Task Gate

A task list is ready only when:

- Every requirement has implementation and verification coverage.
- Tasks are grouped by independently deliverable user story.
- Tasks include exact paths when known.
- Unknown paths or architecture gaps become discovery tasks.
- Tests are included for affected ContextOS intelligence claims.
- Security, documentation, telemetry, and deployment tasks are included where applicable.

### Implementation Gate

Implementation is ready for review only when:

- Code follows approved architecture and existing project patterns.
- Backend, extension, CLI, and UI boundaries are respected.
- OpenAPI/contracts and client integrations are synchronized.
- Source provenance, consent, RBAC, PII, and ignore-file behavior are preserved where applicable.
- Observability and error handling are implemented where applicable.
- Documentation is updated.

### Verification Gate

Validation MUST distinguish planned, implemented, executed, passed, failed, skipped, and blocked tests.

Tests MUST NOT be claimed as passing without command output, CI evidence, or test reports.

PR readiness MUST NOT be approved when implementation files, test evidence, build/lint evidence, security review, or deployment evidence are missing for a feature that requires them.

## Governance

This constitution supersedes generic agent behavior and default Spec Kit examples for this repository.

All agents and contributors MUST check this constitution before generating specs, plans, tasks, validation reports, implementation handoffs, or PR readiness reports.

Amendments require:

- A documented reason.
- A summary of affected agents/templates/artifacts.
- Migration notes for existing specs/plans/tasks if behavior changes.
- Version increment using semantic versioning.

Compliance MUST be evaluated in `validation-report.md` and `review-report.md`.

**Version**: 1.0.0 | **Ratified**: 2026-07-27 | **Last Amended**: 2026-07-27
