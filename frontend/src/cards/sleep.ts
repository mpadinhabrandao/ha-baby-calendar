// Sleep: fell asleep / woke up, with the time asleep.

import { html, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import { clock, timeOfDay } from "../format";
import type { TextKey } from "../i18n";
import type { Baby } from "../types";

export class SleepCard extends BabyCard {
  protected tracker = "sleep";
  protected titleKey: TextKey = "sleep";
  protected accent = "var(--deep-purple-color, #673ab7)";

  private asleepSince(baby: Baby): Date | null {
    const timer = this.entity(baby, "sleep_timer");
    return timer?.state === "on" && timer.attributes.started_at
      ? new Date(timer.attributes.started_at)
      : null;
  }

  protected override tickMs(): number | null {
    const baby = this.baby;
    if (baby && this.asleepSince(baby)) return 1000;
    return super.tickMs();
  }

  protected renderBody(baby: Baby): TemplateResult {
    const since = this.asleepSince(baby);
    if (!since) {
      return html`<button
        class="big"
        @click=${() => this.log("sleep_start", "start_sleep", {}, this.text("sleep_entry"))}
      >
        ${this.text("fell_asleep")}
      </button>`;
    }
    const seconds = (this._now - since.getTime()) / 1000;
    return html`
      <button
        class="big active"
        @click=${() => this.log("sleep_stop", "stop_sleep", {}, this.text("sleep_entry"))}
      >
        <span class="stack">
          <span>${this.text("woke_up")}</span>
          <span class="time">${clock(seconds)}</span>
        </span>
      </button>
      <p class="hint">
        ${this.text("asleep_since", { time: timeOfDay(since, this.language) })}
      </p>
    `;
  }
}
