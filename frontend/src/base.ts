// What every card shares: the baby, the time chip, undo, errors and look.

import { css, html, LitElement, nothing, type PropertyValues, type TemplateResult } from "lit";

import { CHIP_MINUTES, chipTime, timeOfDay } from "./format";
import { RepeatGuard } from "./guard";
import { type Language, languageOf, t, type TextKey } from "./i18n";
import { watchBabies } from "./store";
import type { Baby, CardConfig, Hass, HassEntity } from "./types";

export const UNDO_MS = 60_000;

interface Undo {
  eventId: string;
  text: string;
  expires: number;
}

interface ServiceResult {
  response?: Record<string, any> | null;
}

export abstract class BabyCard extends LitElement {
  static override properties = {
    hass: { attribute: false },
    _config: { state: true },
    _babies: { state: true },
    _minutesAgo: { state: true },
    _undo: { state: true },
    _error: { state: true },
    _now: { state: true },
  };

  hass?: Hass;
  protected _config?: CardConfig;
  protected _babies: Baby[] | null = null;
  protected _minutesAgo = 0;
  protected _undo: Undo | null = null;
  protected _error: string | null = null;
  protected _now = Date.now();

  private _stopWatching?: () => void;
  private _timer?: number;
  private _guard = new RepeatGuard();

  /** The tracker the card needs, or null when it needs none. */
  protected tracker: string | null = null;
  /** The text key of the card's title. */
  protected abstract titleKey: TextKey;
  /** Whether the card logs entries, and so has a time chip and undo. */
  protected logs = true;
  /** The card's accent colour, a CSS value. */
  protected accent = "var(--primary-color)";

  setConfig(config: CardConfig): void {
    this._config = config;
  }

  getCardSize(): number {
    return 3;
  }

  getGridOptions(): Record<string, unknown> {
    return { columns: 12, min_columns: 6 };
  }

  static getConfigElement(): HTMLElement {
    return document.createElement("baby-calendar-card-editor");
  }

  static getStubConfig(): Record<string, unknown> {
    return { baby: "" };
  }

  protected get language(): Language {
    return languageOf(this.hass?.locale?.language ?? this.hass?.language);
  }

  protected text(key: TextKey, values?: Record<string, string | number>): string {
    return t(this.language, key, values);
  }

  protected get baby(): Baby | undefined {
    return this._babies?.find((baby) => baby.device_id === this._config?.baby);
  }

  protected entity(baby: Baby, key: string): HassEntity | undefined {
    const entityId = baby.entities[key];
    return entityId ? this.hass?.states[entityId] : undefined;
  }

  override connectedCallback(): void {
    super.connectedCallback();
    this._watch();
  }

  override disconnectedCallback(): void {
    super.disconnectedCallback();
    this._stopWatching?.();
    this._stopWatching = undefined;
    this._setTimer(null);
  }

  protected override updated(changed: PropertyValues): void {
    if (changed.has("hass")) this._watch();
    this._setTimer(this.tickMs());
  }

  /** How often the card re-renders while connected, or null for never. */
  protected tickMs(): number | null {
    return this._undo ? 1000 : null;
  }

  private _setTimer(ms: number | null): void {
    if (this._timer !== undefined && ms === this._timerMs) return;
    if (this._timer !== undefined) window.clearInterval(this._timer);
    this._timer = undefined;
    this._timerMs = ms;
    if (ms === null || !this.isConnected) return;
    this._timer = window.setInterval(() => {
      this._now = Date.now();
      if (this._undo && this._undo.expires <= this._now) this._undo = null;
    }, ms);
  }

  private _timerMs: number | null = null;

  private _watch(): void {
    if (this._stopWatching || !this.hass || !this.isConnected) return;
    this._stopWatching = watchBabies(this.hass.connection, (babies) => {
      this._babies = babies;
    });
  }

  // ----------------------------------------------------------- actions

  /** Call a service and return its response. */
  protected async call(
    domain: string,
    service: string,
    data: Record<string, unknown>,
    returnResponse = false,
  ): Promise<Record<string, any> | null> {
    const result = await this.hass!.connection.sendMessagePromise<ServiceResult>({
      type: "call_service",
      domain,
      service,
      service_data: data,
      return_response: returnResponse,
    });
    return result?.response ?? null;
  }

