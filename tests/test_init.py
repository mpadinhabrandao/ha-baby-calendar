"""Tests for setting up, removing and purging babies."""

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.baby_calendar.const import (
    CONF_BABY_ID,
    CONF_NAME,
    CONF_TRACKERS,
    DOMAIN,
    SERVICE_PURGE_HISTORY,
)
from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby


async def test_one_device_per_baby(hass: HomeAssistant) -> None:
    """Each baby is a device named after it."""
    alice = await add_baby(hass, "Alice")
    bruno = await add_baby(hass, "Bruno")

    registry = dr.async_get(hass)
    for entry in (alice, bruno):
        device = registry.async_get_device_by_identifier(
            (DOMAIN, entry.data[CONF_BABY_ID]), entry.entry_id
        )
        assert device.name == entry.title
        assert device.config_entry_id == entry.entry_id


async def test_removal_keeps_history(hass: HomeAssistant) -> None:
    """Removing a baby removes its device and keeps its events."""
    entry = await add_baby(hass, "Alice")
    baby_id = entry.data[CONF_BABY_ID]
    store = await async_get_store(hass)
    event = store.add_event(baby_id=baby_id, tracker="diaper", start_ts=100)

    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    assert (
        dr.async_get(hass).async_get_device_by_identifier(
            (DOMAIN, baby_id), entry.entry_id
        )
        is None
    )
    assert store.get_baby(baby_id).removed_ts is not None
    assert store.get_event(event.id) == event


async def test_events_survive_a_restart(hass: HomeAssistant) -> None:
    """Unloading and setting up again finds the same events."""
    entry = await add_baby(hass, "Alice")
    store = await async_get_store(hass)
    event = store.add_event(
        baby_id=entry.data[CONF_BABY_ID], tracker="diaper", start_ts=100
    )

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert store.get_event(event.id) == event


async def test_missing_history_fails_setup(hass: HomeAssistant) -> None:
    """An entry whose baby no longer exists in the store does not load."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Ghost",
        unique_id="missing",
        data={CONF_BABY_ID: "missing", CONF_NAME: "Ghost"},
        options={CONF_TRACKERS: []},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_ERROR


async def test_disabled_tracker_entities_removed(hass: HomeAssistant) -> None:
    """Disabling a tracker drops its registry entries and keeps the others."""
    entry = await add_baby(hass, "Alice")
    baby_id = entry.data[CONF_BABY_ID]
    registry = er.async_get(hass)
    for key, platform in (
        ("bottle_last", "sensor"),
        ("diaper_last", "sensor"),
        ("undo", "button"),
    ):
        registry.async_get_or_create(
            platform, DOMAIN, f"{baby_id}_{key}", config_entry=entry
        )

    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_TRACKERS: ["diaper"]}
    )
    await hass.async_block_till_done()

    unique_ids = {
        registry_entry.unique_id
        for registry_entry in er.async_entries_for_config_entry(
            registry, entry.entry_id
        )
    }
    assert unique_ids == {f"{baby_id}_diaper_last", f"{baby_id}_undo"}
    assert entry.state is ConfigEntryState.LOADED


async def test_tracker_disabled_and_enabled_keeps_events(hass: HomeAssistant) -> None:
    """Events of a tracker are kept while it is disabled."""
    entry = await add_baby(hass, "Alice")
    store = await async_get_store(hass)
    event = store.add_event(
        baby_id=entry.data[CONF_BABY_ID], tracker="bottle", start_ts=100, amount=90
    )

    for trackers in (["diaper"], ["diaper", "bottle"]):
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, CONF_TRACKERS: trackers}
        )
        await hass.async_block_till_done()

    assert entry.runtime_data.trackers == {"diaper", "bottle"}
    assert store.get_event(event.id) == event


async def test_purge_deletes_removed_history(hass: HomeAssistant) -> None:
    """Purging a removed baby deletes its events and spares the other babies."""
    alice = await add_baby(hass, "Alice")
    bruno = await add_baby(hass, "Bruno")
    store = await async_get_store(hass)
    for entry in (alice, bruno):
        store.add_event(baby_id=entry.data[CONF_BABY_ID], tracker="diaper", start_ts=1)
    alice_id = alice.data[CONF_BABY_ID]
    await hass.config_entries.async_remove(alice.entry_id)
    await hass.async_block_till_done()

    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_PURGE_HISTORY,
        {CONF_NAME: "alice"},
        blocking=True,
        return_response=True,
    )

    assert response == {"babies": 1, "events": 1}
    assert store.get_baby(alice_id) is None
    assert len(store.list_events(bruno.data[CONF_BABY_ID], 0, 10)) == 1


async def test_purge_refuses_a_configured_baby(hass: HomeAssistant) -> None:
    """A configured baby's history is never purged."""
    entry = await add_baby(hass, "Alice")
    store = await async_get_store(hass)
    event = store.add_event(
        baby_id=entry.data[CONF_BABY_ID], tracker="diaper", start_ts=1
    )

    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, SERVICE_PURGE_HISTORY, {CONF_NAME: "ALICE"}, blocking=True
        )

    assert err.value.translation_key == "purge_configured_baby"
    assert store.get_event(event.id) == event


async def test_purge_with_nothing_to_delete(hass: HomeAssistant) -> None:
    """Purging a name with no removed history is an error."""
    await add_baby(hass, "Bruno")

    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, SERVICE_PURGE_HISTORY, {CONF_NAME: "Nobody"}, blocking=True
        )

    assert err.value.translation_key == "purge_no_history"
