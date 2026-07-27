/**
 * T049 / FR-015: client-side cancellation aborts in-flight POST /index.
 * OQ-CANCEL: server-side cancel not asserted — client AbortSignal only.
 */
import { describe, expect, it, vi } from "vitest";
import { postIndex } from "../src/api/indexClient";
import { triggerAutoIndex } from "../src/indexing/autoIndex";
import type { ExtensionConfig } from "../src/config";
import { createMockFetch, createTestProgressHost } from "./helpers";

const baseConfig: ExtensionConfig = {
  orchestratorBaseUrl: "http://orchestrator.test",
  autoIndexOnActivate: true,
  reindexOnSave: true,
  indexTimeoutMs: 60_000,
};

describe("index_cancellation (T049)", () => {
  it("aborts fetch when AbortSignal is aborted (client cancel only)", async () => {
    const controller = new AbortController();
    let sawAbort = false;

    const fetchImpl = createMockFetch(async (_url, init) => {
      return await new Promise<Response>((_resolve, reject) => {
        const signal = init?.signal;
        if (!signal) {
          reject(new Error("expected signal"));
          return;
        }
        if (signal.aborted) {
          sawAbort = true;
          reject(Object.assign(new Error("aborted"), { name: "AbortError" }));
          return;
        }
        signal.addEventListener("abort", () => {
          sawAbort = true;
          reject(Object.assign(new Error("aborted"), { name: "AbortError" }));
        });
      });
    });

    const pending = postIndex(
      "http://orchestrator.test",
      { repo_path: "/r", repo_name: "r" },
      { signal: controller.signal, fetchImpl },
    );

    controller.abort();

    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
    expect(sawAbort).toBe(true);
  });

  it("progress cancel aborts auto-index without claiming server cancel", async () => {
    const fetchImpl = createMockFetch(async (_url, init) => {
      return await new Promise<Response>((_resolve, reject) => {
        const signal = init?.signal;
        signal?.addEventListener("abort", () => {
          reject(Object.assign(new Error("aborted"), { name: "AbortError" }));
        });
      });
    });

    const warn = vi.fn();
    const result = await triggerAutoIndex({
      config: baseConfig,
      workspaceFolders: [{ uri: { fsPath: "/tmp/r" }, name: "r" }],
      progressHost: createTestProgressHost({ cancelAfterMs: 5 }),
      showInformationMessage: vi.fn(),
      showWarningMessage: warn,
      showErrorMessage: vi.fn(),
      fetchImpl,
    });

    expect(result.cancelled).toBe(true);
    expect(warn).toHaveBeenCalledWith("ContextOS: indexing cancelled.");
  });
});
