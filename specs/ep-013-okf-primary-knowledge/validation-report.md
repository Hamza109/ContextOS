# Validation Report: EP-013 OKF Primary Knowledge Format

## Executive Summary

| Field | Value |
|-------|-------|
| **Feature Name** | EP-013 OKF Primary Knowledge Format (`ep-013-okf-primary-knowledge`) |
| **Review Date** | 2026-07-28 |
| **Reviewer** | Spec Kit validation (planning readiness) |
| **Stories in scope** | US-046, US-047, US-048 (Proposed backlog extensions) |
| **Overall Status** | **APPROVED for implementation planning** |
| **Overall Readiness Score** | **9.0 / 10** |
| **Implementation Readiness Decision** | **Yes** — Ready to implement with documented Proposed labels and residual risks |
| **Constitution Applied** | Yes (I–V + Roadmap Governance) |

**Planning validation** (section below through Constitution Gate Summary) covers **Spec Kit triad readiness only** and remains **APPROVED**. A separate **Runtime Evidence** section records executed pytest/vitest results. T030 complete: see `review-report.md` (**PR ready: Yes with comments**).

---

## Evidence Reviewed

| Artifact | Role | Status |
|----------|------|--------|
| `specs/ep-013-okf-primary-knowledge/spec.md` | Feature specification | Reviewed |
| `specs/ep-013-okf-primary-knowledge/plan.md` | Implementation plan | Reviewed |
| `specs/ep-013-okf-primary-knowledge/tasks.md` (T001–T030) | Task breakdown | Reviewed |
| Google OKF SPEC v0.2 | External format reference | Reviewed (fetched 2026-07-28) |
| `.specify/memory/constitution.md` v1.0.0 | Governance | Reviewed |
| Lean Spec Kit rule | Artifact set | Pass — only required files |
| `docs/architecture/architecture-overview.md` | Layer/API baseline | Reviewed |
| `docs/architecture/api-contract.md` §2.2–§2.3 | Confirmed endpoints | Reviewed |
| `docs/backlog/user-stories.md` | Roadmap / epic inventory | Reviewed — EP-013 not yet listed (OQ-OKF-04) |
| EP-006 Spec Kit | L1 dependency pattern | Reviewed |
| Graphify query on retrieval path | Repo navigation | Executed |
| `services/orchestrator/app/api/context.py` | Current `/context` composition | Present |
| Existing L5/L1 services | Upstream dependencies | Present |

**Planning-time note (preserved):** at Spec Kit approval, no runtime test execution evidence existed.

**Runtime update (2026-07-28):** see **Runtime Evidence** section — orchestrator OKF/L1/L5 suites and MCP vitest executed; no inferred passes.

---

## Missing Evidence

| Item | Classification | Impact |
|------|----------------|--------|
| Executed OKF generate/retrieve tests | **Resolved (runtime)** | See Runtime Evidence — unit/integration/contract executed |
| CI/build/lint for this feature | Missing Evidence | Local pytest/vitest only; CI not claimed this pass |
| Confirmed BRD requirement naming OKF | Not evidenced | Correctly labeled **Proposed / user-directed** |
| Backlog entries EP-013 / US-046–048 | Partial (T028 note) | Sync note may exist; not Confirmed BRD |
| Production OKF latency/quality corpus | Missing Evidence | Fixture eval only; no production Pass |
| Attested Computation runtime | Out of scope | Explicitly deferred |
| Exact confidence threshold beyond token match | Proposed default (OQ-OKF-02) | Non-blocking |
| `review-report.md` (T030) | **Resolved** | Written 2026-07-28 — PR ready Yes with comments |

---

## Specification Findings

| Check | Result | Evidence |
|-------|--------|----------|
| Required Spec Kit sections | **Pass** | Scenarios, FRs, entities, ContextOS Impact, NFRs, SC, Assumptions, Dependencies, OOS, OQs, Traceability |
| User scenarios prioritized & independently testable | **Pass** | US-046/047/048 with Independent Test + Given/When/Then |
| FRs atomic & testable | **Pass** | FR-001..FR-010 |
| Proposed vs Confirmed labeling | **Pass** | OKF extension labeled Proposed; API Confirmed shapes preserved |
| Six-layer / surface impact | **Pass** | L5 affected; L1 dependency; L2-adjacent only; clients thin |
| Privacy / no-exfil | **Pass** | FR-009; metadata-only bodies |
| Success criteria measurable or labeled | **Pass** | SC-001..SC-005; no pre-execution pass claims |
| No template placeholders | **Pass** | Clean |
| Lean artifact set | **Pass** | No quickstart/open-questions adjunct files |

