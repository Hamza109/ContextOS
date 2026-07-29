/**
 * ContextOS Graph / Blast React Flow Webview panel (EP-007 / US-020).
 *
 * Consumes FastAPI GET /blast JSON only — does not embed graph.html
 * (auth NEEDS CLARIFICATION). Presentation + sanitized IPC only.
 */

import * as vscode from "vscode";
import { getBlast, BlastClientError } from "../api/blastClient";
import type { BlastResponse } from "../api/types";
import type { ExtensionConfig } from "../config";
import { blastResponseToGraphModel } from "./blastGraphModel";
import {
  evaluateStaleness,
  FreshnessSession,
  type StalenessState,
} from "./stalenessPresenter";
import {
  sanitizeExtToWebviewMessage,
  sanitizeWebviewToExtMessage,
  type ExtToWebviewMessage,
} from "./webviewSanitize";

export const SHOW_BLAST_GRAPH_COMMAND = "contextos.showBlastGraph";

export interface GraphBlastPanelDeps {
  extensionUri: vscode.Uri;
  getConfig: () => ExtensionConfig;
  getEditor: () => vscode.TextEditor | undefined;
  workspaceFolders: () => readonly vscode.WorkspaceFolder[] | undefined;
  resolveRepo: () => { repo_name: string; repo_path: string } | undefined;
  relativePathFor: (editor: vscode.TextEditor) => string | undefined;
  showWarningMessage: (m: string) => void;
  showErrorMessage: (m: string) => void;
  openFile?: (relativePath: string) => Promise<void>;
  fetchImpl?: typeof fetch;
  freshnessSession: FreshnessSession;
  createWebviewPanel?: typeof vscode.window.createWebviewPanel;
  statusBarItem?: vscode.StatusBarItem;
}

let activePanel: vscode.WebviewPanel | undefined;

export function getActiveGraphBlastPanel(): vscode.WebviewPanel | undefined {
  return activePanel;
}

/** Test hook: inject panel without VS Code host (Proposed). */
export function setActiveGraphBlastPanelForTests(
  panel: vscode.WebviewPanel | undefined,
): void {
  activePanel = panel;
}

/**
 * Open or reveal the blast/graph React Flow panel and load FastAPI blast data.
 */
export async function openGraphBlastPanel(deps: GraphBlastPanelDeps): Promise<void> {
  const config = deps.getConfig();
  if (!config.enableGraphBlastPanel) {
    deps.showWarningMessage(
      "ContextOS: Graph/Blast panel disabled (contextos.enableGraphBlastPanel).",
    );
    return;
  }

  const repo = deps.resolveRepo();
  if (!repo) {
    deps.showWarningMessage("ContextOS: open a workspace folder to show blast graph.");
    return;
  }

  const editor = deps.getEditor();
  const fileName = editor ? deps.relativePathFor(editor) : undefined;
  if (!fileName) {
    deps.showWarningMessage("ContextOS: open a file to show blast radius.");
    return;
  }

  const createPanel = deps.createWebviewPanel ?? vscode.window.createWebviewPanel.bind(vscode.window);
  if (activePanel) {
    activePanel.reveal(vscode.ViewColumn.Beside);
  } else {
    activePanel = createPanel(
      "contextos.graphBlast",
      "ContextOS Blast Graph",
      vscode.ViewColumn.Beside,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [
          vscode.Uri.joinPath(deps.extensionUri, "media"),
        ],
      },
    );
    activePanel.onDidDispose(() => {
      activePanel = undefined;
      deps.statusBarItem?.hide();
    });
    activePanel.webview.onDidReceiveMessage((raw) => {
      void handleWebviewMessage(raw, deps);
    });
  }

  const nonce = createNonce();
  activePanel.webview.html = buildWebviewHtml(activePanel.webview, deps.extensionUri, nonce);
  await loadBlastIntoPanel(deps, fileName, repo.repo_name);
}

async function handleWebviewMessage(raw: unknown, deps: GraphBlastPanelDeps): Promise<void> {
  const msg = sanitizeWebviewToExtMessage(raw);
  if (!msg) return;

  if (msg.type === "ready" || msg.type === "refresh") {
    const repo = deps.resolveRepo();
    const editor = deps.getEditor();
    const fileName = editor ? deps.relativePathFor(editor) : undefined;
    if (!repo || !fileName) return;
    await loadBlastIntoPanel(deps, fileName, repo.repo_name);
    return;
  }

  if (msg.type === "openFile" && deps.openFile) {
    await deps.openFile(msg.path);
  }
}

