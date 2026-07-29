/**
 * Discoverable L1 graph / blast URLs for Ask DX (Proposed).
 * Thin URL builders only — FastAPI owns graph.html and GET /blast.
 */

const PATH_HINT_RE =
  /(?:[\w.-]+\/)*[\w.-]+\.(?:py|ts|tsx|js|jsx|go|java)\b/i;

export function extractPathHint(query: string | undefined | null): string | null {
  const match = PATH_HINT_RE.exec(query || "");
  return match ? match[0] : null;
}

export function buildGraphHtmlUrl(
  baseUrl: string,
  repo: string,
  file?: string | null,
  depth = 3,
): string {
  const root = baseUrl.replace(/\/+$/, "");
  const d = Math.max(1, Math.min(5, Math.floor(depth)));
  const params = new URLSearchParams({
    repo,
    depth: String(d),
  });
  if (file && file.trim()) {
    params.set("file", file.trim().replace(/^\/+/, ""));
  }
  return `${root}/graph.html?${params.toString()}`;
}

export function buildBlastApiUrl(
  baseUrl: string,
  file: string,
  repo: string,
): string {
  const root = baseUrl.replace(/\/+$/, "");
  const path = file.trim().replace(/^\/+/, "");
  return `${root}/blast/${path.split("/").map(encodeURIComponent).join("/")}?repo=${encodeURIComponent(repo)}`;
}

export function hasBlastPayload(
  blast: Record<string, unknown> | null | undefined,
): boolean {
  if (!blast || typeof blast !== "object") return false;
  const direct = blast.direct_dependents;
  const transitive = blast.transitive;
  if (Array.isArray(direct) && direct.length > 0) return true;
  if (Array.isArray(transitive) && transitive.length > 0) return true;
  if (typeof blast.risk === "string" && blast.risk.length > 0) return true;
  return Object.keys(blast).length > 0;
}

export function formatGraphDiscoverySection(opts: {
  baseUrl: string;
  repo: string;
  file?: string | null;
  query?: string;
  depth?: number;
}): string {
  const seed =
    (opts.file && opts.file.trim()) || extractPathHint(opts.query) || null;
  const depth = opts.depth ?? 3;
  const lines = [
    "--- open graphs ---",
    `L1 IMPORTS graph (browser): ${buildGraphHtmlUrl(opts.baseUrl, opts.repo, seed, depth)}`,
  ];
  if (seed) {
    lines.push(
      `Blast API (JSON): ${buildBlastApiUrl(opts.baseUrl, seed, opts.repo)}`,
    );
  }
  lines.push(
    "VS Code: Command Palette → ContextOS: Show Blast Graph (uses GET /blast)",
  );
  return lines.join("\n");
}