### Gaps (non-blocking)

1. Stories US-046–US-048 are not yet in `docs/backlog/user-stories.md` — tracked as OQ-OKF-04 / T028.
2. Roadmap: user-directed OKF precedes full V2 L2 connectors; plan correctly forbids claiming EP-010 done.

### Blocking for story intent?

**No.** Open questions have plan defaults; Confirmed API contracts are unchanged.

---

## Planning Findings

| Check | Result | Evidence |
|-------|--------|----------|
| Every FR addressed | **Pass** | Traceability matrix in tasks.md |
| Components defined | **Pass** | `okf_bundle`, `okf_generate`, `okf_retrieve`, index/context integration |
| Data model | **Pass** | OKF concept/bundle; no Confirmed API field change |
| Retrieval precedence | **Pass** | OKF → L1 → BM25/vector |
| Privacy obligations | **Pass** | IgnorePolicy-before-generation |
| Testing strategy | **Pass** | Unit/integration/contract/security/eval planned |
| Performance claims gated | **Pass** | Measure-only harnesses |
| Out of scope clear | **Pass** | No store replacement, connectors, blast, Attested Computation |

---

## Task Findings

| Check | Result | Evidence |
|-------|--------|----------|
| Tasks cover US-046/047/048 | **Pass** | Phases 3–5 |
| Discovery defaults first | **Pass** | T001–T005 |
| Tests before/with implementation | **Pass** | T011–T013 before T014–T015; T018–T020 before T021 |
| Contract preservation tasks | **Pass** | T013, T019, SC-005 |
| Fallback regression tasks | **Pass** | T024–T025 |
| Validation/review sequencing | **Pass** | T029 Spec Kit now; T030 review after impl |

---

## Constitution Gate Summary

| Gate | Result |
|------|--------|
| I Evidence-first | **Pass** — user direction + OKF SPEC cited; BRD invent avoided |
| II Layer integrity | **Pass** — L5/L1 roles preserved; L2 not over-claimed |
| III Privacy | **Pass** — FR-009 + metadata-only |
| IV Measurable claims | **Conditional (planning)** → **Runtime: fixture measurements recorded** (see Runtime Evidence; no production SLA Pass) |
| V Boundaries | **Pass** — FastAPI owns OKF; MCP thin |
| Roadmap | **Pass with note** — Proposed user-directed; no V2 connector completion claim |

---

## Residual Risks

1. Backlog not yet updated with EP-013 stories.
2. Matching quality may be weak until eval harness iterates beyond exact/token match.
3. Generator coverage limited to docs/specs/L1 metadata — not full repo wiki synthesis.
4. Implementation must keep L5 fallback hard-tested to avoid search regressions.

---

## Decision (Planning — preserved)

**APPROVED** — Spec Kit triad is implementation-ready (2026-07-28 planning validation).

Authorized next step at planning time: implement T001–T026 on `feature/ep-013-okf-primary-knowledge` without editing Confirmed API contracts. After tests, produce `review-report.md` (T030).

**Planning-time runtime execution status**: Planned / Not Executed.

---

## Runtime Evidence (T030 prep — testing-agent)

| Field | Value |
|-------|-------|
| **Execution Date** | 2026-07-28 |
| **Executor** | testing-agent |
| **Branch** | `feature/ep-013-okf-primary-knowledge` |
| **Runtime status** | **Executed** — suites below; no inferred passes |
| **Defects fixed this pass** | None (no product/test defects found) |
| **T030** | **Complete** — `review-report.md` present; PR ready Yes with comments |
| **Constitution IV** | Measurements recorded for opt-in OKF eval; no SLA Pass invented |

### Commands executed

Working directory: `services/orchestrator` (unless noted). Interpreter: `.venv/bin/python -m pytest`.

