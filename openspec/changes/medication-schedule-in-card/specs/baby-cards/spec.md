## ADDED Requirements

### Requirement: Medication schedule in the card
For each medication it shows, the Medications card SHALL show its schedule (the fixed times, the interval, or that it has none) and its next dose from the medication's next dose sensor: the time, with "tomorrow" or the weekday when it is not today, or, for a dose due now, the time it has been due since. It SHALL show no next dose when the sensor has no value.

#### Scenario: Fixed times
- **WHEN** "Vitamin D" is taken at 09:30 and 21:30, it is 14:00, and today's 09:30 dose was given
- **THEN** the card shows "At 09:30 and 21:30" and "Next 21:30" for Vitamin D

#### Scenario: Next dose tomorrow
- **WHEN** "Vitamin D" is taken at 09:30, it is 14:00, and today's dose was given
- **THEN** the card shows "Next tomorrow 09:30"

#### Scenario: Due since
- **WHEN** the 09:30 dose of "Vitamin D" has not been given and it is 10:15
- **THEN** the card shows Vitamin D as due since 09:30

#### Scenario: Interval
- **WHEN** "Paracetamol" is taken every 8 h, the last dose was at 07:00, and it is 10:00
- **THEN** the card shows "Every 8 h" and "Next 15:00"

#### Scenario: No schedule
- **WHEN** "Iron" has no schedule and the card lists every active medication
- **THEN** the card shows "No schedule" for Iron and no next dose
