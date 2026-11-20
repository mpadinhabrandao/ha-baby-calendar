"""Tests for adding, restoring and editing a baby from the UI."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr

from custom_components.baby_calendar.const import (
    CONF_BABY_ID,
    CONF_BIRTH_DATE,
    CONF_NAME,
    CONF_TRACKERS,
    DOMAIN,
)
from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby


async def _details(hass: HomeAssistant, entry_id: str) -> dict:
    """Open the options and choose the baby's details."""
    result = await hass.config_entries.options.async_init(entry_id)
    assert result["type"] is FlowResultType.MENU
    return await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "details"}
    )


async def _start(hass: HomeAssistant, name: str) -> dict:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    return await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_NAME: name}
    )


async def test_baby_added_before_birth(hass: HomeAssistant) -> None:
    """A baby is created with a name only, both trackers and its own store row."""
    entry = await add_baby(hass, "  Alice ")

    assert entry.title == "Alice"
    assert entry.data[CONF_NAME] == "Alice"
    assert entry.options == {
        CONF_BIRTH_DATE: None,
        CONF_TRACKERS: [
            "diaper",
            "bottle",
            "breastfeeding",
            "sleep",
            "solids",
            "pumping",
            "weight",
            "length",
            "temperature",
        ],
    }
    assert entry.unique_id == entry.data[CONF_BABY_ID]
    assert entry.state is ConfigEntryState.LOADED

    store = await async_get_store(hass)
    baby = store.get_baby(entry.data[CONF_BABY_ID])
    assert (baby.name, baby.removed_ts) == ("Alice", None)


async def test_birth_date_saved(hass: HomeAssistant) -> None:
    """The birth date is kept in the options."""
    entry = await add_baby(hass, birth_date="2026-12-24")
    assert entry.options[CONF_BIRTH_DATE] == "2026-12-24"


async def test_name_missing(hass: HomeAssistant) -> None:
    """A blank name shows an error and creates nothing."""
    result = await _start(hass, "   ")

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_NAME: "name_required"}
    assert hass.config_entries.async_entries(DOMAIN) == []


async def test_duplicate_name_rejected(hass: HomeAssistant) -> None:
    """A name already in use, in any case, shows an error."""
    await add_baby(hass, "Alice")

    result = await _start(hass, "ALICE")

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_NAME: "name_in_use"}
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


async def test_one_tracker_ticked(hass: HomeAssistant) -> None:
    """Only the ticked tracker is enabled."""
    entry = await add_baby(hass, trackers=["diaper"])
    assert entry.options[CONF_TRACKERS] == ["diaper"]


async def test_no_tracker_ticked(hass: HomeAssistant) -> None:
    """A baby can be created with no tracker."""
    entry = await add_baby(hass, trackers=[])
    assert entry.options[CONF_TRACKERS] == []
    assert entry.state is ConfigEntryState.LOADED


async def test_trackers_kept_in_the_integration_order(hass: HomeAssistant) -> None:
    """The stored list does not depend on the order of the ticks."""
    entry = await add_baby(hass, trackers=["bottle", "diaper"])
    assert entry.options[CONF_TRACKERS] == ["diaper", "bottle"]


async def test_no_question_without_removed_history(hass: HomeAssistant) -> None:
    """With no removed baby of that name the flow goes straight to trackers."""
    result = await _start(hass, "Alice")
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "trackers"


async def test_restore_history(hass: HomeAssistant) -> None:
    """Adding a removed baby again with restore brings back the same history."""
    first = await add_baby(hass, "Alice")
    baby_id = first.data[CONF_BABY_ID]
    store = await async_get_store(hass)
    event = store.add_event(baby_id=baby_id, tracker="diaper", start_ts=100)
    await hass.config_entries.async_remove(first.entry_id)
    await hass.async_block_till_done()

    result = await _start(hass, "alice")
    assert result["type"] is FlowResultType.MENU
    assert result["step_id"] == "history"
    assert result["description_placeholders"] == {CONF_NAME: "alice"}

    second = await add_baby(hass, "alice", history="restore")

    assert second.data[CONF_BABY_ID] == baby_id
    assert store.get_baby(baby_id).removed_ts is None
    assert store.get_baby(baby_id).name == "alice"
    assert store.get_event(event.id) == event


async def test_start_empty(hass: HomeAssistant) -> None:
    """Starting empty creates a new baby and leaves the old history stored."""
    first = await add_baby(hass, "Alice")
    old_id = first.data[CONF_BABY_ID]
    store = await async_get_store(hass)
    event = store.add_event(baby_id=old_id, tracker="diaper", start_ts=100)
    await hass.config_entries.async_remove(first.entry_id)
    await hass.async_block_till_done()

    second = await add_baby(hass, "Alice", history="start_empty")

    assert second.data[CONF_BABY_ID] != old_id
    assert store.list_events(second.data[CONF_BABY_ID], 0, 10**10) == []
    assert store.get_baby(old_id).removed_ts is not None
    assert store.get_event(event.id) == event


async def test_options_edit_keeps_events(hass: HomeAssistant) -> None:
    """Renaming and setting the birth date keeps events and renames the device."""
    entry = await add_baby(hass, "Alice")
    baby_id = entry.data[CONF_BABY_ID]
    store = await async_get_store(hass)
    event = store.add_event(baby_id=baby_id, tracker="diaper", start_ts=100)

    result = await _details(hass, entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Alícia",
            CONF_BIRTH_DATE: "2026-12-24",
            CONF_TRACKERS: ["diaper"],
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.title == "Alícia"
    assert entry.data[CONF_NAME] == "Alícia"
    assert entry.options == {
        CONF_BIRTH_DATE: "2026-12-24",
        CONF_TRACKERS: ["diaper"],
    }
    assert entry.state is ConfigEntryState.LOADED
    assert store.get_baby(baby_id).name == "Alícia"
    assert store.get_event(event.id) == event
    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, baby_id), entry.entry_id
    )
    assert device.name == "Alícia"


async def test_options_rejects_a_name_in_use(hass: HomeAssistant) -> None:
    """The options flow cannot take another baby's name."""
    await add_baby(hass, "Alice")
    bruno = await add_baby(hass, "Bruno")

    result = await _details(hass, bruno.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_NAME: "alice", CONF_TRACKERS: []}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_NAME: "name_in_use"}
    assert bruno.data[CONF_NAME] == "Bruno"


async def test_options_keeps_own_name(hass: HomeAssistant) -> None:
    """Saving without renaming is not a duplicate of itself."""
    entry = await add_baby(hass, "Alice")

    result = await _details(hass, entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_NAME: "Alice", CONF_TRACKERS: ["bottle"]}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_TRACKERS] == ["bottle"]
