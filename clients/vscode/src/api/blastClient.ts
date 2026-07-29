/**
 * Orchestrator HTTP client — Blast DX only (EP-007 / US-020).
 * Calls Confirmed GET /blast/{file_name}?repo= — never computes blast locally.
 * Ignore / policy / traversal stay FastAPI-owned (Constitution V).
 */

import type { BlastResponse, BlastRisk } from "./types";

export class BlastClientError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly body?: string,
  ) {
    super(message);
    this.name = "BlastClientError";
  }
}

export interface GetBlastOptions {
  signal?: AbortSignal;
  fetchImpl?: typeof fetch;
  /** Proposed optional hop bound (api-contract EP-007 notes) — not Confirmed. */
  maxHops?: number;
}

/**
 * GET {baseUrl}/blast/{file_name}?repo= — Confirmed FR-08 fields.
 * file_name is path-encoded; never invents graph edges beyond the response.
 */
export async function getBlast(
  baseUrl: string,
  fileName: string,
  repo: string,
  options: GetBlastOptions = {},
): Promise<BlastResponse> {
  const root = baseUrl.replace(/\/+$/, "");
  const trimmedFile = fileName.trim();
  const trimmedRepo = repo.trim();
  if (!trimmedFile) {
    throw new BlastClientError("file_name is required");
  }
  if (!trimmedRepo) {
    throw new BlastClientError("repo is required");
  }

  const params = new URLSearchParams({ repo: trimmedRepo });
  if (typeof options.maxHops === "number" && options.maxHops >= 1) {
    params.set("max_hops", String(options.maxHops));
  }
  const url = `${root}/blast/${encodeURIComponent(trimmedFile)}?${params.toString()}`;
  const fetchImpl = options.fetchImpl ?? globalThis.fetch;

  if (typeof fetchImpl !== "function") {
    throw new BlastClientError("fetch is not available in this runtime");
  }

  let response: Response;
  try {
    response = await fetchImpl(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: options.signal,
    });
  } catch (err) {
    if (isAbortError(err)) {
      throw err;
    }
    throw new BlastClientError(
      `GET /blast network error: ${err instanceof Error ? err.message : String(err)}`,
    );
  }

  const text = await response.text();
  if (!response.ok) {
    throw new BlastClientError(
      `GET /blast failed: HTTP ${response.status}`,
      response.status,
      text,
    );
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(text) as unknown;
  } catch {
    throw new BlastClientError("GET /blast returned non-JSON body", response.status, text);
  }

  return assertBlastResponse(parsed);
}

const RISK_VALUES: ReadonlySet<string> = new Set(["HIGH", "MEDIUM", "LOW"]);

function assertBlastResponse(value: unknown): BlastResponse {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new BlastClientError("Invalid BlastResponse shape");
  }
  const v = value as Record<string, unknown>;
  for (const key of [
    "direct_dependents",
    "transitive",
    "db_tables",
    "tests_to_run",
  ] as const) {
    if (!Array.isArray(v[key]) || !v[key].every((x) => typeof x === "string")) {
      throw new BlastClientError(`Invalid BlastResponse: ${key} must be string[]`);
    }
  }
  if (typeof v.risk !== "string" || !RISK_VALUES.has(v.risk)) {
    throw new BlastClientError("Invalid BlastResponse: risk must be HIGH|MEDIUM|LOW");
  }

  const out: BlastResponse = {
    direct_dependents: v.direct_dependents as string[],
    transitive: v.transitive as string[],
    db_tables: v.db_tables as string[],
    risk: v.risk as BlastRisk,
    tests_to_run: v.tests_to_run as string[],
  };

  // Proposed fields — pass through when present; never invent Confirmed schemas.
  if (Array.isArray(v.owners)) {
    out.owners = v.owners;
  }
  if (v.index_revision === null || typeof v.index_revision === "string") {
    out.index_revision = v.index_revision;
  }
  if (typeof v.stale === "boolean") {
    out.stale = v.stale;
  }

  return out;
}

function isAbortError(err: unknown): boolean {
  return (
    (err instanceof Error && err.name === "AbortError") ||
    (typeof DOMException !== "undefined" &&
      err instanceof DOMException &&
      err.name === "AbortError")
  );
}
