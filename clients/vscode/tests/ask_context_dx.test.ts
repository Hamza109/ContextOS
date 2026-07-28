/**
 * T035–T039 / T040–T046 — Ask ContextOS → contextClient POST /context; no local pack.
 *
 * T032 / T036 Proposed click-count fixture (OQ-Ask-DX / SC-003):
 *   Gesture sequence: Command Palette → "ContextOS: Ask ContextOS"
 *   Gesture count: 1–2 (<3 clicks). Palette command alone = 1–2 gestures.
 *   Optional keybinding (cmd/ctrl+shift+;) and editor/context menu are alternate Proposed paths.
 *   OQ-Ask-DX remains open until UX freeze — fixture is Proposed, not Confirmed.
 *
 * T039 / SC-004 / OQ-IDE-2s-Harness — BLOCKED placeholder:
 *   Client-side latency logging (ASK_LATENCY_LOG_PREFIX) is Proposed instrumentation only.
 *   MUST NOT invent Pass or Fail for SC-004 (<2s symbol-accurate IDE) without harness evidence.
 *   Status: blocked — no Pass/Fail asserted here.
 */
import { describe, expect, it, vi } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { postContext } from "../src/api/contextClient";
import {
  ASK_CONTEXT_COMMAND,
  ASK_ERROR_HTTP,
  ASK_ERROR_UNREACHABLE,
  ASK_LATENCY_LOG_PREFIX,
  buildAskContextRequest,
  runAskContext,
  DEFAULT_ASK_TOP_K,
} from "../src/commands/askContext";
import { PACK_CONTEXT_COMMAND } from "../src/commands/packContext";
import {
  formatAskContextReport,
  formatRelevantFiles,
} from "../src/providers/askContextPresenter";
import { createMockFetch } from "./helpers";
import { Position } from "./mocks/vscode";
import type { ExtensionConfig } from "../src/config";

const baseConfig: ExtensionConfig = {
  orchestratorBaseUrl: "http://orchestrator.test",
  autoIndexOnActivate: true,
  reindexOnSave: true,
  indexTimeoutMs: 60_000,
};

/**
 * Proposed SC-003 initiation fixture (T032 / T036).
 * Palette → Ask = 1–2 gestures; must be < 3.
 */
const ASK_INITIATION_GESTURES_PROPOSED = {
  sequence: "Command Palette → ContextOS: Ask ContextOS",
  minGestures: 1,
  maxGestures: 2,
  clickLimit: 3,
} as const;

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

function contextOkBody(final_context: string, relevant_files: unknown[] = []) {
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
    relevant_files,
    is_real: true,
  };
}

