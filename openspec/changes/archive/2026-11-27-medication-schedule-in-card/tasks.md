# Tasks

## 1. Data

- [x] 1.1 Add each active medication's `schedule` (`type`, and `times` or `hours`) to the `baby_calendar/subscribe_babies` payload and to `Medication` in `frontend/src/types.ts`; cover it in `tests/test_websocket.py` and run `pytest tests/test_websocket.py`

## 2. Card

- [x] 2.1 Add `scheduleText` and `nextDoseText` to `frontend/src/format.ts`, with the English and Portuguese texts in `i18n.ts`: fixed times joined as "09:30 and 21:30", an interval with `duration`, "tomorrow" and the short weekday for later days; cover each spec scenario's text in Vitest
- [x] 2.2 Show the schedule and the next dose under each medication's name in `medication.ts`, and "since HH:MM" next to "Due" for a due dose; rebuild the bundle
- [x] 2.3 e2e: a mocked medication with fixed times and a next dose sensor, one with an interval, and one without a schedule; check the texts in Portuguese, and that a due dose shows "desde"; run `tsc`, Vitest and e2e
- [x] 2.4 README: the Medications card row mentions the schedule and the next dose
- [x] 2.5 Run `openspec validate medication-schedule-in-card --strict`

## 3. Real instance

- [x] 3.1 After the merge, install through the Marketplace and restart; check in Chrome that the Medicamentos page of the Teste dashboard shows each medication's schedule and next dose, matching its next dose sensor

## Workflow follow-up

- Archive the change with `openspec archive medication-schedule-in-card --yes`, in its own PR.
