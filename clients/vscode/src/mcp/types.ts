/**
 * Proposed Serena MCP payload shapes for IDE DX (ADR-005).
 * Mirrors orchestrator adapter intent — not Confirmed REST schemas (OQ-Symbol-REST open).
 */

export interface SymbolLocation {
  path: string;
  line: number;
  column?: number | null;
}

export interface DefinitionResult {
  path: string;
  line: number;
  column?: number | null;
  signature?: string | null;
  docstring?: string | null;
  language?: string | null;
  unresolved?: boolean;
  partial?: boolean;
  message?: string | null;
}

export interface ReferenceHit {
  path: string;
  line: number;
  column?: number | null;
  /** Call-site lines (±2) as returned by Serena — presentation only. */
  contextBefore: string[];
  contextAfter: string[];
  lineText?: string | null;
}

export interface HoverDocs {
  contents: string;
  path?: string | null;
  line?: number | null;
}

/** Rename-scope analysis only — no execute/apply (BRD §6; FR-007). */
export interface RenameScopeAnalysis {
  symbolName: string;
  safeScopePaths: string[];
  breakingChangeCount: number;
  notes?: string | null;
}

export interface SymbolPosition {
  path: string;
  line: number;
  column: number;
  symbol?: string | null;
}
