"""Actions, and the logging path the dashboard buttons share with them."""

from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import Any, Final

import probatio
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.util import dt as dt_util

from .const import CONF_BABY_ID, DOMAIN, TRACKER_KEYS
from .data import async_get_store, async_run
from .models import BabyConfigEntry
from .store import Event, TimerRunningError, UnknownEventError
from .trackers import TIMED_TRACKERS, TRACKERS
from .trackers.base import Tracker
from .trackers.diaper import DIAPER, DIRTY_KINDS, STOOL, STOOL_WINDOW
from .trackers.timed import TimedTracker

ATTR_DEVICE_ID: Final = "device_id"
ATTR_EVENT_ID: Final = "event_id"
ATTR_TIME: Final = "time"
ATTR_NOTES: Final = "notes"
ATTR_FIELDS: Final = "fields"
ATTR_START: Final = "start"
ATTR_END: Final = "end"
ATTR_TRACKER: Final = "tracker"
ATTR_END_TIME: Final = "end_time"
ATTR_DURATION: Final = "duration"
ATTR_IN_PROGRESS: Final = "in_progress"

SERVICE_UPDATE_EVENT: Final = "update_event"
SERVICE_DELETE_EVENT: Final = "delete_event"
SERVICE_LIST_EVENTS: Final = "list_events"

# A time this far in the future is still accepted, for clocks that differ.
FUTURE_TOLERANCE: Final = timedelta(seconds=60)
# How long an entry can still be undone after it was recorded.
UNDO_WINDOW: Final = timedelta(minutes=15)
# A second press of the same logging button within this time is dropped.
REPEAT_GUARD: Final = timedelta(seconds=3)

_NOTES = probatio.All(cv.string, probatio.Length(max=1000))


# ----------------------------------------------------------------- helpers


def _error(key: str, **placeholders: Any) -> ServiceValidationError:
    return ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key=key,
        translation_placeholders={k: str(v) for k, v in placeholders.items()} or None,
    )


def now_ts() -> int:
    """Return the current time as UTC epoch seconds."""
    return int(dt_util.utcnow().timestamp())


def to_timestamp(when: datetime) -> int:
    """Validate an event time and return it as UTC epoch seconds.

    A naive time is taken in the Home Assistant time zone.
    """
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt_util.get_default_time_zone())
    if when > dt_util.utcnow() + FUTURE_TOLERANCE:
        raise _error("future_time")
    return int(when.timestamp())


def entry_for_device(hass: HomeAssistant, device_id: str) -> BabyConfigEntry:
    """Return the loaded config entry of the baby a device belongs to."""
    device = dr.async_get(hass).async_get(device_id)
    if device is not None:
        entry = hass.config_entries.async_get_entry(device.config_entry_id)
        if (
            entry is not None
            and entry.domain == DOMAIN
            and entry.state is ConfigEntryState.LOADED
        ):
            return entry
    raise _error("unknown_baby")


def entry_for_baby(hass: HomeAssistant, baby_id: str) -> BabyConfigEntry | None:
    """Return the loaded config entry of a baby, if it is configured."""
    for entry in hass.config_entries.async_loaded_entries(DOMAIN):
        if entry.data[CONF_BABY_ID] == baby_id:
            return entry
    return None


def _local_iso(ts: int) -> str:
    return dt_util.as_local(dt_util.utc_from_timestamp(ts)).isoformat()


def event_response(hass: HomeAssistant, event: Event) -> dict[str, Any]:
    """Describe an event for a service response or an entity attribute.

    A timed event also has its end, its duration in seconds and whether it
    is in progress; the end and the duration are None while it runs.
    """
    tracker = TRACKERS[event.tracker]
    response: dict[str, Any] = {
        ATTR_EVENT_ID: event.id,
        ATTR_TRACKER: event.tracker,
        ATTR_TIME: _local_iso(event.start_ts),
    }
    if tracker.timed:
        running = event.end_ts is None
        response |= {
            ATTR_END: None if running else _local_iso(event.end_ts),
            ATTR_DURATION: None if running else event.end_ts - event.start_ts,
            ATTR_IN_PROGRESS: running,
        }
    return response | {**tracker.to_fields(event), ATTR_NOTES: event.notes}


