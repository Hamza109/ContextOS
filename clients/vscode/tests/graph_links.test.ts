/**
 * Proposed graph/blast URL discoverability helpers for Ask DX.
 */
import { describe, expect, it } from "vitest";
import {
  buildBlastApiUrl,
  buildGraphHtmlUrl,
  extractPathHint,
  formatGraphDiscoverySection,
} from "../src/providers/graphLinks";
import { formatAskContextReport } from "../src/providers/askContextPresenter";
import type { ContextResponse } from "../src/api/types";

describe("graphLinks", () => {
  it("builds graph.html and blast URLs with file seed", () => {
    expect(
      buildGraphHtmlUrl(
        "http://127.0.0.1:8000",
        "ux-validator",
        "apps/api/src/app.module.ts",
        3,
      ),
    ).toBe(
      "http://127.0.0.1:8000/graph.html?repo=ux-validator&depth=3&file=apps%2Fapi%2Fsrc%2Fapp.module.ts",
    );
    expect(
      buildBlastApiUrl(
        "http://127.0.0.1:8000/",
        "apps/api/src/app.module.ts",
        "ux-validator",
      ),
    ).toBe(
      "http://127.0.0.1:8000/blast/apps/api/src/app.module.ts?repo=ux-validator",
    );
  });

  it("extracts path hints from blast-style queries", () => {
    expect(
      extractPathHint("Blast radius of apps/api/src/app.module.ts"),
    ).toBe("apps/api/src/app.module.ts");
  });

  it("formats discovery section for Ask reports", () => {
    const text = formatGraphDiscoverySection({
      baseUrl: "http://127.0.0.1:8000",
      repo: "demo",
      query: "what breaks in src/a.ts",
    });
    expect(text).toContain("--- open graphs ---");
    expect(text).toContain("graph.html?repo=demo");
    expect(text).toContain("file=src%2Fa.ts");
    expect(text).toContain("Show Blast Graph");
  });
});

describe("formatAskContextReport graph discovery", () => {
  it("includes blast_radius JSON and graph links", () => {
    const response: ContextResponse = {
      final_context: "pack",
      metrics: {
        tokens_before: 10,
        tokens_after: 5,
        saving_percent: 50,
        latency_ms: 1,
        trace: {},
      },
      blast_radius: {
        direct_dependents: ["main.ts"],
        transitive: [],
        risk: "MEDIUM",
      },
      memory: {},
      relevant_files: [],
      is_real: true,
    };
    const text = formatAskContextReport(response, {
      orchestratorBaseUrl: "http://127.0.0.1:8000",
      repo: "ux-validator",
      file: "apps/api/src/app.module.ts",
    });
    expect(text).toContain("--- blast_radius");
    expect(text).toContain("main.ts");
    expect(text).toContain("L1 IMPORTS graph (browser):");
    expect(text).toContain("Blast API (JSON):");
  });
});
