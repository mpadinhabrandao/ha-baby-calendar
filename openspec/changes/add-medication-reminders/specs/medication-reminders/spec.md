# Spec Delta

## Purpose

Defines the schedules a medication can have, when a dose is considered due, and how a due dose is signalled to the user through sensors and an automation blueprint.

## ADDED Requirements

### Requirement: Schedule types
A medication's schedule SHALL be one of: none; fixed times, a list of one or more times of day; or interval, a number of hours since the last dose.

#### Scenario: Fixed times
- **WHEN** a medication is given the fixed times 09:00 and 21:00
- **THEN** it has two scheduled doses every day

#### Scenario: No times given
- **WHEN** the user selects fixed times and enters no time
- **THEN** the form shows an error and the medication is not saved

#### Scenario: Invalid time
- **WHEN** the user enters "25:00" as a fixed time
- **THEN** the form shows an error and the medication is not saved

#### Scenario: Interval of zero
- **WHEN** the user selects interval and enters 0 hours
- **THEN** the form shows an error and the medication is not saved

### Requirement: Doses satisfy scheduled times
With fixed times, each scheduled time of each day SHALL be satisfied by at most one dose, and each dose SHALL satisfy at most one scheduled time: the scheduled time nearest to the dose, if the dose is closer to it than to any other scheduled time and that time is not already satisfied. A dose that satisfies no scheduled time SHALL be recorded and SHALL have no effect on reminders.

#### Scenario: Given early
- **WHEN** the schedule is 09:00 and a dose is recorded at 08:40
- **THEN** the 09:00 time of that day is satisfied

#### Scenario: Logged twice
- **WHEN** the schedule is 09:00 and 21:00 and two doses are recorded at 09:05 and 09:06
- **THEN** the 09:00 time is satisfied and the 21:00 time is not

#### Scenario: Given after midnight
- **WHEN** the schedule is 09:00 and 23:00 and a dose is recorded at 00:10
- **THEN** the 23:00 time of the previous day is satisfied and the 09:00 time is not

### Requirement: Due with fixed times
With fixed times, a dose SHALL be due from a scheduled time until that time is satisfied or the next scheduled time arrives, whichever comes first. Local midnight SHALL NOT end a due dose. Scheduled times SHALL be local wall-clock times in the Home Assistant time zone.

#### Scenario: Time reached
- **WHEN** the schedule is 09:00, no dose was recorded and the time reaches 09:00
- **THEN** a dose becomes due

#### Scenario: Not due when given early
- **WHEN** the schedule is 09:00 and a dose is recorded at 08:40
- **THEN** no dose becomes due at 09:00

#### Scenario: Still due after midnight
- **WHEN** the schedule is 09:00 and 23:00, the 23:00 dose was not recorded and the time passes midnight
- **THEN** the dose is still due

#### Scenario: Superseded by the next time
- **WHEN** the 23:00 dose was never recorded and the time reaches 09:00
- **THEN** one dose is due, for 09:00, and the missed 23:00 time is no longer waited for

#### Scenario: Evening reminder after a double log
- **WHEN** the schedule is 09:00 and 21:00, two doses were recorded in the morning and the time reaches 21:00
- **THEN** a dose becomes due

#### Scenario: Added after its time
- **WHEN** a medication with the fixed time 09:00 is added, or reactivated, at 16:00
- **THEN** it is not due until 09:00 the next day

### Requirement: Due with an interval
With an interval, a dose SHALL be due once the interval has elapsed since the last recorded dose. With no recorded dose, no dose SHALL be due.

#### Scenario: Interval elapsed
- **WHEN** the interval is 6 hours and the last dose was recorded at 08:00
- **THEN** a dose becomes due at 14:00

#### Scenario: Never given
- **WHEN** an interval medication has no recorded dose
- **THEN** no dose is due

### Requirement: Recording a dose clears due
Recording a dose that satisfies the schedule SHALL end the due state immediately. Correcting or deleting a dose SHALL recompute the due state.

#### Scenario: Dose recorded while due
- **WHEN** a dose is due and a dose is recorded
- **THEN** the dose is no longer due

#### Scenario: Dose deleted
- **WHEN** the dose that cleared the due state is deleted
- **THEN** the dose is due again

### Requirement: Due and next dose entities
Each active medication with a schedule SHALL have a binary sensor that is on while a dose is due, with the baby's name, the medication name and the dose text as attributes, and a timestamp sensor with the time of the next dose. While a dose is due the next dose sensor SHALL show the scheduled time that is due. It SHALL report an unknown state when it cannot be determined. A medication with no schedule SHALL have neither entity.

#### Scenario: Next dose with fixed times
- **WHEN** the schedule is 09:00 and 21:00 and the morning dose has been recorded
- **THEN** the next dose sensor shows today at 21:00

#### Scenario: Next dose with an interval
- **WHEN** the interval is 6 hours and the last dose was recorded at 08:00
- **THEN** the next dose sensor shows 14:00

#### Scenario: Overdue
- **WHEN** a dose scheduled for 09:00 has not been recorded and it is 10:30
- **THEN** the due sensor is on and the next dose sensor shows 09:00

#### Scenario: Names for the reminder
- **WHEN** a dose of "Vitamin D" with the dose text "1 drop" is due for the baby "Alice"
- **THEN** the due sensor's attributes give "Alice", "Vitamin D" and "1 drop"

#### Scenario: No schedule
- **WHEN** a medication has no schedule
- **THEN** it has no due sensor and no next dose sensor

### Requirement: Reminder blueprint
The project SHALL provide an automation blueprint that, for a chosen medication, sends a notification through an action chosen by the user when a dose becomes due, and optionally repeats it at a chosen interval until the dose is recorded.

#### Scenario: Reminder on a phone
- **WHEN** an automation created from the blueprint targets a phone and a dose becomes due
- **THEN** the phone receives a notification naming the baby and the medication

#### Scenario: Repeat until recorded
- **WHEN** the blueprint's repeat is set to 15 minutes and the dose stays due
- **THEN** the notification is sent again every 15 minutes and stops once a dose is recorded

### Requirement: No notifications from the integration
The integration SHALL NOT send notifications itself. A due dose SHALL be signalled only through its entities, which automations, including those created from the blueprint, act on.

#### Scenario: Due with no automation
- **WHEN** a dose becomes due and no automation uses its due sensor
- **THEN** the due sensor turns on and no notification is sent

### Requirement: Due state across restarts
The due state SHALL be recomputed when Home Assistant starts. A dose that became due while Home Assistant was not running SHALL be shown as due after start.

#### Scenario: Down at dose time
- **WHEN** Home Assistant is stopped at 08:50 and started at 09:10 with a 09:00 dose not recorded
- **THEN** the due sensor is on after start

#### Scenario: Restart while due
- **WHEN** a dose is due and Home Assistant restarts
- **THEN** the due sensor is on after start
