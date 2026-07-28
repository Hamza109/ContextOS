#!/usr/bin/env node
/**
 * Stdio MCP entrypoint for Cursor / MCP hosts.
 */

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createContextOsMcpServer, resolveBaseUrl } from "./server.js";

async function main(): Promise<void> {
  const baseUrl = resolveBaseUrl();
  const server = createContextOsMcpServer({ baseUrl });
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("contextos-mcp failed:", err);
  process.exit(1);
});
