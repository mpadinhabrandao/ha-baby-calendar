// Recent entries: the baby's latest entries, newest first.

import { html, type PropertyValues, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import { duration, timeOfDay } from "../format";
import type { TextKey } from "../i18n";
import type { Baby, EventItem } from "../types";

const DAY_MS = 24 * 3600 * 1000;
const LIMIT = 15;
// Measurements open their value sensor, which draws the readings.
const MEASUREMENTS = ["weight", "length", "temperature"];

export class RecentCard extends BabyCard {
  static override properties = { ...BabyCard.properties, _events: { state: true } };

  protected titleKey: TextKey = "recent";
  protected logs = false;

  private _events: EventItem[] | null = null;
  private _signature = "";

  /** Changes whenever one of the baby's last-entry sensors changes. */
  private signature(baby: Baby): string {
    return Object.entries(baby.entities)
      .filter(([key]) => key.endsWith("_last") || key === "last_feed")
      .map(([, entityId]) => this.hass?.states[entityId]?.last_changed ?? "")
      .concat(baby.medications.map((m) => this.hass?.states[m.entities.last_dose]?.last_changed ?? ""))
      .join("|");
  }

  protected override updated(changed: PropertyValues): void {
    super.updated(changed);
    const baby = this.baby;
    if (!baby) return;
    const signature = `${baby.device_id}|${this.signature(baby)}`;
    if (signature === this._signature) return;
    this._signature = signature;
    this.refresh(baby);
  }

  private async refresh(baby: Baby): Promise<void> {
    const end = new Date(Date.now() + 60_000);
    const start = new Date(end.getTime() - DAY_MS - 60_000);
    try {
      const response = await this.call(
        "baby_calendar",
        "list_events",
        { device_id: baby.device_id, start: start.toISOString(), end: end.toISOString() },
        true,
      );
      const events = (response?.events ?? []) as EventItem[];
      this._events = [...events].sort((a, b) => (a.time < b.time ? 1 : -1)).slice(0, LIMIT);
    } catch (err) {
      this.showError(err);
    }
  }

  /** A short description of an entry. */
  describe(event: EventItem): string {
    const n = (value: unknown) => String(Math.round(Number(value) * 10) / 10);
    switch (event.tracker) {
      case "diaper": {
        const content = String(event.content);
        const text = this.text(`diaper_${content}` as TextKey);
        return event.stool ? `${text} (${this.text(`stool_${event.stool}` as TextKey).toLowerCase()})` : text;
      }
      case "bottle":
        return this.text("bottle_of", { amount: n(event.amount) });
      case "breastfeeding": {
        const side = event.side ? this.text(event.side as TextKey).toLowerCase() : "";
        const text = this.text("feed_side", { side }).trim();
        return event.in_progress
          ? `${text} · ${this.text("running")}`
          : `${text} · ${duration(Number(event.duration ?? 0))}`;
      }
      case "sleep":
        return event.in_progress
          ? `${this.text("sleep_entry")} · ${this.text("running")}`
          : `${this.text("sleep_entry")} · ${duration(Number(event.duration ?? 0))}`;
      case "weight":
      case "length":
      case "temperature":
        return this.text(`${event.tracker}_of` as TextKey, { value: n(event.value) });
      case "pumping":
        return this.text("pumping_of", { amount: n(event.amount) });
      case "solids":
        return event.notes ? `${this.text("solids_entry")} · ${event.notes}` : this.text("solids_entry");
      case "medication":
        return String(event.medication ?? "");
      default:
        return event.tracker;
    }
  }

  /** The entity whose more-info dialog shows this kind of entry, if it exists. */
  entityOf(event: EventItem): string | undefined {
    const baby = this.baby;
    if (!baby) return undefined;
    if (event.tracker === "medication") {
      const medication = baby.medications.find((m) => m.name === event.medication);
      return medication?.entities.last_dose;
    }
    const key = MEASUREMENTS.includes(event.tracker) ? event.tracker : `${event.tracker}_last`;
    return baby.entities[key];
  }

  private openDetails(entityId: string): void {
    this.dispatchEvent(
      new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true }),
    );
  }

  protected renderBody(): TemplateResult {
    if (this._events === null) return html``;
    if (!this._events.length) return html`<p class="hint">${this.text("no_entries")}</p>`;
    return html`<ul class="list">
      ${this._events.map((event) => {
        const line = html`<span>${this.describe(event)}</span>
          <span class="when">${timeOfDay(new Date(event.time), this.language)}</span>`;
        const entityId = this.entityOf(event);
        return html`<li>
          ${entityId
            ? html`<button class="entry" @click=${() => this.openDetails(entityId)}>${line}</button>`
            : html`<div class="entry">${line}</div>`}
        </li>`;
      })}
    </ul>`;
  }
}
