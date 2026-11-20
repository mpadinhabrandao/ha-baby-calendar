"""Solids tracker: a meal and, in its notes, what was eaten."""

from typing import Any

from ..calendar_strings import words
from ..const import TRACKER_SOLIDS
from ..store import Event, EventStore
from .base import Columns, Day, Tracker, TrackerState


class SolidsTracker(Tracker):
    """Solid food meals. What was eaten is the note, added in the calendar."""

    key = TRACKER_SOLIDS
    log_service = "log_solids"
    log_fields: dict[Any, Any] = {}
    update_fields: dict[Any, Any] = {}

    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Use no column beyond the time and the notes."""
        return Columns()

    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return no field: the notes are common to every tracker."""
        return {}

    def summary(self, event: Event, language: str, now: int) -> str:
        """Return "🥣 Solids"."""
        return f"🥣 {words(language)['solids']}"

    def compute(
        self, store: EventStore, baby_id: str, day: Day, now: int
    ) -> TrackerState:
        """Last meal and today's meals."""
        return TrackerState(
            values={
                "solids_last": store.last_event(baby_id, self.key),
                "solids_count_today": store.count_events(
                    baby_id, self.key, day.start, day.end
                ),
            }
        )


SOLIDS = SolidsTracker()
