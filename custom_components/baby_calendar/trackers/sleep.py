"""Sleep tracker: timed entries with no fields of their own."""

from typing import Any

from ..const import TRACKER_SLEEP
from ..store import Event, EventStore
from .base import Day
from .timed import TimedTracker


class SleepTracker(TimedTracker):
    """Sleeps. The timer doubles as the baby's sleeping state."""

    key = TRACKER_SLEEP
    start_service = "start_sleep"
    stop_service = "stop_sleep"
    log_service = "log_sleep"
    update_fields: dict[Any, Any] = {}
    emoji = "😴"

    def extra_values(
        self,
        store: EventStore,
        baby_id: str,
        day: Day,
        now: int,
        running: Event | None,
    ) -> dict[str, Any]:
        """Sleeps started today, and when the baby last woke up."""
        return {
            "sleep_count_today": store.count_events(
                baby_id, self.key, day.start, day.end
            ),
            "awake_since": None if running else store.last_finished(baby_id, self.key),
        }


SLEEP = SleepTracker()
