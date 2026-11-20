"""Tests for medications: configuration, doses, entities and the due state."""

from datetime import datetime, timedelta
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_capture_events,
    async_fire_time_changed,
)

from custom_components.baby_calendar.const import (
    CONF_BABY_ID,
    CONF_MEDICATIONS,
    DOMAIN,
)
from custom_components.baby_calendar.data import async_get_store
from custom_components.baby_calendar.trackers.medication import (
    MEDICATION_TRACKER,
    current_name,
)

from .conftest import add_baby

TZ = dt_util.get_time_zone("Europe/Lisbon")
# Lisbon is on UTC in November.
NOW = datetime(2026, 11, 20, 8, 0, tzinfo=TZ)


@pytest.fixture(autouse=True)
async def lisbon(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    """Run every test in Lisbon at 08:00."""
    await hass.config.async_set_time_zone("Europe/Lisbon")
    freezer.move_to(NOW)


# ---------------------------------------------------------------- helpers


async def options_step(
    hass: HomeAssistant, entry: ConfigEntry, *steps: str
) -> dict[str, Any]:
    """Open the options and follow menu steps."""
    result = await hass.config_entries.options.async_init(entry.entry_id)
    for step in steps:
        assert result["type"] is FlowResultType.MENU
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": step}
        )
    return result


async def add_medication(
    hass: HomeAssistant, entry: ConfigEntry, **fields: Any
) -> dict[str, Any]:
    """Fill the add medication form and return the flow result."""
    result = await options_step(hass, entry, "medications", "add_medication")
    assert result["step_id"] == "medication"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"schedule_type": "none", **fields}
    )
    await hass.async_block_till_done()
    return result


async def change_medication(
    hass: HomeAssistant, entry: ConfigEntry, current: str, action: str, **fields: Any
) -> dict[str, Any]:
    """Pick a medication by name and edit, toggle or remove it."""
    med_id = med_by_name(entry, current)["id"]
    result = await options_step(hass, entry, "medications", "pick_medication")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"id": med_id, "action": action}
    )
    if action == "edit":
        assert result["step_id"] == "medication"
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], fields
        )
    await hass.async_block_till_done()
    return result


def med_by_name(entry: ConfigEntry, name: str) -> dict[str, Any]:
    """Return a configured medication of a baby."""
    return next(m for m in entry.options[CONF_MEDICATIONS] if m["name"] == name)


def entity_id(
    hass: HomeAssistant, entry: ConfigEntry, name: str, platform: str, key: str
) -> str | None:
    """Return the entity id of one of a medication's entities."""
    med_id = med_by_name(entry, name)["id"]
    return er.async_get(hass).async_get_entity_id(
        platform, DOMAIN, f"{entry.data[CONF_BABY_ID]}_med_{med_id}_{key}"
    )


def device_id(hass: HomeAssistant, entry: ConfigEntry) -> str:
    """Return the device id of a baby."""
    return (
        dr.async_get(hass)
        .async_get_device_by_identifier(
            (DOMAIN, entry.data[CONF_BABY_ID]), entry.entry_id
        )
        .id
    )


async def log_dose(
    hass: HomeAssistant, entry: ConfigEntry, medication: str, **data: Any
) -> str:
    """Record a dose with the action and return the event id."""
    result = await hass.services.async_call(
        DOMAIN,
        "log_medication",
        {"device_id": device_id(hass, entry), "medication": medication, **data},
        blocking=True,
        return_response=True,
    )
    return result["event_id"]


async def list_doses(hass: HomeAssistant, entry: ConfigEntry) -> list[dict]:
    """List the baby's doses of the last week."""
    result = await hass.services.async_call(
        DOMAIN,
        "list_events",
        {
            "device_id": device_id(hass, entry),
            "start": (dt_util.now() - timedelta(days=7)).isoformat(),
            "end": (dt_util.now() + timedelta(minutes=1)).isoformat(),
            "tracker": "medication",
        },
        blocking=True,
        return_response=True,
    )
    return result["events"]


