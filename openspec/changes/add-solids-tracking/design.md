# Design

## Context

A small addition on top of `add-core-tracking` and `add-calendar-view`, using the tracker registry (core D4), the shared dashboard logging path (core D8) and the per-tracker calendar `summary` (calendar C2). No new mechanism is introduced.

## Goals / Non-Goals

**Goals:** one more tracker module, with nothing changed elsewhere.

**Non-Goals:** structured food data, quantities, allergen logic.

## Decisions

### S1. One tracker module

`trackers/solids.py` registers the key `solids`. An event uses only `start_ts` and `notes`; `kind`, `amount` and `data` are unused.

Service: `baby_calendar.log_solids` (`notes`, `time`, required `device_id`), returning the event id when a response is requested.

Entities: `button` `solids_log`; `sensor` `solids_last` (timestamp, attributes `event_id` and `notes`) and `solids_count_today` (daily, `state_class: total` as in core D9).

Calendar `summary`: "🥣" and the translated tracker name. What was eaten is the note, shown as the description, where it is also edited.

### S2. No dashboard note field

A text input for "what was eaten" was considered and left out, in line with the decision that notes are written in the calendar. The button therefore records the meal and its time; the food is added in the calendar dialog when the parent has a hand free.

## Risks / Trade-offs

- [Without a note a solids entry says little, and adding it takes a few taps in the calendar] → Accepted for consistency with the other trackers. A dashboard text field is the obvious later addition if this proves too slow in daily use.
