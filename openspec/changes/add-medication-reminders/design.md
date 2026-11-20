# Design

## Context

Builds on `add-core-tracking` (its design.md, D1 to D10, still applies). Revised after an independent review: fixed-time doses are matched to scheduled times instead of counted per day, removing a medication keeps its doses, and the due sensor carries the names the blueprint needs. Medication differs from the other trackers in two ways: the things being tracked are named by the user, so its entities are dynamic, and it is the first tracker with time-based behaviour that happens without anyone logging anything.

## Goals / Non-Goals

**Goals:**

- Medications are managed with Home Assistant forms only, like the rest of the configuration.
- "Is a dose due" is a pure function of the schedule, the recorded doses and the clock, so it can be unit-tested without Home Assistant and recomputed at any time.
- The integration only exposes state. Delivering a reminder is left to an automation, for which a blueprint is provided.

**Non-Goals:**

- A general user-defined tracker mechanism. This is specific to medication.
- Sending notifications from the integration. An earlier draft had optional per-medication notify targets; it was dropped in favour of the sensor and blueprint alone, which removes the notify-service coupling and the need to persist what was already sent.
- Snooze, acknowledgement without recording a dose, escalation.

## Decisions

### R1. Medications live in the baby's options

`entry.options["medications"]` is a list of:

```
id: str                 # UUID4, never changes
name: str
dose: str | null        # informational text
active: bool
schedule: {type: "none"}
        | {type: "times", times: ["09:00", "21:00"]}
        | {type: "interval", hours: float}
```

The options flow becomes a menu: baby details, trackers, medications. The medications branch lists existing ones and offers add, edit, deactivate or reactivate, and remove. Fixed times are entered in one text field as comma-separated `HH:MM` values, validated and stored sorted and de-duplicated. Saving reloads the entry, which creates and removes entities.

- Alternative: config subentries, one per medication, which give add, reconfigure and delete per item natively on the integration page. Tested on 2026-11-16 against Home Assistant 2026.2.3 in a test harness with a minimal integration: the subentry flow adds a medication, the reconfigure flow renames it, and removing the subentry works. Two findings shape how they could be used:
  - Entities added with `config_subentry_id` are removed automatically with their subentry, but they tie the baby's device to every medication's subentry. From Home Assistant 2026.8 a device may belong to at most one subentry, with no compatibility shim, so this is not usable for several medications on one baby device.
  - Entities added without `config_subentry_id` stay on the baby's device with no such tie, but are not removed with the subentry; the integration must remove their registry entries itself, as it already does for disabled trackers.
  The second form is viable. It was not tested on 2026.8 or later, where the device rule changed. Task 1.1 therefore repeats the harness test on the development version and then picks subentries (second form) or the options-flow menu. No spec depends on the choice.
  - Outcome (task 1.1): the options-flow menu, with a details step (name, birth date, trackers) and a medications branch (add; pick one, then edit, deactivate or reactivate, or remove).

There is no "medication" checkbox in the tracker list: medication is active for a baby when it has at least one active medication.

### R2. Doses are ordinary events

A dose is a row with `tracker = 'medication'`, `kind = <medication id>` and `data = {"name": <name at the time>}`. Listing and the calendar use the current name of the medication when it still exists, else the name stored in `data`, so doses of a removed medication stay readable. Removing a medication deletes nothing from the store; a new medication with the same name gets a new id and its own doses.

### R3. Service and entities

`baby_calendar.log_medication` (`medication`, `notes`, `time`, required `device_id`). `medication` is matched case-insensitively against the names of the baby's active medications. It returns the event id when a response is requested.

The button goes through the shared dashboard path of the core change (D8), so it honours `minutes_ago`, the repeated press guard and undo. The `due` binary sensor has the attributes `baby`, `medication` and `dose`.

Per active medication, unique ids `<baby_id>_med_<medication id>_<key>`:

