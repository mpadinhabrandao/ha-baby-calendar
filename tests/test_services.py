"""Tests for the actions, the event time rules and the per-baby state."""

from datetime import datetime, timedelta
from typing import Any

import probatio
import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.util import dt as dt_util

from custom_components.baby_calendar.const import CONF_BABY_ID, CONF_TRACKERS, DOMAIN
from custom_components.baby_calendar.coordinator import local_day
from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby

TZ = "Europe/Lisbon"
NOW = datetime(2026, 11, 20, 3, 20, tzinfo=dt_util.UTC)


@pytest.fixture(autouse=True)
async def lisbon(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    """Run every test in Lisbon at a fixed time."""
    await hass.config.async_set_time_zone(TZ)
    freezer.move_to(NOW)


def device_id(hass: HomeAssistant, entry: ConfigEntry) -> str:
    """Return the device id of a baby."""
    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, entry.data[CONF_BABY_ID]), entry.entry_id
    )
    return device.id


async def call(
    hass: HomeAssistant, service: str, data: dict[str, Any], response: bool = True
) -> Any:
    """Call one of the integration's actions and return its response."""
    return await hass.services.async_call(
        DOMAIN, service, data, blocking=True, return_response=response
    )


async def log_diaper(hass: HomeAssistant, entry: ConfigEntry, **data: Any) -> str:
    """Log a diaper change and return the event id."""
    result = await call(
        hass, "log_diaper", {"device_id": device_id(hass, entry), **data}
    )
    return result["event_id"]


async def list_day(
    hass: HomeAssistant, entry: ConfigEntry, day: datetime, **data: Any
) -> list[dict[str, Any]]:
    """List a baby's events of one local day."""
    start = dt_util.start_of_local_day(dt_util.as_local(day).date())
    result = await call(
        hass,
        "list_events",
        {
            "device_id": device_id(hass, entry),
            "start": start.isoformat(),
            "end": (start + timedelta(days=1)).isoformat(),
            **data,
        },
    )
    return result["events"]


def state(entry: ConfigEntry, tracker: str = "diaper") -> dict[str, Any]:
    """Return the current state of one tracker of a baby."""
    return entry.runtime_data.coordinator.data[tracker]


# -------------------------------------------------------------- event time


async def test_time_omitted(hass: HomeAssistant) -> None:
    """An event logged without a time is recorded now."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="wet")

    store = await async_get_store(hass)
    assert store.get_event(event_id).start_ts == int(NOW.timestamp())


async def test_late_entry(hass: HomeAssistant) -> None:
    """An event two hours in the past is recorded at that time."""
    entry = await add_baby(hass)
    when = NOW - timedelta(hours=2)
    event_id = await log_diaper(hass, entry, content="wet", time=when.isoformat())

    store = await async_get_store(hass)
    assert store.get_event(event_id).start_ts == int(when.timestamp())


async def test_naive_time_is_local(hass: HomeAssistant) -> None:
    """A time without a zone is taken in the Home Assistant time zone."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="wet", time="2026-11-20 01:00:00")

    store = await async_get_store(hass)
    expected = datetime(2026, 11, 20, 1, 0, tzinfo=dt_util.get_time_zone(TZ))
    assert store.get_event(event_id).start_ts == int(expected.timestamp())


async def test_future_time(hass: HomeAssistant) -> None:
    """An event an hour in the future is refused and nothing is recorded."""
    entry = await add_baby(hass)

    with pytest.raises(ServiceValidationError) as err:
        await log_diaper(
            hass, entry, content="wet", time=(NOW + timedelta(hours=1)).isoformat()
        )

    assert err.value.translation_key == "future_time"
    assert await list_day(hass, entry, NOW) == []


async def test_baby_omitted(hass: HomeAssistant) -> None:
    """A log call that names no baby fails, even with a single baby."""
    entry = await add_baby(hass)

    with pytest.raises(probatio.Invalid):
        await call(hass, "log_diaper", {"content": "wet"})

    assert await list_day(hass, entry, NOW) == []


async def test_unknown_baby(hass: HomeAssistant) -> None:
    """A device that is not a configured baby is refused."""
    await add_baby(hass)

    with pytest.raises(ServiceValidationError) as err:
        await call(hass, "log_diaper", {"device_id": "missing", "content": "wet"})

    assert err.value.translation_key == "unknown_baby"


