/**
 * Presentation mapping: FastAPI blast JSON → React Flow nodes/edges (EP-007 / US-020).
 *
 * Does NOT compute blast radius, traverse IMPORTS, or apply ignore rules.
 * Only layouts path lists already returned by GET /blast.
 *
 * Edge semantics (presentation only): dependent → target file implies reverse-IMPORTS
 * as reported by FastAPI (direct_dependents / transitive lists).
 */

import type { BlastResponse } from "../api/types";
import type { SanitizedGraphEdge, SanitizedGraphNode } from "./webviewSanitize";

export interface BlastGraphModel {
  nodes: SanitizedGraphNode[];
  edges: SanitizedGraphEdge[];
}

/**
 * Build React Flow model from Confirmed blast path lists + target file.
 * Empty dependents → single target node, no fabricated neighbors.
 */
export function blastResponseToGraphModel(
  fileName: string,
  blast: BlastResponse,
): BlastGraphModel {
  const target = fileName.trim();
  const nodesById = new Map<string, SanitizedGraphNode>();

  nodesById.set(target, { id: target, label: target, kind: "target" });

  for (const path of blast.direct_dependents) {
    const id = path.trim();
    if (!id || nodesById.has(id)) continue;
    nodesById.set(id, { id, label: id, kind: "direct" });
  }
  for (const path of blast.transitive) {
    const id = path.trim();
    if (!id || nodesById.has(id)) continue;
    nodesById.set(id, { id, label: id, kind: "transitive" });
  }

  const edges: SanitizedGraphEdge[] = [];
  const addEdge = (source: string, targetId: string) => {
    const id = `${source}__imports__${targetId}`;
    edges.push({ id, source, target: targetId });
  };

  for (const dep of blast.direct_dependents) {
    const id = dep.trim();
    if (!id) continue;
    addEdge(id, target);
  }
  // Transitive list is unordered beyond-direct set from API — connect each to target
  // as presentation hint only (not a hop-accurate path reconstruction).
  for (const dep of blast.transitive) {
    const id = dep.trim();
    if (!id) continue;
    addEdge(id, target);
  }

  return { nodes: [...nodesById.values()], edges };
}
