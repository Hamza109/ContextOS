/**
 * T057: optional observational timing for ~200-file auto-index ~10s illustrative target.
 * Hardware-gated — not a hard SLA. Skips unless CONTEXTOS_OBS_TIMING=1.
 */
import { describe, expect, it, vi } from "vitest";
import { triggerAutoIndex } from "../src/indexing/autoIndex";
import type { ExtensionConfig } from "../src/config";
import { createMockFetch, createTestProgressHost } from "./helpers";

const enabled = process.env.CONTEXTOS_OBS_TIMING === "1";

describe("observational_auto_index_timing (T057)", () => {
  it.runIf(enabled)(
    "records wall-clock timing when CONTEXTOS_OBS_TIMING=1 (illustrative, not SLA)",
    async () => {
      const fetchImpl = createMockFetch(async () => {
        await new Promise((r) => setTimeout(r, 20));
        return new Response(
          JSON.stringify({
            files_indexed: 200,
            graph_nodes: 0,
            embeddings: 400,
            time_ms: 20,
          }),
          { status: 200 },
        );
      });

      const timings: number[] = [];
      const result = await triggerAutoIndex({
        config: {
          orchestratorBaseUrl: "http://orchestrator.test",
          autoIndexOnActivate: true,
          reindexOnSave: true,
          indexTimeoutMs: 60_000,
        } satisfies ExtensionConfig,
        workspaceFolders: [{ uri: { fsPath: "/tmp/big" }, name: "big" }],
        progressHost: createTestProgressHost(),
        showInformationMessage: vi.fn(),
        showWarningMessage: vi.fn(),
        showErrorMessage: vi.fn(),
        fetchImpl,
        logTiming: (ms) => timings.push(ms),
      });

      expect(result.skipped).toBe(false);
      expect(timings[0]).toBeGreaterThanOrEqual(20);
      // Illustrative NFR-004 / SC-008 ~10s for ~200 files — observational only.
      // Do not fail CI on wall clock; log for humans when hardware-gated run is used.
      console.log(
        `[T057 obs] wall_ms=${timings[0]} illustrative_target_ms=10000 (not enforced)`,
      );
    },
  );

  it("documents that timing is observational / hardware-gated when env unset", () => {
    if (enabled) {
      expect(true).toBe(true);
      return;
    }
    expect(process.env.CONTEXTOS_OBS_TIMING ?? "").not.toBe("1");
  });
});
