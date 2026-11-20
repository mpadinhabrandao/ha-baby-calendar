# Spec Delta

## Purpose

Defines the calendar each baby exposes in Home Assistant: which events it shows, how each kind of event is titled and placed in time, and which corrections can be made directly from the calendar.

## ADDED Requirements

### Requirement: One calendar per baby
Each baby SHALL have one calendar entity, attached to the baby's device, showing all of that baby's recorded events from every tracker. Events of other babies SHALL NOT appear in it.

#### Scenario: All trackers in one calendar
- **WHEN** a diaper change, a bottle and a sleep were recorded for a baby today
- **THEN** the baby's calendar shows the three events on today

#### Scenario: Two babies
- **WHEN** babies "Alice" and "Bruno" exist and an event is recorded for "Alice"
- **THEN** it appears in the calendar of "Alice" and not in the calendar of "Bruno"

### Requirement: Full history
The calendar SHALL show events of any date for which events are recorded, without a retention limit, including events of a tracker that has since been disabled.

#### Scenario: Three months ago
- **WHEN** the user navigates the calendar to a week three months in the past
- **THEN** the events recorded in that week are shown

#### Scenario: Disabled tracker
- **WHEN** the bottle tracker is disabled after bottles were recorded
- **THEN** those bottles still appear in the calendar

### Requirement: Event titles
Each calendar event SHALL have a title made of an emoji identifying the kind of event followed by its details, in the language of the Home Assistant instance: the diaper content and stool type, the bottle amount and content, the breastfeeding side and duration, or the sleep duration. An in-progress event SHALL say so instead of a duration. A tracker added by a later change SHALL define its own title.

#### Scenario: Dirty diaper
- **WHEN** a dirty diaper with the stool type soft is recorded on an English instance
- **THEN** its calendar title is "💩 Dirty diaper (soft)"

#### Scenario: Bottle in Portuguese
- **WHEN** a 90 ml formula bottle is recorded on a Portuguese instance
- **THEN** its calendar title is "🍼 Biberão 90 ml fórmula"

#### Scenario: Sleep with duration
- **WHEN** a sleep of one hour and twenty minutes is finished
- **THEN** its calendar title contains the sleep emoji and the duration of 1 h 20 min

#### Scenario: Sleep in progress
- **WHEN** a sleep timer is running
- **THEN** its calendar title says the sleep is in progress

### Requirement: Description is the note
The description of a calendar event SHALL be the event's notes and nothing else. An event without notes SHALL have an empty description.

#### Scenario: Bottle with a note
- **WHEN** a bottle is recorded with the note "spat up a little"
- **THEN** the calendar event's description is "spat up a little"

#### Scenario: No note
- **WHEN** a diaper change is recorded from a button
- **THEN** the calendar event's description is empty

### Requirement: Placement in time
A timed event SHALL span its recorded start and end. An in-progress timed event SHALL span from its start to the current time. An instantaneous event SHALL appear as a block of fixed short length starting at its time.

#### Scenario: Finished sleep
- **WHEN** a sleep from 14:00 to 14:45 is recorded
- **THEN** the calendar shows it from 14:00 to 14:45

#### Scenario: Sleep in progress
- **WHEN** a sleep timer has been running since 22:00 and it is 23:30
- **THEN** the calendar shows the sleep from 22:00 to 23:30

#### Scenario: Diaper change
- **WHEN** a diaper change is recorded at 10:00
- **THEN** the calendar shows a short block starting at 10:00

### Requirement: Change an event's time from the calendar
The user SHALL be able to change an event's time from the Home Assistant calendar. For a finished timed event the start and the end SHALL both be changeable. For an instantaneous event and for an in-progress event only the start SHALL apply. The same time rules as the correction service SHALL apply, and the sensors SHALL reflect the change immediately.

#### Scenario: Diaper moved
- **WHEN** the time of a diaper event is changed from 10:00 to 09:30 in the calendar
- **THEN** the event is recorded at 09:30 and the last diaper sensor follows

#### Scenario: Sleep end corrected
- **WHEN** the end of a finished sleep is changed from 14:45 to 15:10 in the calendar
- **THEN** the sleep ends at 15:10 and today's sleep duration follows

#### Scenario: Moved into the future
- **WHEN** an event is moved to a time in the future
- **THEN** the change is rejected with an error and the event is unchanged

### Requirement: Editing never stops a timer
Saving an in-progress event from the calendar SHALL NOT end it. Its timer SHALL keep running whatever end time the calendar submits.

#### Scenario: Note added to a running sleep
- **WHEN** a note is added in the calendar to a sleep whose timer is running
- **THEN** the note is saved and the sleep timer is still running

### Requirement: Edit notes from the calendar
The user SHALL be able to add, change and remove an event's notes by editing its description in the calendar. The event's other fields SHALL be unchanged.

#### Scenario: Note added
- **WHEN** the description of a bottle event with no note is set to "took it slowly"
- **THEN** the event's notes are "took it slowly" and its amount and content are unchanged

#### Scenario: Two paragraphs
- **WHEN** a description with two paragraphs is saved
- **THEN** the event's notes contain both paragraphs

#### Scenario: Note removed
- **WHEN** the description of an event with a note is emptied and saved
- **THEN** the event has no note

### Requirement: Title is generated
The title of a calendar event SHALL always be generated from the event's data. A title edited in the calendar SHALL NOT change the event's data.

#### Scenario: Title edited
- **WHEN** the user changes the title of a bottle event in the calendar and saves
- **THEN** the event keeps its amount and content and the calendar shows the generated title again

### Requirement: Delete an event from the calendar
The user SHALL be able to delete an event from the Home Assistant calendar. It SHALL be permanently deleted and the sensors SHALL reflect it immediately.

#### Scenario: Mistaken entry
- **WHEN** a bottle logged by mistake is deleted in the calendar
- **THEN** it is gone from the calendar and today's bottle sensors no longer include it

### Requirement: No creation from the calendar
The calendar SHALL NOT offer creating events. Recording an event SHALL remain possible only through the trackers' buttons, switches and services.

#### Scenario: Add event
- **WHEN** the user opens the baby's calendar in Home Assistant
- **THEN** no option to add an event to it is offered

### Requirement: Recorded events only
The calendar SHALL show only recorded events. It SHALL NOT show scheduled or predicted future events.

#### Scenario: Tomorrow
- **WHEN** the user navigates the calendar to tomorrow
- **THEN** no events are shown

### Requirement: Calendar state
The calendar entity SHALL be on while a timed event of the baby is in progress and off otherwise. An instantaneous event SHALL NOT turn it on.

#### Scenario: Diaper logged
- **WHEN** a diaper change is recorded and no timer is running
- **THEN** the calendar entity stays off
