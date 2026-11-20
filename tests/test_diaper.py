"""Tests for the diaper tracker: the action, the buttons, the prompt and the sensors."""

from datetime import datetime, timedelta
from typing import Any

import probatio
import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.baby_calendar.const import CONF_BABY_ID, DOMAIN
from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby
from .test_services import call, device_id

NOW = datetime(2026, 11, 20, 10, 0, tzinfo=dt_util.UTC)


@pytest.fixture(autouse=True)
async def frozen(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> FrozenDateTimeFactory:
    """Run in Lisbon at a fixed time."""
    await hass.config.async_set_time_zone("Europe/Lisbon")
    freezer.move_to(NOW)
    return freezer


def eid(hass: HomeAssistant, entry: ConfigEntry, platform: str, key: str) -> str | None:
    """Return the entity id of one of a baby's entities."""
    return er.async_get(hass).async_get_entity_id(
        platform, DOMAIN, f"{entry.data[CONF_BABY_ID]}_{key}"
    )


def value(hass: HomeAssistant, entry: ConfigEntry, platform: str, key: str) -> str:
    """Return the state of one of a baby's entities."""
    return hass.states.get(eid(hass, entry, platform, key)).state


def attrs(hass: HomeAssistant, entry: ConfigEntry, key: str) -> dict[str, Any]:
    """Return the attributes of one of a baby's sensors."""
    return dict(hass.states.get(eid(hass, entry, "sensor", key)).attributes)


async def press(hass: HomeAssistant, entry: ConfigEntry, key: str) -> None:
    """Press one of a baby's buttons."""
    await hass.services.async_call(
        "button", "press", {"entity_id": eid(hass, entry, "button", key)}, blocking=True
    )
    await hass.async_block_till_done()


async def log(hass: HomeAssistant, entry: ConfigEntry, **data: Any) -> str:
    """Log a diaper change through the action and return its id."""
    result = await call(
        hass, "log_diaper", {"device_id": device_id(hass, entry), **data}
    )
    await hass.async_block_till_done()
    return result["event_id"]


async def stored(hass: HomeAssistant, event_id: str):
    """Return a stored event."""
    return (await async_get_store(hass)).get_event(event_id)


# ------------------------------------------------------------------ action


async def test_wet_diaper(hass: HomeAssistant) -> None:
    """A wet change is one event with the content wet."""
    entry = await add_baby(hass)
    event = await stored(hass, await log(hass, entry, content="wet"))
    assert (event.tracker, event.kind, event.data) == ("diaper", "wet", {})


async def test_both_is_one_event(hass: HomeAssistant) -> None:
    """A wet and dirty change is a single event."""
    entry = await add_baby(hass)
    await log(hass, entry, content="both")

    store = await async_get_store(hass)
    assert store.count_events(entry.data[CONF_BABY_ID], "diaper", 0, 10**10) == 1


async def test_dirty_with_type(hass: HomeAssistant) -> None:
    """A dirty change carries its stool type."""
    entry = await add_baby(hass)
    event = await stored(hass, await log(hass, entry, content="dirty", stool="soft"))
    assert event.data == {"stool": "soft"}


@pytest.mark.parametrize(
    "data",
    [{"content": "green"}, {"content": "dirty", "stool": "green"}, {}],
)
async def test_invalid_content(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Unknown or missing values are refused."""
    entry = await add_baby(hass)
    with pytest.raises(probatio.Invalid):
        await log(hass, entry, **data)
    store = await async_get_store(hass)
    assert store.count_events(entry.data[CONF_BABY_ID], "diaper", 0, 10**10) == 0


async def test_type_on_a_wet_diaper(hass: HomeAssistant) -> None:
    """A stool type on a wet diaper is refused and nothing is recorded."""
    entry = await add_baby(hass)
    with pytest.raises(ServiceValidationError) as err:
        await log(hass, entry, content="wet", stool="soft")
    assert err.value.translation_key == "stool_on_wet"
    store = await async_get_store(hass)
    assert store.count_events(entry.data[CONF_BABY_ID], "diaper", 0, 10**10) == 0


async def test_corrected_to_wet(hass: HomeAssistant) -> None:
    """Correcting a dirty change to wet drops its stool type."""
    entry = await add_baby(hass)
    event_id = await log(hass, entry, content="dirty", stool="soft")

    result = await call(
        hass, "update_event", {"event_id": event_id, "fields": {"content": "wet"}}
    )

    assert (result["content"], result["stool"]) == ("wet", None)
    assert (await stored(hass, event_id)).data == {}


# ----------------------------------------------------------------- buttons


async def test_dirty_button(hass: HomeAssistant) -> None:
    """The dirty button logs a dirty change with no stool type, now."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_dirty")

    event = entry.runtime_data.coordinator.data["diaper"]["diaper_last"]
    assert (event.kind, event.data, event.start_ts) == (
        "dirty",
        {},
        int(NOW.timestamp()),
    )


async def test_button_from_an_automation(hass: HomeAssistant) -> None:
    """An automation pressing the wet button records a wet change."""
    entry = await add_baby(hass)
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": eid(hass, entry, "button", "diaper_wet")},
        blocking=True,
        context=None,
    )
    await hass.async_block_till_done()
    assert value(hass, entry, "sensor", "diaper_wet_today") == "1"


