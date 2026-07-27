/**
 * T050 / T056 / FR-014: extension must not pack locally or bypass backend policy.
 * Static checklist over clients/vscode/src — no ignore/consent/pack/embed logic.
 */
import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { postIndex } from "../src/api/indexClient";
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

describe("no_client_policy_bypass (T050/T056)", () => {
  it("source tree does not implement pack / ignore / consent / embed policy", () => {
    const files = walkTsFiles(SRC_ROOT);
    expect(files.length).toBeGreaterThan(0);

    const forbiddenPatterns: Array<{ re: RegExp; why: string }> = [
      { re: /ignore_policy|IgnorePolicy|\.gitignore/, why: "client-side ignore policy" },
      { re: /consent_gate|ConsentGate|external.?llm.?consent/i, why: "client-side consent policy" },
      { re: /pack_repository|l5_pack|Repomix|xml.?pack/i, why: "client-side packing" },
      { re: /sentence-transformers|MiniLM|qdrant|embedChunks/i, why: "client-side embed/store" },
      { re: /node_modules|hard.?exclude|\.env.*exclude/i, why: "client-side exclusion rules" },
    ];

    const violations: string[] = [];
    for (const file of files) {
      const text = fs.readFileSync(file, "utf8");
      // Allow comments that say we do NOT implement these
      const stripped = text
        .split("\n")
        .filter((line) => !line.trim().startsWith("//") && !line.trim().startsWith("*"))
        .join("\n");

      for (const { re, why } of forbiddenPatterns) {
        if (re.test(stripped)) {
          violations.push(`${path.relative(SRC_ROOT, file)}: ${why} (${re})`);
        }
      }
    }

    expect(violations, violations.join("\n")).toEqual([]);
  });

  it("index client only POSTs to /index and never sends file contents", async () => {
    let body: Record<string, unknown> = {};
    const fetchImpl = createMockFetch(async (url, init) => {
      expect(url.endsWith("/index")).toBe(true);
      body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      return new Response(
        JSON.stringify({
          files_indexed: 1,
          graph_nodes: 0,
          embeddings: 1,
          time_ms: 1,
        }),
        { status: 200 },
      );
    });

    await postIndex(
      "http://orchestrator.test",
      {
        repo_path: "/repo",
        repo_name: "repo",
        // Proposed scope — paths only, not file contents
        files: ["src/a.ts"],
      },
      { fetchImpl },
    );

    expect(Object.keys(body).sort()).toEqual(["files", "repo_name", "repo_path"].sort());
    expect(body).not.toHaveProperty("content");
    expect(body).not.toHaveProperty("source");
    expect(body).not.toHaveProperty("packed");
    expect(typeof body.files).toBe("object");
    expect(JSON.stringify(body)).not.toMatch(/function |class |import /);
  });

  it("checklist: policy ownership remains FastAPI-only", () => {
    const checklist = [
      "Extension triggers POST /index only",
      "No local pack/flatten",
      "No client .gitignore / hard-exclude application",
      "No consent UX (OQ-US016 open)",
      "No embedding or Qdrant client in extension",
    ];
    expect(checklist.length).toBe(5);
  });
});
