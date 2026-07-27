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
