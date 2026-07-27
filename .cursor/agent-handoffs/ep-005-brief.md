# EP-005 Brief — Privacy Defaults, Health & Consent

**Branch:** `feature/ep-005-privacy-health-consent` (off main @ f24dedf; EP-001..EP-004 merged)  
**Feature folder:** `specs/ep-005-privacy-health-consent/`  
**Stories:** **US-013, US-014 only** (US-016 query-time LLM consent is **out of this Spec Kit**)  
**Business:** Protect repo content by default; keep search available under partial failure (Security / DevOps trust for POC)

## Mandatory cites (do not re-spec)

| Source | What to use |
|--------|-------------|
| `.specify/memory/constitution.md` | STRICT — esp. III privacy; V client boundaries |
| `docs/backlog/user-stories.md` | EP-005, US-013, US-014, A-07 |
| `docs/BRD_Context_OS.md` | §10 Code access & PII / indexer availability; Appendix C; Appendix D `GET /` |
| `docs/architecture/api-contract.md` | §2.1 GET /; ignore/privacy on index; Proposed status codes |
| ADR-012 | Privacy defaults Confirmed; RBAC schema open |
| `docs/architecture/tech-stack.md` | Approved stack only |
| `docs/architecture/implementation-guidelines.md` | Layer/surface boundaries |
| EP-001 | Indexing + privacy defaults foundation — cite |
| EP-002 | Hybrid search / POST /context — cite; degraded search builds on |
| EP-004 | CLI/Ask surfaces — cite; must not bypass ignore policy |

## Graphify (pre-explore)

- Nodes of interest: `IgnorePolicy`, `walk_allowed_files`, `consent_gate` (US-016 adjacent — cite only), health router, `hybrid_search`, degraded/partial-index tests

## Existing code (cite; gap-fill only)

- `services/orchestrator/app/security/ignore_policy.py` — IgnorePolicy
- `services/orchestrator/app/adapters/fs_walker.py` — walk_allowed_files
- `services/orchestrator/app/api/health.py` — GET /
- `services/orchestrator/app/api/index.py` + `l5_index.py` / `l5_pack.py`
- `services/orchestrator/app/services/l5_search.py` — search degradation hooks if any
- `clients/vscode/`, `clients/cli/` — thin; MUST NOT bypass orchestrator ignore policy
- Tests: `test_ignore_policy.py`, `test_packer_exclusions.py`, `test_index_exclusions_qdrant.py`, etc.

## Hard constraints

- US-013: `.gitignore` + exclude `.env`/secrets/build/deps/binaries; clients no bypass. Explicit “approved override” UX = **Not evidenced / Proposed only** — no Confirmed freeze
- US-014: `GET /` health (pipeline + Qdrant; Falkor absent/unused OK per A-07); graceful degraded search on partial failure. HTTP status mapping = **Proposed** if not Confirmed in api-contract
- Do NOT invent unsupported APIs, roles, metrics, or Pass/Fail
- Do NOT expand: JetBrains, L1/L4 (V1), L2/L6 (V2), EP-004 rebuild, full RBAC/enterprise consent, **US-016**
- FastAPI owns policy/health; clients thin
- Label Proposed vs Confirmed; no Confirmed freeze of open OQs
- Lean Spec Kit ONLY: `spec.md`, `plan.md`, `tasks.md`, `validation-report.md`
- No quickstart / open-questions / out-of-scope-notes / ui-not-applicable files
- OQs/OOS live inside spec/plan/validation only
- Docs-first Spec Kit OK; do not write application code

## Workflow

1. spec-writer → spec.md ✅  
2. plan-generator → plan.md ✅  
3. task-generator → tasks.md ✅ (T001–T036)  
4. test-validation-agent → validation-report.md ✅ — **Conditionally Approved (8.8/10)**; Ready Yes w/ conditions  
5. lead-developer-agent ← **next** (gap-fill T001–T036; no OQ Confirmed freezes; no SC-007 Pass)  
Stay on `feature/ep-005-privacy-health-consent`; no push/merge to main
