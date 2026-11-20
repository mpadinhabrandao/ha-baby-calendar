"""Runtime data of a set-up baby."""

from dataclasses import dataclass, field
from datetime import datetime

from homeassistant.config_entries import ConfigEntry

from .coordinator import BabyCoordinator


@dataclass(slots=True)
class BabyData:
    """What a set-up config entry knows about its baby.

    ``minutes_ago`` is the pending value of the "minutes ago" input. It is
    deliberately not restored, so it is 0 after a restart.
    """

    baby_id: str
    name: str
    trackers: frozenset[str]
    coordinator: BabyCoordinator
    minutes_ago: int = 0
    # When each logging button last logged, for the repeated press guard.
    last_press: dict[str, datetime] = field(default_factory=dict)


type BabyConfigEntry = ConfigEntry[BabyData]