def _validate_fields(tracker: Tracker, schema: dict[Any, Any], fields: Any) -> dict:
    try:
        return probatio.Schema(schema)(fields)
    except probatio.Invalid as err:
        raise _error("invalid_fields", tracker=tracker.key, error=err) from err


# ------------------------------------------------- shared logging path


async def async_log(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    tracker: Tracker,
    fields: dict[str, Any],
    *,
    when: datetime | None = None,
    notes: str | None = None,
) -> Event:
    """Record an event for a baby. Used by the log services and the buttons."""
    data = entry.runtime_data
    if tracker.key not in data.trackers:
        raise _error("tracker_disabled", tracker=tracker.key, name=data.name)
    tracker.check(fields)
    start_ts = now_ts() if when is None else to_timestamp(when)
    columns = tracker.to_columns(fields)
    store = await async_get_store(hass)
    event = await async_run(
        hass,
        store.add_event,
        baby_id=data.baby_id,
        tracker=tracker.key,
        start_ts=start_ts,
        kind=columns.kind,
        amount=columns.amount,
        data=columns.data,
        notes=notes or None,
        now=now_ts(),
    )
    await data.coordinator.async_refresh()
    return event


async def async_log_from_dashboard(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    key: str,
    log: Callable[[datetime], Awaitable[Any]],
) -> None:
    """Run a logging button's press through the shared dashboard path.

    Drops a repeated press, applies "minutes ago" and sets it back to 0
    whether or not the entry is recorded.
    """
    data = entry.runtime_data
    now = dt_util.utcnow()
    last = data.last_press.get(key)
    if last is not None and timedelta(0) <= now - last < REPEAT_GUARD:
        return

    when = now - timedelta(minutes=data.minutes_ago)
    if data.minutes_ago:
        data.minutes_ago = 0
        data.coordinator.async_update_listeners()
    await log(when)
    data.last_press[key] = now


async def async_undo(hass: HomeAssistant, entry: BabyConfigEntry) -> Event:
    """Delete the baby's most recently recorded entry, if it is recent."""
    data = entry.runtime_data
    store = await async_get_store(hass)
    latest = await async_run(hass, store.latest_recorded, data.baby_id)
    window = int(UNDO_WINDOW.total_seconds())
    if latest is None or latest.created_ts <= now_ts() - window:
        raise HomeAssistantError(
            translation_domain=DOMAIN, translation_key="nothing_to_undo"
        )
    await async_run(hass, store.delete_event, latest.id)
    await data.coordinator.async_refresh()
    return latest


async def async_set_stool(
    hass: HomeAssistant, entry: BabyConfigEntry, stool: str
) -> Event:
    """Set the stool type of the baby's most recently recorded diaper change.

    Only a dirty diaper recorded in the last 10 minutes takes a stool type
    this way; anything else is corrected with update_event.
    """
    data = entry.runtime_data
    store = await async_get_store(hass)
    latest = await async_run(hass, store.latest_recorded, data.baby_id, DIAPER.key)
    if latest is None or latest.kind not in DIRTY_KINDS:
        raise HomeAssistantError(
            translation_domain=DOMAIN, translation_key="stool_not_dirty"
        )
    if latest.created_ts <= now_ts() - STOOL_WINDOW:
        raise HomeAssistantError(
            translation_domain=DOMAIN, translation_key="stool_too_late"
        )
    event = await async_run(
        hass,
        store.update_event,
        latest.id,
        {"data": {**latest.data, STOOL: stool}},
        now=now_ts(),
    )
    await data.coordinator.async_refresh()
    return event


