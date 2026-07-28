/**
 * Orchestrator HTTP client — DX only. Calls confirmed POST /index.
 * Never packs, embeds, applies ignore policy, or invents endpoints.
 */

import type { IndexRequest, IndexResponse } from "./types";

export class IndexClientError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly body?: string,
  ) {
    super(message);
    this.name = "IndexClientError";
  }
}

export interface PostIndexOptions {
  /** Client-side cancel only (OQ-CANCEL server semantics open). */
  signal?: AbortSignal;
  fetchImpl?: typeof fetch;
}

/**
 * POST {baseUrl}/index with Confirmed {repo_path, repo_name}.
 * Optional Proposed paths/files (OQ-14) may be included by callers — labeled Proposed.
 */
export async function postIndex(
  baseUrl: string,
  body: IndexRequest,
  options: PostIndexOptions = {},
): Promise<IndexResponse> {
  const root = baseUrl.replace(/\/+$/, "");
  const url = `${root}/index`;
  const fetchImpl = options.fetchImpl ?? globalThis.fetch;

  if (typeof fetchImpl !== "function") {
    throw new IndexClientError("fetch is not available in this runtime");
  }

  // Confirmed fields only required; Proposed scope fields passed through if present.
  const payload: IndexRequest = {
    repo_path: body.repo_path,
    repo_name: body.repo_name,
  };
  // Proposed (OQ-14) — not Confirmed
  if (body.paths !== undefined) {
    payload.paths = body.paths;
  }
  if (body.files !== undefined) {
    payload.files = body.files;
  }

  let response: Response;
  try {
    response = await fetchImpl(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
      signal: options.signal,
    });
  } catch (err) {
    if (isAbortError(err)) {
      throw err;
    }
    throw new IndexClientError(
      `POST /index network error: ${err instanceof Error ? err.message : String(err)}`,
    );
  }

  const text = await response.text();
  if (!response.ok) {
    throw new IndexClientError(
      `POST /index failed: HTTP ${response.status}${formatApiDetail(text)}`,
      response.status,
      text,
    );
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(text) as unknown;
  } catch {
    throw new IndexClientError("POST /index returned non-JSON body", response.status, text);
  }

  return assertIndexResponse(parsed);
}

function assertIndexResponse(value: unknown): IndexResponse {
  if (!value || typeof value !== "object") {
    throw new IndexClientError("Invalid IndexResponse shape");
  }
  const v = value as Record<string, unknown>;
  for (const key of ["files_indexed", "graph_nodes", "embeddings", "time_ms"] as const) {
    if (typeof v[key] !== "number") {
      throw new IndexClientError(`Invalid IndexResponse: missing numeric ${key}`);
    }
  }
  return {
    files_indexed: v.files_indexed as number,
    graph_nodes: v.graph_nodes as number,
    embeddings: v.embeddings as number,
    time_ms: v.time_ms as number,
  };
}

function formatApiDetail(text: string): string {
  try {
    const parsed = JSON.parse(text) as { detail?: unknown };
    if (typeof parsed.detail === "string" && parsed.detail.trim()) {
      return ` — ${parsed.detail.trim()}`;
    }
  } catch {
    // ignore non-JSON error bodies
  }
  return text.trim() ? ` — ${text.trim().slice(0, 200)}` : "";
}

function isAbortError(err: unknown): boolean {
  return (
    (err instanceof Error && err.name === "AbortError") ||
    (typeof DOMException !== "undefined" &&
      err instanceof DOMException &&
      err.name === "AbortError")
  );
}
