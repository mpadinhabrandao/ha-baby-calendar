"""Tests for the dashboard path: minutes ago, undo and the repeated press guard."""

from datetime import datetime, timedelta

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.baby_calendar.const import CONF_BABY_ID, DOMAIN
from custom_components.baby_calendar.data import async_get_store
from custom_components.baby_calendar.services import async_log_from_dashboard

from .conftest import add_baby

NOW = datetime(2026, 11, 20, 3, 20, tzinfo=dt_util.UTC)


@pytest.fixture(autouse=True)
def frozen(freezer: FrozenDateTimeFactory) -> FrozenDateTimeFactory:
    """Freeze the clock at a known time."""
    freezer.move_to(NOW)
    return freezer


def entity_id(hass: HomeAssistant, entry: ConfigEntry, platform: str, key: str) -> str:
    """Return the entity id of one of a baby's entities."""
    return er.async_get(hass).async_get_entity_id(
        platform, DOMAIN, f"{entry.data[CONF_BABY_ID]}_{key}"
    )


async def set_minutes_ago(hass: HomeAssistant, entry: ConfigEntry, value: int) -> None:
    """Set the baby's "minutes ago" input as a dashboard would."""
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": entity_id(hass, entry, "number", "minutes_ago"), "value": value},
        blocking=True,
    )


async def press(hass: HomeAssistant, entry: ConfigEntry, key: str) -> None:
    """Press one of a baby's buttons."""
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": entity_id(hass, entry, "button", key)},
        blocking=True,
    )


async def test_minutes_ago_entity(hass: HomeAssistant) -> None:
    """The input starts at 0 and takes a value in minutes."""
    entry = await add_baby(hass)
    number = entity_id(hass, entry, "number", "minutes_ago")

    assert hass.states.get(number).state == "0"
    await set_minutes_ago(hass, entry, 20)
    assert hass.states.get(number).state == "20"
    assert entry.runtime_data.minutes_ago == 20


async def test_minutes_ago_back_dates_and_resets(hass: HomeAssistant) -> None:
    """An entry made with "minutes ago" at 20 is recorded 20 minutes earlier."""
    entry = await add_baby(hass)
    await set_minutes_ago(hass, entry, 20)
    times: list[datetime] = []

    async def log(when: datetime) -> None:
        times.append(when)

    await async_log_from_dashboard(hass, entry, "diaper_wet", log)
    await hass.async_block_till_done()

    assert times == [NOW - timedelta(minutes=20)]
    number = entity_id(hass, entry, "number", "minutes_ago")
    assert hass.states.get(number).state == "0"

    await async_log_from_dashboard(hass, entry, "diaper_dirty", log)
    assert times[-1] == NOW


async def test_minutes_ago_resets_when_logging_fails(hass: HomeAssistant) -> None:
    """The input returns to 0 even when the entry is refused."""
    entry = await add_baby(hass)
    await set_minutes_ago(hass, entry, 5)

    async def log(when: datetime) -> None:
        raise HomeAssistantError("refused")

    with pytest.raises(HomeAssistantError):
        await async_log_from_dashboard(hass, entry, "diaper_wet", log)

    assert entry.runtime_data.minutes_ago == 0


async def test_minutes_ago_is_not_restored(hass: HomeAssistant) -> None:
    """After a reload the input is 0 again."""
    entry = await add_baby(hass)
    await set_minutes_ago(hass, entry, 30)

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(entity_id(hass, entry, "number", "minutes_ago")).state == "0"


async def test_repeated_press_guard(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """A second press of the same button within 3 seconds is dropped."""
    entry = await add_baby(hass)
    calls: list[datetime] = []

    async def log(when: datetime) -> None:
        calls.append(when)

    await async_log_from_dashboard(hass, entry, "diaper_wet", log)
    frozen.tick(1)
    await async_log_from_dashboard(hass, entry, "diaper_wet", log)
    await async_log_from_dashboard(hass, entry, "diaper_dirty", log)
    frozen.tick(3)
    await async_log_from_dashboard(hass, entry, "diaper_wet", log)

    assert len(calls) == 3


async def test_failed_press_is_not_guarded(hass: HomeAssistant) -> None:
    """A press that failed can be repeated at once."""
    entry = await add_baby(hass)
    attempts = 0

    async def log(when: datetime) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise HomeAssistantError("refused")

    with pytest.raises(HomeAssistantError):
        await async_log_from_dashboard(hass, entry, "bottle_log", log)
    await async_log_from_dashboard(hass, entry, "bottle_log", log)

    assert attempts == 2


async def _add_event(hass: HomeAssistant, entry: ConfigEntry, **kwargs) -> str:
    store = await async_get_store(hass)
    event = store.add_event(
        baby_id=entry.data[CONF_BABY_ID],
        tracker="diaper",
        kind="wet",
        now=int(dt_util.utcnow().timestamp()),
        **kwargs,
    )
    return event.id


async def test_undo_deletes_the_last_recorded(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """Undo deletes the latest recorded entry, then the one before it."""
    entry = await add_baby(hass)
    store = await async_get_store(hass)
    now = int(NOW.timestamp())
    first = await _add_event(hass, entry, start_ts=now)
    frozen.tick(60)
    backdated = await _add_event(hass, entry, start_ts=now - 7200)

    await press(hass, entry, "undo")
    assert store.get_event(backdated) is None
    assert store.get_event(first) is not None

    await press(hass, entry, "undo")
    assert store.get_event(first) is None

    with pytest.raises(HomeAssistantError) as err:
        await press(hass, entry, "undo")
    assert err.value.translation_key == "nothing_to_undo"


async def test_undo_refuses_an_old_entry(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """Nothing recorded in the last 15 minutes means nothing is deleted."""
    entry = await add_baby(hass)
    store = await async_get_store(hass)
    event_id = await _add_event(hass, entry, start_ts=int(NOW.timestamp()))
    frozen.tick(timedelta(minutes=15))

    with pytest.raises(HomeAssistantError):
        await press(hass, entry, "undo")

    assert store.get_event(event_id) is not None


async def test_undo_updates_the_state(hass: HomeAssistant) -> None:
    """The state no longer includes an undone entry."""
    entry = await add_baby(hass)
    await _add_event(hass, entry, start_ts=int(NOW.timestamp()))
    await entry.runtime_data.coordinator.async_refresh()
    assert entry.runtime_data.coordinator.data["diaper"]["diaper_changes_today"] == 1

    await press(hass, entry, "undo")

    assert entry.runtime_data.coordinator.data["diaper"]["diaper_changes_today"] == 0
