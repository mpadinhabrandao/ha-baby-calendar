"""The trackers the integration offers, and the entities each one owns."""

from ..const import TRACKER_BOTTLE, TRACKER_DIAPER

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
}


def tracker_of_key(key: str) -> str | None:
    """Return the tracker that owns an entity key, or None for shared keys."""
    for tracker, keys in TRACKER_ENTITY_KEYS.items():
        if key in keys:
            return tracker
    return None
