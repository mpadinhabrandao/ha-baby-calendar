# pumping-tracking Specification

## Purpose

Defines how milk pumping sessions are logged, with amount and side, and which sensors report the last session and the totals for the current day.

## Requirements

### Requirement: Pumping tracker
Pumping SHALL be a tracker that the user can enable per baby.

#### Scenario: Enabled for a baby
- **WHEN** the user enables the pumping tracker on a baby
- **THEN** the pumping amount input, side selector, button and sensors become available

### Requirement: Log a pumping session
The integration SHALL provide a service to log a pumping session. The amount in millilitres is required and SHALL be greater than zero. The side, one of left, right or both, is optional, as are notes and time.

#### Scenario: Session with side
- **WHEN** a pumping session of 60 ml on the left side is logged
- **THEN** a pumping event with 60 ml and the side left is recorded

#### Scenario: Amount missing or zero
- **WHEN** a pumping session is logged without an amount or with the amount 0
- **THEN** the call fails with an error and nothing is recorded

#### Scenario: Invalid side
- **WHEN** a pumping session is logged with a side other than left, right or both
- **THEN** the call fails with an error and nothing is recorded

### Requirement: Pumping dashboard entities
A baby with the pumping tracker SHALL have a number entity for the amount in ml, adjustable in steps of 1 ml, a selector for the side, and a button that logs a session with the current amount and side, following the "minutes ago" input, undo and repeated press rules. After an entry the amount SHALL return to zero and the side to "not specified"; both SHALL have those values after a restart.

#### Scenario: Session logged from the dashboard
- **WHEN** the amount shows 80, the side shows both and the pumping button is pressed
- **THEN** an 80 ml session with the side both is recorded, the amount shows 0 and the side shows "not specified"

#### Scenario: Stale amount cannot be logged
- **WHEN** the pumping button is pressed again without entering an amount
- **THEN** the press fails with an error and nothing is recorded

### Requirement: Pumping sensors
A baby with the pumping tracker SHALL have a timestamp sensor for the last session, with its amount and side as attributes, and daily sensors for the number of sessions and the total millilitres of today.

#### Scenario: Two sessions
- **WHEN** sessions of 60 ml and 80 ml are logged today
- **THEN** the sessions sensor shows 2 and the millilitres sensor shows 140

#### Scenario: No sessions yet
- **WHEN** a baby has no pumping events
- **THEN** the last session sensor reports an unknown state

### Requirement: Pumping in the calendar
When the baby has a calendar, a pumping event SHALL appear in it with a title made of an emoji, the translated word for pumping, the amount in ml and the side when set.

#### Scenario: Session in the calendar
- **WHEN** an 80 ml session with the side both is recorded on an English instance
- **THEN** the calendar title contains "Pumping 80 ml" and the side
