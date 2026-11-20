"""Per-baby state: every enabled tracker's values, recomputed on change."""

import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_point_in_utc_time,
    async_track_time_change,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    FEEDING,
    MED_ID,
    MED_SCHEDULE,
    MED_SINCE,
    TRACKER_BOTTLE,
    TRACKER_BREASTFEEDING,
    TRACKER_MEDICATION,
)
from .schedule import DAYS_BEFORE, evaluate
from .store import Event, EventStore
from .trackers import TRACKERS
from .trackers.base import Day

if TYPE_CHECKING:
    from .models import BabyConfigEntry

_LOGGER = logging.getLogger(__name__)

type BabyState = dict[str, Any]

# Key of the BabyState entry holding the day the daily values cover.
DAY = "day"

# Trackers whose entries count as a feed for the last feed sensor.
FEEDING_TRACKERS = frozenset({TRACKER_BOTTLE, TRACKER_BREASTFEEDING})


def local_day(now: datetime) -> Day:
    """Return the local day containing ``now``, which is 23 to 25 hours long."""
    # start_of_local_day takes a datetime's own date, not its local date.
    today = dt_util.as_local(now).date()
    start = dt_util.start_of_local_day(today)
    tomorrow = dt_util.start_of_local_day(today + timedelta(days=1))
    return Day(start=int(start.timestamp()), end=int(tomorrow.timestamp()))


class BabyCoordinator(DataUpdateCoordinator[BabyState]):
    """Holds a baby's state. There is no polling.

    The state is recomputed after every write that affects the baby, at
    local midnight, and when a tracker says a value expires.
    """

    config_entry: BabyConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: BabyConfigEntry,
        store: EventStore,
        baby_id: str,
        trackers: frozenset[str],
        medications: list[dict[str, Any]] | None = None,
    ) -> None:
        """Set up the state of one baby. Nothing is computed yet."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {baby_id}",
            update_interval=None,
        )
        self.store = store
        self.baby_id = baby_id
        self.trackers = trackers
        # The baby's active medications.
        self.medications = medications or []
        self._cancel_expiry: Callable[[], None] | None = None

    @callback
    def async_start(self) -> Callable[[], None]:
        """Recompute at every local midnight. Returns the function that stops it."""
        cancel_midnight = async_track_time_change(
            self.hass, self._async_midnight, hour=0, minute=0, second=0
        )

        @callback
        def stop() -> None:
            cancel_midnight()
            if self._cancel_expiry is not None:
                self._cancel_expiry()
                self._cancel_expiry = None

        return stop

    async def _async_midnight(self, _: datetime) -> None:
        await self.async_refresh()

    async def _async_update_data(self) -> BabyState:
        now = dt_util.utcnow()
        state, refresh_at = await self.hass.async_add_executor_job(
            self._compute, int(now.timestamp()), local_day(now)
        )
        self._schedule_expiry(refresh_at)
        return state

    def _compute(self, now: int, day: Day) -> tuple[BabyState, int | None]:
        # The day the daily values cover, for their last_reset.
        state: BabyState = {DAY: day}
        refresh_at: int | None = None
        for key in self.trackers:
            tracker_state = TRACKERS[key].compute(self.store, self.baby_id, day, now)
            state[key] = tracker_state.values
            if tracker_state.refresh_at is not None and (
                refresh_at is None or tracker_state.refresh_at < refresh_at
            ):
                refresh_at = tracker_state.refresh_at
        if FEEDING_TRACKERS & self.trackers:
            state[FEEDING] = {"last_feed": self._last_feed()}
        if self.medications:
            state[TRACKER_MEDICATION], med_change = self._medications(now, day)
            if med_change is not None and (
                refresh_at is None or med_change < refresh_at
            ):
                refresh_at = med_change
        return state, refresh_at

    def _medications(self, now: int, day: Day) -> tuple[BabyState, int | None]:
        """Return each active medication's doses and due state."""
        zone = dt_util.get_default_time_zone()
        now_dt = dt_util.utc_from_timestamp(now)
        window = now - (DAYS_BEFORE + 1) * 86400
        doses = self.store.list_events(
            self.baby_id, window, now + 1, TRACKER_MEDICATION
        )
        state: BabyState = {}
        refresh_at: int | None = None
        for med in self.medications:
            med_id = med[MED_ID]
            kinds = (med_id,)
            due = evaluate(
                med.get(MED_SCHEDULE, {}),
                [dose.start_ts for dose in doses if dose.kind == med_id],
                now_dt,
                zone,
                med.get(MED_SINCE),
            )
            state[med_id] = {
                "last_dose": self.store.last_event(
                    self.baby_id, TRACKER_MEDICATION, kinds
                ),
                "doses_today": self.store.count_events(
                    self.baby_id, TRACKER_MEDICATION, day.start, day.end, kinds
                ),
                "due": due.due,
                "next_dose": due.next_dose,
            }
            if due.next_change is not None:
                change = int(due.next_change.timestamp())
                if refresh_at is None or change < refresh_at:
                    refresh_at = change
        return state, refresh_at

    def _last_feed(self) -> Event | None:
        """Return the latest bottle or breastfeeding entry, by its start."""
        candidates = [
            event
            for key in FEEDING_TRACKERS & self.trackers
            if (event := self.store.last_event(self.baby_id, key)) is not None
        ]
        return max(candidates, key=lambda event: event.start_ts, default=None)

    @callback
    def _schedule_expiry(self, refresh_at: int | None) -> None:
        if self._cancel_expiry is not None:
            self._cancel_expiry()
            self._cancel_expiry = None
        if refresh_at is None:
            return

        async def _expired(_: datetime) -> None:
            self._cancel_expiry = None
            await self.async_refresh()

        self._cancel_expiry = async_track_point_in_utc_time(
            self.hass, _expired, dt_util.utc_from_timestamp(refresh_at)
        )
