"""Tests for the medication reminder blueprint, run as a real automation."""

import asyncio
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

from .conftest import add_baby
from .test_medication import add_medication, device_id, entity_id, log_dose

BLUEPRINT = (
    Path(__file__).parent.parent
    / "blueprints/automation/baby_calendar/medication_reminder.yaml"
)
TZ = dt_util.get_time_zone("Europe/Lisbon")
NOW = datetime(2026, 11, 20, 8, 0, tzinfo=TZ)


@pytest.fixture(autouse=True)
async def lisbon(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    """Run every test in Lisbon at 08:00."""
    await hass.config.async_set_time_zone("Europe/Lisbon")
    freezer.move_to(NOW)


async def add_scheduled(
    hass: HomeAssistant, entry: ConfigEntry, name: str, time: str
) -> None:
    """Add a medication at a fixed time, given yesterday."""
    await add_medication(
        hass, entry, name=name, dose="1 drop", schedule_type="times", times=time
    )
    await log_dose(hass, entry, name, time=(NOW - timedelta(hours=20)).isoformat())


async def setup_reminder(hass: HomeAssistant, **inputs: Any) -> list:
    """Set up one automation from the blueprint; return the notify calls."""
    target = Path(hass.config.path("blueprints/automation/baby_calendar"))
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy(BLUEPRINT, target / BLUEPRINT.name)
    calls = async_mock_service(hass, "notify", "phone")
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": {
                "use_blueprint": {
                    "path": f"baby_calendar/{BLUEPRINT.name}",
                    "input": {
                        "reminder": [
                            {
                                "action": "notify.phone",
                                "data": {
                                    "message": "{{ baby }}: {{ medication }} "
                                    "({{ dose }})",
                                    "data": {
                                        "actions": [
                                            {
                                                "action": "BABY_CALENDAR_DOSE:"
                                                "{{ button }}",
                                                "title": "Given",
                                            }
                                        ]
                                    },
                                },
                            }
                        ],
                        **inputs,
                    },
                }
            }
        },
    )
    await hass.async_block_till_done()
    return calls


async def settle(hass: HomeAssistant, until=lambda: False) -> None:
    """Let the loop and the store's executor jobs run.

    The automation keeps running while it waits to repeat, so waiting for
    every task to finish would never return, and the clock is frozen, so
    sleeping would never return either. Run until ``until`` holds, then a
    little more so the automation reaches its next wait.
    """
    for _ in range(2000):
        if until():
            break
        await hass.async_add_executor_job(lambda: None)
        await asyncio.sleep(0)
    for _ in range(20):
        await asyncio.sleep(0)


async def move_to(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, when: datetime, until=None
) -> None:
    """Move the clock, fire the time listeners and timers, and settle."""
    freezer.move_to(when)
    async_fire_time_changed(hass, when)
    await settle(hass, until or (lambda: False))


def messages(calls: list) -> list[str]:
    """Return the notification messages sent."""
    return [call.data["message"] for call in calls]


async def test_reminder_on_a_phone(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """When the dose becomes due the phone gets the names, dose and button."""
    entry = await add_baby(hass, "Alice")
    await add_scheduled(hass, entry, "Vitamin D", "9:00")
    calls = await setup_reminder(hass, repeat_minutes=0)

    await move_to(hass, freezer, NOW + timedelta(hours=1), lambda: calls)

    assert messages(calls) == ["Alice: Vitamin D (1 drop)"]
    button = entity_id(hass, entry, "Vitamin D", "button", "take")
    assert calls[0].data["data"]["actions"][0]["action"] == (
        f"BABY_CALENDAR_DOSE:{button}"
    )


async def test_one_automation_for_two_medications_and_one_added_later(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """The same automation reminds for every medication, old and new."""
    entry = await add_baby(hass, "Alice")
    await add_scheduled(hass, entry, "Vitamin D", "9:00")
    await add_scheduled(hass, entry, "Iron", "9:30")
    calls = await setup_reminder(hass, repeat_minutes=0)
    await add_scheduled(hass, entry, "Probiotic", "10:00")

    await move_to(hass, freezer, NOW + timedelta(hours=1), lambda: len(calls) == 1)
    await move_to(
        hass, freezer, NOW + timedelta(hours=1, minutes=30), lambda: len(calls) == 2
    )
    await move_to(hass, freezer, NOW + timedelta(hours=2), lambda: len(calls) == 3)

    assert messages(calls) == [
        "Alice: Vitamin D (1 drop)",
        "Alice: Iron (1 drop)",
        "Alice: Probiotic (1 drop)",
    ]


async def test_repeat_until_recorded(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """With a repeat, it notifies again until the dose is recorded."""
    entry = await add_baby(hass, "Alice")
    await add_scheduled(hass, entry, "Vitamin D", "9:00")
    calls = await setup_reminder(hass, repeat_minutes=15)

    await move_to(hass, freezer, NOW + timedelta(hours=1), lambda: len(calls) == 1)
    await move_to(
        hass,
        freezer,
        NOW + timedelta(hours=1, minutes=15),
        lambda: len(calls) == 2,
    )
    assert len(calls) == 2

    await log_dose(hass, entry, "Vitamin D")
    await move_to(hass, freezer, NOW + timedelta(hours=1, minutes=45))
    assert len(calls) == 2


async def test_only_the_babies_chosen(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """With a baby chosen, another baby's doses send nothing."""
    alice = await add_baby(hass, "Alice")
    bruno = await add_baby(hass, "Bruno")
    await add_scheduled(hass, alice, "Vitamin D", "9:00")
    await add_scheduled(hass, bruno, "Vitamin D", "9:00")
    calls = await setup_reminder(
        hass, repeat_minutes=0, babies=[device_id(hass, bruno)]
    )

    await move_to(hass, freezer, NOW + timedelta(hours=1), lambda: calls)

    assert messages(calls) == ["Bruno: Vitamin D (1 drop)"]


async def test_given_from_the_notification(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Choosing "Given" records the dose and stops the repeat."""
    entry = await add_baby(hass, "Alice")
    await add_scheduled(hass, entry, "Vitamin D", "9:00")
    calls = await setup_reminder(hass, repeat_minutes=15)
    await move_to(hass, freezer, NOW + timedelta(hours=1), lambda: calls)
    due = entity_id(hass, entry, "Vitamin D", "binary_sensor", "due")
    assert hass.states.get(due).state == "on"

    hass.bus.async_fire(
        "mobile_app_notification_action",
        {"action": calls[0].data["data"]["actions"][0]["action"]},
    )
    await settle(hass, lambda: hass.states.get(due).state == "off")

    assert hass.states.get(due).state == "off"
    await move_to(hass, freezer, NOW + timedelta(hours=1, minutes=30))
    assert len(calls) == 1
