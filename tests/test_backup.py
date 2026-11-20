"""Tests for the backup hooks."""

import asyncio
from pathlib import Path

from homeassistant.core import HomeAssistant

from custom_components.baby_calendar import backup
from custom_components.baby_calendar.const import DATA_STORE
from custom_components.baby_calendar.store import EventStore


async def test_hooks_without_a_store(hass: HomeAssistant) -> None:
    """With no baby configured there is no store and the hooks do nothing."""
    await backup.async_pre_backup(hass)
    await backup.async_post_backup(hass)


async def test_store_is_closed_between_the_hooks(
    hass: HomeAssistant, tmp_path: Path
) -> None:
    """The file is closed during a backup and a pending write lands afterwards."""
    store = EventStore(tmp_path / "baby_calendar.db")
    store.open()
    hass.data[DATA_STORE] = store
    baby = store.create_baby("Alice")

    await backup.async_pre_backup(hass)
    assert store._conn is None

    write = hass.async_add_executor_job(
        lambda: store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=1)
    )
    done, _ = await asyncio.wait([write], timeout=0.2)
    assert not done

    await backup.async_post_backup(hass)
    event = await write
    assert store.get_event(event.id) == event
    assert store.create_baby("Bruno").name == "Bruno"
    store.close()
