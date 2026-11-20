# Design

## Context

Greenfield repository. See proposal.md for motivation. Constraints that shape the approach:

- Home Assistant custom integration, Python only, no frontend code. Dashboards are stock cards over our entities.
- The recorder purges state history (10 days by default), so history cannot live in entity states.
- Trackers are fixed and purpose-built. A generic user-configurable model was drafted and dropped.
- Later changes add timed trackers, a calendar entity, medication, measurements, solids and pumping on the same event data.
- The Home Assistant event loop must never block on disk I/O.

This design was revised after an independent review. The main changes: history survives removing a baby, undo and back-dating are in this change, the stool type is a follow-up tap instead of a sticky selector, services require the baby, and solids and pumping moved to their own later changes.

## Goals / Non-Goals

**Goals:**

- One event store shared by every tracker.
- Each tracker is a small, self-contained module, so adding one later touches no other tracker.
- The common night-time slips (wrong button, double tap, "that was 20 minutes ago") are fixed from the dashboard, without services or identifiers.
- No runtime dependency beyond what Home Assistant ships.

**Non-Goals:**

- User-defined trackers, units other than millilitres, imports from other trackers, per-user attribution.
- Keeping long-term statistics in step with corrections to past days (see spec `event-log`, "Charts reflect the day as it was logged").
- Entering notes from the dashboard. Notes come through services and, later, the calendar.

## Decisions

### D1. Storage: one SQLite file in the config directory

Events live in `<config>/baby_calendar.db`, accessed with the standard library `sqlite3` module behind an `EventStore` class that is the only code touching SQL. The store owns one connection opened with `check_same_thread=False` and guards every call with a `threading.Lock`; calls run through `hass.async_add_executor_job`.

- Why not the recorder database: its retention and schema belong to Home Assistant.
- Why not `helpers.storage.Store` (JSON): whole-file rewrites and no range queries.
- Journal mode stays at the SQLite default (rollback journal), so the database is one file.
- Backups: a `backup.py` platform implements `async_pre_backup` (take the store lock and close the connection) and `async_post_backup` (reopen), so the file is never copied mid-transaction.
- On open, a schema version newer than the code knows makes setup fail with a clear error instead of touching the file. A migration first copies the file to a single `baby_calendar.db.bak` (overwritten each time).

### D2. Tables

```
babies(
  baby_id     TEXT PRIMARY KEY,   -- UUID4, stable for the life of the history
  name        TEXT NOT NULL,
  removed_ts  INTEGER             -- NULL while a config entry uses it
)

events(
  id          TEXT PRIMARY KEY,   -- UUID4, the public event identifier
  baby_id     TEXT NOT NULL REFERENCES babies,
  tracker     TEXT NOT NULL,      -- 'diaper' | 'bottle' | later ones
  start_ts    INTEGER NOT NULL,   -- UTC epoch seconds
  end_ts      INTEGER,            -- NULL here; used by add-timed-tracking
  kind        TEXT,               -- main variant: diaper content, bottle content
  amount      REAL,               -- ml for bottle; NULL otherwise
  data        TEXT NOT NULL,      -- JSON object for remaining fields, e.g. {"stool": "soft"}
  notes       TEXT,
  created_ts  INTEGER NOT NULL,   -- when it was recorded; drives undo and the stool prompt
  updated_ts  INTEGER NOT NULL
)
INDEX (baby_id, tracker, start_ts)
INDEX (baby_id, start_ts)
INDEX (baby_id, created_ts)
```

`kind` and `amount` are real columns because sensors filter and sum on them. Everything else is JSON, so a new tracker needs no migration. The schema version is `PRAGMA user_version`.

### D3. Baby identity is separate from the config entry

One config entry per baby. `entry.data` holds `baby_id` (the `babies` row) and the name; `entry.options` holds the birth date and the list of enabled tracker keys. The device identifier is `(DOMAIN, baby_id)` and entity unique ids are `<baby_id>_<key>`, so re-attaching history also brings back the same entity registry entries when they still exist.

