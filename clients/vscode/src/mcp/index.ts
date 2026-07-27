/** Proposed MCP DX surface — Serena wiring only (ADR-005). */

export {
  SerenaMcpClient,
  SerenaUnavailableError,
  SERENA_UNAVAILABLE_MESSAGE,
  formatSerenaError,
  type SerenaSession,
  type SerenaClientOptions,
} from "./serenaClient";
export { InMemorySerenaSession, type InMemorySerenaSeed } from "./inMemorySession";
export type {
  DefinitionResult,
  HoverDocs,
  ReferenceHit,
  RenameScopeAnalysis,
  SymbolLocation,
  SymbolPosition,
} from "./types";
