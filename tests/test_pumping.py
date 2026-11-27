"""Tests for milk pumping sessions."""

from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby
from .test_calendar import NOW, events, frozen, local  # noqa: F401
from .test_diaper import attrs, eid, press, value
from .test_timed import act


def iso(when) -> str:
    """Return a timestamp sensor state."""
    return when.astimezone(dt_util.UTC).isoformat()


async def set_inputs(hass: HomeAssistant, entry, amount: float, side: str) -> None:
    """Set the pumping amount and side as a dashboard would."""
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": eid(hass, entry, "number", "pumping_amount"), "value": amount},
        blocking=True,
    )
    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": eid(hass, entry, "select", "pumping_side"), "option": side},
        blocking=True,
    )


async def test_enabled_for_a_baby(hass: HomeAssistant) -> None:
    """Enabling pumping creates its inputs, button and sensors."""
    entry = await add_baby(hass, trackers=["pumping"])
    other = await add_baby(hass, "Bruno", trackers=["bottle"])

    for platform, key in [
        ("number", "pumping_amount"),
        ("select", "pumping_side"),
        ("button", "pumping_log"),
        ("sensor", "pumping_last"),
        ("sensor", "pumping_count_today"),
        ("sensor", "pumping_ml_today"),
    ]:
        assert eid(hass, entry, platform, key)
        assert eid(hass, other, platform, key) is None


async def test_session_with_side(hass: HomeAssistant) -> None:
    """60 ml on the left is recorded."""
    entry = await add_baby(hass)

    event_id = await act(hass, entry, "log_pumping", amount=60, side="left")

    event = (await async_get_store(hass)).get_event(event_id)
    assert (event.tracker, event.amount, event.kind) == ("pumping", 60, "left")
    assert attrs(hass, entry, "pumping_last")["side"] == "left"
    assert attrs(hass, entry, "pumping_last")["amount"] == 60


@pytest.mark.parametrize("data", [{}, {"amount": 0}, {"amount": 60, "side": "middle"}])
async def test_invalid_session(hass: HomeAssistant, data: dict) -> None:
    """No amount, an amount of 0 or an unknown side fail."""
    entry = await add_baby(hass)

    with pytest.raises(Exception):  # noqa: B017, PT011
        await act(hass, entry, "log_pumping", **data)

    assert value(hass, entry, "sensor", "pumping_last") == "unknown"


async def test_session_from_the_dashboard(hass: HomeAssistant, frozen) -> None:  # noqa: F811
    """The button logs the inputs and resets both; a second press fails."""
    entry = await add_baby(hass)
    await set_inputs(hass, entry, 80, "both")

    await press(hass, entry, "pumping_log")

    assert value(hass, entry, "sensor", "pumping_ml_today") == "80.0"
    assert attrs(hass, entry, "pumping_last")["side"] == "both"
    assert value(hass, entry, "number", "pumping_amount") == "0"
    assert value(hass, entry, "select", "pumping_side") == "not_specified"

    # Later than the repeated press guard, which would drop the press.
    frozen.tick(timedelta(seconds=10))
    with pytest.raises(ServiceValidationError):
        await press(hass, entry, "pumping_log")
    assert value(hass, entry, "sensor", "pumping_count_today") == "1"


async def test_back_dated_press(hass: HomeAssistant) -> None:
    """The button follows "minutes ago"."""
    entry = await add_baby(hass)
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": eid(hass, entry, "number", "minutes_ago"), "value": 30},
        blocking=True,
    )
    await set_inputs(hass, entry, 50, "not_specified")

    await press(hass, entry, "pumping_log")

    assert value(hass, entry, "sensor", "pumping_last") == iso(
        NOW - timedelta(minutes=30)
    )
    assert attrs(hass, entry, "pumping_last")["side"] is None


async def test_inputs_empty_after_a_restart(hass: HomeAssistant) -> None:
    """The amount and side are not restored."""
    entry = await add_baby(hass)
    await set_inputs(hass, entry, 70, "right")

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert value(hass, entry, "number", "pumping_amount") == "0"
    assert value(hass, entry, "select", "pumping_side") == "not_specified"


async def test_two_sessions(hass: HomeAssistant) -> None:
    """60 ml and 80 ml: 2 sessions and 140 ml."""
    entry = await add_baby(hass)
    await act(hass, entry, "log_pumping", amount=60, time=local(NOW.replace(hour=8)))
    await act(hass, entry, "log_pumping", amount=80, time=local(NOW.replace(hour=12)))

    assert value(hass, entry, "sensor", "pumping_count_today") == "2"
    assert value(hass, entry, "sensor", "pumping_ml_today") == "140.0"
    assert value(hass, entry, "sensor", "pumping_last") == iso(NOW.replace(hour=12))


async def test_no_sessions_yet(hass: HomeAssistant) -> None:
    """The last session is unknown and the totals are 0."""
    entry = await add_baby(hass)

    assert value(hass, entry, "sensor", "pumping_last") == "unknown"
    assert value(hass, entry, "sensor", "pumping_count_today") == "0"


@pytest.mark.parametrize(
    ("language", "title"),
    [("en", "🧴 Pumping 80 ml both sides"), ("pt", "🧴 Extração 80 ml ambos os lados")],
)
async def test_session_in_the_calendar(
    hass: HomeAssistant, language: str, title: str
) -> None:
    """The title has the word for pumping, the amount and the side."""
    hass.config.language = language
    entry = await add_baby(hass)
    await act(
        hass,
        entry,
        "log_pumping",
        amount=80,
        side="both",
        time=local(NOW - timedelta(hours=1)),
    )

    [event] = await events(hass, entry, "feeding")

    assert event["summary"] == title
