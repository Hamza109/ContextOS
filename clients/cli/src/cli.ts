/**
 * CLI argument parser — ask verb only for EP-004 (FR-005).
 * Machine --json is Proposed (OQ-10).
 */

import type { AskArgs } from "./ask";

export interface ParsedCli {
  help?: boolean;
  ask?: AskArgs;
  error?: string;
}

export function parseArgv(argv: string[]): ParsedCli {
  const args = argv.slice();
  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    return { help: true };
  }

  const verb = args[0];
  if (verb !== "ask") {
    return {
      error: `Unknown command '${verb}'. Only 'ask' is available in this MVP (FR-005).`,
    };
  }

  const rest = args.slice(1);
  let query: string | undefined;
  let repo: string | undefined;
  let file: string | undefined;
  let topK: number | undefined;
  let baseUrl: string | undefined;
  let json = false;

  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === "--help" || a === "-h") {
      return { help: true };
    }
    if (a === "--json") {
      // Proposed (OQ-10) — schema not Confirmed
      json = true;
      continue;
    }
    if (a === "--repo") {
      repo = rest[++i];
      continue;
    }
    if (a === "--file") {
      file = rest[++i];
      continue;
    }
    if (a === "--top-k") {
      const raw = rest[++i];
      const n = Number(raw);
      if (!Number.isFinite(n) || n <= 0) {
        return { error: `Invalid --top-k value: ${raw}` };
      }
      topK = Math.floor(n);
      continue;
    }
    if (a === "--base-url") {
      baseUrl = rest[++i];
      continue;
    }
    if (a.startsWith("-")) {
      return { error: `Unknown option '${a}'.` };
    }
    if (query === undefined) {
      query = a;
    } else {
      return { error: `Unexpected argument '${a}'.` };
    }
  }

  if (!query) {
    return { error: "Missing query. Usage: contextos ask '<query>' --repo <name>" };
  }
  if (!repo) {
    return { error: "Missing --repo. Usage: contextos ask '<query>' --repo <name>" };
  }

  return {
    ask: {
      query,
      repo,
      file,
      topK,
      baseUrl,
      json,
    },
  };
}

export function helpText(): string {
  return [
    "contextos — ContextOS CLI (thin client of POST /context)",
    "",
    "Usage:",
    "  contextos ask '<query>' --repo <repo_name> [options]",
    "",
    "Options:",
    "  --repo <name>       Repository name (Confirmed ContextRequest.repo)",
    "  --file <path>       Optional file bias (Confirmed ContextRequest.file)",
    "  --top-k <n>         Optional top_k (default 8)",
    "  --base-url <url>    Orchestrator base URL (default http://localhost:8000",
    "                      or CONTEXTOS_ORCHESTRATOR_BASE_URL env)",
    "  --json              Proposed machine-readable output (OQ-10 — schema not Confirmed)",
    "  -h, --help          Show help",
    "",
    "Only the 'ask' verb is shipped in EP-004 MVP (FR-005).",
    "Install/run (Proposed packaging): npm install && npx contextos ask '…' --repo <name>",
    "  or: npm run contextos -- ask '…' --repo <name>",
  ].join("\n");
}
