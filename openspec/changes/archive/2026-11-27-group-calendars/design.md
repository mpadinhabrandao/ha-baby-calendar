# Design

## Context

`calendar.py` creates one `BabyCalendar` per baby. It has the unique id `<baby_id>_calendar`, lists every tracker through `store.list_events(..., tracker=None, timed=...)` and handles update and delete for any event of the baby. Entities of a disabled tracker are removed at setup by `_remove_disabled_tracker_entities` in `__init__.py`, which matches registry entries by unique id. Medication is not one of the options' trackers: a baby "has medication" when its options hold at least one medication.

## Goals / Non-Goals

**Goals:**
- Filter entries with Home Assistant's own calendar panel and calendar card, with no new UI.
- Keep every behaviour of today's calendar (titles, notes, placement, edits, deletion) per group.

**Non-Goals:**
- A calendar with every entry, or user-defined groups.
- Changes to the event store's data, the services or the cards.

## Decisions

### Groups as a fixed mapping
A constant maps each group key to its tracker keys:
- `feeding`: bottle, breastfeeding, solids, pumping;
- `diapers`: diaper;
- `sleep`: sleep;
- `health`: temperature, weight, length, medication.

The mapping is checked at import time so that every key of `TRACKERS` belongs to exactly one group; a tracker added later fails the tests until it is placed in a group.

Each calendar has the unique id `<baby_id>_calendar_<group>` and the translation key `calendar_<group>`. Its entity id is generated once from the translated name, for example `calendar.duarte_alimentacao` on a Portuguese instance.

- Alternative: one calendar per tracker (ten per baby). Rejected: it crowds the calendar panel, and fever and medication belong together.

### Which calendars exist
`async_setup_entry` of the calendar platform creates a group's calendar when any of these holds:
- one of the group's trackers is in the options' trackers;
- the group is Health and the baby has a medication;
- the store has an event of the group's trackers for the baby.

The last condition is a new store query, `trackers_with_events(baby_id)`, which returns the distinct tracker keys of the baby's events and runs once per setup.

Setup in `__init__.py` applies the same rule to remove stale registry entries:
- the old `<baby_id>_calendar`;
- any `<baby_id>_calendar_<group>` whose group no longer qualifies.

The options flow already reloads the entry, so enabling or disabling a tracker updates the calendars.

- Alternative: always create all four. Rejected: a baby that only tracks diapers would add three empty calendars to the calendar panel, which lists every calendar of the house.

### Listing per group
`store.list_events` gains a `trackers` collection filter, a SQL `tracker IN (...)`. The calendar passes its group's trackers, and only those of them that are timed as `timed`. The existing single `tracker` argument used by the services keeps working.

### Own entries only
`_own_event` also checks that the event's tracker belongs to the calendar's group and raises the existing `unknown_event` error otherwise. The calendar UI only offers a calendar's own events, so this guards the `calendar.update_event` and `calendar.delete_event` actions.

### State per group
The `event` property looks only at the group's timed trackers: breastfeeding for Feeding, sleep for Sleep. The other calendars have no timed tracker and are always off.

## Risks / Trade-offs

- [Dashboards and automations using `calendar.<baby>_calendar` break] → Marked BREAKING. The README explains the replacement, and the Teste dashboard is updated as part of this change.
- [A group's last event is deleted while none of its trackers is enabled; the calendar stays, empty, until the next reload] → Acceptable: it only happens after disabling a tracker and deleting its history, and a reload of the entry removes it.
- [Four event queries instead of one when every calendar is shown in the panel] → Each query is indexed by baby and time and returns a fraction of today's rows; no measurable cost expected.

## Migration Plan

1. Install the new version through the Marketplace and restart. Setup removes `<baby_id>_calendar` and creates the group calendars.
2. Point the Teste dashboard's calendar card at the group calendars.
3. Rollback: reinstall the previous version. The old calendar returns, with the same unique id. The group calendars then show as unavailable until they are removed from the entity settings.
