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
from homeassistant.const import UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    FEEDING,
    TRACKER_BOTTLE,
    TRACKER_BREASTFEEDING,
    TRACKER_DIAPER,
    TRACKER_SLEEP,
)
from .coordinator import DAY, FEEDING_TRACKERS
from .entity import BabyEntity, MedicationEntity
from .models import BabyConfigEntry
from .services import (
    ATTR_END,
    ATTR_EVENT_ID,
    ATTR_TIME,
    ATTR_TRACKER,
    event_response,
)
from .store import Event
from .trackers.measurement import MEASUREMENTS
from .trackers.medication import has_schedule, medications

ATTR_ENDED_AT = "ended_at"
ATTR_KIND = "kind"


@dataclass(frozen=True, kw_only=True)
class BabySensorDescription(SensorEntityDescription):
    """A sensor reading one value of the baby's state.

    ``tracker`` is the state group holding the value. The sensor exists while
    any of ``requires`` is enabled, by default the tracker itself. ``daily``
    sensors reset at local midnight. ``at_end`` shows an event's end instead
    of its start.
    """

    tracker: str
    requires: frozenset[str] | None = None
    daily: bool = False
    at_end: bool = False


def _last(key: str, tracker: str, icon: str, **kwargs: Any) -> BabySensorDescription:
    return BabySensorDescription(
        key=key,
        translation_key=key,
        tracker=tracker,
        icon=icon,
        device_class=SensorDeviceClass.TIMESTAMP,
        **kwargs,
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
        device_class=SensorDeviceClass.DURATION if unit == UnitOfTime.MINUTES else None,
    )


SENSORS: tuple[BabySensorDescription, ...] = (
    _last("diaper_last", TRACKER_DIAPER, "mdi:human-baby-changing-table"),
    _last("diaper_last_wet", TRACKER_DIAPER, "mdi:water"),
    _last("diaper_last_dirty", TRACKER_DIAPER, "mdi:emoticon-poop"),
    _today("diaper_changes_today", TRACKER_DIAPER, "mdi:human-baby-changing-table"),
    _today("diaper_wet_today", TRACKER_DIAPER, "mdi:water"),
    _today("diaper_dirty_today", TRACKER_DIAPER, "mdi:emoticon-poop"),
    _last("bottle_last", TRACKER_BOTTLE, "mdi:baby-bottle"),
    _today("bottle_count_today", TRACKER_BOTTLE, "mdi:baby-bottle-outline"),
    _today(
        "bottle_ml_today",
        TRACKER_BOTTLE,
        "mdi:baby-bottle",
        UnitOfVolume.MILLILITERS,
    ),
    _last("breastfeeding_last", TRACKER_BREASTFEEDING, "mdi:mother-nurse"),
    _today("breastfeeding_feeds_today", TRACKER_BREASTFEEDING, "mdi:mother-nurse"),
    _today(
        "breastfeeding_duration_today",
        TRACKER_BREASTFEEDING,
        "mdi:timer-outline",
        UnitOfTime.MINUTES,
    ),
    _last("sleep_last", TRACKER_SLEEP, "mdi:sleep"),
    _last("awake_since", TRACKER_SLEEP, "mdi:weather-sunny", at_end=True),
    _today("sleep_count_today", TRACKER_SLEEP, "mdi:sleep"),
    _today(
        "sleep_duration_today", TRACKER_SLEEP, "mdi:timer-outline", UnitOfTime.MINUTES
    ),
    _last(
        "last_feed",
        FEEDING,
        "mdi:food-apple-outline",
        requires=FEEDING_TRACKERS,
    ),
    *(
        description
        for tracker in MEASUREMENTS
        for description in (
            BabySensorDescription(
                key=tracker.key,
                translation_key=tracker.key,
                tracker=tracker.key,
                icon=tracker.measurement.icon,
                device_class=tracker.measurement.device_class,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=tracker.measurement.unit,
                suggested_display_precision=tracker.measurement.precision,
            ),
            _last(f"{tracker.key}_last", tracker.key, "mdi:clock-outline"),
        )
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the sensors of the baby's enabled trackers."""
    trackers = entry.runtime_data.trackers
    entities: list[SensorEntity] = [
        BabySensor(entry, description)
        for description in SENSORS
        if (description.requires or {description.tracker}) & trackers
    ]
    for med in medications(entry.options, active=True):
        entities += [
            MedicationSensor(entry, med, "last_dose"),
            MedicationSensor(entry, med, "doses_today"),
        ]
        if has_schedule(med):
            entities.append(MedicationSensor(entry, med, "next_dose"))
    async_add_entities(entities)


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
            if self.entity_description.at_end:
                return dt_util.utc_from_timestamp(value.end_ts)
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
        if self.entity_description.tracker == FEEDING:
            return {ATTR_KIND: value.tracker, ATTR_EVENT_ID: value.id}
        if self.entity_description.at_end:
            return {ATTR_EVENT_ID: value.id}
        # The event's id, fields and notes; the time is the state itself.
        attributes = event_response(self.hass, value)
        del attributes[ATTR_TIME], attributes[ATTR_TRACKER]
        if ATTR_END in attributes:
            attributes[ATTR_ENDED_AT] = attributes.pop(ATTR_END)
        return attributes


class MedicationSensor(MedicationEntity, SensorEntity):
    """The last dose, today's doses or the next dose of one medication."""

    def __init__(self, entry: BabyConfigEntry, medication: dict, key: str) -> None:
        """Create one sensor of a medication."""
        super().__init__(entry, medication, key)
        self._value_key = key
        if key == "doses_today":
            self._attr_icon = "mdi:pill"
            self._attr_state_class = SensorStateClass.TOTAL
        else:
            self._attr_icon = "mdi:clock-outline"
            self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    @override
    def native_value(self) -> datetime | int | None:
        value = self.medication_state[self._value_key]
        if isinstance(value, Event):
            return dt_util.utc_from_timestamp(value.start_ts)
        return value

    @property
    @override
    def last_reset(self) -> datetime | None:
        if self._value_key != "doses_today":
            return None
        return dt_util.utc_from_timestamp(self.coordinator.data[DAY].start)

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self._value_key != "last_dose":
            return None
        dose = self.medication_state["last_dose"]
        return {
            ATTR_EVENT_ID: dose.id if dose else None,
            "dose": self.medication.get("dose"),
        }
