/**
 * Definition lookup command (T033) — MCP DX only.
 */

import type * as vscode from "vscode";
import type { SerenaMcpClient } from "../mcp/serenaClient";
import { formatSerenaError } from "../mcp/serenaClient";
import type { DefinitionResult } from "../mcp/types";
import { snapshotActiveEditor, toSymbolPosition } from "./editorContext";

export const DEFINITION_LOOKUP_COMMAND = "contextos.definitionLookup";

export function formatDefinitionResult(def: DefinitionResult): string {
  if (def.unresolved) {
    return `ContextOS: definition unresolved — ${def.message ?? "no definition"}`;
  }
  const parts = [`ContextOS definition: ${def.path}:${def.line}`];
  if (def.signature) parts.push(`signature: ${def.signature}`);
  if (def.docstring) parts.push(def.docstring);
  return parts.join("\n");
}

export interface DefinitionLookupDeps {
  getClient: () => SerenaMcpClient;
  getEditor: () => vscode.TextEditor | undefined;
  workspaceFolders: () => readonly vscode.WorkspaceFolder[] | undefined;
  showInformationMessage: (m: string) => void;
  showWarningMessage: (m: string) => void;
  showErrorMessage: (m: string) => void;
  openAt?: (path: string, line: number) => Promise<void>;
}

export async function runDefinitionLookup(deps: DefinitionLookupDeps): Promise<DefinitionResult | undefined> {
  const snap = snapshotActiveEditor(deps.getEditor(), deps.workspaceFolders());
  if (!snap) {
    deps.showWarningMessage("ContextOS: open a file to look up a definition.");
    return undefined;
  }
  try {
    const def = await deps.getClient().findDefinition(toSymbolPosition(snap));
    deps.showInformationMessage(formatDefinitionResult(def));
    if (!def.unresolved && deps.openAt) {
      await deps.openAt(def.path, def.line);
    }
    return def;
  } catch (err) {
    deps.showErrorMessage(formatSerenaError(err));
    return undefined;
  }
}
