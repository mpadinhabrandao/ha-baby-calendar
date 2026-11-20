# Design

## Context

See proposal.md - Why, and the approved mockup (canvas "Painel do bebé – maqueta", 2026-11-20), whose screen is now split into cards. The user's instance runs navbar-card, Mushroom, Bubble Card, button-card and card-mod; the cards have to sit beside them. The integration already provides every action the card needs, as services (`log_*`, `start_*`, `stop_*`, `delete_event`, `list_events`, `log_medication`) and as the stool type buttons, sensors for the facts, and entities whose ids follow the language of Home Assistant. Home Assistant 2026.11 loads custom cards as JavaScript modules; `frontend.add_extra_js_url` adds one to every dashboard.

## Goals / Non-Goals

**Goals:**
- Cards call services and read states; all rules (repeat guard, feeds, due state, validation) stay in the integration.
- Cards that keep working when trackers and medications change, with no reload.
- Cards that look native next to stock and Mushroom cards.
- Something the user can test within days, then correct.

**Non-Goals:**
- Offline use or queuing actions while disconnected.
- A build step for users: the bundle is committed.

## Decisions

### D1. Lit and TypeScript, one bundled module for all cards

Source in `frontend/src/` (TypeScript, Lit 3), one file per card over a shared base class (subscription, baby lookup, repeat guard, time chip, undo bar, error line, texts), bundled by esbuild into one ES module, `custom_components/baby_calendar/frontend/baby-calendar-cards.js`, minified, with Lit's licence comment kept. The bundle is committed because HACS installs repository files and runs no build. CI rebuilds it and fails when the committed file differs.

Alternatives: plain JavaScript with no framework (no build, but hand-written DOM updates for live timers and many states); reusing the Lit instance Home Assistant loads (not a public API, breaks without notice).

### D2. Registration

`async_setup` registers a static path `/baby_calendar/frontend` for the bundle's folder (cached) and calls `frontend.add_extra_js_url(hass, "/baby_calendar/frontend/baby-calendar-cards.js?v=<version>")`, the version read from the manifest. The module defines `baby-calendar-diaper-card`, `-bottle-card`, `-breastfeeding-card`, `-sleep-card`, `-medication-card`, `-summary-card`, `-today-card`, `-entry-card` and `-recent-card`, one shared editor, and adds each to `window.customCards` so they are in the card picker. `manifest.json` adds `http` and `websocket_api` to `dependencies` and `frontend` to `after_dependencies`: the frontend needs its compiled package, absent in the test environment, so the module is added only when the frontend is loaded.

### D3. Finding the baby's entities

Entity ids depend on the language and on renames, so the card never builds them. A WebSocket command `baby_calendar/subscribe_babies` (any authenticated user, read only) sends a list of babies: `entry_id`, `device_id`, `name`, `trackers`, `medications` (`id`, `name`, `dose`, `entities`), and `entities`, a map from the unique id suffix (`diaper_wet`, `bottle_amount`, `stool_prompt`, `breastfeeding_last` and so on) to the entity id, read from the entity registry. It is sent on subscribe and again whenever a Baby Calendar entry's state changes (loaded, unload started), which covers adding, removing and reconfiguring a baby. Each card is configured with the baby's `device_id` (the editor lists names) and looks everything up in this message; one subscription is shared by all cards on a page.

### D4. Actions

| Card and action | Service |
|---|---|
| Diaper buttons | `log_diaper` with `content`, and `time` when the chip is set |
| Stool type | `button.press` on that stool type's button, which sets it on the dirty diaper just recorded |
| Bottle | sets the amount number entity on − / +; `log_bottle` with `amount` and `content` from the inputs |
| Breastfeeding side | `start_breastfeeding` with `side`; if a side runs, `stop_breastfeeding` first, then start |
| Sleep | `start_sleep` / `stop_sleep` |
| Given | `log_medication` with the medication's name |
| Undo bar | `delete_event` with the event id the service returned |
| More forms | `log_weight`, `log_length`, `log_temperature`, `log_solids`, `log_pumping`, `log_medication` |

Every call passes `device_id` and uses `return_response` to get the event id. Each card keeps its own repeat guard for 3 seconds per button, besides the integration's, so a double tap sends one call. The time chip sends `time` explicitly instead of using the "minutes ago" entity, so cards never share a pending value with each other or with the entities.

### D5. Live values

Facts and running timers are derived from states: `last_feed`, the last diaper change, `awake_since`, and the running timer's switch with its `start` attribute. A 1-second interval, active only while a card with a running timer is connected, re-renders its elapsed time; ago texts re-render every 30 seconds; nothing is polled. The last feed is drawn from the `feed` attribute (D6). The Recent entries card calls `list_events` for the last 24 hours when it connects and whenever one of the baby's last-entry sensors changes.

### D6. The `feed` attribute

`BreastfeedingTracker.extra_values` already lists today's entries to count feeds; it adds the entries of the last feed, walking back from the latest entry while each starts within `FEED_GAP` of the previous one's end, across midnight. The last breastfeeding sensor exposes them as `feed`: a list of `{side, start, end}` with ISO times and `end` null while running.

### D7. Look

Cards render inside `ha-card` and use the theme's CSS variables (`--ha-card-background`, `--primary-text-color`, `--secondary-text-color`, `--ha-card-border-radius`, `--primary-color`, `--state-*-color`), so they follow light, dark and custom themes and card-mod applies to them. Each tracker has one accent colour taken from Home Assistant's own palette variables (`--amber-color`, `--blue-color`, `--pink-color`, `--deep-purple-color`, `--red-color`) at low opacity for buttons, with text at contrast. `getGridOptions` gives each card its default size and minimum in the sections grid. No card draws navigation.

### D8. Texts

A small dictionary per language in `frontend/src/i18n.ts`, chosen from `hass.locale.language`; Portuguese for `pt*`, English otherwise. Numbers and times use `Intl` with that language.

### D9. Tests

- Python: the subscription message and its update after a reload, the `feed` attribute across a pause and midnight, the static path and module URL.
- Vitest: pure logic: elapsed and "ago" texts, the last feed line in every case of the spec, the repeat guard, the time chip, the Today totals.
- Playwright with the pre-installed Chromium: each card rendered against a fake `hass` object at 390 px wide in light and dark, in its idle and active states (stool question, running timer, due medication, undo bar, error), checking that taps call the expected services.

### D10. What happens to add-baby-dashboard

Its view and README section are removed; its attributes stay (harmless, and useful for anyone's own dashboards). Its open tasks are marked superseded by this change, and both are archived together after review.

## Risks / Trade-offs

- [Frontend code to maintain, in another language] → Logic stays in the integration; the card only displays and calls services, and its pure parts are unit tested.
- [A cached old bundle after an update] → The module URL carries the version (D2).
- [Home Assistant changes how cards are loaded] → `add_extra_js_url` and `customCards` have been stable for years; the README keeps the manual resource as a fallback.
- [Two parents tap at once] → Each call is independent; the integration's repeat guard and the shown state settle it, as with the current buttons.
- [First version will need corrections after use] → Accepted by the user; changes go through OpenSpec as usual.
