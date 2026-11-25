# event-log Specification

## Purpose

Defines the durable record of baby events: how long entries are kept, how entries are back-dated, undone, corrected, deleted and queried, and the rules every tracker's daily values follow.

## Requirements

### Requirement: Durable history
Recorded events SHALL be kept indefinitely. They SHALL NOT be removed by the Home Assistant recorder purge, by a Home Assistant restart, or by an update of the integration.

#### Scenario: Recorder purge
- **WHEN** an event is older than the recorder's retention period and the recorder purge runs
- **THEN** the event is still returned when events are listed

#### Scenario: Restart
- **WHEN** Home Assistant restarts after events were recorded
- **THEN** all events are present and the sensors show the same values as before the restart

### Requirement: Included in backups
The event data SHALL be part of a standard Home Assistant backup, SHALL be captured in a consistent state even if an entry is being written when the backup runs, and SHALL be fully restored with it.

#### Scenario: Backup restored
- **WHEN** a Home Assistant backup taken after events were recorded is restored
- **THEN** every event recorded before the backup is present

### Requirement: Event time
Every event SHALL have a time. When no time is given the current time SHALL be used. A time in the past SHALL be accepted. A time in the future SHALL be rejected with an error and nothing SHALL be recorded.

#### Scenario: Time omitted
- **WHEN** an event is logged without a time
- **THEN** it is recorded with the current time

#### Scenario: Late entry
- **WHEN** an event is logged with a time two hours in the past
- **THEN** it is recorded with that time

#### Scenario: Future time
- **WHEN** an event is logged with a time one hour in the future
- **THEN** the call fails with an error and no event is recorded

### Requirement: Minutes ago input
Each baby SHALL have a number entity "minutes ago". An entry made with any of that baby's dashboard entities SHALL be recorded at the current time minus that many minutes. The input SHALL return to zero after every entry and SHALL be zero after a restart.

#### Scenario: Changed twenty minutes ago
- **WHEN** "minutes ago" is set to 20 and the wet diaper button is pressed at 03:20
- **THEN** a wet diaper change is recorded at 03:00 and "minutes ago" shows 0

#### Scenario: Next entry is not back-dated
- **WHEN** a second button is pressed right after a back-dated entry
- **THEN** the second entry is recorded at the current time

### Requirement: Undo last entry
Each baby SHALL have an "undo" button that permanently deletes the entry of that baby that was recorded most recently, whatever its event time, provided it was recorded within the last 15 minutes. Pressing it again SHALL delete the one recorded before it, under the same limit.

#### Scenario: Wrong button
- **WHEN** the dirty diaper button is pressed by mistake and "undo" is pressed a moment later
- **THEN** that diaper change is deleted and the sensors no longer include it

#### Scenario: Back-dated entry undone
- **WHEN** an entry back-dated by two hours was just recorded and "undo" is pressed
- **THEN** that entry is deleted, not an entry with a later event time

#### Scenario: Nothing recent
- **WHEN** "undo" is pressed and no entry was recorded in the last 15 minutes
- **THEN** the press fails with an error and nothing is deleted

### Requirement: Repeated press guard
A second press of the same logging button of the same baby within three seconds SHALL NOT record a second entry.

#### Scenario: Double tap
- **WHEN** the wet diaper button is pressed twice within one second
- **THEN** one diaper change is recorded

### Requirement: Baby in services
A service call that logs or lists events SHALL name the baby it applies to. A call that names no baby SHALL fail with an error, including when only one baby is configured.

#### Scenario: Baby named
- **WHEN** an event is logged through a service naming the baby "Alice"
- **THEN** the event is recorded for "Alice"

#### Scenario: Baby omitted
- **WHEN** an event is logged through a service without naming a baby
- **THEN** the call fails with an error and nothing is recorded

### Requirement: Event identity
Every recorded event SHALL have a unique identifier that is returned when the event is created and when events are listed, and that each tracker's last-event sensor exposes as an attribute.

