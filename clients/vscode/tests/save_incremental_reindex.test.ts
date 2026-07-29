/**
 * T060 / FR-016: file save triggers incremental re-index via Proposed POST /index reuse.
 * OQ-14: files[] is Proposed — not Confirmed freeze.
 */
import { describe, expect, it, vi } from "vitest";
import { triggerSaveReindex } from "../src/indexing/onSaveReindex";
import type { ExtensionConfig } from "../src/config";
import { createMockFetch, createTestProgressHost } from "./helpers";

const baseConfig: ExtensionConfig = {
  orchestratorBaseUrl: "http://orchestrator.test",
  autoIndexOnActivate: true,
  reindexOnSave: true,
  indexTimeoutMs: 60_000,
  enableGraphBlastPanel: true,
  showStalenessWarnings: true,
};

describe("save_incremental_reindex (T060)", () => {
  it("on save POSTs Confirmed fields + Proposed files scope", async () => {
    let captured: unknown;
    const fetchImpl = createMockFetch(async (_url, init) => {
      captured = JSON.parse(String(init?.body ?? "{}"));
      return new Response(
        JSON.stringify({
          files_indexed: 1,
          graph_nodes: 0,
          embeddings: 2,
          time_ms: 15,
        }),
        { status: 200 },
      );
    });

    const result = await triggerSaveReindex(
      { uri: { fsPath: "/tmp/demo-repo/src/foo.ts", scheme: "file" } },
      {
        config: baseConfig,
        workspaceFolders: [{ uri: { fsPath: "/tmp/demo-repo" }, name: "demo-repo" }],
        progressHost: createTestProgressHost(),
        showWarningMessage: vi.fn(),
        showErrorMessage: vi.fn(),
        fetchImpl,
      },
    );

    expect(result.skipped).toBe(false);
    expect(result.proposedFiles).toEqual(["src/foo.ts"]);
    expect(captured).toEqual({
      repo_path: "/tmp/demo-repo",
      repo_name: "demo-repo",
      // Proposed (OQ-14) — not Confirmed
      files: ["src/foo.ts"],
    });
  });

  it("skips when reindexOnSave disabled", async () => {
    const fetchImpl = vi.fn();
    const result = await triggerSaveReindex(
      { uri: { fsPath: "/tmp/demo-repo/a.ts", scheme: "file" } },
      {
        config: { ...baseConfig, reindexOnSave: false },
        workspaceFolders: [{ uri: { fsPath: "/tmp/demo-repo" }, name: "demo-repo" }],
        progressHost: createTestProgressHost(),
        showWarningMessage: vi.fn(),
        showErrorMessage: vi.fn(),
        fetchImpl: fetchImpl as unknown as typeof fetch,
      },
    );
    expect(result.skipped).toBe(true);
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("does not invent a new endpoint — only /index", async () => {
    let url = "";
    const fetchImpl = createMockFetch(async (u, init) => {
      url = u;
      void init;
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

    await triggerSaveReindex(
      { uri: { fsPath: "/ws/a.ts", scheme: "file" } },
      {
        config: baseConfig,
        workspaceFolders: [{ uri: { fsPath: "/ws" }, name: "ws" }],
        progressHost: createTestProgressHost(),
        showWarningMessage: vi.fn(),
        showErrorMessage: vi.fn(),
        fetchImpl,
      },
    );

    expect(url).toBe("http://orchestrator.test/index");
    expect(url).not.toMatch(/\/delta|\/reindex|\/incremental/);
  });
});