async def test_tracker_not_enabled(hass: HomeAssistant) -> None:
    """Logging on a tracker the baby does not use is an error."""
    entry = await add_baby(hass, trackers=["bottle"])

    with pytest.raises(ServiceValidationError) as err:
        await log_diaper(hass, entry, content="wet")

    assert err.value.translation_key == "tracker_disabled"


async def test_identifier_and_notes_returned(hass: HomeAssistant) -> None:
    """The response holds the new event's id, and listing shows its notes."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="dirty", notes="green")

    assert await list_day(hass, entry, NOW) == [
        {
            "event_id": event_id,
            "tracker": "diaper",
            "time": dt_util.as_local(NOW).isoformat(),
            "content": "dirty",
            "stool": None,
            "notes": "green",
        }
    ]


async def test_two_babies_are_independent(hass: HomeAssistant) -> None:
    """Logging for one baby changes only that baby's state."""
    alice = await add_baby(hass, "Alice")
    bruno = await add_baby(hass, "Bruno")

    await log_diaper(hass, alice, content="wet")

    assert state(alice)["diaper_changes_today"] == 1
    assert state(bruno)["diaper_changes_today"] == 0
    assert await list_day(hass, bruno, NOW) == []


# ---------------------------------------------------------- update_event


async def test_time_corrected(hass: HomeAssistant) -> None:
    """Changing the time keeps the other fields."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="dirty", stool="soft", notes="n")
    earlier = NOW - timedelta(minutes=30)

    result = await call(
        hass, "update_event", {"event_id": event_id, "time": earlier.isoformat()}
    )

    assert result["time"] == dt_util.as_local(earlier).isoformat()
    assert (result["content"], result["stool"], result["notes"]) == (
        "dirty",
        "soft",
        "n",
    )
    assert (await list_day(hass, entry, NOW))[0]["time"] == result["time"]


async def test_note_cleared_and_set(hass: HomeAssistant) -> None:
    """An empty note clears it; a new note replaces it."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="wet", notes="old")

    result = await call(hass, "update_event", {"event_id": event_id, "notes": ""})
    assert result["notes"] is None
    result = await call(hass, "update_event", {"event_id": event_id, "notes": "new"})
    assert result["notes"] == "new"
    result = await call(hass, "update_event", {"event_id": event_id, "notes": None})
    assert result["notes"] is None


async def test_field_cleared_with_null(hass: HomeAssistant) -> None:
    """A field set to null is cleared."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="dirty", stool="soft")

    result = await call(
        hass, "update_event", {"event_id": event_id, "fields": {"stool": None}}
    )

    assert (result["content"], result["stool"]) == ("dirty", None)


async def test_fields_follow_the_logging_rules(hass: HomeAssistant) -> None:
    """Invalid or forbidden values are refused and nothing changes."""
    entry = await add_baby(hass)
    wet_id = await log_diaper(hass, entry, content="wet")

    for fields, key in (
        ({"content": "green"}, "invalid_fields"),
        ({"content": None}, "invalid_fields"),
        ({"colour": "x"}, "invalid_fields"),
        ({"stool": "soft"}, "stool_on_wet"),
    ):
        with pytest.raises(ServiceValidationError) as err:
            await call(hass, "update_event", {"event_id": wet_id, "fields": fields})
        assert err.value.translation_key == key

    assert (await list_day(hass, entry, NOW))[0]["content"] == "wet"


async def test_unknown_event(hass: HomeAssistant) -> None:
    """Correcting or deleting an unknown event is an error."""
    await add_baby(hass)

    for service, data in (
        ("update_event", {"event_id": "missing", "notes": "x"}),
        ("delete_event", {"event_id": "missing"}),
    ):
        with pytest.raises(ServiceValidationError) as err:
            await call(hass, service, data, response=service == "update_event")
        assert err.value.translation_key == "unknown_event"


async def test_event_of_a_removed_baby_is_unknown(hass: HomeAssistant) -> None:
    """Only events of configured babies can be corrected."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="wet")
    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError):
        await call(hass, "delete_event", {"event_id": event_id}, response=False)


