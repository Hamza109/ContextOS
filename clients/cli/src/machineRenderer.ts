/**
 * Proposed machine-readable serialization (OQ-10 / FR-003 / SC-002 / SC-006).
 * Schema is NOT Confirmed — do not freeze fields or invent schema Pass criteria.
 * Flag wiring / smoke only.
 */

import type { ContextResponse } from "./types";

/** Proposed envelope label — not a Confirmed contract. */
export const PROPOSED_MACHINE_SCHEMA_NOTE =
  "Proposed only (OQ-10) — schema not Confirmed; do not treat as freeze";

export function formatMachineAskReport(response: ContextResponse): string {
  const envelope = {
    _schema: PROPOSED_MACHINE_SCHEMA_NOTE,
    final_context: response.final_context,
    metrics: response.metrics,
    relevant_files: response.relevant_files,
    is_real: response.is_real,
    // blast_radius / memory included as pass-through; shape not Confirmed for CLI
    blast_radius: response.blast_radius,
    memory: response.memory,
  };
  return JSON.stringify(envelope, null, 2);
}
