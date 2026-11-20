"""Tests for weight, length and temperature readings."""

from datetime import datetime, timedelta
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.baby_calendar.const import CONF_BABY_ID, DOMAIN
from custom_components.baby_calendar.data import async_get_store
from custom_components.baby_calendar.trackers.measurement import (
    LENGTH,
    TEMPERATURE,
    WEIGHT,
)

from .conftest import add_baby

TZ = dt_util.get_time_zone("Europe/Lisbon")
NOW = datetime(2026, 11, 20, 10, 0, tzinfo=TZ)


@pytest.fixture(autouse=True)
async def lisbon(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    """Run every test in Lisbon at 10:00."""
    await hass.config.async_set_time_zone("Europe/Lisbon")
    freezer.move_to(NOW)


def entity_id(hass: HomeAssistant, entry: ConfigEntry, platform: str, key: str):
    """Return the entity id of one of a baby's entities, or None."""
    return er.async_get(hass).async_get_entity_id(
        platform, DOMAIN, f"{entry.data[CONF_BABY_ID]}_{key}"
    )


def state(hass: HomeAssistant, entry: ConfigEntry, platform: str, key: str) -> str:
    """Return the state of one of a baby's entities."""
    return hass.states.get(entity_id(hass, entry, platform, key)).state


def device_id(hass: HomeAssistant, entry: ConfigEntry) -> str:
    """Return the device id of a baby."""
    return (
        dr.async_get(hass)
        .async_get_device_by_identifier(
            (DOMAIN, entry.data[CONF_BABY_ID]), entry.entry_id
        )
        .id
    )


async def log(hass: HomeAssistant, entry: ConfigEntry, key: str, **data: Any) -> str:
    """Log a reading with the action and return the event id."""
    result = await hass.services.async_call(
        DOMAIN,
        f"log_{key}",
        {"device_id": device_id(hass, entry), **data},
        blocking=True,
        return_response=True,
    )
    return result["event_id"]


async def set_number(hass: HomeAssistant, entity: str, value: float) -> None:
    """Set a number input as a dashboard would."""
    await hass.services.async_call(
        "number", "set_value", {"entity_id": entity, "value": value}, blocking=True
    )


async def press(hass: HomeAssistant, entity: str) -> None:
    """Press a button."""
    await hass.services.async_call(
        "button", "press", {"entity_id": entity}, blocking=True
    )


def iso(when: datetime) -> str:
    """Return a timestamp sensor state."""
    return when.isoformat(timespec="seconds")


# ----------------------------------------------------------------- trackers


async def test_only_weight_enabled(hass: HomeAssistant) -> None:
    """Enabling only weight creates only the weight entities."""
    entry = await add_baby(hass, trackers=["weight"])

    for platform, key in [
        ("number", "weight_value"),
        ("button", "weight_log"),
        ("sensor", "weight"),
        ("sensor", "weight_last"),
    ]:
        assert entity_id(hass, entry, platform, key)
    for key in ("length", "temperature"):
        assert entity_id(hass, entry, "sensor", key) is None
        assert entity_id(hass, entry, "number", f"{key}_value") is None


async def test_disabling_removes_the_entities(hass: HomeAssistant) -> None:
    """A measurement tracker disabled later loses its entities."""
    entry = await add_baby(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "details"}
    )
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"name": "Alice", "trackers": ["diaper"]}
    )
    await hass.async_block_till_done()

    assert entity_id(hass, entry, "sensor", "weight") is None
    assert entity_id(hass, entry, "button", "temperature_log") is None


# ----------------------------------------------------------------- service


async def test_weight_logged(hass: HomeAssistant) -> None:
    """A weight is recorded now, in grams; the sensors show it."""
    entry = await add_baby(hass)

    event_id = await log(hass, entry, "weight", value=3450)

    store = await async_get_store(hass)
    event = store.get_event(event_id)
    assert (event.tracker, event.amount) == ("weight", 3450)
    weight = hass.states.get(entity_id(hass, entry, "sensor", "weight"))
    assert weight.state == "3450.0"
    assert weight.attributes["unit_of_measurement"] == "g"
    assert weight.attributes["state_class"] == "measurement"
    assert weight.attributes["device_class"] == "weight"
    last = hass.states.get(entity_id(hass, entry, "sensor", "weight_last"))
    assert last.state == iso(NOW)
    assert last.attributes["event_id"] == event_id
    assert last.attributes["value"] == 3450


async def test_reading_from_a_past_check_up(hass: HomeAssistant) -> None:
    """A length three days ago is recorded at that time, with a note."""
    entry = await add_baby(hass)
    when = NOW - timedelta(days=3)

    event_id = await log(
        hass, entry, "length", value=51.5, time=when.isoformat(), notes="check-up"
    )

    event = (await async_get_store(hass)).get_event(event_id)
    assert event.start_ts == int(when.timestamp())
    assert event.amount == 51.5
    assert event.notes == "check-up"


