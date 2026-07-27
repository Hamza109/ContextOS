/**
 * T041 — find-references command + file-type filter UX (presentation only).
 */
import { describe, expect, it, vi } from "vitest";
import { SerenaMcpClient } from "../src/mcp/serenaClient";
import { InMemorySerenaSession } from "../src/mcp/inMemorySession";
import { runFindReferences } from "../src/commands/findReferences";
import {
  collectReferenceExtensions,
  filterReferencesByExtensions,
  formatReferencesReport,
} from "../src/providers/referencesPresenter";
import { Position } from "./mocks/vscode";

const hits = [
  {
    path: "src/a.ts",
    line: 2,
    contextBefore: ["prev"],
    contextAfter: ["next"],
    lineText: "foo()",
  },
  {
    path: "src/b.py",
    line: 5,
    contextBefore: ["p0"],
    contextAfter: ["p1"],
    lineText: "foo()",
  },
  {
    path: "lib/c.ts",
    line: 9,
    contextBefore: [],
    contextAfter: [],
    lineText: "foo",
  },
];

function makeEditor() {
  const wordRange = {
    start: new Position(0, 0),
    end: new Position(0, 3),
  };
  return {
    document: {
      uri: { fsPath: "/repo/src/main.ts", scheme: "file" },
      getWordRangeAtPosition: () => wordRange,
      getText: () => "foo",
    },
    selection: { active: new Position(0, 0), isEmpty: true },
  };
}

describe("find_references_dx (T041/T044)", () => {
  it("filters MCP hits by extension for UX only", () => {
    expect(collectReferenceExtensions(hits).sort()).toEqual([".py", ".ts"]);
    const onlyTs = filterReferencesByExtensions(hits, [".ts"]);
    expect(onlyTs).toHaveLength(2);
    expect(onlyTs.every((h) => h.path.endsWith(".ts"))).toBe(true);
    expect(filterReferencesByExtensions(hits, [])).toHaveLength(3);
  });

  it("command wires MCP → filter pick → report", async () => {
    const session = new InMemorySerenaSession({
      references: { foo: hits },
    });
    const client = new SerenaMcpClient({ session });
    const present = vi.fn();
    const pick = vi.fn(async () => [".ts"]);

    const filtered = await runFindReferences({
      getClient: () => client,
      getEditor: () => makeEditor() as never,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
      pickFileTypeFilters: pick,
      presentReport: present,
    });

    expect(pick).toHaveBeenCalled();
    expect(filtered).toHaveLength(2);
    expect(present).toHaveBeenCalled();
    const report = present.mock.calls[0][0] as string;
    expect(report).toContain("a.ts:2");
    expect(report).not.toContain("b.py");
    expect(formatReferencesReport("foo", filtered!)).toMatch(/2\)/);
  });

  it("does not invent local reference index — empty MCP yields empty report", async () => {
    const client = new SerenaMcpClient({ session: new InMemorySerenaSession() });
    const present = vi.fn();
    const filtered = await runFindReferences({
      getClient: () => client,
      getEditor: () => makeEditor() as never,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
      pickFileTypeFilters: async () => [],
      presentReport: present,
    });
    expect(filtered).toEqual([]);
    expect(present.mock.calls[0][0]).toMatch(/no references/);
  });
});
