/**
 * Rename-scope review command (T052) — analysis presentation only.
 * No execute / sandbox UX (FR-007; T050).
 */

import type * as vscode from "vscode";
import type { SerenaMcpClient } from "../mcp/serenaClient";
import { formatSerenaError } from "../mcp/serenaClient";
import type { RenameScopeAnalysis } from "../mcp/types";
import { formatRenameScopeReport } from "../providers/renameScopePresenter";
import { snapshotActiveEditor, toSymbolPosition } from "./editorContext";

export const RENAME_SCOPE_COMMAND = "contextos.renameScopeAnalysis";

export interface RenameScopeDeps {
  getClient: () => SerenaMcpClient;
  getEditor: () => vscode.TextEditor | undefined;
  workspaceFolders: () => readonly vscode.WorkspaceFolder[] | undefined;
  showInformationMessage: (m: string) => void;
  showWarningMessage: (m: string) => void;
  showErrorMessage: (m: string) => void;
  presentReport: (text: string) => void;
}

export async function runRenameScopeAnalysis(
  deps: RenameScopeDeps,
): Promise<RenameScopeAnalysis | undefined> {
  const snap = snapshotActiveEditor(deps.getEditor(), deps.workspaceFolders());
  if (!snap) {
    deps.showWarningMessage("ContextOS: open a file to analyze rename scope.");
    return undefined;
  }
  try {
    const analysis = await deps.getClient().renameScopeAnalysis(toSymbolPosition(snap));
    const report = formatRenameScopeReport(analysis);
    deps.presentReport(report);
    deps.showInformationMessage(
      `ContextOS: rename-scope for ${analysis.symbolName} — ` +
        `${analysis.breakingChangeCount} breaking change(s) (review only)`,
    );
    return analysis;
  } catch (err) {
    deps.showErrorMessage(formatSerenaError(err));
    return undefined;
  }
}
