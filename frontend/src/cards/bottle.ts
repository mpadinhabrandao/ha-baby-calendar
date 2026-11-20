// Bottle: the amount on the button, − / + beside it, and the content.

import { html, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import type { TextKey } from "../i18n";
import type { Baby } from "../types";

const STEP = 10;
const CONTENTS = ["formula", "breast_milk"] as const;

export class BottleCard extends BabyCard {
  protected tracker = "bottle";
  protected titleKey: TextKey = "bottle";
  protected accent = "var(--blue-color, #2196f3)";

  static override properties = { ...BabyCard.properties, _pending: { state: true } };

  /** The amount just set with − / +, shown until the entity reports it. */
  private _pending: number | null = null;

  private amount(baby: Baby): number {
    const value = Number(this.entity(baby, "bottle_amount")?.state);
    const current = Number.isFinite(value) ? value : 0;
    if (this._pending !== null && this._pending === current) this._pending = null;
    return this._pending ?? current;
  }

  private async setAmount(baby: Baby, amount: number): Promise<void> {
    const entity = this.entity(baby, "bottle_amount");
    const max = Number(entity?.attributes.max ?? 500);
    const value = Math.min(max, Math.max(0, amount));
    // Not guarded: each tap is a new amount, and the latest one wins.
    this._pending = value;
    try {
      await this.call("number", "set_value", {
        entity_id: baby.entities.bottle_amount,
        value,
      });
      this._error = null;
    } catch (err) {
      this._pending = null;
      this.showError(err);
    }
  }

  protected renderBody(baby: Baby): TemplateResult {
    const amount = this.amount(baby);
    const content = this.entity(baby, "bottle_content")?.state;
    return html`
      <div class="amount">
        <button
          class="big step"
          aria-label=${this.text("less")}
          @click=${() => this.setAmount(baby, amount - STEP)}
        >
          −
        </button>
        <button
          class="big"
          @click=${() =>
            this.log(
              "bottle",
              "log_bottle",
              {
                amount,
                ...(content && CONTENTS.includes(content as any) ? { content } : {}),
              },
              this.text("bottle_of", { amount }),
            )}
        >
          ${this.text("bottle_button", { amount })}
        </button>
        <button
          class="big step"
          aria-label=${this.text("more")}
          @click=${() => this.setAmount(baby, amount + STEP)}
        >
          +
        </button>
      </div>
      <div class="choices">
        ${CONTENTS.map(
          (option) => html`<button
            class="small ${content === option ? "selected" : ""}"
            aria-pressed=${content === option ? "true" : "false"}
            @click=${() =>
              this.act(`bottle_content_${option}`, () =>
                this.call("select", "select_option", {
                  entity_id: baby.entities.bottle_content,
                  option,
                }),
              )}
          >
            ${this.text(option)}
          </button>`,
        )}
      </div>
    `;
  }
}