async def press(hass: HomeAssistant, entity: str) -> None:
    """Press a button."""
    await hass.services.async_call(
        "button", "press", {"entity_id": entity}, blocking=True
    )


async def baby_with_vitamin_d(hass: HomeAssistant, **fields: Any) -> ConfigEntry:
    """Add Alice with "Vitamin D", "1 drop"."""
    entry = await add_baby(hass, "Alice")
    result = await add_medication(
        hass, entry, name="Vitamin D", dose="1 drop", **fields
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    return entry


async def move_to(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, when: datetime
) -> None:
    """Move the clock and fire the time listeners."""
    freezer.move_to(when)
    async_fire_time_changed(hass, when)
    await hass.async_block_till_done()


# ---------------------------------------------------------- configuration


async def test_vitamin_d_added(hass: HomeAssistant) -> None:
    """Its entities exist right away; without a schedule there is no due."""
    entry = await baby_with_vitamin_d(hass)

    med = med_by_name(entry, "Vitamin D")
    assert med["dose"] == "1 drop"
    assert med["active"] is True
    assert med["schedule"] == {"type": "none"}
    assert hass.states.get(entity_id(hass, entry, "Vitamin D", "button", "take"))
    last = hass.states.get(entity_id(hass, entry, "Vitamin D", "sensor", "last_dose"))
    assert last.state == "unknown"
    assert last.attributes["dose"] == "1 drop"
    today = entity_id(hass, entry, "Vitamin D", "sensor", "doses_today")
    assert hass.states.get(today).state == "0"
    assert entity_id(hass, entry, "Vitamin D", "binary_sensor", "due") is None
    assert entity_id(hass, entry, "Vitamin D", "sensor", "next_dose") is None


async def test_entity_names_carry_the_medication(hass: HomeAssistant) -> None:
    """The fixed part is translated and the name is the user's."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")

    due = hass.states.get(entity_id(hass, entry, "Vitamin D", "binary_sensor", "due"))
    assert due.attributes["friendly_name"] == "Alice Vitamin D due"


async def test_duplicate_name(hass: HomeAssistant) -> None:
    """A second medication with the same name, in any case, is refused."""
    entry = await baby_with_vitamin_d(hass)

    result = await add_medication(hass, entry, name="vitamin d")

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"name": "medication_in_use"}
    assert len(entry.options[CONF_MEDICATIONS]) == 1


@pytest.mark.parametrize(
    ("fields", "errors"),
    [
        ({"schedule_type": "times"}, {"times": "times_required"}),
        ({"schedule_type": "times", "times": "25:00"}, {"times": "time_invalid"}),
        (
            {"schedule_type": "interval", "interval": {"hours": 0, "minutes": 0}},
            {"interval": "interval_invalid"},
        ),
        ({"schedule_type": "interval"}, {"interval": "interval_invalid"}),
        ({"name": "  "}, {"name": "name_required"}),
    ],
)
async def test_invalid_schedule(
    hass: HomeAssistant, fields: dict[str, Any], errors: dict[str, str]
) -> None:
    """No times, an invalid time, a zero interval or no name are refused."""
    entry = await add_baby(hass, "Alice")

    result = await add_medication(hass, entry, **{"name": "Vitamin D", **fields})

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == errors
    assert CONF_MEDICATIONS not in entry.options


async def test_fixed_times_stored_sorted(hass: HomeAssistant) -> None:
    """Times are stored sorted and the baby's other options are kept."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="21:00, 9:00")

    assert med_by_name(entry, "Vitamin D")["schedule"] == {
        "type": "times",
        "times": ["09:00", "21:00"],
    }
    assert entry.options["trackers"]


async def test_renamed(hass: HomeAssistant) -> None:
    """A renamed medication keeps its doses, listed under the new name."""
    entry = await baby_with_vitamin_d(hass)
    await log_dose(hass, entry, "Vitamin D")

    await change_medication(
        hass, entry, "Vitamin D", "edit", name="Vit D", schedule_type="none"
    )

    doses = await list_doses(hass, entry)
    assert [dose["medication"] for dose in doses] == ["Vit D"]
    last = entity_id(hass, entry, "Vit D", "sensor", "last_dose")
    assert hass.states.get(last).state == NOW.isoformat(timespec="seconds")


async def test_course_finished(hass: HomeAssistant) -> None:
    """Deactivating keeps the doses; reactivating brings the entities back."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    await log_dose(hass, entry, "Vitamin D")

    await change_medication(hass, entry, "Vitamin D", "toggle")

    assert med_by_name(entry, "Vitamin D")["active"] is False
    for platform, key in [
        ("button", "take"),
        ("sensor", "last_dose"),
        ("sensor", "doses_today"),
        ("sensor", "next_dose"),
        ("binary_sensor", "due"),
    ]:
        assert entity_id(hass, entry, "Vitamin D", platform, key) is None
    assert len(await list_doses(hass, entry)) == 1
    with pytest.raises(ServiceValidationError):
        await log_dose(hass, entry, "Vitamin D")

    await change_medication(hass, entry, "Vitamin D", "toggle")

    today = entity_id(hass, entry, "Vitamin D", "sensor", "doses_today")
    assert hass.states.get(today).state == "1"


async def test_medication_removed(hass: HomeAssistant) -> None:
    """Removing keeps the doses under the name; a new one starts empty."""
    entry = await baby_with_vitamin_d(hass)
    await add_medication(hass, entry, name="Iron")
    old_id = med_by_name(entry, "Vitamin D")["id"]
    await log_dose(hass, entry, "Vitamin D")
    await log_dose(hass, entry, "Iron")

    await change_medication(hass, entry, "Vitamin D", "remove")

    assert [m["name"] for m in entry.options[CONF_MEDICATIONS]] == ["Iron"]
    registry = er.async_get(hass)
    prefix = f"{entry.data[CONF_BABY_ID]}_med_{old_id}_"
    assert not [
        e
        for e in er.async_entries_for_config_entry(registry, entry.entry_id)
        if e.unique_id.startswith(prefix)
    ]
    names = sorted(dose["medication"] for dose in await list_doses(hass, entry))
    assert names == ["Iron", "Vitamin D"]
    iron = entity_id(hass, entry, "Iron", "sensor", "doses_today")
    assert hass.states.get(iron).state == "1"

    await add_medication(hass, entry, name="Vitamin D")

    today = entity_id(hass, entry, "Vitamin D", "sensor", "doses_today")
    assert hass.states.get(today).state == "0"
    assert len(await list_doses(hass, entry)) == 2


# ------------------------------------------------------------------ doses


async def test_dose_by_button(hass: HomeAssistant) -> None:
    """The button records a dose now; the sensors follow."""
    entry = await baby_with_vitamin_d(hass)

    await press(hass, entity_id(hass, entry, "Vitamin D", "button", "take"))

    doses = await list_doses(hass, entry)
    assert len(doses) == 1
    last = hass.states.get(entity_id(hass, entry, "Vitamin D", "sensor", "last_dose"))
    assert last.state == NOW.isoformat(timespec="seconds")
    assert last.attributes["event_id"] == doses[0]["event_id"]
    today = entity_id(hass, entry, "Vitamin D", "sensor", "doses_today")
    assert hass.states.get(today).state == "1"


async def test_dose_by_button_minutes_ago_and_undo(hass: HomeAssistant) -> None:
    """The button follows "minutes ago", and undo deletes the dose."""
    entry = await baby_with_vitamin_d(hass)
    baby_id = entry.data[CONF_BABY_ID]
    minutes = er.async_get(hass).async_get_entity_id(
        "number", DOMAIN, f"{baby_id}_minutes_ago"
    )
    undo = er.async_get(hass).async_get_entity_id("button", DOMAIN, f"{baby_id}_undo")
    await hass.services.async_call(
        "number", "set_value", {"entity_id": minutes, "value": 30}, blocking=True
    )

    await press(hass, entity_id(hass, entry, "Vitamin D", "button", "take"))

    last = entity_id(hass, entry, "Vitamin D", "sensor", "last_dose")
    expected = NOW - timedelta(minutes=30)
    assert hass.states.get(last).state == expected.isoformat(timespec="seconds")

    await press(hass, undo)

    assert await list_doses(hass, entry) == []
    assert hass.states.get(last).state == "unknown"


async def test_dose_given_earlier(hass: HomeAssistant) -> None:
    """The action records a dose an hour ago, with a note."""
    entry = await baby_with_vitamin_d(hass)

    await log_dose(
        hass,
        entry,
        "vitamin d",
        time=(NOW - timedelta(hours=1)).isoformat(),
        notes="with milk",
    )

    [dose] = await list_doses(hass, entry)
    assert dose["time"] == (NOW - timedelta(hours=1)).isoformat()
    assert dose["notes"] == "with milk"
    assert dose["medication"] == "Vitamin D"


async def test_unknown_medication(hass: HomeAssistant) -> None:
    """A name that matches no active medication fails and records nothing."""
    entry = await baby_with_vitamin_d(hass)

    with pytest.raises(ServiceValidationError) as err:
        await log_dose(hass, entry, "Iron")

    assert err.value.translation_key == "unknown_medication"
    assert await list_doses(hass, entry) == []


async def test_dose_deleted(hass: HomeAssistant) -> None:
    """A deleted dose leaves the count and the last dose."""
    entry = await baby_with_vitamin_d(hass)
    await log_dose(
        hass, entry, "Vitamin D", time=(NOW - timedelta(hours=2)).isoformat()
    )
    mistake = await log_dose(hass, entry, "Vitamin D")

    await hass.services.async_call(
        DOMAIN, "delete_event", {"event_id": mistake}, blocking=True
    )

    today = entity_id(hass, entry, "Vitamin D", "sensor", "doses_today")
    assert hass.states.get(today).state == "1"
    last = entity_id(hass, entry, "Vitamin D", "sensor", "last_dose")
    expected = NOW - timedelta(hours=2)
    assert hass.states.get(last).state == expected.isoformat(timespec="seconds")


async def test_two_doses_close_together(hass: HomeAssistant) -> None:
    """Both are recorded, with no warning of the integration's own."""
    entry = await baby_with_vitamin_d(hass)

    await log_dose(
        hass, entry, "Vitamin D", time=(NOW - timedelta(minutes=3)).isoformat()
    )
    await log_dose(hass, entry, "Vitamin D")

    today = entity_id(hass, entry, "Vitamin D", "sensor", "doses_today")
    assert hass.states.get(today).state == "2"


async def test_calendar_summary_names(hass: HomeAssistant) -> None:
    """A dose is shown with the current name, or the stored one once removed."""
    entry = await baby_with_vitamin_d(hass)
    event_id = await log_dose(hass, entry, "Vitamin D")
    store = await async_get_store(hass)
    event = store.get_event(event_id)

    assert MEDICATION_TRACKER.summary(event, "en", 0) == "💊 Vitamin D"
    await change_medication(
        hass, entry, "Vitamin D", "edit", name="Vit D", schedule_type="none"
    )
    assert current_name(entry.options, event) == "Vit D"
    await change_medication(hass, entry, "Vit D", "remove")
    assert current_name(entry.options, event) == "Vitamin D"


# -------------------------------------------------------------- due state


async def test_time_reached(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """At 09:00 the due sensor turns on, with the names for a reminder."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    due = entity_id(hass, entry, "Vitamin D", "binary_sensor", "due")
    next_dose = entity_id(hass, entry, "Vitamin D", "sensor", "next_dose")
    # Yesterday's dose was given, so nothing is due at 08:00.
    await log_dose(
        hass, entry, "Vitamin D", time=(NOW - timedelta(hours=23)).isoformat()
    )
    assert hass.states.get(due).state == "off"
    assert hass.states.get(next_dose).state == (NOW + timedelta(hours=1)).isoformat(
        timespec="seconds"
    )

    await move_to(hass, freezer, NOW + timedelta(hours=1))

    state = hass.states.get(due)
    assert state.state == "on"
    assert state.attributes["baby"] == "Alice"
    assert state.attributes["medication"] == "Vitamin D"
    assert state.attributes["dose"] == "1 drop"


async def test_dose_recorded_while_due_then_deleted(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A dose turns the sensor off; deleting it turns it back on."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    due = entity_id(hass, entry, "Vitamin D", "binary_sensor", "due")
    await move_to(hass, freezer, NOW + timedelta(hours=1, minutes=30))
    assert hass.states.get(due).state == "on"

    event_id = await log_dose(hass, entry, "Vitamin D")
    assert hass.states.get(due).state == "off"

    await hass.services.async_call(
        DOMAIN, "delete_event", {"event_id": event_id}, blocking=True
    )
    assert hass.states.get(due).state == "on"


async def test_overdue(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    """At 10:30 with 09:00 not given, the next dose shows 09:00."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")

    await move_to(hass, freezer, NOW + timedelta(hours=2, minutes=30))

    next_dose = entity_id(hass, entry, "Vitamin D", "sensor", "next_dose")
    assert hass.states.get(next_dose).state == (NOW + timedelta(hours=1)).isoformat(
        timespec="seconds"
    )


async def test_interval(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    """Six hours after a dose it is due; the next dose is that time."""
    entry = await baby_with_vitamin_d(
        hass, schedule_type="interval", interval={"hours": 6}
    )
    due = entity_id(hass, entry, "Vitamin D", "binary_sensor", "due")
    next_dose = entity_id(hass, entry, "Vitamin D", "sensor", "next_dose")
    assert hass.states.get(next_dose).state == "unknown"

    await log_dose(hass, entry, "Vitamin D")
    assert hass.states.get(next_dose).state == (NOW + timedelta(hours=6)).isoformat(
        timespec="seconds"
    )

    await move_to(hass, freezer, NOW + timedelta(hours=6))
    assert hass.states.get(due).state == "on"


async def test_down_at_dose_time(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Stopped at 08:50 and started at 09:10: due after start."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    await log_dose(
        hass, entry, "Vitamin D", time=(NOW - timedelta(hours=23)).isoformat()
    )
    freezer.move_to(NOW + timedelta(minutes=50))
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    freezer.move_to(NOW + timedelta(hours=1, minutes=10))
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    due = entity_id(hass, entry, "Vitamin D", "binary_sensor", "due")
    assert hass.states.get(due).state == "on"


async def test_restart_while_due(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A reload while due keeps the sensor on."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    await move_to(hass, freezer, NOW + timedelta(hours=1, minutes=5))

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    due = entity_id(hass, entry, "Vitamin D", "binary_sensor", "due")
    assert hass.states.get(due).state == "on"


async def test_schedule_removed_drops_due_entities(hass: HomeAssistant) -> None:
    """Editing a medication to no schedule removes due and next dose."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")

    await change_medication(
        hass, entry, "Vitamin D", "edit", name="Vitamin D", schedule_type="none"
    )

    assert entity_id(hass, entry, "Vitamin D", "binary_sensor", "due") is None
    assert entity_id(hass, entry, "Vitamin D", "sensor", "next_dose") is None
    assert entity_id(hass, entry, "Vitamin D", "button", "take")


async def test_added_after_its_time(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Added at 08:00 with 07:00: due tomorrow at 07:00, not now."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="07:00")
    due = entity_id(hass, entry, "Vitamin D", "binary_sensor", "due")
    next_dose = entity_id(hass, entry, "Vitamin D", "sensor", "next_dose")

    assert hass.states.get(due).state == "off"
    tomorrow = NOW + timedelta(hours=23)
    assert hass.states.get(next_dose).state == tomorrow.isoformat(timespec="seconds")

    await move_to(hass, freezer, tomorrow)
    assert hass.states.get(due).state == "on"


async def test_reactivated_after_its_time(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Times missed while deactivated are not due on reactivation."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    await change_medication(hass, entry, "Vitamin D", "toggle")
    freezer.move_to(NOW + timedelta(hours=2))

    await change_medication(hass, entry, "Vitamin D", "toggle")

    due = entity_id(hass, entry, "Vitamin D", "binary_sensor", "due")
    assert hass.states.get(due).state == "off"


async def test_interval_in_hours_and_minutes(hass: HomeAssistant) -> None:
    """6 minutes is stored as 0.1 hours and shown again as 0 h 6 min."""
    entry = await baby_with_vitamin_d(
        hass, schedule_type="interval", interval={"hours": 0, "minutes": 6}
    )

    assert med_by_name(entry, "Vitamin D")["schedule"] == {
        "type": "interval",
        "hours": 0.1,
    }
    med_id = med_by_name(entry, "Vitamin D")["id"]
    result = await options_step(hass, entry, "medications", "pick_medication")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"id": med_id, "action": "edit"}
    )
    shown = next(key for key in result["data_schema"].schema if str(key) == "interval")
    assert shown.description["suggested_value"] == {
        "hours": 0,
        "minutes": 6,
        "seconds": 0,
    }


# -------------------------------------------------------------- due event


async def test_due_event_when_a_dose_becomes_due(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """One event at 09:00 with the names and the two entity ids."""
    events = async_capture_events(hass, "baby_calendar_medication_due")
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    assert events == []

    await move_to(hass, freezer, NOW + timedelta(hours=1))
    await move_to(hass, freezer, NOW + timedelta(hours=1, minutes=1))

    assert len(events) == 1
    assert events[0].data == {
        "baby": "Alice",
        "device_id": device_id(hass, entry),
        "medication": "Vitamin D",
        "dose": "1 drop",
        "due_entity": entity_id(hass, entry, "Vitamin D", "binary_sensor", "due"),
        "button_entity": entity_id(hass, entry, "Vitamin D", "button", "take"),
    }


async def test_due_event_again_after_a_dose(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A dose ends it; the next interval fires a new event."""
    events = async_capture_events(hass, "baby_calendar_medication_due")
    entry = await baby_with_vitamin_d(
        hass, schedule_type="interval", interval={"hours": 1}
    )
    await log_dose(hass, entry, "Vitamin D")

    await move_to(hass, freezer, NOW + timedelta(hours=1))
    assert len(events) == 1
    await log_dose(hass, entry, "Vitamin D")
    await move_to(hass, freezer, NOW + timedelta(hours=2))

    assert len(events) == 2


async def test_due_event_after_a_reload(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A reload while due fires the event again."""
    events = async_capture_events(hass, "baby_calendar_medication_due")
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    await move_to(hass, freezer, NOW + timedelta(hours=1, minutes=5))

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert len(events) == 2
    assert events[1].data["due_entity"] == entity_id(
        hass, entry, "Vitamin D", "binary_sensor", "due"
    )


async def test_due_event_waits_for_the_start(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Set up while starting and due: the event comes once started."""
    entry = await baby_with_vitamin_d(hass, schedule_type="times", times="09:00")
    await move_to(hass, freezer, NOW + timedelta(hours=1, minutes=5))
    assert await hass.config_entries.async_unload(entry.entry_id)
    events = async_capture_events(hass, "baby_calendar_medication_due")

    hass.set_state(CoreState.starting)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert events == []

    hass.set_state(CoreState.running)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()
    assert [event.data["medication"] for event in events] == ["Vitamin D"]


async def test_no_due_event_without_a_schedule(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A medication with no schedule never fires the event."""
    events = async_capture_events(hass, "baby_calendar_medication_due")
    await baby_with_vitamin_d(hass)

    await move_to(hass, freezer, NOW + timedelta(days=2))

    assert events == []
