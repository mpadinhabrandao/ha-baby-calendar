"""Button entities: undo, and each tracker's one-tap logging buttons."""

from typing import override

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import BabyEntity
from .models import BabyConfigEntry
from .services import async_undo


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the baby's buttons."""
    async_add_entities([UndoButton(entry)])


class UndoButton(BabyEntity, ButtonEntity):
    """Delete the entry recorded last, if it was recorded in the last 15 minutes."""

    _attr_icon = "mdi:undo"

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the undo button of one baby."""
        super().__init__(entry, "undo")

    @override
    async def async_press(self) -> None:
        await async_undo(self.hass, self.entry)
