/**
 * Ask ContextOS presentation (T041).
 * Formats orchestrator final_context + relevant_files for Output Channel.
 * No local packing / search / symbol policy — DX only.
 */

import type { ContextResponse } from "../api/types";

/** Format relevant_files array for human-readable Ask report (Proposed layout). */
export function formatRelevantFiles(relevantFiles: unknown[]): string {
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
              : typeof o.name === "string"
                ? o.name
                : JSON.stringify(entry);
        return `${i + 1}. ${path}`;
      }
      return `${i + 1}. ${String(entry)}`;
    })
    .join("\n");
}

/**
 * Present Ask results from Confirmed ContextResponse fields only.
 * Does not pack, filter, or enrich beyond display formatting.
 */
export function formatAskContextReport(response: ContextResponse): string {
  const m = response.metrics;
  const header = [
    "ContextOS Ask (via POST /context)",
    `tokens_before=${m.tokens_before} tokens_after=${m.tokens_after} ` +
      `saving_percent=${m.saving_percent} latency_ms=${m.latency_ms}`,
    `is_real=${response.is_real}`,
    "",
  ].join("\n");

  const files = formatRelevantFiles(response.relevant_files);
  return (
    `${header}${response.final_context}\n\n` +
    `--- relevant_files ---\n${files}`
  );
}
