/**
 * US-012: on save → incremental re-index via Proposed reuse of POST /index.
 * Sends Confirmed {repo_path, repo_name} plus Proposed optional `files` (OQ-14).
 * Does NOT invent new endpoints. Does NOT apply client-side ignore policy.
 */

import { postIndex, IndexClientError } from "../api/indexClient";
import type { ExtensionConfig } from "../config";
import { runWithIndexProgress, type IndexProgressHost } from "./progress";
import {
  relativeWorkspacePath,
  resolvePrimaryWorkspace,
  type WorkspaceFolderLike,
} from "./workspace";

export interface SavedDocumentLike {
  uri: { fsPath: string; scheme: string };
}

export interface OnSaveReindexDeps {
  config: ExtensionConfig;
  workspaceFolders: readonly WorkspaceFolderLike[] | undefined;
  progressHost: IndexProgressHost;
  showWarningMessage: (message: string) => void;
  showErrorMessage: (message: string) => void;
  fetchImpl?: typeof fetch;
  /** Debounce / in-flight guard — optional */
  isIndexing?: () => boolean;
  setIndexing?: (v: boolean) => void;
}

export interface SaveReindexResult {
  skipped: boolean;
  reason?: string;
  cancelled?: boolean;
  /** Proposed files[] sent (OQ-14) */
  proposedFiles?: string[];
}

/**
 * Trigger incremental re-index for a saved file.
 * Client sends path only; backend ignore/consent/pack policy applies.
 */
export async function triggerSaveReindex(
  doc: SavedDocumentLike,
  deps: OnSaveReindexDeps,
): Promise<SaveReindexResult> {
  if (!deps.config.reindexOnSave) {
    return { skipped: true, reason: "reindexOnSave disabled" };
  }
  if (doc.uri.scheme !== "file") {
    return { skipped: true, reason: "non-file scheme" };
  }

  const repo = resolvePrimaryWorkspace(deps.workspaceFolders);
  if (!repo) {
    return { skipped: true, reason: "no workspace folder" };
  }

  const rel = relativeWorkspacePath(repo.repo_path, doc.uri.fsPath);
  if (!rel) {
    return { skipped: true, reason: "file outside workspace" };
  }

  if (deps.isIndexing?.()) {
    return { skipped: true, reason: "index already in progress" };
  }

  deps.setIndexing?.(true);
  try {
    // Proposed (OQ-14): optional files scope — not Confirmed Appendix D
    const proposedFiles = [rel];
    await runWithIndexProgress(
      deps.progressHost,
      "ContextOS: Re-indexing saved file…",
      async (signal, progress) => {
        progress.report({ message: rel });
        const signalWithTimeout = combineTimeout(signal, deps.config.indexTimeoutMs);
        return postIndex(
          deps.config.orchestratorBaseUrl,
          {
            repo_path: repo.repo_path,
            repo_name: repo.repo_name,
            // Proposed (OQ-14) — narrower scope; backend may ignore until Confirmed
            files: proposedFiles,
          },
          { signal: signalWithTimeout, fetchImpl: deps.fetchImpl },
        );
      },
    );
    return { skipped: false, proposedFiles };
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      deps.showWarningMessage("ContextOS: re-index cancelled.");
      return { skipped: false, cancelled: true, proposedFiles: [rel] };
    }
    const msg =
      err instanceof IndexClientError
        ? err.message
        : err instanceof Error
          ? err.message
          : String(err);
    deps.showErrorMessage(`ContextOS: save re-index failed — ${msg}`);
    return { skipped: false, reason: msg, proposedFiles: [rel] };
  } finally {
    deps.setIndexing?.(false);
  }
}

function combineTimeout(signal: AbortSignal, timeoutMs: number): AbortSignal {
  if (typeof AbortSignal !== "undefined" && "timeout" in AbortSignal && typeof AbortSignal.timeout === "function") {
    const timed = AbortSignal.timeout(timeoutMs);
    if (typeof AbortSignal.any === "function") {
      return AbortSignal.any([signal, timed]);
    }
  }
  return signal;
}

export type DisposeFn = () => void;

export interface SaveListenerHost {
  onDidSaveTextDocument: (
    listener: (doc: SavedDocumentLike) => void,
  ) => { dispose: DisposeFn };
}

/**
 * Register workspace save listener (T063).
 */
export function registerOnSaveReindex(
  host: SaveListenerHost,
  getDeps: () => OnSaveReindexDeps,
): { dispose: DisposeFn } {
  return host.onDidSaveTextDocument((doc) => {
    void triggerSaveReindex(doc, getDeps());
  });
}
