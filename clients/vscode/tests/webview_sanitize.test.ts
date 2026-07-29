/**
 * T028 / T031 — Webview message sanitize + no client blast/policy bypass (EP-007 US-020).
 */
import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { getBlast } from "../src/api/blastClient";
import {
  sanitizeExtToWebviewMessage,
  sanitizeWebviewToExtMessage,
} from "../src/providers/webviewSanitize";
import { createMockFetch } from "./helpers";

const SRC_ROOT = path.resolve(__dirname, "../src");

function walkTsFiles(dir: string): string[] {
  const out: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...walkTsFiles(full));
    } else if (entry.name.endsWith(".ts")) {
      out.push(full);
    }
  }
  return out;
}

function stripComments(text: string): string {
  return text
    .split("\n")
    .filter((line) => !line.trim().startsWith("//") && !line.trim().startsWith("*"))
    .join("\n");
}

describe("webview sanitize (T028/T031)", () => {
  it("allows blastGraph with path nodes/edges and drops unknown types", () => {
    const ok = sanitizeExtToWebviewMessage({
      type: "blastGraph",
      fileName: "src/a.ts",
      risk: "LOW",
      stale: false,
      nodes: [{ id: "src/a.ts", label: "src/a.ts", kind: "target" }],
      edges: [],
    });
    expect(ok?.type).toBe("blastGraph");

    expect(sanitizeExtToWebviewMessage({ type: "eval", code: "1+1" })).toBeUndefined();
    expect(
      sanitizeExtToWebviewMessage({
        type: "blastGraph",
        fileName: "<script>",
        risk: "LOW",
        stale: false,
        nodes: [],
        edges: [],
      }),
    ).toBeUndefined();
  });

  it("sanitizes webview→ext openFile paths and rejects garbage", () => {
    expect(sanitizeWebviewToExtMessage({ type: "ready" })).toEqual({ type: "ready" });
    expect(sanitizeWebviewToExtMessage({ type: "refresh" })).toEqual({ type: "refresh" });
    expect(sanitizeWebviewToExtMessage({ type: "openFile", path: "src/x.ts" })).toEqual({
      type: "openFile",
      path: "src/x.ts",
    });
    expect(
      sanitizeWebviewToExtMessage({ type: "openFile", path: "x\u0000y.ts" }),
    ).toBeUndefined();
    expect(sanitizeWebviewToExtMessage({ type: "runShell", cmd: "rm -rf /" })).toBeUndefined();
  });

  it("blast client only GETs /blast and never posts source bodies", async () => {
    let url = "";
    let method = "";
    const fetchImpl = createMockFetch(async (u, init) => {
      url = u;
      method = String(init?.method ?? "GET");
      return new Response(
        JSON.stringify({
          direct_dependents: ["b.ts"],
          transitive: [],
          db_tables: [],
          risk: "LOW",
          tests_to_run: [],
          owners: [],
          index_revision: "rev1",
        }),
        { status: 200 },
      );
    });

    const blast = await getBlast("http://orchestrator.test", "a.ts", "repo", { fetchImpl });
    expect(method).toBe("GET");
    expect(url).toBe("http://orchestrator.test/blast/a.ts?repo=repo");
    expect(blast.direct_dependents).toEqual(["b.ts"]);
    expect(blast).not.toHaveProperty("source");
  });

  it("source tree does not compute blast or reimplement policy (T028 regression)", () => {
    const files = walkTsFiles(SRC_ROOT);
    const forbiddenPatterns: Array<{ re: RegExp; why: string }> = [
      { re: /computeBlastRadius|traverseImports|reverseImportWalk/i, why: "client blast traversal" },
      { re: /ignore_policy|IgnorePolicy/, why: "client ignore policy" },
      { re: /createElement\(\s*['\"]iframe['\"]/i, why: "iframe embed of API HTML" },
    ];
    const violations: string[] = [];
    for (const file of files) {
      const stripped = stripComments(fs.readFileSync(file, "utf8"));
      for (const { re, why } of forbiddenPatterns) {
        if (re.test(stripped)) {
          violations.push(`${path.relative(SRC_ROOT, file)}: ${why}`);
        }
      }
    }
    expect(violations, violations.join("\n")).toEqual([]);
  });

  it("documents graph.html auth as NEEDS CLARIFICATION in panel HTML builder", () => {
    const panelSrc = fs.readFileSync(
      path.join(SRC_ROOT, "providers/graphBlastPanel.ts"),
      "utf8",
    );
    expect(panelSrc).toMatch(/NEEDS CLARIFICATION/);
    expect(panelSrc).toMatch(/GET \/blast/);
    expect(panelSrc).not.toMatch(/fetch\(.*graph\.html/);
  });
});
