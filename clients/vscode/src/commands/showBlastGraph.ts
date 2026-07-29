/**
 * ContextOS: Show Blast Graph — Proposed command (EP-007 / US-020).
 * Opens React Flow Webview over FastAPI GET /blast data.
 */

import * as vscode from "vscode";
import type { ExtensionConfig } from "../config";
import { resolvePrimaryWorkspace } from "../indexing/workspace";
import {
  SHOW_BLAST_GRAPH_COMMAND,
  openGraphBlastPanel,
  type GraphBlastPanelDeps,
} from "../providers/graphBlastPanel";
import type { FreshnessSession } from "../providers/stalenessPresenter";
import { snapshotActiveEditor } from "./editorContext";

export { SHOW_BLAST_GRAPH_COMMAND };

export interface ShowBlastGraphDeps {
  extensionUri: vscode.Uri;
  getConfig: () => ExtensionConfig;
  getEditor: () => vscode.TextEditor | undefined;
  workspaceFolders: () => readonly vscode.WorkspaceFolder[] | undefined;
  showWarningMessage: (m: string) => void;
  showErrorMessage: (m: string) => void;
  freshnessSession: FreshnessSession;
  statusBarItem?: vscode.StatusBarItem;
  fetchImpl?: typeof fetch;
}

export async function runShowBlastGraph(deps: ShowBlastGraphDeps): Promise<void> {
  const panelDeps: GraphBlastPanelDeps = {
    extensionUri: deps.extensionUri,
    getConfig: deps.getConfig,
    getEditor: deps.getEditor,
    workspaceFolders: deps.workspaceFolders,
    resolveRepo: () => resolvePrimaryWorkspace(deps.workspaceFolders()),
    relativePathFor: (editor) => {
      const snap = snapshotActiveEditor(editor, deps.workspaceFolders());
      return snap?.relativePath;
    },
    showWarningMessage: deps.showWarningMessage,
    showErrorMessage: deps.showErrorMessage,
    freshnessSession: deps.freshnessSession,
    statusBarItem: deps.statusBarItem,
    fetchImpl: deps.fetchImpl,
    openFile: async (relativePath) => {
      const ws = resolvePrimaryWorkspace(deps.workspaceFolders());
      if (!ws) return;
      const abs = `${ws.repo_path.replace(/\/+$/, "")}/${relativePath.replace(/^\/+/, "")}`;
      const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(abs));
      await vscode.window.showTextDocument(doc);
    },
  };
  await openGraphBlastPanel(panelDeps);
}
