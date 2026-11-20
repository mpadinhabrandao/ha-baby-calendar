"""Switch entities: each timed tracker's timer."""

from datetime import datetime
from typing import Any, override

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .entity import BabyEntity
from .models import BabyConfigEntry
from .services import async_log_from_dashboard, async_start_timer, async_stop_timer
from .store import Event
from .trackers import TIMED_TRACKERS
from .trackers.timed import TimedTracker

ATTR_STARTED_AT = "started_at"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add a timer switch for each enabled timed tracker."""
    async_add_entities(
        TimerSwitch(entry, tracker)
        for key, tracker in TIMED_TRACKERS.items()
        if key in entry.runtime_data.trackers
    )


class TimerSwitch(BabyEntity, SwitchEntity):
    """On while the tracker's timer runs.

    Turning it on starts the timer and turning it off stops it, both through
    the dashboard path, so "minutes ago" moves the start or the end.
    """

    def __init__(self, entry: BabyConfigEntry, tracker: TimedTracker) -> None:
        """Create the timer switch of one tracker."""
        super().__init__(entry, f"{tracker.key}_timer")
        self._tracker = tracker
        self._attr_icon = "mdi:timer-play-outline"

    @property
    def _running(self) -> Event | None:
        return self.coordinator.data[self._tracker.key][f"{self._tracker.key}_running"]

    @property
    @override
    def is_on(self) -> bool:
        return self._running is not None

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any]:
        running = self._running
        return {
            ATTR_STARTED_AT: dt_util.as_local(
                dt_util.utc_from_timestamp(running.start_ts)
            ).isoformat()
            if running
            else None
        }

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        fields = self._tracker.dashboard_fields(
            self.entry.runtime_data.breastfeeding_side
        )

        async def start(when: datetime) -> None:
            await async_start_timer(
                self.hass, self.entry, self._tracker, fields, when=when
            )

        await async_log_from_dashboard(self.hass, self.entry, f"{self.key}_on", start)

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        async def stop(when: datetime) -> None:
            await async_stop_timer(self.hass, self.entry, self._tracker, when=when)

        await async_log_from_dashboard(self.hass, self.entry, f"{self.key}_off", stop)
