/**
 * Orchestrator HTTP client — Pack Context DX only (T016 / T064).
 * Calls Confirmed POST /context with EP-002 fields: query / file / repo / top_k.
 * Never packs, searches, indexes, or applies ignore/consent locally (FR-010, FR-011).
 */

import type { ContextRequest, ContextResponse, ContextMetrics } from "./types";

export class ContextClientError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly body?: string,
  ) {
    super(message);
    this.name = "ContextClientError";
  }
}

export interface PostContextOptions {
  signal?: AbortSignal;
  fetchImpl?: typeof fetch;
}

/**
 * POST {baseUrl}/context — Confirmed contract only.
 */
export async function postContext(
  baseUrl: string,
  body: ContextRequest,
  options: PostContextOptions = {},
): Promise<ContextResponse> {
  const root = baseUrl.replace(/\/+$/, "");
  const url = `${root}/context`;
  const fetchImpl = options.fetchImpl ?? globalThis.fetch;

  if (typeof fetchImpl !== "function") {
    throw new ContextClientError("fetch is not available in this runtime");
  }

  const payload: ContextRequest = {
    query: body.query,
    repo: body.repo,
    top_k: body.top_k,
  };
  if (body.file !== undefined && body.file !== null && body.file !== "") {
    payload.file = body.file;
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
    throw new ContextClientError(
      `POST /context network error: ${err instanceof Error ? err.message : String(err)}`,
    );
  }

  const text = await response.text();
  if (!response.ok) {
    throw new ContextClientError(
      `POST /context failed: HTTP ${response.status}`,
      response.status,
      text,
    );
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(text) as unknown;
  } catch {
    throw new ContextClientError("POST /context returned non-JSON body", response.status, text);
  }

  return assertContextResponse(parsed);
}

function assertContextResponse(value: unknown): ContextResponse {
  if (!value || typeof value !== "object") {
    throw new ContextClientError("Invalid ContextResponse shape");
  }
  const v = value as Record<string, unknown>;
  if (typeof v.final_context !== "string") {
    throw new ContextClientError("Invalid ContextResponse: missing final_context string");
  }
  if (typeof v.is_real !== "boolean") {
    throw new ContextClientError("Invalid ContextResponse: missing is_real boolean");
  }
  if (!Array.isArray(v.blast_radius) || !Array.isArray(v.memory) || !Array.isArray(v.relevant_files)) {
    throw new ContextClientError("Invalid ContextResponse: array fields required");
  }
  return {
    final_context: v.final_context,
    metrics: assertMetrics(v.metrics),
    blast_radius: v.blast_radius,
    memory: v.memory,
    relevant_files: v.relevant_files,
    is_real: v.is_real,
  };
}

function assertMetrics(value: unknown): ContextMetrics {
  if (!value || typeof value !== "object") {
    throw new ContextClientError("Invalid ContextResponse: metrics object required");
  }
  const m = value as Record<string, unknown>;
  for (const key of ["tokens_raw", "tokens_compacted", "reduction_pct", "latency_ms"] as const) {
    if (typeof m[key] !== "number") {
      throw new ContextClientError(`Invalid ContextMetrics: missing numeric ${key}`);
    }
  }
  return {
    tokens_raw: m.tokens_raw as number,
    tokens_compacted: m.tokens_compacted as number,
    reduction_pct: m.reduction_pct as number,
    latency_ms: m.latency_ms as number,
  };
}

function isAbortError(err: unknown): boolean {
  return (
    (err instanceof Error && err.name === "AbortError") ||
    (typeof DOMException !== "undefined" &&
      err instanceof DOMException &&
      err.name === "AbortError")
  );
}
