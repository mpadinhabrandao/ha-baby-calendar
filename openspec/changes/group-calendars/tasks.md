# Tasks

## 1. Store

- [x] 1.1 Add a `trackers` collection filter to `store.list_events` and a `trackers_with_events(baby_id)` query; cover both in `tests/test_store.py` (filter by two trackers, timed overlap still applied, distinct trackers of one baby only) and run `pytest tests/test_store.py`

## 2. Group calendars

- [x] 2.1 Add the group mapping with an import-time check that every tracker is in exactly one group; one calendar entity per group with unique id `<baby_id>_calendar_<group>`, listing, state and own-entries check per group; names in `strings.json` and `translations/en.json`/`pt.json`
- [x] 2.2 Create a group's calendar only when a tracker of it is enabled, the group is Health and the baby has a medication, or the baby has events of it; at setup remove `<baby_id>_calendar` and group calendars that no longer qualify
- [x] 2.3 Rewrite `tests/test_calendar.py` for the spec scenarios: entries split by group, fever, weight and medication in Health, two babies, Portuguese names, diapers-only baby, disabled tracker with history, medication-only Health, event of another group rejected, upgrade removes the single calendar, Sleep on while Feeding off, and the existing title, notes, placement, edit and delete tests on the group calendars; run the full `pytest` and `ruff check`
- [x] 2.4 README Calendar section: the four calendars and their entries, filtering in the calendar panel, a calendar card example with several calendars, the BREAKING note on `calendar.<baby>_calendar`; check that no other README section names the old calendar
- [x] 2.5 Run `openspec validate group-calendars --strict`

## 3. Real instance

- [ ] 3.1 After the PR is merged, install through the Marketplace and restart; verify in Home Assistant that the Teste baby has the four calendars (all its trackers are enabled), that the old single calendar is gone and that the logs have no errors
- [ ] 3.2 Point the calendar card of the Teste dashboard at the group calendars; verify in Chrome that the Hoje page shows entries and that the calendar panel lists the four calendars with their checkboxes, and that showing only Saúde shows only temperatures, weights, lengths and doses

## Workflow follow-up

- Archive the change with `openspec archive group-calendars --yes`, in its own PR.
