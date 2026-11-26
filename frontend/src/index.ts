// Registers every Baby Calendar card and the shared editor.

import { BottleCard } from "./cards/bottle";
import { BreastfeedingCard } from "./cards/breastfeeding";
import { DiaperCard } from "./cards/diaper";
import { EntryCard } from "./cards/entry";
import { MedicationCard } from "./cards/medication";
import { SleepCard } from "./cards/sleep";
import { SummaryCard } from "./cards/summary";
import { TodayCard } from "./cards/today";
import { BabyCardEditor } from "./editor";

export const CARDS: [string, CustomElementConstructor, string, string][] = [
  ["baby-calendar-diaper-card", DiaperCard, "Baby Calendar: diapers", "Wet, dirty or both, and the stool type."],
  ["baby-calendar-bottle-card", BottleCard, "Baby Calendar: bottle", "A bottle with its amount and content."],
  ["baby-calendar-breastfeeding-card", BreastfeedingCard, "Baby Calendar: breastfeeding", "Left and right, and the last feed."],
  ["baby-calendar-sleep-card", SleepCard, "Baby Calendar: sleep", "Fell asleep and woke up."],
  ["baby-calendar-medication-card", MedicationCard, "Baby Calendar: medications", "Doses due, with Given."],
  ["baby-calendar-summary-card", SummaryCard, "Baby Calendar: summary", "Since the last feed, diaper and sleep."],
  ["baby-calendar-today-card", TodayCard, "Baby Calendar: today", "The day's totals."],
  ["baby-calendar-entry-card", EntryCard, "Baby Calendar: other entries", "Weight, length, temperature, solids, pumping, a dose."],
];

declare global {
  interface Window {
    customCards?: { type: string; name: string; description: string; preview?: boolean }[];
  }
}

if (!customElements.get("baby-calendar-card-editor")) {
  customElements.define("baby-calendar-card-editor", BabyCardEditor);
}
window.customCards = window.customCards ?? [];
for (const [tag, element, name, description] of CARDS) {
  if (customElements.get(tag)) continue;
  customElements.define(tag, element);
  window.customCards.push({ type: tag, name, description, preview: false });
}
