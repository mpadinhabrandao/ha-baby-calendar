# Baby Calendar

A Home Assistant custom integration to log a baby's day: diapers and bottles
first, with more trackers planned. It has no frontend of its own. It provides
entities and services, and you build the dashboard with stock cards.

All data stays on your Home Assistant host. The integration records and
displays data only; it gives no health advice.

**Status:** under development, not ready for use yet.

## Babies

### Adding a baby

Settings > Devices & services > Add integration > **Baby Calendar**.

1. Enter the baby's name. The birth date is optional, so you can add the
   baby before it is born and set the date later.
2. Tick the trackers to use for this baby. You can tick none and enable them
   later.

Each baby is one device, named after it, holding all of its entities. Add one
entry per baby; two babies cannot share a name.

Entity ids are made from the baby's name and the entity names in your Home
Assistant language. The examples below use an English install and a baby
called Alice; with Portuguese, for example, the wet diaper button is
`button.alice_fralda_com_xixi`. Look up the real ids on the baby's device
page.

### Editing a baby

Open the baby's entry and choose **Configure** to change the name, the birth
date or the enabled trackers. Nothing recorded is lost.

Disabling a tracker removes its entities and keeps its events. Enabling it
again brings the entities back with the same default entity ids, but any
entity id you renamed and any dashboard card pointing at it must be set up
again.

### Removing a baby and its history

Deleting a baby's entry removes its device and entities and **keeps its
history** in `baby_calendar.db`. Removing and re-adding an entry is a common
troubleshooting step, and it should not cost months of records.

When you add a baby with the same name as a removed one, the integration asks
whether to:

- **Restore that history**: the baby comes back with all of its events.
- **Start empty**: the baby starts with no events, and the old history stays
  stored but unattached.

To delete the stored history of a removed baby for good, call the
`baby_calendar.purge_history` action with its name:

```yaml
action: baby_calendar.purge_history
data:
  name: Alice
```

It refuses to act on a baby that is still configured. If several removed
babies share the name, it deletes all of them and its response says how
many babies and events were deleted.

## Logging from the dashboard

Every baby has two entities that work with all trackers:

- **Minutes ago** (`number`): set it before pressing a button to record
  something that happened earlier. It goes back to 0 after every entry and
  after a restart.
- **Undo last entry** (`button`): deletes the entry recorded last, whatever
  its time, if it was recorded in the last 15 minutes. Press it again to
  delete the one before.

A second press of the same logging button within 3 seconds is ignored, so a
double tap records one entry.

## Diapers

### Entities

| Entity | What it does |
|---|---|
| Wet diaper, Dirty diaper, Wet and dirty diaper (`button`) | Log a change with that content. |
| Stool normal, soft, hard, diarrhea (`button`) | Set the stool type of the dirty diaper just logged. Works for 10 minutes after it was recorded. |
| Stool type pending (`binary_sensor`) | On while the dirty diaper just logged has no stool type, for up to 10 minutes. |
| Last diaper change, Last wet diaper, Last dirty diaper (`sensor`) | Time of the last matching change, with its `event_id`, `content`, `stool` and `notes` as attributes. |
| Diaper changes today, Wet diapers today, Dirty diapers today (`sensor`) | Today's counts, from local midnight. |

A wet and dirty change counts once as a change, once as wet and once as
dirty.

### Dashboard example

The stool type buttons appear only after a dirty diaper, and disappear once a
type is chosen or after 10 minutes. Replace the entity ids with your baby's
(see the note under *Adding a baby*).

