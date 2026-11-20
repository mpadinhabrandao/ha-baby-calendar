"""Sensors: each tracker's last entries and today's values."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, override

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import TRACKER_DIAPER
from .coordinator import DAY
from .entity import BabyEntity
from .models import BabyConfigEntry
from .services import ATTR_TIME, ATTR_TRACKER, event_response
from .store import Event


@dataclass(frozen=True, kw_only=True)
class BabySensorDescription(SensorEntityDescription):
    """A sensor of one tracker. ``daily`` sensors reset at local midnight."""

    tracker: str
    daily: bool = False


def _last(key: str, tracker: str, icon: str) -> BabySensorDescription:
    return BabySensorDescription(
        key=key,
        translation_key=key,
        tracker=tracker,
        icon=icon,
        device_class=SensorDeviceClass.TIMESTAMP,
    )


def _today(
    key: str, tracker: str, icon: str, unit: str | None = None
) -> BabySensorDescription:
    return BabySensorDescription(
        key=key,
        translation_key=key,
        tracker=tracker,
        icon=icon,
        daily=True,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=unit,
    )


SENSORS: tuple[BabySensorDescription, ...] = (
    _last("diaper_last", TRACKER_DIAPER, "mdi:human-baby-changing-table"),
    _last("diaper_last_wet", TRACKER_DIAPER, "mdi:water"),
    _last("diaper_last_dirty", TRACKER_DIAPER, "mdi:emoticon-poop"),
    _today("diaper_changes_today", TRACKER_DIAPER, "mdi:human-baby-changing-table"),
    _today("diaper_wet_today", TRACKER_DIAPER, "mdi:water"),
    _today("diaper_dirty_today", TRACKER_DIAPER, "mdi:emoticon-poop"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the sensors of the baby's enabled trackers."""
    trackers = entry.runtime_data.trackers
    async_add_entities(
        BabySensor(entry, description)
        for description in SENSORS
        if description.tracker in trackers
    )


class BabySensor(BabyEntity, SensorEntity):
    """A value from the baby's state."""

    entity_description: BabySensorDescription

    def __init__(
        self, entry: BabyConfigEntry, description: BabySensorDescription
    ) -> None:
        """Create one sensor of a baby."""
        super().__init__(entry, description.key)
        self.entity_description = description

    @property
    def _value(self) -> Any:
        description = self.entity_description
        return self.coordinator.data[description.tracker][description.key]

    @property
    @override
    def native_value(self) -> datetime | float | None:
        value = self._value
        if isinstance(value, Event):
            return dt_util.utc_from_timestamp(value.start_ts)
        return value

    @property
    @override
    def last_reset(self) -> datetime | None:
        if not self.entity_description.daily:
            return None
        return dt_util.utc_from_timestamp(self.coordinator.data[DAY].start)

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any] | None:
        value = self._value
        if not isinstance(value, Event):
            return None
        # The event's id, fields and notes; the time is the state itself.
        attributes = event_response(self.hass, value)
        del attributes[ATTR_TIME], attributes[ATTR_TRACKER]
        return attributes
