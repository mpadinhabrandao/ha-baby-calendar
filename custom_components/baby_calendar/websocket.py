"""WebSocket support for the cards: a live description of every baby."""

from typing import Any

import probatio
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)

from .const import CONF_BABY_ID, DOMAIN, MED_DOSE, MED_ID, MED_NAME
from .models import BabyConfigEntry
from .trackers import MEDICATION_KEY_PREFIX
from .trackers.medication import medications

# The entities of one medication, by the suffix of their unique id.
MEDICATION_ENTITY_KEYS = ("take", "last_dose", "doses_today", "next_dose", "due")

# Sent when a baby is set up or unloaded, so subscribers get the babies again.
SIGNAL_BABIES_CHANGED = f"{DOMAIN}_babies_changed"


@callback
def async_register_websocket(hass: HomeAssistant) -> None:
    """Register the WebSocket commands."""
    websocket_api.async_register_command(hass, ws_subscribe_babies)


@callback
def async_babies_changed(hass: HomeAssistant) -> None:
    """Tell subscribers that a baby was set up or unloaded."""
    async_dispatcher_send(hass, SIGNAL_BABIES_CHANGED)


@callback
def babies(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Describe every loaded baby for the cards."""
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    result = []
    entries: list[BabyConfigEntry] = hass.config_entries.async_loaded_entries(DOMAIN)
    for entry in entries:
        data = entry.runtime_data
        baby_id = entry.data[CONF_BABY_ID]
        device = device_registry.async_get_device_by_identifier(
            (DOMAIN, baby_id), entry.entry_id
        )
        entities: dict[str, str] = {}
        med_entities: dict[str, dict[str, str]] = {}
        prefix = f"{baby_id}_"
        for item in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
            if item.disabled or not item.unique_id.startswith(prefix):
                continue
            key = item.unique_id.removeprefix(prefix)
            if key.startswith(MEDICATION_KEY_PREFIX):
                rest = key.removeprefix(MEDICATION_KEY_PREFIX)
                for med_key in MEDICATION_ENTITY_KEYS:
                    if rest.endswith(f"_{med_key}"):
                        med_id = rest.removesuffix(f"_{med_key}")
                        med_entities.setdefault(med_id, {})[med_key] = item.entity_id
                        break
            else:
                entities[key] = item.entity_id
        result.append(
            {
                "entry_id": entry.entry_id,
                "device_id": device.id if device else None,
                "name": data.name,
                "trackers": sorted(data.trackers),
                "medications": [
                    {
                        "id": med[MED_ID],
                        "name": med[MED_NAME],
                        "dose": med.get(MED_DOSE),
                        "entities": med_entities.get(med[MED_ID], {}),
                    }
                    for med in medications(entry.options, active=True)
                ],
                "entities": entities,
            }
        )
    return sorted(result, key=lambda baby: baby["name"].casefold())


@callback
@websocket_api.websocket_command(
    {probatio.Required("type"): f"{DOMAIN}/subscribe_babies"}
)
def ws_subscribe_babies(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Send the babies now and again whenever one changes.

    Any user may subscribe: logging is for every member of the household.
    """

    @callback
    def send() -> None:
        connection.send_message(
            websocket_api.event_message(msg["id"], {"babies": babies(hass)})
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, SIGNAL_BABIES_CHANGED, send
    )
    connection.send_message(websocket_api.result_message(msg["id"]))
    send()
