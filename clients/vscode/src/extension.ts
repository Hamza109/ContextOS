/**
 * ContextOS VS Code extension entry (EP-001 indexing + EP-003 L3 DX).
 *
 * Owns DX only: activation auto-index, progress, client cancel, save re-index,
 * Serena MCP hover/commands, Pack Context + Ask ContextOS → POST /context.
 * FastAPI owns pack / ignore / consent / embed / Qdrant / symbol policy —
 * never reimplemented here.
 */

import * as vscode from "vscode";
import { postIndex, IndexClientError } from "./api/indexClient";
import { readExtensionConfig } from "./config";
import { triggerAutoIndex } from "./indexing/autoIndex";
import { registerOnSaveReindex } from "./indexing/onSaveReindex";
import { runWithIndexProgress, type IndexProgressHost } from "./indexing/progress";
import { resolvePrimaryWorkspace } from "./indexing/workspace";
import { SerenaMcpClient } from "./mcp/serenaClient";
import { createSerenaHoverProvider } from "./providers/hoverProvider";
import {
  ASK_CONTEXT_COMMAND,
  DEFINITION_LOOKUP_COMMAND,
  FIND_REFERENCES_COMMAND,
  PACK_CONTEXT_COMMAND,
  RENAME_SCOPE_COMMAND,
  runAskContext,
  runDefinitionLookup,
  runFindReferences,
  runPackContext,
  runRenameScopeAnalysis,
} from "./commands";

let indexingInFlight = false;
let outputChannel: vscode.OutputChannel | undefined;
let serenaClient: SerenaMcpClient | undefined;

