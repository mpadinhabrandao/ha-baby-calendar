"""Tests for the calendar: titles, placement, edits and deletion."""

from datetime import datetime, timedelta
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.calendar import CalendarEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.baby_calendar.calendar_strings import format_duration
from custom_components.baby_calendar.const import CONF_TRACKERS
from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby
from .test_diaper import attrs, eid, press, value
from .test_timed import act

TZ = dt_util.get_time_zone("Europe/Lisbon")
NOW = datetime(2026, 11, 20, 16, 0, tzinfo=TZ)


@pytest.fixture(autouse=True)
async def frozen(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> FrozenDateTimeFactory:
    """Run in Lisbon at 16:00 on a fixed day, in English."""
    await hass.config.async_set_time_zone("Europe/Lisbon")
    hass.config.language = "en"
    freezer.move_to(NOW)
    return freezer


def calendar_id(hass: HomeAssistant, entry: ConfigEntry) -> str:
    """Return the entity id of a baby's calendar."""
    return eid(hass, entry, "calendar", "calendar")


async def events(
    hass: HomeAssistant,
    entry: ConfigEntry,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[dict[str, Any]]:
    """Return the calendar events of a period, today by default."""
    start = start or NOW.replace(hour=0)
    end = end or start + timedelta(days=1)
    entity_id = calendar_id(hass, entry)
    result = await hass.services.async_call(
        "calendar",
        "get_events",
        {"start_date_time": start, "end_date_time": end},
        target={"entity_id": entity_id},
        blocking=True,
        return_response=True,
    )
    return result[entity_id]["events"]


async def ws(hass_ws_client, hass: HomeAssistant, **message: Any) -> dict[str, Any]:
    """Send one calendar websocket command and return the reply."""
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(message)
    return await client.receive_json()


def local(when: datetime) -> str:
    """Format a time as the calendar service returns it."""
    return when.isoformat()


# ------------------------------------------------------------ presentation


def test_durations() -> None:
    """Durations read 45 min, 2 h and 1 h 20 min."""
    assert format_duration(45 * 60) == "45 min"
    assert format_duration(2 * 3600) == "2 h"
    assert format_duration(80 * 60) == "1 h 20 min"


async def test_titles_and_placement(hass: HomeAssistant) -> None:
    """Every tracker appears in one calendar, with its title and its block."""
    entry = await add_baby(hass)
    nine = NOW.replace(hour=9)
    await act(
        hass, entry, "log_diaper", content="dirty", stool="soft", time=local(nine)
    )
    await act(
        hass,
        entry,
        "log_bottle",
        amount=90,
        content="formula",
        notes="spat up a little",
        time=local(nine.replace(hour=10)),
    )
    await act(
        hass,
        entry,
        "log_sleep",
        duration={"minutes": 80},
        time=local(nine.replace(hour=11)),
    )
    await act(
        hass,
        entry,
        "log_breastfeeding",
        duration={"minutes": 15},
        side="left",
        time=local(nine.replace(hour=13)),
    )

    listed = await events(hass, entry)

    assert [(e["summary"], e["start"], e["end"]) for e in listed] == [
        ("💩 Dirty diaper (soft)", local(nine), local(nine + timedelta(minutes=5))),
        (
            "🍼 Bottle 90 ml formula",
            local(nine.replace(hour=10)),
            local(nine.replace(hour=10, minute=5)),
        ),
        (
            "😴 Sleep 1 h 20 min",
            local(nine.replace(hour=11)),
            local(nine.replace(hour=12, minute=20)),
        ),
        (
            "🤱 Breastfeeding left 15 min",
            local(nine.replace(hour=13)),
            local(nine.replace(hour=13, minute=15)),
        ),
    ]
    assert [e.get("description", "") for e in listed] == [
        "",
        "spat up a little",
        "",
        "",
    ]


async def test_titles_in_portuguese(hass: HomeAssistant) -> None:
    """A Portuguese instance titles a formula bottle in Portuguese."""
    hass.config.language = "pt"
    entry = await add_baby(hass)
    await act(hass, entry, "log_bottle", amount=90, content="formula")
    await act(hass, entry, "log_breastfeeding", duration={"minutes": 5})
    summaries = [e["summary"] for e in await events(hass, entry)]
    # The feed ended now, so it started before the bottle.
    assert summaries == ["🤱 Mamada 5 min", "🍼 Biberão 90 ml fórmula"]


async def test_sleep_in_progress(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """A running sleep spans from its start to now and says it is in progress."""
    entry = await add_baby(hass)
    await act(hass, entry, "start_sleep", time=local(NOW - timedelta(minutes=90)))
    frozen.tick(30)

    [event] = await events(hass, entry)

    assert event["summary"] == "😴 Sleep in progress"
    assert event["start"] == local(NOW - timedelta(minutes=90))
    assert event["end"] == local(NOW + timedelta(minutes=1))
    assert value(hass, entry, "calendar", "calendar") == STATE_ON


async def test_state_off_after_a_diaper(hass: HomeAssistant) -> None:
    """An instantaneous event does not turn the calendar on."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_wet")
    assert value(hass, entry, "calendar", "calendar") == STATE_OFF


async def test_two_babies(hass: HomeAssistant) -> None:
    """An event of one baby is not in the other's calendar."""
    alice = await add_baby(hass, "Alice")
    bruno = await add_baby(hass, "Bruno")
    await act(hass, alice, "log_diaper", content="wet")
    assert len(await events(hass, alice)) == 1
    assert await events(hass, bruno) == []


async def test_history_and_disabled_trackers(hass: HomeAssistant) -> None:
    """Old events and events of a disabled tracker are shown; tomorrow is empty."""
    entry = await add_baby(hass)
    months_ago = NOW - timedelta(days=90)
    await act(hass, entry, "log_bottle", amount=60, time=local(months_ago))
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_TRACKERS: ["diaper"]}
    )
    await hass.async_block_till_done()

    week = await events(
        hass, entry, months_ago - timedelta(days=3), months_ago + timedelta(days=4)
    )
    assert [e["summary"] for e in week] == ["🍼 Bottle 60 ml"]
    assert await events(hass, entry, NOW + timedelta(days=1)) == []


async def test_sleep_overlapping_the_range(hass: HomeAssistant) -> None:
    """A sleep from 23:00 yesterday is in today's view."""
    entry = await add_baby(hass)
    yesterday = NOW.replace(hour=23) - timedelta(days=1)
    await act(hass, entry, "log_sleep", duration={"hours": 7}, time=local(yesterday))
    [event] = await events(hass, entry)
    assert event["summary"] == "😴 Sleep 7 h"


async def test_logged_by_button_appears(hass: HomeAssistant) -> None:
    """An event logged by a button is in the calendar without a reload."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_both")
    assert [e["summary"] for e in await events(hass, entry)] == [
        "💧💩 Wet and dirty diaper"
    ]


async def test_supported_features(hass: HomeAssistant) -> None:
    """The calendar offers edit and delete, and no creation."""
    entry = await add_baby(hass)
    features = hass.states.get(calendar_id(hass, entry)).attributes[
        "supported_features"
    ]
    assert features & CalendarEntityFeature.UPDATE_EVENT
    assert features & CalendarEntityFeature.DELETE_EVENT
    assert not features & CalendarEntityFeature.CREATE_EVENT


# ----------------------------------------------------------------- edits


async def update(
    hass: HomeAssistant,
    hass_ws_client,
    entry: ConfigEntry,
    uid: str,
    **event: Any,
) -> dict[str, Any]:
    """Save an event from the calendar dialog."""
    stored = (await async_get_store(hass)).get_event(uid)
    start = dt_util.utc_from_timestamp(stored.start_ts)
    end = dt_util.utc_from_timestamp(stored.end_ts or stored.start_ts + 300)
    payload = {
        "dtstart": start.isoformat(),
        "dtend": end.isoformat(),
        "summary": "anything",
        **event,
    }
    return await ws(
        hass_ws_client,
        hass,
        type="calendar/event/update",
        entity_id=calendar_id(hass, entry),
        uid=uid,
        event=payload,
    )


async def test_diaper_moved(hass: HomeAssistant, hass_ws_client) -> None:
    """Moving a diaper from 10:00 to 09:30 moves it and its sensor."""
    entry = await add_baby(hass)
    ten = NOW.replace(hour=10)
    uid = await act(hass, entry, "log_diaper", content="wet", time=local(ten))

    reply = await update(
        hass,
        hass_ws_client,
        entry,
        uid,
        dtstart=local(ten - timedelta(minutes=30)),
        dtend=local(ten - timedelta(minutes=25)),
    )

    assert reply["success"]
    assert (
        value(hass, entry, "sensor", "diaper_last")
        == (ten - timedelta(minutes=30)).astimezone(dt_util.UTC).isoformat()
    )


async def test_sleep_end_corrected(hass: HomeAssistant, hass_ws_client) -> None:
    """Moving a sleep's end from 14:45 to 15:10 changes today's sleep."""
    entry = await add_baby(hass)
    two = NOW.replace(hour=14)
    uid = await act(hass, entry, "log_sleep", duration={"minutes": 45}, time=local(two))

    reply = await update(
        hass,
        hass_ws_client,
        entry,
        uid,
        dtstart=local(two),
        dtend=local(two + timedelta(minutes=70)),
    )

    assert reply["success"]
    assert float(value(hass, entry, "sensor", "sleep_duration_today")) == 70


async def test_moved_into_the_future(hass: HomeAssistant, hass_ws_client) -> None:
    """A move into the future is refused and nothing changes."""
    entry = await add_baby(hass)
    uid = await act(hass, entry, "log_diaper", content="wet")
    future = NOW + timedelta(hours=2)

    reply = await update(
        hass,
        hass_ws_client,
        entry,
        uid,
        dtstart=local(future),
        dtend=local(future + timedelta(minutes=5)),
    )

    assert not reply["success"]
    stored = (await async_get_store(hass)).get_event(uid)
    assert stored.start_ts == int(NOW.timestamp())


async def test_notes(hass: HomeAssistant, hass_ws_client) -> None:
    """A note is added, kept over two paragraphs and removed; fields stay."""
    entry = await add_baby(hass)
    uid = await act(hass, entry, "log_bottle", amount=90, content="formula")
    store = await async_get_store(hass)

    assert (
        await update(hass, hass_ws_client, entry, uid, description="took it slowly")
    )["success"]
    assert store.get_event(uid).notes == "took it slowly"

    text = "first line\n\nsecond paragraph"
    await update(hass, hass_ws_client, entry, uid, description=text)
    assert store.get_event(uid).notes == text

    await update(hass, hass_ws_client, entry, uid, description="")
    stored = store.get_event(uid)
    assert (stored.notes, stored.amount, stored.kind) == (None, 90, "formula")


async def test_note_on_a_running_sleep(hass: HomeAssistant, hass_ws_client) -> None:
    """A note added to a running sleep keeps the timer running."""
    entry = await add_baby(hass)
    uid = await act(hass, entry, "start_sleep")

    reply = await update(
        hass,
        hass_ws_client,
        entry,
        uid,
        dtend=local(NOW + timedelta(hours=1)),
        description="restless",
    )

    assert reply["success"]
    stored = (await async_get_store(hass)).get_event(uid)
    assert (stored.notes, stored.end_ts) == ("restless", None)
    assert value(hass, entry, "switch", "sleep_timer") == STATE_ON


async def test_title_edit_and_untouched_save(
    hass: HomeAssistant, hass_ws_client
) -> None:
    """An edited title changes nothing, and an untouched save is a no-op."""
    entry = await add_baby(hass)
    uid = await act(hass, entry, "log_bottle", amount=90, content="formula")
    store = await async_get_store(hass)
    before = store.get_event(uid)

    await update(hass, hass_ws_client, entry, uid, summary="🍼 Bottle 500 ml")

    assert store.get_event(uid) == before
    assert attrs(hass, entry, "bottle_last")["amount"] == 90


@pytest.mark.parametrize(
    "event",
    [
        {"rrule": "FREQ=DAILY"},
        {"dtstart": "2026-11-20", "dtend": "2026-11-21"},
    ],
)
async def test_recurrence_and_all_day_refused(
    hass: HomeAssistant, hass_ws_client, event: dict[str, Any]
) -> None:
    """Recurring and all-day values are refused."""
    entry = await add_baby(hass)
    uid = await act(hass, entry, "log_diaper", content="wet")
    reply = await update(hass, hass_ws_client, entry, uid, **event)
    assert not reply["success"]


async def test_deleted_from_the_calendar(hass: HomeAssistant, hass_ws_client) -> None:
    """A bottle deleted in the calendar leaves today's bottle sensors."""
    entry = await add_baby(hass)
    uid = await act(hass, entry, "log_bottle", amount=90)

    reply = await ws(
        hass_ws_client,
        hass,
        type="calendar/event/delete",
        entity_id=calendar_id(hass, entry),
        uid=uid,
    )

    assert reply["success"]
    assert value(hass, entry, "sensor", "bottle_count_today") == "0"
    assert await events(hass, entry) == []


async def test_event_of_another_baby_refused(
    hass: HomeAssistant, hass_ws_client
) -> None:
    """A calendar cannot delete another baby's event."""
    alice = await add_baby(hass, "Alice")
    bruno = await add_baby(hass, "Bruno")
    uid = await act(hass, alice, "log_diaper", content="wet")

    reply = await ws(
        hass_ws_client,
        hass,
        type="calendar/event/delete",
        entity_id=calendar_id(hass, bruno),
        uid=uid,
    )

    assert not reply["success"]
    assert (await async_get_store(hass)).get_event(uid) is not None
