"""Medication tracker: doses of medications the user defines per baby.

Unlike the other trackers it is not ticked in the tracker list: a baby uses
it when it has at least one active medication. A dose stores the
medication's id as its kind and the name it had, so doses of a removed
medication stay readable.
"""

from typing import Any, Final

from ..const import (
    CONF_MEDICATIONS,
    MED_ACTIVE,
    MED_ID,
    MED_NAME,
    MED_SCHEDULE,
    TRACKER_MEDICATION,
)
from ..store import Event, EventStore
from .base import Columns, Day, Tracker, TrackerState

MEDICATION: Final = "medication"


def medications(options: dict[str, Any], *, active: bool | None = None) -> list[dict]:
    """Return a baby's medications from its options, optionally by state."""
    meds = list(options.get(CONF_MEDICATIONS, []))
    if active is None:
        return meds
    return [med for med in meds if bool(med.get(MED_ACTIVE, True)) is active]


def has_schedule(medication: dict[str, Any]) -> bool:
    """Return whether a medication has a schedule, so it can be due."""
    return medication.get(MED_SCHEDULE, {}).get("type", "none") != "none"


def current_name(options: dict[str, Any], event: Event) -> str:
    """Return the medication's current name, or the name stored with the dose."""
    for med in medications(options):
        if med[MED_ID] == event.kind:
            return med[MED_NAME]
    return event.data.get(MED_NAME, "")


class MedicationTracker(Tracker):
    """Doses. The log service is registered on its own; see services.py."""

    key = TRACKER_MEDICATION
    log_service = "log_medication"
    log_fields: dict[Any, Any] = {}
    update_fields: dict[Any, Any] = {}

    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Store the medication id as the kind and its name in the data."""
        return Columns(kind=fields[MED_ID], data={MED_NAME: fields[MED_NAME]})

    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return the medication name stored with the dose."""
        return {MEDICATION: event.data.get(MED_NAME)}

    def summary(self, event: Event, language: str, now: int) -> str:
        """Return "💊 Vitamin D"."""
        return f"💊 {event.data.get(MED_NAME, '')}"

    def compute(
        self, store: EventStore, baby_id: str, day: Day, now: int
    ) -> TrackerState:
        """Per-medication state is computed by the coordinator."""
        return TrackerState(values={})


MEDICATION_TRACKER = MedicationTracker()
