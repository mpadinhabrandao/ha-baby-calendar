"""Button entities: undo, and each tracker's one-tap logging buttons."""

from datetime import datetime, timedelta
from typing import override

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, TRACKER_BOTTLE, TRACKER_DIAPER, TRACKER_SOLIDS
from .entity import BabyEntity, MedicationEntity
from .models import BabyConfigEntry
from .services import (
    async_log,
    async_log_dose,
    async_log_duration,
    async_log_from_dashboard,
    async_set_stool,
    async_undo,
)
from .trackers import TIMED_TRACKERS, bottle
from .trackers.diaper import BOTH, CONTENT, DIAPER, DIRTY, STOOLS, WET
from .trackers.measurement import MEASUREMENTS, VALUE, MeasurementTracker
from .trackers.medication import medications
from .trackers.solids import SOLIDS
from .trackers.timed import TimedTracker


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
    if TRACKER_BOTTLE in trackers:
        entities.append(BottleButton(entry))
    if TRACKER_SOLIDS in trackers:
        entities.append(SolidsButton(entry))
    entities += [
        DurationLogButton(entry, tracker)
        for key, tracker in TIMED_TRACKERS.items()
        if key in trackers
    ]
    entities += [
        MeasurementButton(entry, tracker)
        for tracker in MEASUREMENTS
        if tracker.key in trackers
    ]
    entities += [
        MedicationButton(entry, med) for med in medications(entry.options, active=True)
    ]
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


class BottleButton(BabyEntity, ButtonEntity):
    """Log a bottle with the amount and content currently set."""

    _attr_icon = "mdi:baby-bottle"

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the bottle button of one baby."""
        super().__init__(entry, "bottle_log")

    @override
    async def async_press(self) -> None:
        data = self.entry.runtime_data

        async def log(when: datetime) -> None:
            # Checked inside the dashboard path, so "minutes ago" still resets.
            if data.bottle_amount <= 0:
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="bottle_amount_zero"
                )
            fields = {bottle.AMOUNT: data.bottle_amount}
            if data.bottle_content:
                fields[bottle.CONTENT] = data.bottle_content
            await async_log(self.hass, self.entry, bottle.BOTTLE, fields, when=when)

        await async_log_from_dashboard(self.hass, self.entry, self.key, log)


class DurationLogButton(BabyEntity, ButtonEntity):
    """Log a finished entry of the duration set, ending now or "minutes ago"."""

    _attr_icon = "mdi:timer-check-outline"

    def __init__(self, entry: BabyConfigEntry, tracker: TimedTracker) -> None:
        """Create the log button of one timed tracker."""
        super().__init__(entry, f"{tracker.key}_log")
        self._tracker = tracker

    @override
    async def async_press(self) -> None:
        data = self.entry.runtime_data
        key = self._tracker.key

        async def log(when: datetime) -> None:
            await async_log_duration(
                self.hass,
                self.entry,
                self._tracker,
                self._tracker.dashboard_fields(data.breastfeeding_side),
                timedelta(minutes=data.durations.get(key, 0)),
                end=when,
            )
            data.durations[key] = 0
            data.coordinator.async_update_listeners()

        await async_log_from_dashboard(self.hass, self.entry, self.key, log)


class MedicationButton(MedicationEntity, ButtonEntity):
    """Record a dose of one medication."""

    _attr_icon = "mdi:pill"

    def __init__(self, entry: BabyConfigEntry, medication: dict) -> None:
        """Create the dose button of one medication."""
        super().__init__(entry, medication, "take")

    @override
    async def async_press(self) -> None:
        async def log(when: datetime) -> None:
            await async_log_dose(self.hass, self.entry, self.medication, when=when)

        await async_log_from_dashboard(self.hass, self.entry, self.key, log)


class MeasurementButton(BabyEntity, ButtonEntity):
    """Log a reading with the value of the measurement's input."""

    def __init__(self, entry: BabyConfigEntry, tracker: MeasurementTracker) -> None:
        """Create the log button of one measurement."""
        super().__init__(entry, f"{tracker.key}_log")
        self._tracker = tracker
        self._attr_icon = tracker.measurement.icon

    @override
    async def async_press(self) -> None:
        data = self.entry.runtime_data
        key = self._tracker.key

        async def log(when: datetime) -> None:
            value = data.measurements.get(key, 0)
            await async_log(
                self.hass, self.entry, self._tracker, {VALUE: value}, when=when
            )
            data.measurements[key] = 0
            data.coordinator.async_update_listeners()

        await async_log_from_dashboard(self.hass, self.entry, self.key, log)


class SolidsButton(BabyEntity, ButtonEntity):
    """Log a meal with no note; what was eaten is added in the calendar."""

    _attr_icon = "mdi:bowl-mix"

    def __init__(self, entry: BabyConfigEntry) -> None:
        """Create the solids button of one baby."""
        super().__init__(entry, "solids_log")

    @override
    async def async_press(self) -> None:
        async def log(when: datetime) -> None:
            await async_log(self.hass, self.entry, SOLIDS, {}, when=when)

        await async_log_from_dashboard(self.hass, self.entry, self.key, log)
