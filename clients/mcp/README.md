# ContextOS MCP (Proposed agent wiring)

Thin MCP server so Cursor/agents can call budgeted **`POST /context`** like Graphify’s budgeted query — FastAPI still owns search/pack/ignore.

## Tools

| Tool | Backend |
|------|---------|
| `contextos_health` | `GET /` |
| `contextos_index` | `POST /index` (`repo_path`, `repo_name`) |
| `contextos_ask` | `POST /context` + pack text including `blast_radius` (when present) and openable `/graph.html` + `/blast` links |

## Run locally

```bash
# Orchestrator must be up (host or Docker) and repo indexed
cd clients/mcp
npm install
npm start
```

Env:

- `CONTEXTOS_ORCHESTRATOR_BASE_URL` (default `http://127.0.0.1:8000`)

`contextos_index` requires the orchestrator to read `repo_path`. Host-run FastAPI
can read ordinary local paths; Docker requires a matching volume mount.

## Cursor project config

See repo root `.cursor/mcp.json` — enables this server for the ContextOS workspace.

## Agent rule

`.cursor/rules/contextos-first.mdc` (`alwaysApply`) — prefer `contextos_ask` before dumping large source trees.
