"""Backup hooks: keep the event store closed while its file is copied."""

from homeassistant.core import HomeAssistant

from .const import DATA_STORE


async def async_pre_backup(hass: HomeAssistant) -> None:
    """Close the store. Calls made from now on wait for the backup to end."""
    if (store := hass.data.get(DATA_STORE)) is not None:
        await hass.async_add_executor_job(store.suspend)


async def async_post_backup(hass: HomeAssistant) -> None:
    """Reopen the store and let waiting calls proceed."""
    if (store := hass.data.get(DATA_STORE)) is not None:
        await hass.async_add_executor_job(store.resume)