- Config flow: name and birth date, then, if a removed baby with the same name (case-insensitive) exists in `babies`, a step offering "restore history" or "start empty", then the tracker multi-select. Restore reuses the row and clears `removed_ts`; start empty creates a new row.
- `async_remove_entry` only sets `removed_ts`. Nothing is deleted.
- `baby_calendar.purge_history` takes a `name`, matches removed babies only, and deletes their rows and events. If several removed babies share the name it deletes all of them and says how many in the response.
- An options flow edits name, birth date and trackers and reloads the entry. On setup, entities are created only for enabled trackers and registry entries of trackers no longer enabled are removed.

Why keep history on removal: removing and re-adding an entry is a routine Home Assistant troubleshooting step, and here it would otherwise destroy months of records.

### D4. Tracker modules

Each tracker is one module under `trackers/` exposing its key, the schema of its log service, a function turning validated input into an event row, the entity descriptions it contributes, and a function computing its state from the store. `__init__` and the platforms iterate over a registry. Diaper and bottle are registered here.

### D5. Services

Registered once in `async_setup`:

- `baby_calendar.log_diaper` (`content`, `stool`, `notes`, `time`) and `baby_calendar.log_bottle` (`amount`, `content`, `notes`, `time`), each with a required `device_id` (device selector filtered to this integration), returning the event id when a response is requested. Logging on a tracker that is not enabled for that baby is an error.
- `baby_calendar.update_event` and `baby_calendar.delete_event`: take `event_id`.
- `baby_calendar.list_events`: `device_id`, `start`, `end`, optional `tracker`. Response only.
- `baby_calendar.purge_history`: `name`. See D3.

`device_id` is required, with no fallback to "the only baby". Home Assistant's guidance for actions is to make the target required, and a fallback would break every automation the day a second baby is added. Dashboard entities are unaffected, since each belongs to a baby.

`update_event` does not take a union of loosely named fields. It takes `time`, `notes` and a `fields` object whose keys are validated by the schema of the event's own tracker (`content` and `stool` for diaper; `amount` and `content` for bottle). A key present with the value `null` clears that field; `notes: ""` clears the notes. After merging, the tracker's normaliser runs: for diaper, content `wet` drops `stool`.

### D6. Time handling

Service `time` is parsed with `cv.datetime`, made timezone-aware in the Home Assistant time zone when naive, and stored as UTC. Anything later than now plus 60 seconds is rejected. "Today" is `[dt_util.start_of_local_day(), next local midnight)`, so a day is 23 or 25 hours long on a daylight saving change.

### D7. Entities

Per baby, always:

| Platform | Key | Notes |
|---|---|---|
| number | `minutes_ago` | Box, 0 to 720, step 1. Not restored: 0 after restart |
| button | `undo` | See D8 |

Per baby, when the tracker is enabled:

| Tracker | Platform | Keys |
|---|---|---|
| diaper | button | `diaper_wet`, `diaper_dirty`, `diaper_both` |
| diaper | button | `stool_normal`, `stool_soft`, `stool_hard`, `stool_diarrhea` |
| diaper | binary_sensor | `stool_prompt` |
| diaper | sensor | `diaper_last`, `diaper_last_wet`, `diaper_last_dirty` (timestamp); `diaper_changes_today`, `diaper_wet_today`, `diaper_dirty_today` |
| bottle | number, select, button | `bottle_amount` (ml, box, 0 to 500, step 1), `bottle_content`, `bottle_log` |
| bottle | sensor | `bottle_last` (timestamp); `bottle_count_today`, `bottle_ml_today` |

All entities use `has_entity_name` and translation keys, fully translated to `en` and `pt`. The `*_last` sensors carry `event_id` and the event's fields as attributes. The bottle amount and content are UI state for the next press and are restored; they are the only inputs that keep their value, because a baby's usual bottle rarely changes from one feed to the next.

The intended dashboard for the stool type is a conditional card that shows the four stool buttons while `stool_prompt` is on. The README carries that example.

