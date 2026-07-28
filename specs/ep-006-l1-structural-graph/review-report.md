# Review Report: EP-006 L1 Structural Graph Generation

## Summary

- **Date**: 2026-07-28
- **Branch**: `feature/ep-006-l1-structural-graph`
- **Scope**: US-017 L1 structural graph generation and US-021 FastAPI-owned hot-entity structural query enrichment.
- **Decision**: **Ready for PR with comments** with residual risks documented below.

## Implementation Reviewed

- L1 parser, FalkorDB adapter, graph orchestration, entity cache, and structural query enrichment under `services/orchestrator/app/`.
- Existing `POST /index`, `POST /context`, health, configuration, telemetry, and Docker Compose integration.
- MCP regression behavior in `clients/mcp/tests/formatAskPack.test.ts`; MCP remains stateless.
- Architecture and Spec Kit artifacts under `docs/architecture/` and `specs/ep-006-l1-structural-graph/`.

## Verification Evidence

| Check | Result |
|---|---|
| Full orchestrator suite | `137 passed, 9 skipped, 13 warnings` |
| CI-shaped orchestrator Ruff | Passed with intentional L1 structural fixture corpus excluded |
| CI-shaped orchestrator pytest | `137 passed, 6 skipped, 3 deselected, 13 warnings` |
| VS Code extension lint/tests | TypeScript no-emit passed; Vitest `10` files passed, `38 passed | 1 skipped` |
| EP-006 focused parser/accuracy regression | `11 passed` |
| EP-006 changed-file Ruff | Passed |
| MCP tests/build | Vitest `4 passed`; TypeScript build passed |
| Live FalkorDB integration | Passed |
| Compose API/Qdrant/FalkorDB smoke | `1 passed in 5.96s` |
| Graph/query eval fixtures | Precision/recall/F1 `1.0` on synthetic fixtures |
| 100-file delta harness | `0.0706s`, 500 graph nodes, embeddings skipped |
| 1M-LOC full-index harness | Skipped; no approved corpus |

## Findings

- No blocking implementation defect remains after fixing Python sibling relative import resolution to produce File→File `IMPORTS` edges.
- No stale-graph blocker remains after fixing scoped L1 re-index context and full re-index stale relationship cleanup.
- Public API shape is preserved: no new endpoint or response field was added for `/index` or `/context`.
- Blast analysis and visualization remain excluded for EP-007.
- Ignore/no-exfiltration behavior is preserved before L1 parsing and persistence.
- FalkorDB/cache/telemetry store metadata and provenance only; no full source bodies are persisted.

## Residual Risks

- Qdrant client `1.18.0` warns against the running server `1.12.5`; tests pass, but deployment versions should be aligned.
- 1M-LOC full-index timing is unverified until an approved corpus is available.
- Accuracy and latency evidence uses small deterministic fixtures; it is not a broad production-quality claim.
- CI Ruff excludes the intentional structural source fixture corpus because it contains malformed/sample source by design.
- Docker disk usage should be monitored because the first failed build exhausted local storage before CPU-only Torch caching was added.

## Recommendation

Proceed to PR. Do not merge until the PR reviewer accepts the residual risks or they are split into follow-up tasks.
