# Proposal

## Why

Breastfeeding and sleep are measured in time, and they are logged while they happen: a parent starts a feed, and stops it when the baby is done. The trackers from `add-core-tracking` only record instantaneous events, so the two things parents of a newborn track most cannot be recorded yet. And because the family may breastfeed, bottle-feed or both, "when did she last eat" must have one answer.

## What Changes

- Two new trackers the user can enable per baby: breastfeeding (with a side, left or right) and sleep. Their events have a start, an end and therefore a duration.
- A timer per timed tracker: services to start and stop it, and a switch entity that does the same from a dashboard, an automation, a Zigbee button or an NFC tag. A running timer keeps running until it is stopped, including across restarts.
- Logging a finished feed or sleep after the fact by giving its duration: through a service, or from a dashboard with a duration input (minutes) and a button.
- Daily durations are split at local midnight: a sleep from 23:00 to 06:00 counts one hour on the first day and six on the second, and a running timer adds to today as it runs.
- Left then right within 30 minutes is two entries but one feed in "feeds today". The side selector switches to the other side when a feed ends.
- A combined "last feed" sensor across breastfeeding and bottle, and an "awake since" sensor for sleep.
- Event correction and listing gain the end time, the duration and whether the event is in progress. Listing returns timed events that overlap the requested period.

Depends on `add-core-tracking` being implemented and archived first. The existing trackers behave exactly as before. This change extends the `update_event` and `list_events` services of `event-log` and the tracker list of `baby-profile`; those extensions are specified here as new requirements.

Out of scope: automatic stop after a maximum duration, switching side inside one entry, pause and resume, resuming a finished entry.

## Capabilities

### New Capabilities

- `timers`: the behaviour shared by every timed tracker, covering start and stop, the timer switch, logging a finished event by duration, correction, and how durations appear in sensors and listings.
- `breastfeeding-tracking`: what is specific to breastfeeding: the side, how sides are grouped into feeds, and the combined last feed.
- `sleep-tracking`: what is specific to sleep: the sleeping state and the time awake.

### Modified Capabilities

None.

## Impact

- `custom_components/baby_calendar/`: two tracker modules, store queries, services, a new `switch` platform, sensors, translations. The tracker list in the baby flow gains two entries.
- No schema migration: the event table already has an end time column.
- No new dependencies. No network access.