async def async_update_fields(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    event: Event,
    supplied: dict[str, Any],
    *,
    when: datetime | None = None,
    end: datetime | None = None,
    notes: str | None = None,
    clear_notes: bool = False,
) -> Event:
    """Correct an event with the same rules as when it was logged."""
    tracker = TRACKERS[event.tracker]
    supplied = _validate_fields(tracker, tracker.update_fields, supplied)
    merged = tracker.normalise({**tracker.to_fields(event), **supplied}, set(supplied))
    tracker.check(merged)
    columns = tracker.to_columns({k: v for k, v in merged.items() if v is not None})

    changes: dict[str, Any] = {}
    if supplied:
        changes |= {
            "kind": columns.kind,
            "amount": columns.amount,
            "data": columns.data,
        }
    if when is not None:
        changes["start_ts"] = to_timestamp(when)
    if end is not None:
        if not tracker.timed:
            raise _error("end_time_not_timed", tracker=tracker.key)
        if event.end_ts is None:
            raise _error("end_time_running")
        changes["end_ts"] = to_timestamp(end)
    if tracker.timed and event.end_ts is not None:
        start_ts = changes.get("start_ts", event.start_ts)
        if changes.get("end_ts", event.end_ts) <= start_ts:
            raise _error("end_before_start")
    if clear_notes:
        changes["notes"] = None
    elif notes is not None:
        changes["notes"] = notes

    store = await async_get_store(hass)
    if changes:
        event = await async_run(
            hass, store.update_event, event.id, changes, now=now_ts()
        )
        await entry.runtime_data.coordinator.async_refresh()
    return event


# ----------------------------------------------------------------- timers


def _enabled_timed(entry: BabyConfigEntry, tracker: TimedTracker) -> None:
    data = entry.runtime_data
    if tracker.key not in data.trackers:
        raise _error("tracker_disabled", tracker=tracker.key, name=data.name)


async def _finished(
    hass: HomeAssistant, entry: BabyConfigEntry, tracker: TimedTracker, event: Event
) -> None:
    """Move the side selection on after a finished entry, then refresh."""
    if (side := tracker.other_side(event)) is not None:
        entry.runtime_data.breastfeeding_side = side
    await entry.runtime_data.coordinator.async_refresh()


async def async_start_timer(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    tracker: TimedTracker,
    fields: dict[str, Any],
    *,
    when: datetime | None = None,
    notes: str | None = None,
) -> Event:
    """Start a timed tracker's timer, refused while one is running."""
    _enabled_timed(entry, tracker)
    data = entry.runtime_data
    start_ts = now_ts() if when is None else to_timestamp(when)
    columns = tracker.to_columns(fields)
    store = await async_get_store(hass)
    try:
        event = await async_run(
            hass,
            store.start_timer,
            baby_id=data.baby_id,
            tracker=tracker.key,
            start_ts=start_ts,
            kind=columns.kind,
            data=columns.data,
            notes=notes or None,
            now=now_ts(),
        )
    except TimerRunningError as err:
        raise _error("timer_running", tracker=tracker.key) from err
    await data.coordinator.async_refresh()
    return event


async def async_stop_timer(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    tracker: TimedTracker,
    *,
    when: datetime | None = None,
) -> Event:
    """Stop a timed tracker's running timer, now or at a given end."""
    data = entry.runtime_data
    store = await async_get_store(hass)
    running = await async_run(hass, store.running_event, data.baby_id, tracker.key)
    if running is None:
        raise _error("timer_not_running", tracker=tracker.key)
    end_ts = now_ts() if when is None else to_timestamp(when)
    if end_ts <= running.start_ts:
        raise _error("end_before_start")
    event = await async_run(
        hass, store.update_event, running.id, {"end_ts": end_ts}, now=now_ts()
    )
    await _finished(hass, entry, tracker, event)
    return event


