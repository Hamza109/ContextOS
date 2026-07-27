/**
 * Progress notification UX for indexing (FR-015).
 * Cancellation is client-side AbortSignal only (OQ-CANCEL).
 */

export interface ProgressReporter {
  report(value: { message?: string; increment?: number }): void;
}

export interface CancellationTokenLike {
  isCancellationRequested: boolean;
  onCancellationRequested: (listener: () => void) => { dispose(): void };
}

export interface WithProgressOptions {
  title: string;
  cancellable: boolean;
}

export type WithProgressFn = <T>(
  options: WithProgressOptions,
  task: (
    progress: ProgressReporter,
    token: CancellationTokenLike,
  ) => Thenable<T>,
) => Thenable<T>;

export interface IndexProgressHost {
  withProgress: WithProgressFn;
  /** Optional: vscode.ProgressLocation.Notification value */
  locationNotification: number;
}

/**
 * Run an index operation under a cancellable progress notification.
 * Wires token → AbortController (client cancel only).
 */
export async function runWithIndexProgress<T>(
  host: IndexProgressHost,
  title: string,
  work: (signal: AbortSignal, progress: ProgressReporter) => Promise<T>,
): Promise<T> {
  return host.withProgress(
    {
      title,
      cancellable: true,
      // location set by caller wrapper if needed — we pass via host.withProgress binding
    } as WithProgressOptions & { location?: number },
    async (progress, token) => {
      const controller = new AbortController();
      const sub = token.onCancellationRequested(() => {
        controller.abort();
      });
      try {
        if (token.isCancellationRequested) {
          controller.abort();
        }
        progress.report({ message: "Calling orchestrator POST /index…" });
        return await work(controller.signal, progress);
      } finally {
        sub.dispose();
      }
    },
  );
}
