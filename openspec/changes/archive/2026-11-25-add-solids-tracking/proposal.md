# Proposal

## Why

Around six months a baby starts eating solid food, and parents want to note each meal, and above all what was eaten, to introduce foods one at a time and to trace a reaction back to a meal. Nothing in the existing trackers records a meal.

## What Changes

- A new tracker the user can enable per baby: solids.
- A service to log a meal with a note of what was eaten, and a one-tap button that logs a meal without a note. The note is added or edited afterwards in the calendar.
- Sensors for the last meal, with its note, and for the number of meals today.
- The "last feed" sensor is unchanged: it continues to cover breastfeeding and bottles only.

Depends on `add-core-tracking` and `add-calendar-view` being implemented and archived first; without the calendar there would be no practical way to write what was eaten.

Out of scope: a food list, allergen tracking, quantities.

## Capabilities

### New Capabilities

- `solids-tracking`: logging solid food meals and the sensors derived from them.

### Modified Capabilities

None.

## Impact

- `custom_components/baby_calendar/`: one tracker module, a service, entities, translations, a calendar title. The tracker list in the baby flow gains one entry.
- No schema migration, no new dependencies, no network access.