  /**
   * Record an entry with a Baby Calendar action: one call per tap, the time
   * chip applied once, then the undo bar.
   */
  protected async log(
    key: string,
    service: string,
    fields: Record<string, unknown>,
    what: string,
  ): Promise<boolean> {
    const baby = this.baby;
    if (!baby || !this._guard.allow(key)) return false;
    const time = chipTime(this._minutesAgo, new Date());
    try {
      const response = await this.call(
        "baby_calendar",
        service,
        { device_id: baby.device_id, ...fields, ...(time ? { time } : {}) },
        true,
      );
      this._minutesAgo = 0;
      this._error = null;
      const eventId = response?.event_id as string | undefined;
      if (eventId) this.showUndo(eventId, what, time ? new Date(time) : new Date());
      return true;
    } catch (err) {
      this.showError(err);
      return false;
    }
  }

  /** Run another action, guarded and with errors shown. */
  protected async act(key: string, action: () => Promise<unknown>): Promise<boolean> {
    if (!this._guard.allow(key)) return false;
    try {
      await action();
      this._error = null;
      return true;
    } catch (err) {
      this.showError(err);
      return false;
    }
  }

  protected showUndo(eventId: string, what: string, when: Date): void {
    this._undo = {
      eventId,
      text: this.text("logged", { what, time: timeOfDay(when, this.language) }),
      expires: Date.now() + UNDO_MS,
    };
  }

  protected showError(err: unknown): void {
    const message =
      (err as { message?: string })?.message ?? (typeof err === "string" ? err : String(err));
    this._error = this.text("not_recorded", { error: message });
  }

  private async _undoLast(): Promise<void> {
    const undo = this._undo;
    if (!undo) return;
    try {
      await this.call("baby_calendar", "delete_event", { event_id: undo.eventId });
      this._undo = null;
      this._error = null;
    } catch (err) {
      this.showError(err);
    }
  }

  // ----------------------------------------------------------- rendering

  protected abstract renderBody(baby: Baby): TemplateResult | typeof nothing;

  protected override render(): TemplateResult {
    const message = this._message();
    return html`<ha-card style="--bc-accent: ${this.accent}">
      <div class="header">
        <h2>${this.text(this.titleKey)}</h2>
        ${this.logs && !message ? this._renderChip() : nothing}
      </div>
      ${message
        ? html`<p class="message">${message}</p>`
        : html`<div class="body">${this.renderBody(this.baby!)}</div>`}
      ${this._undo && !message
        ? html`<div class="undo" role="status">
            <span>${this._undo.text}</span>
            <button class="undo-button" @click=${this._undoLast}>${this.text("undo")}</button>
          </div>`
        : nothing}
      ${this._error ? html`<p class="error" role="alert">${this._error}</p>` : nothing}
    </ha-card>`;
  }

  private _message(): string | null {
    if (!this._config?.baby) return this.text("no_baby");
    if (this._babies === null) return " ";
    const baby = this.baby;
    if (!baby) return this.text("baby_not_found");
    if (this.tracker && !baby.trackers.includes(this.tracker)) {
      return this.text("tracker_off", { tracker: this.text(this.titleKey), baby: baby.name });
    }
    return null;
  }

  private _renderChip(): TemplateResult {
    return html`<label class="chip">
      <span class="visually-hidden">${this.text("when")}</span>
      <select
        .value=${String(this._minutesAgo)}
        @change=${(event: Event) => {
          this._minutesAgo = Number((event.target as HTMLSelectElement).value);
        }}
      >
        ${CHIP_MINUTES.map(
          (minutes) =>
            html`<option value=${minutes} ?selected=${minutes === this._minutesAgo}>
              ${minutes ? this.text("minutes_ago", { minutes }) : this.text("now")}
            </option>`,
        )}
      </select>
    </label>`;
  }