async def test_disabled_tracker_events(hass: HomeAssistant) -> None:
    """Events of a disabled tracker can still be listed, corrected and deleted."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="wet")
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_TRACKERS: ["bottle"]}
    )
    await hass.async_block_till_done()

    assert len(await list_day(hass, entry, NOW)) == 1
    result = await call(hass, "update_event", {"event_id": event_id, "notes": "x"})
    assert result["notes"] == "x"
    await call(hass, "delete_event", {"event_id": event_id}, response=False)
    assert await list_day(hass, entry, NOW) == []


# ----------------------------------------------------- delete and listing


async def test_mistaken_entry_deleted(hass: HomeAssistant) -> None:
    """A deleted event disappears from listings and today's values."""
    entry = await add_baby(hass)
    event_id = await log_diaper(hass, entry, content="wet")
    assert state(entry)["diaper_changes_today"] == 1

    await call(hass, "delete_event", {"event_id": event_id}, response=False)

    assert await list_day(hass, entry, NOW) == []
    assert state(entry)["diaper_changes_today"] == 0


async def test_events_of_a_day_and_filter(hass: HomeAssistant) -> None:
    """A listing covers one baby's local day, oldest first, optionally filtered."""
    entry = await add_baby(hass)
    yesterday = NOW - timedelta(days=1)
    await log_diaper(hass, entry, content="wet", time=yesterday.isoformat())
    second = await log_diaper(hass, entry, content="dirty")
    first = await log_diaper(
        hass, entry, content="wet", time=(NOW - timedelta(hours=1)).isoformat()
    )
    bottle = await call(
        hass, "log_bottle", {"device_id": device_id(hass, entry), "amount": 90}
    )

    events = await list_day(hass, entry, NOW)
    assert [event["event_id"] for event in events] == [
        first,
        second,
        bottle["event_id"],
    ]

    bottles = await list_day(hass, entry, NOW, tracker="bottle")
    assert [event["event_id"] for event in bottles] == [bottle["event_id"]]
    assert bottles[0]["amount"] == 90


async def test_empty_period(hass: HomeAssistant) -> None:
    """A period without events returns an empty list."""
    entry = await add_baby(hass)
    assert await list_day(hass, entry, NOW - timedelta(days=30)) == []


# ------------------------------------------------------------ daily values


async def test_midnight_resets_today(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """At local midnight every daily value returns to 0 without a write."""
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    entry = await add_baby(hass)
    await log_diaper(hass, entry, content="both")
    assert state(entry)["diaper_changes_today"] == 1

    midnight = dt_util.start_of_local_day() + timedelta(days=1)
    freezer.move_to(midnight)
    async_fire_time_changed(hass, midnight)
    await hass.async_block_till_done()

    assert state(entry)["diaper_changes_today"] == 0
    assert state(entry)["diaper_last"] is not None


async def test_late_entry_for_yesterday(hass: HomeAssistant) -> None:
    """An event logged today for yesterday evening does not change today."""
    entry = await add_baby(hass)
    yesterday_evening = dt_util.start_of_local_day() - timedelta(hours=2)

    await log_diaper(hass, entry, content="wet", time=yesterday_evening.isoformat())

    assert state(entry)["diaper_changes_today"] == 0


async def test_day_with_a_daylight_saving_change(hass: HomeAssistant) -> None:
    """The local day is 23 hours when the clocks go forward."""
    day = local_day(datetime(2026, 3, 29, 12, 0, tzinfo=dt_util.UTC))
    assert day.end - day.start == 23 * 3600
    day = local_day(datetime(2026, 10, 25, 12, 0, tzinfo=dt_util.UTC))
    assert day.end - day.start == 25 * 3600


async def test_local_day_uses_the_local_date(hass: HomeAssistant) -> None:
    """Late evening in a zone behind UTC is still that local day."""
    await hass.config.async_set_time_zone("America/Los_Angeles")
    # 03:20 UTC on the 20th is 19:20 on the 19th in Los Angeles.
    day = local_day(NOW)
    start = datetime(2026, 11, 19, tzinfo=dt_util.get_time_zone("America/Los_Angeles"))
    assert (day.start, day.end) == (
        int(start.timestamp()),
        int((start + timedelta(days=1)).timestamp()),
    )
