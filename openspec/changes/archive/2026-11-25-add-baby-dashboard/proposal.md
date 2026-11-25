# Proposal

## Why

Every tracker and medication adds entities to the baby's device, but logging at night needs them on one screen, in a sensible order, on a phone. A dashboard built by hand with stock cards lists its entities one by one, so enabling a tracker or adding a medication means editing the dashboard; a new medication would have no button until someone does. Testing on a real instance made this the next thing missing.

## What Changes

- A ready-made dashboard view for one baby, shipped in the repository, that the user adds to Home Assistant and points at the baby by its name. Several babies get one view each.
- The view fills itself from the baby's entities with the community card auto-entities (MIT), installed from the Marketplace, wrapping stock cards (tile, entities, calendar). Entities of trackers enabled later and of medications added later appear without editing it; disabled trackers and removed or deactivated medications disappear.
- Sections, in this order: logging buttons and running timers; the stool type, shown only while the stool prompt is on; medications; today's totals; last times; measurements; the inputs (minutes ago, bottle amount and the like); the calendar.
- So the view can tell entities apart in any language, the integration adds two attributes: `medication` on every medication entity, and `stool_type` on each stool type button. No other integration behaviour changes.
- The project context changes: the integration still has no frontend of its own, but the documented dashboard depends on auto-entities. A dashboard of stock cards alone remains possible and is described as such.

Out of scope: a dashboard strategy or any custom frontend code in the integration, a dashboard generated or rewritten by the integration, and dashboards for several babies on one view.

## Capabilities

### New Capabilities

- `baby-dashboard`: the ready-made dashboard view for a baby, what it shows, in which order, and how it follows the entities the baby has.

### Modified Capabilities

None. The two attributes are new requirements in this change, since the medication and core tracking changes are not archived yet.

Superseded on 2026-11-20 by `add-baby-card`, and archived without its specs. Before archiving, the requirement on the two attributes, which the code keeps, was moved: `stool_type` to the `diaper-tracking` spec of `add-core-tracking` ("Stool type attribute") and `medication` to the `medication-tracking` spec of `add-medication-reminders` ("Medication attribute").

## Impact

- `dashboards/baby.yaml` in the repository: the view, with the baby's name as its one placeholder.
- `custom_components/baby_calendar/`: the `medication` attribute on medication entities and the `stool_type` attribute on stool buttons.
- `README.md`: a dashboard section, including installing auto-entities and its licence.
- `openspec/config.yaml`: the project context names the dashboard and its dependency, and lists this change.
- New user-side dependency: the auto-entities card (thomasloven/lovelace-auto-entities, MIT). The integration itself gains no dependency.
