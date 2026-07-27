/**
 * Pack Context presentation (T066).
 * Shows orchestrator final_context (may include Proposed safe-edit block).
 * Output channel only — no local pack; optional Webview deferred (constitution III).
 */

import type { ContextResponse } from "../api/types";

/** Proposed delimiter mirrored from orchestrator final_context enrichment — presentation detect only. */
export const SAFE_EDIT_BLOCK_MARKER = "--- ContextOS safe edit plan (Proposed) ---";

export function extractSafeEditSection(finalContext: string): string | undefined {
  const idx = finalContext.indexOf(SAFE_EDIT_BLOCK_MARKER);
  if (idx < 0) return undefined;
  return finalContext.slice(idx).trim();
}

export function formatPackContextReport(response: ContextResponse): string {
  const m = response.metrics;
  const header = [
    "ContextOS Pack Context (via POST /context)",
    `tokens_raw=${m.tokens_raw} tokens_compacted=${m.tokens_compacted} ` +
      `reduction_pct=${m.reduction_pct} latency_ms=${m.latency_ms}`,
    `is_real=${response.is_real}`,
    "",
  ].join("\n");

  const safe = extractSafeEditSection(response.final_context);
  const body = safe
    ? `${response.final_context}\n\n[safe-edit section detected in final_context — Proposed shape]`
    : response.final_context;

  return `${header}${body}`;
}
