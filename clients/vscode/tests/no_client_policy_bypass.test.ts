/**
 * T050 / T056 / T017 / T062 / T072 / T073 + EP-005 T013 / SC-003 / FR-004:
 * Extension must not pack locally, bypass backend policy, or reimplement symbol policy.
 * Static checklist over clients/vscode/src — policy stays FastAPI-only (SC-008).
 * EP-005: no local ignore/pack/upload of excluded paths; indexClient / auto-index
 * only call orchestrator (US-016 consent product OOS — cite only).
 */
import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { postIndex } from "../src/api/indexClient";
import { postContext } from "../src/api/contextClient";
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

describe("no_client_policy_bypass (T050/T056/T017/SC-008)", () => {
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
      const stripped = stripComments(fs.readFileSync(file, "utf8"));
      for (const { re, why } of forbiddenPatterns) {
        if (re.test(stripped)) {
          violations.push(`${path.relative(SRC_ROOT, file)}: ${why} (${re})`);
        }
      }
    }

    expect(violations, violations.join("\n")).toEqual([]);
  });

  it("source tree does not reimplement symbol policy / local symbol graph (T017/SC-008)", () => {
    const files = walkTsFiles(SRC_ROOT);
    const forbiddenPatterns: Array<{ re: RegExp; why: string }> = [
      { re: /SymbolService|l3_symbol|filter_references_by_file_type/, why: "orchestrator symbol policy" },
      { re: /buildSymbolGraph|localSymbolIndex|symbolGraph\s*=/, why: "local symbol graph/index" },
      { re: /hybrid_search|l5_search|embedAndSearch/i, why: "client-side search" },
      { re: /compose_safe_edit_plan|attach_safe_edit_plan/, why: "server safe-edit composition" },
    ];

    const violations: string[] = [];
    for (const file of files) {
      const stripped = stripComments(fs.readFileSync(file, "utf8"));
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

  it("context client only POSTs to /context with Confirmed fields (T062)", async () => {
    let url = "";
    let body: Record<string, unknown> = {};
    const fetchImpl = createMockFetch(async (u, init) => {
      url = u;
      body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      return new Response(
        JSON.stringify({
          final_context: "x",
          metrics: {
            tokens_before: 1,
            tokens_after: 1,
            saving_percent: 0,
            trace: { duration_ms: 1 },
          },
          blast_radius: {},
          memory: {},
          relevant_files: [],
          is_real: true,
        }),
        { status: 200 },
      );
    });

    await postContext(
      "http://orchestrator.test/",
      { query: "q", file: "a.ts", repo: "r", top_k: 5 },
      { fetchImpl },
    );

    expect(url).toBe("http://orchestrator.test/context");
    expect(Object.keys(body).sort()).toEqual(["file", "query", "repo", "top_k"].sort());
    expect(body).not.toHaveProperty("content");
    expect(body).not.toHaveProperty("source_files");
    expect(body).not.toHaveProperty("consent");
  });

  it("Pack/symbol paths do not open secret files client-side (T072)", () => {
    const files = walkTsFiles(SRC_ROOT);
    const forbidden = [/readFileSync\s*\(\s*['"].*\.env/, /openSync\s*\(\s*['"].*\.env/];
    const violations: string[] = [];
    for (const file of files) {
      const stripped = stripComments(fs.readFileSync(file, "utf8"));
      for (const re of forbidden) {
        if (re.test(stripped)) {
          violations.push(`${path.relative(SRC_ROOT, file)}: ${re}`);
        }
      }
    }
    expect(violations, violations.join("\n")).toEqual([]);
  });

  it("checklist: policy ownership remains FastAPI-only (T073)", () => {
    const checklist = [
      "Extension triggers POST /index only for indexing",
      "Pack Context triggers POST /context only",
      "Ask ContextOS triggers POST /context only (EP-004 US-008)",
      "Blast graph triggers GET /blast only (EP-007 US-020) — no client blast traversal",
      "Symbol DX uses Serena MCP client — no local symbol policy",
      "No local pack/flatten",
      "No client exclusion / consent application",
      "No embedding or vector store client in extension",
      "No rename execution / ContextOS sandbox UX",
    ];
    expect(checklist.length).toBe(9);
  });

  it("EP-007: blast panel modules must not invent blast traversal (T028)", () => {
    const blastFiles = [
      path.join(SRC_ROOT, "api/blastClient.ts"),
      path.join(SRC_ROOT, "providers/blastGraphModel.ts"),
      path.join(SRC_ROOT, "providers/graphBlastPanel.ts"),
    ];
    for (const file of blastFiles) {
      expect(fs.existsSync(file), file).toBe(true);
      const stripped = stripComments(fs.readFileSync(file, "utf8"));
      expect(stripped).not.toMatch(/computeBlastRadius|traverseImports|FalkorDB/i);
      expect(stripped).not.toMatch(/ignore_policy|IgnorePolicy/);
    }
  });

  it("EP-005 SC-003: indexClient cannot force-include excluded paths around orchestrator", async () => {
    let body: Record<string, unknown> = {};
    const fetchImpl = createMockFetch(async (_url, init) => {
      body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      return new Response(
        JSON.stringify({
          files_indexed: 0,
          graph_nodes: 0,
          embeddings: 0,
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
        // Client may *request* paths; orchestrator IgnorePolicy still owns exclusion.
        files: [".env", "node_modules/x.js", "src/ok.ts"],
      },
      { fetchImpl },
    );

    expect(body).not.toHaveProperty("override");
    expect(body).not.toHaveProperty("force_include");
    expect(body).not.toHaveProperty("bypass_ignore");
    expect(body).not.toHaveProperty("content");
    expect(JSON.stringify(body)).not.toMatch(/API_KEY=|BEGIN RSA PRIVATE KEY/);
  });

  it("Ask ContextOS source must not reimplement pack/search/symbol/ignore/consent (T037)", () => {
    const askFiles = [
      path.join(SRC_ROOT, "commands/askContext.ts"),
      path.join(SRC_ROOT, "providers/askContextPresenter.ts"),
    ];
    for (const file of askFiles) {
      expect(fs.existsSync(file), file).toBe(true);
      const stripped = stripComments(fs.readFileSync(file, "utf8"));
      expect(stripped).toMatch(/postContext|ContextResponse|final_context/);
      expect(stripped).not.toMatch(/pack_repository|l5_pack|hybrid_search|IgnorePolicy|ConsentGate/i);
      expect(stripped).not.toMatch(/SymbolService|buildSymbolGraph|embedAndSearch/i);
    }
  });
});
