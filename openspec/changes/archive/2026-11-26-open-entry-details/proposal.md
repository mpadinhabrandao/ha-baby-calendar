# Proposal

## Why

On a real instance the parent wanted to see a value's history from the Recent entries card, and the card's lines are plain text: they open nothing. Adding stock cards for each measurement next to it made the page confusing. Every entry already belongs to an entity with Home Assistant's own history and graph; tapping the entry should open it, like any entity.

## What Changes

- Tapping a line of the Recent entries card opens Home Assistant's more-info dialog of the entity that holds that kind of entry:
  - weight, length and temperature: the sensor with the value (its dialog draws the graph of the readings);
  - diaper, bottle, breastfeeding, sleep, solids and pumping: the tracker's last entry sensor;
  - a medication dose: that medication's last dose sensor.
- A line whose entity no longer exists (a tracker disabled, a medication removed) opens nothing and looks the same as before.
- Lines show that they can be tapped (pointer, focus and keyboard), as the other buttons of the cards do.

Out of scope: editing an entry from the card (the calendar and `update_event` remain), and making the other cards' values tappable.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `baby-cards`: a new requirement, opening an entry's entity from the Recent entries card.

## Impact

- `frontend/src/cards/recent.ts` and the shared styles; the bundle `custom_components/baby_calendar/frontend/baby-calendar-cards.js` is rebuilt.
- `frontend/e2e/run.mjs`: a check that tapping a line fires `hass-more-info` with the right entity.
- No change to the integration's Python code: the cards already receive each baby's entity ids by purpose.
