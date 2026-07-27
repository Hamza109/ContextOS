# ContextOS CLI (Proposed packaging — OQ-CLI-Packaging)

Thin client for Confirmed `POST /context` (api-contract §2.3 / §6). FastAPI owns orchestration.

## Run (local)

```bash
cd clients/cli
npm install
npm run contextos -- ask 'where is X?' --repo <repo_name>
```

Or after `npm run build`: `node dist/bin.js ask '…' --repo <name>`.

Base URL: `--base-url` or `CONTEXTOS_ORCHESTRATOR_BASE_URL` (default `http://localhost:8000`).

## Options

- `--file`, `--top-k` — Confirmed optional request fields
- `--json` — **Proposed** machine-readable output (OQ-10; schema not Confirmed)

Only the `ask` verb is shipped for EP-004 (FR-005).