| Suite | Command | Result |
|-------|---------|--------|
| OKF unit | `pytest tests/unit/test_okf_bundle.py tests/unit/test_okf_generate.py tests/unit/test_okf_retrieve.py tests/unit/test_okf_telemetry.py -q` | **11 passed** |
| OKF integration + security + contract | `pytest tests/integration/test_index_okf.py tests/integration/test_context_okf.py tests/integration/test_index_no_exfil.py tests/contract/ -q` | **24 passed** (combined with unit above as **35 passed** in one re-confirm run) |
| L1/L5 regression subset | `pytest tests/unit/test_l1_*.py tests/integration/test_context_l1_structural.py tests/integration/test_index_l1_graph.py tests/integration/test_context_hybrid_signals.py -q` | **24 passed, 1 skipped** (`test_index_l1_graph` live FalkorDB: set `CONTEXTOS_FALKORDB_INTEGRATION=1`) |
| Opt-in OKF eval | `CONTEXTOS_OKF_RETRIEVAL_EVAL=1 pytest tests/eval/test_okf_retrieval.py -s` | **1 passed** |
| Full orchestrator (non-perf) | `pytest -q -m "not perf"` | **154 passed, 7 skipped, 3 deselected** |
| MCP (T020 thin client) | `cd clients/mcp && npx vitest run` | **4 passed** (`formatAskPack.test.ts`) |

**Note**: Full-suite runs inside the Cursor sandbox can fail with `PermissionError` on temp fixture `.git/config`; unsandboxed / `required_permissions: all` run is the authoritative evidence (**154 passed**).

### Opt-in eval measurements (fixture only)

Stdout from `tests/eval/test_okf_retrieval.py` (`dataset_revision=okf-retrieval-eval-v1`):

```text
grounding: precision=1.0 recall=1.0 f1=1.0
fallback_miss_cases: 1
latency_ms: p50≈1.34 p95≈1.34 (fixture-scale only; not an SLA claim)
```

Without `CONTEXTOS_OKF_RETRIEVAL_EVAL=1`, the same test is **skipped** in the default full suite (counted in the 7 skips).

### Success criteria (evidence only)

| SC | Status | Evidence |
|----|--------|----------|
| SC-001 | **Pass (executed)** | `test_index_fixture_writes_okf_with_provenance_and_exclusions`; unit `test_generate_emits_frontmatter_provenance_and_links` |
| SC-002 | **Pass (executed)** | `test_context_okf_hit_with_embeddings_stubbed` |
| SC-003 | **Pass (executed)** | `test_context_okf_miss_falls_back_to_hybrid`; `test_qdrant_indexing_remains_when_okf_enabled` |
| SC-004 | **Pass (executed)** | `test_excluded_paths_never_become_sources`; `test_index_no_exfil_with_and_without_consent` OKF secret assertions |
| SC-005 | **Pass (executed)** | `tests/contract/test_index_contract.py`, `test_context_contract.py`; `test_index_http_confirmed_four_fields_unchanged` |

### Full-suite skips (not claimed as pass)

| Skip | Reason |
|------|--------|
| `test_okf_retrieval.py` | Opt-in: set `CONTEXTOS_OKF_RETRIEVAL_EVAL=1` (executed separately above) |
| `test_l1_structural_queries.py` | Opt-in L1 eval |
| `test_l3_definition_accuracy_oq12.py` | BLOCKED OQ-12 |
| `test_l3_ide_2s_harness_blocked.py` | BLOCKED OQ-IDE-2s |
| `test_context_recall_at_10.py` | BLOCKED OQ-recall-harness |
| `test_index_l1_graph` live FalkorDB | Opt-in `CONTEXTOS_FALKORDB_INTEGRATION=1` |
| `test_l1_compose_smoke.py` | Opt-in Compose smoke |

### Residual risks (runtime)

1. OKF match quality beyond fixture exact/token cases unproven (OQ-OKF-02 lexical only).
2. Eval P/R/F1=1.0 is synthetic fixture-scale only — not production corpus.
3. Live FalkorDB / Compose smoke not executed this pass (skipped).
4. Qdrant client/server version warning remains deployment hygiene risk.
5. CI green on this branch not yet verified (review residual).

### Runtime decision for lead

- Implementation test evidence for US-046/047/048 is **executed and green** on this branch.
- T030 complete — see `review-report.md` (**PR ready: Yes with comments**).
- Next: open PR when requested; verify CI on branch.
