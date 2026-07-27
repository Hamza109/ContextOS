/**
 * Minimal vscode stub for vitest (Proposed — not @vscode/test-electron host).
 * Integration tests against a real VS Code host are out of band for unit suite.
 */

export const ProgressLocation = {
  Notification: 15,
} as const;

export class Position {
  constructor(
    public line: number,
    public character: number,
  ) {}
}

export class Range {
  constructor(
    public start: Position,
    public end: Position,
  ) {}
}

export class Selection extends Range {
  constructor(anchor: Position, active: Position) {
    super(anchor, active);
  }
}

export class MarkdownString {
  constructor(
    public value: string = "",
    public supportThemeIcons: boolean = false,
  ) {}
}

export class Hover {
  constructor(
    public contents: MarkdownString | MarkdownString[],
    public range?: Range,
  ) {}
}

export const Uri = {
  file: (fsPath: string) => ({ fsPath, scheme: "file" }),
};

export const window = {
  activeTextEditor: undefined as
    | {
        document: {
          uri: { fsPath: string; scheme: string };
          getWordRangeAtPosition: (pos: Position) => Range | undefined;
          getText: (range?: Range) => string;
        };
        selection: {
          active: Position;
          isEmpty: boolean;
        };
      }
    | undefined,
  showInformationMessage: async (_m: string) => undefined,
  showWarningMessage: async (_m: string) => undefined,
  showErrorMessage: async (_m: string) => undefined,
  showQuickPick: async <T>(_items: T[], _opts?: unknown): Promise<T | T[] | undefined> =>
    undefined,
  showTextDocument: async (_doc: unknown) => ({
    selection: undefined as unknown,
    revealRange: (_r: Range) => undefined,
  }),
  createOutputChannel: (_name: string) => ({
    appendLine: (_s: string) => undefined,
    show: (_preserveFocus?: boolean) => undefined,
    dispose: () => undefined,
  }),
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
  openTextDocument: async (uri: { fsPath: string }) => ({
    uri,
    getText: () => "",
  }),
  asRelativePath: (pathOrUri: string | { fsPath: string }) =>
    typeof pathOrUri === "string" ? pathOrUri : pathOrUri.fsPath,
};

export const commands = {
  registerCommand: (_id: string, _fn: (...args: unknown[]) => unknown) => ({
    dispose() {},
  }),
};

export const languages = {
  registerHoverProvider: (_selector: unknown, _provider: unknown) => ({
    dispose() {},
  }),
};

export type ExtensionContext = {
  subscriptions: { dispose(): void }[];
};

export type TextEditor = NonNullable<typeof window.activeTextEditor>;
export type WorkspaceFolder = { uri: { fsPath: string }; name: string };
