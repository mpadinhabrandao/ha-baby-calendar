// Other entries: small forms for weight, length, temperature, solids,
// pumping and a medication dose.

import { html, nothing, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import type { TextKey } from "../i18n";
import type { Baby } from "../types";

type Form = "weight" | "length" | "temperature" | "solids" | "pumping" | "medication";

const MEASUREMENTS: Record<string, { unit: string; step: string; what: TextKey }> = {
  weight: { unit: "g", step: "1", what: "weight_of" },
  length: { unit: "cm", step: "0.5", what: "length_of" },
  temperature: { unit: "°C", step: "0.1", what: "temperature_of" },
};

export class EntryCard extends BabyCard {
  static override properties = {
    ...BabyCard.properties,
    _open: { state: true },
    _values: { state: true },
  };

  protected titleKey: TextKey = "other";
  protected accent = "var(--teal-color, #009688)";

  private _open: Form | null = null;
  private _values: Record<string, string> = {};

  /** The forms the baby has, in a fixed order. */
  forms(baby: Baby): Form[] {
    const forms = (["weight", "length", "temperature", "solids", "pumping"] as Form[]).filter(
      (form) => baby.trackers.includes(form),
    );
    if (baby.medications.length) forms.push("medication");
    return forms;
  }

  private value(name: string): string {
    return this._values[name] ?? "";
  }

  private setValue(name: string, value: string): void {
    this._values = { ...this._values, [name]: value };
  }

  private async save(baby: Baby, form: Form): Promise<void> {
    let ok = false;
    if (form in MEASUREMENTS) {
      const value = Number(this.value("value").replace(",", "."));
      ok = await this.log(
        form,
        `log_${form}`,
        { value },
        this.text(MEASUREMENTS[form].what, { value: this.value("value") }),
      );
    } else if (form === "solids") {
      const notes = this.value("notes").trim();
      ok = await this.log(
        form,
        "log_solids",
        notes ? { notes } : {},
        notes || this.text("solids_entry"),
      );
    } else if (form === "pumping") {
      const amount = Number(this.value("amount"));
      const side = this.value("side");
      ok = await this.log(
        form,
        "log_pumping",
        { amount, ...(side ? { side } : {}) },
        this.text("pumping_of", { amount }),
      );
    } else {
      const name = this.value("medication") || baby.medications[0]?.name;
      ok = await this.log(form, "log_medication", { medication: name }, name);
    }
    if (ok) {
      this._open = null;
      this._values = {};
    }
  }

  protected renderBody(baby: Baby): TemplateResult {
    const forms = this.forms(baby);
    return html`
      <div class="row" style="--columns: 2">
        ${forms.map(
          (form) => html`<button
            class="big ${this._open === form ? "active" : ""}"
            aria-expanded=${this._open === form ? "true" : "false"}
            @click=${() => {
              this._open = this._open === form ? null : form;
              this._values = {};
            }}
          >
            ${this.text(form)}
          </button>`,
        )}
      </div>
      ${this._open ? this.renderForm(baby, this._open) : nothing}
    `;
  }

  private renderForm(baby: Baby, form: Form): TemplateResult {
    const input = (name: string, label: TextKey, attrs: Record<string, string> = {}) =>
      html`<label class="field">
        <span>${this.text(label)}${attrs.unit ? ` (${attrs.unit})` : ""}</span>
        <input
          name=${name}
          type=${attrs.type ?? "text"}
          inputmode=${attrs.inputmode ?? "text"}
          step=${attrs.step ?? "any"}
          .value=${this.value(name)}
          @input=${(event: Event) =>
            this.setValue(name, (event.target as HTMLInputElement).value)}
        />
      </label>`;
    let fields: TemplateResult;
    if (form in MEASUREMENTS) {
      const { unit, step } = MEASUREMENTS[form];
      fields = input("value", "value", { type: "number", inputmode: "decimal", step, unit });
    } else if (form === "solids") {
      fields = input("notes", "notes");
    } else if (form === "pumping") {
      fields = html`${input("amount", "amount", {
          type: "number",
          inputmode: "numeric",
          step: "1",
          unit: "ml",
        })}
        <label class="field">
          <span>${this.text("side")}</span>
          <select
            name="side"
            @change=${(event: Event) =>
              this.setValue("side", (event.target as HTMLSelectElement).value)}
          >
            <option value="">${this.text("side_none")}</option>
            <option value="left">${this.text("left")}</option>
            <option value="right">${this.text("right")}</option>
            <option value="both">${this.text("side_both")}</option>
          </select>
        </label>`;
    } else {
      fields = html`<label class="field">
        <span>${this.text("medication")}</span>
        <select
          name="medication"
          @change=${(event: Event) =>
            this.setValue("medication", (event.target as HTMLSelectElement).value)}
        >
          ${baby.medications.map(
            (medication) => html`<option value=${medication.name}>${medication.name}</option>`,
          )}
        </select>
      </label>`;
    }
    return html`<form
      class="form"
      @submit=${(event: Event) => {
        event.preventDefault();
        this.save(baby, form);
      }}
    >
      ${fields}
      <div class="choices">
        <button class="small selected" type="submit">${this.text("save")}</button>
        <button
          class="small"
          type="button"
          @click=${() => {
            this._open = null;
            this._values = {};
          }}
        >
          ${this.text("cancel")}
        </button>
      </div>
    </form>`;
  }
}
