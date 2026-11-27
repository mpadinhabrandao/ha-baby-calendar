"""The trackers the integration offers, and the entities each one owns."""

from collections.abc import Collection

from ..const import (
    TRACKER_BOTTLE,
    TRACKER_BREASTFEEDING,
    TRACKER_DIAPER,
    TRACKER_LENGTH,
    TRACKER_MEDICATION,
    TRACKER_PUMPING,
    TRACKER_SLEEP,
    TRACKER_SOLIDS,
    TRACKER_TEMPERATURE,
    TRACKER_WEIGHT,
)
from .base import Tracker
from .bottle import BOTTLE
from .breastfeeding import BREASTFEEDING
from .diaper import DIAPER
from .measurement import MEASUREMENTS
from .medication import MEDICATION_TRACKER
from .pumping import PUMPING
from .sleep import SLEEP
from .solids import SOLIDS
from .timed import TimedTracker

TRACKERS: dict[str, Tracker] = {
    tracker.key: tracker
    for tracker in (
        DIAPER,
        BOTTLE,
        BREASTFEEDING,
        SLEEP,
        SOLIDS,
        PUMPING,
        *MEASUREMENTS,
        MEDICATION_TRACKER,
    )
}

TIMED_TRACKERS: dict[str, TimedTracker] = {
    key: tracker
    for key, tracker in TRACKERS.items()
    if isinstance(tracker, TimedTracker)
}

# Entity keys owned by each tracker. An entity's unique id is
# "<baby_id>_<key>", so these keys tell which registry entries belong to a
# tracker when it is disabled.
TRACKER_ENTITY_KEYS: dict[str, frozenset[str]] = {
    TRACKER_DIAPER: frozenset(
        {
            "diaper_wet",
            "diaper_dirty",
            "diaper_both",
            "stool_normal",
            "stool_soft",
            "stool_hard",
            "stool_diarrhea",
            "stool_prompt",
            "diaper_last",
            "diaper_last_wet",
            "diaper_last_dirty",
            "diaper_changes_today",
            "diaper_wet_today",
            "diaper_dirty_today",
        }
    ),
    TRACKER_BOTTLE: frozenset(
        {
            "bottle_amount",
            "bottle_content",
            "bottle_log",
            "bottle_last",
            "bottle_count_today",
            "bottle_ml_today",
        }
    ),
    TRACKER_BREASTFEEDING: frozenset(
        {
            "breastfeeding_timer",
            "breastfeeding_side",
            "breastfeeding_duration",
            "breastfeeding_log",
            "breastfeeding_last",
            "breastfeeding_feeds_today",
            "breastfeeding_duration_today",
        }
    ),
    TRACKER_SLEEP: frozenset(
        {
            "sleep_timer",
            "sleep_duration",
            "sleep_log",
            "sleep_last",
            "awake_since",
            "sleep_count_today",
            "sleep_duration_today",
        }
    ),
    TRACKER_SOLIDS: frozenset({"solids_log", "solids_last", "solids_count_today"}),
    TRACKER_PUMPING: frozenset(
        {
            "pumping_amount",
            "pumping_side",
            "pumping_log",
            "pumping_last",
            "pumping_count_today",
            "pumping_ml_today",
        }
    ),
    **{
        m.key: frozenset({f"{m.key}_value", f"{m.key}_log", m.key, f"{m.key}_last"})
        for m in MEASUREMENTS
    },
}

# Entities that exist while any of several trackers is enabled.
SHARED_ENTITY_KEYS: dict[str, frozenset[str]] = {
    "last_feed": frozenset({TRACKER_BOTTLE, TRACKER_BREASTFEEDING}),
}


# The calendars of a baby, by group, and the trackers each one shows. Every
# tracker is in exactly one group.
CALENDAR_GROUPS: dict[str, tuple[str, ...]] = {
    "feeding": (TRACKER_BOTTLE, TRACKER_BREASTFEEDING, TRACKER_SOLIDS, TRACKER_PUMPING),
    "diapers": (TRACKER_DIAPER,),
    "sleep": (TRACKER_SLEEP,),
    "health": (TRACKER_TEMPERATURE, TRACKER_WEIGHT, TRACKER_LENGTH, TRACKER_MEDICATION),
}
_grouped = [key for keys in CALENDAR_GROUPS.values() for key in keys]
if sorted(_grouped) != sorted(TRACKERS):
    raise RuntimeError(f"Calendar groups do not cover each tracker once: {_grouped}")

# Unique id key of the calendar of a group: "<baby_id>_calendar_<group>".
CALENDAR_KEY_PREFIX = "calendar_"


def calendar_groups(
    enabled: Collection[str], has_medication: bool, recorded: Collection[str]
) -> tuple[str, ...]:
    """Return the groups a baby has a calendar for, in display order.

    A group qualifies when one of its trackers is enabled, when it shows
    medication doses and the baby has a medication, or when the baby has
    events of its trackers, such as those of a tracker disabled later.
    """
    return tuple(
        group
        for group, keys in CALENDAR_GROUPS.items()
        if any(key in enabled or key in recorded for key in keys)
        or (has_medication and TRACKER_MEDICATION in keys)
    )


# Unique id prefix of a medication's entities: "<baby_id>_med_<id>_<key>".
MEDICATION_KEY_PREFIX = "med_"


def trackers_of_key(key: str) -> frozenset[str] | None:
    """Return the trackers an entity key needs, any of them enabled.

    None means the entity belongs to every baby, whatever its trackers.
    """
    if key in SHARED_ENTITY_KEYS:
        return SHARED_ENTITY_KEYS[key]
    for tracker, keys in TRACKER_ENTITY_KEYS.items():
        if key in keys:
            return frozenset({tracker})
    return None
