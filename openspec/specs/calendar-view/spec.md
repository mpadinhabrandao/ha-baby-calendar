# calendar-view Specification

## Purpose

Defines the calendar each baby exposes in Home Assistant: which events it shows, how each kind of event is titled and placed in time, and which corrections can be made directly from the calendar.

## Requirements

### Requirement: Full history
Each calendar SHALL show events of any date for which events of its group are recorded, without a retention limit, including events of a tracker that has since been disabled.

#### Scenario: Three months ago
- **WHEN** the user navigates the Diapers calendar to a week three months in the past
- **THEN** the diaper changes recorded in that week are shown

#### Scenario: Disabled tracker
- **WHEN** the bottle tracker is disabled after bottles were recorded
- **THEN** those bottles still appear in the Feeding calendar

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
A calendar SHALL be on while a timed event of its group for the baby is in progress and off otherwise. An instantaneous event SHALL NOT turn it on.

#### Scenario: Diaper logged
- **WHEN** a diaper change is recorded and no timer is running
- **THEN** every calendar of the baby stays off

#### Scenario: Sleep running
- **WHEN** a sleep timer of the baby is running and no breastfeeding timer is
- **THEN** the Sleep calendar is on and the Feeding calendar is off

### Requirement: Calendars by group
Each baby SHALL have one calendar entity per group of entries, attached to the baby's device:

| Group | Entries |
|---|---|
| Feeding | bottle, breastfeeding, solids, pumping |
| Diapers | diaper changes |
| Sleep | sleep |
| Health | temperature, weight, length, medication doses |

A calendar SHALL show the baby's recorded events of its group's trackers and no other events. Events of other babies SHALL NOT appear in it.

#### Scenario: Entries split by group
- **WHEN** a diaper change, a bottle and a sleep were recorded for a baby today
- **THEN** the Diapers calendar shows only the diaper change, the Feeding calendar only the bottle and the Sleep calendar only the sleep

#### Scenario: Health entries together
- **WHEN** a temperature of 38.5 °C, a weight of 4200 g and a paracetamol dose were recorded for a baby
- **THEN** all three appear in the baby's Health calendar and none appears in the other calendars

#### Scenario: Two babies
- **WHEN** babies "Alice" and "Bruno" exist and a diaper change is recorded for "Alice"
- **THEN** it appears in the Diapers calendar of "Alice" and not in the Diapers calendar of "Bruno"

#### Scenario: Filter in the calendar panel
- **WHEN** the user turns off every calendar of a baby except Health in the calendar panel
- **THEN** only temperatures, weights, lengths and medication doses are shown

### Requirement: Calendar names
Each calendar SHALL be named after its group, in the language of the Home Assistant instance.

#### Scenario: Portuguese instance
- **WHEN** a baby "Duarte" is added on a Portuguese instance
- **THEN** its calendars are named "Alimentação", "Fraldas", "Sono" and "Saúde" on the baby's device

### Requirement: When a group calendar exists
A group's calendar SHALL exist when at least one of the group's trackers is enabled for the baby, when the group is Health and the baby has a medication, or when the baby has recorded events of the group's trackers. Otherwise it SHALL NOT exist, and a calendar that stops meeting these conditions SHALL be removed.

#### Scenario: Diapers only
- **WHEN** a new baby has only the diaper tracker enabled and no medications
- **THEN** the baby has a Diapers calendar and no Feeding, Sleep or Health calendar

#### Scenario: Tracker disabled with history
- **WHEN** the pumping tracker was the only Feeding tracker enabled, pumpings were recorded and then the tracker is disabled
- **THEN** the Feeding calendar still exists and shows those pumpings

#### Scenario: Medication only
- **WHEN** a baby has no measurement tracker enabled but has a medication
- **THEN** the baby has a Health calendar

### Requirement: Own entries only
Changing the time of an event, editing its notes or deleting it through a calendar SHALL apply only to events of that calendar's group. A request for an event of another group or another baby SHALL be rejected with an error and the event SHALL be unchanged.

#### Scenario: Event of another group
- **WHEN** a delete is requested through the Diapers calendar for the uid of a bottle event
- **THEN** the request fails and the bottle still exists

### Requirement: Single calendar removed
The calendar that showed all of a baby's events SHALL NOT exist. When the integration starts, it SHALL remove that calendar from the entity registry if it is still there.

#### Scenario: Upgrade
- **WHEN** a baby set up with the single calendar is loaded by this version
- **THEN** the single calendar is gone from Home Assistant and the baby's group calendars exist instead
