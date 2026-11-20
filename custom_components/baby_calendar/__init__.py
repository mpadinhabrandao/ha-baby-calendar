"""Baby Calendar: log a baby's day in Home Assistant."""

import probatio
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ConfigEntryError, ServiceValidationError
from homeassistant.helpers import (
    config_validation as cv,
)
from homeassistant.helpers import (
    device_registry as dr,
)
from homeassistant.helpers import (
    entity_registry as er,
)
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BABY_ID,
    CONF_NAME,
    CONF_TRACKERS,
    DOMAIN,
    SERVICE_PURGE_HISTORY,
)
from .coordinator import BabyCoordinator
from .data import async_get_store, async_run
from .models import BabyConfigEntry, BabyData
from .services import async_register_services
from .store import EventStore
from .trackers import TIMED_TRACKERS, trackers_of_key

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

PURGE_HISTORY_SCHEMA = probatio.Schema(
    {probatio.Required(CONF_NAME): probatio.All(cv.string, probatio.Length(min=1))}
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the services that do not belong to one baby."""

    async def purge_history(call: ServiceCall) -> ServiceResponse:
        name = call.data[CONF_NAME].strip()
        wanted = name.casefold()
        if any(
            entry.data.get(CONF_NAME, "").casefold() == wanted
            for entry in hass.config_entries.async_entries(DOMAIN)
        ):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="purge_configured_baby",
                translation_placeholders={CONF_NAME: name},
            )
        store = await async_get_store(hass)
        result = await async_run(hass, store.purge_removed, name)
        if result.babies == 0:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="purge_no_history",
                translation_placeholders={CONF_NAME: name},
            )
        return {"babies": result.babies, "events": result.events}

    hass.services.async_register(
        DOMAIN,
        SERVICE_PURGE_HISTORY,
        purge_history,
        schema=PURGE_HISTORY_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: BabyConfigEntry) -> bool:
    """Set up one baby."""
    baby_id: str = entry.data[CONF_BABY_ID]
    name: str = entry.data[CONF_NAME]
    store = await async_get_store(hass)

    baby = await async_run(hass, store.get_baby, baby_id)
    if baby is None:
        raise ConfigEntryError(
            translation_domain=DOMAIN,
            translation_key="history_missing",
            translation_placeholders={CONF_NAME: name},
        )
    if baby.removed_ts is not None:
        await async_run(hass, store.reattach, baby_id)
    if baby.name != name:
        await async_run(hass, store.rename_baby, baby_id, name)

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, baby_id)},
        name=name,
        entry_type=dr.DeviceEntryType.SERVICE,
    )
    if device.name != name:
        device_registry.async_update_device(device.id, name=name)

    trackers = frozenset(entry.options.get(CONF_TRACKERS, []))
    _remove_disabled_tracker_entities(hass, entry, baby_id, trackers)
    await async_run(hass, _stop_disabled_timers, store, baby_id, trackers)

    coordinator = BabyCoordinator(hass, entry, store, baby_id, trackers)
    entry.runtime_data = BabyData(
        baby_id=baby_id, name=name, trackers=trackers, coordinator=coordinator
    )
    await coordinator.async_config_entry_first_refresh()
    entry.async_on_unload(coordinator.async_start())
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BabyConfigEntry) -> bool:
    """Unload one baby. Its events stay in the store."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Detach the baby from Home Assistant and keep its history."""
    store = await async_get_store(hass)
    baby_id = entry.data[CONF_BABY_ID]
    if await async_run(hass, store.get_baby, baby_id) is not None:
        await async_run(hass, store.mark_removed, baby_id)


async def _async_reload(hass: HomeAssistant, entry: BabyConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _remove_disabled_tracker_entities(
    hass: HomeAssistant, entry: ConfigEntry, baby_id: str, trackers: frozenset[str]
) -> None:
    """Drop registry entries of trackers that are no longer enabled."""
    registry = er.async_get(hass)
    prefix = f"{baby_id}_"
    for registry_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if not registry_entry.unique_id.startswith(prefix):
            continue
        needed = trackers_of_key(registry_entry.unique_id.removeprefix(prefix))
        if needed is not None and not needed & trackers:
            registry.async_remove(registry_entry.entity_id)


def _stop_disabled_timers(
    store: EventStore, baby_id: str, trackers: frozenset[str]
) -> None:
    """Finish the running timer of every timed tracker that is not enabled.

    Runs on every setup, so disabling a tracker in the options finishes its
    timer when the entry reloads. Runs in the executor.
    """
    now = int(dt_util.utcnow().timestamp())
    for key in TIMED_TRACKERS.keys() - trackers:
        if (running := store.running_event(baby_id, key)) is not None:
            store.update_event(
                running.id, {"end_ts": max(now, running.start_ts + 1)}, now=now
            )
