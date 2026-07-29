/**
 * T033 (extension) / T035 — Proposed staleness presence/clear (EP-007 US-027).
 * No Confirmed numeric threshold constant.
 */
import { describe, expect, it } from "vitest";
import { formatAskContextReport } from "../src/providers/askContextPresenter";
import { formatPackContextReport } from "../src/providers/packContextPresenter";
import {
  evaluateStaleness,
  FreshnessSession,
  STALE_BADGE_TEXT,
  STALE_BANNER_PREFIX,
} from "../src/providers/stalenessPresenter";
import type { ContextResponse } from "../src/api/types";

function contextResponse(blast_radius: Record<string, unknown> | null): ContextResponse {
  return {
    final_context: "packed",
    metrics: {
      tokens_before: 10,
      tokens_after: 5,
      saving_percent: 50,
      trace: {},
      latency_ms: 1,
    },
    blast_radius,
    memory: null,
    relevant_files: [],
    is_real: true,
  };
}

describe("staleness presenter (T033/T035)", () => {
  it("warns on Proposed stale flag and clears when false", () => {
    const warn = evaluateStaleness(
      { stale: true },
      { showStalenessWarnings: true },
    );
    expect(warn.isStale).toBe(true);
    expect(warn.badgeText).toBe(STALE_BADGE_TEXT);
    expect(warn.reason).toBe("flag");

    const clear = evaluateStaleness(
      { stale: false },
      { showStalenessWarnings: true },
    );
    expect(clear.isStale).toBe(false);
    expect(clear.badgeText).toBeUndefined();
    expect(clear.reason).toBe("fresh");
  });

  it("warns on revision drift and clears when baseline matches", () => {
    const drift = evaluateStaleness(
      { indexRevision: "rev-2", baselineRevision: "rev-1" },
      { showStalenessWarnings: true },
    );
    expect(drift.isStale).toBe(true);
    expect(drift.reason).toBe("revision_drift");

    const ok = evaluateStaleness(
      { indexRevision: "rev-2", baselineRevision: "rev-2" },
      { showStalenessWarnings: true },
    );
    expect(ok.isStale).toBe(false);
  });

  it("respects Proposed boolean config — no Confirmed threshold constant", () => {
    const disabled = evaluateStaleness(
      { stale: true },
      { showStalenessWarnings: false },
    );
    expect(disabled.isStale).toBe(false);
    expect(disabled.reason).toBe("disabled");

    // Ensure this module does not encode a Confirmed numeric threshold.
    const src = evaluateStaleness.toString();
    expect(src).not.toMatch(/THRESHOLD\s*=\s*\d+/);
  });

  it("session markIndexed clears baseline so refresh can restore freshness", () => {
    const session = new FreshnessSession();
    session.adoptFreshRevision("rev-old");
    expect(session.getBaseline()).toBe("rev-old");
    session.markIndexed();
    expect(session.getBaseline()).toBeNull();
    session.adoptFreshRevision("rev-new");
    expect(
      evaluateStaleness(
        { indexRevision: "rev-new", baselineRevision: session.getBaseline() },
        { showStalenessWarnings: true },
      ).isStale,
    ).toBe(false);
  });

  it("Ask/Pack DX surfaces stale banner when blast_radius.stale is true", () => {
    const ask = formatAskContextReport(
      contextResponse({ stale: true, index_revision: "r1" }),
      { showStalenessWarnings: true },
    );
    expect(ask).toContain(STALE_BANNER_PREFIX);

    const pack = formatPackContextReport(
      contextResponse({ stale: true }),
      { showStalenessWarnings: true },
    );
    expect(pack).toContain(STALE_BANNER_PREFIX);

    const cleared = formatAskContextReport(
      contextResponse({ stale: false }),
      { showStalenessWarnings: true },
    );
    expect(cleared).not.toContain(STALE_BANNER_PREFIX);
  });
});
