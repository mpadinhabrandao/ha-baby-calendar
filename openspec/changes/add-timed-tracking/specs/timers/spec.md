# Spec Delta

## Purpose

Defines the behaviour shared by timed trackers, whose events have a start and an end: starting and stopping a timer, logging a finished event by its duration, and reporting durations in sensors and listings.

## ADDED Requirements

### Requirement: Start a timer
Each timed tracker SHALL provide a service that starts its timer for a baby, creating an in-progress event. Notes and a start time in the past are optional.

#### Scenario: Started now
- **WHEN** a timed tracker's timer is started with no time
- **THEN** an in-progress event with the current time as start exists

#### Scenario: Started late
- **WHEN** the timer is started with a start time ten minutes in the past
- **THEN** the in-progress event starts at that time

### Requirement: One running timer per tracker
A timed tracker SHALL have at most one in-progress event per baby. Timers of different trackers and of different babies SHALL run independently.

#### Scenario: Already running
- **WHEN** a timer start is requested while that tracker's timer is running
- **THEN** the call fails with an error and the running event is unchanged

#### Scenario: Two trackers at once
- **WHEN** the sleep timer is started while the breastfeeding timer is running
- **THEN** both timers run

### Requirement: Stop a timer
Each timed tracker SHALL provide a service that stops its running timer, setting the end of the in-progress event to the current time or to a given time. The end SHALL be later than the start and SHALL NOT be in the future.

#### Scenario: Stopped now
- **WHEN** a timer started twelve minutes ago is stopped
- **THEN** the event is finished with a duration of twelve minutes

#### Scenario: Stopped with an earlier end
- **WHEN** a timer is stopped with an end time five minutes in the past
- **THEN** the event ends at that time

#### Scenario: Nothing running
- **WHEN** a stop is requested with no running timer
- **THEN** the call fails with an error

#### Scenario: End before start
- **WHEN** a stop is requested with an end time earlier than the event's start
- **THEN** the call fails with an error and the timer keeps running

### Requirement: Timer keeps running
A running timer SHALL keep running until it is stopped, its event is deleted or its tracker is disabled. It SHALL NOT be stopped automatically by elapsed time, by local midnight or by a Home Assistant restart.

#### Scenario: Restart while running
- **WHEN** Home Assistant restarts while a timer is running
- **THEN** the timer is still running with its original start time

#### Scenario: Forgotten timer
- **WHEN** a timer is left running for a day and then stopped with the real end time
- **THEN** the event is finished with that end time

### Requirement: Disabling a tracker stops its timer
When a timed tracker is disabled for a baby while its timer is running, the in-progress event SHALL be finished at that moment.

#### Scenario: Disabled while running
- **WHEN** the sleep tracker is disabled while a sleep timer is running
- **THEN** the sleep event is finished with the current time as its end

### Requirement: Timer switch
Each enabled timed tracker SHALL have a switch entity that is on while its timer is running and exposes the start time. Turning it on SHALL start the timer, applying the baby's "minutes ago" input to the start. Turning it off SHALL stop it, applying "minutes ago" to the end.

#### Scenario: Turned on and off
- **WHEN** the switch is turned on and, eight minutes later, turned off
- **THEN** a finished event of eight minutes exists and the switch is off

#### Scenario: Started ten minutes ago
- **WHEN** "minutes ago" is set to 10 and the switch is turned on
- **THEN** the in-progress event starts ten minutes in the past and "minutes ago" shows 0

#### Scenario: Forgot to stop
- **WHEN** "minutes ago" is set to 15 and the switch of a running timer is turned off
- **THEN** the event ends fifteen minutes in the past

#### Scenario: Started by service
- **WHEN** a timer is started through the service
- **THEN** the switch of that tracker turns on

### Requirement: Log a finished event by service
Each timed tracker SHALL provide a service that records a finished event without using the timer. The duration is required and SHALL be greater than zero. With no time given the event SHALL end at the current time; a given time SHALL be the start. The end SHALL NOT be in the future.

#### Scenario: Logged afterwards
- **WHEN** a sleep is logged with a duration of ninety minutes and no time
- **THEN** a finished event ending now and starting ninety minutes ago is recorded

#### Scenario: Start time given
- **WHEN** a sleep is logged with a start of 14:00 and a duration of forty minutes
- **THEN** a finished event from 14:00 to 14:40 is recorded

