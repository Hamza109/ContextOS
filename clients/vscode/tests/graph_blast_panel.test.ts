/**
 * T029 — Panel interaction with mocked FastAPI blast payloads (EP-007 US-020).
 * React Flow model is derived from API lists only — no fabricated dependents.
 */
import { describe, expect, it, beforeEach } from "vitest";
import { blastResponseToGraphModel } from "../src/providers/blastGraphModel";
import {
  loadBlastIntoPanel,
  setActiveGraphBlastPanelForTests,
  buildWebviewHtml,
  createNonce,
  type GraphBlastPanelDeps,
} from "../src/providers/graphBlastPanel";
import { FreshnessSession } from "../src/providers/stalenessPresenter";
import { defaultTestConfig } from "../src/config";
import { createMockFetch } from "./helpers";
import { Uri, window } from "./mocks/vscode";

function blastBody(overrides: Record<string, unknown> = {}) {
  return {
    direct_dependents: ["src/b.ts"],
    transitive: ["src/c.ts"],
    db_tables: [],
    risk: "MEDIUM",
    tests_to_run: ["tests/test_a.py"],
    owners: [],
    index_revision: "rev-a",
    ...overrides,
  };
}

describe("graph blast panel (T029)", () => {
  beforeEach(() => {
    setActiveGraphBlastPanelForTests(undefined);
  });

  it("maps FastAPI blast lists to React Flow nodes/edges without fabricating neighbors", () => {
    const model = blastResponseToGraphModel("src/a.ts", {
      direct_dependents: ["src/b.ts"],
      transitive: ["src/c.ts"],
      db_tables: [],
      risk: "LOW",
      tests_to_run: [],
    });
    expect(model.nodes.map((n) => n.id).sort()).toEqual([
      "src/a.ts",
      "src/b.ts",
      "src/c.ts",
    ]);
    expect(model.nodes.find((n) => n.id === "src/a.ts")?.kind).toBe("target");
    expect(model.edges).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ source: "src/b.ts", target: "src/a.ts" }),
        expect.objectContaining({ source: "src/c.ts", target: "src/a.ts" }),
      ]),
    );
  });

  it("empty blast yields target-only model — no invented dependents", () => {
    const model = blastResponseToGraphModel("alone.ts", {
      direct_dependents: [],
      transitive: [],
      db_tables: [],
      risk: "LOW",
      tests_to_run: [],
    });
    expect(model.nodes).toEqual([
      { id: "alone.ts", label: "alone.ts", kind: "target" },
    ]);
    expect(model.edges).toEqual([]);
  });

  it("posts sanitized blastGraph from mocked GET /blast and handles errors", async () => {
    const panel = window.createWebviewPanel("t", "t", 1, {});
    setActiveGraphBlastPanelForTests(panel as never);
    const messages: unknown[] = [];
    panel.webview.postMessage = async (msg: unknown) => {
      messages.push(msg);
      return true;
    };

    const deps: GraphBlastPanelDeps = {
      extensionUri: Uri.file("/ext"),
      getConfig: () => defaultTestConfig(),
      getEditor: () => undefined,
      workspaceFolders: () => undefined,
      resolveRepo: () => ({ repo_name: "repo", repo_path: "/repo" }),
      relativePathFor: () => "src/a.ts",
      showWarningMessage: () => undefined,
      showErrorMessage: () => undefined,
      freshnessSession: new FreshnessSession(),
      fetchImpl: createMockFetch(async () =>
        new Response(JSON.stringify(blastBody()), { status: 200 }),
      ),
    };

    const result = await loadBlastIntoPanel(deps, "src/a.ts", "repo");
    expect(result.blast?.risk).toBe("MEDIUM");
    const graphMsg = messages.find(
      (m) => m && typeof m === "object" && (m as { type: string }).type === "blastGraph",
    ) as { nodes: unknown[]; edges: unknown[]; fileName: string } | undefined;
    expect(graphMsg?.fileName).toBe("src/a.ts");
    expect(graphMsg?.nodes.length).toBe(3);
    expect(graphMsg?.edges.length).toBe(2);

    messages.length = 0;
    deps.fetchImpl = createMockFetch(async () => new Response("nope", { status: 503 }));
    await loadBlastIntoPanel(deps, "src/a.ts", "repo");
    expect(
      messages.some(
        (m) => m && typeof m === "object" && (m as { type: string }).type === "error",
      ),
    ).toBe(true);
  });

  it("empty API dependents surfaces empty state without fabricating edges", async () => {
    const panel = window.createWebviewPanel("t", "t", 1, {});
    setActiveGraphBlastPanelForTests(panel as never);
    const messages: unknown[] = [];
    panel.webview.postMessage = async (msg: unknown) => {
      messages.push(msg);
      return true;
    };

    const deps: GraphBlastPanelDeps = {
      extensionUri: Uri.file("/ext"),
      getConfig: () => defaultTestConfig(),
      getEditor: () => undefined,
      workspaceFolders: () => undefined,
      resolveRepo: () => ({ repo_name: "repo", repo_path: "/repo" }),
      relativePathFor: () => "alone.ts",
      showWarningMessage: () => undefined,
      showErrorMessage: () => undefined,
      freshnessSession: new FreshnessSession(),
      fetchImpl: createMockFetch(async () =>
        new Response(
          JSON.stringify(blastBody({ direct_dependents: [], transitive: [] })),
          { status: 200 },
        ),
      ),
    };

    await loadBlastIntoPanel(deps, "alone.ts", "repo");
    expect(
      messages.some(
        (m) => m && typeof m === "object" && (m as { type: string }).type === "empty",
      ),
    ).toBe(true);
    const graphMsg = messages.find(
      (m) => m && typeof m === "object" && (m as { type: string }).type === "blastGraph",
    ) as { edges: unknown[] } | undefined;
    expect(graphMsg?.edges).toEqual([]);
  });

  it("webview HTML uses CSP nonce and does not embed graph.html", () => {
    const panel = window.createWebviewPanel("t", "t", 1, {});
    const html = buildWebviewHtml(panel.webview as never, Uri.file("/ext") as never, createNonce());
    expect(html).toMatch(/Content-Security-Policy/);
    expect(html).toMatch(/nonce-/);
    expect(html).toMatch(/NEEDS CLARIFICATION/);
    expect(html).not.toMatch(/src=["'].*graph\.html/);
  });
});
