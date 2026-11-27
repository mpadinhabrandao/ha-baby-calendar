import { describe, expect, it } from "vitest";

import { ago, chipTime, clock, duration, feedText, nextDoseText, scheduleText } from "../src/format";
import { RepeatGuard } from "../src/guard";
import { languageOf, t } from "../src/i18n";

const at = (hhmm: string) => `2026-11-20T${hhmm}:00Z`;

describe("duration and clock", () => {
  it("writes minutes and hours", () => {
    expect(duration(12 * 60)).toBe("12 min");
    expect(duration(130 * 60)).toBe("2 h 10 min");
    expect(duration(120 * 60)).toBe("2 h");
    expect(duration(-5)).toBe("0 min");
  });

  it("writes a running time", () => {
    expect(clock(12 * 60 + 40)).toBe("12:40");
    expect(clock(80 * 60)).toBe("1:20:00");
  });

  it("says how long ago, in each language", () => {
    const since = new Date(at("01:30"));
    const now = new Date(at("03:40"));
    expect(ago(since, now, "en")).toBe("2 h 10 min ago");
    expect(ago(since, now, "pt")).toBe("há 2 h 10 min");
  });
});

describe("last feed", () => {
  const now = new Date(at("06:00"));

  it("one side", () => {
    const text = feedText([{ side: "right", start: at("03:12"), end: at("03:27") }], now, "en");
    expect(text?.line).toBe("Right 15 min");
    expect(text?.heading).toMatch(/^Last feed · \d\d:\d\d \(2 h 48 min ago\)$/);
  });

  it("two sides with a pause", () => {
    const text = feedText(
      [
        { side: "left", start: at("03:12"), end: at("03:24") },
        { side: "right", start: at("03:29"), end: at("03:37") },
      ],
      now,
      "en",
    );
    expect(text?.line).toBe("Left 12 min · pause 5 min · Right 8 min · 20 min in total");
  });

  it("two sides with no pause", () => {
    const text = feedText(
      [
        { side: "left", start: at("03:12"), end: at("03:24") },
        { side: "right", start: at("03:24"), end: at("03:32") },
      ],
      now,
      "en",
    );
    expect(text?.line).toBe("Left 12 min · Right 8 min · 20 min in total");
  });

  it("the same side twice", () => {
    const text = feedText(
      [
        { side: "left", start: at("03:00"), end: at("03:10") },
        { side: "left", start: at("03:16"), end: at("03:21") },
      ],
      now,
      "pt",
    );
    expect(text?.line).toBe("Esquerda 10 min · pausa 6 min · Esquerda 5 min · 15 min no total");
  });

  it("running", () => {
    const text = feedText(
      [
        { side: "left", start: at("03:12"), end: at("03:24") },
        { side: "right", start: at("03:29"), end: null },
      ],
      now,
      "en",
    );
    expect(text?.heading).toMatch(/^Feeding since \d\d:\d\d$/);
    expect(text?.line).toBe("Left 12 min · pause 5 min · Right running");
  });

  it("no feed", () => {
    expect(feedText([], now, "en")).toBeNull();
  });
});

describe("time chip and repeat guard", () => {
  it("now sends no time, minutes ago send that time", () => {
    const now = new Date(at("10:00"));
    expect(chipTime(0, now)).toBeUndefined();
    expect(chipTime(15, now)).toBe("2026-11-20T09:45:00.000Z");
  });

  it("drops a second tap within 3 seconds, per button", () => {
    const guard = new RepeatGuard();
    expect(guard.allow("wet", 0)).toBe(true);
    expect(guard.allow("wet", 1000)).toBe(false);
    expect(guard.allow("dirty", 1000)).toBe(true);
    expect(guard.allow("wet", 3000)).toBe(true);
  });
});

describe("language", () => {
  it("Portuguese for pt, English otherwise", () => {
    expect(languageOf("pt-PT")).toBe("pt");
    expect(languageOf("pt-BR")).toBe("pt");
    expect(languageOf("de")).toBe("en");
    expect(t("pt", "wet")).toBe("Xixi");
    expect(t("pt", "dirty")).toBe("Cocó");
    expect(t("pt", "both")).toBe("Os dois");
  });
});

describe("medication schedule", () => {
  // Local times: the card shows the browser's clock.
  const local = (day: number, hour: number, minute = 0) => new Date(2026, 10, day, hour, minute);

  it("writes fixed times, an interval or none", () => {
    expect(scheduleText({ type: "times", times: ["09:30", "21:30"] }, "en")).toBe(
      "At 09:30 and 21:30",
    );
    expect(scheduleText({ type: "times", times: ["08:00", "14:00", "20:00"] }, "pt")).toBe(
      "Às 08:00, 14:00 e 20:00",
    );
    expect(scheduleText({ type: "times", times: ["09:30"] }, "pt")).toBe("Às 09:30");
    expect(scheduleText({ type: "interval", hours: 8 }, "en")).toBe("Every 8 h");
    expect(scheduleText({ type: "interval", hours: 6.5 }, "pt")).toBe("A cada 6 h 30 min");
    expect(scheduleText({ type: "none" }, "en")).toBe("No schedule");
    expect(scheduleText({ type: "none" }, "pt")).toBe("Sem horário");
  });

  it("writes the next dose today, tomorrow or on a later day", () => {
    const now = local(27, 14);
    expect(nextDoseText(local(27, 21, 30), now, "en")).toBe("Next 21:30");
    expect(nextDoseText(local(27, 15), now, "pt")).toBe("Próxima 15:00");
    expect(nextDoseText(local(28, 9, 30), now, "en")).toBe("Next tomorrow 09:30");
    expect(nextDoseText(local(28, 9, 30), now, "pt")).toBe("Próxima amanhã 09:30");
    expect(nextDoseText(local(29, 9, 30), now, "en")).toBe("Next Sun 09:30");
    expect(nextDoseText(local(29, 9, 30), now, "pt")).toBe("Próxima domingo 09:30");
  });

  it("writes since when a dose is due", () => {
    expect(t("en", "due_since", { time: "09:30" })).toBe("since 09:30");
    expect(t("pt", "due_since", { time: "09:30" })).toBe("desde 09:30");
  });
});
