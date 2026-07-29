/**
 * Proposed US-027 staleness signaling (presence/clear only).
 *
 * Numeric freshness threshold remains NEEDS CLARIFICATION — do NOT invent a
 * Confirmed constant. Gate behind Proposed boolean config + optional API flag /
 * revision-drift comparison only.
 */

export const STALE_BADGE_TEXT = "Index may be stale";
export const STALE_BANNER_PREFIX = "[ContextOS] STALE:";

export interface FreshnessSignal {
  /** Proposed: explicit stale boolean when present on blast/graph/context payloads */
  stale?: boolean;
  /** Proposed: index_revision from GET /blast or blast_radius */
  indexRevision?: string | null;
  /**
   * Proposed session baseline: last revision considered fresh after index+refresh.
   * Drift (baseline !== indexRevision) → warn; match → clear.
   */
  baselineRevision?: string | null;
}

export interface StalenessConfig {
  /** Proposed: master enable for staleness UX (default true) */
  showStalenessWarnings: boolean;
}

export interface StalenessState {
  isStale: boolean;
  badgeText: string | undefined;
  reason: "disabled" | "flag" | "revision_drift" | "fresh";
}

/**
 * Evaluate Proposed freshness metadata for badge/warn UX.
 * No Confirmed numeric threshold.
 */
export function evaluateStaleness(
  signal: FreshnessSignal,
  config: StalenessConfig,
): StalenessState {
  if (!config.showStalenessWarnings) {
    return { isStale: false, badgeText: undefined, reason: "disabled" };
  }

  if (signal.stale === true) {
    return { isStale: true, badgeText: STALE_BADGE_TEXT, reason: "flag" };
  }
  if (signal.stale === false) {
    return { isStale: false, badgeText: undefined, reason: "fresh" };
  }

  const current = typeof signal.indexRevision === "string" ? signal.indexRevision.trim() : "";
  const baseline =
    typeof signal.baselineRevision === "string" ? signal.baselineRevision.trim() : "";
  if (current && baseline && current !== baseline) {
    return { isStale: true, badgeText: STALE_BADGE_TEXT, reason: "revision_drift" };
  }

  return { isStale: false, badgeText: undefined, reason: "fresh" };
}

/** Extract Proposed freshness fields from blast_radius / blast-like objects. */
export function extractFreshnessSignal(
  blastLike: Record<string, unknown> | null | undefined,
  baselineRevision?: string | null,
): FreshnessSignal {
  if (!blastLike) {
    return { baselineRevision: baselineRevision ?? null };
  }
  const signal: FreshnessSignal = {
    baselineRevision: baselineRevision ?? null,
  };
  if (typeof blastLike.stale === "boolean") {
    signal.stale = blastLike.stale;
  }
  if (blastLike.index_revision === null) {
    signal.indexRevision = null;
  } else if (typeof blastLike.index_revision === "string") {
    signal.indexRevision = blastLike.index_revision;
  }
  return signal;
}

/** One-line banner for Ask/Pack/search Output Channel DX. */
export function formatStalenessBanner(state: StalenessState): string | undefined {
  if (!state.isStale || !state.badgeText) return undefined;
  return `${STALE_BANNER_PREFIX} ${state.badgeText} (threshold NEEDS CLARIFICATION — Proposed signal only)`;
}

/**
 * Session helper: after successful index, baseline is cleared so the next
 * refresh can adopt the new revision as fresh (appear→clear scenario).
 *
 * Scenario (T036):
 * 1. Open blast panel — baseline set from first index_revision (fresh).
 * 2. Proposed stale=true or revision drift → badge appears.
 * 3. Run Index Repository / refresh after index → markIndexed(); next blast
 *    with restored freshness (stale=false or matching revision) → badge clears.
 */
export class FreshnessSession {
  private baselineRevision: string | null = null;

  getBaseline(): string | null {
    return this.baselineRevision;
  }

  /** Adopt revision as fresh baseline when currently unset or after index restore. */
  adoptFreshRevision(revision: string | null | undefined): void {
    if (typeof revision === "string" && revision.trim()) {
      this.baselineRevision = revision.trim();
    }
  }

  /** After index completes — clear baseline so restore can re-adopt. */
  markIndexed(): void {
    this.baselineRevision = null;
  }

  /** Test/DX: force a baseline for revision-drift checks. */
  setBaselineForTests(revision: string | null): void {
    this.baselineRevision = revision;
  }
}
