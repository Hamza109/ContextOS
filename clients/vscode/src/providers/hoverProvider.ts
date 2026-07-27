/**
 * Hover provider — presents Serena-backed hover/definition docs (T032; FR-014).
 * DX only: no local symbol graph or policy.
 */

import * as vscode from "vscode";
import type { SerenaMcpClient } from "../mcp/serenaClient";
import { formatSerenaError, SerenaUnavailableError } from "../mcp/serenaClient";
import type { DefinitionResult, HoverDocs } from "../mcp/types";

export function formatHoverMarkdown(hover: HoverDocs, definition?: DefinitionResult): string {
  const parts: string[] = [];
  if (hover.contents.trim()) {
    parts.push(hover.contents.trim());
  }
  if (definition && !definition.unresolved) {
    const loc = `${definition.path}:${definition.line}`;
    parts.push(`**Definition:** \`${loc}\``);
    if (definition.signature) {
      parts.push("```\n" + definition.signature + "\n```");
    }
    if (definition.docstring) {
      parts.push(definition.docstring);
    }
  } else if (definition?.message) {
    parts.push(`_${definition.message}_`);
  }
  return parts.join("\n\n");
}

export function createSerenaHoverProvider(
  getClient: () => SerenaMcpClient,
): vscode.HoverProvider {
  return {
    async provideHover(document, position, _token) {
      const wordRange = document.getWordRangeAtPosition(position);
      const symbol = wordRange ? document.getText(wordRange) : undefined;
      const client = getClient();
      try {
        const pos = {
          path: document.uri.fsPath,
          line: position.line + 1,
          column: position.character,
          symbol: symbol ?? null,
        };
        const [hover, definition] = await Promise.all([
          client.hover(pos),
          client.findDefinition(pos),
        ]);
        const md = formatHoverMarkdown(hover, definition);
        if (!md.trim()) {
          return undefined;
        }
        return new vscode.Hover(new vscode.MarkdownString(md, true), wordRange);
      } catch (err) {
        if (err instanceof SerenaUnavailableError) {
          // Soft-fail hover when MCP down — avoid spamming every mouse move.
          return new vscode.Hover(
            new vscode.MarkdownString(`_${formatSerenaError(err)}_`, true),
          );
        }
        return undefined;
      }
    },
  };
}