async def test_value_missing(hass: HomeAssistant) -> None:
    """A reading without a value fails."""
    entry = await add_baby(hass)

    with pytest.raises(Exception, match="value"):
        await log(hass, entry, "weight")

    assert state(hass, entry, "sensor", "weight") == "unknown"


async def test_low_but_within_range(hass: HomeAssistant) -> None:
    """345 g is accepted: the range only catches gross errors."""
    entry = await add_baby(hass)

    await log(hass, entry, "weight", value=345)

    assert state(hass, entry, "sensor", "weight") == "345.0"


@pytest.mark.parametrize(
    ("key", "value", "minimum", "maximum"),
    [
        ("weight", 3.4, "300", "30000"),
        ("weight", 30001, "300", "30000"),
        ("length", 19.5, "20", "130"),
        ("length", 131, "20", "130"),
        ("temperature", 375, "30", "45"),
        ("temperature", 29.9, "30", "45"),
    ],
)
async def test_out_of_range(
    hass: HomeAssistant, key: str, value: float, minimum: str, maximum: str
) -> None:
    """A reading outside the range fails, naming the range."""
    entry = await add_baby(hass)

    with pytest.raises(ServiceValidationError) as err:
        await log(hass, entry, key, value=value)

    assert err.value.translation_key == "value_out_of_range"
    assert err.value.translation_placeholders["minimum"] == minimum
    assert err.value.translation_placeholders["maximum"] == maximum
    assert state(hass, entry, "sensor", key) == "unknown"


async def test_corrected_value(hass: HomeAssistant) -> None:
    """update_event changes the value, and refuses one outside the range."""
    entry = await add_baby(hass)
    event_id = await log(hass, entry, "weight", value=345)

    await hass.services.async_call(
        DOMAIN,
        "update_event",
        {"event_id": event_id, "fields": {"value": 3450}},
        blocking=True,
    )
    assert state(hass, entry, "sensor", "weight") == "3450.0"

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "update_event",
            {"event_id": event_id, "fields": {"value": 3.45}},
            blocking=True,
        )
    assert state(hass, entry, "sensor", "weight") == "3450.0"


# --------------------------------------------------------------- dashboard


async def test_temperature_from_the_dashboard(hass: HomeAssistant) -> None:
    """The button logs the input's value, and the input goes back to 0."""
    entry = await add_baby(hass)
    number = entity_id(hass, entry, "number", "temperature_value")
    await set_number(hass, number, 37.8)

    await press(hass, entity_id(hass, entry, "button", "temperature_log"))

    assert state(hass, entry, "sensor", "temperature") == "37.8"
    assert hass.states.get(number).state == "0"


async def test_stray_press(hass: HomeAssistant) -> None:
    """Pressing with the input at 0 fails and records nothing."""
    entry = await add_baby(hass)

    with pytest.raises(ServiceValidationError):
        await press(hass, entity_id(hass, entry, "button", "weight_log"))

    assert state(hass, entry, "sensor", "weight_last") == "unknown"


async def test_input_out_of_range(hass: HomeAssistant) -> None:
    """Pressing with a value outside the range fails and keeps the input."""
    entry = await add_baby(hass)
    number = entity_id(hass, entry, "number", "weight_value")
    await set_number(hass, number, 30)

    with pytest.raises(ServiceValidationError):
        await press(hass, entity_id(hass, entry, "button", "weight_log"))

    assert state(hass, entry, "sensor", "weight") == "unknown"
    assert hass.states.get(number).state == "30.0"


async def test_reading_back_dated(hass: HomeAssistant) -> None:
    """The button follows "minutes ago"."""
    entry = await add_baby(hass)
    await set_number(hass, entity_id(hass, entry, "number", "minutes_ago"), 20)
    await set_number(hass, entity_id(hass, entry, "number", "weight_value"), 3500)

    await press(hass, entity_id(hass, entry, "button", "weight_log"))

    assert state(hass, entry, "sensor", "weight_last") == iso(
        NOW - timedelta(minutes=20)
    )


async def test_input_zero_after_a_restart(hass: HomeAssistant) -> None:
    """The input is not restored."""
    entry = await add_baby(hass)
    number = entity_id(hass, entry, "number", "length_value")
    await set_number(hass, number, 50)

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(number).state == "0"


async def test_input_steps(hass: HomeAssistant) -> None:
    """Weight in steps of 1 g, length of 0.5 cm, temperature of 0.1 degrees."""
    entry = await add_baby(hass)

    steps = {
        key: hass.states.get(
            entity_id(hass, entry, "number", f"{key}_value")
        ).attributes["step"]
        for key in ("weight", "length", "temperature")
    }

    assert steps == {"weight": 1, "length": 0.5, "temperature": 0.1}