```yaml
type: vertical-stack
cards:
  - type: grid
    columns: 3
    square: false
    cards:
      - type: button
        entity: button.alice_wet_diaper
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.alice_wet_diaper
      - type: button
        entity: button.alice_dirty_diaper
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.alice_dirty_diaper
      - type: button
        entity: button.alice_wet_and_dirty_diaper
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.alice_wet_and_dirty_diaper
  - type: conditional
    conditions:
      - condition: state
        entity: binary_sensor.alice_stool_type_pending
        state: "on"
    card:
      type: grid
      columns: 4
      square: false
      cards:
        - type: button
          entity: button.alice_stool_normal
          tap_action:
            action: perform-action
            perform_action: button.press
            target:
              entity_id: button.alice_stool_normal
        - type: button
          entity: button.alice_stool_soft
          tap_action:
            action: perform-action
            perform_action: button.press
            target:
              entity_id: button.alice_stool_soft
        - type: button
          entity: button.alice_stool_hard
          tap_action:
            action: perform-action
            perform_action: button.press
            target:
              entity_id: button.alice_stool_hard
        - type: button
          entity: button.alice_stool_diarrhea
          tap_action:
            action: perform-action
            perform_action: button.press
            target:
              entity_id: button.alice_stool_diarrhea
  - type: entities
    entities:
      - number.alice_minutes_ago
      - button.alice_undo_last_entry
      - sensor.alice_last_diaper_change
      - sensor.alice_diaper_changes_today
```

### Action

```yaml
action: baby_calendar.log_diaper
data:
  device_id: <the baby's device>
  content: dirty    # wet, dirty or both
  stool: soft       # optional, only for dirty or both: normal, soft, hard, diarrhea
  notes: Green      # optional
  time: "2026-11-20 03:00:00"  # optional, now if left out
response_variable: logged      # optional, holds event_id
```

## Bottles

### Entities

| Entity | What it does |
|---|---|
| Bottle amount (`number`) | Millilitres of the next bottle, 0 to 500 in steps of 1. |
| Bottle content (`select`) | Not specified, formula or breast milk. |
| Log bottle (`button`) | Logs a bottle with the amount and content set. Fails while the amount is 0. |
| Last bottle (`sensor`) | Time of the last bottle, with its `event_id`, `amount`, `content` and `notes` as attributes. |
| Bottles today, Bottle millilitres today (`sensor`) | Today's count and total, from local midnight. |

The amount and the content keep their value after a press and after a
restart, since a baby's usual bottle rarely changes from one feed to the
next. They are the only inputs that do.

On a phone, the amount box saves its value when it loses focus. Check the
amount shown before pressing the button; if it was wrong, press **Undo last
entry** or correct the bottle with `update_event`.

### Dashboard example

```yaml
type: entities
entities:
  - number.alice_bottle_amount
  - select.alice_bottle_content
  - button.alice_log_bottle
  - sensor.alice_last_bottle
  - sensor.alice_bottles_today
  - sensor.alice_bottle_millilitres_today
```

### Action

```yaml
action: baby_calendar.log_bottle
data:
  device_id: <the baby's device>
  amount: 90                # millilitres, more than 0
  content: formula          # optional: formula or breast_milk
  notes: Took a while       # optional
  time: "2026-11-20 03:00:00"  # optional, now if left out
```

## Correcting, deleting and listing entries

```yaml
action: baby_calendar.update_event
data:
  event_id: <id>
  time: "2026-11-20 02:40:00"   # optional
  notes: ""                     # optional, empty removes the notes
  fields:                       # optional, only the fields to change
    content: wet                # a wet diaper drops its stool type
    stool: null                 # null clears a field
```

```yaml
action: baby_calendar.delete_event
data:
  event_id: <id>
```

```yaml
action: baby_calendar.list_events
data:
  device_id: <the baby's device>
  start: "2026-11-20 00:00:00"
  end: "2026-11-21 00:00:00"
  tracker: diaper               # optional
response_variable: entries
```

Every entry has an `event_id`; the action that logs it returns it, listings
include it, and the "last" sensors expose it.

Charts of the daily sensors show each day as it stood that day. Correcting a
past day changes the entries, not the statistics already recorded.

### Where the data lives

Events are stored in `baby_calendar.db` in the Home Assistant configuration
directory, independent of the recorder, so they are kept beyond its retention
period. The file is part of standard Home Assistant backups.

## License

[MIT](LICENSE)
