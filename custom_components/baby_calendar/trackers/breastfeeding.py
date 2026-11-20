"""Breastfeeding tracker: timed entries with an optional side."""

from typing import Any, Final

import probatio

from ..const import TRACKER_BREASTFEEDING
from ..store import Event, EventStore
from .base import Columns, Day
from .timed import TimedTracker

SIDE: Final = "side"
LEFT: Final = "left"
RIGHT: Final = "right"
SIDES: Final = (LEFT, RIGHT)
OTHER_SIDE: Final = {LEFT: RIGHT, RIGHT: LEFT}

# An entry starting within this many seconds of the previous entry's end
# belongs to the same feed.
FEED_GAP: Final = 30 * 60


def count_feeds(previous: Event | None, today: list[Event], now: int) -> int:
    """Count the feeds that started today.

    ``previous`` is the last entry that started before today, so a side
    change just after midnight does not count as a new feed.
    """
    feeds = 0
    last_end = None
    if previous is not None:
        last_end = now if previous.end_ts is None else previous.end_ts
    for event in today:
        if last_end is None or event.start_ts - last_end > FEED_GAP:
            feeds += 1
        end = now if event.end_ts is None else event.end_ts
        last_end = end if last_end is None else max(last_end, end)
    return feeds


class BreastfeedingTracker(TimedTracker):
    """Breastfeeding entries; a side change is a new entry."""

    key = TRACKER_BREASTFEEDING
    start_service = "start_breastfeeding"
    stop_service = "stop_breastfeeding"
    log_service = "log_breastfeeding"
    log_fields = {probatio.Optional(SIDE): probatio.In(SIDES)}
    update_fields = {probatio.Optional(SIDE): probatio.Maybe(probatio.In(SIDES))}

    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Store the side as the kind."""
        return Columns(kind=fields.get(SIDE))

    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return the side."""
        return {SIDE: event.kind}

    def extra_values(
        self,
        store: EventStore,
        baby_id: str,
        day: Day,
        now: int,
        running: Event | None,
    ) -> dict[str, Any]:
        """Count today's feeds, grouping entries close together into one."""
        today = store.list_events(baby_id, day.start, day.end, self.key)
        previous = store.last_before(baby_id, self.key, day.start)
        return {"breastfeeding_feeds_today": count_feeds(previous, today, now)}

    def dashboard_fields(self, side: str | None) -> dict[str, Any]:
        """Use the side selection, unless it is "not specified"."""
        return {SIDE: side} if side else {}

    def other_side(self, event: Event) -> str | None:
        """After a left entry the next is right, and the other way round."""
        return OTHER_SIDE.get(event.kind or "")


BREASTFEEDING = BreastfeedingTracker()