export async function loadBlastIntoPanel(
  deps: GraphBlastPanelDeps,
  fileName: string,
  repo: string,
): Promise<{ blast?: BlastResponse; staleState?: StalenessState }> {
  if (!activePanel) return {};

  postToWebview(activePanel, {
    type: "status",
    message: "Loading blast from FastAPI…",
  });

  const config = deps.getConfig();
  try {
    const blast = await getBlast(config.orchestratorBaseUrl, fileName, repo, {
      fetchImpl: deps.fetchImpl,
    });

    const staleState = evaluateStaleness(
      {
        stale: blast.stale,
        indexRevision: blast.index_revision,
        baselineRevision: deps.freshnessSession.getBaseline(),
      },
      { showStalenessWarnings: config.showStalenessWarnings },
    );

    // Adopt baseline on first fresh load or after markIndexed cleared it.
    if (!staleState.isStale && blast.index_revision) {
      deps.freshnessSession.adoptFreshRevision(blast.index_revision);
    }

    const model = blastResponseToGraphModel(fileName, blast);
    if (model.nodes.length <= 1 && blast.direct_dependents.length === 0 && blast.transitive.length === 0) {
      postToWebview(activePanel, {
        type: "empty",
        message: `No dependents returned for ${fileName} (empty blast — not fabricated).`,
      });
    }

    postToWebview(activePanel, {
      type: "blastGraph",
      fileName,
      risk: blast.risk,
      nodes: model.nodes,
      edges: model.edges,
      stale: staleState.isStale,
      badge: staleState.badgeText,
      indexRevision: blast.index_revision ?? null,
    });

    updateStatusBar(deps, staleState);
    return { blast, staleState };
  } catch (err) {
    const message =
      err instanceof BlastClientError
        ? err.message
        : err instanceof Error
          ? err.message
          : String(err);
    postToWebview(activePanel, { type: "error", message });
    deps.showErrorMessage(`ContextOS: blast graph failed — ${message}`);
    return {};
  }
}

function postToWebview(panel: vscode.WebviewPanel, raw: ExtToWebviewMessage): void {
  const sanitized = sanitizeExtToWebviewMessage(raw);
  if (!sanitized) return;
  void panel.webview.postMessage(sanitized);
}

function updateStatusBar(deps: GraphBlastPanelDeps, state: StalenessState): void {
  const item = deps.statusBarItem;
  if (!item) return;
  if (state.isStale && state.badgeText) {
    item.text = `$(warning) ContextOS: ${state.badgeText}`;
    item.tooltip =
      "Proposed freshness signal (US-027). Threshold NEEDS CLARIFICATION. Refresh after index to clear.";
    item.show();
  } else {
    item.text = "$(check) ContextOS: index fresh";
    item.tooltip = "Proposed freshness OK (or warnings disabled).";
    item.show();
  }
}

/**
 * Secure Webview HTML — CSP + nonce; script from local media only.
 * React Flow app is bundled to media/graphBlast.js (see scripts/build-webview.mjs).
 *
 * NOTE: Prefer GET /blast JSON for React Flow. Serving/embedding API HTML graph
 * views remains auth NEEDS CLARIFICATION (api-contract §2.5) — not used here.
 */
export function buildWebviewHtml(
  webview: vscode.Webview,
  extensionUri: vscode.Uri,
  nonce: string,
): string {
  const scriptUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "graphBlast.js"),
  );
  const styleUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "graphBlast.css"),
  );
  const csp = [
    `default-src 'none'`,
    `img-src ${webview.cspSource} data:`,
    `style-src ${webview.cspSource} 'unsafe-inline'`,
    `script-src 'nonce-${nonce}'`,
  ].join("; ");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Content-Security-Policy" content="${csp}" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ContextOS Blast Graph</title>
  <link rel="stylesheet" href="${styleUri}" />
  <style>
    html, body, #root { height: 100%; margin: 0; background: #0f172a; color: #e2e8f0; font-family: var(--vscode-font-family, sans-serif); }
    #badge { display: none; position: absolute; z-index: 10; top: 8px; right: 8px; padding: 4px 10px; background: #b45309; color: #fff; border-radius: 4px; font-size: 12px; }
    #badge.visible { display: block; }
    #banner { padding: 8px 12px; font-size: 12px; background: #1e293b; border-bottom: 1px solid #334155; }
    #banner.error { background: #7f1d1d; }
    #banner.empty { background: #334155; }
  </style>
</head>
<body>
  <div id="badge" role="status" aria-live="polite"></div>
  <div id="banner">Loading…</div>
  <div id="root"></div>
  <!-- API HTML graph auth NEEDS CLARIFICATION — React Flow uses GET /blast JSON only -->
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
}

export function createNonce(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let out = "";
  for (let i = 0; i < 32; i++) {
    out += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return out;
}
