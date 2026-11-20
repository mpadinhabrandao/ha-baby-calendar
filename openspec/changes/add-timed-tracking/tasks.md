# Tasks

## 1. Shared timer logic

- [ ] 1.1 Implement store operations for start (with the one-running check in the same transaction), stop, get running event and the overlap query per design T2 and T5; verify with unit tests for start, double start, stop, stop with nothing running, end before start and events overlapping a range at either edge
- [ ] 1.2 Implement the shared timed-tracker base (start, stop, log by duration, last event, count by start day, duration split at midnight with a running event counted to now, the one-minute recompute while running) per design T1 and T5; verify with tests using a frozen clock for two finished events, the 23:00 to 06:00 sleep, the 18:00 to 01:00 sleep, a still-running timer advancing, the count for a sleep started before midnight, logged afterwards with and without a start time, and a missing or zero duration
- [ ] 1.3 Extend `update_event` with `end_time` and the in-progress rule, and `list_events` with `end`, `duration`, `in_progress` and overlap; verify with tests for a corrected end, an invalid end, the start of a running timer corrected, `end_time` rejected on a running timer, and a listing that returns a sleep overlapping the start of the period
- [ ] 1.4 Stop a running timer when its tracker is disabled; verify with a test that the event is finished at that moment
- [ ] 1.5 Verify with a test that a running timer survives closing and reopening the store and an integration reload, and that undo deletes a timer started by mistake

## 2. Breastfeeding tracker

- [ ] 2.1 Register the breastfeeding tracker and add it to the tracker list in the baby flows with `en` and `pt` strings; verify with a test that enabling it creates its entities
- [ ] 2.2 Implement `start_breastfeeding`, `stop_breastfeeding` and `log_breastfeeding` with `services.yaml` selectors and translations per design T3; verify with tests for started on the left, started late, already running, invalid side, side omitted and stop with an earlier end
- [ ] 2.3 Implement the switch, side select, duration number and button through the shared dashboard path per design T4; verify with tests for the selection used by the switch and by the button, started ten minutes ago, forgot to stop, the duration input returning to zero, a press with the duration at zero, and a press while the timer is running
- [ ] 2.4 Implement the selector flip and the feed grouping per design T6 and T7; verify with tests for after a left feed, an entry with no side, both sides in one sitting counting one feed, two separate feeds, and a feed whose first entry started before midnight
- [ ] 2.5 Implement the breastfeeding sensors; verify with tests for the in-progress and finished attributes, the last side and the daily duration for left then right
- [ ] 2.6 Document the breastfeeding services and entities with examples in `README.md`, including how a side change is logged and how feeds are counted; verify each example runs as written on a real instance

## 3. Sleep tracker and feeding summary

- [ ] 3.1 Register the sleep tracker, add it to the tracker list, and implement `start_sleep`, `stop_sleep` and `log_sleep`; verify with tests for a nap timed with the services, logged afterwards and two trackers running at once
- [ ] 3.2 Implement the sleep switch, duration number, button and sensors including `awake_since`; verify with tests for a nap timed with the switch, the switch following a start by service, the switch staying off when a sleep is logged afterwards, awake since after a nap and while asleep
- [ ] 3.3 Implement the `last_feed` sensor per design T4; verify with tests for a bottle after a breastfeed, only bottles enabled, only breastfeeding enabled and no feeds
- [ ] 3.4 Document the sleep services and entities and the last feed sensor in `README.md`, with an example automation using the sleep switch and the note that daily sleep is split at midnight; verify each example runs as written on a real instance

## 4. Integration checks

- [ ] 4.1 On a real instance, enable breastfeeding and sleep on an existing baby, run a left then right feed with the switch, log a third feed with the duration input and button, and verify three entries, two feeds, the daily duration and the side selector
- [ ] 4.2 Start a sleep timer in the evening, leave it over midnight, stop it in the morning and verify both days' durations in the sensors and in the statistics graph
- [ ] 4.3 Start a timer, restart Home Assistant and verify the switch is still on with the original start time; check the recorder for the number of state rows written per hour by a running timer
- [ ] 4.4 Verify that the diaper and bottle trackers and their existing events behave exactly as before
- [ ] 4.5 Run `openspec validate add-timed-tracking --strict` and verify it passes

## Workflow follow-up

- Archive the change after review, then confirm `openspec/specs/` contains `timers`, `breastfeeding-tracking` and `sleep-tracking` with their Purpose sections filled in.
