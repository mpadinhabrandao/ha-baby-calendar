# Design

## Context

The Recent entries card (`frontend/src/cards/recent.ts`) builds its lines from `list_events` and already receives, through the `baby_calendar/subscribe_babies` subscription, the baby's entity ids by purpose (`diaper_last`, `bottle_last`, `breastfeeding_last`, `sleep_last`, `solids_last`, `pumping_last`, `weight`, `length`, `temperature`) and, per medication, its entities (`last_dose`). Home Assistant opens an entity's more-info dialog when a card dispatches the `hass-more-info` event with `{ entityId }`, bubbling and composed.

## Goals / Non-Goals

**Goals:** one tap on a line shows the entity's history and graph in Home Assistant's own dialog.

**Non-Goals:** editing entries from the card; tap actions on the other cards.

## Decisions

### D1: Map the tracker to an entity by purpose
`tracker → key`: diaper `diaper_last`, bottle `bottle_last`, breastfeeding `breastfeeding_last`, sleep `sleep_last`, solids `solids_last`, pumping `pumping_last`, weight `weight`, length `length`, temperature `temperature`; a medication dose looks up the medication by name in `baby.medications` and takes `entities.last_dose`. Using the subscription's keys keeps the card free of entity ids and languages. For measurements the value sensor is chosen over the "last measured" timestamp, because its dialog draws the readings.

Alternative: open the calendar at the entry. Rejected for now: the calendar panel has no deep link to an event.

### D2: The line is a button
Each line becomes a `<button>` with the line's look, so it gets focus, Enter/Space and the pointer for free; a line without an entity stays a plain row. The click dispatches `hass-more-info` from the card.

## Risks / Trade-offs

- [The dialog shows the last-entry sensor, whose history is a list of times, not of amounts] → For bottles and pumping the amount is in the attributes and the calendar; the measurement graph is the main need, and the value sensors carry it.
- [A medication renamed since the dose was recorded] → The dose keeps the old name and finds no medication: the line opens nothing, as specified.
