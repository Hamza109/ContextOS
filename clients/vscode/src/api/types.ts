/**
 * Confirmed POST /index request fields (docs/architecture/api-contract.md §2.2).
 */
export interface IndexRequestConfirmed {
  repo_path: string;
  repo_name: string;
}

/**
 * Proposed (OQ-14) optional narrower-scope fields for incremental re-index.
 * NOT Confirmed Appendix D — do not treat as freeze.
 */
export interface IndexRequestProposedScope {
  /** Proposed (OQ-14): optional path scope */
  paths?: string[];
  /** Proposed (OQ-14): optional file list */
  files?: string[];
}

export type IndexRequest = IndexRequestConfirmed & IndexRequestProposedScope;

/** Confirmed POST /index response fields (api-contract §2.2). */
export interface IndexResponse {
  files_indexed: number;
  graph_nodes: number;
  embeddings: number;
  time_ms: number;
}

/**
 * Confirmed POST /context request fields (api-contract Appendix D / EP-002).
 * No invented L3 REST fields — safe-edit lives inside final_context (OQ-Safe-Edit-Shape).
 */
export interface ContextRequest {
  query: string;
  /** Confirmed optional: cursor/file context bias */
  file?: string | null;
  repo: string;
  top_k: number;
}

/**
 * Confirmed ContextMetrics keys (Appendix D / api-contract §2.3).
 * latency_ms is observational — taken from metrics.trace.duration_ms when present.
 */
export interface ContextMetrics {
  tokens_before: number;
  tokens_after: number;
  saving_percent: number;
  trace: string | Record<string, unknown>;
  /** Proposed observational — from trace.duration_ms when available */
  latency_ms: number;
}

/**
 * Confirmed POST /context response (Appendix D).
 * blast_radius / memory are Confirmed keys; MVP empty object or null (not arrays).
 * Citations / safe-edit plan: content inside final_context only (OQ-11 / OQ-Safe-Edit-Shape).
 */
export interface ContextResponse {
  final_context: string;
  metrics: ContextMetrics;
  blast_radius: Record<string, unknown> | null;
  memory: Record<string, unknown> | null;
  relevant_files: unknown[];
  is_real: boolean;
}
