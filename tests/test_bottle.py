"""Tests for the bottle tracker: the action, the dashboard inputs and the sensors."""

from datetime import datetime
from typing import Any

import probatio
import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    mock_restore_cache_with_extra_data,
)

from custom_components.baby_calendar.const import CONF_BABY_ID
from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby
from .test_diaper import attrs, eid, press, value
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


async def log(hass: HomeAssistant, entry: ConfigEntry, **data: Any) -> str:
    """Log a bottle through the action and return its id."""
    result = await call(
        hass, "log_bottle", {"device_id": device_id(hass, entry), **data}
    )
    await hass.async_block_till_done()
    return result["event_id"]


async def count(hass: HomeAssistant, entry: ConfigEntry) -> int:
    """Count the baby's bottle events."""
    store = await async_get_store(hass)
    return store.count_events(entry.data[CONF_BABY_ID], "bottle", 0, 10**10)


async def set_amount(hass: HomeAssistant, entry: ConfigEntry, amount: float) -> None:
    """Set the bottle amount input."""
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": eid(hass, entry, "number", "bottle_amount"), "value": amount},
        blocking=True,
    )


async def set_content(hass: HomeAssistant, entry: ConfigEntry, option: str) -> None:
    """Choose the bottle content input."""
    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": eid(hass, entry, "select", "bottle_content"), "option": option},
        blocking=True,
    )


# ------------------------------------------------------------------ action


async def test_bottle_with_content(hass: HomeAssistant) -> None:
    """A 90 ml formula bottle is recorded as such."""
    entry = await add_baby(hass)
    event_id = await log(hass, entry, amount=90, content="formula")

    event = (await async_get_store(hass)).get_event(event_id)
    assert (event.tracker, event.amount, event.kind) == ("bottle", 90, "formula")


async def test_small_first_feed(hass: HomeAssistant) -> None:
    """A 7 ml bottle is accepted."""
    entry = await add_baby(hass)
    event_id = await log(hass, entry, amount=7)

    event = (await async_get_store(hass)).get_event(event_id)
    assert (event.amount, event.kind) == (7, None)


@pytest.mark.parametrize(
    "data",
    [{}, {"amount": 0}, {"amount": -5}, {"amount": 90, "content": "juice"}],
)
async def test_invalid_bottle(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """A missing, zero or negative amount, or an unknown content, is refused."""
    entry = await add_baby(hass)
    with pytest.raises(probatio.Invalid):
        await log(hass, entry, **data)
    assert await count(hass, entry) == 0


# ------------------------------------------------------------ dashboard


async def test_inputs_start_empty(hass: HomeAssistant) -> None:
    """A new baby's amount is 0 and its content is not specified."""
    entry = await add_baby(hass)
    assert float(value(hass, entry, "number", "bottle_amount")) == 0
    assert value(hass, entry, "select", "bottle_content") == "not_specified"


async def test_usual_bottle(hass: HomeAssistant) -> None:
    """90 and formula then the button: a 90 ml formula bottle; the inputs stay."""
    entry = await add_baby(hass)
    await set_amount(hass, entry, 90)
    await set_content(hass, entry, "formula")

    await press(hass, entry, "bottle_log")

    last = attrs(hass, entry, "bottle_last")
    assert (last["amount"], last["content"]) == (90, "formula")
    assert float(value(hass, entry, "number", "bottle_amount")) == 90
    assert value(hass, entry, "select", "bottle_content") == "formula"


async def test_content_not_specified(hass: HomeAssistant) -> None:
    """With the content not specified the bottle has no content."""
    entry = await add_baby(hass)
    await set_amount(hass, entry, 60)
    await set_content(hass, entry, "formula")
    await set_content(hass, entry, "not_specified")

    await press(hass, entry, "bottle_log")

    assert attrs(hass, entry, "bottle_last")["content"] is None


async def test_amount_at_zero(hass: HomeAssistant) -> None:
    """The button fails with the amount at 0, and "minutes ago" still resets."""
    entry = await add_baby(hass)
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": eid(hass, entry, "number", "minutes_ago"), "value": 10},
        blocking=True,
    )

    with pytest.raises(ServiceValidationError) as err:
        await press(hass, entry, "bottle_log")

    assert err.value.translation_key == "bottle_amount_zero"
    assert await count(hass, entry) == 0
    assert value(hass, entry, "number", "minutes_ago") == "0"


