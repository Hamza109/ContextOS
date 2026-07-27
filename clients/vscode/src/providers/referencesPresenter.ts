/**
 * References presentation + file-type filter UX (T044).
 * Filters display of MCP results only — not SymbolService policy.
 */

import type { ReferenceHit } from "../mcp/types";

export function fileExtension(path: string): string {
  const base = path.split(/[/\\]/).pop() ?? path;
  const i = base.lastIndexOf(".");
  if (i <= 0) return "";
  return base.slice(i).toLowerCase();
}

/** Collect unique extensions from MCP reference hits for filter QuickPick. */
export function collectReferenceExtensions(hits: ReferenceHit[]): string[] {
  const set = new Set<string>();
  for (const h of hits) {
    const ext = fileExtension(h.path);
    if (ext) set.add(ext);
  }
  return [...set].sort();
}

/**
 * Presentation filter by file extension (UX). Empty selected → all hits.
 */
export function filterReferencesByExtensions(
  hits: ReferenceHit[],
  selectedExtensions: string[] | undefined,
): ReferenceHit[] {
  if (!selectedExtensions || selectedExtensions.length === 0) {
    return hits;
  }
  const allow = new Set(selectedExtensions.map((e) => e.toLowerCase()));
  return hits.filter((h) => allow.has(fileExtension(h.path)));
}

export function formatReferenceHit(hit: ReferenceHit): string {
  const header = `${hit.path}:${hit.line}`;
  const before = hit.contextBefore.map((l) => `  | ${l}`).join("\n");
  const mid = `> | ${hit.lineText ?? ""}`;
  const after = hit.contextAfter.map((l) => `  | ${l}`).join("\n");
  return [header, before, mid, after].filter((s) => s.length > 0).join("\n");
}

export function formatReferencesReport(
  symbol: string | undefined,
  hits: ReferenceHit[],
): string {
  const title = `ContextOS references${symbol ? ` for \`${symbol}\`` : ""} (${hits.length})`;
  if (hits.length === 0) {
    return `${title}\n\n(no references)`;
  }
  return `${title}\n\n${hits.map(formatReferenceHit).join("\n\n")}`;
}
