# Proposal

## Why

Each baby has one calendar with every entry, so finding one kind of entry (a fever three weeks ago among dozens of diapers and feeds a day) means scrolling through everything. Home Assistant's calendar panel and calendar card filter by calendar, not by the kind of entry, so the only way to filter natively is to have one calendar per group of entries.

## What Changes

- Each baby gets five calendars instead of one, one per group of entries:
  - **Feeding**: bottle, breastfeeding, solids and pumping;
  - **Diapers**;
  - **Sleep**;
  - **Health**: temperature and medication doses;
  - **Growth**: weight and length.
- A group's calendar exists when one of its trackers is enabled (for Health, also when the baby has a medication) or when the baby has recorded entries of the group. A diapers-only baby does not fill the calendar panel with empty calendars, and the history of a tracker disabled later stays visible.
- Each calendar keeps today's behaviour for its own entries: titles, notes, placement in time, changing the time, editing notes and deleting. A calendar is on while a timer of its own group runs, so only Feeding and Sleep are ever on.
- **BREAKING**: the single calendar (`calendar.<baby>_calendar`) is removed, together with its entity registry entry. Dashboards and automations that use it must switch to the group calendars. Seeing the whole day still works by turning on all of a baby's calendars in the calendar panel, or by listing them all in a calendar card.
- README: the Calendar section describes the five calendars, how to filter in the calendar panel and a calendar card example with several calendars.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `calendar-view`: one calendar per baby becomes one calendar per group of entries; when a group calendar exists; the full history and the on/off state apply per group; edits are limited to the calendar's own entries.

## Impact

- `custom_components/baby_calendar/calendar.py`: one entity per group, each listing only its group's trackers.
- `custom_components/baby_calendar/__init__.py`: removal of the old calendar's registry entry and of a group calendar that no longer applies.
- `custom_components/baby_calendar/store.py`: a query for whether a baby has entries of given trackers, and filtering a listing by several trackers.
- `strings.json` and `translations/*.json`: names of the five calendars.
- `tests/test_calendar.py`.
- `README.md`.
- The Teste dashboard's calendar card is pointed at the new calendars after the install.
- No change to the stored events, the services or the cards.
