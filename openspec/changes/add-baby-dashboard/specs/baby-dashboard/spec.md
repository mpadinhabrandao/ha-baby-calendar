# Spec Delta

## Purpose

Gives each baby a ready-made dashboard view that shows its logging buttons, medications, totals and inputs, and follows the trackers and medications the baby has without being edited.

## ADDED Requirements

### Requirement: Ready-made view per baby
The project SHALL provide a dashboard view, in the repository, that the user adds to Home Assistant and points at one baby by the baby's name. A second baby SHALL be covered by a second copy of the view with that baby's name.

#### Scenario: View for one baby
- **WHEN** the view is added with the name "Alice"
- **THEN** it shows Alice's entities and none of another baby's

#### Scenario: Two babies
- **WHEN** a second view is added with the name "Bruno"
- **THEN** each view shows only its own baby's entities

### Requirement: View follows the baby's entities
The view SHALL show the entities the baby has at the time it is opened, without being edited: entities of a tracker enabled later and of a medication added later SHALL appear, and those of a tracker disabled or a medication removed or deactivated SHALL disappear.

#### Scenario: Medication added later
- **WHEN** a medication is added to the baby after the view was set up
- **THEN** its dose button and its sensors appear in the medications section

#### Scenario: Tracker disabled
- **WHEN** the sleep tracker is disabled for the baby
- **THEN** its timer, button and sensors no longer appear

### Requirement: Sections in logging order
The view SHALL show, in this order: logging buttons and running timers; the stool type buttons; medications; today's totals; last times; measurements; the inputs; the calendar. A section with no entities SHALL not be shown.

#### Scenario: Logging first
- **WHEN** the view is opened on a phone
- **THEN** the logging buttons are at the top, before any sensor

#### Scenario: Baby with diapers only
- **WHEN** the baby has only the diaper tracker
- **THEN** no medications, measurements or timer section is shown

### Requirement: Stool type only while asked
The stool type buttons SHALL be shown only while the baby's stool prompt is on, and SHALL not be among the logging buttons.

#### Scenario: Dirty diaper logged
- **WHEN** a dirty diaper is logged with no stool type
- **THEN** the stool type buttons appear, and disappear once a type is set

### Requirement: Entities identifiable in any language
Every medication entity SHALL have the attribute `medication` with the medication's name, and every stool type button SHALL have the attribute `stool_type` with its type, so a view can select them whatever the language of Home Assistant.

#### Scenario: Portuguese instance
- **WHEN** Home Assistant is in Portuguese and the baby has "Vitamina D"
- **THEN** the "Vitamina D" entities have `medication: Vitamina D` and the medications section shows them

#### Scenario: Stool buttons
- **WHEN** the diaper tracker is enabled
- **THEN** each stool type button has `stool_type` set to its type

### Requirement: Dependency stated
The documentation SHALL state that the view needs the auto-entities card, how to install it from the Marketplace and its licence, and that the integration itself works without it.

#### Scenario: Without auto-entities
- **WHEN** auto-entities is not installed
- **THEN** the integration and its entities work, and the README says the view will not render until the card is installed