#### Scenario: Identifier returned on creation
- **WHEN** an event is logged through a service call that requests a response
- **THEN** the response contains the identifier of the new event

### Requirement: Correct an event
The integration SHALL provide a service to change the time, the tracker-specific fields and the notes of an existing event, identified by its identifier. Fields that are not supplied SHALL keep their value. Supplied values SHALL follow the same rules as when logging. Sensors SHALL reflect the change immediately.

#### Scenario: Time corrected
- **WHEN** the time of an existing event is changed to thirty minutes earlier
- **THEN** listing events shows the event at the new time with its other fields unchanged

#### Scenario: Unknown identifier
- **WHEN** a correction is requested for an identifier that does not exist
- **THEN** the call fails with an error and no event changes

### Requirement: Clear a field
The correction service SHALL allow an optional field or the notes of an event to be cleared by supplying an explicit empty value.

#### Scenario: Note removed
- **WHEN** a correction supplies an empty value for the notes of an event that has a note
- **THEN** the event has no note

### Requirement: Works for disabled trackers
Correcting, deleting and listing SHALL work for every stored event of a configured baby, including events of a tracker that is currently disabled.

#### Scenario: Old bottle deleted
- **WHEN** the bottle tracker is disabled and a stored bottle event is deleted by its identifier
- **THEN** the event is deleted

### Requirement: Delete an event
The integration SHALL provide a service to permanently delete an event by its identifier. Sensors SHALL reflect the deletion immediately.

#### Scenario: Mistaken entry deleted
- **WHEN** an event logged by mistake is deleted
- **THEN** it no longer appears when events are listed and today's values no longer include it

#### Scenario: Unknown identifier
- **WHEN** a deletion is requested for an identifier that does not exist
- **THEN** the call fails with an error

### Requirement: List events
The integration SHALL provide a service that returns the events of one baby within a start and end time, ordered by time, each with its identifier, tracker, time, tracker-specific fields and notes. An optional tracker filter SHALL be supported.

#### Scenario: Events of a day
- **WHEN** events are requested for a baby from midnight to midnight of a given day
- **THEN** the response contains exactly that baby's events of that day, oldest first

#### Scenario: Filtered by tracker
- **WHEN** events are requested for a day with the bottle tracker as filter
- **THEN** the response contains only that day's bottle events

#### Scenario: Empty period
- **WHEN** events are requested for a period with no events
- **THEN** the response contains an empty list and the call succeeds

### Requirement: Daily values
Every sensor described as a value of today SHALL cover local midnight to local midnight in the Home Assistant time zone, by event time, SHALL return to zero at local midnight, and SHALL be recorded in Home Assistant long-term statistics.

#### Scenario: Midnight
- **WHEN** local midnight passes
- **THEN** every daily sensor shows 0

#### Scenario: Late entry for yesterday
- **WHEN** an event is logged today with a time of yesterday evening
- **THEN** today's values do not change

#### Scenario: Chart over a month
- **WHEN** events have been logged for more than the recorder retention period
- **THEN** a statistics chart of a daily sensor shows values for the whole period

### Requirement: Charts reflect the day as it was logged
Long-term statistics SHALL reflect each day's values as they stood during that day. Correcting, adding or deleting an event of a past day SHALL change the event log and SHALL NOT be required to change the statistics already recorded for that day.

#### Scenario: Yesterday corrected
- **WHEN** an event of yesterday is deleted today
- **THEN** listing yesterday's events no longer returns it, and yesterday's recorded statistics may still include it

### Requirement: Local only
Event data SHALL stay on the Home Assistant host. The integration SHALL NOT send event data to any external service and SHALL NOT make outbound network requests.

#### Scenario: No connectivity
- **WHEN** the Home Assistant host has no internet connection
- **THEN** logging, correcting, deleting and listing events all work

### Requirement: No health assessment
The integration SHALL record and display data. It SHALL NOT derive health assessments, warnings or advice from the recorded data.

#### Scenario: Unusual day
- **WHEN** a day ends with an unusually low number of diaper changes
- **THEN** the integration raises no alert or notification of its own
