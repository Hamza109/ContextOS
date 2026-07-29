/**
 * ContextOS MCP server (Proposed agent wiring).
 * Tools are thin clients of Confirmed FastAPI endpoints — no local pack/search/ignore.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  ContextClientError,
  formatAskPack,
  getHealth,
  postContext,
  postIndex,
} from "./contextClient.js";

export const DEFAULT_BASE_URL = "http://127.0.0.1:8000";
export const DEFAULT_TOP_K = 8;
/** Proposed client-side char budget — not a Confirmed API field */
export const DEFAULT_MAX_CHARS = 12000;

export function resolveBaseUrl(env: NodeJS.ProcessEnv = process.env): string {
  const raw =
    env.CONTEXTOS_ORCHESTRATOR_BASE_URL?.trim() ||
    env.CONTEXTOS_BASE_URL?.trim() ||
    DEFAULT_BASE_URL;
  return raw.replace(/\/+$/, "");
}

export function createContextOsMcpServer(options?: {
  baseUrl?: string;
  fetchImpl?: typeof fetch;
}): McpServer {
  const baseUrl = options?.baseUrl ?? resolveBaseUrl();
  // fetchImpl reserved for tests — inject via global in unit tests
  void options?.fetchImpl;

  const server = new McpServer({
    name: "contextos",
    version: "0.1.0",
  });

  server.tool(
    "contextos_health",
    "Check ContextOS orchestrator health (GET /). Use before ask if unsure the API is up.",
    {},
    async () => {
      try {
        const health = await getHealth(baseUrl);
        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({ baseUrl, health }, null, 2),
            },
          ],
        };
      } catch (err) {
        const msg = err instanceof ContextClientError ? err.message : String(err);
        return {
          isError: true,
          content: [{ type: "text" as const, text: `contextos_health failed: ${msg}` }],
        };
      }
    },
  );

  server.tool(
    "contextos_index",
    "Index a local repository via Confirmed POST /index. Call before contextos_ask when the repo is not indexed. The orchestrator must be able to read repo_path.",
    {
      repo_path: z
        .string()
        .min(1)
        .describe("Confirmed local path to the repository that the orchestrator can read"),
      repo_name: z
        .string()
        .min(1)
        .describe("Confirmed logical name used later as contextos_ask repo"),
    },
    async ({ repo_path, repo_name }) => {
      try {
        const result = await postIndex(baseUrl, { repo_path, repo_name });
        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify(
                {
                  repo_name,
                  repo_path,
                  ...result,
                  next: "Use contextos_ask with this repo_name.",
                },
                null,
                2,
              ),
            },
          ],
        };
      } catch (err) {
        const msg = err instanceof ContextClientError ? err.message : String(err);
        return {
          isError: true,
          content: [
            {
              type: "text" as const,
              text:
                `contextos_index failed: ${msg}\n` +
                "Hint: run the orchestrator on the host for arbitrary local paths, or mount the repo path into Docker.",
            },
          ],
        };
      }
    },
  );

  server.tool(
    "contextos_ask",
    "Budgeted ContextOS retrieve+pack via Confirmed POST /context. Prefer this before dumping many source files. Requires the repo to be indexed (POST /index). Returns compressed final_context, relevant_files, L1 blast_radius when present, and openable /graph.html + /blast links.",
    {
      query: z.string().min(1).describe("Natural-language question about the indexed repo"),
      repo: z
        .string()
        .min(1)
        .describe("Logical repo name (usually the workspace folder name used at index time)"),
      top_k: z
        .number()
        .int()
        .positive()
        .optional()
        .describe(`Confirmed top_k (default ${DEFAULT_TOP_K}). Keep small for token savings.`),
      file: z
        .string()
        .optional()
        .describe("Optional Confirmed file bias (workspace-relative path)"),
      max_chars: z
        .number()
        .int()
        .positive()
        .optional()
        .describe(
          `Proposed client truncate of final_context (default ${DEFAULT_MAX_CHARS}). Not a Confirmed API field.`,
        ),
    },
    async ({ query, repo, top_k, file, max_chars }) => {
      try {
        const response = await postContext(baseUrl, {
          query,
          repo,
          top_k: top_k ?? DEFAULT_TOP_K,
          file: file ?? null,
        });
        const text = formatAskPack(response, max_chars ?? DEFAULT_MAX_CHARS, {
          baseUrl,
          repo,
          file: file ?? null,
          query,
        });
        return {
          content: [{ type: "text" as const, text }],
        };
      } catch (err) {
        const msg = err instanceof ContextClientError ? err.message : String(err);
        return {
          isError: true,
          content: [
            {
              type: "text" as const,
              text:
                `contextos_ask failed: ${msg}\n` +
                `Hint: ensure orchestrator at ${baseUrl} is up and repo '${repo}' is indexed (POST /index).`,
            },
          ],
        };
      }
    },
  );

  return server;
}
