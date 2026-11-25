# Design

## Context

Builds on `add-core-tracking` (its design.md, D1 to D10, still applies). Revised after an independent review: the temperature sensor expires, the dashboard input is one-shot, steps match real scales, and the limits of long-term statistics for back-dated readings are stated. The three measurements plug into the tracker registry (D4) and reuse the store, the baby resolution, the time rules and the correction, deletion and listing services unchanged.

## Goals / Non-Goals

**Goals:**

- One measurement implementation parameterised by unit, range and precision, registered three times.
- Sensors that chart well over months with the stock statistics graph.

**Non-Goals:**

- Unit conversion, percentiles, WHO growth curves.
- Daily values: a measurement has no "today" total.

## Decisions

### M1. One parameterised tracker class

`trackers/measurement.py` defines a measurement tracker from a small description, and registers three instances:

| Key | Unit | Device class | Range | Step |
|---|---|---|---|---|
| `weight` | g | `weight` | 300 to 30000 | 1 |
| `length` | cm | `distance` | 20 to 130 | 0.5 |
| `temperature` | °C | `temperature` | 30.0 to 45.0 | 0.1 |

Adding head circumference later is one more row. The reading is stored in the event's `amount` column; `kind` and `data` are unused.

### M2. Services

`baby_calendar.log_weight`, `log_length` and `log_temperature`, each with `value`, `notes`, `time` and the required `device_id`, returning the event id when a response is requested. One service per measurement, following D5, so each has its own unit and range in the selector. `update_event` accepts `value` in `fields` for measurement events and re-validates the range.

### M3. Entities

Per enabled measurement: `number` `<key>_value`, `button` `<key>_log`, `sensor` `<key>` (the latest reading) and `sensor` `<key>_last` (timestamp, with `event_id` and `value` attributes, consistent with the other trackers).

The number is box mode, from 0 to the upper bound of the range, with the step above, and is not restored: it is a one-shot input like `minutes_ago`, set back to 0 by the shared dashboard path (core D8) after each press. Zero is below every range, so an untouched press fails validation instead of logging a default.

The weight and length sensors use `state_class: measurement` with their device class and unit; long-term statistics then keep hourly mean, min and max. The sensor documentation allows `measurement` for these device classes. Statistics are compiled from the sensor's live state, which has two consequences stated in the spec and the README: a reading logged with a past time, or corrected later, is not charted at its event time; and a mistaken reading that was the state for an hour stays in that hour's statistics even after it is deleted.

The temperature sensor also uses `measurement`, but the tracker schedules a state write for `start_ts + 24 hours` of the latest reading, after which the state is `None`. With no state there is nothing to chart, so a single fever reading does not become a flat line for weeks.

Suggested display precision: 0 for weight, 1 for length and temperature.

### M4. Latest means latest by event time

The value sensor shows the reading with the greatest `start_ts`, not the most recently inserted one, so entering old check-up values does not overwrite the current reading. It is the same "last event" query the other trackers use.

### M5. Home Assistant unit conversion

Because the sensors have a device class, Home Assistant may display them converted to the user's unit system (for example Fahrenheit, or pounds). That is display only: services, the number inputs and stored values stay in grams, centimetres and degrees Celsius.

### M6. Calendar titles

The measurement module provides the calendar `summary` (calendar C2): "⚖️", "📏" or "🌡️" followed by the value and unit, for example "⚖️ 3450 g". This applies when `add-calendar-view` is archived, which the planned order guarantees.

## Risks / Trade-offs

- [A value typed in the wrong unit but inside the range, such as 345 g instead of 3450 g, is accepted] → The range only catches gross errors. The sensor shows the value immediately, and `update_event` corrects it.
- [A weight reading stays the sensor state for weeks] → Intended. Tested in the harness described in core D9: a `measurement` sensor that does not change keeps producing an hourly statistics row with the same value, so the chart is a step line between readings. A sensor set to unknown stops producing rows, which is what makes the temperature expiry work.
- [Back-dated and corrected readings are missing or wrong in the long-term chart] → Stated in the spec. The event log and the calendar are always right; importing statistics from the store is a possible later change.
- [Users on imperial units see converted sensors but must enter metric values] → Documented. Imperial input is out of scope.
