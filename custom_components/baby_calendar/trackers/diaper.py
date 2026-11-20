"""Diaper tracker: wet, dirty or both, with an optional stool type."""

from typing import Any, Final

import probatio
from homeassistant.exceptions import ServiceValidationError

from ..calendar_strings import words
from ..const import DOMAIN, TRACKER_DIAPER
from ..store import Event, EventStore
from .base import Columns, Day, Tracker, TrackerState

CONTENT: Final = "content"
STOOL: Final = "stool"

WET: Final = "wet"
DIRTY: Final = "dirty"
BOTH: Final = "both"
CONTENTS: Final = (WET, DIRTY, BOTH)
WET_KINDS: Final = (WET, BOTH)
DIRTY_KINDS: Final = (DIRTY, BOTH)

STOOLS: Final = ("normal", "soft", "hard", "diarrhea")

EMOJI: Final = {WET: "💧", DIRTY: "💩", BOTH: "💧💩"}

# How long after a dirty diaper the stool type can still be added by button,
# and how long the stool prompt stays on.
STOOL_WINDOW: Final = 600


class DiaperTracker(Tracker):
    """Diaper changes."""

    key = TRACKER_DIAPER
    log_service = "log_diaper"
    log_fields = {
        probatio.Required(CONTENT): probatio.In(CONTENTS),
        probatio.Optional(STOOL): probatio.In(STOOLS),
    }
    update_fields = {
        probatio.Optional(CONTENT): probatio.In(CONTENTS),
        probatio.Optional(STOOL): probatio.Maybe(probatio.In(STOOLS)),
    }

    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Store the content as the kind and the stool type in the data."""
        stool = fields.get(STOOL)
        return Columns(kind=fields[CONTENT], data={STOOL: stool} if stool else {})

    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return the content and the stool type."""
        return {CONTENT: event.kind, STOOL: event.data.get(STOOL)}

    def check(self, fields: dict[str, Any]) -> None:
        """Refuse a stool type on a wet diaper."""
        if fields.get(CONTENT) == WET and fields.get(STOOL):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="stool_on_wet"
            )

    def normalise(self, fields: dict[str, Any], supplied: set[str]) -> dict[str, Any]:
        """Correcting the content to wet drops the stool type."""
        if CONTENT in supplied and STOOL not in supplied and fields[CONTENT] == WET:
            return {**fields, STOOL: None}
        return fields

    def summary(self, event: Event, language: str, now: int) -> str:
        """Return "💩 Dirty diaper (soft)" and the like."""
        text = words(language)
        title = f"{EMOJI[event.kind]} {text[f'diaper_{event.kind}']}"
        if stool := event.data.get(STOOL):
            title += f" ({text[f'stool_{stool}']})"
        return title

    def compute(
        self, store: EventStore, baby_id: str, day: Day, now: int
    ) -> TrackerState:
        """Last changes, today's counts and the stool prompt."""
        last = store.last_event(baby_id, self.key)
        last_wet = store.last_event(baby_id, self.key, WET_KINDS)
        last_dirty = store.last_event(baby_id, self.key, DIRTY_KINDS)
        recorded = store.latest_recorded(baby_id, self.key)

        prompt_until = None
        if (
            recorded is not None
            and recorded.kind in DIRTY_KINDS
            and not recorded.data.get(STOOL)
            and recorded.created_ts + STOOL_WINDOW > now
        ):
            prompt_until = recorded.created_ts + STOOL_WINDOW

        def count(kinds: tuple[str, ...] | None) -> int:
            return store.count_events(baby_id, self.key, day.start, day.end, kinds)

        return TrackerState(
            values={
                "diaper_last": last,
                "diaper_last_wet": last_wet,
                "diaper_last_dirty": last_dirty,
                "diaper_changes_today": count(None),
                "diaper_wet_today": count(WET_KINDS),
                "diaper_dirty_today": count(DIRTY_KINDS),
                "stool_prompt": prompt_until is not None,
                "latest_recorded": recorded,
            },
            refresh_at=prompt_until,
        )


DIAPER = DiaperTracker()
