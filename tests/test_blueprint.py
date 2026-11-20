"""Tests for the medication reminder blueprint, run as a real automation."""

import asyncio
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

from custom_components.baby_calendar.const import CONF_BABY_ID, DOMAIN

from .conftest import add_baby
from .test_medication import add_medication, log_dose, med_by_name

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


async def setup_reminder(hass: HomeAssistant, repeat: int) -> tuple[str, list]:
    """Add Alice with Vitamin D at 09:00 and an automation from the blueprint."""
    target = Path(hass.config.path("blueprints/automation/baby_calendar"))
    target.mkdir(parents=True)
    shutil.copy(BLUEPRINT, target / BLUEPRINT.name)

    entry = await add_baby(hass, "Alice")
    await add_medication(
        hass,
        entry,
        name="Vitamin D",
        dose="1 drop",
        schedule_type="times",
        times="9:00",
    )
    await log_dose(
        hass, entry, "Vitamin D", time=(NOW - timedelta(hours=23)).isoformat()
    )
    med_id = med_by_name(entry, "Vitamin D")["id"]
    due = er.async_get(hass).async_get_entity_id(
        "binary_sensor", DOMAIN, f"{entry.data[CONF_BABY_ID]}_med_{med_id}_due"
    )
    calls = async_mock_service(hass, "notify", "phone")
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": {
                "use_blueprint": {
                    "path": f"baby_calendar/{BLUEPRINT.name}",
                    "input": {
                        "due_sensor": due,
                        "repeat_minutes": repeat,
                        "reminder": [
                            {
                                "action": "notify.phone",
                                "data": {
                                    "message": "{{ baby }}: {{ medication }} "
                                    "({{ dose }})"
                                },
                            }
                        ],
                    },
                }
            }
        },
    )
    await hass.async_block_till_done()
    return entry, calls


async def settle(hass: HomeAssistant, until=lambda: False) -> None:
    """Let the loop and the store's executor jobs run.

    The automation keeps running while it waits to repeat, so waiting for
    every task to finish would never return, and the clock is frozen, so
    sleeping would never return either. Run until ``until`` holds, then a
    little more so the automation reaches its next wait.
    """
    for _ in range(200):
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


async def test_reminder_on_a_phone(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """When the dose becomes due the phone gets the names and the dose."""
    _, calls = await setup_reminder(hass, repeat=0)
    assert calls == []

    await move_to(hass, freezer, NOW + timedelta(hours=1), lambda: calls)

    assert [call.data["message"] for call in calls] == ["Alice: Vitamin D (1 drop)"]


async def test_repeat_until_recorded(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """With a repeat, it notifies again until the dose is recorded."""
    entry, calls = await setup_reminder(hass, repeat=15)

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
