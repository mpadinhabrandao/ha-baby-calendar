# medication-tracking Specification

## Purpose

Defines how medications and vitamins are set up for a baby, how each dose given is recorded, and which sensors report the last dose and the doses of the current day.

## Requirements

### Requirement: Define a medication
The user SHALL be able to add a medication to a baby from the UI, with a name, an optional dose text and an optional schedule. Medication names SHALL be unique within a baby. The dose text SHALL be informational only.

#### Scenario: Vitamin D added
- **WHEN** the user adds the medication "Vitamin D" with the dose text "1 drop"
- **THEN** the medication exists and its entities become available without restarting Home Assistant

#### Scenario: Duplicate name
- **WHEN** the user adds a medication with the name of an existing medication of the same baby
- **THEN** the form shows an error and no medication is created

### Requirement: Edit a medication
The user SHALL be able to change a medication's name, dose text and schedule. Recorded doses SHALL be kept and SHALL be listed under the new name.

#### Scenario: Renamed
- **WHEN** a medication with recorded doses is renamed
- **THEN** its doses remain and are listed under the new name

### Requirement: Deactivate a medication
The user SHALL be able to deactivate a medication. A deactivated medication SHALL have no entities and SHALL raise no reminders, and its recorded doses SHALL be kept. Reactivating it SHALL bring back its entities with those doses.

#### Scenario: Course finished
- **WHEN** a medication is deactivated after a course ends
- **THEN** its entities are gone, no reminder is raised for it, and its doses still appear when events are listed

### Requirement: Remove a medication
The user SHALL be able to remove a medication. Removing it SHALL remove its entities and SHALL keep its recorded doses, which SHALL continue to be listed under the medication's name. Other medications SHALL be unaffected.

#### Scenario: Medication removed
- **WHEN** a medication with recorded doses is removed
- **THEN** its entities are gone and its doses still appear, with its name, when events are listed

#### Scenario: Same name added later
- **WHEN** a medication is removed and a new one with the same name is added
- **THEN** the new medication starts with no doses of its own and the earlier doses remain in the history

### Requirement: Record a dose
The integration SHALL provide a service to record a dose of a medication, identified by its name, for a baby. Notes and time are optional. Each medication SHALL also have a button that records a dose, which SHALL follow the baby's "minutes ago" input, undo and repeated press rules like every other logging button.

#### Scenario: Dose by button
- **WHEN** the button of "Vitamin D" is pressed
- **THEN** a dose of "Vitamin D" is recorded at the current time

#### Scenario: Dose given earlier
- **WHEN** a dose is recorded with a time of one hour ago and a note
- **THEN** the dose is recorded at that time with the note

#### Scenario: Both parents press
- **WHEN** the button of "Vitamin D" is pressed and "undo" is pressed right after
- **THEN** that dose is deleted

#### Scenario: Unknown medication
- **WHEN** a dose is recorded for a name that matches no active medication of the baby
- **THEN** the call fails with an error and nothing is recorded

### Requirement: Dose sensors
Each active medication SHALL have a timestamp sensor for its last dose, with the dose text as an attribute, and a daily sensor for the number of doses of today. With no doses the last dose sensor SHALL report an unknown state.

#### Scenario: Has she had it today
- **WHEN** one dose of "Vitamin D" was recorded today
- **THEN** its doses today sensor shows 1 and its last dose sensor shows the time of that dose

#### Scenario: Dose deleted
- **WHEN** a dose recorded by mistake is deleted
- **THEN** the doses today sensor no longer counts it and the last dose sensor shows the previous dose

### Requirement: No medical advice
The integration SHALL NOT suggest a medicine, a dose or a schedule, and SHALL NOT judge whether a recorded dose is appropriate. It SHALL act only on what the user entered.

#### Scenario: Two doses close together
- **WHEN** two doses of the same medication are recorded within a few minutes
- **THEN** both are recorded and the integration raises no warning of its own

### Requirement: Medication attribute
Every entity of a medication SHALL have the attribute `medication` with the medication's name, so its entities can be told apart whatever the language of Home Assistant.

#### Scenario: Portuguese instance
- **WHEN** Home Assistant is in Portuguese and the baby has "Vitamina D"
- **THEN** each of the "Vitamina D" entities has `medication: Vitamina D`
