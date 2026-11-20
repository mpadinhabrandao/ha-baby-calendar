"""The trackers the integration offers, and the entities each one owns."""

from ..const import (
    TRACKER_BOTTLE,
    TRACKER_BREASTFEEDING,
    TRACKER_DIAPER,
    TRACKER_PUMPING,
    TRACKER_SLEEP,
    TRACKER_SOLIDS,
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