async def test_changed_twenty_minutes_ago(hass: HomeAssistant) -> None:
    """With "minutes ago" at 20 the wet button logs 20 minutes earlier."""
    entry = await add_baby(hass)
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": eid(hass, entry, "number", "minutes_ago"), "value": 20},
        blocking=True,
    )

    await press(hass, entry, "diaper_wet")

    last = entry.runtime_data.coordinator.data["diaper"]["diaper_last"]
    assert last.start_ts == int((NOW - timedelta(minutes=20)).timestamp())
    assert value(hass, entry, "number", "minutes_ago") == "0"


async def test_double_tap(hass: HomeAssistant, frozen: FrozenDateTimeFactory) -> None:
    """Two presses within a second record one change."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_wet")
    frozen.tick(0.5)
    await press(hass, entry, "diaper_wet")
    assert value(hass, entry, "sensor", "diaper_changes_today") == "1"


async def test_wrong_button_undone(hass: HomeAssistant) -> None:
    """Undo right after a wrong press removes that change."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_dirty")
    await press(hass, entry, "undo")
    assert value(hass, entry, "sensor", "diaper_changes_today") == "0"
    assert value(hass, entry, "sensor", "diaper_last") == STATE_UNKNOWN


async def test_type_added_as_a_second_tap(hass: HomeAssistant) -> None:
    """Dirty then soft gives one dirty change with the type soft."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_dirty")
    await press(hass, entry, "stool_soft")

    assert value(hass, entry, "sensor", "diaper_changes_today") == "1"
    assert attrs(hass, entry, "diaper_last_dirty")["stool"] == "soft"


async def test_type_changed(hass: HomeAssistant) -> None:
    """A second stool button replaces the type."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_both")
    await press(hass, entry, "stool_soft")
    await press(hass, entry, "stool_hard")
    assert attrs(hass, entry, "diaper_last_dirty")["stool"] == "hard"


async def test_last_diaper_was_wet(hass: HomeAssistant) -> None:
    """A stool button after a wet change fails and changes nothing."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_dirty")
    await press(hass, entry, "diaper_wet")

    with pytest.raises(HomeAssistantError) as err:
        await press(hass, entry, "stool_soft")

    assert err.value.translation_key == "stool_not_dirty"
    assert attrs(hass, entry, "diaper_last_dirty")["stool"] is None


async def test_too_late(hass: HomeAssistant, frozen: FrozenDateTimeFactory) -> None:
    """A stool button 30 minutes after the dirty change fails."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_dirty")
    frozen.tick(timedelta(minutes=30))

    with pytest.raises(HomeAssistantError) as err:
        await press(hass, entry, "stool_soft")

    assert err.value.translation_key == "stool_too_late"
    assert attrs(hass, entry, "diaper_last_dirty")["stool"] is None


async def test_stool_button_with_no_diaper(hass: HomeAssistant) -> None:
    """A stool button with nothing logged fails."""
    entry = await add_baby(hass)
    with pytest.raises(HomeAssistantError):
        await press(hass, entry, "stool_normal")


# ------------------------------------------------------------------ prompt


async def test_prompt_appears_and_is_answered(hass: HomeAssistant) -> None:
    """The prompt turns on after a dirty change and off once a type is set."""
    entry = await add_baby(hass)
    assert value(hass, entry, "binary_sensor", "stool_prompt") == STATE_OFF

    await press(hass, entry, "diaper_dirty")
    assert value(hass, entry, "binary_sensor", "stool_prompt") == STATE_ON

    await press(hass, entry, "stool_normal")
    assert value(hass, entry, "binary_sensor", "stool_prompt") == STATE_OFF


