// Summary: how long ago the baby ate and had a diaper change, and sleep.

import { html, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import { duration } from "../format";
import type { TextKey } from "../i18n";
import type { Baby } from "../types";

export class SummaryCard extends BabyCard {
  protected titleKey: TextKey = "summary";
  protected logs = false;

  protected override tickMs(): number | null {
    return 30_000;
  }

  private since(value: string | undefined): string {
    if (!value || value === "unknown" || value === "unavailable") return this.text("never");
    const seconds = (this._now - new Date(value).getTime()) / 1000;
    return this.text("ago", { duration: duration(seconds) });
  }

  protected renderBody(baby: Baby): TemplateResult {
    const facts: TemplateResult[] = [];
    const feed = this.entity(baby, "last_feed");
    if (feed) facts.push(this.fact("ate", this.since(feed.state)));
    const diaper = this.entity(baby, "diaper_last");
    if (diaper) facts.push(this.fact("diaper", this.since(diaper.state)));
    const timer = this.entity(baby, "sleep_timer");
    if (timer?.state === "on" && timer.attributes.started_at) {
      const seconds = (this._now - new Date(timer.attributes.started_at).getTime()) / 1000;
      facts.push(this.fact("asleep", duration(seconds)));
    } else {
      const awake = this.entity(baby, "awake_since");
      if (awake) facts.push(this.fact("awake", this.since(awake.state)));
    }
    return html`<div class="facts" style="--columns: ${facts.length || 1}">${facts}</div>`;
  }

  private fact(label: TextKey, value: string): TemplateResult {
    return html`<div class="fact">
      <div class="label">${this.text(label)}</div>
      <div class="value">${value}</div>
    </div>`;
  }
}

