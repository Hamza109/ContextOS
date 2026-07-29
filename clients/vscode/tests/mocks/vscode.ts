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
  joinPath: (base: { fsPath?: string; path?: string }, ...parts: string[]) => {
    const root = base.fsPath ?? base.path ?? "";
    return { fsPath: [root, ...parts].join("/"), scheme: "file" };
  },
};

export const ViewColumn = {
  Beside: 2,
  One: 1,
} as const;

export const StatusBarAlignment = {
  Left: 1,
  Right: 2,
} as const;

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
  showInputBox: async (_opts?: unknown): Promise<string | undefined> => undefined,
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
  createStatusBarItem: (_alignment?: number, _priority?: number) => ({
    text: "",
    tooltip: "",
    command: undefined as string | undefined,
    show: () => undefined,
    hide: () => undefined,
    dispose: () => undefined,
  }),
  createWebviewPanel: (
    _viewType: string,
    _title: string,
    _showOptions: unknown,
    _options?: unknown,
  ) => {
    const messages: unknown[] = [];
    const panel = {
      reveal: (_column?: unknown) => undefined,
      onDidDispose: (_listener: () => void) => ({ dispose() {} }),
      webview: {
        html: "",
        cspSource: "vscode-webview://test",
        postMessage: async (msg: unknown) => {
          messages.push(msg);
          return true;
        },
        onDidReceiveMessage: (_listener: (msg: unknown) => void) => ({ dispose() {} }),
        asWebviewUri: (uri: { fsPath: string }) => ({
          toString: () => `webview://${uri.fsPath}`,
        }),
      },
      dispose: () => undefined,
      _messages: messages,
    };
    return panel;
  },
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
  extensionUri: { fsPath: string; scheme: string };
};

export type TextEditor = NonNullable<typeof window.activeTextEditor>;
export type WorkspaceFolder = { uri: { fsPath: string }; name: string };
export type StatusBarItem = ReturnType<typeof window.createStatusBarItem>;
export type WebviewPanel = ReturnType<typeof window.createWebviewPanel>;
export type TextDocument = { uri: { fsPath: string }; getText: () => string };
export type Uri = { fsPath: string; scheme: string };
