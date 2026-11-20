# Spec Delta

## Purpose

Defines how a baby is added to, edited in and removed from Home Assistant, how its enabled trackers are chosen, what happens to its history on removal, and how each baby appears as a device.

## ADDED Requirements

### Requirement: Add a baby from the UI
The integration SHALL let the user add a baby from the Home Assistant integrations page by entering a name and, optionally, a birth date. No YAML configuration SHALL be required.

#### Scenario: Baby added before birth
- **WHEN** the user adds a baby with the name "Alice" and leaves the birth date empty
- **THEN** the baby is created

#### Scenario: Name missing
- **WHEN** the user submits the form with an empty name
- **THEN** the form shows an error and no baby is created

### Requirement: Choose trackers when adding a baby
When adding a baby the user SHALL be shown the list of available trackers and SHALL be able to tick any number of them, including none. Only the ticked trackers SHALL create entities for that baby.

#### Scenario: One tracker ticked
- **WHEN** the user adds a baby and ticks diaper only
- **THEN** the baby has the diaper entities and no bottle entities

#### Scenario: None ticked
- **WHEN** the user adds a baby and ticks no tracker
- **THEN** the baby is created with no tracker entities

### Requirement: Change enabled trackers
The user SHALL be able to change a baby's enabled trackers later from the UI, without restarting Home Assistant. Disabling a tracker SHALL remove its entities and SHALL keep its recorded events. Enabling it again SHALL bring back its entities with those events.

#### Scenario: Tracker enabled later
- **WHEN** the user enables the bottle tracker on an existing baby
- **THEN** the bottle entities become available

#### Scenario: Tracker disabled and re-enabled
- **WHEN** the bottle tracker is disabled and enabled again
- **THEN** its sensors show the bottles recorded before it was disabled

### Requirement: One device per baby
Each baby SHALL be represented as one Home Assistant device named after the baby, and every entity that belongs to that baby SHALL be attached to that device.

#### Scenario: Entities grouped under the baby
- **WHEN** a baby named "Alice" has been added
- **THEN** a device named "Alice" exists and lists all of that baby's entities

### Requirement: Multiple babies
The integration SHALL support more than one baby at the same time, and the events, entities and daily values of one baby SHALL NOT affect another.

#### Scenario: Two babies logged independently
- **WHEN** babies "Alice" and "Bruno" exist and a diaper change is logged for "Alice"
- **THEN** only the sensors of "Alice" change

#### Scenario: Duplicate name rejected
- **WHEN** the user adds a baby with the same name as an existing baby
- **THEN** the form shows an error and no second baby is created

### Requirement: Edit a baby
The user SHALL be able to change a baby's name and birth date after creation without losing any recorded event.

#### Scenario: Birth date set later
- **WHEN** the user sets the birth date of an existing baby that has recorded events
- **THEN** the birth date is saved and all previously recorded events remain

### Requirement: Removing a baby keeps its history
Removing a baby from the integrations page SHALL remove its device and entities and SHALL keep its recorded events.

#### Scenario: Baby removed
- **WHEN** the user removes the baby "Alice"
- **THEN** the device and entities of "Alice" are gone and her events are still stored

### Requirement: Re-attach history
When the user adds a baby whose name matches a removed baby with stored history, the flow SHALL offer to restore that history or to start empty. Restoring SHALL make every stored event of that baby available again.

#### Scenario: Removed and added again
- **WHEN** "Alice" is removed and then added again with the option to restore history
- **THEN** her sensors and event listings include the events recorded before she was removed

#### Scenario: Start empty
- **WHEN** "Alice" is added again with the option to start empty
- **THEN** she has no events and the earlier history stays stored, unattached

### Requirement: Delete history explicitly
The integration SHALL provide a service that permanently deletes the stored history of a removed baby, identified by name. It SHALL refuse to act on a baby that is currently configured.

#### Scenario: History purged
- **WHEN** the purge service is called with the name of a removed baby
- **THEN** that baby's stored events are permanently deleted and other babies are untouched

#### Scenario: Baby still configured
- **WHEN** the purge service is called with the name of a baby that is currently configured
- **THEN** the call fails with an error and nothing is deleted
