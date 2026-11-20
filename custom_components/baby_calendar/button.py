"""Button entities: undo, and each tracker's one-tap logging buttons."""

from datetime import datetime
from typing import override

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import TRACKER_DIAPER
from .entity import BabyEntity
from .models import BabyConfigEntry
from .services import async_log, async_log_from_dashboard, async_set_stool, async_undo
from .trackers.diaper import BOTH, CONTENT, DIAPER, DIRTY, STOOLS, WET


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the baby's buttons, for the enabled trackers only."""
    trackers = entry.runtime_data.trackers
    entities: list[ButtonEntity] = [UndoButton(entry)]
    if TRACKER_DIAPER in trackers:
        entities += [DiaperButton(entry, content) for content in (WET, DIRTY, BOTH)]
        entities += [StoolButton(entry, stool) for stool in STOOLS]
    async_add_entities(entities)


class UndoButton(BabyEntity, ButtonEntity):
    """Delete the entry recorded last, if it was recorded in the last 15 minutes."""

    _attr_icon = "mdi:undo"

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the undo button of one baby."""
        super().__init__(entry, "undo")

    @override
    async def async_press(self) -> None:
        await async_undo(self.hass, self.entry)


class DiaperButton(BabyEntity, ButtonEntity):
    """Log a diaper change with one content and no stool type."""

    _attr_icon = "mdi:human-baby-changing-table"

    def __init__(self, entry: BabyConfigEntry, content: str) -> None:
        """Create the button for one content."""
        super().__init__(entry, f"diaper_{content}")
        self._content = content

    @override
    async def async_press(self) -> None:
        async def log(when: datetime) -> None:
            await async_log(
                self.hass, self.entry, DIAPER, {CONTENT: self._content}, when=when
            )

        await async_log_from_dashboard(self.hass, self.entry, self.key, log)


class StoolButton(BabyEntity, ButtonEntity):
    """Set the stool type of the dirty diaper just logged."""

    _attr_icon = "mdi:emoticon-poop"

    def __init__(self, entry: BabyConfigEntry, stool: str) -> None:
        """Create the button for one stool type."""
        super().__init__(entry, f"stool_{stool}")
        self._stool = stool

    @override
    async def async_press(self) -> None:
        await async_set_stool(self.hass, self.entry, self._stool)
