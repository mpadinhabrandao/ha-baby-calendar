# Design

## Context

A small addition on top of `add-core-tracking`, using the tracker registry (core D4) and the shared dashboard logging path (core D8). If `add-calendar-view` is archived, the module also provides the calendar `summary` (calendar C2). No new mechanism is introduced.

## Goals / Non-Goals

**Goals:** one more tracker module, with nothing changed elsewhere.

**Non-Goals:** timing a session, stock of expressed milk.

## Decisions

### P1. One tracker module

`trackers/pumping.py` registers the key `pumping`. The amount is stored in `amount` and the side in `kind`.

Service: `baby_calendar.log_pumping` (`amount`, `side`, `notes`, `time`, required `device_id`), returning the event id when a response is requested.

Entities: `number` `pumping_amount` (ml, box, 0 to 500, step 1), `select` `pumping_side` (not specified, left, right, both), `button` `pumping_log`; `sensor` `pumping_last` (timestamp, attributes `event_id`, `amount`, `side`), `pumping_count_today` and `pumping_ml_today` (daily, `state_class: total` as in core D9).

Calendar `summary`: "🧴", the translated tracker name, the amount and the side when set.

### P2. One-shot inputs

Unlike the bottle inputs, which keep the usual bottle, the pumping amount and side are reset by the shared dashboard path after each press and are not restored after a restart. A pumped amount is different every session, so a kept value would only ever be logged by mistake; with the amount back at zero, a second press fails instead.

## Risks / Trade-offs

- [The pumping tracker belongs to a baby although it describes the parent, which is awkward with twins] → Accepted. With several babies the user enables it on one of them.
