# Tasks

## 1. Scaffolding and statistics spike

- [x] 1.1 Create `custom_components/baby_calendar/` with `manifest.json` (domain, name, version, `config_flow`, `integration_type: device`, `iot_class: local_push`, empty `requirements`) and `const.py`; verify the hassfest GitHub Action passes
- [x] 1.2 Add `hacs.json` with the minimum Home Assistant version set to the release used for development, `LICENSE` (MIT), `.gitignore` and a `README.md` stub; verify the HACS validation action passes
- [x] 1.3 Add `pyproject.toml` with ruff and pytest configuration and `pytest-homeassistant-custom-component` as a dev dependency; verify `pytest` runs and collects zero tests without error
- [x] 1.4 Add GitHub Actions workflows for hassfest, HACS validation, ruff and pytest; verify all four are green on a push
- [ ] 1.5 On a real instance, add a throwaway sensor with `state_class: total` and a daily `last_reset`, leave it over two midnights and open a statistics graph card with `chart_type: bar`, `period: day`, `stat_types: [change]`; verify it shows one bar per day with that day's total, as the harness test in design.md D9 predicts

## 2. Event store

- [x] 2.1 Implement `EventStore` (single locked connection, schema creation for `babies` and `events`, `PRAGMA user_version`, single pre-migration copy, refusal of a newer schema) per design D1 and D2; verify with tests for a fresh file, a reopened file and a file with a newer version
- [x] 2.2 Implement add, get, update, delete, list by baby and period with optional tracker filter, latest by `created_ts`, and the baby operations (create, mark removed, find removed by name, re-attach, purge); verify with unit tests covering each operation, unknown identifiers and ordering
- [x] 2.3 Implement the query helpers used by tracker state (last event by tracker and kinds, count and amount sum for a period); verify with unit tests including an empty store
- [x] 2.4 Implement `backup.py` with pre and post backup hooks per design D1; verify with a test that the store is closed between the hooks and usable after, and that a write issued during a backup completes afterwards

## 3. Baby profile

- [x] 3.1 Implement the config flow (name required, birth date optional, case-insensitive duplicate check, restore-or-start-empty step, tracker multi-select) with `en` and `pt` strings per design D3; verify with tests for success, empty name, duplicate name, one tracker ticked, none ticked, restore and start empty
- [x] 3.2 Implement the options flow to edit name, birth date and enabled trackers; verify with tests that events survive an edit
- [x] 3.3 Implement `async_setup_entry`, `async_unload_entry`, device registration, entity creation for enabled trackers only and removal of registry entries of disabled trackers; verify with tests for enabling a tracker later and for disabling and re-enabling one with its events intact
- [x] 3.4 Implement `async_remove_entry` marking the baby removed, and `baby_calendar.purge_history`; verify with tests that removal keeps events, that purge deletes only removed babies' history and that purge refuses a configured baby
- [ ] 3.5 Document adding a baby, choosing trackers, removal, restoring and purging history in `README.md`; verify the steps match the UI on a real instance

## 4. Shared services, state and dashboard path

- [x] 4.1 Implement the tracker registry and time parsing and validation per design D4 and D6; verify with tests for a tracker not enabled, a missing `device_id`, and omitted, past and future time
- [x] 4.2 Implement `baby_calendar.update_event` with `fields`, clearing by null and the tracker normaliser, `delete_event` and `list_events` per design D5; verify with tests for a corrected time, untouched fields, a cleared note, unknown identifiers, events of a disabled tracker, a day range, the tracker filter and an empty period
- [x] 4.3 Implement the per-entry state object with recompute on write and at local midnight per design D9; verify with tests using a frozen clock for midnight, a late entry for yesterday and a 23-hour day
- [x] 4.4 Implement the shared dashboard logging path, the `minutes_ago` number and the `undo` button per design D7 and D8; verify with tests for an entry back-dated by twenty minutes, the input returning to zero, the next entry not back-dated, a double tap, the wrong button undone, a back-dated entry undone, a second undo, and nothing recent

## 5. Diaper tracker

- [x] 5.1 Implement `baby_calendar.log_diaper` with `services.yaml` selectors and translations; verify with tests for wet, dirty with a stool type, both as a single event, invalid content, a stool type on a wet diaper and a correction to wet dropping the stool type
- [x] 5.2 Implement the three content buttons, the four stool type buttons and the `stool_prompt` binary sensor per design D8; verify with tests for a type added as a second tap, a type changed, last diaper wet, too late, the prompt appearing, answered, ignored for ten minutes and staying off after a wet diaper
- [x] 5.3 Implement the three timestamp sensors and three daily sensors with `en` and `pt` names, using the outcome of task 1.5; verify with tests for the mixed-day, no-events and latest-deleted scenarios and the stool type attribute
- [ ] 5.4 Document the diaper service and entities in `README.md`, with the conditional card that shows the stool buttons; verify the example loads and behaves as described on a real instance

## 6. Bottle tracker

- [ ] 6.1 Implement `baby_calendar.log_bottle` and the bottle number, select and button; verify with tests for a bottle with content, a 7 ml bottle, missing and zero amount, invalid content, the usual bottle from the dashboard, a press with the amount at zero, and inputs restored after a restart
- [ ] 6.2 Implement the bottle sensors; verify with tests for two bottles, a corrected amount and no bottles yet
- [ ] 6.3 Document the bottle service and entities with examples in `README.md`; verify each example runs as written on a real instance

## 7. Integration checks

- [ ] 7.1 Install the repository through HACS as a custom repository on a real instance, add a baby with both trackers and build the README's example dashboard; on a phone, log each kind of entry, back-date one, undo one, and set a bottle amount and press the button immediately to check the logged amount
- [ ] 7.2 Restart Home Assistant and verify events, sensor values and the bottle inputs are unchanged and `minutes_ago` is 0
- [ ] 7.3 Take a Home Assistant backup while pressing buttons, confirm `baby_calendar.db` is inside it, restore it and verify events are present
- [ ] 7.4 Remove the baby, add it again with "restore history" and verify the events and sensors are back
- [ ] 7.5 Run `openspec validate add-core-tracking --strict` and verify it passes

## Workflow follow-up

- Archive the change after review, then confirm `openspec/specs/` contains `baby-profile`, `event-log`, `diaper-tracking` and `feeding-tracking` with their Purpose sections filled in.
