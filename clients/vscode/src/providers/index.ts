/** Proposed presentation helpers for L3 DX. */

export {
  createSerenaHoverProvider,
  formatHoverMarkdown,
} from "./hoverProvider";
export {
  collectReferenceExtensions,
  filterReferencesByExtensions,
  formatReferenceHit,
  formatReferencesReport,
  fileExtension,
} from "./referencesPresenter";
export {
  formatRenameScopeReport,
  renameScopeClaimsExecution,
  RENAME_SCOPE_REVIEW_DISCLAIMER,
} from "./renameScopePresenter";
export {
  formatPackContextReport,
  extractSafeEditSection,
  SAFE_EDIT_BLOCK_MARKER,
} from "./packContextPresenter";
export {
  formatAskContextReport,
  formatRelevantFiles,
} from "./askContextPresenter";
export {
  buildBlastApiUrl,
  buildGraphHtmlUrl,
  extractPathHint,
  formatGraphDiscoverySection,
} from "./graphLinks";
export {
  evaluateStaleness,
  extractFreshnessSignal,
  formatStalenessBanner,
  FreshnessSession,
  STALE_BADGE_TEXT,
} from "./stalenessPresenter";
export {
  sanitizeExtToWebviewMessage,
  sanitizeWebviewToExtMessage,
} from "./webviewSanitize";
export { blastResponseToGraphModel } from "./blastGraphModel";
export {
  SHOW_BLAST_GRAPH_COMMAND,
  openGraphBlastPanel,
  buildWebviewHtml,
} from "./graphBlastPanel";
