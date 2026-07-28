/** Confirmed POST /context request/response — consume only (api-contract §2.3). */

export interface ContextRequest {
  query: string;
  file?: string | null;
  repo: string;
  top_k: number;
}

/** Confirmed POST /index request and response fields (api-contract §2.2). */
export interface IndexRequest {
  repo_path: string;
  repo_name: string;
}

export interface IndexResponse {
  files_indexed: number;
  graph_nodes: number;
  embeddings: number;
  time_ms: number;
}

export interface ContextMetrics {
  tokens_before: number;
  tokens_after: number;
  saving_percent: number;
  trace: string | Record<string, unknown>;
  latency_ms: number;
}

export interface ContextResponse {
  final_context: string;
  metrics: ContextMetrics;
  blast_radius: Record<string, unknown> | null;
  memory: Record<string, unknown> | null;
  relevant_files: unknown[];
  is_real: boolean;
}
