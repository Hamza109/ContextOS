/**
 * T049 / T050 — rename-scope review surface; no execute/sandbox claim.
 */
import { describe, expect, it, vi } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { SerenaMcpClient } from "../src/mcp/serenaClient";
import { InMemorySerenaSession } from "../src/mcp/inMemorySession";
import { runRenameScopeAnalysis } from "../src/commands/renameScope";
import {
  formatRenameScopeReport,
  renameScopeClaimsExecution,
  RENAME_SCOPE_REVIEW_DISCLAIMER,
} from "../src/providers/renameScopePresenter";
import { Position } from "./mocks/vscode";

const SRC_ROOT = path.resolve(__dirname, "../src");

function walkTsFiles(dir: string): string[] {
  const out: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walkTsFiles(full));
    else if (entry.name.endsWith(".ts")) out.push(full);
  }
  return out;
}

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

describe("rename_scope_dx (T049/T050/T052)", () => {
  it("presents analysis only — disclaimer, no execute claim", async () => {
    const session = new InMemorySerenaSession({
      renameScopes: {
        foo: {
          symbolName: "foo",
          safeScopePaths: ["src/a.ts", "src/b.ts"],
          breakingChangeCount: 2,
          notes: "callers outside module",
        },
      },
    });
    const present = vi.fn();
    const analysis = await runRenameScopeAnalysis({
      getClient: () => new SerenaMcpClient({ session }),
      getEditor: () => makeEditor() as never,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
      presentReport: present,
    });

    expect(analysis?.breakingChangeCount).toBe(2);
    const report = present.mock.calls[0][0] as string;
    expect(report).toContain(RENAME_SCOPE_REVIEW_DISCLAIMER);
    expect(report).toContain("Breaking-change count: 2");
    expect(renameScopeClaimsExecution(report)).toBe(false);
    expect(renameScopeClaimsExecution(formatRenameScopeReport(analysis!))).toBe(false);
  });

  it("static: extension surfaces do not claim ContextOS rename sandbox/execute APIs", () => {
    const files = walkTsFiles(SRC_ROOT);
    const forbidden = [
      /executeRename|applyRename|renameSandbox/i,
      /contextos\.executeRename/i,
      /WorkspaceEdit.*rename|rename.*WorkspaceEdit/i,
    ];
    const violations: string[] = [];
    for (const file of files) {
      const text = fs.readFileSync(file, "utf8");
      const stripped = text
        .split("\n")
        .filter((line) => !line.trim().startsWith("//") && !line.trim().startsWith("*"))
        .join("\n");
      // Allow the disclaimer / detection helpers that mention sandbox to forbid it
      if (file.endsWith("renameScopePresenter.ts")) continue;
      for (const re of forbidden) {
        if (re.test(stripped)) {
          violations.push(`${path.relative(SRC_ROOT, file)}: ${re}`);
        }
      }
    }
    expect(violations, violations.join("\n")).toEqual([]);
  });
});
