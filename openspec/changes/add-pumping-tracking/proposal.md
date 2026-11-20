# Proposal

## Why

A parent who expresses milk wants to know how much was pumped in each session and over the day, to judge supply and plan bottles. It is a record about the parent rather than the baby, but it belongs with the feeding record and nothing in the existing trackers holds it.

## What Changes

- A new tracker the user can enable per baby: pumping.
- A service to log a session with the amount in ml and, optionally, the side (left, right or both).
- A number input for the amount, a side selector and a button to log a session from a dashboard. Because the amount differs every session, both inputs return to their empty value after each entry.
- Sensors for the last session and for today's sessions and total ml.

Depends on `add-core-tracking` being implemented and archived first. If `add-calendar-view` is in place, sessions appear in the calendar.

Out of scope: session duration, a milk stock or freezer inventory, linking pumped milk to bottles.

## Capabilities

### New Capabilities

- `pumping-tracking`: logging milk pumping sessions and the sensors derived from them.

### Modified Capabilities

None.

## Impact

- `custom_components/baby_calendar/`: one tracker module, a service, entities, translations, a calendar title. The tracker list in the baby flow gains one entry.
- No schema migration, no new dependencies, no network access.
