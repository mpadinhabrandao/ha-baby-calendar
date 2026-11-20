# Design

## Context

Builds on `add-core-tracking` (its design.md, D1 to D10, still applies). That change left `end_ts` in the event table unused for this purpose, and its tracker registry (D4) and dashboard logging path (D8) are how the two new trackers plug in.

Revised after an independent review: daily durations are split at midnight (attributing a whole event to its start day meant a night's sleep never reached any daily sensor), feeds are grouped, the side selector flips, and "last feed" and "awake since" sensors were added.

## Goals / Non-Goals

**Goals:**

- Durations without a schema migration and without changing the existing trackers.
- A running timer is plain data in the event store, so it survives restarts by construction.
- The timer logic is written once and reused by breastfeeding and sleep.
- Daily durations are correct for sleep that crosses midnight.

**Non-Goals:**

- Pause and resume, automatic stop, resuming a finished entry.
- A live "elapsed" sensor ticking every second.

## Decisions

### T1. Timed trackers are tracker modules with a shared base

`trackers/breastfeeding.py` and `trackers/sleep.py` register like the existing ones. A shared `timed.py` provides start, stop and log-by-duration, the state computation and the common entity descriptions (switch, duration number, button, sensors). Breastfeeding adds the side, stored in `kind`, the feed grouping and the selector flip.

### T2. In-progress means `end_ts IS NULL` on a timed tracker's event

Start inserts a row with `end_ts = NULL`; stop sets it. "At most one running" is enforced in the store inside the same transaction as the insert, which is safe because store access is serialized. Events of non-timed trackers also have `end_ts = NULL` and are never treated as in progress, because the check is scoped to timed trackers.

`update_event` on an in-progress event accepts `time` (start) and rejects `end_time`. When a timed tracker is removed from a baby's enabled list, the options flow handler stops its running timer before the entry reloads.

### T3. Services

- `baby_calendar.start_breastfeeding` (`side`, `notes`, `time`), `stop_breastfeeding` (`time`), `log_breastfeeding` (`duration`, `side`, `notes`, `time`).
- `baby_calendar.start_sleep` (`notes`, `time`), `stop_sleep` (`time`), `log_sleep` (`duration`, `notes`, `time`).

All take the required `device_id` and return the event id when a response is requested. `duration` is a `cv.positive_time_period`. For the log services: with `time`, start is `time` and end is `time + duration`; without, end is now and start is `now - duration`.

`update_event` gains `end_time`. `list_events` adds `end`, `duration` (seconds) and `in_progress` to timed events, and its range query becomes "starts before the range end and ends after the range start, or is still running" for timed trackers.

### T4. Entities

| Tracker | Platform | Keys |
|---|---|---|
| breastfeeding | switch | `breastfeeding_timer` (attribute `started_at`) |
| breastfeeding | select | `breastfeeding_side` (not specified, left, right) |
| breastfeeding | number, button | `breastfeeding_duration` (min), `breastfeeding_log` |
| breastfeeding | sensor | `breastfeeding_last` (timestamp); `breastfeeding_feeds_today`, `breastfeeding_duration_today` |
| sleep | switch | `sleep_timer` (attribute `started_at`) |
| sleep | number, button | `sleep_duration` (min), `sleep_log` |
| sleep | sensor | `sleep_last`, `awake_since` (timestamp); `sleep_count_today`, `sleep_duration_today` |
| breastfeeding or bottle | sensor | `last_feed` (timestamp; attribute `kind`) |

The switch's `is_on` is derived from tracker state. `turn_on`, `turn_off` and the log button go through the shared dashboard path of D8, so they read and reset `minutes_ago`, and failures raise `HomeAssistantError`. The duration number is box mode, minutes, 0 to 1440, step 1, and is not restored: like `minutes_ago` it is a one-shot input, because a feed's length differs every time. The side select is restored.

`*_duration_today` uses `device_class: duration`, native unit minutes, and the daily `state_class: total` of D9. `*_last` carries `ended_at`, `duration` (seconds, absent while in progress), `in_progress` and, for breastfeeding, `side`.

`last_feed` is contributed by a small `feeding_summary` module that is active when either tracker is enabled; it takes the later of the last bottle's `start_ts` and the last breastfeeding entry's `start_ts`.

### T5. Durations are split at midnight

For a day `[d0, d1)`, a tracker's duration is the sum over its events that overlap the day of `min(end, d1) - max(start, d0)`, with `end = now` for a running event. One query selects the overlapping rows (the same predicate as T3's listing) and the clamp is done in Python.

While a timer is running, the state object schedules a recompute every minute so `*_duration_today` advances; the listener is cancelled when the timer stops. At midnight the daily sensors reset and a running event immediately starts contributing to the new day.

- Alternatives rejected: attributing to the start day (a 23:00 to 06:00 sleep finishes after its day's sensor was reset, so its hours appear nowhere) and attributing to the end day (an 18:00 to 01:00 sleep would put seven hours on a day that had one).
- The count is by start day and is not split: a sleep is one sleep.

### T6. Feed grouping

`breastfeeding_feeds_today` is computed by walking today's entries in start order, plus the last entry before midnight, and starting a new feed whenever the gap from the previous entry's end to this entry's start exceeds 30 minutes. A feed belongs to the day of its first entry. An in-progress entry counts. The threshold is a constant, not a setting.

### T7. Side selector flip

When an entry with a side is finished through any path (stop service, switch, log service, log button), the breastfeeding module sets the select to the other side. It does not flip on start, on correction or on undo. Undoing an entry therefore leaves the selector on the flipped side; that is accepted, the selector is visible.

### T8. Undo

`undo` already deletes the most recently created row. Starting a timer creates a row, so undo removes a mistaken start. Stopping a timer updates a row and is not an entry: undo after a stop deletes the whole event if it was created within 15 minutes. That is stated in the README; resuming is out of scope.

## Risks / Trade-offs

- [A state write every minute per running timer adds recorder rows] → One sensor per running timer, only while running. Negligible next to typical installs; measured in task 4.3.
- [A forgotten timer keeps adding to today's duration until corrected] → Chosen behaviour. The switch stays visibly on; turning it off with `minutes_ago`, or `update_event`, fixes it, and the daily value recomputes.
- [Statistics for a past day are not rewritten when a long event is corrected after midnight] → Same rule as the core change: charts reflect the day as it was logged.
- [The 30 minute feed grouping is wrong for cluster feeding, where feeds are minutes apart] → Accepted for the first version. The entries and durations are always exact; only the count is an approximation.
- [`device_class: duration` with `state_class: total` and a daily reset does not chart as expected] → Tested in the harness described in core D9: a sleep split at midnight produced the expected daily `change` on both days. The visual check is task 4.2.
