// Medications: the doses due, each with "Given"; optionally every one.

import { html, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import { nextDoseText, scheduleText, timeOfDay } from "../format";
import type { TextKey } from "../i18n";
import type { Baby, Medication } from "../types";

export class MedicationCard extends BabyCard {
  protected titleKey: TextKey = "medications";
  protected accent = "var(--red-color, #f44336)";

  private due(medication: Medication): boolean {
    const entityId = medication.entities.due;
    return Boolean(entityId && this.hass?.states[entityId]?.state === "on");
  }

  /** The next dose sensor's time, or null when it has none. */
  private nextDose(medication: Medication): Date | null {
    const entityId = medication.entities.next_dose;
    const state = entityId ? this.hass?.states[entityId]?.state : undefined;
    const when = state ? new Date(state) : null;
    return when && !Number.isNaN(when.getTime()) ? when : null;
  }

  private dueLabel(next: Date | null): string {
    const label = this.text("due_now");
    return next
      ? `${label} · ${this.text("due_since", { time: timeOfDay(next, this.language) })}`
      : label;
  }

  // Each part stays on one line; a narrow card wraps between them.
  private scheduleLine(medication: Medication, next: Date | null, due: boolean): TemplateResult {
    const schedule = scheduleText(medication.schedule ?? { type: "none" }, this.language);
    return next && !due
      ? html`<span>${schedule}</span> · <span>${nextDoseText(next, new Date(), this.language)}</span>`
      : html`<span>${schedule}</span>`;
  }

  protected renderBody(baby: Baby): TemplateResult {
    const shown = this._config?.show_all
      ? baby.medications
      : baby.medications.filter((medication) => this.due(medication));
    if (!shown.length) return html`<p class="hint">${this.text("nothing_due")}</p>`;
    return html`${shown.map((medication) => {
      const due = this.due(medication);
      const next = this.nextDose(medication);
      return html`<div class="medication ${due ? "due" : ""}">
        <div class="what">
          ${due ? html`<div class="label">${this.dueLabel(next)}</div>` : ""}
          <div class="name">
            ${medication.name}${medication.dose ? html` · ${medication.dose}` : ""}
          </div>
          <div class="schedule">${this.scheduleLine(medication, next, due)}</div>
        </div>
        <button
          class="big given"
          @click=${() =>
            this.log(
              `med_${medication.id}`,
              "log_medication",
              { medication: medication.name },
              medication.name,
            )}
        >
          ${this.text("given")}
        </button>
      </div>`;
    })}`;
  }
}
