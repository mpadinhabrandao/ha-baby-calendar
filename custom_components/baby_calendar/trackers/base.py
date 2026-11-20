"""What every tracker provides to the shared services and state."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..store import Event, EventStore


@dataclass(frozen=True, slots=True)
class Columns:
    """The store columns a tracker fills from its fields."""

    kind: str | None = None
    amount: float | None = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Day:
    """Today's local day as UTC epoch seconds, ``[start, end)``."""

    start: int
    end: int


@dataclass(slots=True)
class TrackerState:
    """Values computed from the store for a tracker's entities.

    ``refresh_at`` is a UTC epoch second at which the values change on
    their own, for example when a prompt expires.
    """

    values: dict[str, Any]
    refresh_at: int | None = None


class Tracker(ABC):
    """One purpose-built tracker.

    A tracker turns the fields of its log service into store columns and
    back, checks the rules between its fields, and computes the values its
    entities show.
    """

    key: str
    # Timed trackers record events with a start and an end; see timed.py.
    timed: bool = False
    log_service: str
    # Validators for the log service's own fields, keyed by probatio markers.
    log_fields: dict[Any, Any]
    # Validators for the keys of ``fields`` in update_event. A field that may
    # be cleared accepts None.
    update_fields: dict[Any, Any]

    @abstractmethod
    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Turn validated fields into store columns."""

    @abstractmethod
    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return an event's tracker fields, every field present."""

    def check(self, fields: dict[str, Any]) -> None:
        """Raise ServiceValidationError when the fields break a rule."""
        return

    def normalise(self, fields: dict[str, Any], supplied: set[str]) -> dict[str, Any]:
        """Adjust merged fields after a correction.

        ``supplied`` names the fields the correction set explicitly.
        """
        return fields

    @abstractmethod
    def compute(
        self, store: EventStore, baby_id: str, day: Day, now: int
    ) -> TrackerState:
        """Compute the state of the tracker's entities. Runs in the executor."""
