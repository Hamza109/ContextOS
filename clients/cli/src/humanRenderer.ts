/**
 * Human-readable renderer for ask results (FR-001; SC-001).
 * Layout is Proposed (OQ-CLI-Human-Format) — Confirmed intent is "useful".
 * Proposed: include L1 blast_radius + openable graph.html / blast links.
 */

import type { ContextResponse } from "./types";

export interface HumanAskReportOptions {
  baseUrl?: string;
  repo?: string;
  file?: string;
  query?: string;
  depth?: number;
}

const PATH_HINT_RE =
  /(?:[\w.-]+\/)*[\w.-]+\.(?:py|ts|tsx|js|jsx|go|java)\b/i;

function extractPathHint(query: string | undefined): string | null {
  const match = PATH_HINT_RE.exec(query || "");
  return match ? match[0] : null;
}

function buildGraphHtmlUrl(
  baseUrl: string,
  repo: string,
  file?: string | null,
  depth = 3,
): string {
  const root = baseUrl.replace(/\/+$/, "");
  const d = Math.max(1, Math.min(5, Math.floor(depth)));
  const params = new URLSearchParams({ repo, depth: String(d) });
  if (file && file.trim()) {
    params.set("file", file.trim().replace(/^\/+/, ""));
  }
  return `${root}/graph.html?${params.toString()}`;
}

function buildBlastApiUrl(baseUrl: string, file: string, repo: string): string {
  const root = baseUrl.replace(/\/+$/, "");
  const path = file.trim().replace(/^\/+/, "");
  return `${root}/blast/${path.split("/").map(encodeURIComponent).join("/")}?repo=${encodeURIComponent(repo)}`;
}

function hasBlastPayload(blast: Record<string, unknown> | null): boolean {
  if (!blast || typeof blast !== "object") return false;
  const direct = blast.direct_dependents;
  const transitive = blast.transitive;
  if (Array.isArray(direct) && direct.length > 0) return true;
  if (Array.isArray(transitive) && transitive.length > 0) return true;
  if (typeof blast.risk === "string" && blast.risk.length > 0) return true;
  return Object.keys(blast).length > 0;
}

export function formatHumanAskReport(
  response: ContextResponse,
  opts: HumanAskReportOptions = {},
): string {
  const m = response.metrics;
  const lines: string[] = [
    "ContextOS ask (via POST /context)",
    `is_real=${response.is_real}`,
    `tokens_before=${m.tokens_before} tokens_after=${m.tokens_after} ` +
      `saving_percent=${m.saving_percent} latency_ms=${m.latency_ms}`,
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

  if (hasBlastPayload(response.blast_radius)) {
    lines.push(
      "",
      "--- blast_radius (L1 reverse IMPORTS from FastAPI) ---",
      JSON.stringify(response.blast_radius, null, 2),
      "Note: this is who imports the file — not Nest/module wiring inside the file.",
    );
  }

  if (opts.baseUrl && opts.repo) {
    const seed =
      (opts.file && opts.file.trim()) || extractPathHint(opts.query) || null;
    lines.push(
      "",
      "--- open graphs ---",
      `L1 IMPORTS graph (browser): ${buildGraphHtmlUrl(opts.baseUrl, opts.repo, seed, opts.depth ?? 3)}`,
    );
    if (seed) {
      lines.push(
        `Blast API (JSON): ${buildBlastApiUrl(opts.baseUrl, seed, opts.repo)}`,
      );
    }
    lines.push(
      "VS Code: Command Palette → ContextOS: Show Blast Graph (uses GET /blast)",
    );
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
          : JSON.stringify(item);
    return `- ${path}`;
  }
  return `- ${String(item)}`;
}
