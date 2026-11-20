// Diapers: wet, dirty, both, and the stool type right after a dirty one.

import { html, type TemplateResult } from "lit";

import { BabyCard } from "../base";
import type { TextKey } from "../i18n";
import type { Baby } from "../types";

const CONTENTS = ["wet", "dirty", "both"] as const;
const STOOLS = ["normal", "soft", "hard", "diarrhea"] as const;

export class DiaperCard extends BabyCard {
  protected tracker = "diaper";
  protected titleKey: TextKey = "diapers";
  protected accent = "var(--amber-color, #ffc107)";

  protected renderBody(baby: Baby): TemplateResult {
    const asking = this.entity(baby, "stool_prompt")?.state === "on";
    return html`
      <div class="row">
        ${CONTENTS.map(
          (content) => html`<button
            class="big"
            @click=${() =>
              this.log(
                `diaper_${content}`,
                "log_diaper",
                { content },
                this.text(`diaper_${content}` as TextKey),
              )}
          >
            ${this.text(content)}
          </button>`,
        )}
      </div>
      ${asking
        ? html`<div class="question" role="group" aria-label=${this.text("stool_question")}>
            <p class="ask">${this.text("stool_question")}</p>
            <div class="row" style="--columns: 2">
              ${STOOLS.map(
                (stool) => html`<button
                  class="big"
                  @click=${() =>
                    this.act(`stool_${stool}`, () =>
                      this.call("button", "press", { entity_id: baby.entities[`stool_${stool}`] }),
                    )}
                >
                  ${this.text(`stool_${stool}` as TextKey)}
                </button>`,
              )}
            </div>
            <p class="hint">${this.text("stool_optional")}</p>
          </div>`
        : ""}
    `;
  }
}
