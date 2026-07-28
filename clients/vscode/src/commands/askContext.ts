/**
 * Ask ContextOS command (T040 / T044) — Proposed ID contextos.askContext.
 *
 * Distinct from Pack Context (`contextos.packContext`):
 *   - Ask prompts for a natural-language query via InputBox (selection as default).
 *   - Pack uses selection/symbol directly without an NL prompt.
 *
 * Thin client of Confirmed POST /context via postContext — no local pack/search/symbol/ignore/consent.
 *
 * Proposed click-count fixture (OQ-Ask-DX / T032 / SC-003):
 *   Command Palette → "ContextOS: Ask ContextOS" = 1–2 gestures (<3 clicks).
 *   Optional keybinding / editor context menu are alternate Proposed paths (OQ remains open).
 *
 * SC-004 / OQ-IDE-2s-Harness: client-side latency logging is Proposed instrumentation only —
 * MUST NOT invent Pass/Fail without harness evidence (T039 / T046).
 */

import type * as vscode from "vscode";
import { postContext, ContextClientError } from "../api/contextClient";
import type { ContextRequest, ContextResponse } from "../api/types";
import type { ExtensionConfig } from "../config";
import { resolvePrimaryWorkspace } from "../indexing/workspace";
import { formatAskContextReport } from "../providers/askContextPresenter";
import { snapshotActiveEditor } from "./editorContext";

/** Proposed command ID — not Confirmed product freeze. */
export const ASK_CONTEXT_COMMAND = "contextos.askContext";

export const DEFAULT_ASK_TOP_K = 8;

/**
 * Proposed error copy (NFR-006) — visible failure when orchestrator unreachable / non-2xx.
 * Not Confirmed product strings.
 */
export const ASK_ERROR_UNREACHABLE =
  "ContextOS: Ask failed — orchestrator unreachable. Check contextos.orchestratorBaseUrl and that the backend is running.";

export const ASK_ERROR_HTTP =
  "ContextOS: Ask failed — orchestrator returned an error. Ensure the workspace is indexed and try again.";

/** Proposed obs log prefix for Ask success latency (T046) — do not claim SC-004 Pass. */
export const ASK_LATENCY_LOG_PREFIX = "[ContextOS][obs][ask]";

export interface AskContextDeps {
  getConfig: () => ExtensionConfig;
  getEditor: () => vscode.TextEditor | undefined;
  workspaceFolders: () => readonly vscode.WorkspaceFolder[] | undefined;
  showInputBox: (options: {
    title?: string;
    prompt?: string;
    placeHolder?: string;
    value?: string;
    ignoreFocusOut?: boolean;
  }) => Thenable<string | undefined>;
  showInformationMessage: (m: string) => void;
  showWarningMessage: (m: string) => void;
  showErrorMessage: (m: string) => void;
  presentReport: (text: string) => void;
  /** Proposed: latency logger (console or output channel). */
  logLatency?: (wallMs: number, serverLatencyMs: number) => void;
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  /** Optional override query (skips InputBox — tests / menu args). */
  queryOverride?: string;
}

/**
 * Map NL query + optional editor/workspace bias to Confirmed ContextRequest fields only.
 */
export function buildAskContextRequest(opts: {
  query: string;
  repo: string;
  file?: string;
  topK?: number;
}): ContextRequest | undefined {
  const query = opts.query.trim();
  if (!query) {
    return undefined;
  }
  if (!opts.repo.trim()) {
    return undefined;
  }
  const req: ContextRequest = {
    query,
    repo: opts.repo,
    top_k: opts.topK ?? DEFAULT_ASK_TOP_K,
  };
  if (opts.file) {
    req.file = opts.file;
  }
  return req;
}

function formatAskFailureMessage(err: unknown): string {
  if (err instanceof ContextClientError) {
    if (err.status === undefined) {
      // Network / unreachable only when fetch threw (message carries "network error")
      if (/network error/i.test(err.message) || /fetch is not available/i.test(err.message)) {
        return ASK_ERROR_UNREACHABLE;
      }
      // Validation / parse failures after a response — do not mislabel as unreachable
      return `${ASK_ERROR_HTTP} (${err.message})`;
    }
    // Non-2xx after HTTP response
    return `${ASK_ERROR_HTTP} (${err.message})`;
  }
  if (err instanceof Error) {
    return `ContextOS: Ask failed — ${err.message}`;
  }
  return `ContextOS: Ask failed — ${String(err)}`;
}

export async function runAskContext(
  deps: AskContextDeps,
): Promise<ContextResponse | undefined> {
  const ws = resolvePrimaryWorkspace(deps.workspaceFolders());
  if (!ws) {
    deps.showWarningMessage("ContextOS: open a workspace folder to Ask ContextOS.");
    return undefined;
  }

  const snap = snapshotActiveEditor(deps.getEditor(), deps.workspaceFolders());
  const defaultQuery = snap?.selectionText?.trim() || "";

  let query: string | undefined = deps.queryOverride;
  if (query === undefined) {
    query = await deps.showInputBox({
      title: "ContextOS: Ask ContextOS",
      prompt: "Ask a natural-language question about this workspace",
      placeHolder: "e.g. How does authentication work?",
      value: defaultQuery,
      ignoreFocusOut: true,
    });
  }

  if (query === undefined) {
    // User cancelled InputBox — not an error
    return undefined;
  }

  const body = buildAskContextRequest({
    query,
    repo: ws.repo_name,
    file: snap?.relativePath,
  });
  if (!body) {
    deps.showWarningMessage("ContextOS: enter a non-empty question to Ask ContextOS.");
    return undefined;
  }

  const config = deps.getConfig();
  const started = Date.now();
  try {
    const response = await postContext(config.orchestratorBaseUrl, body, {
      fetchImpl: deps.fetchImpl,
      signal: deps.signal,
    });
    const wallMs = Date.now() - started;
    // Proposed client-side latency logging (T046) — instrumentation only; SC-004 Pass blocked.
    const log =
      deps.logLatency ??
      ((wall, server) => {
        console.log(
          `${ASK_LATENCY_LOG_PREFIX} wall_ms=${wall} server_latency_ms=${server}`,
        );
      });
    log(wallMs, response.metrics.latency_ms);

    deps.presentReport(formatAskContextReport(response));
    deps.showInformationMessage(
      `ContextOS: Ask ready (${response.metrics.tokens_after} compacted tokens)`,
    );
    return response;
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      deps.showWarningMessage("ContextOS: Ask cancelled.");
      return undefined;
    }
    deps.showErrorMessage(formatAskFailureMessage(err));
    return undefined;
  }
}
