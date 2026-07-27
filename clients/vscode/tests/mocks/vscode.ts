/**
 * Minimal vscode stub for vitest (Proposed — not @vscode/test-electron host).
 * Integration tests against a real VS Code host are out of band for EP-001 unit suite.
 */

export const ProgressLocation = {
  Notification: 15,
} as const;

export const window = {
  showInformationMessage: async (_m: string) => undefined,
  showWarningMessage: async (_m: string) => undefined,
  showErrorMessage: async (_m: string) => undefined,
  withProgress: async <T>(
    _options: unknown,
    task: (
      progress: { report: (v: { message?: string }) => void },
      token: {
        isCancellationRequested: boolean;
        onCancellationRequested: (cb: () => void) => { dispose(): void };
      },
    ) => Promise<T>,
  ): Promise<T> => {
    const token = {
      isCancellationRequested: false,
      onCancellationRequested: (_cb: () => void) => ({ dispose() {} }),
    };
    return task({ report() {} }, token);
  },
};

export const workspace = {
  workspaceFolders: undefined as
    | { uri: { fsPath: string }; name: string }[]
    | undefined,
  getConfiguration: (_section?: string) => ({
    get: <T>(_key: string): T | undefined => undefined,
  }),
  onDidSaveTextDocument: (_listener: (doc: unknown) => void) => ({
    dispose() {},
  }),
};

export const commands = {
  registerCommand: (_id: string, _fn: (...args: unknown[]) => unknown) => ({
    dispose() {},
  }),
};

export type ExtensionContext = {
  subscriptions: { dispose(): void }[];
};
