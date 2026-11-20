# Proposal

## Why

Parents record a baby's weight and length at every check-up and weigh-in, and take the temperature several times a day when the baby is ill. These are values, not counts: what matters is the latest reading and how it evolves over weeks. The existing trackers only count events and sum amounts per day, so there is nowhere to keep these readings next to the rest of the baby's record.

## What Changes

- Three new trackers the user can enable per baby: weight (grams), length (centimetres) and temperature (degrees Celsius).
- A service per measurement to log a reading, with optional notes and time, and a number input plus a button to do the same from a dashboard.
- Per measurement, a sensor holding the latest reading and a timestamp sensor for when it was taken. Weight and length are recorded in long-term statistics so growth can be charted over months. The temperature sensor goes blank 24 hours after the reading, so an old fever is never mistaken for a current one.
- Readings outside a plausible range are rejected, to catch typing mistakes such as kilograms instead of grams. The dashboard input returns to zero after each reading, so a stray press never logs a stale value.
- Readings are corrected, deleted and listed through the existing event services.

Depends on `add-core-tracking` being implemented and archived first. If `add-calendar-view` is in place, readings appear in the calendar with their value and unit.

Out of scope: head circumference, growth percentiles or curves, fever alerts or any interpretation of a reading, units other than grams, centimetres and degrees Celsius.

## Capabilities

### New Capabilities

- `measurement-tracking`: logging weight, length and temperature readings and the sensors that report the latest reading.

### Modified Capabilities

None.

## Impact

- `custom_components/baby_calendar/`: three tracker modules, services, entities, translations. The tracker list in the baby flow gains three entries.
- No schema migration: a reading is stored in the existing `amount` column.
- No new dependencies. No network access.
