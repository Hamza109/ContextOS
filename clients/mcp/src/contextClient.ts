/**
 * Thin HTTP client — Confirmed POST /context + GET / only.
 * FastAPI owns search/pack; MCP never reimplements intelligence.
 */

import type {
  ContextRequest,
  ContextResponse,
  ContextMetrics,
  IndexRequest,
  IndexResponse,
} from "./types.js";

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

export async function getHealth(baseUrl: string): Promise<unknown> {
  const root = baseUrl.replace(/\/+$/, "");
  const response = await fetch(`${root}/`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  const text = await response.text();
  if (!response.ok) {
    throw new ContextClientError(`GET / failed: HTTP ${response.status}`, response.status, text);
  }
  try {
    return JSON.parse(text) as unknown;
  } catch {
    throw new ContextClientError("GET / returned non-JSON body", response.status, text);
  }
}

/** Thin wrapper over Confirmed POST /index. */
export async function postIndex(
  baseUrl: string,
  body: IndexRequest,
): Promise<IndexResponse> {
  const root = baseUrl.replace(/\/+$/, "");
  let response: Response;
  try {
    response = await fetch(`${root}/index`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
  } catch (err) {
    throw new ContextClientError(
      `POST /index network error: ${err instanceof Error ? err.message : String(err)}`,
    );
  }

  const text = await response.text();
  if (!response.ok) {
    throw new ContextClientError(
      `POST /index failed: HTTP ${response.status}${formatDetail(text)}`,
      response.status,
      text,
    );
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(text) as unknown;
  } catch {
    throw new ContextClientError("POST /index returned non-JSON body", response.status, text);
  }
  return assertIndexResponse(parsed);
}

export async function postContext(
  baseUrl: string,
  body: ContextRequest,
): Promise<ContextResponse> {
  const root = baseUrl.replace(/\/+$/, "");
  const payload: ContextRequest = {
    query: body.query,
    repo: body.repo,
    top_k: body.top_k,
  };
  if (body.file) {
    payload.file = body.file;
  }

  let response: Response;
  try {
    response = await fetch(`${root}/context`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    throw new ContextClientError(
      `POST /context network error: ${err instanceof Error ? err.message : String(err)}`,
    );
  }

  const text = await response.text();
  if (!response.ok) {
    throw new ContextClientError(
      `POST /context failed: HTTP ${response.status}${formatDetail(text)}`,
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

export function formatAskPack(
  response: ContextResponse,
  maxChars: number,
): string {
  const m = response.metrics;
  const header = [
    "ContextOS pack (via POST /context)",
    `is_real=${response.is_real}`,
    `tokens_before=${m.tokens_before} tokens_after=${m.tokens_after} saving_percent=${m.saving_percent} latency_ms=${m.latency_ms}`,
    "",
    "--- final_context ---",
  ].join("\n");

  let body = response.final_context ?? "";
  let truncated = false;
  if (maxChars > 0 && body.length > maxChars) {
    body = body.slice(0, maxChars) + "\n…[truncated by contextos_ask max_chars budget]…";
    truncated = true;
  }

  const files = formatRelevantFiles(response.relevant_files);
  const footer = `\n\n--- relevant_files ---\n${files}${truncated ? "\n(note: final_context truncated by max_chars)" : ""}`;
  return `${header}\n${body}${footer}`;
}

function formatRelevantFiles(relevantFiles: unknown[]): string {
  if (!relevantFiles.length) {
    return "(none)";
  }
  return relevantFiles
    .map((entry, i) => {
      if (typeof entry === "string") {
        return `${i + 1}. ${entry}`;
      }
      if (entry && typeof entry === "object") {
        const o = entry as Record<string, unknown>;
        const path =
          typeof o.path === "string"
            ? o.path
            : typeof o.file === "string"
              ? o.file
              : JSON.stringify(entry);
        return `${i + 1}. ${path}`;
      }
      return `${i + 1}. ${String(entry)}`;
    })
    .join("\n");
}

function formatDetail(text: string): string {
  try {
    const parsed = JSON.parse(text) as { detail?: unknown };
    if (typeof parsed.detail === "string" && parsed.detail.trim()) {
      return ` — ${parsed.detail.trim()}`;
    }
  } catch {
    // ignore
  }
  return text.trim() ? ` — ${text.trim().slice(0, 200)}` : "";
}

function assertIndexResponse(value: unknown): IndexResponse {
  if (!value || typeof value !== "object") {
    throw new ContextClientError("Invalid IndexResponse shape");
  }
  const v = value as Record<string, unknown>;
  for (const key of ["files_indexed", "graph_nodes", "embeddings", "time_ms"] as const) {
    if (typeof v[key] !== "number") {
      throw new ContextClientError(`Invalid IndexResponse: missing numeric ${key}`);
    }
  }
  return {
    files_indexed: v.files_indexed as number,
    graph_nodes: v.graph_nodes as number,
    embeddings: v.embeddings as number,
    time_ms: v.time_ms as number,
  };
}

function assertContextResponse(value: unknown): ContextResponse {
  if (!value || typeof value !== "object") {
    throw new ContextClientError("Invalid ContextResponse shape");
  }
  const v = value as Record<string, unknown>;
  if (typeof v.final_context !== "string") {
    throw new ContextClientError("Invalid ContextResponse: missing final_context");
  }
  if (typeof v.is_real !== "boolean") {
    throw new ContextClientError("Invalid ContextResponse: missing is_real");
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

function assertMetrics(value: unknown): ContextMetrics {
  if (!value || typeof value !== "object") {
    throw new ContextClientError("Invalid ContextMetrics");
  }
  const m = value as Record<string, unknown>;
  for (const key of ["tokens_before", "tokens_after", "saving_percent"] as const) {
    if (typeof m[key] !== "number") {
      throw new ContextClientError(`Invalid ContextMetrics: missing ${key}`);
    }
  }
  if (typeof m.trace !== "string" && !isPlainObject(m.trace)) {
    throw new ContextClientError("Invalid ContextMetrics: trace");
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

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}