#### Scenario: Duration missing or zero
- **WHEN** a finished event is logged without a duration or with a duration of zero
- **THEN** the call fails with an error and nothing is recorded

#### Scenario: Running timer untouched
- **WHEN** a finished event is logged while the tracker's timer is running
- **THEN** the finished event is recorded and the timer keeps running

### Requirement: Log a finished event from a dashboard
Each enabled timed tracker SHALL have a number entity for a duration in minutes and a button that records a finished event of that duration, ending at the current time minus the baby's "minutes ago". The duration input SHALL return to zero after an entry and SHALL be zero after a restart.

#### Scenario: Logged from the dashboard
- **WHEN** the duration input shows 15 and the button is pressed
- **THEN** a finished event ending now and starting fifteen minutes ago is recorded and the input shows 0

#### Scenario: Duration input at zero
- **WHEN** the button is pressed while the duration input is 0
- **THEN** the press fails with an error and nothing is recorded

### Requirement: Correct a timed event
The event correction service SHALL allow changing the start and the end of a timed event. The end SHALL remain later than the start and SHALL NOT be in the future. The end of an in-progress event SHALL only be set by stopping its timer.

#### Scenario: End corrected
- **WHEN** the end of a finished event is changed to ten minutes earlier
- **THEN** its duration is ten minutes shorter and the sensors reflect it

#### Scenario: Invalid end
- **WHEN** the end of an event is changed to a time before its start
- **THEN** the call fails with an error and the event is unchanged

#### Scenario: Start of a running timer corrected
- **WHEN** the start of an in-progress event is changed to five minutes earlier
- **THEN** the timer keeps running from the new start

### Requirement: Undo and timers
The "undo" button SHALL treat starting a timer and logging a finished event as entries. Undoing a timer that is still running SHALL delete the in-progress event.

#### Scenario: Timer started by mistake
- **WHEN** the sleep switch is turned on by mistake and "undo" is pressed
- **THEN** no sleep event exists and the switch is off

### Requirement: Last-event sensor
Each enabled timed tracker SHALL have a timestamp sensor showing the start of its most recent event, finished or in progress, with its end, its duration and whether it is in progress as attributes.

#### Scenario: While running
- **WHEN** a timer has been running since 10:00
- **THEN** the last-event sensor shows 10:00 and is marked as in progress

#### Scenario: Finished
- **WHEN** a sleep from 14:00 to 14:45 is the most recent event
- **THEN** the sensor shows 14:00 with the end 14:45 and a duration of forty-five minutes

### Requirement: Daily duration split at midnight
Each enabled timed tracker SHALL have a daily sensor with the total time of its events that falls within today, local midnight to local midnight. An event that crosses midnight SHALL count on each day only for the part within that day. A running timer SHALL count up to the current time, updated at least once a minute.

#### Scenario: Two finished events
- **WHEN** events of eight and six minutes are finished today
- **THEN** the daily duration shows fourteen minutes

#### Scenario: Night sleep
- **WHEN** a sleep starts at 23:00 and is stopped at 06:00 the next day
- **THEN** the first day's duration includes one hour of it and the second day's includes six hours

#### Scenario: Evening sleep
- **WHEN** a sleep starts at 18:00 and is stopped at 01:00 the next day
- **THEN** the first day's duration includes six hours of it and the second day's includes one hour

#### Scenario: Still running
- **WHEN** a timer started at 10:00 is still running at 10:30
- **THEN** the daily duration includes thirty minutes for it

### Requirement: Daily count
Each enabled timed tracker SHALL have a daily sensor counting the events that started today, including one in progress.

#### Scenario: Started before midnight
- **WHEN** a sleep started at 23:00 yesterday and ended at 06:00 today, and a nap started at 10:00 today
- **THEN** today's count shows 1

### Requirement: Durations in listings
Event listings SHALL include each timed event's end, duration and in-progress state, and SHALL return every timed event that overlaps the requested period, not only those that start within it.

#### Scenario: Listing a finished event
- **WHEN** events are listed for a day containing a finished forty-minute sleep
- **THEN** that event is returned with its end time and a duration of forty minutes

#### Scenario: Overlapping the period
- **WHEN** events are listed for today and a sleep ran from 23:00 yesterday to 06:00 today
- **THEN** that sleep is returned
