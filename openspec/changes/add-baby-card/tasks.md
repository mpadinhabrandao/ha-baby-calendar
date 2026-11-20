# Tasks

## 1. Integration support

- [ ] 1.1 Add the `feed` attribute to the last breastfeeding sensor per design D6; verify with tests for one side, two sides with a pause, a pause over 30 minutes, a feed across midnight and a running side
- [ ] 1.2 Add the `baby_calendar/subscribe_babies` WebSocket subscription per design D3; verify with tests for the message's content, a non-administrator user, and a new message after a medication is added and after a baby is removed
- [ ] 1.3 Serve and register the card module per design D2, with the `http`, `frontend` and `websocket_api` dependencies; verify with a test that the static path serves the bundle and the module URL carries the version, and that Hassfest passes

## 2. Frontend tooling

- [ ] 2.1 Set up `frontend/` (package.json with pinned versions, TypeScript, Lit, esbuild, Vitest, Playwright) and a build script writing the bundle with Lit's licence notice; verify the build produces `custom_components/baby_calendar/frontend/baby-calendar-card.js`
- [ ] 2.2 Add a CI job that installs, runs the frontend tests, rebuilds the bundle and fails if it differs from the committed one; verify on the pull request

## 3. Card

- [ ] 3.1 Card skeleton: configuration by baby, the subscription, the "baby not found" message, the visual editor listing babies, `window.customCards`, the two tabs and the English and Portuguese texts; verify with Vitest and a Playwright render in each language
- [ ] 3.2 Home tab: facts at the top, diaper buttons with the stool question in place, bottle with − / + and content, breastfeeding sides with live timers and the last feed line, sleep, the time chip, only enabled trackers; verify with Vitest for the texts and sections and Playwright for the idle and running states and the services called
- [ ] 3.3 Due medications on top with "Given", the undo bar, the repeat guard and errors shown; verify with Playwright that each calls the expected service and that a failed call shows the message and keeps the inputs
- [ ] 3.4 More tab: today's totals, the forms for weight, length, temperature, solids, pumping and a medication with range errors, and the latest entries; verify with Playwright

## 4. Documentation and project

- [ ] 4.1 Document the card in `README.md` (adding it, what each part does, the Lit licence) and remove the auto-entities section and `dashboards/baby.yaml`; verify the README's steps on a real instance
- [ ] 4.2 Update `openspec/config.yaml` (the integration has a frontend of its own; this change listed as the ninth) and mark the open tasks of `add-baby-dashboard` as superseded by this change; verify `openspec validate --strict` passes for both changes

## 5. Integration checks

- [ ] 5.1 On a real instance, add the card for the test baby and use it on a phone: a diaper with its stool type, a bottle after changing the amount, breastfeeding left then right with a pause, sleep, a due medication's "Given", undo, an entry 15 minutes ago, and each More form
- [ ] 5.2 On the real instance, enable a tracker and add a medication with the card open; verify they appear without a reload
- [ ] 5.3 After updating the integration, verify the phone loads the new card version without clearing the cache

## Workflow follow-up

- Archive this change together with `add-baby-dashboard` after review.
