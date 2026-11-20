"""Number entities: the "minutes ago" input."""

from typing import override

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import BabyEntity
from .models import BabyConfigEntry

MAX_MINUTES_AGO = 720


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the baby's number entities."""
    async_add_entities([MinutesAgoNumber(entry)])


class MinutesAgoNumber(BabyEntity, NumberEntity):
    """How long ago the next dashboard entry happened.

    Not restored: it is 0 after a restart, and the logging path sets it back
    to 0 after every entry.
    """

    _attr_icon = "mdi:clock-time-four-outline"
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = MAX_MINUTES_AGO
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the input for one baby."""
        super().__init__(entry, "minutes_ago")

    @property
    @override
    def native_value(self) -> float:
        return self.entry.runtime_data.minutes_ago

    @override
    async def async_set_native_value(self, value: float) -> None:
        self.entry.runtime_data.minutes_ago = int(value)
        self.async_write_ha_state()
