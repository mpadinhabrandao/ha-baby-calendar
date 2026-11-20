# Proposal

## Why

Sensors answer "when was the last one" and "how many today", but not "what did yesterday look like" or "what happened between 2 and 6 a.m.". A calendar shows a baby's day as a timeline, and Home Assistant already has a calendar dashboard and card. It is also the only stock screen where an older entry can be found, corrected, annotated or deleted without calling a service, which is why this change comes right after the trackers a newborn needs. Exposing the event log as a calendar is the feature this integration is named after.

## What Changes

- One calendar entity per baby, showing every recorded event of every tracker.
- Each event has a title with an emoji and its details (for example "💩 Dirty diaper (soft)", "🍼 Bottle 90 ml formula", "😴 Sleep 1 h 20 min"), in the language of the instance.
- Timed events span their real start and end. Instantaneous events appear as short blocks at their time.
- From the Home Assistant calendar, an event's time can be changed, a note can be added or edited, and an event can be deleted. The sensors follow immediately. This is where notes are written.
- Events are not created from the calendar: logging stays with the buttons, switches and services.

Depends on `add-core-tracking` and `add-timed-tracking` being implemented and archived first. Trackers added by later changes bring their own calendar presentation.

Out of scope: an ICS feed or any other way to see the calendar in a phone's calendar app (not planned for now), one calendar per tracker, future events, creating events from the calendar, recurring events.

## Capabilities

### New Capabilities

- `calendar-view`: the per-baby calendar entity, how each kind of event is presented in it, and which corrections can be made from it.

### Modified Capabilities

None.

## Impact

- `custom_components/baby_calendar/`: a new `calendar` platform, a presentation function per tracker module, title strings.
- No schema migration, no new dependencies, no network access.
