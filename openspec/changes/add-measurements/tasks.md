# Tasks

## 1. Measurement tracker

- [ ] 1.1 Implement the parameterised measurement tracker and register weight, length and temperature per design M1, and add them to the tracker list in the baby flows with `en` and `pt` strings; verify with a test that enabling only weight creates only the weight entities
- [ ] 1.2 Implement `log_weight`, `log_length` and `log_temperature` with `services.yaml` selectors and translations per design M2; verify with tests for a logged weight, a reading from a past check-up, a missing value and each range rejection
- [ ] 1.3 Extend `update_event` to accept `value` for measurement events; verify with tests for a corrected value and a correction outside the range

## 2. Entities

- [ ] 2.1 Implement the number input and button per design M3; verify with tests for a reading from the dashboard, the input returning to zero, a stray press at zero, a press with an out-of-range input, a reading back-dated with `minutes_ago`, and the input being zero after a restart
- [ ] 2.2 Implement the latest reading and timestamp sensors per design M3 and M4; verify with tests for a new reading, an older reading added later, the latest reading deleted, no readings yet, the temperature sensor expiring after 24 hours with a frozen clock, and the weight sensor not expiring
- [ ] 2.3 Confirm on a real instance that the weight sensor appears in a statistics graph and charts readings logged over several days
- [ ] 2.4 Add the calendar `summary` for the three measurements (emoji, value and unit) per design M6; verify with unit tests for a weight, a length and a temperature title in English and Portuguese
- [ ] 2.5 Document the measurement services and entities with examples in `README.md`, including the metric-only input note and what the long-term chart does and does not show; verify each example runs as written on a real instance

## 3. Integration checks

- [ ] 3.1 On a real instance, enable the three measurements on an existing baby, log readings by service and from the dashboard, and verify the sensors and `list_events`
- [ ] 3.2 Verify that the other trackers and their existing events behave exactly as before
- [ ] 3.3 Run `openspec validate add-measurements --strict` and verify it passes

## Workflow follow-up

- Archive the change after review, then confirm `openspec/specs/` contains `measurement-tracking` with its Purpose section filled in.