async def test_prompt_ignored(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """The prompt turns off by itself 10 minutes after the dirty change."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_dirty")

    frozen.tick(timedelta(minutes=10))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert value(hass, entry, "binary_sensor", "stool_prompt") == STATE_OFF
    assert attrs(hass, entry, "diaper_last_dirty")["stool"] is None


async def test_prompt_stays_off_for_a_wet_diaper(hass: HomeAssistant) -> None:
    """A wet change never turns the prompt on."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_wet")
    assert value(hass, entry, "binary_sensor", "stool_prompt") == STATE_OFF


async def test_prompt_off_after_undo(hass: HomeAssistant) -> None:
    """Undoing the dirty change turns the prompt off."""
    entry = await add_baby(hass)
    await press(hass, entry, "diaper_dirty")
    await press(hass, entry, "undo")
    assert value(hass, entry, "binary_sensor", "stool_prompt") == STATE_OFF


# ----------------------------------------------------------------- sensors


async def test_no_events_yet(hass: HomeAssistant) -> None:
    """With no changes the last sensors are unknown and today's are 0."""
    entry = await add_baby(hass)
    for key in ("diaper_last", "diaper_last_wet", "diaper_last_dirty"):
        assert value(hass, entry, "sensor", key) == STATE_UNKNOWN
    for key in ("diaper_changes_today", "diaper_wet_today", "diaper_dirty_today"):
        assert value(hass, entry, "sensor", key) == "0"


async def test_after_a_dirty_diaper(hass: HomeAssistant) -> None:
    """The last change and last dirty show 10:00, the last wet shows 08:00."""
    entry = await add_baby(hass)
    eight = NOW - timedelta(hours=2)
    await log(hass, entry, content="wet", time=eight.isoformat())
    await log(hass, entry, content="dirty", stool="soft")

    assert value(hass, entry, "sensor", "diaper_last") == NOW.isoformat()
    assert value(hass, entry, "sensor", "diaper_last_dirty") == NOW.isoformat()
    assert value(hass, entry, "sensor", "diaper_last_wet") == eight.isoformat()
    dirty = attrs(hass, entry, "diaper_last_dirty")
    assert (dirty["content"], dirty["stool"]) == ("dirty", "soft")
    assert dirty["event_id"]


async def test_mixed_day(hass: HomeAssistant) -> None:
    """One wet, one dirty and one both: 3 changes, 2 wet, 2 dirty."""
    entry = await add_baby(hass)
    for content in ("wet", "dirty", "both"):
        await log(hass, entry, content=content)

    assert value(hass, entry, "sensor", "diaper_changes_today") == "3"
    assert value(hass, entry, "sensor", "diaper_wet_today") == "2"
    assert value(hass, entry, "sensor", "diaper_dirty_today") == "2"
    assert value(hass, entry, "sensor", "diaper_last_wet") == NOW.isoformat()


async def test_latest_event_deleted(hass: HomeAssistant) -> None:
    """Deleting the latest change shows the previous matching one."""
    entry = await add_baby(hass)
    earlier = NOW - timedelta(hours=1)
    await log(hass, entry, content="dirty", time=earlier.isoformat())
    latest = await log(hass, entry, content="dirty")

    await call(hass, "delete_event", {"event_id": latest}, response=False)
    await hass.async_block_till_done()

    assert value(hass, entry, "sensor", "diaper_last_dirty") == earlier.isoformat()


async def test_daily_sensors_are_statistics_totals(hass: HomeAssistant) -> None:
    """Daily sensors are totals that reset at local midnight."""
    entry = await add_baby(hass)
    state = hass.states.get(eid(hass, entry, "sensor", "diaper_changes_today"))
    assert state.attributes["state_class"] == "total"
    assert state.attributes["last_reset"] == dt_util.start_of_local_day().isoformat()


async def test_no_diaper_entities_without_the_tracker(hass: HomeAssistant) -> None:
    """A baby without the diaper tracker has no diaper entities."""
    entry = await add_baby(hass, trackers=["bottle"])
    assert eid(hass, entry, "button", "diaper_wet") is None
    assert eid(hass, entry, "sensor", "diaper_last") is None
    assert eid(hass, entry, "binary_sensor", "stool_prompt") is None
    assert eid(hass, entry, "button", "undo") is not None
