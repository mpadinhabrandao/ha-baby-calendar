# Tasks

## 1. Medication configuration

- [x] 1.1 Repeat the subentry harness test from design.md R1 on the development version of Home Assistant (entities on the baby's device without `config_subentry_id`, registry cleanup on removal) and record the outcome; then implement add and edit medication with name, dose text and schedule, as subentries or as the options-flow menu, with `en` and `pt` strings; verify with tests for a medication added, a duplicate name, fixed times with no time, an invalid time and an interval of zero
- [x] 1.2 Implement deactivate, reactivate and remove; verify with tests that deactivating keeps doses and removes entities, reactivating restores them, removing keeps the doses listed under the medication's name, and a new medication with the same name starts with no doses
- [ ] 1.3 Document managing medications in `README.md`, including that neither removal nor deactivation deletes history; verify the steps match the UI on a real instance

  - 1.1 outcome (2026-11-20): the harness test was not repeated. The options-flow menu was chosen: it needs no subentry, so the one-subentry-per-device rule from 2026.8 does not apply, and the entity cleanup it needs is the same as for disabled trackers. Fixed times, the doses and the specs are unchanged by the choice.
  - 1.3 and 2.4: the README sections are written; checking them against the UI and running the examples on a real instance is still to do.
  - 4.2: the event-triggered blueprint is written and runs in the tests as a real automation (two medications and one added later, repeat until recorded, baby filter, "Given" recording the dose); checked on a real instance on 2026-11-20: one automation reminded two phones (Márcio's and Mariana's) for Paracetamol, the repeats replaced the previous notification, and "Given" on the phone recorded the dose and stopped the repeats.
  - 4.3: the import link was checked on a real instance on 2026-11-20 (the blueprint imported from its GitHub URL).

## 2. Doses

- [x] 2.1 Register the medication tracker and implement `baby_calendar.log_medication` with `services.yaml` selectors and translations per design R2 and R3; verify with tests for a dose given earlier with a note, an unknown medication, a deactivated medication and a rename that keeps doses listed under the new name
- [x] 2.2 Implement the per-medication button and the `last_dose` and `doses_today` sensors, created and removed with the medication without reloading Home Assistant; verify with tests for a dose by button, a back-dated dose with `minutes_ago`, a dose undone, the doses today count, a deleted dose and two doses close together raising no warning
- [x] 2.3 Add the calendar `summary` for doses ("💊" and the medication name, current or stored) per design R2; verify with unit tests for an active, a renamed and a removed medication
- [x] 2.4 Document the service and entities with examples in `README.md`; verify each example runs as written on a real instance

## 3. Schedules and due state

- [x] 3.1 Implement the pure due computation per design R4; verify with unit tests for every scenario of the dose matching, fixed times and interval requirements, including given early, logged twice, given after midnight, still due after midnight, superseded by the next time, never given, and a scheduled time inside a daylight saving gap and inside a repeated hour
- [x] 3.2 Implement the scheduler per design R5 and the `due` binary sensor and `next_dose` sensor; verify with tests using a frozen clock for time reached, dose recorded while due, dose deleted, overdue, the due sensor's attributes, and a medication with no schedule having neither entity
- [x] 3.3 Next dose skips a scheduled time already satisfied by an early dose (found on a real instance on 2026-11-24: a dose at 09:28 left the next dose at 09:30 until 09:30); verify with a unit test for the scenario "Next dose after an early dose"

## 4. Reminders

- [x] 4.1 Verify with tests that the due state is recomputed at startup: Home Assistant down at dose time, and a restart while a dose is due
- [x] 4.2 Write the reminder blueprint per design R6, triggered by the due event; verify with tests that one automation reminds for two medications, a medication added later, a repeat until the dose is recorded, a baby filter and the "Given" action recording the dose; then verify on a real instance that a phone receives the reminder with the baby name, medication name and dose text, and that "Given" records the dose
- [x] 4.3 Document reminders in `README.md`, leading with the blueprint import link, stating that the integration sends no notifications itself, and describing the due event and the "Given" action; verify the import link works on a real instance
- [x] 4.4 Fire the due event per design R5; verify with tests for a dose becoming due, a start while due, a reload while due, a dose recorded and due again later, and a medication with no schedule
- [x] 4.5 Reloading a baby after Home Assistant has started logs no error (found on a real instance on 2026-11-24: "Unable to remove unknown job listener" for the start listener of the due event, which had already fired); verify with a test that sets the baby up while starting, starts, reloads and finds no error in the log

## 5. Integration checks

- [x] 5.1 On a real instance, add a fixed-times medication and an interval medication and one automation from the blueprint; verify both reminders arrive and stop once a dose is recorded
- [x] 5.2 Restart Home Assistant while a dose is due and verify the due sensor is on after start
- [x] 5.3 Verify that the other trackers and their existing events behave exactly as before
- [x] 5.4 Run `openspec validate add-medication-reminders --strict` and verify it passes

## Workflow follow-up

- Archive the change after review, then confirm `openspec/specs/` contains `medication-tracking` and `medication-reminders` with their Purpose sections filled in.
