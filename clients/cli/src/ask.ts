/**
 * contextos ask — maps CLI args → Confirmed ContextRequest → POST /context (US-007).
 * Only verb required for EP-004 (FR-005).
 */

import { postContext, ContextClientError } from "./contextClient";
import { formatHumanAskReport } from "./humanRenderer";
import { formatMachineAskReport } from "./machineRenderer";
import type { ContextRequest, ContextResponse } from "./types";

export const DEFAULT_TOP_K = 8;
export const DEFAULT_BASE_URL = "http://localhost:8000";

export interface AskArgs {
  query: string;
  repo: string;
  file?: string;
  topK?: number;
  baseUrl?: string;
  /** Proposed (OQ-10): machine-readable mode — schema not Confirmed. */
  json?: boolean;
}

export interface AskDeps {
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  env?: NodeJS.ProcessEnv;
  stdoutWrite?: (s: string) => void;
  stderrWrite?: (s: string) => void;
}

export function buildAskRequest(args: AskArgs): ContextRequest {
  const query = args.query.trim();
  if (!query) {
    throw new Error("contextos ask: query is required");
  }
  const repo = args.repo.trim();
  if (!repo) {
    throw new Error("contextos ask: --repo is required");
  }
  const req: ContextRequest = {
    query,
    repo,
    top_k: args.topK ?? DEFAULT_TOP_K,
  };
  if (args.file !== undefined && args.file !== "") {
    req.file = args.file;
  }
  return req;
}

export function resolveBaseUrl(args: AskArgs, env: NodeJS.ProcessEnv = process.env): string {
  return (
    args.baseUrl?.trim() ||
    env.CONTEXTOS_ORCHESTRATOR_BASE_URL?.trim() ||
    DEFAULT_BASE_URL
  );
}

export async function runAsk(
  args: AskArgs,
  deps: AskDeps = {},
): Promise<ContextResponse> {
  const body = buildAskRequest(args);
  const baseUrl = resolveBaseUrl(args, deps.env ?? process.env);
  const stdout = deps.stdoutWrite ?? ((s) => process.stdout.write(s));
  const stderr = deps.stderrWrite ?? ((s) => process.stderr.write(s));

  try {
    const response = await postContext(baseUrl, body, {
      fetchImpl: deps.fetchImpl,
      signal: deps.signal,
    });
    const text = args.json
      ? formatMachineAskReport(response)
      : formatHumanAskReport(response, {
          baseUrl,
          repo: body.repo,
          file: body.file,
          query: body.query,
        });
    stdout(text.endsWith("\n") ? text : `${text}\n`);
    return response;
  } catch (err) {
    const msg = formatAskError(err);
    stderr(`${msg}\n`);
    throw err;
  }
}

export function formatAskError(err: unknown): string {
  if (err instanceof ContextClientError) {
    return `ContextOS ask failed — ${err.message}`;
  }
  if (err instanceof Error) {
    return `ContextOS ask failed — ${err.message}`;
  }
  return `ContextOS ask failed — ${String(err)}`;
}