export function activate(context: vscode.ExtensionContext): void {
  const progressHost = createProgressHost();
  outputChannel = vscode.window.createOutputChannel("ContextOS");
  context.subscriptions.push(outputChannel);

  // Proposed: injectable MCP session not supplied at activate — unavailable until host wires live Serena.
  // Tests inject via createSerenaClientForTests. Clear IDE error on command use (T070).
  serenaClient = new SerenaMcpClient();
  context.subscriptions.push({
    dispose: () => {
      serenaClient?.close();
      serenaClient = undefined;
    },
  });

  const getConfig = () => readExtensionConfig(vscode.workspace.getConfiguration.bind(vscode.workspace));
  const getClient = () => serenaClient ?? new SerenaMcpClient();

  const showInfo = (m: string) => {
    void vscode.window.showInformationMessage(m);
  };
  const showWarn = (m: string) => {
    void vscode.window.showWarningMessage(m);
  };
  const showError = (m: string) => {
    void vscode.window.showErrorMessage(m);
  };
  const presentReport = (text: string) => {
    outputChannel?.appendLine(text);
    outputChannel?.appendLine("");
    outputChannel?.show(true);
  };

  context.subscriptions.push(
    vscode.commands.registerCommand("contextos.indexRepository", async () => {
      const config = getConfig();
      const repo = resolvePrimaryWorkspace(vscode.workspace.workspaceFolders);
      if (!repo) {
        showWarn("ContextOS: open a workspace folder to index.");
        return;
      }
      if (indexingInFlight) {
        showWarn("ContextOS: index already in progress.");
        return;
      }
      indexingInFlight = true;
      try {
        const response = await runWithIndexProgress(
          progressHost,
          "ContextOS: Indexing repository…",
          async (signal, progress) => {
            progress.report({ message: repo.repo_name });
            return postIndex(
              config.orchestratorBaseUrl,
              { repo_path: repo.repo_path, repo_name: repo.repo_name },
              { signal },
            );
          },
        );
        showInfo(
          `ContextOS: indexed ${response.files_indexed} files (${response.embeddings} embeddings)`,
        );
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          showWarn("ContextOS: indexing cancelled.");
        } else {
          const msg =
            err instanceof IndexClientError
              ? err.message
              : err instanceof Error
                ? err.message
                : String(err);
          showError(`ContextOS: index failed — ${msg}`);
        }
      } finally {
        indexingInFlight = false;
      }
    }),
  );

  // --- EP-003 L3 commands (Proposed IDs) ---
  context.subscriptions.push(
    vscode.commands.registerCommand(DEFINITION_LOOKUP_COMMAND, async () => {
      await runDefinitionLookup({
        getClient,
        getEditor: () => vscode.window.activeTextEditor,
        workspaceFolders: () => vscode.workspace.workspaceFolders,
        showInformationMessage: showInfo,
        showWarningMessage: showWarn,
        showErrorMessage: showError,
        openAt: async (path, line) => {
          const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(path));
          const editor = await vscode.window.showTextDocument(doc);
          const pos = new vscode.Position(Math.max(0, line - 1), 0);
          editor.selection = new vscode.Selection(pos, pos);
          editor.revealRange(new vscode.Range(pos, pos));
        },
      });
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(FIND_REFERENCES_COMMAND, async () => {
      await runFindReferences({
        getClient,
        getEditor: () => vscode.window.activeTextEditor,
        workspaceFolders: () => vscode.workspace.workspaceFolders,
        showInformationMessage: showInfo,
        showWarningMessage: showWarn,
        showErrorMessage: showError,
        presentReport,
        pickFileTypeFilters: async (extensions) => {
          const items = [
            { label: "All file types", description: "Show every MCP reference", picked: true },
            ...extensions.map((ext) => ({
              label: ext,
              description: `Filter to ${ext}`,
              picked: false,
            })),
          ];
          const picked = await vscode.window.showQuickPick(items, {
            canPickMany: true,
            title: "ContextOS: filter references by file type",
            placeHolder: "Select extensions (All = no filter)",
          });
          if (!picked) return undefined;
          if (picked.some((p) => p.label === "All file types") || picked.length === 0) {
            return [];
          }
          return picked.map((p) => p.label);
        },
      });
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(RENAME_SCOPE_COMMAND, async () => {
      await runRenameScopeAnalysis({
        getClient,
        getEditor: () => vscode.window.activeTextEditor,
        workspaceFolders: () => vscode.workspace.workspaceFolders,
        showInformationMessage: showInfo,
        showWarningMessage: showWarn,
        showErrorMessage: showError,
        presentReport,
      });
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(PACK_CONTEXT_COMMAND, async () => {
      await runPackContext({
        getConfig,
        getEditor: () => vscode.window.activeTextEditor,
        workspaceFolders: () => vscode.workspace.workspaceFolders,
        showInformationMessage: showInfo,
        showWarningMessage: showWarn,
        showErrorMessage: showError,
        presentReport,
      });
    }),
  );

  // --- EP-004 US-008 Ask ContextOS (Proposed ID contextos.askContext) ---
  context.subscriptions.push(
    vscode.commands.registerCommand(ASK_CONTEXT_COMMAND, async () => {
      await runAskContext({
        getConfig,
        getEditor: () => vscode.window.activeTextEditor,
        workspaceFolders: () => vscode.workspace.workspaceFolders,
        showInputBox: (options) => vscode.window.showInputBox(options),
        showInformationMessage: showInfo,
        showWarningMessage: showWarn,
        showErrorMessage: showError,
        presentReport,
        logLatency: (wallMs, serverLatencyMs) => {
          // Proposed obs names (T046) — SC-004 Pass blocked (OQ-IDE-2s-Harness / T039)
          const line = `[ContextOS][obs][ask] wall_ms=${wallMs} server_latency_ms=${serverLatencyMs}`;
          console.log(line);
          outputChannel?.appendLine(line);
        },
      });
    }),
  );

  context.subscriptions.push(
    vscode.languages.registerHoverProvider(
      { scheme: "file" },
      createSerenaHoverProvider(getClient),
    ),
  );

  context.subscriptions.push(
    registerOnSaveReindex(
      {
        onDidSaveTextDocument: (listener) =>
          vscode.workspace.onDidSaveTextDocument((doc) => {
            listener({
              uri: { fsPath: doc.uri.fsPath, scheme: doc.uri.scheme },
            });
          }),
      },
      () => ({
        config: getConfig(),
        workspaceFolders: vscode.workspace.workspaceFolders,
        progressHost,
        showWarningMessage: showWarn,
        showErrorMessage: showError,
        isIndexing: () => indexingInFlight,
        setIndexing: (v) => {
          indexingInFlight = v;
        },
      }),
    ),
  );

  // FR-013: auto-index on activation (US-011)
  void triggerAutoIndex({
    config: getConfig(),
    workspaceFolders: vscode.workspace.workspaceFolders,
    progressHost,
    showInformationMessage: showInfo,
    showWarningMessage: showWarn,
    showErrorMessage: showError,
    logTiming: (ms, result) => {
      console.log(
        `[ContextOS][obs] auto-index wall_ms=${ms} server_time_ms=${result.time_ms} files=${result.files_indexed}`,
      );
    },
  }).finally(() => {
    // auto-index sets its own progress; clear guard if we want overlap protection
  });
}

export function deactivate(): void {
  serenaClient?.close();
  serenaClient = undefined;
}

/** Test hook: replace MCP client (Proposed — not a product API). */
export function setSerenaClientForTests(client: SerenaMcpClient | undefined): void {
  serenaClient = client;
}

function createProgressHost(): IndexProgressHost {
  return {
    locationNotification: vscode.ProgressLocation.Notification,
    withProgress: (options, task) =>
      vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: options.title,
          cancellable: options.cancellable,
        },
        (progress, token) =>
          task(
            {
              report: (v) => progress.report(v),
            },
            {
              isCancellationRequested: token.isCancellationRequested,
              onCancellationRequested: (listener) => token.onCancellationRequested(listener),
            },
          ),
      ),
  };
}