# ----------------------------------------------------------------- sensors


async def test_new_reading(hass: HomeAssistant) -> None:
    """A later reading replaces the earlier one."""
    entry = await add_baby(hass)
    await log(
        hass, entry, "weight", value=3450, time=(NOW - timedelta(days=7)).isoformat()
    )

    await log(hass, entry, "weight", value=3600)

    assert state(hass, entry, "sensor", "weight") == "3600.0"
    assert state(hass, entry, "sensor", "weight_last") == iso(NOW)


async def test_older_reading_added_later(hass: HomeAssistant) -> None:
    """A reading dated last week does not replace today's."""
    entry = await add_baby(hass)
    await log(hass, entry, "weight", value=3600)

    await log(
        hass, entry, "weight", value=3450, time=(NOW - timedelta(days=7)).isoformat()
    )

    assert state(hass, entry, "sensor", "weight") == "3600.0"


async def test_latest_reading_deleted(hass: HomeAssistant) -> None:
    """Deleting the latest reading shows the previous one."""
    entry = await add_baby(hass)
    earlier = NOW - timedelta(days=7)
    await log(hass, entry, "weight", value=3450, time=earlier.isoformat())
    latest = await log(hass, entry, "weight", value=3600)

    await hass.services.async_call(
        DOMAIN, "delete_event", {"event_id": latest}, blocking=True
    )

    assert state(hass, entry, "sensor", "weight") == "3450.0"
    assert state(hass, entry, "sensor", "weight_last") == iso(earlier)


async def test_no_readings_yet(hass: HomeAssistant) -> None:
    """Both sensors are unknown."""
    entry = await add_baby(hass)

    assert state(hass, entry, "sensor", "length") == "unknown"
    assert state(hass, entry, "sensor", "length_last") == "unknown"


async def test_yesterdays_fever(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """After 24 hours the temperature is unknown; its time stays."""
    entry = await add_baby(hass)
    await log(hass, entry, "temperature", value=39.5)
    assert state(hass, entry, "sensor", "temperature") == "39.5"

    later = NOW + timedelta(hours=25)
    freezer.move_to(later)
    async_fire_time_changed(hass, later)
    await hass.async_block_till_done()

    assert state(hass, entry, "sensor", "temperature") == "unknown"
    assert state(hass, entry, "sensor", "temperature_last") == iso(NOW)


async def test_old_temperature_after_a_restart(hass: HomeAssistant) -> None:
    """A temperature older than 24 hours is unknown from the start."""
    entry = await add_baby(hass)
    await log(
        hass,
        entry,
        "temperature",
        value=38,
        time=(NOW - timedelta(hours=30)).isoformat(),
    )

    assert state(hass, entry, "sensor", "temperature") == "unknown"


async def test_weight_from_last_month(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Weight does not expire."""
    entry = await add_baby(hass)
    await log(hass, entry, "weight", value=3450)

    later = NOW + timedelta(days=31)
    freezer.move_to(later)
    async_fire_time_changed(hass, later)
    await hass.async_block_till_done()

    assert state(hass, entry, "sensor", "weight") == "3450.0"


async def test_high_temperature_raises_nothing(hass: HomeAssistant) -> None:
    """39.5 is recorded with no alert of the integration's own."""
    entry = await add_baby(hass)
    notifications = []
    hass.bus.async_listen(
        "persistent_notifications_updated", lambda e: notifications.append(e)
    )

    await log(hass, entry, "temperature", value=39.5)
    await hass.async_block_till_done()

    assert state(hass, entry, "sensor", "temperature") == "39.5"
    assert notifications == []


# ---------------------------------------------------------------- calendar


@pytest.mark.parametrize(
    ("tracker", "amount", "language", "title"),
    [
        (WEIGHT, 3450, "en", "⚖️ 3450 g"),
        (LENGTH, 51.5, "en", "📏 51.5 cm"),
        (LENGTH, 51.5, "pt", "📏 51,5 cm"),
        (TEMPERATURE, 37.8, "en", "🌡️ 37.8 °C"),
        (TEMPERATURE, 37.8, "pt", "🌡️ 37,8 °C"),
        (WEIGHT, 3450, "pt", "⚖️ 3450 g"),
    ],
)
async def test_calendar_titles(
    hass: HomeAssistant, tracker: Any, amount: float, language: str, title: str
) -> None:
    """The title is the emoji, the value and the unit."""
    entry = await add_baby(hass)
    event_id = await log(hass, entry, tracker.key, value=amount)
    event = (await async_get_store(hass)).get_event(event_id)

    assert tracker.summary(event, language, 0) == title