### D8. Dashboard logging path

Every logging button goes through one function that:

1. drops the press if the same button of the same baby was accepted less than 3 seconds ago (in-memory timestamp per entity);
2. reads `minutes_ago`, computes the event time, and sets `minutes_ago` back to 0 whether or not the log succeeds;
3. calls the same code as the service.

`undo` deletes the row with the greatest `created_ts` for that baby if it is within 15 minutes, else raises `HomeAssistantError`. It uses `created_ts`, not `start_ts`, so a back-dated entry made a moment ago is the one undone.

The stool buttons update the row with the greatest `created_ts` among that baby's diaper events under the rule in the spec. `stool_prompt` is recomputed after every write and by a timer set for `created_ts + 10 minutes` of the latest dirty diaper.

### D9. State and statistics

Each entry owns a state object holding every enabled tracker's values, recomputed from the store after every write, correction or deletion affecting it, and by an `async_track_time_change` listener at local midnight. Entities subscribe and write their state on change. There is no polling.

Daily sensors use `state_class: total` with `last_reset` at the start of the local day. The Home Assistant sensor documentation confirms that `total` accepts a decrease (the statistics sum moves by the difference) and that a changed `last_reset` starts a new cycle from zero; `total_increasing` would treat a decrease as a meter reset. This was tested on 2026-11-16 against Home Assistant 2026.2.3 in a test harness (real recorder and statistics compiler, simulated clock, no frontend). A counter that went 1, 2, 3, back to 2 after a deletion, 3, then reset at midnight and reached 2 the next day produced these daily statistics: `change` 3 then 2, `state` 3 then 2, `sum` 3 then 5. A duration sensor fed by a sleep from 23:00 to 06:00 produced a daily `change` of about 60 then 360 minutes. So the data is right, and the per-day figure is the `change` statistic (or `state`); `sum` is cumulative across days and is not what a parent wants to see.

The statistics graph card documents `period: day` and `stat_types` including `change` and `state`, so the README's example card uses `chart_type: bar`, `period: day`, `stat_types: [change]`. Only the visual result in the frontend remains unchecked; task 1.5 is reduced to looking at that card on a real instance. `measurement` is not a fallback, since it is defined for instantaneous values, not daily totals.

### D10. Repository layout and tooling

```
custom_components/baby_calendar/   __init__, manifest.json, const, config_flow,
                                   store, backup, coordinator, services(.py/.yaml),
                                   trackers/ (diaper, bottle),
                                   sensor, binary_sensor, button, select, number,
                                   strings.json, translations/
tests/                             pytest-homeassistant-custom-component
hacs.json, README.md, LICENSE (MIT)
.github/workflows/                 hassfest, HACS validation, pytest, ruff
```

`manifest.json`: `config_flow: true`, `integration_type: device`, `iot_class: local_push`, empty `requirements`. The minimum Home Assistant version in `hacs.json` is the release used for development; no older release is supported.

## Risks / Trade-offs

- [`minutes_ago` and the bottle inputs are shared per baby, so two parents on two devices can change each other's pending input] → Accepted. The window is the few seconds between setting a value and pressing, and `undo` covers the slip.
- [A box-mode number on a phone commits its value in a separate call from the button press, so a fast press can log the previous amount] → The amount is visible next to the button and in the last bottle sensor; `undo` and `update_event` correct it. Verified on a real phone in task 7.1.
- [Disabling and re-enabling a tracker loses renamed entity ids and dashboard references, because registry entries are removed] → Documented. Unique ids are stable, so default entity ids come back.
- [Unattached history accumulates when babies are removed and added with "start empty"] → `purge_history` removes it. The README explains when to use it.
- [SQLite file on network or SD storage is slow or corrupts] → Single serialized connection, the pre-migration copy and Home Assistant backups.
- [Statistics do not follow corrections to past days] → Stated in the spec. The event log, and later the calendar, are always correct.

## Open Questions

None that affect the specs or tasks.
