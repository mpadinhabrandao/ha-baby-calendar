// Medications: the doses due, each with "Given"; optionally every one.

import { html, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import type { TextKey } from "../i18n";
import type { Baby, Medication } from "../types";

export class MedicationCard extends BabyCard {
  protected titleKey: TextKey = "medications";
  protected accent = "var(--red-color, #f44336)";

  private due(medication: Medication): boolean {
    const entityId = medication.entities.due;
    return Boolean(entityId && this.hass?.states[entityId]?.state === "on");
  }

  protected renderBody(baby: Baby): TemplateResult {
    const shown = this._config?.show_all
      ? baby.medications
      : baby.medications.filter((medication) => this.due(medication));
    if (!shown.length) return html`<p class="hint">${this.text("nothing_due")}</p>`;
    return html`${shown.map(
      (medication) => html`<div class="medication ${this.due(medication) ? "due" : ""}">
        <div class="what">
          ${this.due(medication) ? html`<div class="label">${this.text("due_now")}</div>` : ""}
          <div class="name">
            ${medication.name}${medication.dose ? html` · ${medication.dose}` : ""}
          </div>
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
      </div>`,
    )}`;
  }
}
