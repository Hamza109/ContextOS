/**
 * T060 / T064 — Pack Context → contextClient POST /context; no local pack/search/index.
 */
import { describe, expect, it, vi } from "vitest";
import { postContext } from "../src/api/contextClient";
import { runPackContext, buildContextRequest } from "../src/commands/packContext";
import {
  extractSafeEditSection,
  formatPackContextReport,
  SAFE_EDIT_BLOCK_MARKER,
} from "../src/providers/packContextPresenter";
import { createMockFetch } from "./helpers";
import { Position } from "./mocks/vscode";
import type { ExtensionConfig } from "../src/config";

const baseConfig: ExtensionConfig = {
  orchestratorBaseUrl: "http://orchestrator.test",
  autoIndexOnActivate: true,
  reindexOnSave: true,
  indexTimeoutMs: 60_000,
  enableGraphBlastPanel: true,
  showStalenessWarnings: true,
};

function makeEditor(selectionText: string) {
  const wordRange = {
    start: new Position(0, 0),
    end: new Position(0, selectionText.length),
  };
  return {
    document: {
      uri: { fsPath: "/repo/src/main.ts", scheme: "file" },
      getWordRangeAtPosition: () => wordRange,
      getText: (range?: unknown) => (range ? selectionText : selectionText),
    },
    selection: {
      active: new Position(0, 0),
      isEmpty: false,
    },
  };
}

function contextOkBody(final_context: string) {
  return {
    final_context,
    metrics: {
      tokens_before: 100,
      tokens_after: 40,
      saving_percent: 60,
      trace: { duration_ms: 12 },
    },
    blast_radius: {},
    memory: {},
    relevant_files: [],
    is_real: true,
  };
}

describe("pack_context_dx (T060/T063/T064/T066)", () => {
  it("contextClient POSTs Confirmed query/file/repo/top_k only", async () => {
    let url = "";
    let body: Record<string, unknown> = {};
    const fetchImpl = createMockFetch(async (u, init) => {
      url = u;
      body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      return new Response(JSON.stringify(contextOkBody("packed")), { status: 200 });
    });

    await postContext(
      "http://orchestrator.test",
      { query: "how does auth work", file: "src/main.ts", repo: "repo", top_k: 8 },
      { fetchImpl },
    );

    expect(url).toBe("http://orchestrator.test/context");
    expect(Object.keys(body).sort()).toEqual(["file", "query", "repo", "top_k"].sort());
    expect(body).not.toHaveProperty("content");
    expect(body).not.toHaveProperty("packed");
    expect(body).not.toHaveProperty("paths");
  });

  it("Pack Context command calls POST /context and presents final_context", async () => {
    const present = vi.fn();
    const fetchImpl = createMockFetch(async (_u, init) => {
      const body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      expect(body.query).toBe("auth flow");
      expect(body.repo).toBe("repo");
      expect(body.file).toBe("src/main.ts");
      expect(typeof body.top_k).toBe("number");
      const fc =
        "<!-- pack -->\n" +
        SAFE_EDIT_BLOCK_MARKER +
        "\nedit plan: touch callers (Proposed)\n";
      return new Response(JSON.stringify(contextOkBody(fc)), { status: 200 });
    });

    const response = await runPackContext({
      getConfig: () => baseConfig,
      getEditor: () => makeEditor("auth flow") as never,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
      presentReport: present,
      fetchImpl,
    });

    expect(response?.is_real).toBe(true);
    expect(present).toHaveBeenCalled();
    const report = present.mock.calls[0][0] as string;
    expect(report).toContain("POST /context");
    expect(extractSafeEditSection(response!.final_context)).toContain(SAFE_EDIT_BLOCK_MARKER);
    expect(formatPackContextReport(response!)).toContain("safe-edit section detected");
  });

  it("buildContextRequest uses selection-derived Confirmed fields only", () => {
    const snap = {
      path: "/repo/src/main.ts",
      relativePath: "src/main.ts",
      line: 1,
      column: 0,
      symbol: "auth",
      selectionText: "how does login work",
      repoName: "repo",
      repoPath: "/repo",
    };
    const req = buildContextRequest(snap);
    expect(req).toEqual({
      query: "how does login work",
      file: "src/main.ts",
      repo: "repo",
      top_k: 8,
    });
  });
});
