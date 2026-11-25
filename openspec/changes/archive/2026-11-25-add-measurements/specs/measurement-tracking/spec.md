# Spec Delta

## Purpose

Defines how weight, length and temperature readings are logged for a baby, and how the latest reading of each is reported and charted over time.

## ADDED Requirements

### Requirement: Measurement trackers
Weight in grams, length in centimetres and temperature in degrees Celsius SHALL each be a tracker that the user can enable per baby, independently of the others.

#### Scenario: Only weight enabled
- **WHEN** the user enables the weight tracker and not the length or temperature trackers
- **THEN** the baby has the weight entities and no length or temperature entities

### Requirement: Log a reading
Each measurement tracker SHALL provide a service to log a reading for a baby. The value is required. Notes and time are optional.

#### Scenario: Weight logged
- **WHEN** a weight of 3450 is logged
- **THEN** a weight event with the value 3450 g is recorded at the current time

#### Scenario: Reading from a past check-up
- **WHEN** a length of 51.5 is logged with a time of three days ago
- **THEN** a length event with the value 51.5 cm is recorded at that time

#### Scenario: Value missing
- **WHEN** a reading is logged without a value
- **THEN** the call fails with an error and nothing is recorded

### Requirement: Plausible range
A reading outside its plausible range SHALL be rejected with an error: weight from 300 to 30000 g, length from 20 to 130 cm, temperature from 30.0 to 45.0 degrees Celsius.

#### Scenario: Low but within range
- **WHEN** a weight of 345 is logged
- **THEN** the event is recorded, because 345 g is within the accepted range

#### Scenario: Kilograms typed instead of grams
- **WHEN** a weight of 3.4 is logged
- **THEN** the call fails with an error naming the accepted range and nothing is recorded

#### Scenario: Temperature typo
- **WHEN** a temperature of 375 is logged
- **THEN** the call fails with an error and nothing is recorded

### Requirement: Dashboard entities
Each enabled measurement tracker SHALL have a number entity for the value, in the tracker's unit, and a button that logs a reading with that value, following the baby's "minutes ago" input. The value SHALL return to zero after a reading and SHALL be zero after a restart. Weight SHALL be adjustable in steps of 1 g, length in steps of 0.5 cm and temperature in steps of 0.1 degrees.

#### Scenario: Temperature from the dashboard
- **WHEN** the temperature input shows 37.8 and the temperature button is pressed
- **THEN** a temperature reading of 37.8 is recorded and the input shows 0

#### Scenario: Stray press
- **WHEN** the weight button is pressed while the weight input is 0
- **THEN** the press fails with an error and nothing is recorded

#### Scenario: Input out of range
- **WHEN** the button is pressed while the input holds a value outside the plausible range
- **THEN** the press fails with an error and nothing is recorded

### Requirement: Latest reading sensors
Each enabled measurement tracker SHALL have a sensor whose state is the value of the reading with the most recent time, in the tracker's unit, and a timestamp sensor with the time of that reading. With no readings both SHALL report an unknown state.

#### Scenario: New reading
- **WHEN** a weight of 3600 is logged after an earlier reading of 3450
- **THEN** the weight sensor shows 3600 g and the timestamp sensor shows the time of the new reading

#### Scenario: Older reading added later
- **WHEN** a weight dated last week is logged after a reading dated today
- **THEN** the weight sensor still shows today's reading

#### Scenario: Latest reading deleted
- **WHEN** the most recent reading is deleted
- **THEN** the sensors show the previous reading and its time

#### Scenario: No readings yet
- **WHEN** a measurement tracker has no readings
- **THEN** both sensors report an unknown state

### Requirement: Temperature expires
The temperature value sensor SHALL report an unknown state once its latest reading is more than 24 hours old. The reading SHALL remain in the event log and the timestamp sensor SHALL keep showing its time. Weight and length SHALL NOT expire.

#### Scenario: Yesterday's fever
- **WHEN** the latest temperature reading was taken 25 hours ago
- **THEN** the temperature sensor reports an unknown state and the timestamp sensor still shows when it was taken

#### Scenario: Weight from last month
- **WHEN** the latest weight reading was taken a month ago
- **THEN** the weight sensor still shows it

### Requirement: Long-term history
The weight and length sensors SHALL be recorded in Home Assistant long-term statistics, so that their evolution can be charted beyond the recorder retention period. The chart SHALL reflect readings from the moment they are logged; a reading logged with a past time SHALL appear in the event log at that time and SHALL NOT be required to appear in the chart at that time.

#### Scenario: Growth over three months
- **WHEN** weight readings have been logged as they were taken over three months
- **THEN** a statistics chart of the weight sensor shows the evolution over the whole period

#### Scenario: Check-up entered a week late
- **WHEN** a weight is logged today with a time of last week
- **THEN** listing last week's events returns it, and the chart is not required to show it last week

### Requirement: No interpretation
The integration SHALL NOT classify, compare or comment on a reading. It SHALL NOT compute percentiles and SHALL NOT raise alerts based on a value.

#### Scenario: High temperature
- **WHEN** a temperature of 39.5 is logged
- **THEN** the reading is recorded and the integration raises no alert or notification of its own
