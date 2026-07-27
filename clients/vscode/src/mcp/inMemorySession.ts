/**
 * In-memory Serena session double for DX tests / local wiring.
 * Not a production LSP and not a symbol-policy engine.
 */

import type {
  DefinitionResult,
  HoverDocs,
  ReferenceHit,
  RenameScopeAnalysis,
  SymbolPosition,
} from "./types";
import type { SerenaSession } from "./serenaClient";
import { SerenaUnavailableError } from "./serenaClient";

export interface InMemorySerenaSeed {
  definitions?: Record<string, DefinitionResult>;
  references?: Record<string, ReferenceHit[]>;
  hovers?: Record<string, HoverDocs>;
  renameScopes?: Record<string, RenameScopeAnalysis>;
  available?: boolean;
}

function key(pos: SymbolPosition): string {
  return `${pos.path}:${pos.line}:${pos.symbol ?? ""}`;
}

export class InMemorySerenaSession implements SerenaSession {
  private readonly definitions: Record<string, DefinitionResult>;
  private readonly references: Record<string, ReferenceHit[]>;
  private readonly hovers: Record<string, HoverDocs>;
  private readonly renameScopes: Record<string, RenameScopeAnalysis>;
  private readonly available: boolean;

  constructor(seed: InMemorySerenaSeed = {}) {
    this.definitions = seed.definitions ?? {};
    this.references = seed.references ?? {};
    this.hovers = seed.hovers ?? {};
    this.renameScopes = seed.renameScopes ?? {};
    this.available = seed.available !== false;
  }

  private ensure(): void {
    if (!this.available) {
      throw new SerenaUnavailableError();
    }
  }

  async findDefinition(pos: SymbolPosition): Promise<DefinitionResult> {
    this.ensure();
    const k = key(pos);
    if (this.definitions[k]) return this.definitions[k];
    if (pos.symbol && this.definitions[pos.symbol]) return this.definitions[pos.symbol];
    return {
      path: pos.path,
      line: pos.line,
      column: pos.column,
      unresolved: true,
      partial: true,
      message: "no definition found (Proposed unresolved; OQ-Unresolved-Symbol)",
    };
  }

  async findReferences(pos: SymbolPosition): Promise<ReferenceHit[]> {
    this.ensure();
    const k = key(pos);
    if (this.references[k]) return [...this.references[k]];
    if (pos.symbol && this.references[pos.symbol]) return [...this.references[pos.symbol]];
    return [];
  }

  async hover(pos: SymbolPosition): Promise<HoverDocs> {
    this.ensure();
    const k = key(pos);
    if (this.hovers[k]) return this.hovers[k];
    if (pos.symbol && this.hovers[pos.symbol]) return this.hovers[pos.symbol];
    return { contents: "", path: pos.path, line: pos.line };
  }

  async renameScopeAnalysis(pos: SymbolPosition): Promise<RenameScopeAnalysis> {
    this.ensure();
    const k = key(pos);
    if (this.renameScopes[k]) return this.renameScopes[k];
    if (pos.symbol && this.renameScopes[pos.symbol]) return this.renameScopes[pos.symbol];
    const name = pos.symbol || pos.path.split(/[/\\]/).pop() || "symbol";
    return {
      symbolName: name,
      safeScopePaths: [pos.path],
      breakingChangeCount: 0,
      notes: "Proposed default analysis — review only; no ContextOS rename execution",
    };
  }

  close(): void {
    // no-op
  }
}
