"""Binary sensors: the stool type prompt and medication doses due."""

from typing import Any, override

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import TRACKER_DIAPER
from .entity import BabyEntity, MedicationEntity
from .models import BabyConfigEntry
from .trackers.medication import has_schedule, medications


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the baby's binary sensors, for the enabled trackers only."""
    entities: list[BinarySensorEntity] = []
    if TRACKER_DIAPER in entry.runtime_data.trackers:
        entities.append(StoolPromptBinarySensor(entry))
    entities += [
        MedicationDueBinarySensor(entry, med)
        for med in medications(entry.options, active=True)
        if has_schedule(med)
    ]
    async_add_entities(entities)


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


class MedicationDueBinarySensor(MedicationEntity, BinarySensorEntity):
    """On while a dose of the medication is due, by the schedule entered.

    The integration sends no notification: automations, such as the
    reminder blueprint, act on this sensor.
    """

    _attr_icon = "mdi:pill-multiple"

    def __init__(self, entry: BabyConfigEntry, medication: dict) -> None:
        """Create the due sensor of one medication."""
        super().__init__(entry, medication, "due")

    @property
    @override
    def is_on(self) -> bool:
        return bool(self.medication_state["due"])

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "baby": self.entry.runtime_data.name,
            "medication": self.medication["name"],
            "dose": self.medication.get("dose"),
        }
