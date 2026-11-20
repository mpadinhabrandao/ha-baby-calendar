# Spec Delta

## Purpose

Defines how a diaper change is logged as wet, dirty or both, how a stool type is added to it, and which sensors report the last change and the counts for the current day.

## ADDED Requirements

### Requirement: Log a diaper change
The integration SHALL provide a service to log a diaper change for a baby. The content is required and SHALL be one of wet, dirty or both. Notes and time are optional. One diaper change SHALL be one event whatever its content.

#### Scenario: Wet diaper
- **WHEN** a wet diaper change is logged
- **THEN** one diaper event with the content wet is recorded

#### Scenario: Wet and dirty diaper
- **WHEN** a diaper change with the content both is logged
- **THEN** one diaper event is recorded, not two

#### Scenario: Invalid content
- **WHEN** a diaper change is logged with a content other than wet, dirty or both
- **THEN** the call fails with an error and nothing is recorded

### Requirement: Stool type
A diaper change with the content dirty or both MAY carry a stool type, one of normal, soft, hard or diarrhea. A stool type SHALL be rejected when logging a wet diaper change. Correcting a diaper change to the content wet SHALL remove its stool type.

#### Scenario: Dirty with type
- **WHEN** a dirty diaper change is logged through the service with the stool type soft
- **THEN** the recorded event carries the stool type soft

#### Scenario: Type on a wet diaper
- **WHEN** a wet diaper change is logged with a stool type
- **THEN** the call fails with an error and nothing is recorded

#### Scenario: Corrected to wet
- **WHEN** a dirty diaper change with the stool type soft is corrected to the content wet
- **THEN** the event has the content wet and no stool type

### Requirement: One-tap buttons
A baby with the diaper tracker SHALL have three button entities, for a wet, a dirty and a wet-and-dirty diaper. Pressing one SHALL log a diaper change with that content and no stool type.

#### Scenario: Dirty button
- **WHEN** the dirty diaper button is pressed
- **THEN** a dirty diaper change with no stool type is recorded

#### Scenario: Button used from an automation
- **WHEN** an automation presses the wet diaper button in response to a physical button
- **THEN** a wet diaper change is recorded exactly as if it had been pressed on a dashboard

### Requirement: Stool type buttons
A baby with the diaper tracker SHALL have one button entity per stool type. Pressing one SHALL set that stool type on the baby's most recently recorded diaper change, replacing any type it had, provided that change is dirty or both and was recorded within the last 10 minutes. Otherwise the press SHALL fail with an error.

#### Scenario: Type added as a second tap
- **WHEN** the dirty diaper button is pressed and then the soft button is pressed
- **THEN** one dirty diaper change with the stool type soft exists

#### Scenario: Type changed
- **WHEN** the soft button was pressed by mistake and the hard button is pressed right after
- **THEN** that diaper change has the stool type hard

#### Scenario: Last diaper was wet
- **WHEN** the most recently recorded diaper change is wet and a stool type button is pressed
- **THEN** the press fails with an error and no event changes

#### Scenario: Too late
- **WHEN** a stool type button is pressed 30 minutes after the last dirty diaper was recorded
- **THEN** the press fails with an error and no event changes

### Requirement: Stool type prompt
A baby with the diaper tracker SHALL have a binary sensor that is on while the most recently recorded diaper change is dirty or both, has no stool type and was recorded within the last 10 minutes, so that a dashboard can show the stool type buttons only then.

#### Scenario: Prompt appears
- **WHEN** the dirty diaper button is pressed
- **THEN** the prompt sensor turns on

#### Scenario: Prompt answered
- **WHEN** a stool type button is pressed while the prompt sensor is on
- **THEN** the prompt sensor turns off

#### Scenario: Prompt ignored
- **WHEN** no stool type button is pressed for 10 minutes after a dirty diaper
- **THEN** the prompt sensor turns off and the diaper change keeps no stool type

#### Scenario: Wet diaper
- **WHEN** the wet diaper button is pressed
- **THEN** the prompt sensor stays off

### Requirement: Last diaper sensors
A baby with the diaper tracker SHALL have timestamp sensors for the last diaper change, the last wet diaper and the last dirty diaper. A change with the content both SHALL count as wet and as dirty. The last dirty sensor SHALL expose the stool type as an attribute. A sensor with no matching event SHALL report an unknown state.

#### Scenario: After a dirty diaper
- **WHEN** a dirty diaper change is logged at 10:00 and the last wet diaper was at 08:00
- **THEN** the last change and last dirty sensors show 10:00 and the last wet sensor shows 08:00

#### Scenario: No events yet
- **WHEN** a baby has no diaper events
- **THEN** the three sensors report an unknown state

#### Scenario: Latest event deleted
- **WHEN** the most recent diaper event is deleted
- **THEN** the sensors show the time of the previous matching event

### Requirement: Daily diaper counts
A baby with the diaper tracker SHALL have daily sensors counting today's diaper changes, wet diapers and dirty diapers. A change with the content both SHALL add one to each of the three.

#### Scenario: Mixed day
- **WHEN** one wet, one dirty and one both change are logged today
- **THEN** the changes sensor shows 3, the wet sensor shows 2 and the dirty sensor shows 2
