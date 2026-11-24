"""Tests for the pure due computation of medication schedules."""

from datetime import datetime, timedelta

import pytest
from homeassistant.util import dt as dt_util

from custom_components.baby_calendar.schedule import (
    claimed_slots,
    evaluate,
    local_instant,
    parse_times,
)

TZ = dt_util.get_time_zone("Europe/Lisbon")


def at(day: int, hour: int, minute: int = 0, month: int = 11) -> datetime:
    """Return a Lisbon time in 2026."""
    return datetime(2026, month, day, hour, minute, tzinfo=TZ)


def ts(when: datetime) -> int:
    """Return epoch seconds."""
    return int(when.timestamp())


def times(*values: str) -> dict:
    """Return a fixed-times schedule."""
    return {"type": "times", "times": list(values)}


# ---------------------------------------------------------------- parsing


def test_parse_times() -> None:
    """Times are normalised, sorted and de-duplicated."""
    assert parse_times("21:00, 9:00, 09:00") == ["09:00", "21:00"]


@pytest.mark.parametrize("text", ["", " , ", "25:00", "9", "9:7", "ab:cd", "12:60"])
def test_parse_times_invalid(text: str) -> None:
    """An empty list or an invalid time is refused."""
    with pytest.raises(ValueError, match=r".*"):
        parse_times(text)


# --------------------------------------------------------- fixed times


def test_time_reached() -> None:
    """At 09:00 with nothing given, a dose is due and the next is 09:00."""
    state = evaluate(times("09:00"), [ts(at(19, 9))], at(20, 9), TZ)
    assert state.due
    assert state.next_dose == at(20, 9)
    assert state.next_change == at(21, 9)


def test_given_early() -> None:
    """A dose at 08:40 satisfies 09:00, so nothing becomes due."""
    state = evaluate(times("09:00"), [ts(at(20, 8, 40))], at(20, 9, 30), TZ)
    assert not state.due
    assert state.next_dose == at(21, 9)


def test_logged_twice() -> None:
    """Two morning doses satisfy 09:00 only; 21:00 still becomes due."""
    doses = [ts(at(20, 9, 5)), ts(at(20, 9, 6))]
    slots = [at(20, 9), at(20, 21)]
    assert claimed_slots(slots, doses) == {0}
    assert evaluate(times("09:00", "21:00"), doses, at(20, 21), TZ).due


def test_given_after_midnight() -> None:
    """A dose at 00:10 satisfies the 23:00 of the day before, not 09:00."""
    schedule = times("09:00", "23:00")
    doses = [ts(at(19, 9)), ts(at(20, 0, 10))]
    assert not evaluate(schedule, doses, at(20, 0, 20), TZ).due
    assert evaluate(schedule, doses, at(20, 9), TZ).due


def test_still_due_after_midnight() -> None:
    """A missed 23:00 dose is still due after midnight."""
    state = evaluate(times("09:00", "23:00"), [ts(at(19, 9))], at(20, 0, 30), TZ)
    assert state.due
    assert state.next_dose == at(19, 23)


def test_superseded_by_the_next_time() -> None:
    """At 09:00 only the 09:00 dose is due; the missed 23:00 is dropped."""
    state = evaluate(times("09:00", "23:00"), [ts(at(19, 9))], at(20, 9), TZ)
    assert state.due
    assert state.next_dose == at(20, 9)


def test_overdue() -> None:
    """At 10:30 with 09:00 not given, it is due and the next dose is 09:00."""
    state = evaluate(times("09:00"), [], at(20, 10, 30), TZ)
    assert (state.due, state.next_dose) == (True, at(20, 9))


def test_next_dose_after_the_morning() -> None:
    """With 09:00 given, the next dose is 21:00."""
    state = evaluate(times("09:00", "21:00"), [ts(at(20, 9))], at(20, 12), TZ)
    assert (state.due, state.next_dose) == (False, at(20, 21))


def test_next_dose_after_an_early_dose() -> None:
    """With 09:00 given at 08:40, the next dose is 21:00, also before 09:00."""
    schedule = times("09:00", "21:00")
    doses = [ts(at(19, 21)), ts(at(20, 8, 40))]
    state = evaluate(schedule, doses, at(20, 8, 45), TZ)
    assert (state.due, state.next_dose) == (False, at(20, 21))
    assert state.next_change == at(20, 9)


def test_dose_at_the_midpoint_claims_nothing() -> None:
    """A dose exactly between two times satisfies neither."""
    slots = [at(20, 9), at(20, 21)]
    assert claimed_slots(slots, [ts(at(20, 15))]) == set()


def test_time_in_a_daylight_saving_gap() -> None:
    """01:30 on the spring change day becomes the first valid time, 02:00."""
    instant = local_instant(
        at(29, 0, month=3).date(), datetime.min.time().replace(hour=1, minute=30), TZ
    )
    assert instant.astimezone(TZ).hour == 2
    assert instant.astimezone(TZ).minute == 0


def test_time_in_a_repeated_hour() -> None:
    """01:30 on the autumn change day is its first occurrence."""
    instant = local_instant(
        at(25, 0, month=10).date(), datetime.min.time().replace(hour=1, minute=30), TZ
    )
    assert instant.utcoffset() == timedelta(hours=1)


# -------------------------------------------------------------- interval


def test_interval_elapsed() -> None:
    """Six hours after an 08:00 dose, it is due at 14:00."""
    schedule = {"type": "interval", "hours": 6}
    before = evaluate(schedule, [ts(at(20, 8))], at(20, 13), TZ)
    assert (before.due, before.next_dose, before.next_change) == (
        False,
        at(20, 14),
        at(20, 14),
    )
    assert evaluate(schedule, [ts(at(20, 8))], at(20, 14), TZ).due


def test_interval_never_given() -> None:
    """With no dose, nothing is due and there is no next dose."""
    state = evaluate({"type": "interval", "hours": 6}, [], at(20, 14), TZ)
    assert (state.due, state.next_dose, state.next_change) == (False, None, None)


def test_no_schedule() -> None:
    """Without a schedule nothing is ever due."""
    assert not evaluate({"type": "none"}, [], at(20, 9), TZ).due


def test_time_before_the_schedule_started() -> None:
    """Added at 16:00 with 09:00: not due until tomorrow's 09:00."""
    since = ts(at(20, 16))
    state = evaluate(times("09:00"), [], at(20, 16, 5), TZ, since)
    assert (state.due, state.next_dose) == (False, at(21, 9))
    assert evaluate(times("09:00"), [], at(21, 9), TZ, since).due
