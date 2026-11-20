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