| Platform | Key | Present when |
|---|---|---|
| button | `take` | always |
| sensor | `last_dose` (timestamp; attributes `event_id`, `dose`) | always |
| sensor | `doses_today` | always |
| sensor | `next_dose` (timestamp) | has a schedule |
| binary_sensor | `due` | has a schedule |

Entity names use translation keys with a `{medication}` placeholder (for example "{medication} due"), so the fixed part is translated and the name is the user's.

### R4. Due computation

`schedule.py` exposes one pure function: given the schedule, the medication's dose times in a look-back window, and `now`, it returns `(due: bool, next_dose: datetime | None, next_change: datetime | None)`.

Fixed times:

1. Build the slots: every scheduled local time from two days before `now` to the day after, as timezone-aware datetimes. A local time that does not exist on a daylight saving day is moved forward to the first valid instant; a repeated local time uses its first occurrence.
2. Match doses to slots, in dose order: a dose claims the slot nearest to it if that slot is unclaimed and the dose is nearer to it than to either neighbouring slot. Otherwise the dose claims nothing. With one time per day, each slot's reach is therefore 12 hours either side; with 09:00 and 21:00 it is 6 hours.
3. Let `current` be the latest slot at or before `now`. `due` is true when `current` is unclaimed. Earlier unclaimed slots are missed and ignored: only the current slot can be due.
4. `next_dose` is `current` when due, else the first slot after `now`. `next_change` is the first slot after `now`.

Interval: `next_dose = last_dose + hours`, `due = now >= next_dose`, `next_change = next_dose` when it is in the future. With no dose, `due` is false and `next_dose` is `None`.

Matching doses to slots, rather than counting doses per day, is what makes an early dose count, keeps a double log from cancelling the evening reminder, and lets a 23:00 dose stay due past midnight until 09:00. Nothing is persisted: the result depends only on the schedule, the stored doses and the clock.

### R5. Scheduler

Each entry has a medication scheduler. For every active medication with a schedule it evaluates R4 and arms one `async_track_point_in_time` at `next_change`. It re-evaluates when that fires, when a dose of that medication is recorded, corrected or deleted, at local midnight, and on entry reload. The binary sensor and `next_dose` sensor take their state from the evaluation. Because the state is always recomputed from the schedule, the stored doses and the clock, nothing about reminders needs to be persisted: after a restart a dose that became due while Home Assistant was down simply evaluates as due.

### R6. Blueprint

`blueprints/automation/baby_calendar/medication_reminder.yaml`: inputs are the `due` binary sensor, an action sequence, and an optional repeat interval. It triggers when the sensor turns on, and also at Home Assistant start if the sensor is already on, runs the action, and if a repeat is set loops `delay` then action while the sensor is on. The action receives the baby and medication names and the dose text as variables. HACS does not install blueprints, so the README carries an import link.

## Risks / Trade-offs

- [A dose given far from every scheduled time, for example 15:00 with a 09:00 and 21:00 schedule, satisfies whichever is nearer, or neither at exactly the midpoint] → Accepted. The due and next dose sensors show the outcome immediately.
- [A missed dose is dropped when the next scheduled time arrives, without a trace in the entities] → The event log shows the gap; the integration does not flag it, in line with giving no medical advice.
- [An interval reminder says a dose is due when the medicine may be "as needed"] → The user chooses whether to give an interval at all; without a schedule nothing is ever due. The README says so, and the integration gives no advice either way.
- [No reminder arrives unless the user creates an automation] → The README's medication section leads with the blueprint import link, and the due sensor is usable on a dashboard on its own.
- [A restart while a dose is due makes a blueprint automation notify again] → Accepted; a second reminder for a dose that is still due is harmless.
- [Dynamic entity names are not translated for the medication part] → Accepted; the name is the user's own text.

## Open Questions

- Whether to move medications to config subentries once that Home Assistant feature has been tried on a real instance. It would change the configuration UI but no spec.
