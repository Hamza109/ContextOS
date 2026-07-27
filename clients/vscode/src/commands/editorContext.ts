/**
 * Editor helpers for L3 DX — selection/word only.
 * No file-system walks of secrets; no local symbol index.
 */

import type * as vscode from "vscode";
import type { SymbolPosition } from "../mcp/types";
import { relativeWorkspacePath, resolvePrimaryWorkspace } from "../indexing/workspace";

export interface ActiveEditorSnapshot {
  path: string;
  relativePath: string | undefined;
  line: number;
  column: number;
  symbol: string | undefined;
  selectionText: string;
  repoName: string | undefined;
  repoPath: string | undefined;
}

export function snapshotActiveEditor(
  editor: vscode.TextEditor | undefined,
  workspaceFolders: readonly vscode.WorkspaceFolder[] | undefined,
): ActiveEditorSnapshot | undefined {
  if (!editor) {
    return undefined;
  }
  const doc = editor.document;
  const pos = editor.selection.active;
  const wordRange = doc.getWordRangeAtPosition(pos);
  const symbol = wordRange ? doc.getText(wordRange) : undefined;
  const selectionText = editor.selection.isEmpty
    ? symbol ?? ""
    : doc.getText(editor.selection);

  const ws = resolvePrimaryWorkspace(workspaceFolders);
  const relative = ws
    ? relativeWorkspacePath(ws.repo_path, doc.uri.fsPath)
    : undefined;

  return {
    path: doc.uri.fsPath,
    relativePath: relative,
    line: pos.line + 1,
    column: pos.character,
    symbol,
    selectionText: selectionText.trim(),
    repoName: ws?.repo_name,
    repoPath: ws?.repo_path,
  };
}

export function toSymbolPosition(snap: ActiveEditorSnapshot): SymbolPosition {
  return {
    path: snap.path,
    line: snap.line,
    column: snap.column,
    symbol: snap.symbol ?? null,
  };
}
