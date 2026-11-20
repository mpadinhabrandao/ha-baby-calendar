"""Access to the event store from the event loop."""

import asyncio
from collections.abc import Callable
from typing import Any

from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant, callback

from .const import DATA_STORE, DB_FILENAME
from .store import EventStore

_OPEN_LOCK = "baby_calendar_store_lock"


async def async_get_store(hass: HomeAssistant) -> EventStore:
    """Return the shared event store, opening it on first use.

    The file stays open until Home Assistant stops. Both the config flow and
    the config entries use this, so the store exists before any baby does.
    """
    if (store := hass.data.get(DATA_STORE)) is not None:
        return store
    lock: asyncio.Lock = hass.data.setdefault(_OPEN_LOCK, asyncio.Lock())
    async with lock:
        if (store := hass.data.get(DATA_STORE)) is not None:
            return store
        store = EventStore(hass.config.path(DB_FILENAME))
        await hass.async_add_executor_job(store.open)
        hass.data[DATA_STORE] = store

        @callback
        def _close(_: Event) -> None:
            hass.data.pop(DATA_STORE, None)
            hass.async_add_executor_job(store.close)

        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _close)
    return store


async def async_run[T](
    hass: HomeAssistant, func: Callable[..., T], *args: Any, **kwargs: Any
) -> T:
    """Run a store method in the executor."""
    return await hass.async_add_executor_job(lambda: func(*args, **kwargs))