async def async_log_duration(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    tracker: TimedTracker,
    fields: dict[str, Any],
    duration: timedelta,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    notes: str | None = None,
) -> Event:
    """Record a finished timed event of a duration.

    With ``start`` the event begins then; otherwise it ends at ``end``, or
    now. A running timer is not affected.
    """
    _enabled_timed(entry, tracker)
    seconds = int(duration.total_seconds())
    if seconds <= 0:
        raise _error("duration_zero")
    if start is not None:
        start_ts = to_timestamp(start)
        end_ts = start_ts + seconds
        if end_ts > now_ts() + int(FUTURE_TOLERANCE.total_seconds()):
            raise _error("future_time")
    else:
        end_ts = now_ts() if end is None else to_timestamp(end)
        start_ts = end_ts - seconds
    columns = tracker.to_columns(fields)
    data = entry.runtime_data
    store = await async_get_store(hass)
    event = await async_run(
        hass,
        store.add_event,
        baby_id=data.baby_id,
        tracker=tracker.key,
        start_ts=start_ts,
        end_ts=end_ts,
        kind=columns.kind,
        data=columns.data,
        notes=notes or None,
        now=now_ts(),
    )
    await _finished(hass, entry, tracker, event)
    return event


async def async_delete(
    hass: HomeAssistant, entry: BabyConfigEntry, event: Event
) -> None:
    """Permanently delete an event and refresh the baby's state."""
    store = await async_get_store(hass)
    try:
        await async_run(hass, store.delete_event, event.id)
    except UnknownEventError as err:
        raise _error("unknown_event", event_id=event.id) from err
    await entry.runtime_data.coordinator.async_refresh()


# ---------------------------------------------------------------- actions


def _fields(tracker: Tracker, call: ServiceCall) -> dict[str, Any]:
    """Return the tracker fields given in a service call."""
    return {
        key: call.data[key]
        for key in (str(marker) for marker in tracker.log_fields)
        if key in call.data
    }


def _register_timed(hass: HomeAssistant, tracker: TimedTracker) -> None:
    """Register a timed tracker's start, stop and log actions."""
    base = {probatio.Required(ATTR_DEVICE_ID): cv.string}

    async def start(call: ServiceCall) -> ServiceResponse:
        entry = entry_for_device(hass, call.data[ATTR_DEVICE_ID])
        event = await async_start_timer(
            hass,
            entry,
            tracker,
            _fields(tracker, call),
            when=call.data.get(ATTR_TIME),
            notes=call.data.get(ATTR_NOTES),
        )
        return {ATTR_EVENT_ID: event.id}

    async def stop(call: ServiceCall) -> ServiceResponse:
        entry = entry_for_device(hass, call.data[ATTR_DEVICE_ID])
        event = await async_stop_timer(
            hass, entry, tracker, when=call.data.get(ATTR_TIME)
        )
        return {ATTR_EVENT_ID: event.id}

    async def log(call: ServiceCall) -> ServiceResponse:
        entry = entry_for_device(hass, call.data[ATTR_DEVICE_ID])
        event = await async_log_duration(
            hass,
            entry,
            tracker,
            _fields(tracker, call),
            call.data[ATTR_DURATION],
            start=call.data.get(ATTR_TIME),
            notes=call.data.get(ATTR_NOTES),
        )
        return {ATTR_EVENT_ID: event.id}

    for name, handler, schema in (
        (
            tracker.start_service,
            start,
            {
                **base,
                **tracker.log_fields,
                probatio.Optional(ATTR_NOTES): _NOTES,
                probatio.Optional(ATTR_TIME): cv.datetime,
            },
        ),
        (
            tracker.stop_service,
            stop,
            {**base, probatio.Optional(ATTR_TIME): cv.datetime},
        ),
        (
            tracker.log_service,
            log,
            {
                **base,
                probatio.Required(ATTR_DURATION): cv.positive_time_period,
                **tracker.log_fields,
                probatio.Optional(ATTR_NOTES): _NOTES,
                probatio.Optional(ATTR_TIME): cv.datetime,
            },
        ),
    ):
        hass.services.async_register(
            DOMAIN,
            name,
            handler,
            schema=probatio.Schema(schema),
            supports_response=SupportsResponse.OPTIONAL,
        )


def _log_schema(tracker: Tracker) -> probatio.Schema:
    return probatio.Schema(
        {
            probatio.Required(ATTR_DEVICE_ID): cv.string,
            **tracker.log_fields,
            probatio.Optional(ATTR_NOTES): _NOTES,
            probatio.Optional(ATTR_TIME): cv.datetime,
        }
    )


