/**
 * Find-all-references command + file-type filter UX (T044).
 * MCP results only — presentation filter is not SymbolService policy.
 */

import type * as vscode from "vscode";
import type { SerenaMcpClient } from "../mcp/serenaClient";
import { formatSerenaError } from "../mcp/serenaClient";
import type { ReferenceHit } from "../mcp/types";
import {
  collectReferenceExtensions,
  filterReferencesByExtensions,
  formatReferencesReport,
} from "../providers/referencesPresenter";
import { snapshotActiveEditor, toSymbolPosition } from "./editorContext";

export const FIND_REFERENCES_COMMAND = "contextos.findReferences";

export interface FindReferencesDeps {
  getClient: () => SerenaMcpClient;
  getEditor: () => vscode.TextEditor | undefined;
  workspaceFolders: () => readonly vscode.WorkspaceFolder[] | undefined;
  showInformationMessage: (m: string) => void;
  showWarningMessage: (m: string) => void;
  showErrorMessage: (m: string) => void;
  /** QuickPick: return selected extensions, empty = all, undefined = cancelled. */
  pickFileTypeFilters: (extensions: string[]) => Promise<string[] | undefined>;
  presentReport: (text: string) => void;
}

export async function runFindReferences(
  deps: FindReferencesDeps,
): Promise<ReferenceHit[] | undefined> {
  const snap = snapshotActiveEditor(deps.getEditor(), deps.workspaceFolders());
  if (!snap) {
    deps.showWarningMessage("ContextOS: open a file to find references.");
    return undefined;
  }
  try {
    const hits = await deps.getClient().findReferences(toSymbolPosition(snap));
    const exts = collectReferenceExtensions(hits);
    let selected: string[] | undefined = [];
    if (exts.length > 1) {
      selected = await deps.pickFileTypeFilters(exts);
      if (selected === undefined) {
        deps.showWarningMessage("ContextOS: find references cancelled.");
        return undefined;
      }
    }
    const filtered = filterReferencesByExtensions(hits, selected);
    const report = formatReferencesReport(snap.symbol, filtered);
    deps.presentReport(report);
    deps.showInformationMessage(
      `ContextOS: ${filtered.length} reference(s)${snap.symbol ? ` for ${snap.symbol}` : ""}`,
    );
    return filtered;
  } catch (err) {
    deps.showErrorMessage(formatSerenaError(err));
    return undefined;
  }
}
