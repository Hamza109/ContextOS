/**
 * T028 — definition hover/command DX smoke (thin MCP; no policy).
 */
import { describe, expect, it, vi } from "vitest";
import { SerenaMcpClient, SerenaUnavailableError } from "../src/mcp/serenaClient";
import { InMemorySerenaSession } from "../src/mcp/inMemorySession";
import { formatDefinitionResult, runDefinitionLookup } from "../src/commands/definitionLookup";
import { formatHoverMarkdown } from "../src/providers/hoverProvider";
import { Position } from "./mocks/vscode";

function makeEditor(opts: {
  path: string;
  line: number;
  col: number;
  word: string;
}) {
  const wordRange = {
    start: new Position(opts.line, opts.col),
    end: new Position(opts.line, opts.col + opts.word.length),
  };
  return {
    document: {
      uri: { fsPath: opts.path, scheme: "file" },
      getWordRangeAtPosition: () => wordRange,
      getText: (range?: { start: Position; end: Position }) =>
        range ? opts.word : opts.word,
    },
    selection: {
      active: new Position(opts.line, opts.col),
      isEmpty: true,
    },
  };
}

describe("definition_lookup_dx (T028/T032/T033)", () => {
  it("command presents Serena definition via injected MCP session", async () => {
    const session = new InMemorySerenaSession({
      definitions: {
        foo: {
          path: "/repo/src/foo.ts",
          line: 10,
          signature: "function foo(): void",
          docstring: "Does foo",
        },
      },
    });
    const client = new SerenaMcpClient({ session });
    const info = vi.fn();
    const result = await runDefinitionLookup({
      getClient: () => client,
      getEditor: () =>
        makeEditor({ path: "/repo/src/bar.ts", line: 0, col: 0, word: "foo" }) as never,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInformationMessage: info,
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
    });

    expect(result?.path).toBe("/repo/src/foo.ts");
    expect(result?.line).toBe(10);
    expect(info).toHaveBeenCalled();
    expect(formatDefinitionResult(result!)).toContain("foo.ts:10");
  });

  it("hover markdown includes signature without local symbol graph", () => {
    const md = formatHoverMarkdown(
      { contents: "hover docs" },
      {
        path: "a.ts",
        line: 3,
        signature: "export const x = 1",
        docstring: "x doc",
      },
    );
    expect(md).toContain("hover docs");
    expect(md).toContain("a.ts:3");
    expect(md).toContain("export const x = 1");
  });

  it("surfaces clear unavailable error when MCP session missing (T070)", async () => {
    const client = new SerenaMcpClient();
    const err = vi.fn();
    const result = await runDefinitionLookup({
      getClient: () => client,
      getEditor: () =>
        makeEditor({ path: "/repo/a.ts", line: 0, col: 0, word: "x" }) as never,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: err,
    });
    expect(result).toBeUndefined();
    expect(err.mock.calls[0][0]).toMatch(/Serena MCP unavailable/i);
    await expect(client.findDefinition({ path: "a", line: 1, column: 0 })).rejects.toBeInstanceOf(
      SerenaUnavailableError,
    );
  });
});
