# Proposal

## Why

On a real instance the Recent entries card mixed today's and yesterday's entries showing only a time, listed test doses that made no sense to the parent, and was not what the Registos page needed: the parent only wants weight, length and temperature, which stock tiles of their sensors already show, with Home Assistant's own history. The card adds code and confusion for no remaining use.

## What Changes

- **BREAKING**: the Recent entries card (`custom:baby-calendar-recent-card`) is removed from the integration's cards. A dashboard that still uses it shows Home Assistant's "custom element doesn't exist" error until the card is removed from it.
- The card picker offers eight Baby Calendar cards instead of nine.
- The README's cards table and examples drop the card and say how to show measurements with stock tiles instead.

Out of scope: the `list_events` service and the calendar, which keep listing every entry.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `baby-cards`: "Cards available with the integration" lists eight cards; "Recent entries card" and "Entry details from Recent entries" are removed.

## Impact

- `frontend/src/cards/recent.ts` deleted; `frontend/src/index.ts` and `frontend/src/i18n.ts` lose its registration and strings; the shared list styles used only by it go; the bundle is rebuilt.
- `frontend/e2e/run.mjs`: the Recent entries checks go.
- `README.md`.
- On the real instance, the Teste dashboard no longer uses the card (it was replaced with tiles on 2026-11-26).
