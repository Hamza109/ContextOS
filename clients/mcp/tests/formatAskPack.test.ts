import { afterEach, describe, expect, it, vi } from "vitest";
import { formatAskPack, postIndex } from "../src/contextClient.js";
import type { ContextResponse } from "../src/types.js";

function sample(overrides: Partial<ContextResponse> = {}): ContextResponse {
  return {
    final_context: "A".repeat(100),
    metrics: {
      tokens_before: 1000,
      tokens_after: 300,
      saving_percent: 70,
      trace: { duration_ms: 12 },
      latency_ms: 12,
    },
    blast_radius: {},
    memory: {},
    relevant_files: [{ path: "src/a.ts" }],
    is_real: true,
    ...overrides,
  };
}

describe("formatAskPack", () => {
  it("includes Confirmed metrics and relevant_files", () => {
    const text = formatAskPack(sample(), 50_000);
    expect(text).toContain("tokens_before=1000");
    expect(text).toContain("tokens_after=300");
    expect(text).toContain("src/a.ts");
    expect(text).toContain("AAAA");
  });

  it("truncates final_context by Proposed max_chars budget", () => {
    const text = formatAskPack(sample({ final_context: "B".repeat(500) }), 40);
    expect(text).toContain("truncated by contextos_ask max_chars");
    expect(text.length).toBeLessThan(500);
  });
});

describe("postIndex", () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    vi.restoreAllMocks();
    globalThis.fetch = originalFetch;
  });

  it("forwards only confirmed index fields and parses the response", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          files_indexed: 3,
          graph_nodes: 0,
          embeddings: 7,
          time_ms: 10,
        }),
        { status: 200 },
      ),
    );
    globalThis.fetch = fetchMock;

    await expect(
      postIndex("http://localhost:8000/", {
        repo_path: "/tmp/demo",
        repo_name: "demo",
      }),
    ).resolves.toEqual({
      files_indexed: 3,
      graph_nodes: 0,
      embeddings: 7,
      time_ms: 10,
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/index",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ repo_path: "/tmp/demo", repo_name: "demo" }),
      }),
    );
  });
});
