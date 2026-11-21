// Breastfeeding: each side started and stopped on its own, and the last feed.

import { html, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import { clock, feedText } from "../format";
import type { TextKey } from "../i18n";
import type { Baby, FeedEntry } from "../types";

const SIDES = ["left", "right"] as const;

export class BreastfeedingCard extends BabyCard {
  protected tracker = "breastfeeding";
  protected titleKey: TextKey = "breastfeeding";
  protected accent = "var(--pink-color, #e91e63)";

  private running(baby: Baby): { side: string | null; start: Date } | null {
    const timer = this.entity(baby, "breastfeeding_timer");
    if (timer?.state !== "on" || !timer.attributes.started_at) return null;
    const last = this.entity(baby, "breastfeeding_last");
    const side = last?.attributes.in_progress ? (last.attributes.side ?? null) : null;
    return { side, start: new Date(timer.attributes.started_at) };
  }

  protected override tickMs(): number | null {
    const baby = this.baby;
    if (baby && this.running(baby)) return 1000;
    return super.tickMs() ?? 30_000;
  }

  private async tap(baby: Baby, side: string): Promise<void> {
    const running = this.running(baby);
    const label = this.text("feed_side", { side: this.text(side as TextKey).toLowerCase() });
    if (running && running.side === side) {
      await this.log(`stop_${side}`, "stop_breastfeeding", {}, label);
      return;
    }
    if (running) {
      // Another side runs: finish it, then start this one.
      const stopped = await this.act(`stop_${running.side}`, () =>
        this.call("baby_calendar", "stop_breastfeeding", { device_id: baby.device_id }),
      );
      if (!stopped) return;
    }
    await this.log(`start_${side}`, "start_breastfeeding", { side }, label);
  }

  protected renderBody(baby: Baby): TemplateResult {
    const running = this.running(baby);
    const now = new Date(this._now);
    const feed = (this.entity(baby, "breastfeeding_last")?.attributes.feed ?? []) as FeedEntry[];
    const last = feedText(feed, now, this.language);
    return html`
      <div class="row" style="--columns: 2">
        ${SIDES.map((side) => {
          const active = running?.side === side;
          return html`<button
            class="big ${active ? "active" : ""}"
            @click=${() => this.tap(baby, side)}
          >
            ${active
              ? html`<span class="stack">
                  <span>${this.text("stop")} · ${this.text(side).toLowerCase()}</span>
                  <span class="time"
                    >${clock((now.getTime() - running!.start.getTime()) / 1000)}</span
                  >
                </span>`
              : this.text(`start_${side}`)}
          </button>`;
        })}
      </div>
      <div class="fact">
        ${last
          ? html`<div class="label">${last.heading}</div>
              <div class="line">${last.line}</div>`
          : html`<div class="label">${this.text("no_feed")}</div>`}
      </div>
    `;
  }
}
