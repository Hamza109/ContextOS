/**
 * Webview ↔ extension message sanitize (EP-007 / US-020; Constitution III).
 *
 * Prefer FastAPI JSON blast → React Flow nodes/edges.
 * Embedding GET /graph.html remains NEEDS CLARIFICATION (auth unresolved) —
 * this panel does NOT fetch or embed graph.html.
 */

/** Allowed extension → webview message types. */
export const EXT_TO_WEBVIEW_TYPES = [
  "blastGraph",
  "error",
  "empty",
  "status",
  "staleness",
] as const;

/** Allowed webview → extension message types. */
export const WEBVIEW_TO_EXT_TYPES = ["ready", "refresh", "openFile"] as const;

export type ExtToWebviewType = (typeof EXT_TO_WEBVIEW_TYPES)[number];
export type WebviewToExtType = (typeof WEBVIEW_TO_EXT_TYPES)[number];

const MAX_PATH_LEN = 1024;
const MAX_MESSAGE_LEN = 2000;
const MAX_NODES = 500;
const MAX_EDGES = 2000;

export interface SanitizedGraphNode {
  id: string;
  label: string;
  kind: "target" | "direct" | "transitive";
}

export interface SanitizedGraphEdge {
  id: string;
  source: string;
  target: string;
}

export interface BlastGraphPayload {
  type: "blastGraph";
  fileName: string;
  risk: string;
  nodes: SanitizedGraphNode[];
  edges: SanitizedGraphEdge[];
  stale: boolean;
  badge?: string;
  indexRevision?: string | null;
}

export type ExtToWebviewMessage =
  | BlastGraphPayload
  | { type: "error"; message: string }
  | { type: "empty"; message: string }
  | { type: "status"; message: string }
  | { type: "staleness"; stale: boolean; badge?: string };

export type WebviewToExtMessage =
  | { type: "ready" }
  | { type: "refresh" }
  | { type: "openFile"; path: string };

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function sanitizePath(raw: unknown): string | undefined {
  if (typeof raw !== "string") return undefined;
  const trimmed = raw.trim();
  if (!trimmed || trimmed.length > MAX_PATH_LEN) return undefined;
  // Reject control chars / obvious script smuggling; paths only.
  if (/[\u0000-\u001f<>`]/.test(trimmed)) return undefined;
  return trimmed;
}

function sanitizeShortText(raw: unknown, max = MAX_MESSAGE_LEN): string | undefined {
  if (typeof raw !== "string") return undefined;
  const trimmed = raw.trim();
  if (!trimmed || trimmed.length > max) return undefined;
  if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(trimmed)) return undefined;
  return trimmed;
}

function sanitizeNode(raw: unknown): SanitizedGraphNode | undefined {
  if (!isPlainObject(raw)) return undefined;
  const id = sanitizePath(raw.id);
  const label = sanitizePath(raw.label) ?? id;
  const kind = raw.kind;
  if (!id || !label) return undefined;
  if (kind !== "target" && kind !== "direct" && kind !== "transitive") return undefined;
  return { id, label, kind };
}

function sanitizeEdge(raw: unknown): SanitizedGraphEdge | undefined {
  if (!isPlainObject(raw)) return undefined;
  const id = sanitizePath(raw.id);
  const source = sanitizePath(raw.source);
  const target = sanitizePath(raw.target);
  if (!id || !source || !target) return undefined;
  return { id, source, target };
}

/**
 * Sanitize host → webview payload. Drops unknown types and fabricated fields.
 * Never injects nodes/edges that were not supplied by the caller (API-derived).
 */
export function sanitizeExtToWebviewMessage(raw: unknown): ExtToWebviewMessage | undefined {
  if (!isPlainObject(raw) || typeof raw.type !== "string") return undefined;
  const type = raw.type as ExtToWebviewType;
  if (!(EXT_TO_WEBVIEW_TYPES as readonly string[]).includes(type)) return undefined;

  if (type === "error" || type === "empty" || type === "status") {
    const message = sanitizeShortText(raw.message);
    if (!message) return undefined;
    return { type, message };
  }

  if (type === "staleness") {
    if (typeof raw.stale !== "boolean") return undefined;
    const badge = raw.badge === undefined ? undefined : sanitizeShortText(raw.badge, 200);
    return badge ? { type: "staleness", stale: raw.stale, badge } : { type: "staleness", stale: raw.stale };
  }

  // blastGraph
  const fileName = sanitizePath(raw.fileName);
  const risk = sanitizeShortText(raw.risk, 16);
  if (!fileName || !risk) return undefined;
  if (!Array.isArray(raw.nodes) || !Array.isArray(raw.edges)) return undefined;
  if (raw.nodes.length > MAX_NODES || raw.edges.length > MAX_EDGES) return undefined;
  if (typeof raw.stale !== "boolean") return undefined;

  const nodes: SanitizedGraphNode[] = [];
  for (const n of raw.nodes) {
    const sn = sanitizeNode(n);
    if (!sn) return undefined;
    nodes.push(sn);
  }
  const edges: SanitizedGraphEdge[] = [];
  for (const e of raw.edges) {
    const se = sanitizeEdge(e);
    if (!se) return undefined;
    edges.push(se);
  }

  const badge = raw.badge === undefined ? undefined : sanitizeShortText(raw.badge, 200);
  const indexRevision =
    raw.indexRevision === null
      ? null
      : raw.indexRevision === undefined
        ? undefined
        : sanitizeShortText(raw.indexRevision, 256);

  const payload: BlastGraphPayload = {
    type: "blastGraph",
    fileName,
    risk,
    nodes,
    edges,
    stale: raw.stale,
  };
  if (badge) payload.badge = badge;
  if (indexRevision !== undefined) payload.indexRevision = indexRevision;
  return payload;
}

/**
 * Sanitize webview → host message. Only allowlisted actions.
 */
export function sanitizeWebviewToExtMessage(raw: unknown): WebviewToExtMessage | undefined {
  if (!isPlainObject(raw) || typeof raw.type !== "string") return undefined;
  const type = raw.type as WebviewToExtType;
  if (!(WEBVIEW_TO_EXT_TYPES as readonly string[]).includes(type)) return undefined;

  if (type === "ready" || type === "refresh") {
    return { type };
  }
  const path = sanitizePath(raw.path);
  if (!path) return undefined;
  return { type: "openFile", path };
}
