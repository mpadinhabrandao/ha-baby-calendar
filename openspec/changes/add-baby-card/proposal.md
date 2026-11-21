# Proposal

## Why

The dashboard view of `add-baby-dashboard`, stock cards filled by auto-entities, was tried on a real instance and judged neither usable nor intuitive: eighteen identical tiles, technical names, the inputs a button needs (bottle amount, "minutes ago") far from the button, and no live timer. Stock cards cannot show a running timer on its button, ask the stool type right after a dirty diaper, or offer undo for the entry just made. A mockup of that experience was approved on 2026-11-20 as a first version. The user wants it as separate cards, one per job, so each household builds its own dashboards with them, next to the community cards it already uses (a floating bottom navigation bar, Mushroom, Bubble Card); the dashboards come later.

## What Changes

- A set of custom Lovelace cards shipped inside the integration and registered by it, so they are in every dashboard's card picker with no separate install. Each is configured with one baby, has a visual editor, follows the Home Assistant theme and fits the sections grid:
  - **Diapers**: wet, dirty, both; after a dirty diaper the stool type question appears in the card.
  - **Bottle**: the amount it will record between − and +, the content choices, and a "Log bottle" button (first shown as a button carrying the amount, judged unclear on a phone).
  - **Breastfeeding**: "Start left" and "Start right", each started and stopped on its own, pauses included; the running side shows its live time; the last feed shown as it happened, with no side suggested (first shown as "Left" and "Right", which did not say that a tap starts the side).
  - **Sleep**: fell asleep / woke up, with the live time.
  - **Medications**: the doses due, each with "Given"; optionally every active medication.
  - **Summary**: how long ago the baby ate, had a diaper change, and how long awake or asleep.
  - **Today**: the day's totals.
  - **Other entries**: small forms for weight, length, temperature, solids, pumping and a medication dose.
  - **Recent entries**: the latest entries.
- Every logging card has a "when" chip ("now", or minutes ago) for its next entry, going back to "now" after it, and shows for 60 seconds a bar naming the entry it just recorded with "Undo".
- Integration support for the cards: a WebSocket subscription giving each baby's trackers, medications and entity ids, and the entries of the last feed as an attribute of the last breastfeeding sensor.
- Card text in English and Portuguese, following the user's language.
- **Replaces** the auto-entities view: `dashboards/baby.yaml` and its README section are removed, and `add-baby-dashboard` is closed as superseded. Its two attributes (`medication`, `stool_type`) stay. Dashboards built from the new cards are a later change.
- The project context changes: the integration now has a frontend of its own, these cards.

Out of scope for this first version: dashboards, navigation, charts, editing entries in a card (the calendar and `update_event` remain), several babies in one card.

## Capabilities

### New Capabilities

- `baby-cards`: the cards a parent uses to log and see a baby's day: what each card shows and does, and what they share (configuration, time chip, undo, errors, theme, language).
- `baby-card-data`: what the integration provides for the cards: their registration, the WebSocket subscription and the last feed's entries.

### Modified Capabilities

None. The breastfeeding attribute is a new requirement here, since `add-timed-tracking` is not archived.

## Impact

- New `frontend/` source in the repository (TypeScript, Lit), bundled into `custom_components/baby_calendar/frontend/baby-calendar-cards.js`, which is committed so HACS installs it. New build and test tooling (Node, esbuild, Vitest, Playwright) in development and CI only.
- Lit, bundled into the cards, is BSD-3-Clause licensed; its notice ships with the bundle.
- `custom_components/baby_calendar/`: static path and module registration, a WebSocket command, the `feed` attribute; `manifest.json` gains the `http` and `websocket_api` dependencies and `frontend` as an after dependency.
- `README.md`, `dashboards/baby.yaml` (removed), `openspec/config.yaml`.
- No new runtime dependency for Home Assistant, no network access.