UPDATE_EVENT_SCHEMA = probatio.Schema(
    {
        probatio.Required(ATTR_EVENT_ID): cv.string,
        probatio.Optional(ATTR_TIME): cv.datetime,
        probatio.Optional(ATTR_END_TIME): cv.datetime,
        probatio.Optional(ATTR_NOTES): probatio.Maybe(_NOTES),
        probatio.Optional(ATTR_FIELDS): dict,
    }
)

DELETE_EVENT_SCHEMA = probatio.Schema({probatio.Required(ATTR_EVENT_ID): cv.string})

LIST_EVENTS_SCHEMA = probatio.Schema(
    {
        probatio.Required(ATTR_DEVICE_ID): cv.string,
        probatio.Required(ATTR_START): cv.datetime,
        probatio.Required(ATTR_END): cv.datetime,
        probatio.Optional(ATTR_TRACKER): probatio.In(TRACKER_KEYS),
    }
)


async def event_and_entry(
    hass: HomeAssistant, event_id: str
) -> tuple[Event, BabyConfigEntry]:
    """Return a stored event of a configured baby, with that baby's entry."""
    store = await async_get_store(hass)
    event = await async_run(hass, store.get_event, event_id)
    if event is not None and (entry := entry_for_baby(hass, event.baby_id)):
        return event, entry
    raise _error("unknown_event", event_id=event_id)


@callback
def async_register_services(hass: HomeAssistant) -> None:
    """Register the actions of every tracker and the shared ones."""
    for tracker in TRACKERS.values():
        if isinstance(tracker, TimedTracker):
            _register_timed(hass, tracker)
            continue

        async def log_service(
            call: ServiceCall, tracker: Tracker = tracker
        ) -> ServiceResponse:
            entry = entry_for_device(hass, call.data[ATTR_DEVICE_ID])
            event = await async_log(
                hass,
                entry,
                tracker,
                _fields(tracker, call),
                when=call.data.get(ATTR_TIME),
                notes=call.data.get(ATTR_NOTES),
            )
            return {ATTR_EVENT_ID: event.id}

        hass.services.async_register(
            DOMAIN,
            tracker.log_service,
            log_service,
            schema=_log_schema(tracker),
            supports_response=SupportsResponse.OPTIONAL,
        )

    async def update_event(call: ServiceCall) -> ServiceResponse:
        event, entry = await event_and_entry(hass, call.data[ATTR_EVENT_ID])
        notes = call.data.get(ATTR_NOTES, ...)
        event = await async_update_fields(
            hass,
            entry,
            event,
            call.data.get(ATTR_FIELDS) or {},
            when=call.data.get(ATTR_TIME),
            end=call.data.get(ATTR_END_TIME),
            notes=notes if isinstance(notes, str) and notes else None,
            clear_notes=ATTR_NOTES in call.data and not notes,
        )
        return event_response(hass, event)

    async def delete_event(call: ServiceCall) -> None:
        event, entry = await event_and_entry(hass, call.data[ATTR_EVENT_ID])
        await async_delete(hass, entry, event)

    async def list_events(call: ServiceCall) -> ServiceResponse:
        entry = entry_for_device(hass, call.data[ATTR_DEVICE_ID])
        start = to_period_ts(call.data[ATTR_START])
        end = to_period_ts(call.data[ATTR_END])
        store = await async_get_store(hass)
        events = await async_run(
            hass,
            store.list_events,
            entry.runtime_data.baby_id,
            start,
            end,
            call.data.get(ATTR_TRACKER),
            tuple(TIMED_TRACKERS),
        )
        return {"events": [event_response(hass, event) for event in events]}

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_EVENT,
        update_event,
        schema=UPDATE_EVENT_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_EVENT, delete_event, schema=DELETE_EVENT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LIST_EVENTS,
        list_events,
        schema=LIST_EVENTS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


def to_period_ts(when: datetime) -> int:
    """Return a period bound as UTC epoch seconds; the future is allowed."""
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt_util.get_default_time_zone())
    return int(when.timestamp())
