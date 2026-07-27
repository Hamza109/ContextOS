/**
 * Thin Serena MCP client for VS Code DX (T015).
 *
 * Owns transport/session wiring for definition / references / hover / rename-scope only.
 * Does NOT implement search, index, ignore, consent, or symbol-policy logic (FR-011; ADR-005).
 *
 * Live SDK package pins: NEEDS CLARIFICATION — without an injected session, surfaces a
 * clear unavailable error (OQ-MCP-Fallback; T070). No Confirmed regex-fallback Pass invent.
 */

import type {
  DefinitionResult,
  HoverDocs,
  ReferenceHit,
  RenameScopeAnalysis,
  SymbolPosition,
} from "./types";

/** Proposed: MCP/Serena session unavailable — clear IDE error path (T070). */
export class SerenaUnavailableError extends Error {
  constructor(message = SERENA_UNAVAILABLE_MESSAGE) {
    super(message);
    this.name = "SerenaUnavailableError";
  }
}

export const SERENA_UNAVAILABLE_MESSAGE =
  "ContextOS: Serena MCP unavailable. Symbol navigation requires a Serena session " +
  "(Proposed clear error; OQ-MCP-Fallback open — no Confirmed fallback).";

/**
 * Minimal session protocol — concrete SDK binding NEEDS CLARIFICATION.
 * Injectable for vitest; production may supply a live MCP session later.
 */
export interface SerenaSession {
  findDefinition(pos: SymbolPosition): Promise<DefinitionResult>;
  findReferences(pos: SymbolPosition): Promise<ReferenceHit[]>;
  hover(pos: SymbolPosition): Promise<HoverDocs>;
  renameScopeAnalysis(pos: SymbolPosition): Promise<RenameScopeAnalysis>;
  close(): void;
}

export interface SerenaClientOptions {
  /** Injected session (tests / host-provided MCP). */
  session?: SerenaSession;
}

export class SerenaMcpClient {
  private session: SerenaSession | undefined;
  private readonly owned: boolean;

  constructor(options: SerenaClientOptions = {}) {
    this.session = options.session;
    this.owned = options.session === undefined;
  }

  /**
   * Open or return session. Without injection, fail clearly (no invented live SDK).
   */
  async connect(): Promise<SerenaSession> {
    if (this.session) {
      return this.session;
    }
    throw new SerenaUnavailableError();
  }

  close(): void {
    if (this.session && this.owned) {
      this.session.close();
    }
    this.session = undefined;
  }

  async findDefinition(pos: SymbolPosition): Promise<DefinitionResult> {
    const s = await this.connect();
    return s.findDefinition(pos);
  }

  async findReferences(pos: SymbolPosition): Promise<ReferenceHit[]> {
    const s = await this.connect();
    return s.findReferences(pos);
  }

  async hover(pos: SymbolPosition): Promise<HoverDocs> {
    const s = await this.connect();
    return s.hover(pos);
  }

  async renameScopeAnalysis(pos: SymbolPosition): Promise<RenameScopeAnalysis> {
    const s = await this.connect();
    return s.renameScopeAnalysis(pos);
  }
}

/** Format unavailable / session errors for IDE notifications (T070). */
export function formatSerenaError(err: unknown): string {
  if (err instanceof SerenaUnavailableError) {
    return err.message;
  }
  if (err instanceof Error) {
    return `ContextOS: Serena MCP error — ${err.message}`;
  }
  return `ContextOS: Serena MCP error — ${String(err)}`;
}
