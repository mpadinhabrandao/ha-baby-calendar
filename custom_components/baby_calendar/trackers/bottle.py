"""Bottle tracker: an amount in ml and, optionally, what was in it."""

from typing import Any, Final

import probatio

from ..const import TRACKER_BOTTLE
from ..store import Event, EventStore
from .base import Columns, Day, Tracker, TrackerState

AMOUNT: Final = "amount"
CONTENT: Final = "content"

FORMULA: Final = "formula"
BREAST_MILK: Final = "breast_milk"
CONTENTS: Final = (FORMULA, BREAST_MILK)

MAX_AMOUNT: Final = 500

_AMOUNT = probatio.All(
    probatio.Coerce(float),
    probatio.Range(min=0, max=MAX_AMOUNT, min_included=False),
)


class BottleTracker(Tracker):
    """Bottles."""

    key = TRACKER_BOTTLE
    log_service = "log_bottle"
    log_fields = {
        probatio.Required(AMOUNT): _AMOUNT,
        probatio.Optional(CONTENT): probatio.In(CONTENTS),
    }
    update_fields = {
        probatio.Optional(AMOUNT): _AMOUNT,
        probatio.Optional(CONTENT): probatio.Maybe(probatio.In(CONTENTS)),
    }

    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Store the content as the kind and the amount in its column."""
        return Columns(kind=fields.get(CONTENT), amount=fields[AMOUNT])

    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return the amount and the content."""
        return {AMOUNT: event.amount, CONTENT: event.kind}

    def compute(
        self, store: EventStore, baby_id: str, day: Day, now: int
    ) -> TrackerState:
        """Last bottle and today's totals."""
        return TrackerState(
            values={
                "bottle_last": store.last_event(baby_id, self.key),
                "bottle_count_today": store.count_events(
                    baby_id, self.key, day.start, day.end
                ),
                "bottle_ml_today": store.sum_amount(
                    baby_id, self.key, day.start, day.end
                ),
            }
        )


BOTTLE = BottleTracker()
