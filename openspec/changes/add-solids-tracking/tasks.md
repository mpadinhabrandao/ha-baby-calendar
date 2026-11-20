# Tasks

## 1. Solids tracker

- [ ] 1.1 Register the solids tracker and add it to the tracker list in the baby flows with `en` and `pt` strings; verify with a test that enabling it creates its entities
- [ ] 1.2 Implement `baby_calendar.log_solids` and the solids button; verify with tests for a meal with a note, a button press, a back-dated press and an undone press
- [ ] 1.3 Implement the solids sensors and the calendar title; verify with tests for two meals, a note added later showing in the attribute, and the calendar title and description in English and Portuguese
- [ ] 1.4 Document the solids service, entities and how to note what was eaten in `README.md`; verify each example runs as written on a real instance

## 2. Integration checks

- [ ] 2.1 On a real instance, enable solids, log a meal with the button, add what was eaten in the calendar and verify the sensor attribute
- [ ] 2.2 Verify that the other trackers and the last feed sensor behave exactly as before
- [ ] 2.3 Run `openspec validate add-solids-tracking --strict` and verify it passes

## Workflow follow-up

- Archive the change after review, then confirm `openspec/specs/` contains `solids-tracking` with its Purpose section filled in.
