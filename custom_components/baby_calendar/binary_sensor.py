"""Binary sensors: the stool type prompt."""

from typing import override

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import TRACKER_DIAPER
from .entity import BabyEntity
from .models import BabyConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the baby's binary sensors, for the enabled trackers only."""
    if TRACKER_DIAPER in entry.runtime_data.trackers:
        async_add_entities([StoolPromptBinarySensor(entry)])


class StoolPromptBinarySensor(BabyEntity, BinarySensorEntity):
    """On while the dirty diaper just logged still has no stool type.

    A dashboard shows the stool type buttons only while this is on.
    """

    _attr_icon = "mdi:emoticon-poop-outline"

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the prompt of one baby."""
        super().__init__(entry, "stool_prompt")

    @property
    @override
    def is_on(self) -> bool:
        return bool(self.coordinator.data[TRACKER_DIAPER]["stool_prompt"])
