"""Number entities: the "minutes ago" input and the bottle amount."""

from typing import override

from homeassistant.components.number import NumberEntity, NumberMode, RestoreNumber
from homeassistant.const import UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import TRACKER_BOTTLE
from .entity import BabyEntity
from .models import BabyConfigEntry
from .trackers import TIMED_TRACKERS
from .trackers.bottle import MAX_AMOUNT

MAX_MINUTES_AGO = 720
MAX_DURATION = 1440


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the baby's number entities, for the enabled trackers only."""
    entities: list[NumberEntity] = [MinutesAgoNumber(entry)]
    if TRACKER_BOTTLE in entry.runtime_data.trackers:
        entities.append(BottleAmountNumber(entry))
    entities += [
        DurationNumber(entry, key)
        for key in TIMED_TRACKERS
        if key in entry.runtime_data.trackers
    ]
    async_add_entities(entities)


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


class BottleAmountNumber(BabyEntity, RestoreNumber):
    """Amount of the next bottle logged with the bottle button.

    Kept after a press and restored after a restart, because a baby's usual
    bottle rarely changes from one feed to the next.
    """

    _attr_icon = "mdi:baby-bottle-outline"
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = MAX_AMOUNT
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfVolume.MILLILITERS

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the bottle amount input of one baby."""
        super().__init__(entry, "bottle_amount")

    @override
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_number_data()) is not None and (
            last.native_value is not None
        ):
            self.entry.runtime_data.bottle_amount = last.native_value

    @property
    @override
    def native_value(self) -> float:
        return self.entry.runtime_data.bottle_amount

    @override
    async def async_set_native_value(self, value: float) -> None:
        self.entry.runtime_data.bottle_amount = value
        self.async_write_ha_state()


class DurationNumber(BabyEntity, NumberEntity):
    """Minutes of a finished entry to log with the tracker's log button.

    Not restored and set back to 0 after an entry, like "minutes ago",
    because every feed or nap has its own length.
    """

    _attr_icon = "mdi:timer-outline"
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = MAX_DURATION
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, entry: BabyConfigEntry, tracker: str) -> None:
        """Create the duration input of one timed tracker."""
        super().__init__(entry, f"{tracker}_duration")
        self._tracker = tracker

    @property
    @override
    def native_value(self) -> float:
        return self.entry.runtime_data.durations.get(self._tracker, 0)

    @override
    async def async_set_native_value(self, value: float) -> None:
        self.entry.runtime_data.durations[self._tracker] = int(value)
        self.async_write_ha_state()
