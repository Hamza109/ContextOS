# EP-001 Quickstart — L5 Packing & Indexing

Local POC: FastAPI orchestrator + Qdrant. FalkorDB optional/unused for EP-001 (`graph_nodes=0`).

## Prerequisites

- Docker + Docker Compose
- Python 3.11+ (for local uvicorn without Docker)
- ~90MB disk for `sentence-transformers/all-MiniLM-L6-v2` model weights (downloaded on first embed)

## Compose up

```bash
cd deploy
docker compose up -d qdrant
# API image builds with model deps — first build is slow
docker compose up -d --build api
```

Health:

```bash
curl -s http://localhost:8000/
# Expect status ok|degraded; qdrant ok when Qdrant is up; falkor "unused"
```

## Index a repository

Confirmed request/response only:

```bash
curl -s -X POST http://localhost:8000/index \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/absolute/path/to/repo","repo_name":"my-repo"}'
```

Example response:

```json
{"files_indexed":12,"graph_nodes":0,"embeddings":40,"time_ms":1234}
```

### Proposed incremental scope (OQ-14 — not Confirmed)

```bash
curl -s -X POST http://localhost:8000/index \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/abs/repo","repo_name":"my-repo","files":["src/a.py"]}'
```

## Local uvicorn (without API container)

```bash
cd services/orchestrator
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export CONTEXTOS_QDRANT_URL=http://localhost:6333
export CONTEXTOS_PACK_CACHE_DIR=/tmp/contextos/packs
uvicorn app.main:app --reload --port 8000
```

## Proposed env keys

| Key | Default | Notes |
|-----|---------|-------|
| `CONTEXTOS_QDRANT_URL` | `http://localhost:6333` | Proposed |
| `CONTEXTOS_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Confirmed model |
| `CONTEXTOS_PACK_CACHE_DIR` | `/tmp/contextos/packs` | Proposed (OQ-PACK) |
| `CONTEXTOS_LOCAL_INFERENCE_URL` | unset | Proposed Ollama hook (FR-020); not used by `/index` |
| `CONTEXTOS_EXTERNAL_LLM_CONSENT` | `false` | Proposed deny-by-default flag (OQ-US016) |

## CI (GitHub Actions)

Minimal workflow: `.github/workflows/ci.yml`

- **Orchestrator:** ruff + `pytest -m "not perf"` with Qdrant service (T035 live upsert)
- **VS Code:** `npm ci`, `npm run lint` (tsc), `npm test` (vitest)

Out of this workflow: T081/T082 perf corpora, live MiniLM download, Extension Host E2E.

## Rollback

- Disable extension auto-index/save triggers (extension side).
- `docker compose down` in `deploy/` — tear down API + Qdrant.
- No destructive Qdrant wipe required to roll back triggers; optional volume remove only if resetting index data intentionally.

## Out of scope (EP-001)

Hybrid search, Serena/L3, L1 graph writes, L4 compression product, L2/L6, invented Confirmed endpoints.

## Open questions

See `open-questions.md` — OQ-14, OQ-US016, OQ-PACK remain unresolved; Proposed paths only.
