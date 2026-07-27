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
