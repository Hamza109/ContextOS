/**
 * Activation auto-index (FR-013 / US-011).
 * Triggers POST /index only — FastAPI owns pack/ignore/embed/consent.
 */

import { postIndex, IndexClientError } from "../api/indexClient";
import type { IndexResponse } from "../api/types";
import type { ExtensionConfig } from "../config";
import { runWithIndexProgress, type IndexProgressHost } from "./progress";
import { resolvePrimaryWorkspace, type WorkspaceFolderLike } from "./workspace";

export interface AutoIndexDeps {
  config: ExtensionConfig;
  workspaceFolders: readonly WorkspaceFolderLike[] | undefined;
  progressHost: IndexProgressHost;
  showInformationMessage: (message: string) => void;
  showWarningMessage: (message: string) => void;
  showErrorMessage: (message: string) => void;
  fetchImpl?: typeof fetch;
  /** Optional observational timing (T057 / NFR-004) — hardware-gated, not SLA. */
  logTiming?: (ms: number, result: IndexResponse) => void;
}

export interface AutoIndexResult {
  skipped: boolean;
  reason?: string;
  response?: IndexResponse;
  cancelled?: boolean;
  durationMs?: number;
}

/**
 * On activation: if autoIndexOnActivate and a folder exists, POST /index
 * with Confirmed {repo_path, repo_name} only.
 */
export async function triggerAutoIndex(deps: AutoIndexDeps): Promise<AutoIndexResult> {
  if (!deps.config.autoIndexOnActivate) {
    return { skipped: true, reason: "autoIndexOnActivate disabled" };
  }

  const repo = resolvePrimaryWorkspace(deps.workspaceFolders);
  if (!repo) {
    deps.showWarningMessage("ContextOS: no workspace folder open — skipping auto-index.");
    return { skipped: true, reason: "no workspace folder" };
  }

  const started = Date.now();
  try {
    const response = await runWithIndexProgress(
      deps.progressHost,
      "ContextOS: Indexing repository…",
      async (signal, progress) => {
        progress.report({ message: `${repo.repo_name}` });
        // Proposed: client timeout combined with cancel token (OQ-CANCEL)
        const signalWithTimeout = combineTimeout(signal, deps.config.indexTimeoutMs);
        return postIndex(
          deps.config.orchestratorBaseUrl,
          {
            // Confirmed request body only for full auto-index
            repo_path: repo.repo_path,
            repo_name: repo.repo_name,
          },
          { signal: signalWithTimeout, fetchImpl: deps.fetchImpl },
        );
      },
    );

    const durationMs = Date.now() - started;
    deps.logTiming?.(durationMs, response);
    deps.showInformationMessage(
      `ContextOS: indexed ${response.files_indexed} files (${response.embeddings} embeddings) in ${response.time_ms}ms`,
    );
    return { skipped: false, response, durationMs };
  } catch (err) {
    if (isAbort(err)) {
      deps.showWarningMessage("ContextOS: indexing cancelled.");
      return { skipped: false, cancelled: true, durationMs: Date.now() - started };
    }
    const msg =
      err instanceof IndexClientError
        ? err.message
        : err instanceof Error
          ? err.message
          : String(err);
    deps.showErrorMessage(`ContextOS: auto-index failed — ${msg}`);
    return { skipped: false, reason: msg, durationMs: Date.now() - started };
  }
}

function isAbort(err: unknown): boolean {
  return err instanceof Error && err.name === "AbortError";
}

/** Proposed: merge user cancel with client timeout AbortSignal. */
function combineTimeout(signal: AbortSignal, timeoutMs: number): AbortSignal {
  if (typeof AbortSignal !== "undefined" && "timeout" in AbortSignal && typeof AbortSignal.timeout === "function") {
    const timed = AbortSignal.timeout(timeoutMs);
    if (typeof AbortSignal.any === "function") {
      return AbortSignal.any([signal, timed]);
    }
  }
  // Fallback: rely on progress cancel only when AbortSignal.timeout/any unavailable
  return signal;
}
