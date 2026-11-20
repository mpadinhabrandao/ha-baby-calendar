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

Open the baby's entry, choose **Configure**, then **Name, birth date and
trackers** to change them. Nothing recorded is lost. **Medications** in the
same menu manages the baby's medications (see [Medications](#medications)).

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

## Timers: breastfeeding and sleep

Breastfeeding and sleep have a start and an end. Each has a timer you start
and stop while it happens, or you log a finished entry by its duration.

| Entity | What it does |
|---|---|
| Breastfeeding, Sleeping (`switch`) | On while the timer runs, with `started_at` as an attribute. Turning it on starts the timer; turning it off stops it. "Minutes ago" moves the start or the end. |
| Breastfeeding duration, Sleep duration (`number`) | Minutes of a finished entry to log with the button. Goes back to 0 after each entry and after a restart. |
| Log breastfeeding, Log sleep (`button`) | Logs a finished entry of that duration, ending now, or "minutes ago". |
| Last breastfeeding, Last sleep (`sensor`) | Start of the most recent entry, with `ended_at`, `duration` (seconds), `in_progress` and, for breastfeeding, `side`. |
| Breastfeeding time today, Sleep time today (`sensor`) | Minutes within today, updated every minute while a timer runs. |
| Breastfeeds today, Sleeps today (`sensor`) | Feeds and sleeps that started today. |

A timer keeps running until it is stopped, across midnight and restarts. Only
one timer per tracker runs at a time; breastfeeding and sleep can run
together.

Daily times are split at midnight: a sleep from 23:00 to 06:00 counts one
hour on the first day and six hours on the second. The count goes to the day
the sleep or feed started.

Undo treats starting a timer and logging a finished entry as entries, so a
timer started by mistake is undone. Undo after stopping a timer deletes the
whole entry if it was started in the last 15 minutes.

Disabling breastfeeding or sleep on a baby while its timer runs finishes the
entry at that moment.

### Breastfeeding

| Entity | What it does |
|---|---|
| Breastfeeding side (`select`) | Not specified, left or right. Used by the switch and the button, kept after a restart. |

Each entry has one side. To change side, turn the switch off and on again:
that is two entries. When an entry with a side ends, the selector moves to
the other side, ready for the next one.

**Breastfeeds today** counts feeds, not entries: an entry that starts within
30 minutes of the previous one's end belongs to the same feed, so left then
right is one feed. A feed counts on the day its first entry started.
Breastfeeding time today adds up every entry.

```yaml
action: baby_calendar.start_breastfeeding
data:
  device_id: <the baby's device>
  side: left              # optional: left or right
  time: "2026-11-20 03:00:00"  # optional start, now if left out
```

```yaml
action: baby_calendar.stop_breastfeeding
data:
  device_id: <the baby's device>
  time: "2026-11-20 03:12:00"  # optional end, now if left out
```

```yaml
action: baby_calendar.log_breastfeeding
data:
  device_id: <the baby's device>
  duration: "00:15:00"
  side: right             # optional
  time: "2026-11-20 03:00:00"  # optional start; without it the entry ends now
```

### Sleep

| Entity | What it does |
|---|---|
| Awake since (`sensor`) | End of the last finished sleep; unknown while asleep. |

The Sleeping switch is on exactly while a sleep runs, so it works as the
baby's sleeping state in automations:

```yaml
alias: Dim the nursery while the baby sleeps
triggers:
  - trigger: state
    entity_id: switch.alice_sleeping
    to: "on"
actions:
  - action: light.turn_on
    target:
      entity_id: light.nursery
    data:
      brightness_pct: 5
```

`start_sleep`, `stop_sleep` and `log_sleep` take the same fields as the
breastfeeding actions, without `side`.

### Last feed

With bottles, breastfeeding or both enabled, **Last feed** (`sensor`) shows
the start of the most recent feed of either kind, with `kind` (`bottle` or
`breastfeeding`) as an attribute.

## Medications

Baby Calendar records doses of the medications you enter and tells you when
one is due by the schedule you enter. It does not suggest medicines, doses or
schedules, and it raises no warning about the doses you record.

### Managing medications

Open the baby's entry, choose **Configure**, then **Medications**:

- **Add a medication**: a name (unique for the baby), an optional dose text
  such as "1 drop", shown with reminders only, and a schedule:
  - **No schedule**: you only record doses.
  - **Fixed times**: times of day separated by commas, such as `09:00, 21:00`.
  - **Interval**: hours between doses, counted from the last dose.
- **Change a medication**: pick it, then **Edit**, **Deactivate or
  reactivate**, or **Remove**.

