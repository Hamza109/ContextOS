/**
 * Pack Context command (T063 / T064) — Proposed ID contextos.packContext.
 * Calls contextClient → Confirmed POST /context; no local pack/search/index.
 */

import type * as vscode from "vscode";
import { postContext, ContextClientError } from "../api/contextClient";
import type { ContextRequest, ContextResponse } from "../api/types";
import type { ExtensionConfig } from "../config";
import { formatPackContextReport } from "../providers/packContextPresenter";
import { snapshotActiveEditor } from "./editorContext";

export const PACK_CONTEXT_COMMAND = "contextos.packContext";

export const DEFAULT_PACK_TOP_K = 8;

export interface PackContextDeps {
  getConfig: () => ExtensionConfig;
  getEditor: () => vscode.TextEditor | undefined;
  workspaceFolders: () => readonly vscode.WorkspaceFolder[] | undefined;
  showInformationMessage: (m: string) => void;
  showWarningMessage: (m: string) => void;
  showErrorMessage: (m: string) => void;
  presentReport: (text: string) => void;
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  /** Optional override query (e.g. from menu args). */
  queryOverride?: string;
}

export function buildContextRequest(
  snap: NonNullable<ReturnType<typeof snapshotActiveEditor>>,
  queryOverride?: string,
  topK: number = DEFAULT_PACK_TOP_K,
): ContextRequest | undefined {
  const query = (queryOverride ?? (snap.selectionText || snap.symbol || "")).trim();
  if (!query) {
    return undefined;
  }
  if (!snap.repoName) {
    return undefined;
  }
  const req: ContextRequest = {
    query,
    repo: snap.repoName,
    top_k: topK,
  };
  if (snap.relativePath) {
    req.file = snap.relativePath;
  }
  return req;
}

export async function runPackContext(
  deps: PackContextDeps,
): Promise<ContextResponse | undefined> {
  const snap = snapshotActiveEditor(deps.getEditor(), deps.workspaceFolders());
  if (!snap) {
    deps.showWarningMessage("ContextOS: open a workspace file to Pack Context.");
    return undefined;
  }
  const body = buildContextRequest(snap, deps.queryOverride);
  if (!body) {
    deps.showWarningMessage(
      "ContextOS: select text or place the cursor on a symbol to Pack Context.",
    );
    return undefined;
  }

  const config = deps.getConfig();
  try {
    const response = await postContext(config.orchestratorBaseUrl, body, {
      fetchImpl: deps.fetchImpl,
      signal: deps.signal,
    });
    deps.presentReport(formatPackContextReport(response));
    deps.showInformationMessage(
      `ContextOS: Pack Context ready (${response.metrics.tokens_after} compacted tokens)`,
    );
    return response;
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      deps.showWarningMessage("ContextOS: Pack Context cancelled.");
      return undefined;
    }
    const msg =
      err instanceof ContextClientError
        ? err.message
        : err instanceof Error
          ? err.message
          : String(err);
    deps.showErrorMessage(`ContextOS: Pack Context failed — ${msg}`);
    return undefined;
  }
}
