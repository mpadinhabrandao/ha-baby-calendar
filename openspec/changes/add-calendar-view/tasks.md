# Tasks

## 1. Presentation

- [ ] 1.1 Add `summary` to the diaper, bottle, breastfeeding and sleep modules and the `en` and `pt` title strings per design C2 and C3; verify with unit tests for the dirty diaper, the bottle in Portuguese, the sleep duration, a breastfeeding entry with and without a side, and an in-progress event
- [ ] 1.2 Implement the duration formatter; verify with unit tests for under an hour, exact hours and hours with minutes

## 2. Calendar entity

- [ ] 2.1 Implement the `calendar` platform with one entity per baby and `async_get_events` per design C1 and C4; verify with tests for all trackers in one calendar, two babies, a week three months in the past, a disabled tracker's events, a finished sleep, a sleep in progress, a diaper change block, a sleep overlapping the start of the requested range, tomorrow being empty, and a description that is the note or empty
- [ ] 2.2 Implement `async_update_event` per design C5; verify with tests for a diaper moved, a sleep end corrected, a move into the future, a note added, two paragraphs, a note removed, a note added to a running sleep leaving the timer running, a title edited, an untouched save being a no-op, an `rrule` and an all-day value
- [ ] 2.3 Implement `async_delete_event`, the refresh after any store write and the entity state per design C6; verify with tests that deleting in the calendar updates the sensors, that an event logged by button appears without a reload, that the entity is on during a timer and stays off after a diaper change
- [ ] 2.4 Verify with a test that the entity does not advertise event creation

## 3. Integration checks

- [ ] 3.1 On a real instance, open the baby's calendar in the calendar panel and in a calendar card; verify titles, emoji and durations in day, week and list views, in English and in Portuguese, and that both offer Edit and Delete and neither offers adding an event
- [ ] 3.2 Load a year of generated events into a test instance and verify the month view opens without noticeable delay
- [ ] 3.3 From the calendar on a phone, change an event's time, add a note to a running sleep and delete another event; verify the sensors and `list_events` agree and the sleep timer is still running
- [ ] 3.4 Document the calendar in `README.md` with an example calendar card, the list of emoji, what can be edited and that notes are written here; verify the example card loads on a real instance
- [ ] 3.5 Run `openspec validate add-calendar-view --strict` and verify it passes

## Workflow follow-up

- Archive the change after review, then confirm `openspec/specs/` contains `calendar-view` with its Purpose section filled in.
