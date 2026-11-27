# Proposal

## Why

The Medications card shows a medication's name, its dose and "Given", but not when it is taken. The parent has to remember the schedule, or open the medication's settings, to know when the next dose is.

## What Changes

- Under each medication's name, the Medications card shows its **schedule**:
  - fixed times as "At 09:30 and 21:30" ("Às 09:30 e 21:30");
  - an interval as "Every 8 h" ("A cada 8 h");
  - "No schedule" ("Sem horário") when there is none.
- Next to it, the card shows the **next dose**, read from the medication's next dose sensor:
  - "Next 21:30" today, "Next tomorrow 09:30" tomorrow, and the weekday further ahead ("Next Sat 09:30");
  - for a dose due now, the time it has been due since ("since 09:30") next to the existing "Due" label;
  - nothing when there is no next dose: no schedule, or an interval with no dose recorded yet.
- The `baby_calendar/subscribe_babies` WebSocket payload gains each active medication's `schedule`, as stored in the options (`type`, `times` or `hours`).
- README: the Medications card row mentions the schedule and the next dose.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `baby-cards`: a new requirement for the Medications card to show each medication's schedule and next dose; the existing Medications card requirement is unchanged.

## Impact

- `custom_components/baby_calendar/websocket.py`: `schedule` in each medication; `tests/test_websocket.py`.
- `frontend/src/cards/medication.ts`, `frontend/src/format.ts` (schedule and next dose text, with Vitest tests), `frontend/src/i18n.ts`, `frontend/src/types.ts`, `frontend/src/base.ts` (one line of style).
- `frontend/e2e/run.mjs`: Medications checks with a schedule and a next dose.
- The rebuilt bundle `custom_components/baby_calendar/frontend/baby-calendar-cards.js`.
- `README.md`.
- No change to the schedule rules, the sensors or the services.
