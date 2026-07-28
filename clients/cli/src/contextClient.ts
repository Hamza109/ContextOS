/**
 * Thin HTTP client — Confirmed POST /context only (api-contract §2.3 / §6).
 * FastAPI owns search/pack/symbol; CLI never reimplements (FR-002, FR-010; SC-005).
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
  if (!Array.isArray(v.relevant_files)) {
    throw new ContextClientError("Invalid ContextResponse: relevant_files must be an array");
  }
  if (v.blast_radius != null && !isPlainObject(v.blast_radius)) {
    throw new ContextClientError("Invalid ContextResponse: blast_radius must be object or null");
  }
  if (v.memory != null && !isPlainObject(v.memory)) {
    throw new ContextClientError("Invalid ContextResponse: memory must be object or null");
  }
  return {
    final_context: v.final_context,
    metrics: assertMetrics(v.metrics),
    blast_radius: (v.blast_radius as Record<string, unknown> | null) ?? null,
    memory: (v.memory as Record<string, unknown> | null) ?? null,
    relevant_files: v.relevant_files,
    is_real: v.is_real,
  };
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function assertMetrics(value: unknown): ContextMetrics {
  if (!value || typeof value !== "object") {
    throw new ContextClientError("Invalid ContextResponse: metrics object required");
  }
  const m = value as Record<string, unknown>;
  for (const key of ["tokens_before", "tokens_after", "saving_percent"] as const) {
    if (typeof m[key] !== "number") {
      throw new ContextClientError(`Invalid ContextMetrics: missing numeric ${key}`);
    }
  }
  if (typeof m.trace !== "string" && !isPlainObject(m.trace)) {
    throw new ContextClientError("Invalid ContextMetrics: trace must be string or object");
  }
  let latencyMs = 0;
  if (isPlainObject(m.trace) && typeof m.trace.duration_ms === "number") {
    latencyMs = m.trace.duration_ms;
  }
  return {
    tokens_before: m.tokens_before as number,
    tokens_after: m.tokens_after as number,
    saving_percent: m.saving_percent as number,
    trace: m.trace as string | Record<string, unknown>,
    latency_ms: latencyMs,
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
