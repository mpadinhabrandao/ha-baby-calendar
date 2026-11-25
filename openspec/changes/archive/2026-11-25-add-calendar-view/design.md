# Design

## Context

Builds on `add-core-tracking` and `add-timed-tracking`. The event store already answers "events of a baby overlapping a period" (used by `list_events`), which is what a Home Assistant calendar entity is asked for. This change is mostly presentation.

Revised after an independent review: the description is now the notes only (reading notes back out of a mixed description was fragile), editing never ends a running timer, and the entity state ignores instantaneous events.

## Goals / Non-Goals

**Goals:**

- The calendar is a view over the event store with no state of its own.
- Edits made in the calendar go through the same validation as `update_event` and `delete_event`.

**Non-Goals:**

- Exposing the calendar outside Home Assistant, recurrence, all-day events, creating events.

## Decisions

### C1. One `CalendarEntity` per config entry

A `calendar` platform creates one entity per baby, key `calendar`, unique id `<baby_id>_calendar`, attached to the baby's device, independent of which trackers are enabled.

`async_get_events(hass, start, end)` runs the store's overlap query for that baby and maps each row to a `CalendarEvent` with `uid` set to the event id. `list_events` and the calendar use the same query, so they always agree.

### C2. Presentation belongs to the tracker modules

Each tracker module gains `summary(event, language) -> str`. The calendar calls it and adds nothing itself, so a tracker added later brings its own.

| Tracker | Emoji | Title text |
|---|---|---|
| diaper | 💧 wet, 💩 dirty, 💧💩 both | content, stool type in brackets |
| bottle | 🍼 | amount in ml, then content when set |
| breastfeeding | 🤱 | side when set, then duration |
| sleep | 😴 | duration |

Durations are formatted as `45 min` or `1 h 20 min`. An in-progress event shows the translated "in progress" instead.

All details go in the title, so the description can be the notes alone. The calendar event's `location` is left empty.

### C3. Strings for titles are kept in Python

Titles are built in the backend, where `strings.json` categories do not cover free-form text. `calendar_strings.py` holds the `en` and `pt` fragments, selected by `hass.config.language` with English as fallback. Option labels shown in titles use the same wording as the entities. Titles therefore follow the instance language, not each user's profile language; that is accepted.

### C4. Placement in time

- Timed, finished: `start_ts` to `end_ts`.
- Timed, in progress: `start_ts` to now, rounded up to the next minute.
- Instantaneous: `start_ts` to `start_ts + 5 minutes`. Home Assistant requires an end later than the start.

All events are timed (`datetime`), never all-day.

### C5. Supported features: update and delete only

`supported_features = UPDATE_EVENT | DELETE_EVENT`. The frontend gates its "add event" button on `CREATE_EVENT`, its Edit action on `UPDATE_EVENT` and Delete on `DELETE_EVENT` (checked in the frontend source), so this calendar offers edit and delete and no add. Editing a time is done in the event dialog; the stock calendar has no drag and drop. The dashboard calendar card renders the same `ha-full-calendar` component as the calendar panel and passes it nothing that disables this (checked in the frontend source on 2026-11-16), so events can be edited and deleted from a dashboard card as well as from the panel.

`async_update_event(uid, event, recurrence_id=None, recurrence_range=None)` receives the full event from the editor (summary, description, location, rrule, dtstart, dtend) and:

- rejects an `rrule` or an all-day value with `HomeAssistantError`;
- maps `dtstart` to the start;
- maps `dtend` to the end only for a finished timed event; for an instantaneous or in-progress event `dtend` is ignored;
- maps `description` to the notes verbatim, an empty or missing description clearing them;
- ignores `summary` and `location`;
- skips fields that did not change, so saving the dialog untouched is a no-op;
- then calls the same internal update path as `baby_calendar.update_event`.

`async_delete_event` calls the same internal path as `baby_calendar.delete_event`.

After any store write, from any source, the calendar entity writes its state so that open calendar views, which subscribe to the entity, refresh.

### C6. Entity state

`event` (the property behind the state) returns the baby's in-progress timed event if there is one, else `None`. The entity is therefore on only while a timer runs. Instantaneous events never become the "current event", which avoids scheduling a state write five minutes after each one.

## Risks / Trade-offs

- [A day with forty short events is crowded in the month view] → Inherent to the data. The week and day views and the list card handle it; the README recommends them.
- [Emoji render differently, or not at all, on some wall tablets] → Accepted. The text after the emoji is sufficient on its own.
- [Notes can only be typed in the calendar dialog, a few taps away from the dashboard] → Chosen, to keep the dashboard to one-tap logging.
- [Wide ranges, such as a year in a list card, load many rows] → The range query is indexed; a year of intensive logging is in the low tens of thousands of rows. Measured in task 3.2.
