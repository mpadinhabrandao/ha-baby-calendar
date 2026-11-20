// The visual editor shared by every card: the baby, and for the
// medications card whether to list every medication.

import { css, html, LitElement, type TemplateResult } from "lit";

import { languageOf, t } from "./i18n";
import { watchBabies } from "./store";
import type { Baby, CardConfig, Hass } from "./types";

export class BabyCardEditor extends LitElement {
  static override properties = {
    hass: { attribute: false },
    _config: { state: true },
    _babies: { state: true },
  };

  hass?: Hass;
  private _config?: CardConfig;
  private _babies: Baby[] = [];
  private _stop?: () => void;

  setConfig(config: CardConfig): void {
    this._config = config;
  }

  override connectedCallback(): void {
    super.connectedCallback();
    this._watch();
  }

  override disconnectedCallback(): void {
    super.disconnectedCallback();
    this._stop?.();
    this._stop = undefined;
  }

  protected override updated(): void {
    this._watch();
  }

  private _watch(): void {
    if (this._stop || !this.hass || !this.isConnected) return;
    this._stop = watchBabies(this.hass.connection, (babies) => {
      this._babies = babies;
    });
  }

  private _change(update: Partial<CardConfig>): void {
    const config = { ...this._config!, ...update };
    this._config = config;
    this.dispatchEvent(
      new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }),
    );
  }

  protected override render(): TemplateResult {
    const language = languageOf(this.hass?.locale?.language ?? this.hass?.language);
    const medications = this._config?.type === "custom:baby-calendar-medication-card";
    return html`
      <label>
        <span>${t(language, "baby")}</span>
        <select
          @change=${(event: Event) =>
            this._change({ baby: (event.target as HTMLSelectElement).value })}
        >
          <option value="" ?selected=${!this._config?.baby}>—</option>
          ${this._babies.map(
            (baby) =>
              html`<option value=${baby.device_id} ?selected=${baby.device_id === this._config?.baby}>
                ${baby.name}
              </option>`,
          )}
        </select>
      </label>
      ${medications
        ? html`<label class="check">
            <input
              type="checkbox"
              .checked=${Boolean(this._config?.show_all)}
              @change=${(event: Event) =>
                this._change({ show_all: (event.target as HTMLInputElement).checked })}
            />
            <span>${t(language, "show_all")}</span>
          </label>`
        : ""}
    `;
  }

  static override styles = css`
    :host {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    label {
      display: flex;
      flex-direction: column;
      gap: 4px;
      color: var(--primary-text-color);
    }
    label.check {
      flex-direction: row;
      align-items: center;
    }
    select {
      min-height: 44px;
      font: inherit;
      color: var(--primary-text-color);
      background: var(--card-background-color, transparent);
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
      border-radius: 8px;
      padding: 0 8px;
    }
  `;
}
