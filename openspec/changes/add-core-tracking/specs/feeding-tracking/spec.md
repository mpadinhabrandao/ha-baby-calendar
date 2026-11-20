# Spec Delta

## Purpose

Defines how bottles are logged for a baby and which sensors report the last bottle and the totals for the current day.

## ADDED Requirements

### Requirement: Log a bottle
The integration SHALL provide a service to log a bottle for a baby. The amount in millilitres is required and SHALL be greater than zero. The content, formula or breast milk, is optional, as are notes and time.

#### Scenario: Bottle with content
- **WHEN** a bottle of 90 ml of formula is logged
- **THEN** a bottle event with 90 ml and the content formula is recorded

#### Scenario: Small first feeds
- **WHEN** a bottle of 7 ml is logged
- **THEN** a bottle event with 7 ml is recorded

#### Scenario: Amount missing or zero
- **WHEN** a bottle is logged without an amount or with the amount 0
- **THEN** the call fails with an error and nothing is recorded

#### Scenario: Invalid content
- **WHEN** a bottle is logged with a content other than formula or breast milk
- **THEN** the call fails with an error and nothing is recorded

### Requirement: Bottle dashboard entities
A baby with the bottle tracker SHALL have a number entity for the amount in ml, adjustable in steps of 1 ml, a selector for the content with a "not specified" initial choice, and a button that logs a bottle with the current amount and content. The amount and the content SHALL be kept after a press and across restarts.

#### Scenario: Usual bottle
- **WHEN** the amount shows 90, the content shows formula and the bottle button is pressed
- **THEN** a 90 ml formula bottle is recorded and the amount still shows 90

#### Scenario: Amount at zero
- **WHEN** the bottle button is pressed while the amount is 0
- **THEN** the press fails with an error and nothing is recorded

### Requirement: Bottle sensors
A baby with the bottle tracker SHALL have a timestamp sensor for the last bottle, with its amount and content as attributes, and daily sensors for the number of bottles and the total millilitres of today.

#### Scenario: Two bottles
- **WHEN** bottles of 90 ml and 120 ml are logged today
- **THEN** the bottles sensor shows 2 and the millilitres sensor shows 210

#### Scenario: Amount corrected
- **WHEN** the 120 ml bottle is corrected to 100 ml
- **THEN** the millilitres sensor shows 190

#### Scenario: No bottles yet
- **WHEN** a baby has no bottle events
- **THEN** the last bottle sensor reports an unknown state
