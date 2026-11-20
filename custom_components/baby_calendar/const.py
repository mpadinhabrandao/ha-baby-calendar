"""Constants for the Baby Calendar integration."""

from typing import Final

DOMAIN: Final = "baby_calendar"

DB_FILENAME: Final = "baby_calendar.db"

# The single event store shared by every baby, in hass.data.
DATA_STORE: Final = "baby_calendar_store"

# Config entry data: what identifies the baby.
CONF_BABY_ID: Final = "baby_id"
CONF_NAME: Final = "name"

# Config entry options: what the user can change later.
CONF_BIRTH_DATE: Final = "birth_date"
CONF_TRACKERS: Final = "trackers"

TRACKER_DIAPER: Final = "diaper"
TRACKER_BOTTLE: Final = "bottle"
TRACKER_BREASTFEEDING: Final = "breastfeeding"
TRACKER_SLEEP: Final = "sleep"
TRACKER_SOLIDS: Final = "solids"
TRACKER_PUMPING: Final = "pumping"
TRACKER_WEIGHT: Final = "weight"
TRACKER_LENGTH: Final = "length"
TRACKER_TEMPERATURE: Final = "temperature"

# Every tracker the integration offers, in the order the UI lists them.
TRACKER_KEYS: Final = (
    TRACKER_DIAPER,
    TRACKER_BOTTLE,
    TRACKER_BREASTFEEDING,
    TRACKER_SLEEP,
    TRACKER_SOLIDS,
    TRACKER_PUMPING,
    TRACKER_WEIGHT,
    TRACKER_LENGTH,
    TRACKER_TEMPERATURE,
)

# State group of the values computed across trackers, such as the last feed.
FEEDING: Final = "feeding"

SERVICE_PURGE_HISTORY: Final = "purge_history"

TRACKER_MEDICATION: Final = "medication"

# Config entry options: the baby's medications, a list of dicts with these keys.
CONF_MEDICATIONS: Final = "medications"
MED_ID: Final = "id"
MED_NAME: Final = "name"
MED_DOSE: Final = "dose"
MED_ACTIVE: Final = "active"
MED_SINCE: Final = "since"

# Fired when a dose of a medication becomes due; see coordinator.py.
EVENT_MEDICATION_DUE: Final = "baby_calendar_medication_due"
MED_SCHEDULE: Final = "schedule"
