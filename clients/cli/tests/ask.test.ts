/**
 * T019–T024 / T022 / T023 — CLI ask maps to Confirmed ContextRequest; thin-client boundary.
 */
import { describe, expect, it, vi } from "vitest";
import fs from "node:fs";
import path from "node:path";
import {
  buildAskRequest,
  formatAskError,
  runAsk,
  DEFAULT_TOP_K,
} from "../src/ask";
import { postContext, ContextClientError } from "../src/contextClient";
import { formatHumanAskReport } from "../src/humanRenderer";
import {
  formatMachineAskReport,
  PROPOSED_MACHINE_SCHEMA_NOTE,
} from "../src/machineRenderer";
import { parseArgv, helpText } from "../src/cli";

const SRC_ROOT = path.resolve(__dirname, "../src");

function createMockFetch(handler: (url: string, init?: RequestInit) => Promise<Response>) {
  return (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
    return handler(url, init);
  }) as typeof fetch;
}

function contextOkBody(overrides: Partial<{ final_context: string; relevant_files: unknown[] }> = {}) {
  return {
    final_context: overrides.final_context ?? "packed context about auth",
    metrics: {
      tokens_raw: 100,
      tokens_compacted: 40,
      reduction_pct: 60,
      latency_ms: 12,
    },
    blast_radius: [],
    memory: [],
    relevant_files: overrides.relevant_files ?? ["src/auth.ts", { path: "src/login.ts" }],
    is_real: true,
  };
}

describe("CLI ask request mapping (T019)", () => {
  it("buildAskRequest maps query/repo/file/top_k Confirmed fields only", () => {
    const req = buildAskRequest({
      query: "where is auth?",
      repo: "myrepo",
      file: "src/main.ts",
      topK: 5,
    });
    expect(req).toEqual({
      query: "where is auth?",
      repo: "myrepo",
      file: "src/main.ts",
      top_k: 5,
    });
    expect(Object.keys(req).sort()).toEqual(["file", "query", "repo", "top_k"].sort());
  });

  it("defaults top_k and omits empty file", () => {
    const req = buildAskRequest({ query: "q", repo: "r" });
    expect(req.top_k).toBe(DEFAULT_TOP_K);
    expect(req).not.toHaveProperty("file");
  });

  it("parseArgv ask → ContextRequest-shaped args", () => {
    const parsed = parseArgv([
      "ask",
      "where is X?",
      "--repo",
      "demo",
      "--file",
      "a.ts",
      "--top-k",
      "3",
    ]);
    expect(parsed.ask).toEqual({
      query: "where is X?",
      repo: "demo",
      file: "a.ts",
      topK: 3,
      baseUrl: undefined,
      json: false,
    });
  });
});

describe("CLI human renderer (T020 / SC-001)", () => {
  it("renders non-empty final_context and relevant files", () => {
    const text = formatHumanAskReport(contextOkBody() as never);
    expect(text).toContain("final_context");
    expect(text).toContain("packed context about auth");
    expect(text).toContain("relevant_files");
    expect(text).toContain("src/auth.ts");
    expect(text).toContain("src/login.ts");
  });
});

describe("CLI visible failure (T021 / NFR-006)", () => {
  it("surfaces network / non-2xx via stderr", async () => {
    const stderr = vi.fn();
    const fetchImpl = createMockFetch(async () => {
      throw new TypeError("fetch failed");
    });
    await expect(
      runAsk(
        { query: "q", repo: "r" },
        { fetchImpl, stderrWrite: stderr, stdoutWrite: vi.fn() },
      ),
    ).rejects.toBeInstanceOf(ContextClientError);
    expect(stderr.mock.calls[0][0]).toMatch(/ContextOS ask failed/);
  });

  it("formatAskError includes HTTP status message", () => {
    expect(formatAskError(new ContextClientError("POST /context failed: HTTP 503", 503))).toContain(
      "503",
    );
  });
});

describe("CLI thin-client boundary (T022 / SC-005)", () => {
  it("source tree has no local hybrid search / pack / symbol policy", () => {
    const files = fs
      .readdirSync(SRC_ROOT)
      .filter((f) => f.endsWith(".ts"))
      .map((f) => path.join(SRC_ROOT, f));
    const forbidden = [
      /hybrid_search|l5_search|embedAndSearch/i,
      /pack_repository|l5_pack|Repomix|phase.?pack/i,
      /SymbolService|l3_symbol|buildSymbolGraph/i,
      /ignore_policy|ConsentGate/i,
    ];
    const violations: string[] = [];
    for (const file of files) {
      const text = fs.readFileSync(file, "utf8");
      for (const re of forbidden) {
        if (re.test(text)) {
          violations.push(`${path.basename(file)}: ${re}`);
        }
      }
    }
    expect(violations).toEqual([]);
  });

  it("postContext POSTs Confirmed fields only", async () => {
    let body: Record<string, unknown> = {};
    const fetchImpl = createMockFetch(async (_u, init) => {
      body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      return new Response(JSON.stringify(contextOkBody()), { status: 200 });
    });
    await postContext(
      "http://orchestrator.test",
      { query: "q", repo: "r", top_k: 8, file: "f.ts" },
      { fetchImpl },
    );
    expect(Object.keys(body).sort()).toEqual(["file", "query", "repo", "top_k"].sort());
  });
});

describe("CLI Proposed --json (T023 / OQ-10)", () => {
  it("wires --json without Confirmed schema freeze", () => {
    const parsed = parseArgv(["ask", "q", "--repo", "r", "--json"]);
    expect(parsed.ask?.json).toBe(true);
    const out = formatMachineAskReport(contextOkBody() as never);
    expect(out).toContain(PROPOSED_MACHINE_SCHEMA_NOTE);
    expect(helpText()).toMatch(/OQ-10|Proposed/);
  });
});

describe("CLI acceptance smoke (T024 / SC-001)", () => {
  it("ask 'where is X?' yields human grounded output against mocked POST /context", async () => {
    const stdout: string[] = [];
    const fetchImpl = createMockFetch(async (url, init) => {
      expect(url).toBe("http://orchestrator.test/context");
      const body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      expect(body.query).toBe("where is X?");
      return new Response(
        JSON.stringify(contextOkBody({ final_context: "X lives in src/x.ts" })),
        { status: 200 },
      );
    });
    await runAsk(
      { query: "where is X?", repo: "demo", baseUrl: "http://orchestrator.test" },
      {
        fetchImpl,
        stdoutWrite: (s) => {
          stdout.push(s);
        },
        stderrWrite: vi.fn(),
      },
    );
    const text = stdout.join("");
    expect(text).toContain("X lives in src/x.ts");
    expect(text).toContain("final_context");
  });

  it("rejects unknown verbs (FR-005)", () => {
    const parsed = parseArgv(["index"]);
    expect(parsed.error).toMatch(/ask/i);
  });
});
