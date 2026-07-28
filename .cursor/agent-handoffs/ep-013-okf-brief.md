# EP-013 OKF Primary Knowledge — Implementation Brief

**Branch**: `feature/ep-013-okf-primary-knowledge`  
**Stories**: US-046, US-047, US-048  
**UI/UX / Frontend / VS Code**: N/A

## Locked defaults (T001–T005)

| ID | Default |
|---|---|
| OQ-OKF-01 | `CONTEXTOS_OKF_CACHE_DIR` beside pack cache; bundle `{cache}/{repo_name}/` |
| OQ-OKF-02 | Exact + token-normalized match on id/title/tags/description; no embedding for OKF hit |
| OQ-OKF-03 | No Confirmed `/index` field for OKF concept counts |
| L2-adjacent | Docs/spec concepts only; connectors remain EP-010 / OQ-03 |
| Privacy | Metadata-only bodies; IgnorePolicy before generation |

## Settings (T006)

- `okf_cache_dir`, `okf_enabled`, `okf_link_expand_limit`

## Modules

- `app/adapters/okf_bundle.py`
- `app/services/okf_generate.py`
- `app/services/okf_retrieve.py`
- Integrate generate in `l5_index.py` after eligibility (+ after L1 when present)
- Compose OKF-first in `api/context.py` before L1/L5

## Sources (FR-002)

- `docs/architecture/`
- `docs/backlog/user-stories.md`
- `specs/*/{spec,plan,tasks,validation-report,review-report}.md`
- Selected EP-006 L1 metadata summaries

## Hard constraints

- Preserve Confirmed `/index` and `/context` shapes
- OKF evidence only in `final_context` + non-sensitive `metrics.trace`
- Do not replace FalkorDB/Qdrant; no Attested Computation, blast, L4, L6, CLI, VS Code
- MCP remains stateless thin client
- Do not invent Confirmed BRD claims; label Proposed
- Do not edit `.cursor/plans/`

## Task checklist

- T001–T005: defaults (lead)
- T006–T010: foundations
- T011–T017: US-046 generate + tests
- T018–T023: US-047 retrieve + tests
- T024–T026: US-048 fallback + eval
- T027–T028: Proposed architecture + optional backlog note
- T029: Spec Kit validation already done
- T030: review-report after evidence (lead + reviewer)
