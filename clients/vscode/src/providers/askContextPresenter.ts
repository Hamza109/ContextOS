/**
 * Ask ContextOS presentation (T041).
 * Formats orchestrator final_context + relevant_files for Output Channel.
 * No local packing / search / symbol policy — DX only.
 * Proposed: surface FastAPI graph.html / blast URLs for discoverability.
 */

import type { ContextResponse } from "../api/types";
import {
  formatGraphDiscoverySection,
  hasBlastPayload,
} from "./graphLinks";
import {
  evaluateStaleness,
  extractFreshnessSignal,
  formatStalenessBanner,
} from "./stalenessPresenter";

export interface AskReportOptions {
  /** Proposed US-027: surface staleness on search/Ask DX when flag set */
  showStalenessWarnings?: boolean;
  baselineRevision?: string | null;
  /** Orchestrator base URL for openable /graph.html and /blast links. */
  orchestratorBaseUrl?: string;
  repo?: string;
  file?: string | null;
  query?: string;
}

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
 * Proposed: append staleness banner when blast_radius freshness indicates drift;
 * append blast_radius JSON + graph.html / blast API links when available.
 */
export function formatAskContextReport(
  response: ContextResponse,
  opts: AskReportOptions = {},
): string {
  const m = response.metrics;
  const staleState = evaluateStaleness(
    extractFreshnessSignal(response.blast_radius, opts.baselineRevision),
    { showStalenessWarnings: opts.showStalenessWarnings ?? true },
  );
  const banner = formatStalenessBanner(staleState);
  const headerLines = [
    "ContextOS Ask (via POST /context)",
    `tokens_before=${m.tokens_before} tokens_after=${m.tokens_after} ` +
      `saving_percent=${m.saving_percent} latency_ms=${m.latency_ms}`,
    `is_real=${response.is_real}`,
  ];
  if (banner) {
    headerLines.push(banner);
  }
  headerLines.push("");

  const files = formatRelevantFiles(response.relevant_files);
  const parts = [
    `${headerLines.join("\n")}${response.final_context}\n\n` +
      `--- relevant_files ---\n${files}`,
  ];

  if (hasBlastPayload(response.blast_radius)) {
    parts.push(
      "",
      "--- blast_radius (L1 reverse IMPORTS from FastAPI) ---",
      JSON.stringify(response.blast_radius, null, 2),
      "Note: this is who imports the file — not Nest/module wiring inside the file.",
    );
  }

  if (opts.orchestratorBaseUrl && opts.repo) {
    parts.push(
      "",
      formatGraphDiscoverySection({
        baseUrl: opts.orchestratorBaseUrl,
        repo: opts.repo,
        file: opts.file,
        query: opts.query,
      }),
    );
  }

  return parts.join("\n");
}
