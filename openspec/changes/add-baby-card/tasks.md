# Tasks

## 1. Integration support

- [x] 1.1 Add the `feed` attribute to the last breastfeeding sensor per design D6; verify with tests for one side, two sides with a pause, the same side twice, a pause over 30 minutes, a feed across midnight and a running side
- [x] 1.2 Add the `baby_calendar/subscribe_babies` WebSocket subscription per design D3; verify with tests for the message's content, a non-administrator user, and a new message after a medication is added and after a baby is removed
- [x] 1.3 Serve and register the cards' module per design D2, with the `http` and `websocket_api` dependencies and `frontend` after; verify with a test that the static path serves the bundle and the module URL carries the bundle's hash, and that Hassfest passes

## 2. Frontend tooling

- [x] 2.1 Set up `frontend/` (package.json with pinned versions, TypeScript, Lit, esbuild, Vitest, Playwright) and a build script writing the bundle with Lit's licence notice; verify the build produces `custom_components/baby_calendar/frontend/baby-calendar-cards.js`
- [ ] 2.2 Add a CI job that installs, runs the frontend tests, rebuilds the bundle and fails if it differs from the committed one; verify on the pull request

## 3. Shared card base

- [x] 3.1 The base every card uses: the shared subscription, the baby lookup and "baby not found", "tracker not enabled", the visual editor listing babies, `window.customCards`, theme styling per design D7, `getGridOptions`, the English and Portuguese texts; verify with Vitest and a Playwright render of a minimal card in each language, light and dark
- [x] 3.2 The time chip, the 3-second repeat guard, the undo bar and the error line; verify with Vitest for the chip and guard, and Playwright that undo calls `delete_event` with the returned id and a failed call shows the message and keeps the inputs

## 4. Cards

- [x] 4.1 Diapers card with the stool type question; verify with Playwright for wet, dirty with a type, and the chip
- [x] 4.2 Bottle card with − / + and content; verify with Playwright that the amount entity is set and `log_bottle` gets the amount and content
- [x] 4.3 Breastfeeding card: sides, live time, side change, last feed line; verify with Vitest for every last feed case in the spec and Playwright for start, stop and side change
- [x] 4.4 Sleep card; verify with Playwright for asleep and awake
- [x] 4.5 Medications card, due doses and the optional full list; verify with Playwright that "Given" calls `log_medication` and nothing due is shown when none is
- [x] 4.6 Summary and Today cards; verify with Vitest for the totals and ago texts and Playwright renders
- [x] 4.7 Other entries card with its forms and range errors; verify with Playwright for weight, a refused weight, pumping and a medication dose
- [x] 4.8 Recent entries card; verify with Playwright that it lists `list_events` results newest first and refreshes after an entry

- [x] 4.9 Bottle card revised after use on a phone: the amount as a value between − and +, and a separate "Log bottle" button; verify with Playwright that − / + and the content record nothing and "Log bottle" records the amount and content
- [x] 4.10 Breastfeeding buttons named by what they do: "Start left" / "Start right" ("Começar esquerda" / "Começar direita") while no side runs; verify with Playwright the idle labels, and that start, stop and side change still call the same services

## 5. Documentation and project

- [ ] 5.1 Document the cards in `README.md` (adding them, what each does, a sample of a few together, the Lit licence) and remove the auto-entities section and `dashboards/baby.yaml`; verify the README's steps on a real instance
- [x] 5.2 Update `openspec/config.yaml` (the integration has a frontend of its own; this change listed as the ninth) and mark the open tasks of `add-baby-dashboard` as superseded by this change; verify `openspec validate --strict` passes for both changes

## 6. Integration checks

- [ ] 6.1 On a real instance, add each card for the test baby next to the household's own cards and use them on a phone: a diaper with its stool type, a bottle after changing the amount, breastfeeding left then right with a pause, sleep, a due medication's "Given", undo, an entry 15 minutes ago, each Other entries form
- [ ] 6.2 On the real instance, enable a tracker and add a medication with the cards open; verify they appear without a reload
- [ ] 6.3 After updating the integration, verify the phone loads the new cards without clearing the cache

## Workflow follow-up

- Archive this change together with `add-baby-dashboard` after review.
- Dashboards built from these cards are a later change.
