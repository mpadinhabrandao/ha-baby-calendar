"""Shared logic of timed trackers, whose events have a start and an end."""

from typing import Any, Final

from ..store import Event, EventStore
from .base import Columns, Day, Tracker, TrackerState

# A running timer's daily duration is recomputed this often.
RUNNING_REFRESH: Final = 60


def duration_in_day(events: list[Event], day: Day, now: int) -> int:
    """Return the seconds of these events that fall within the day.

    An event crossing midnight counts only for its part within the day, and a
    running event counts up to now.
    """
    total = 0
    for event in events:
        end = now if event.end_ts is None else event.end_ts
        start = max(event.start_ts, day.start)
        stop = min(end, day.end, now)
        if stop > start:
            total += stop - start
    return total


class TimedTracker(Tracker):
    """A tracker with a timer: start, stop and log by duration.

    Its events are in progress while ``end_ts`` is None. Subclasses name the
    services and add their own fields and values.
    """

    timed = True
    start_service: str
    stop_service: str
    # Fields of the start and log services besides duration, notes and time,
    # such as the side. ``log_fields`` holds the same for the shared code.
    log_fields: dict[Any, Any] = {}

    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Store no columns besides the times, unless a subclass adds some."""
        return Columns()

    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return no fields besides the times, unless a subclass adds some."""
        return {}

    def compute(
        self, store: EventStore, baby_id: str, day: Day, now: int
    ) -> TrackerState:
        """Last event, running event, today's count and duration."""
        running = store.running_event(baby_id, self.key)
        overlapping = store.list_events(
            baby_id, day.start, day.end, self.key, timed=(self.key,)
        )
        values = {
            f"{self.key}_last": store.last_event(baby_id, self.key),
            f"{self.key}_running": running,
            f"{self.key}_duration_today": round(
                duration_in_day(overlapping, day, now) / 60, 1
            ),
            **self.extra_values(store, baby_id, day, now, running),
        }
        return TrackerState(
            values=values, refresh_at=now + RUNNING_REFRESH if running else None
        )

    def extra_values(
        self,
        store: EventStore,
        baby_id: str,
        day: Day,
        now: int,
        running: Event | None,
    ) -> dict[str, Any]:
        """Values specific to the tracker."""
        return {}

    def dashboard_fields(self, side: str | None) -> dict[str, Any]:
        """Return the fields the dashboard inputs give a new entry."""
        return {}

    def other_side(self, event: Event) -> str | None:
        """Return the side the selector moves to after this entry, if any."""
        return None