Neither deactivating nor removing deletes any dose. A deactivated medication
has no entities and is never due; reactivating it brings its entities back
with its doses. Doses of a removed medication stay in the history and the
calendar under its name; a new medication with the same name starts with no
doses of its own. Renaming a medication lists its earlier doses under the new
name.

### Entities

Each active medication adds these entities to the baby's device. Their names
start with the medication's name, so with "Vitamin D" the button is
**Vitamin D given**.

| Entity | What it shows or does |
|---|---|
| **given** (`button`) | Records a dose now, or "minutes ago" earlier; undo removes it |
| **last dose** (`sensor`) | Time of the last dose, with `event_id` and `dose` |
| **doses today** (`sensor`) | Doses since midnight |
| **next dose** (`sensor`) | With a schedule: the time of the next dose, or of the one due now |
| **due** (`binary_sensor`) | With a schedule: on while a dose is due, with `baby`, `medication` and `dose` |

With fixed times, a dose counts for the scheduled time nearest to it, so a
dose given a little early counts, and logging twice does not cancel the next
time. A missed dose stays due until the next scheduled time, then only that
one is due. The due state is worked out from the schedule, the recorded doses
and the clock, so a dose that became due while Home Assistant was off is due
when it starts.

### Action

```yaml
action: baby_calendar.log_medication
data:
  device_id: <the baby's device>
  medication: Vitamin D        # the name, in any case
  notes: With the morning bottle  # optional
  time: "2026-11-20 09:05:00"  # optional, now if left out
```

The name must match an active medication of the baby, or the action fails
and records nothing.

### Reminders

[![Import the reminder blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/create-link/?redirect=blueprint_import&blueprint_url=https%3A%2F%2Fgithub.com%2Fmpadinhabrandao%2Fha-baby-calendar%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fbaby_calendar%2Fmedication_reminder.yaml)

Baby Calendar sends no notifications itself. Import the **medication
reminder** blueprint with the button above, then create an automation from
it: pick the medication's **due** sensor, the actions to run (such as a
notification to your phone) and, optionally, how often to repeat them while
the dose is still due. In the actions, `{{ baby }}`, `{{ medication }}`
and `{{ dose }}` hold the names and the dose text:

```yaml
action: notify.mobile_app_my_phone
data:
  message: "{{ baby }}: {{ medication }} ({{ dose }})"
```

The automation also runs when Home Assistant starts if a dose is already due.

## Calendar

Each baby has a calendar entity with every recorded entry of every tracker,
including trackers disabled later. Open it in the Calendar panel, or add a
calendar card; the week and list views read best on days with many entries.

```yaml
type: calendar
initial_view: listWeek
entities:
  - calendar.alice_calendar
```

| Emoji | Entry | Example title |
|---|---|---|
| 💧 | Wet diaper | 💧 Wet diaper |
| 💩 | Dirty diaper, with the stool type | 💩 Dirty diaper (soft) |
| 💧💩 | Wet and dirty diaper | 💧💩 Wet and dirty diaper |
| 🍼 | Bottle, amount and content | 🍼 Bottle 90 ml formula |
| 🤱 | Breastfeeding, side and duration | 🤱 Breastfeeding left 15 min |
| 😴 | Sleep and duration | 😴 Sleep 1 h 20 min |

Titles follow the Home Assistant language. A running timer shows "in
progress" and reaches up to now; diaper changes and bottles are short blocks
at their time. The calendar is on while a timer runs.

From the calendar you can:

- **Change the time** of an entry. For a finished breastfeeding or sleep,
  both the start and the end; for anything else, the start. The same rules as
  `update_event` apply, so a time in the future is refused.
- **Write notes**: the description is the entry's notes, and this is where
  they are meant to be written. Emptying it removes them. Saving a running
  sleep or feed never stops its timer.
- **Delete** an entry.

The title is generated, so editing it changes nothing. Entries cannot be
created from the calendar, and it shows recorded entries only.

## Correcting, deleting and listing entries

```yaml
action: baby_calendar.update_event
data:
  event_id: <id>
  time: "2026-11-20 02:40:00"   # optional, new start
  end_time: "2026-11-20 03:10:00"  # optional, new end of a finished timed entry
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

Timed entries in a listing also have `end`, `duration` (seconds) and
`in_progress`, and a listing includes every timed entry that overlaps the
period, such as a sleep that started the night before. The end of a running
timer is set only by stopping it.

Charts of the daily sensors show each day as it stood that day. Correcting a
past day changes the entries, not the statistics already recorded.

### Where the data lives

Events are stored in `baby_calendar.db` in the Home Assistant configuration
directory, independent of the recorder, so they are kept beyond its retention
period. The file is part of standard Home Assistant backups.

## License

[MIT](LICENSE)