describe("ask_context_dx (T035/T036/T038/T040–T046)", () => {
  it("registers Proposed Ask command ID distinct from Pack Context (T033/T035)", () => {
    expect(ASK_CONTEXT_COMMAND).toBe("contextos.askContext");
    expect(ASK_CONTEXT_COMMAND).not.toBe(PACK_CONTEXT_COMMAND);
    expect(PACK_CONTEXT_COMMAND).toBe("contextos.packContext");
  });

  it("package.json contributes Ask title + <3-click paths (T043)", () => {
    const pkg = JSON.parse(
      fs.readFileSync(path.resolve(__dirname, "../package.json"), "utf8"),
    ) as {
      contributes: {
        commands: Array<{ command: string; title: string }>;
        keybindings?: Array<{ command: string }>;
        menus?: { "editor/context"?: Array<{ command: string }> };
      };
    };
    const ask = pkg.contributes.commands.find((c) => c.command === ASK_CONTEXT_COMMAND);
    expect(ask?.title).toBe("ContextOS: Ask ContextOS");
    expect(pkg.contributes.keybindings?.some((k) => k.command === ASK_CONTEXT_COMMAND)).toBe(
      true,
    );
    expect(
      pkg.contributes.menus?.["editor/context"]?.some((m) => m.command === ASK_CONTEXT_COMMAND),
    ).toBe(true);
  });

  it("Proposed click-count fixture: palette command alone = 1–2 gestures <3 (T032/T036)", () => {
    // Fixture documents OQ-Ask-DX Proposed initiation path — not a Confirmed UX freeze.
    expect(ASK_INITIATION_GESTURES_PROPOSED.maxGestures).toBeLessThan(
      ASK_INITIATION_GESTURES_PROPOSED.clickLimit,
    );
    expect(ASK_INITIATION_GESTURES_PROPOSED.minGestures).toBeGreaterThanOrEqual(1);
    expect(ASK_INITIATION_GESTURES_PROPOSED.maxGestures).toBeLessThanOrEqual(2);
    expect(ASK_INITIATION_GESTURES_PROPOSED.sequence).toContain("Command Palette");
  });

  it("buildAskContextRequest maps NL query to Confirmed ContextRequest fields only (T044)", () => {
    const req = buildAskContextRequest({
      query: "  how does auth work  ",
      repo: "repo",
      file: "src/main.ts",
    });
    expect(req).toEqual({
      query: "how does auth work",
      file: "src/main.ts",
      repo: "repo",
      top_k: DEFAULT_ASK_TOP_K,
    });
    expect(buildAskContextRequest({ query: "   ", repo: "repo" })).toBeUndefined();
    expect(buildAskContextRequest({ query: "q", repo: "" })).toBeUndefined();
  });

  it("Ask command calls postContext only and presents final_context + relevant_files (T035/T041)", async () => {
    const present = vi.fn();
    const logLatency = vi.fn();
    const showInput = vi.fn(async () => "how does login work");
    const fetchImpl = createMockFetch(async (_u, init) => {
      const body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      expect(body.query).toBe("how does login work");
      expect(body.repo).toBe("repo");
      expect(body.file).toBe("src/main.ts");
      expect(typeof body.top_k).toBe("number");
      expect(Object.keys(body).sort()).toEqual(["file", "query", "repo", "top_k"].sort());
      return new Response(
        JSON.stringify(
          contextOkBody("ask packed context", [{ path: "src/auth.ts" }, "src/login.ts"]),
        ),
        { status: 200 },
      );
    });

    const response = await runAskContext({
      getConfig: () => baseConfig,
      getEditor: () => makeEditor("selection default") as never,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInputBox: showInput,
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
      presentReport: present,
      logLatency,
      fetchImpl,
    });

    expect(showInput).toHaveBeenCalled();
    const inputOpts = showInput.mock.calls[0][0] as { value?: string };
    expect(inputOpts.value).toBe("selection default");

    expect(response?.is_real).toBe(true);
    expect(present).toHaveBeenCalled();
    const report = present.mock.calls[0][0] as string;
    expect(report).toContain("ContextOS Ask (via POST /context)");
    expect(report).toContain("ask packed context");
    expect(report).toContain("relevant_files");
    expect(report).toContain("src/auth.ts");
    expect(formatRelevantFiles([{ path: "a.ts" }])).toContain("a.ts");
    expect(formatAskContextReport(response!)).toContain("tokens_after");
    expect(logLatency).toHaveBeenCalled();
    expect(ASK_LATENCY_LOG_PREFIX).toBe("[ContextOS][obs][ask]");
  });

  it("Ask with queryOverride skips InputBox and still POSTs /context", async () => {
    const showInput = vi.fn();
    const fetchImpl = createMockFetch(async (_u, init) => {
      const body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      expect(body.query).toBe("override query");
      expect(body).not.toHaveProperty("file");
      return new Response(JSON.stringify(contextOkBody("ok")), { status: 200 });
    });

    await runAskContext({
      getConfig: () => baseConfig,
      getEditor: () => undefined,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInputBox: showInput,
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: vi.fn(),
      presentReport: vi.fn(),
      queryOverride: "override query",
      fetchImpl,
    });

    expect(showInput).not.toHaveBeenCalled();
  });

  it("surfaces visible failure when orchestrator unreachable (T038 / NFR-006)", async () => {
    const showError = vi.fn();
    const fetchImpl = createMockFetch(async () => {
      throw new TypeError("fetch failed");
    });

    const result = await runAskContext({
      getConfig: () => baseConfig,
      getEditor: () => undefined,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInputBox: async () => "q",
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: showError,
      presentReport: vi.fn(),
      fetchImpl,
    });

    expect(result).toBeUndefined();
    expect(showError).toHaveBeenCalledWith(ASK_ERROR_UNREACHABLE);
  });

  it("surfaces visible failure on non-2xx (T038 / NFR-006)", async () => {
    const showError = vi.fn();
    const fetchImpl = createMockFetch(async () => new Response("nope", { status: 503 }));

    await runAskContext({
      getConfig: () => baseConfig,
      getEditor: () => undefined,
      workspaceFolders: () => [{ uri: { fsPath: "/repo" }, name: "repo" }],
      showInputBox: async () => "q",
      showInformationMessage: vi.fn(),
      showWarningMessage: vi.fn(),
      showErrorMessage: showError,
      presentReport: vi.fn(),
      fetchImpl,
    });

    expect(showError).toHaveBeenCalled();
    const msg = showError.mock.calls[0][0] as string;
    expect(msg.startsWith(ASK_ERROR_HTTP)).toBe(true);
  });

  it("contextClient POSTs Confirmed fields only via Ask path", async () => {
    let url = "";
    let body: Record<string, unknown> = {};
    const fetchImpl = createMockFetch(async (u, init) => {
      url = u;
      body = JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
      return new Response(JSON.stringify(contextOkBody("x")), { status: 200 });
    });

    await postContext(
      "http://orchestrator.test",
      { query: "nl ask", file: "src/a.ts", repo: "repo", top_k: 8 },
      { fetchImpl },
    );

    expect(url).toBe("http://orchestrator.test/context");
    expect(Object.keys(body).sort()).toEqual(["file", "query", "repo", "top_k"].sort());
  });
});

/**
 * T039 — SC-004 / OQ-IDE-2s-Harness blocked placeholder.
 * Instrumentation hook exists (ASK_LATENCY_LOG_PREFIX / logLatency); harness evidence does not.
 * Do not assert Pass or Fail for SC-004 here.
 */
describe("ask_context SC-004 harness gate (T039)", () => {
  it("documents SC-004 measurement as blocked without inventing Pass/Fail", () => {
    const sc004Status = "blocked" as const; // OQ-IDE-2s-Harness — no harness evidence in this epic
    expect(sc004Status).toBe("blocked");
    expect(ASK_LATENCY_LOG_PREFIX).toMatch(/\[ContextOS\]\[obs\]\[ask\]/);
    // Explicitly: no latency threshold assertion — would invent SC-004 Pass/Fail.
  });
});
