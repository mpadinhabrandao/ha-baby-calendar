# Design

## Context

Builds on the trackers and medications already merged (see proposal.md - Why). Entity ids follow the language of Home Assistant (`teste_coco_mole`, `teste_vitamina_d_dado`), so a view cannot select entities by id or name. Unique ids are stable but are not visible to dashboard cards. The project context rules out frontend code in the integration.

## Goals / Non-Goals

**Goals:**
- One view per baby that needs editing only to set the baby's name.
- Works the same in English and Portuguese.

**Non-Goals:**
- Choosing card styles per entity beyond tile and entities cards.
- Showing history graphs; the measurement sensors can be added to a graph card by hand.

## Decisions

### D1. auto-entities around stock cards

Each section is an auto-entities card wrapping a stock card: a `grid` of `tile` cards for buttons and timers, `entities` for sensors and inputs, and a stock `calendar` card. auto-entities resolves its filters each time the view renders, so the view follows the baby's entities.

Alternatives: a dashboard strategy in the integration (custom JavaScript, dynamic and with no dependency, but frontend code the project avoids); a view regenerated on demand (no dependency, not dynamic). The user chose auto-entities.

### D2. Selecting the baby

Every filter includes `integration: baby_calendar` and `device: "<baby name>"`. The device filter matches the device's display name, so renaming the baby, or the device in Home Assistant, requires the name in the view to change too. The name is the view's only placeholder.

### D3. Selecting sections without names

Filters use domains, device classes, state classes and two new attributes, never entity ids or names:

| Section | Filter |
|---|---|
| Logging and timers | `button` without `medication` or `stool_type`; `switch` |
| Stool type | `button` with `stool_type`, inside a stock `conditional` card on the stool prompt sensor |
| Medications | any entity with `medication` |
| Today | `sensor` with `state_class: total`, without `medication` |
| Last times | `sensor` with `device_class: timestamp`, without `medication` |
| Measurements | `sensor` with `state_class: measurement` |
| Inputs | `number`, `select` |
| Calendar | a stock calendar card on the baby's calendar entity, named directly |

A stock conditional card needs the stool prompt sensor's entity id, and the calendar card does not render inside auto-entities (checked on a real instance: it showed an empty strip), so the view names both entities directly, as two placeholders next to the baby's name. The README says where to find them.

On tiles and rows, the entity's own name is shown without the baby's (`name: {type: entity}`), which keeps tiles readable on a phone.

`medication` and `stool_type` are added to `extra_state_attributes`. They are static strings, so they add a few bytes per state in the recorder.

### D4. Shipping the view

`dashboards/baby.yaml` holds one view in the sections layout, with `BABY_NAME`, `STOOL_PROMPT_ENTITY` and `CALENDAR_ENTITY` placeholders. The README tells the user to install auto-entities, create a dashboard, open its raw configuration editor and paste the view with the three values filled. HACS does not install dashboards, so nothing is automatic.

## Risks / Trade-offs

- [auto-entities stops working with a future Home Assistant] → The integration is unaffected, and its entities can still be placed on stock cards by hand.
- [The baby is renamed] → The view shows nothing until its name is changed; the README says so.
- [The medications section grows long with many medications] → Its entities are sorted by the `medication` attribute, so each medication's entities stay together.
