/**
 * Proposed extension settings (T052). Keys are not Confirmed product contracts.
 */

export const PROPOSED_SETTING_KEYS = {
  orchestratorBaseUrl: "contextos.orchestratorBaseUrl",
  autoIndexOnActivate: "contextos.autoIndexOnActivate",
  reindexOnSave: "contextos.reindexOnSave",
  indexTimeoutMs: "contextos.indexTimeoutMs",
  enableGraphBlastPanel: "contextos.enableGraphBlastPanel",
  showStalenessWarnings: "contextos.showStalenessWarnings",
} as const;

export const DEFAULT_ORCHESTRATOR_BASE_URL = "http://localhost:8000";
export const DEFAULT_INDEX_TIMEOUT_MS = 600_000;

export interface ExtensionConfig {
  /** Proposed: orchestrator base URL */
  orchestratorBaseUrl: string;
  /** Proposed: auto-index on activation */
  autoIndexOnActivate: boolean;
  /** Proposed: re-index on save */
  reindexOnSave: boolean;
  /** Proposed: client abort timeout */
  indexTimeoutMs: number;
  /** Proposed: enable React Flow blast/graph panel (EP-007 US-020) */
  enableGraphBlastPanel: boolean;
  /**
   * Proposed: show staleness badge/warnings (EP-007 US-027).
   * Numeric threshold remains NEEDS CLARIFICATION — boolean gate only.
   */
  showStalenessWarnings: boolean;
}

export type ConfigurationSection = {
  get(key: string): unknown;
};

export type GetConfiguration = (section: string) => ConfigurationSection | undefined;

/** Read Proposed settings from vscode.workspace.getConfiguration("contextos"). */
export function readExtensionConfig(getConfiguration: GetConfiguration): ExtensionConfig {
  const cfg = getConfiguration("contextos");
  const rawBase = cfg?.get("orchestratorBaseUrl");
  const base =
    (typeof rawBase === "string" ? rawBase : DEFAULT_ORCHESTRATOR_BASE_URL).trim() ||
    DEFAULT_ORCHESTRATOR_BASE_URL;
  const timeout = cfg?.get("indexTimeoutMs");
  const timeoutMs =
    typeof timeout === "number" && timeout >= 1000 ? timeout : DEFAULT_INDEX_TIMEOUT_MS;

  return {
    orchestratorBaseUrl: base.replace(/\/+$/, ""),
    autoIndexOnActivate: typeof cfg?.get("autoIndexOnActivate") === "boolean"
      ? (cfg.get("autoIndexOnActivate") as boolean)
      : true,
    reindexOnSave: typeof cfg?.get("reindexOnSave") === "boolean"
      ? (cfg.get("reindexOnSave") as boolean)
      : true,
    indexTimeoutMs: timeoutMs,
    enableGraphBlastPanel:
      typeof cfg?.get("enableGraphBlastPanel") === "boolean"
        ? (cfg.get("enableGraphBlastPanel") as boolean)
        : true,
    showStalenessWarnings:
      typeof cfg?.get("showStalenessWarnings") === "boolean"
        ? (cfg.get("showStalenessWarnings") as boolean)
        : true,
  };
}

/** Test helper: full ExtensionConfig with Proposed EP-007 defaults. */
export function defaultTestConfig(
  partial: Partial<ExtensionConfig> = {},
): ExtensionConfig {
  return {
    orchestratorBaseUrl: "http://orchestrator.test",
    autoIndexOnActivate: true,
    reindexOnSave: true,
    indexTimeoutMs: 60_000,
    enableGraphBlastPanel: true,
    showStalenessWarnings: true,
    ...partial,
  };
}
