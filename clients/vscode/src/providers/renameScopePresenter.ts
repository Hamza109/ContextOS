/**
 * Rename-scope review presentation (T052).
 * Analysis only — never claims ContextOS rename sandbox / execute (FR-007; SC-005).
 */

import type { RenameScopeAnalysis } from "../mcp/types";

export const RENAME_SCOPE_REVIEW_DISCLAIMER =
  "Review only — ContextOS does not execute renames or provide a rename sandbox. " +
  "Apply rename with your editor/LSP after review.";

export function formatRenameScopeReport(analysis: RenameScopeAnalysis): string {
  const lines = [
    `ContextOS rename-scope analysis: \`${analysis.symbolName}\``,
    "",
    RENAME_SCOPE_REVIEW_DISCLAIMER,
    "",
    `Breaking-change count: ${analysis.breakingChangeCount}`,
    "Safe scope paths:",
    ...analysis.safeScopePaths.map((p) => `  - ${p}`),
  ];
  if (analysis.notes) {
    lines.push("", `Notes: ${analysis.notes}`);
  }
  return lines.join("\n");
}

/**
 * Detect affirmative execute/sandbox UX claims (not "does not execute" disclaimers).
 */
export function renameScopeClaimsExecution(text: string): boolean {
  return (
    /\b(will|can|now)\s+execute\s+rename\b/i.test(text) ||
    /\bapply\s+rename\s+now\b/i.test(text) ||
    /\bContextOS\s+rename\s+sandbox\b/i.test(text) ||
    /\brun\s+rename\s+in\s+(a\s+)?sandbox\b/i.test(text)
  );
}