async def test_inputs_restored_after_a_restart(hass: HomeAssistant) -> None:
    """The amount and the content come back after a restart."""
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State("number.alice_bottle_amount", "120"),
                {
                    "native_value": 120.0,
                    "native_min_value": 0,
                    "native_max_value": 500,
                    "native_step": 1,
                    "native_unit_of_measurement": "mL",
                },
            ),
            (State("select.alice_bottle_content", "breast_milk"), {}),
        ],
    )
    entry = await add_baby(hass)
    assert eid(hass, entry, "number", "bottle_amount") == "number.alice_bottle_amount"

    assert float(value(hass, entry, "number", "bottle_amount")) == 120
    assert value(hass, entry, "select", "bottle_content") == "breast_milk"

    await press(hass, entry, "bottle_log")
    last = attrs(hass, entry, "bottle_last")
    assert (last["amount"], last["content"]) == (120, "breast_milk")


async def test_inputs_kept_across_a_reload(hass: HomeAssistant) -> None:
    """Reloading the entry, as when trackers change, keeps the inputs."""
    entry = await add_baby(hass)
    await set_amount(hass, entry, 150)
    await set_content(hass, entry, "breast_milk")

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert float(value(hass, entry, "number", "bottle_amount")) == 150
    assert value(hass, entry, "select", "bottle_content") == "breast_milk"


async def test_no_bottle_entities_without_the_tracker(hass: HomeAssistant) -> None:
    """A baby without the bottle tracker has no bottle entities."""
    entry = await add_baby(hass, trackers=["diaper"])
    for platform, key in (
        ("number", "bottle_amount"),
        ("select", "bottle_content"),
        ("button", "bottle_log"),
        ("sensor", "bottle_last"),
    ):
        assert eid(hass, entry, platform, key) is None


# ----------------------------------------------------------------- sensors


async def test_two_bottles(hass: HomeAssistant) -> None:
    """90 ml and 120 ml today: 2 bottles and 210 ml."""
    entry = await add_baby(hass)
    await log(hass, entry, amount=90)
    await log(hass, entry, amount=120)

    assert value(hass, entry, "sensor", "bottle_count_today") == "2"
    assert float(value(hass, entry, "sensor", "bottle_ml_today")) == 210


async def test_amount_corrected(hass: HomeAssistant) -> None:
    """Correcting 120 ml to 100 ml gives 190 ml."""
    entry = await add_baby(hass)
    await log(hass, entry, amount=90)
    event_id = await log(hass, entry, amount=120)

    await call(hass, "update_event", {"event_id": event_id, "fields": {"amount": 100}})
    await hass.async_block_till_done()

    assert float(value(hass, entry, "sensor", "bottle_ml_today")) == 190


async def test_content_cleared(hass: HomeAssistant) -> None:
    """A correction can clear the content but not the amount."""
    entry = await add_baby(hass)
    event_id = await log(hass, entry, amount=90, content="formula")

    result = await call(
        hass, "update_event", {"event_id": event_id, "fields": {"content": None}}
    )
    assert (result["amount"], result["content"]) == (90, None)

    with pytest.raises(ServiceValidationError):
        await call(
            hass, "update_event", {"event_id": event_id, "fields": {"amount": None}}
        )


async def test_no_bottles_yet(hass: HomeAssistant) -> None:
    """With no bottles the last bottle is unknown and today's values are 0."""
    entry = await add_baby(hass)
    assert value(hass, entry, "sensor", "bottle_last") == STATE_UNKNOWN
    assert value(hass, entry, "sensor", "bottle_count_today") == "0"
    assert float(value(hass, entry, "sensor", "bottle_ml_today")) == 0


async def test_millilitres_sensor_unit(hass: HomeAssistant) -> None:
    """The millilitres sensor is a total in mL."""
    entry = await add_baby(hass)
    state = hass.states.get(eid(hass, entry, "sensor", "bottle_ml_today"))
    assert state.attributes["unit_of_measurement"] == "mL"
    assert state.attributes["state_class"] == "total"
