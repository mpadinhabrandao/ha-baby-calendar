# Spec Delta

## Purpose

Defines what is specific to tracking sleep on top of the shared timer behaviour: the sleep tracker, its use as the baby's sleeping state, and the time awake.

## ADDED Requirements

### Requirement: Sleep tracker
Sleep SHALL be a timed tracker that the user can enable per baby, with its own start, stop and log services and its own switch, duration input, button and sensors. A sleep event SHALL carry no fields other than its times and optional notes.

#### Scenario: Enabled for a baby
- **WHEN** the user enables the sleep tracker on a baby
- **THEN** the sleep switch, duration input, button and sensors become available

#### Scenario: Nap timed with the switch
- **WHEN** the sleep switch is turned on at 14:00 and turned off at 14:45
- **THEN** a finished sleep event of forty-five minutes is recorded

### Requirement: Sleeping state
The sleep switch SHALL be usable as the baby's sleeping state in automations: it SHALL be on exactly while a sleep event is in progress.

#### Scenario: Automation condition
- **WHEN** a sleep timer is running
- **THEN** an automation condition on the sleep switch being on is true

#### Scenario: Sleep logged afterwards
- **WHEN** a finished sleep is logged by its duration
- **THEN** the sleep switch stays off

### Requirement: Awake since
A baby with the sleep tracker SHALL have a timestamp sensor with the end of the sleep that ended most recently. It SHALL report an unknown state while a sleep is in progress and when no sleep has ended yet.

#### Scenario: After a nap
- **WHEN** a nap ends at 14:45 and no sleep is in progress
- **THEN** the awake since sensor shows 14:45

#### Scenario: Asleep
- **WHEN** a sleep timer is running
- **THEN** the awake since sensor reports an unknown state
