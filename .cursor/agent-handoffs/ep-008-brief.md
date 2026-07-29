# EP-008 Brief — L4 Compression, Budgets & Telemetry

**Branch:** `feature/ep-008-l4-compression-budgets-telemetry`  
**Artifacts dir:** `specs/ep-008-l4-compression-budgets-telemetry/`  
**Stories:** US-022, US-023, US-024  
**Roadmap:** V1 L1+L4 (L1 EP-006/007 done; EP-013 OKF on main — do not redesign)

## Source of truth

| Source | What to use |
|--------|-------------|
| `docs/backlog/user-stories.md` | EP-008, US-022/023/024, OQ-07/08/09 |
| `docs/BRD_Context_OS.md` | §5 L4, FR-11..13, §10 compression NFR, §12 metrics, §15 V1 |
| `docs/architecture/architecture-overview.md` | L4 row; pipeline |
| `docs/architecture/api-contract.md` | §2.3 metrics; Proposed dashboard route |
| ADRs | ADR-006 (Headroom V1), ADR-011 (OTel), ADR-009 (HTTP surface) |

## Confirmed today (do not invent as L4)

- `POST /context` metrics keys exist: `tokens_before`, `tokens_after`, `saving_percent`, `trace` (EP-001/002 packing).
- MVP semantics = packing token estimates in `l5_phase_pack.py` — **not** full Headroom compression.
- Consent gate notes full L4 product out of scope for EP-001.
- L1 blast / graph / OKF retrieval already shipped — EP-008 consumes packs; does not redesign them.

## EP-008 must add (V1 L4)

| Story | Capability |
|-------|------------|
| US-023 | Adaptive summarization; preserve symbols/types/TODOs; 60–95% savings; recall@10 >0.92 |
| US-022 | Headroom-style per-phase budgets; hard-fail + degradation (FR-11) |
| US-024 | OTel compression ratio, recall@k, cost-saved; `contextos_token_dashboard.html` (or equivalent); meaningful metrics on compress |

## Open questions — do NOT invent Confirmed contracts

| OQ | Topic | Status |
|----|-------|--------|
| **OQ-07** | Dev budget 8k (§5) vs 12k (FR-11) | **Blocking** for numeric AC |
| **OQ-08** | Dashboard serving (static HTML vs API) | Non-blocking |
| **OQ-09** | OTel exporter / collector vendor | Non-blocking |

## Lean Spec Kit only

Produce: `spec.md`, `plan.md`, `tasks.md`, `validation-report.md`  
Do NOT create: quickstart, open-questions.md, out-of-scope-notes.md, full UI design suite (token dashboard may be minimal).

## Labeling

Always label **Confirmed** vs **Proposed** vs **Missing Evidence**. Mark OQ-07/08/09 with `[NEEDS CLARIFICATION]`.

## Agent sequence

1. Spec Writer → `spec.md`
2. Plan Generator → `plan.md`
3. Task Generator → `tasks.md`
4. Test Validation → `validation-report.md`

Graphify-first before broad exploration; `graphify update .` after substantive artifact writes.

## Implementation checklist (lead-dev)

| Stream | Tasks | Status |
|--------|-------|--------|
| UI/UX | — | N/A (minimal dashboard HTML only) |
| Backend | T001–T031, T032, T034 | In progress |
| VS Code | — | N/A |
| Frontend dashboard | T028, T031 | Via backend (Proposed static/route like graph.html) |
| Testing | T008–T028 evidence + T033 | After backend |
| Review | T036 → review-report.md | After tests |
| OQ-07 gated | T021, T037 | Skip/xfail until resolved |

Do not invent Confirmed Dev=8k/12k, OQ-08 auth, or OQ-09 exporter vendor.
