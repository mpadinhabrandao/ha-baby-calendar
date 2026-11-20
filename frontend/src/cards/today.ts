// Today: the day's totals for the baby's trackers.

import { html, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import { duration } from "../format";
import type { TextKey } from "../i18n";
import type { Baby } from "../types";

interface Total {
  label: TextKey;
  value: string;
  detail?: string;
}

export class TodayCard extends BabyCard {
  protected titleKey: TextKey = "today";
  protected logs = false;

  private number(baby: Baby, key: string): number | null {
    const state = this.entity(baby, key)?.state;
    const value = Number(state);
    return state === undefined || !Number.isFinite(value) ? null : value;
  }

  /** Every total the baby has, in the order of the trackers. */
  totals(baby: Baby): Total[] {
    const n = (key: string) => this.number(baby, key);
    const round = (value: number | null) => String(Math.round(value ?? 0));
    const totals: Total[] = [];
    if (n("diaper_changes_today") !== null) {
      totals.push({
        label: "diaper_changes",
        value: round(n("diaper_changes_today")),
        detail: this.text("wet_dirty", {
          wet: round(n("diaper_wet_today")),
          dirty: round(n("diaper_dirty_today")),
        }),
      });
    }
    if (n("bottle_count_today") !== null) {
      totals.push({
        label: "bottles",
        value: round(n("bottle_count_today")),
        detail: `${round(n("bottle_ml_today"))} ml`,
      });
    }
    if (n("breastfeeding_feeds_today") !== null) {
      totals.push({
        label: "feeds",
        value: round(n("breastfeeding_feeds_today")),
        detail: duration((n("breastfeeding_duration_today") ?? 0) * 60),
      });
    }
    if (n("sleep_duration_today") !== null) {
      totals.push({
        label: "sleeps",
        value: duration((n("sleep_duration_today") ?? 0) * 60),
        detail: `${round(n("sleep_count_today"))}×`,
      });
    }
    if (n("solids_count_today") !== null) {
      totals.push({ label: "solids", value: round(n("solids_count_today")) });
    }
    if (n("pumping_count_today") !== null) {
      totals.push({
        label: "pumping",
        value: round(n("pumping_count_today")),
        detail: `${round(n("pumping_ml_today"))} ml`,
      });
    }
    return totals;
  }

  protected renderBody(baby: Baby): TemplateResult {
    return html`<div class="facts" style="--columns: 2">
      ${this.totals(baby).map(
        (total) => html`<div class="fact">
          <div class="label">${this.text(total.label)}</div>
          <div class="value">${total.value}</div>
          ${total.detail ? html`<div class="detail">${total.detail}</div>` : ""}
        </div>`,
      )}
    </div>`;
  }
}
