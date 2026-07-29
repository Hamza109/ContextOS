/**
 * T048 / SC-007: activation triggers POST /index (mock server).
 */
import { describe, expect, it, vi } from "vitest";
import { triggerAutoIndex } from "../src/indexing/autoIndex";
import type { ExtensionConfig } from "../src/config";
import { createMockFetch, createTestProgressHost } from "./helpers";

const baseConfig: ExtensionConfig = {
  orchestratorBaseUrl: "http://127.0.0.1:9",
  autoIndexOnActivate: true,
  reindexOnSave: true,
  indexTimeoutMs: 60_000,
  enableGraphBlastPanel: true,
  showStalenessWarnings: true,
};

describe("activation_auto_index (T048)", () => {
  it("POSTs Confirmed {repo_path, repo_name} to /index on activation", async () => {
    let capturedUrl = "";
    let capturedBody: unknown;

    const fetchImpl = createMockFetch(async (url, init) => {
      capturedUrl = url;
      capturedBody = JSON.parse(String(init?.body ?? "{}"));
      return new Response(
        JSON.stringify({
          files_indexed: 3,
          graph_nodes: 0,
          embeddings: 9,
          time_ms: 42,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      );
    });

    const info = vi.fn();
    const result = await triggerAutoIndex({
      config: { ...baseConfig, orchestratorBaseUrl: "http://orchestrator.test" },
      workspaceFolders: [{ uri: { fsPath: "/tmp/demo-repo" }, name: "demo-repo" }],
      progressHost: createTestProgressHost(),
      showInformationMessage: info,
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
      fetchImpl,
    });

    expect(result.skipped).toBe(false);
    expect(result.response?.files_indexed).toBe(3);
    expect(capturedUrl).toBe("http://orchestrator.test/index");
    expect(capturedBody).toEqual({
      repo_path: "/tmp/demo-repo",
      repo_name: "demo-repo",
    });
    // Full auto-index must not invent Proposed scope fields
    expect(capturedBody).not.toHaveProperty("files");
    expect(capturedBody).not.toHaveProperty("paths");
    expect(info).toHaveBeenCalled();
  });

  it("skips when autoIndexOnActivate is false", async () => {
    const fetchImpl = vi.fn();
    const result = await triggerAutoIndex({
      config: { ...baseConfig, autoIndexOnActivate: false },
      workspaceFolders: [{ uri: { fsPath: "/tmp/x" }, name: "x" }],
      progressHost: createTestProgressHost(),
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.skipped).toBe(true);
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("skips when no workspace folder", async () => {
    const warn = vi.fn();
    const result = await triggerAutoIndex({
      config: baseConfig,
      workspaceFolders: undefined,
      progressHost: createTestProgressHost(),
      showInformationMessage: vi.fn(),
      showWarningMessage: warn,
      showErrorMessage: vi.fn(),
    });
    expect(result.skipped).toBe(true);
    expect(warn).toHaveBeenCalled();
  });
});
