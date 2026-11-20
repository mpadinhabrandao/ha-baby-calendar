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

# Every tracker the integration offers, in the order the UI lists them.
TRACKER_KEYS: Final = (
    TRACKER_DIAPER,
    TRACKER_BOTTLE,
    TRACKER_BREASTFEEDING,
    TRACKER_SLEEP,
)

# State group of the values computed across trackers, such as the last feed.
FEEDING: Final = "feeding"

SERVICE_PURGE_HISTORY: Final = "purge_history"
