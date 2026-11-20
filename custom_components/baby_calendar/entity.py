"""Base entity: one baby, one device, state from the baby's coordinator."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BabyCoordinator
from .models import BabyConfigEntry


class BabyEntity(CoordinatorEntity[BabyCoordinator]):
    """An entity of one baby.

    The key is the translation key and the suffix of the unique id, which is
    "<baby_id>_<key>".
    """

    _attr_has_entity_name = True

    def __init__(self, entry: BabyConfigEntry, key: str) -> None:
        """Attach the entity to the baby's device."""
        data = entry.runtime_data
        super().__init__(data.coordinator)
        self.entry = entry
        self.key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{data.baby_id}_{key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, data.baby_id)})


class MedicationEntity(BabyEntity):
    """An entity of one of the baby's medications.

    Its unique id is "<baby_id>_med_<medication id>_<key>"; its name is a
    translation with the medication's name as the {medication} placeholder.
    """

    def __init__(self, entry: BabyConfigEntry, medication: dict, key: str) -> None:
        """Attach the entity to the baby's device and to one medication."""
        super().__init__(entry, f"med_{medication['id']}_{key}")
        self.medication = medication
        self._attr_translation_key = f"medication_{key}"
        self._attr_translation_placeholders = {"medication": medication["name"]}
        # Lets a dashboard select a medication's entities in any language.
        self._attr_extra_state_attributes = {"medication": medication["name"]}

    @property
    def medication_state(self) -> dict:
        """Return this medication's computed state."""
        return self.coordinator.data["medication"][self.medication["id"]]
