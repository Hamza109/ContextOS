/**
 * ContextOS VS Code extension entry (EP-001 US-011 / US-012).
 *
 * Owns DX only: activation auto-index, progress, client cancel, save re-index trigger,
 * Proposed orchestrator base URL settings.
 * FastAPI owns pack / ignore / consent / embed / Qdrant — never reimplemented here.
 */

import * as vscode from "vscode";
import { postIndex, IndexClientError } from "./api/indexClient";
import { readExtensionConfig } from "./config";
import { triggerAutoIndex } from "./indexing/autoIndex";
import { registerOnSaveReindex } from "./indexing/onSaveReindex";
import { runWithIndexProgress, type IndexProgressHost } from "./indexing/progress";
import { resolvePrimaryWorkspace } from "./indexing/workspace";

let indexingInFlight = false;

export function activate(context: vscode.ExtensionContext): void {
  const progressHost = createProgressHost();

  const getConfig = () => readExtensionConfig(vscode.workspace.getConfiguration.bind(vscode.workspace));

  const showInfo = (m: string) => {
    void vscode.window.showInformationMessage(m);
  };
  const showWarn = (m: string) => {
    void vscode.window.showWarningMessage(m);
  };
  const showError = (m: string) => {
    void vscode.window.showErrorMessage(m);
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
      // T057: optional observational timing — hardware-gated, not a hard SLA
      console.log(
        `[ContextOS][obs] auto-index wall_ms=${ms} server_time_ms=${result.time_ms} files=${result.files_indexed}`,
      );
    },
  }).finally(() => {
    // auto-index sets its own progress; clear guard if we want overlap protection
  });
}

export function deactivate(): void {
  // no-op
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