  static override styles = css`
    :host {
      display: block;
    }
    ha-card {
      padding: 12px 16px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      height: 100%;
      box-sizing: border-box;
      color: var(--primary-text-color);
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      min-height: 40px;
    }
    h2 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--primary-text-color);
    }
    .body {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .message {
      margin: 0;
      color: var(--secondary-text-color);
    }
    .row {
      display: grid;
      grid-template-columns: repeat(var(--columns, 3), minmax(0, 1fr));
      gap: 8px;
    }
    .big {
      min-height: 56px;
      border: none;
      border-radius: var(--ha-card-border-radius, 12px);
      background: color-mix(in srgb, var(--bc-accent) 22%, transparent);
      color: var(--primary-text-color);
      font: inherit;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      padding: 8px;
    }
    .big:hover {
      background: color-mix(in srgb, var(--bc-accent) 32%, transparent);
    }
    .big.active {
      outline: 2px solid var(--bc-accent);
      background: color-mix(in srgb, var(--bc-accent) 38%, transparent);
    }
    .big:focus-visible,
    .small:focus-visible,
    select:focus-visible {
      outline: 2px solid var(--primary-color);
      outline-offset: 2px;
    }
    .small {
      min-height: 44px;
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
      border-radius: 22px;
      background: transparent;
      color: var(--primary-text-color);
      font: inherit;
      font-size: 14px;
      padding: 0 14px;
      cursor: pointer;
    }
    .small.selected {
      background: color-mix(in srgb, var(--bc-accent) 22%, transparent);
      border-color: var(--bc-accent);
      font-weight: 600;
    }
    .amount {
      display: grid;
      grid-template-columns: 56px minmax(0, 1fr) 56px;
      gap: 8px;
    }
    .step {
      font-size: 24px;
    }
    .value {
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .big.primary {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: var(--bc-accent);
      color: var(--text-primary-color, #fff);
      font-size: 17px;
    }
    .big.primary:hover {
      background: color-mix(in srgb, var(--bc-accent) 85%, black);
    }
    .choices {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .stack {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
    }
    .time {
      font-size: 22px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .line {
      font-size: 15px;
      font-weight: 500;
    }
    .medication {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 8px 8px 12px;
      border-radius: 12px;
      background: color-mix(in srgb, var(--primary-text-color) 6%, transparent);
    }
    .medication.due {
      background: color-mix(in srgb, var(--bc-accent) 14%, transparent);
      border: 1px solid var(--bc-accent);
    }
    .medication .what {
      flex-grow: 1;
    }
    .medication .label {
      font-size: 13px;
      color: var(--secondary-text-color);
    }
    .medication .name {
      font-size: 16px;
      font-weight: 600;
    }
    .given {
      min-width: 96px;
    }
    .form {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .field {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 14px;
      color: var(--secondary-text-color);
    }
    .field input,
    .field select {
      min-height: 44px;
      font: inherit;
      font-size: 16px;
      color: var(--primary-text-color);
      background: var(--card-background-color, transparent);
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
      border-radius: 10px;
      padding: 0 10px;
    }
    .list {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .list li {
      border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.2));
    }
    .list .entry {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      width: 100%;
      padding: 10px 0;
      border: none;
      background: none;
      color: inherit;
      font: inherit;
      text-align: start;
    }
    .list button.entry {
      cursor: pointer;
    }
    .list button.entry:focus-visible {
      outline: 2px solid var(--bc-accent);
      outline-offset: 2px;
    }
    .list li:last-child {
      border-bottom: none;
    }
    .when {
      color: var(--secondary-text-color);
      white-space: nowrap;
    }
    .question {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 12px;
      border-radius: 12px;
      border: 1px solid var(--bc-accent);
      background: color-mix(in srgb, var(--bc-accent) 10%, transparent);
    }
    .ask {
      margin: 0;
      font-weight: 600;
    }
    .hint {
      margin: 0;
      font-size: 13px;
      color: var(--secondary-text-color);
    }
    .chip select {
      min-height: 40px;
      border-radius: 20px;
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
      background: var(--card-background-color, transparent);
      color: var(--primary-text-color);
      font: inherit;
      font-size: 14px;
      padding: 0 12px;
    }
    .undo {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 6px 6px 6px 12px;
      border-radius: 12px;
      background: color-mix(in srgb, var(--primary-text-color) 10%, transparent);
      font-size: 14px;
    }
    .undo-button {
      min-height: 40px;
      border: none;
      border-radius: 10px;
      background: color-mix(in srgb, var(--primary-text-color) 16%, transparent);
      color: var(--primary-text-color);
      font: inherit;
      font-weight: 600;
      padding: 0 14px;
      cursor: pointer;
    }
    .error {
      margin: 0;
      color: var(--error-color, #db4437);
      font-size: 14px;
    }
    .visually-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
    }
    .facts {
      display: grid;
      grid-template-columns: repeat(var(--columns, 3), minmax(0, 1fr));
      gap: 8px;
    }
    .fact {
      border-radius: 12px;
      padding: 10px 12px;
      background: color-mix(in srgb, var(--primary-text-color) 6%, transparent);
    }
    .fact .label {
      font-size: 13px;
      color: var(--secondary-text-color);
    }
    .fact .value {
      font-size: 18px;
      font-weight: 600;
    }
    .fact .detail {
      font-size: 13px;
      color: var(--secondary-text-color);
    }
  `;
}
