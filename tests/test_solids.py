"""Tests for solid food meals."""

from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby
from .test_calendar import NOW, events, frozen, local, update  # noqa: F401
from .test_diaper import attrs, eid, press, value
from .test_timed import act


def iso(when) -> str:
    """Return a timestamp sensor state."""
    return when.astimezone(dt_util.UTC).isoformat()


async def test_enabled_for_a_baby(hass: HomeAssistant) -> None:
    """Enabling solids creates its button and sensors; disabled, none."""
    entry = await add_baby(hass, trackers=["solids"])
    other = await add_baby(hass, "Bruno", trackers=["diaper"])

    for platform, key in [
        ("button", "solids_log"),
        ("sensor", "solids_last"),
        ("sensor", "solids_count_today"),
    ]:
        assert eid(hass, entry, platform, key)
        assert eid(hass, other, platform, key) is None
    assert value(hass, entry, "sensor", "solids_count_today") == "0"
    assert value(hass, entry, "sensor", "solids_last") == "unknown"


async def test_meal_with_a_note(hass: HomeAssistant) -> None:
    """The action records a meal with what was eaten."""
    entry = await add_baby(hass)

    event_id = await act(hass, entry, "log_solids", notes="carrot puree")

    event = (await async_get_store(hass)).get_event(event_id)
    assert (event.tracker, event.notes) == ("solids", "carrot puree")
    assert attrs(hass, entry, "solids_last")["notes"] == "carrot puree"


async def test_button_pressed(hass: HomeAssistant) -> None:
    """The button records a meal now with no note."""
    entry = await add_baby(hass)

    await press(hass, entry, "solids_log")

    assert value(hass, entry, "sensor", "solids_last") == iso(NOW)
    assert attrs(hass, entry, "solids_last")["notes"] is None


async def test_back_dated_and_undone(hass: HomeAssistant) -> None:
    """The button follows "minutes ago", and undo removes the meal."""
    entry = await add_baby(hass)
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": eid(hass, entry, "number", "minutes_ago"), "value": 15},
        blocking=True,
    )

    await press(hass, entry, "solids_log")
    assert value(hass, entry, "sensor", "solids_last") == iso(
        NOW - timedelta(minutes=15)
    )

    await press(hass, entry, "undo")
    assert value(hass, entry, "sensor", "solids_count_today") == "0"
    with pytest.raises(HomeAssistantError):
        await press(hass, entry, "undo")


async def test_two_meals(hass: HomeAssistant) -> None:
    """Two meals today: the count is 2 and the last is the second."""
    entry = await add_baby(hass)
    second = NOW - timedelta(hours=1)
    await act(hass, entry, "log_solids", time=local(NOW - timedelta(hours=4)))
    await act(hass, entry, "log_solids", time=local(second))

    assert value(hass, entry, "sensor", "solids_count_today") == "2"
    assert value(hass, entry, "sensor", "solids_last") == iso(second)


async def test_note_added_later(hass: HomeAssistant, hass_ws_client) -> None:
    """A note added in the calendar shows in the last meal's attribute."""
    entry = await add_baby(hass)
    uid = await act(hass, entry, "log_solids")

    reply = await update(
        hass, hass_ws_client, entry, "feeding", uid, description="banana and oats"
    )

    assert reply["success"]
    assert attrs(hass, entry, "solids_last")["notes"] == "banana and oats"


@pytest.mark.parametrize(
    ("language", "title"), [("en", "🥣 Solids"), ("pt", "🥣 Sólidos")]
)
async def test_meal_in_the_calendar(
    hass: HomeAssistant, language: str, title: str
) -> None:
    """The calendar shows the meal with its note as the description."""
    hass.config.language = language
    entry = await add_baby(hass)
    await act(
        hass,
        entry,
        "log_solids",
        notes="carrot puree",
        time=local(NOW - timedelta(hours=1)),
    )

    [event] = await events(hass, entry, "feeding")

    assert event["summary"] == title
    assert event["description"] == "carrot puree"
