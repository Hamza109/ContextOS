import type { IndexProgressHost, ProgressReporter } from "../../src/indexing/progress";
import type { CancellationTokenLike } from "../../src/indexing/progress";

/** In-memory progress host for unit tests (no VS Code host required). */
export function createTestProgressHost(opts?: {
  cancelAfterMs?: number;
}): IndexProgressHost & { lastTitle?: string; aborted?: boolean } {
  const host: IndexProgressHost & { lastTitle?: string; aborted?: boolean } = {
    locationNotification: 15,
    lastTitle: undefined,
    aborted: false,
    withProgress: async (options, task) => {
      host.lastTitle = options.title;
      let cancelled = false;
      const listeners: Array<() => void> = [];
      const token: CancellationTokenLike = {
        get isCancellationRequested() {
          return cancelled;
        },
        onCancellationRequested: (listener) => {
          listeners.push(listener);
          return {
            dispose() {
              const i = listeners.indexOf(listener);
              if (i >= 0) listeners.splice(i, 1);
            },
          };
        },
      };
      const progress: ProgressReporter = {
        report() {},
      };

      if (opts?.cancelAfterMs !== undefined) {
        setTimeout(() => {
          cancelled = true;
          host.aborted = true;
          for (const l of listeners) l();
        }, opts.cancelAfterMs);
      }

      return task(progress, token);
    },
  };
  return host;
}

export function createMockFetch(handler: (url: string, init?: RequestInit) => Promise<Response>) {
  return (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
    return handler(url, init);
  }) as typeof fetch;
}
