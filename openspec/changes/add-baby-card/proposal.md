# Proposal

## Why

The dashboard view of `add-baby-dashboard`, stock cards filled by auto-entities, was tried on a real instance and judged neither usable nor intuitive: eighteen identical tiles, technical names, the inputs a button needs (bottle amount, "minutes ago") far from the button, and no live timer. A parent logging one-handed at night needs one screen built for that, which stock cards cannot give. A mockup of that screen was approved on 2026-11-20 as a first version, to be corrected after use.

## What Changes

- A custom Lovelace card, "Baby Calendar card", shipped inside the integration and registered by it, so it is available in every dashboard with no separate install. A dashboard needs one line: the card and the baby.
- **Home tab**, only the enabled trackers: three facts at the top (last feed, last diaper, awake since or asleep for); big buttons for diapers, a bottle with its amount and − / + beside it, breastfeeding left and right, and sleep; a "when" chip ("now", or minutes ago) for the next entry, which goes back to "now" after it.
- Live state on the same screen: a running timer shows its time and a stop button; after a dirty diaper the stool type question appears below the diaper buttons; a due medication appears at the top with "Given"; after each entry a bar names it and offers "Undo".
- Breastfeeding: each side is started and stopped on its own, pauses included; tapping the other side while one runs stops it and starts the other. The last feed is shown as it happened ("Left 12 min · pause 5 min · Right 8 min"), with no side suggested.
- **More tab**: today's totals, the other trackers (weight, length, temperature, solids, pumping, a medication) as small forms, and the latest entries.
- Integration support for the card: a WebSocket subscription giving a baby's trackers, medications and entity ids, and the entries of the last feed as an attribute of the last breastfeeding sensor.
- The card's text in English and Portuguese, following the user's language.
- **Replaces** the auto-entities view: `dashboards/baby.yaml` and its README section are removed, and `add-baby-dashboard` is closed as superseded. Its two attributes (`medication`, `stool_type`) stay.
- The project context changes: the integration now has a frontend of its own, this card.

Out of scope for this first version: charts, editing entries in the card (the calendar and `update_event` remain), several babies on one card, themes beyond Home Assistant's light and dark.

## Capabilities

### New Capabilities

- `baby-card`: the card the parent uses to log and see a baby's day: its tabs, buttons, live state and texts.
- `baby-card-data`: what the integration provides for the card: the card's registration, the WebSocket subscription and the last feed's entries.

### Modified Capabilities

None. The breastfeeding attribute is a new requirement here, since `add-timed-tracking` is not archived.

## Impact

- New `frontend/` source in the repository (TypeScript, Lit), bundled into `custom_components/baby_calendar/frontend/baby-calendar-card.js`, which is committed so HACS installs it. New build and test tooling (Node, esbuild, Vitest, Playwright) in development and CI only.
- Lit, bundled into the card, is BSD-3-Clause licensed; its notice ships with the bundle.
- `custom_components/baby_calendar/`: static path and module registration, a WebSocket command, the `feed` attribute; `manifest.json` gains the `http`, `frontend` and `websocket_api` dependencies.
- `README.md`, `dashboards/baby.yaml` (removed), `openspec/config.yaml`.
- No new runtime dependency for Home Assistant, no network access.
