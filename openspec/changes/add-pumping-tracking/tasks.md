# Tasks

## 1. Pumping tracker

- [x] 1.1 Register the pumping tracker and add it to the tracker list in the baby flows with `en` and `pt` strings; verify with a test that enabling it creates its entities
- [x] 1.2 Implement `baby_calendar.log_pumping` and the pumping number, select and button with one-shot inputs per design P2; verify with tests for a session with side, missing and zero amount, invalid side, a session from the dashboard resetting both inputs, a second press failing, a back-dated press and inputs empty after a restart
- [x] 1.3 Implement the pumping sensors and, when the calendar exists, the calendar title; verify with tests for two sessions, no sessions yet and the calendar title in English and Portuguese
- [x] 1.4 Document the pumping service and entities with examples in `README.md`; verify each example runs as written on a real instance

  - 1.4: the README section is written; running its example on a real instance is still to do.

## 2. Integration checks

- [ ] 2.1 On a real instance, enable pumping, log a session from the dashboard on a phone and verify the sensors and that the inputs were reset
- [ ] 2.2 Verify that the other trackers behave exactly as before
- [x] 2.3 Run `openspec validate add-pumping-tracking --strict` and verify it passes

## Workflow follow-up

- Archive the change after review, then confirm `openspec/specs/` contains `pumping-tracking` with its Purpose section filled in.
