"""Runtime data of a set-up baby."""

from dataclasses import dataclass, field
from datetime import datetime

from homeassistant.config_entries import ConfigEntry

from .coordinator import BabyCoordinator


@dataclass(slots=True)
class BabyData:
    """What a set-up config entry knows about its baby.

    ``minutes_ago`` is the pending value of the "minutes ago" input. It is
    deliberately not restored, so it is 0 after a restart. The bottle inputs
    are the baby's usual bottle and are restored by their entities.
    """

    baby_id: str
    name: str
    trackers: frozenset[str]
    coordinator: BabyCoordinator
    minutes_ago: int = 0
    bottle_amount: float = 0
    bottle_content: str | None = None
    # The breastfeeding side selection, restored by its entity.
    breastfeeding_side: str | None = None
    # Pending "duration" inputs of the timed trackers, in minutes, by tracker.
    # Not restored, like minutes_ago.
    durations: dict[str, int] = field(default_factory=dict)
    # Pending pumping inputs. Not restored: every session is different.
    pumping_amount: float = 0
    pumping_side: str | None = None
    # Pending measurement inputs, by tracker. Not restored, like minutes_ago.
    measurements: dict[str, float] = field(default_factory=dict)
    # When each logging button last logged, for the repeated press guard.
    last_press: dict[str, datetime] = field(default_factory=dict)


type BabyConfigEntry = ConfigEntry[BabyData]
