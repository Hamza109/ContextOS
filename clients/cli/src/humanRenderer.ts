/**
 * Human-readable renderer for ask results (FR-001; SC-001).
 * Layout is Proposed (OQ-CLI-Human-Format) — Confirmed intent is "useful".
 */

import type { ContextResponse } from "./types";

export function formatHumanAskReport(response: ContextResponse): string {
  const m = response.metrics;
  const lines: string[] = [
    "ContextOS ask (via POST /context)",
    `is_real=${response.is_real}`,
    `tokens_raw=${m.tokens_raw} tokens_compacted=${m.tokens_compacted} ` +
      `reduction_pct=${m.reduction_pct} latency_ms=${m.latency_ms}`,
    "",
    "--- final_context ---",
    response.final_context.trim() ? response.final_context : "(empty)",
    "",
    "--- relevant_files ---",
  ];

  if (response.relevant_files.length === 0) {
    lines.push("(none)");
  } else {
    for (const item of response.relevant_files) {
      lines.push(formatRelevantFile(item));
    }
  }

  return lines.join("\n");
}

function formatRelevantFile(item: unknown): string {
  if (typeof item === "string") {
    return `- ${item}`;
  }
  if (item && typeof item === "object") {
    const o = item as Record<string, unknown>;
    const path =
      typeof o.path === "string"
        ? o.path
        : typeof o.file === "string"
          ? o.file
          : typeof o.name === "string"
            ? o.name
            : JSON.stringify(item);
    return `- ${path}`;
  }
  return `- ${String(item)}`;
}
