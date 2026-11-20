# Proposal

## Why

Babies are given vitamin D every day for months, and at times a course of medicine every few hours. Tired parents forget a dose, or give it twice because each thought the other had not. A shared record of each dose answers "has she had it?", and a reminder when a dose is due removes the need to remember.

## What Changes

- Medications are defined by the user, per baby: a name, an optional dose text (informational, for example "1 drop") and an optional schedule. They are added, edited, deactivated and removed from the baby's configuration in the Home Assistant UI. Removing a medication keeps the doses already recorded.
- Two schedule types, chosen per medication: fixed times of day (vitamin D at 09:00) or an interval since the last dose (every 6 hours). A medication can also have no schedule and simply be logged. With fixed times, each scheduled time is satisfied by a dose given near it, and a missed dose stays due until it is given or the next scheduled time arrives, including across midnight.
- A service and a one-tap button per medication to record a dose, with optional notes and time.
- Per medication: sensors for the last dose, today's doses and the next dose, and a binary sensor that is on while a dose is due.
- Reminders through the due sensor and a ready-made automation blueprint that sends the notification wherever the user wants (a phone, a speaker, a light), optionally repeating until the dose is recorded. The integration itself sends no notifications.
- Doses are corrected, deleted and listed through the existing event services.

Depends on `add-core-tracking` being implemented and archived first. If `add-calendar-view` is in place, doses appear in the calendar as "💊" followed by the medication name.

Out of scope: notifications sent directly by the integration, recording the dose amount per intake, stock or refill tracking, courses with an end date, weekly or more complex schedules, and any suggestion of a medicine, dose or schedule. Reminders follow only the schedule the user entered.

## Capabilities

### New Capabilities

- `medication-tracking`: defining medications for a baby, recording doses and the sensors derived from them.
- `medication-reminders`: schedules, when a dose is due, and the sensors and blueprint through which reminders reach the user.

### Modified Capabilities

None.

## Impact

- `custom_components/baby_calendar/`: a medication tracker module, a medications menu in the options flow, services, a new `binary_sensor` platform, sensors, buttons, a scheduler, translations.
- A new `blueprints/automation/baby_calendar/medication_reminder.yaml` in the repository, imported by the user from its URL.
- No network access.
- No schema migration and no new dependencies.
