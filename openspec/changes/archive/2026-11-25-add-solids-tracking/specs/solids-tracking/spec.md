# Spec Delta

## Purpose

Defines how solid food meals are logged for a baby, how what was eaten is noted, and which sensors report the last meal and the number of meals today.

## ADDED Requirements

### Requirement: Solids tracker
Solids SHALL be a tracker that the user can enable per baby.

#### Scenario: Enabled for a baby
- **WHEN** the user enables the solids tracker on a baby
- **THEN** the solids button and sensors become available

### Requirement: Log a meal
The integration SHALL provide a service to log a solid food meal for a baby, with optional notes describing what was eaten and an optional time. A baby with the solids tracker SHALL have a button that logs a meal with no note, following the "minutes ago" input, undo and repeated press rules.

#### Scenario: Meal with a note
- **WHEN** a meal is logged through the service with the note "carrot puree"
- **THEN** a solids event carrying that note is recorded

#### Scenario: Button pressed
- **WHEN** the solids button is pressed
- **THEN** a solids event with no note is recorded at the current time

### Requirement: Solids sensors
A baby with the solids tracker SHALL have a timestamp sensor for the last meal, with its notes as an attribute, and a daily sensor for the number of meals of today.

#### Scenario: Two meals
- **WHEN** two meals are logged today
- **THEN** the meals sensor shows 2 and the last meal sensor shows the time of the second

#### Scenario: Note added later
- **WHEN** a note is added in the calendar to the most recent meal
- **THEN** the last meal sensor's notes attribute shows it

### Requirement: Solids in the calendar
A solids event SHALL appear in the baby's calendar with a title made of a food emoji and the translated word for a meal, and with its notes as the description.

#### Scenario: Meal in the calendar
- **WHEN** a meal with the note "carrot puree" is recorded on an English instance
- **THEN** the calendar shows "🥣 Solids" with the description "carrot puree"
