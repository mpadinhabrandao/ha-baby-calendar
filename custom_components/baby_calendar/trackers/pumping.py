"""Pumping tracker: an amount of expressed milk in ml and, optionally, the side."""

from typing import Any, Final

import probatio

from ..calendar_strings import format_amount, words
from ..const import TRACKER_PUMPING
from ..store import Event, EventStore
from .base import Columns, Day, Tracker, TrackerState
from .bottle import MAX_AMOUNT

AMOUNT: Final = "amount"
SIDE: Final = "side"
SIDES: Final = ("left", "right", "both")

_AMOUNT = probatio.All(
    probatio.Coerce(float),
    probatio.Range(min=0, max=MAX_AMOUNT, min_included=False),
)


class PumpingTracker(Tracker):
    """Pumping sessions."""

    key = TRACKER_PUMPING
    log_service = "log_pumping"
    log_fields = {
        probatio.Required(AMOUNT): _AMOUNT,
        probatio.Optional(SIDE): probatio.In(SIDES),
    }
    update_fields = {
        probatio.Optional(AMOUNT): _AMOUNT,
        probatio.Optional(SIDE): probatio.Maybe(probatio.In(SIDES)),
    }

    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Store the side as the kind and the amount in its column."""
        return Columns(kind=fields.get(SIDE), amount=fields[AMOUNT])

    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return the amount and the side."""
        return {AMOUNT: event.amount, SIDE: event.kind}

    def summary(self, event: Event, language: str, now: int) -> str:
        """Return "🧴 Pumping 80 ml both sides" and the like."""
        text = words(language)
        title = f"🧴 {text['pumping']} {format_amount(event.amount or 0, language)} ml"
        if event.kind:
            title += f" {text[f'pumping_{event.kind}']}"
        return title

    def compute(
        self, store: EventStore, baby_id: str, day: Day, now: int
    ) -> TrackerState:
        """Last session and today's totals."""
        return TrackerState(
            values={
                "pumping_last": store.last_event(baby_id, self.key),
                "pumping_count_today": store.count_events(
                    baby_id, self.key, day.start, day.end
                ),
                "pumping_ml_today": store.sum_amount(
                    baby_id, self.key, day.start, day.end
                ),
            }
        )


PUMPING = PumpingTracker()
