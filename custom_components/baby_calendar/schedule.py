"""When a medication dose is due: a pure function of schedule, doses and clock.

Nothing here touches Home Assistant or the store, so it can be evaluated
at any moment, such as right after a restart, and tested on its own.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta, tzinfo
from typing import Any, Final

SCHEDULE_NONE: Final = "none"
SCHEDULE_TIMES: Final = "times"
SCHEDULE_INTERVAL: Final = "interval"

# Days of fixed-time slots built around now: before, and after.
DAYS_BEFORE: Final = 2
DAYS_AFTER: Final = 1


@dataclass(frozen=True, slots=True)
class DueState:
    """Whether a dose is due, the next dose time and when this changes."""

    due: bool
    next_dose: datetime | None
    next_change: datetime | None


NOTHING_DUE: Final = DueState(due=False, next_dose=None, next_change=None)


def parse_times(text: str) -> list[str]:
    """Parse "9:00, 21:00" into sorted, unique "HH:MM" values.

    Raises ValueError for an empty list or an invalid time.
    """
    values = set()
    for part in text.replace(";", ",").split(","):
        if not (part := part.strip()):
            continue
        hours, sep, minutes = part.partition(":")
        if not sep or not hours.isdigit() or not minutes.isdigit():
            raise ValueError(part)
        if len(minutes) != 2 or int(hours) > 23 or int(minutes) > 59:
            raise ValueError(part)
        values.add(f"{int(hours):02d}:{minutes}")
    if not values:
        raise ValueError("no time")
    return sorted(values)


def local_instant(day: date, at: time, zone: tzinfo) -> datetime:
    """Return a local wall-clock time on a day as an aware datetime.

    A time skipped by a daylight saving change is moved forward to the first
    time that exists; a time that happens twice is its first occurrence.
    """
    naive = datetime.combine(day, at)
    for minutes in range(0, 24 * 60):
        candidate = naive + timedelta(minutes=minutes)
        aware = candidate.replace(tzinfo=zone, fold=0)
        # Through UTC: converting to the same zone returns the input unchanged.
        if aware.astimezone(UTC).astimezone(zone).replace(tzinfo=None) == candidate:
            return aware
    raise ValueError(f"No valid time near {naive}")  # pragma: no cover


def slots_around(times: list[str], now: datetime, zone: tzinfo) -> list[datetime]:
    """Return every scheduled time from two days before now to the next day."""
    today = now.astimezone(zone).date()
    slots = [
        local_instant(today + timedelta(days=offset), time.fromisoformat(value), zone)
        for offset in range(-DAYS_BEFORE, DAYS_AFTER + 1)
        for value in times
    ]
    return sorted(slots, key=lambda slot: slot.timestamp())


def claimed_slots(slots: list[datetime], doses: list[int]) -> set[int]:
    """Match doses to slots and return the indexes of the claimed slots.

    In dose order, a dose claims its nearest slot when that slot is still
    free and the dose is nearer to it than to either neighbouring slot.
    """
    stamps = [int(slot.timestamp()) for slot in slots]
    claimed: set[int] = set()
    for dose in sorted(doses):
        nearest = min(range(len(stamps)), key=lambda i: abs(stamps[i] - dose))
        distance = abs(stamps[nearest] - dose)
        neighbours = [
            abs(stamps[i] - dose)
            for i in (nearest - 1, nearest + 1)
            if 0 <= i < len(stamps)
        ]
        if nearest in claimed or any(other <= distance for other in neighbours):
            continue
        claimed.add(nearest)
    return claimed


def evaluate(
    schedule: dict[str, Any],
    doses: list[int],
    now: datetime,
    zone: tzinfo,
    since: int | None = None,
) -> DueState:
    """Return whether a dose is due now.

    ``doses`` are the medication's dose times, as UTC epoch seconds, at
    least from two days before now; ``now`` is aware. ``since`` is when the
    schedule started applying, as UTC epoch seconds: a fixed time before it
    is never due, so a medication added at 16:00 with a 09:00 time is not
    due until the next 09:00.
    """
    kind = schedule.get("type", SCHEDULE_NONE)
    if kind == SCHEDULE_INTERVAL:
        return _evaluate_interval(float(schedule["hours"]), doses, now)
    if kind == SCHEDULE_TIMES and schedule.get("times"):
        return _evaluate_times(list(schedule["times"]), doses, now, zone, since)
    return NOTHING_DUE


def _evaluate_interval(hours: float, doses: list[int], now: datetime) -> DueState:
    past = [dose for dose in doses if dose <= now.timestamp()]
    if not past:
        return NOTHING_DUE
    next_dose = datetime.fromtimestamp(max(past), now.tzinfo) + timedelta(hours=hours)
    due = now >= next_dose
    return DueState(
        due=due, next_dose=next_dose, next_change=None if due else next_dose
    )


def _evaluate_times(
    times: list[str],
    doses: list[int],
    now: datetime,
    zone: tzinfo,
    since: int | None,
) -> DueState:
    slots = slots_around(times, now, zone)
    claimed = claimed_slots(slots, [dose for dose in doses if dose <= now.timestamp()])
    current = max((i for i, slot in enumerate(slots) if slot <= now), default=None)
    upcoming = next(slot for slot in slots if slot > now)
    # A time already satisfied by an early dose is not the next dose.
    next_free = next(
        (slot for i, slot in enumerate(slots) if slot > now and i not in claimed),
        upcoming,
    )
    due = (
        current is not None
        and current not in claimed
        and (since is None or slots[current].timestamp() >= since)
    )
    return DueState(
        due=due,
        next_dose=slots[current] if due else next_free,
        next_change=upcoming,
    )
