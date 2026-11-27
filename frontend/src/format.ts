// Pure text helpers: durations, clocks and the last feed line.

import { type Language, t } from "./i18n";
import type { FeedEntry, Schedule } from "./types";

const MINUTE = 60;
const HOUR = 3600;

/** Minutes as "12 min", hours as "2 h 10 min". */
export function duration(seconds: number): string {
  const minutes = Math.max(0, Math.round(seconds / MINUTE));
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours} h ${rest} min` : `${hours} h`;
}

/** A running time as "12:40", or "1:20:00" from an hour. */
export function clock(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(total / HOUR);
  const minutes = Math.floor((total % HOUR) / MINUTE);
  const secs = total % MINUTE;
  const two = (n: number) => String(n).padStart(2, "0");
  return hours ? `${hours}:${two(minutes)}:${two(secs)}` : `${two(minutes)}:${two(secs)}`;
}

/** The local time of day, "03:12". */
export function timeOfDay(when: Date, language: Language): string {
  return when.toLocaleTimeString(language === "pt" ? "pt-PT" : "en-GB", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** A medication's schedule: "At 09:30 and 21:30", "Every 8 h", "No schedule". */
export function scheduleText(schedule: Schedule, language: Language): string {
  if (schedule.type === "times" && schedule.times?.length) {
    const times = schedule.times;
    const joined =
      times.length === 1
        ? times[0]
        : `${times.slice(0, -1).join(", ")} ${t(language, "and")} ${times[times.length - 1]}`;
    return t(language, "schedule_times", { times: joined });
  }
  if (schedule.type === "interval" && schedule.hours) {
    return t(language, "schedule_interval", { duration: duration(schedule.hours * HOUR) });
  }
  return t(language, "schedule_none");
}

/** The next dose: "Next 21:30", "Next tomorrow 09:30", "Next Sat 09:30". */
export function nextDoseText(next: Date, now: Date, language: Language): string {
  const time = timeOfDay(next, language);
  const day = (when: Date) => new Date(when.getFullYear(), when.getMonth(), when.getDate());
  const days = Math.round((day(next).getTime() - day(now).getTime()) / (24 * HOUR * 1000));
  let when = time;
  if (days === 1) when = `${t(language, "tomorrow")} ${time}`;
  else if (days > 1) {
    const weekday = next.toLocaleDateString(language === "pt" ? "pt-PT" : "en-GB", {
      weekday: "short",
    });
    when = `${weekday} ${time}`;
  }
  return t(language, "next_dose", { when });
}

/** "2 h 10 min ago" / "há 2 h 10 min". */
export function ago(since: Date, now: Date, language: Language): string {
  return t(language, "ago", { duration: duration((now.getTime() - since.getTime()) / 1000) });
}

function sideLabel(side: string | null, language: Language): string {
  if (side === "left") return t(language, "left");
  if (side === "right") return t(language, "right");
  return t(language, "side_none");
}

export interface FeedText {
  heading: string;
  line: string;
}

/**
 * The last feed as it happened: each side with its duration, the pauses
 * between them, and the time spent feeding when there is more than one
 * entry. A running feed has no total.
 */
export function feedText(feed: FeedEntry[], now: Date, language: Language): FeedText | null {
  if (!feed.length) return null;
  const start = new Date(feed[0].start);
  const running = feed[feed.length - 1].end === null;
  const parts: string[] = [];
  let feeding = 0;
  feed.forEach((entry, index) => {
    if (index > 0) {
      const previousEnd = new Date(feed[index - 1].end ?? feed[index - 1].start);
      const gap = (new Date(entry.start).getTime() - previousEnd.getTime()) / 1000;
      if (gap >= MINUTE) parts.push(t(language, "pause", { duration: duration(gap) }));
    }
    const side = sideLabel(entry.side, language);
    if (entry.end === null) {
      parts.push(`${side} ${t(language, "running")}`);
      return;
    }
    const seconds = (new Date(entry.end).getTime() - new Date(entry.start).getTime()) / 1000;
    feeding += seconds;
    parts.push(`${side} ${duration(seconds)}`);
  });
  if (feed.length > 1 && !running) {
    parts.push(t(language, "total", { duration: duration(feeding) }));
  }
  const time = timeOfDay(start, language);
  const heading = running
    ? t(language, "feeding_since", { time })
    : t(language, "last_feed", { time, ago: ago(start, now, language) });
  return { heading, line: parts.join(" · ") };
}

/** The time a chip sets, as an ISO string, or undefined for "now". */
export function chipTime(minutesAgo: number, now: Date): string | undefined {
  if (!minutesAgo) return undefined;
  return new Date(now.getTime() - minutesAgo * MINUTE * 1000).toISOString();
}

/** Minutes offered by the time chip. */
export const CHIP_MINUTES = [0, 5, 10, 15, 20, 30, 45, 60, 90, 120];
