# Tasks

## 1. Medication configuration

- [ ] 1.1 Repeat the subentry harness test from design.md R1 on the development version of Home Assistant (entities on the baby's device without `config_subentry_id`, registry cleanup on removal) and record the outcome; then implement add and edit medication with name, dose text and schedule, as subentries or as the options-flow menu, with `en` and `pt` strings; verify with tests for a medication added, a duplicate name, fixed times with no time, an invalid time and an interval of zero
- [ ] 1.2 Implement deactivate, reactivate and remove; verify with tests that deactivating keeps doses and removes entities, reactivating restores them, removing keeps the doses listed under the medication's name, and a new medication with the same name starts with no doses
- [ ] 1.3 Document managing medications in `README.md`, including that neither removal nor deactivation deletes history; verify the steps match the UI on a real instance

## 2. Doses

- [ ] 2.1 Register the medication tracker and implement `baby_calendar.log_medication` with `services.yaml` selectors and translations per design R2 and R3; verify with tests for a dose given earlier with a note, an unknown medication, a deactivated medication and a rename that keeps doses listed under the new name
- [ ] 2.2 Implement the per-medication button and the `last_dose` and `doses_today` sensors, created and removed with the medication without reloading Home Assistant; verify with tests for a dose by button, a back-dated dose with `minutes_ago`, a dose undone, the doses today count, a deleted dose and two doses close together raising no warning
- [ ] 2.3 Add the calendar `summary` for doses ("💊" and the medication name, current or stored) per design R2; verify with unit tests for an active, a renamed and a removed medication
- [ ] 2.4 Document the service and entities with examples in `README.md`; verify each example runs as written on a real instance

## 3. Schedules and due state

- [ ] 3.1 Implement the pure due computation per design R4; verify with unit tests for every scenario of the dose matching, fixed times and interval requirements, including given early, logged twice, given after midnight, still due after midnight, superseded by the next time, never given, and a scheduled time inside a daylight saving gap and inside a repeated hour
- [ ] 3.2 Implement the scheduler per design R5 and the `due` binary sensor and `next_dose` sensor; verify with tests using a frozen clock for time reached, dose recorded while due, dose deleted, overdue, the due sensor's attributes, and a medication with no schedule having neither entity

## 4. Reminders

- [ ] 4.1 Verify with tests that the due state is recomputed at startup: Home Assistant down at dose time, and a restart while a dose is due
- [ ] 4.2 Write the reminder blueprint per design R6; verify on a real instance that an automation created from it notifies a phone when a dose becomes due, repeats until the dose is recorded, and receives the baby name, medication name and dose text
- [ ] 4.3 Document reminders in `README.md`, leading with the blueprint import link and stating that the integration sends no notifications itself; verify the import link works on a real instance

## 5. Integration checks

- [ ] 5.1 On a real instance, add a fixed-times medication and an interval medication, each with an automation from the blueprint; verify both reminders arrive and stop once a dose is recorded
- [ ] 5.2 Restart Home Assistant while a dose is due and verify the due sensor is on after start
- [ ] 5.3 Verify that the other trackers and their existing events behave exactly as before
- [ ] 5.4 Run `openspec validate add-medication-reminders --strict` and verify it passes

## Workflow follow-up

- Archive the change after review, then confirm `openspec/specs/` contains `medication-tracking` and `medication-reminders` with their Purpose sections filled in.
