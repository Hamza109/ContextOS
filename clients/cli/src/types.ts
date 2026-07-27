/**
 * Confirmed POST /context request/response fields (api-contract §2.3).
 * Mirror of clients/vscode/src/api/types.ts — consume only; no intelligence.
 */

export interface ContextRequest {
  query: string;
  file?: string | null;
  repo: string;
  top_k: number;
}

export interface ContextMetrics {
  tokens_raw: number;
  tokens_compacted: number;
  reduction_pct: number;
  latency_ms: number;
}

export interface ContextResponse {
  final_context: string;
  metrics: ContextMetrics;
  blast_radius: unknown[];
  memory: unknown[];
  relevant_files: unknown[];
  is_real: boolean;
}
