"""Select entities: the next bottle's content and the next breastfeeding side."""

from typing import Final, override

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import TRACKER_BOTTLE, TRACKER_BREASTFEEDING
from .entity import BabyEntity
from .models import BabyConfigEntry
from .trackers.bottle import CONTENTS
from .trackers.breastfeeding import SIDES

NOT_SPECIFIED: Final = "not_specified"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the baby's select entities, for the enabled trackers only."""
    trackers = entry.runtime_data.trackers
    entities: list[SelectEntity] = []
    if TRACKER_BOTTLE in trackers:
        entities.append(BottleContentSelect(entry))
    if TRACKER_BREASTFEEDING in trackers:
        entities.append(BreastfeedingSideSelect(entry))
    async_add_entities(entities)


class BottleContentSelect(BabyEntity, SelectEntity, RestoreEntity):
    """Content of the next bottle logged with the bottle button.

    Starts at "not specified"; kept after a press and restored after a restart.
    """

    _attr_icon = "mdi:baby-bottle"
    _attr_options = [NOT_SPECIFIED, *CONTENTS]

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the bottle content input of one baby."""
        super().__init__(entry, "bottle_content")

    @override
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) is not None and (
            last.state in CONTENTS
        ):
            self.entry.runtime_data.bottle_content = last.state

    @property
    @override
    def current_option(self) -> str:
        return self.entry.runtime_data.bottle_content or NOT_SPECIFIED

    @override
    async def async_select_option(self, option: str) -> None:
        self.entry.runtime_data.bottle_content = (
            None if option == NOT_SPECIFIED else option
        )
        self.async_write_ha_state()


class BreastfeedingSideSelect(BabyEntity, SelectEntity, RestoreEntity):
    """Side of the next breastfeeding entry.

    Moves to the other side when an entry with a side ends; restored after a
    restart.
    """

    _attr_icon = "mdi:mother-nurse"
    _attr_options = [NOT_SPECIFIED, *SIDES]

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the side selector of one baby."""
        super().__init__(entry, "breastfeeding_side")

    @override
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) is not None and (
            last.state in SIDES
        ):
            self.entry.runtime_data.breastfeeding_side = last.state

    @property
    @override
    def current_option(self) -> str:
        return self.entry.runtime_data.breastfeeding_side or NOT_SPECIFIED

    @override
    async def async_select_option(self, option: str) -> None:
        self.entry.runtime_data.breastfeeding_side = (
            None if option == NOT_SPECIFIED else option
        )
        self.async_write_ha_state()
