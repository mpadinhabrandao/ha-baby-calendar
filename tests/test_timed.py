"""Tests for the timed trackers: timers, durations, breastfeeding and sleep."""

from datetime import datetime, timedelta
from typing import Any

import probatio
import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.baby_calendar.const import CONF_BABY_ID, CONF_TRACKERS
from custom_components.baby_calendar.data import async_get_store

from .conftest import add_baby
from .test_diaper import attrs, eid, press, value
from .test_services import call, device_id

TZ = dt_util.get_time_zone("Europe/Lisbon")
NOW = datetime(2026, 11, 20, 10, 0, tzinfo=TZ)


@pytest.fixture(autouse=True)
async def frozen(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> FrozenDateTimeFactory:
    """Run in Lisbon at 10:00 on a fixed day."""
    await hass.config.async_set_time_zone("Europe/Lisbon")
    freezer.move_to(NOW)
    return freezer


async def act(
    hass: HomeAssistant, entry: ConfigEntry, service: str, **data: Any
) -> str:
    """Call a timed action for a baby and return the event id."""
    result = await call(hass, service, {"device_id": device_id(hass, entry), **data})
    await hass.async_block_till_done()
    return result["event_id"]


async def event(hass: HomeAssistant, event_id: str):
    """Return a stored event."""
    return (await async_get_store(hass)).get_event(event_id)


async def set_number(
    hass: HomeAssistant, entry: ConfigEntry, key: str, val: float
) -> None:
    """Set one of a baby's number inputs."""
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": eid(hass, entry, "number", key), "value": val},
        blocking=True,
    )


async def switch(hass: HomeAssistant, entry: ConfigEntry, key: str, on: bool) -> None:
    """Turn one of a baby's switches on or off."""
    await hass.services.async_call(
        "switch",
        "turn_on" if on else "turn_off",
        {"entity_id": eid(hass, entry, "switch", key)},
        blocking=True,
    )
    await hass.async_block_till_done()


async def side(hass: HomeAssistant, entry: ConfigEntry, option: str) -> None:
    """Choose the breastfeeding side."""
    await hass.services.async_call(
        "select",
        "select_option",
        {
            "entity_id": eid(hass, entry, "select", "breastfeeding_side"),
            "option": option,
        },
        blocking=True,
    )


def ts(when: datetime) -> int:
    """Return a datetime as epoch seconds."""
    return int(when.timestamp())


# ------------------------------------------------------- start and stop


async def test_started_and_stopped(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """A timer started now and stopped twelve minutes later lasts twelve minutes."""
    entry = await add_baby(hass)
    event_id = await act(hass, entry, "start_sleep")
    assert (await event(hass, event_id)).end_ts is None
    assert value(hass, entry, "switch", "sleep_timer") == STATE_ON

    frozen.tick(timedelta(minutes=12))
    await act(hass, entry, "stop_sleep")

    stored = await event(hass, event_id)
    assert stored.end_ts - stored.start_ts == 12 * 60
    assert value(hass, entry, "switch", "sleep_timer") == STATE_OFF


async def test_started_late_and_stopped_earlier(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """A start ten minutes ago and an end five minutes ago are kept."""
    entry = await add_baby(hass)
    event_id = await act(
        hass, entry, "start_sleep", time=(NOW - timedelta(minutes=10)).isoformat()
    )
    frozen.tick(timedelta(minutes=20))
    await act(
        hass,
        entry,
        "stop_sleep",
        time=(dt_util.now() - timedelta(minutes=5)).isoformat(),
    )

    stored = await event(hass, event_id)
    assert stored.start_ts == ts(NOW - timedelta(minutes=10))
    assert stored.end_ts == ts(NOW + timedelta(minutes=15))


async def test_already_running(hass: HomeAssistant) -> None:
    """A second start fails and leaves the running timer unchanged."""
    entry = await add_baby(hass)
    first = await act(hass, entry, "start_sleep")

    with pytest.raises(ServiceValidationError) as err:
        await act(hass, entry, "start_sleep")

    assert err.value.translation_key == "timer_running"
    assert (await event(hass, first)).end_ts is None


async def test_two_trackers_at_once(hass: HomeAssistant) -> None:
    """Breastfeeding and sleep timers run independently."""
    entry = await add_baby(hass)
    await act(hass, entry, "start_breastfeeding")
    await act(hass, entry, "start_sleep")
    assert value(hass, entry, "switch", "breastfeeding_timer") == STATE_ON
    assert value(hass, entry, "switch", "sleep_timer") == STATE_ON


async def test_stop_errors(hass: HomeAssistant) -> None:
    """Stopping with nothing running or before the start fails."""
    entry = await add_baby(hass)
    with pytest.raises(ServiceValidationError) as err:
        await act(hass, entry, "stop_sleep")
    assert err.value.translation_key == "timer_not_running"

    event_id = await act(hass, entry, "start_sleep")
    with pytest.raises(ServiceValidationError) as err:
        await act(
            hass, entry, "stop_sleep", time=(NOW - timedelta(minutes=1)).isoformat()
        )
    assert err.value.translation_key == "end_before_start"
    assert (await event(hass, event_id)).end_ts is None


async def test_timer_survives_a_reload(hass: HomeAssistant) -> None:
    """A running timer is still running after the entry reloads."""
    entry = await add_baby(hass)
    event_id = await act(hass, entry, "start_sleep")

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert value(hass, entry, "switch", "sleep_timer") == STATE_ON
    started = hass.states.get(eid(hass, entry, "switch", "sleep_timer")).attributes
    assert started["started_at"] == NOW.isoformat()
    assert (await event(hass, event_id)).end_ts is None


async def test_timer_stopped_when_its_tracker_is_disabled(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """Disabling sleep while it runs finishes the sleep at that moment."""
    entry = await add_baby(hass)
    event_id = await act(hass, entry, "start_sleep")
    frozen.tick(timedelta(minutes=30))

    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_TRACKERS: ["diaper"]}
    )
    await hass.async_block_till_done()

    assert (await event(hass, event_id)).end_ts == ts(NOW + timedelta(minutes=30))


async def test_undo_a_timer_started_by_mistake(hass: HomeAssistant) -> None:
    """Undo after turning the switch on deletes the running entry."""
    entry = await add_baby(hass)
    await switch(hass, entry, "sleep_timer", True)
    await press(hass, entry, "undo")

    assert value(hass, entry, "switch", "sleep_timer") == STATE_OFF
    store = await async_get_store(hass)
    assert store.count_events(entry.data[CONF_BABY_ID], "sleep", 0, 10**10) == 0


# ---------------------------------------------------------- the switch


async def test_switch_on_and_off(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """On, eight minutes, off: one finished eight-minute event."""
    entry = await add_baby(hass)
    await switch(hass, entry, "sleep_timer", True)
    frozen.tick(timedelta(minutes=8))
    await switch(hass, entry, "sleep_timer", False)

    last = attrs(hass, entry, "sleep_last")
    assert (last["duration"], last["in_progress"]) == (480, False)


async def test_switch_with_minutes_ago(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """Minutes ago moves the start on and the end off, and goes back to 0."""
    entry = await add_baby(hass)
    await set_number(hass, entry, "minutes_ago", 10)
    await switch(hass, entry, "sleep_timer", True)
    assert value(hass, entry, "number", "minutes_ago") == "0"

    frozen.tick(timedelta(hours=1))
    await set_number(hass, entry, "minutes_ago", 15)
    await switch(hass, entry, "sleep_timer", False)

    last = attrs(hass, entry, "sleep_last")
    assert (
        value(hass, entry, "sensor", "sleep_last")
        == (NOW - timedelta(minutes=10)).astimezone(dt_util.UTC).isoformat()
    )
    assert last["ended_at"] == (NOW + timedelta(minutes=45)).isoformat()


async def test_switch_follows_the_service(hass: HomeAssistant) -> None:
    """Starting by service turns the switch on; logging afterwards does not."""
    entry = await add_baby(hass)
    await act(hass, entry, "log_sleep", duration={"minutes": 30})
    assert value(hass, entry, "switch", "sleep_timer") == STATE_OFF
    await act(hass, entry, "start_sleep")
    assert value(hass, entry, "switch", "sleep_timer") == STATE_ON


# ------------------------------------------------------ log by duration


async def test_logged_afterwards(hass: HomeAssistant) -> None:
    """Ninety minutes with no time ends now."""
    entry = await add_baby(hass)
    stored = await event(hass, await act(hass, entry, "log_sleep", duration="01:30:00"))
    assert (stored.start_ts, stored.end_ts) == (
        ts(NOW - timedelta(minutes=90)),
        ts(NOW),
    )


async def test_logged_with_a_start(hass: HomeAssistant) -> None:
    """A start of 08:00 and forty minutes gives 08:00 to 08:40."""
    entry = await add_baby(hass)
    start = NOW.replace(hour=8)
    stored = await event(
        hass,
        await act(
            hass, entry, "log_sleep", duration={"minutes": 40}, time=start.isoformat()
        ),
    )
    assert (stored.start_ts, stored.end_ts) == (
        ts(start),
        ts(start + timedelta(minutes=40)),
    )


async def test_duration_missing_or_zero(hass: HomeAssistant) -> None:
    """No duration or a zero duration is refused."""
    entry = await add_baby(hass)
    with pytest.raises(probatio.Invalid):
        await act(hass, entry, "log_sleep")
    with pytest.raises(ServiceValidationError) as err:
        await act(hass, entry, "log_sleep", duration={"minutes": 0})
    assert err.value.translation_key == "duration_zero"


async def test_log_leaves_a_running_timer(hass: HomeAssistant) -> None:
    """Logging a finished sleep while one runs keeps the timer running."""
    entry = await add_baby(hass)
    await act(hass, entry, "start_sleep")
    await act(hass, entry, "log_sleep", duration={"minutes": 20})
    assert value(hass, entry, "switch", "sleep_timer") == STATE_ON


async def test_logged_from_the_dashboard(hass: HomeAssistant) -> None:
    """Fifteen in the duration input and the button: fifteen minutes ending now."""
    entry = await add_baby(hass)
    await set_number(hass, entry, "sleep_duration", 15)
    await press(hass, entry, "sleep_log")

    last = attrs(hass, entry, "sleep_last")
    assert last["duration"] == 15 * 60
    assert last["ended_at"] == NOW.isoformat()
    assert value(hass, entry, "number", "sleep_duration") == "0"


async def test_dashboard_duration_at_zero(hass: HomeAssistant) -> None:
    """The button fails while the duration input is 0."""
    entry = await add_baby(hass)
    with pytest.raises(ServiceValidationError):
        await press(hass, entry, "sleep_log")
    assert value(hass, entry, "sensor", "sleep_last") == STATE_UNKNOWN


# ------------------------------------------------------------ correction


async def test_end_corrected(hass: HomeAssistant) -> None:
    """Moving the end ten minutes earlier shortens the event."""
    entry = await add_baby(hass)
    event_id = await act(hass, entry, "log_sleep", duration={"minutes": 40})

    result = await call(
        hass,
        "update_event",
        {"event_id": event_id, "end_time": (NOW - timedelta(minutes=10)).isoformat()},
    )

    assert (result["duration"], result["in_progress"]) == (30 * 60, False)
    assert float(value(hass, entry, "sensor", "sleep_duration_today")) == 30


async def test_invalid_end(hass: HomeAssistant) -> None:
    """An end before the start is refused and nothing changes."""
    entry = await add_baby(hass)
    event_id = await act(hass, entry, "log_sleep", duration={"minutes": 40})

    with pytest.raises(ServiceValidationError) as err:
        await call(
            hass,
            "update_event",
            {"event_id": event_id, "end_time": (NOW - timedelta(hours=1)).isoformat()},
        )

    assert err.value.translation_key == "end_before_start"
    assert (await event(hass, event_id)).end_ts == ts(NOW)


async def test_running_timer_corrected(hass: HomeAssistant) -> None:
    """A running timer's start can move; its end cannot be set."""
    entry = await add_baby(hass)
    event_id = await act(hass, entry, "start_sleep")

    result = await call(
        hass,
        "update_event",
        {"event_id": event_id, "time": (NOW - timedelta(minutes=5)).isoformat()},
    )
    assert result["in_progress"] is True
    assert result["time"] == (NOW - timedelta(minutes=5)).isoformat()

    with pytest.raises(ServiceValidationError) as err:
        await call(
            hass, "update_event", {"event_id": event_id, "end_time": NOW.isoformat()}
        )
    assert err.value.translation_key == "end_time_running"


async def test_end_time_on_an_instant_event(hass: HomeAssistant) -> None:
    """A diaper change has no end time."""
    entry = await add_baby(hass)
    event_id = await act(hass, entry, "log_diaper", content="wet")
    with pytest.raises(ServiceValidationError) as err:
        await call(
            hass, "update_event", {"event_id": event_id, "end_time": NOW.isoformat()}
        )
    assert err.value.translation_key == "end_time_not_timed"


# ----------------------------------------------------------- durations


async def test_two_finished_events(hass: HomeAssistant) -> None:
    """Eight and six minutes today make fourteen."""
    entry = await add_baby(hass)
    await act(
        hass,
        entry,
        "log_breastfeeding",
        duration={"minutes": 8},
        time=NOW.replace(hour=7).isoformat(),
    )
    await act(hass, entry, "log_breastfeeding", duration={"minutes": 6})
    assert float(value(hass, entry, "sensor", "breastfeeding_duration_today")) == 14


@pytest.mark.parametrize(
    ("start_hour", "end_hour", "first_day", "second_day"),
    [(23, 6, 60, 6 * 60), (18, 1, 6 * 60, 60)],
)
async def test_sleep_across_midnight(
    hass: HomeAssistant,
    frozen: FrozenDateTimeFactory,
    start_hour: int,
    end_hour: int,
    first_day: int,
    second_day: int,
) -> None:
    """A sleep across midnight counts on each day for its part of that day."""
    entry = await add_baby(hass)
    start = NOW.replace(hour=start_hour)
    frozen.move_to(start)
    await act(hass, entry, "start_sleep")

    midnight = NOW.replace(hour=0) + timedelta(days=1)
    frozen.move_to(midnight - timedelta(seconds=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert float(value(hass, entry, "sensor", "sleep_duration_today")) == pytest.approx(
        first_day, abs=0.1
    )

    frozen.move_to(midnight)
    async_fire_time_changed(hass, midnight)
    await hass.async_block_till_done()
    frozen.move_to(midnight.replace(hour=end_hour))
    await act(hass, entry, "stop_sleep")

    assert float(value(hass, entry, "sensor", "sleep_duration_today")) == second_day
    assert value(hass, entry, "sensor", "sleep_count_today") == "0"


async def test_running_timer_advances(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """A timer started at 10:00 counts thirty minutes at 10:30."""
    entry = await add_baby(hass)
    await act(hass, entry, "start_sleep")
    for _ in range(30):
        frozen.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
    assert float(value(hass, entry, "sensor", "sleep_duration_today")) == 30


async def test_count_by_start_day(hass: HomeAssistant) -> None:
    """A sleep from 23:00 yesterday is not counted today; a nap today is."""
    entry = await add_baby(hass)
    yesterday = NOW.replace(hour=23) - timedelta(days=1)
    await act(
        hass, entry, "log_sleep", duration={"hours": 7}, time=yesterday.isoformat()
    )
    await act(hass, entry, "log_sleep", duration={"minutes": 20})
    assert value(hass, entry, "sensor", "sleep_count_today") == "1"


async def test_listing_overlapping_sleep(hass: HomeAssistant) -> None:
    """Today's listing includes a sleep from 23:00 yesterday to 06:00 today."""
    entry = await add_baby(hass)
    yesterday = NOW.replace(hour=23) - timedelta(days=1)
    event_id = await act(
        hass, entry, "log_sleep", duration={"hours": 7}, time=yesterday.isoformat()
    )

    result = await call(
        hass,
        "list_events",
        {
            "device_id": device_id(hass, entry),
            "start": NOW.replace(hour=0).isoformat(),
            "end": (NOW.replace(hour=0) + timedelta(days=1)).isoformat(),
        },
    )

    [listed] = result["events"]
    assert listed["event_id"] == event_id
    assert listed["end"] == NOW.replace(hour=6).isoformat()
    assert (listed["duration"], listed["in_progress"]) == (7 * 3600, False)


# -------------------------------------------------------- breastfeeding


async def test_side_from_the_service(hass: HomeAssistant) -> None:
    """The side given to start is kept; an unknown side is refused."""
    entry = await add_baby(hass)
    stored = await event(
        hass, await act(hass, entry, "start_breastfeeding", side="left")
    )
    assert stored.kind == "left"
    with pytest.raises(probatio.Invalid):
        await act(hass, entry, "log_breastfeeding", duration={"minutes": 5}, side="top")


async def test_side_omitted(hass: HomeAssistant) -> None:
    """An entry logged without a side has none and leaves the selector."""
    entry = await add_baby(hass)
    await side(hass, entry, "left")
    stored = await event(
        hass, await act(hass, entry, "log_breastfeeding", duration={"minutes": 5})
    )
    assert stored.kind is None
    assert value(hass, entry, "select", "breastfeeding_side") == "left"


async def test_selector_used_by_the_switch_and_flipped(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """Right then the switch gives a right entry; stopping it selects left."""
    entry = await add_baby(hass)
    await side(hass, entry, "right")
    await switch(hass, entry, "breastfeeding_timer", True)
    assert attrs(hass, entry, "breastfeeding_last")["side"] == "right"

    frozen.tick(timedelta(minutes=8))
    await switch(hass, entry, "breastfeeding_timer", False)
    assert value(hass, entry, "select", "breastfeeding_side") == "left"


async def test_selector_used_by_the_button(hass: HomeAssistant) -> None:
    """Left and fifteen minutes with the button: a left entry; right is next."""
    entry = await add_baby(hass)
    await side(hass, entry, "left")
    await set_number(hass, entry, "breastfeeding_duration", 15)
    await press(hass, entry, "breastfeeding_log")

    last = attrs(hass, entry, "breastfeeding_last")
    assert (last["side"], last["duration"]) == ("left", 900)
    assert value(hass, entry, "select", "breastfeeding_side") == "right"


async def test_left_then_right_is_one_feed(
    hass: HomeAssistant, frozen: FrozenDateTimeFactory
) -> None:
    """Left eight minutes, a pause, right six: two entries, one feed, 14 min."""
    entry = await add_baby(hass)
    await side(hass, entry, "left")
    await switch(hass, entry, "breastfeeding_timer", True)
    frozen.tick(timedelta(minutes=8))
    await switch(hass, entry, "breastfeeding_timer", False)
    frozen.tick(timedelta(minutes=2))
    await switch(hass, entry, "breastfeeding_timer", True)
    frozen.tick(timedelta(minutes=6))
    await switch(hass, entry, "breastfeeding_timer", False)

    assert value(hass, entry, "sensor", "breastfeeding_feeds_today") == "1"
    assert float(value(hass, entry, "sensor", "breastfeeding_duration_today")) == 14
    assert attrs(hass, entry, "breastfeeding_last")["side"] == "right"
    assert value(hass, entry, "select", "breastfeeding_side") == "left"


async def test_two_separate_feeds(hass: HomeAssistant) -> None:
    """Entries more than 30 minutes apart are two feeds."""
    entry = await add_baby(hass)
    await act(
        hass,
        entry,
        "log_breastfeeding",
        duration={"minutes": 10},
        time=NOW.replace(hour=7).isoformat(),
    )
    await act(hass, entry, "log_breastfeeding", duration={"minutes": 10})
    assert value(hass, entry, "sensor", "breastfeeding_feeds_today") == "2"


async def test_feed_started_before_midnight(hass: HomeAssistant) -> None:
    """A side change just after midnight belongs to yesterday's feed."""
    entry = await add_baby(hass)
    midnight = NOW.replace(hour=0)
    await act(
        hass,
        entry,
        "log_breastfeeding",
        duration={"minutes": 10},
        time=(midnight - timedelta(minutes=15)).isoformat(),
    )
    await act(
        hass,
        entry,
        "log_breastfeeding",
        duration={"minutes": 10},
        time=(midnight + timedelta(minutes=2)).isoformat(),
    )
    assert value(hass, entry, "sensor", "breastfeeding_feeds_today") == "0"


async def test_breastfeeding_last_while_running(hass: HomeAssistant) -> None:
    """While running the last entry is marked in progress, with no end."""
    entry = await add_baby(hass)
    await act(hass, entry, "start_breastfeeding", side="left")
    last = attrs(hass, entry, "breastfeeding_last")
    assert (last["in_progress"], last["ended_at"], last["duration"]) == (
        True,
        None,
        None,
    )


# ------------------------------------------------------- sleep and feeds


async def test_awake_since(hass: HomeAssistant, frozen: FrozenDateTimeFactory) -> None:
    """Awake since shows the last sleep's end, and is unknown while asleep."""
    entry = await add_baby(hass)
    assert value(hass, entry, "sensor", "awake_since") == STATE_UNKNOWN

    await act(hass, entry, "log_sleep", duration={"minutes": 45})
    assert (
        value(hass, entry, "sensor", "awake_since")
        == NOW.astimezone(dt_util.UTC).isoformat()
    )

    frozen.tick(timedelta(hours=1))
    await act(hass, entry, "start_sleep")
    assert value(hass, entry, "sensor", "awake_since") == STATE_UNKNOWN


async def test_last_feed_bottle_after_breast(hass: HomeAssistant) -> None:
    """A bottle at 10:00 after a breastfeed at 08:00 is the last feed."""
    entry = await add_baby(hass)
    await act(
        hass,
        entry,
        "log_breastfeeding",
        duration={"minutes": 10},
        time=NOW.replace(hour=8).isoformat(),
    )
    assert attrs(hass, entry, "last_feed")["kind"] == "breastfeeding"

    await act(hass, entry, "log_bottle", amount=90)

    assert attrs(hass, entry, "last_feed")["kind"] == "bottle"
    assert (
        value(hass, entry, "sensor", "last_feed")
        == NOW.astimezone(dt_util.UTC).isoformat()
    )


@pytest.mark.parametrize(
    ("trackers", "exists"),
    [(["bottle"], True), (["breastfeeding"], True), (["diaper", "sleep"], False)],
)
async def test_last_feed_with_one_feeding_tracker(
    hass: HomeAssistant, trackers: list[str], exists: bool
) -> None:
    """The last feed sensor exists with either feeding tracker, unknown at first."""
    entry = await add_baby(hass, trackers=trackers)
    entity_id = eid(hass, entry, "sensor", "last_feed")
    assert (entity_id is not None) is exists
    if exists:
        assert hass.states.get(entity_id).state == STATE_UNKNOWN


async def test_timed_entities_only_when_enabled(hass: HomeAssistant) -> None:
    """A baby with only diapers has no timed entities."""
    entry = await add_baby(hass, trackers=["diaper"])
    for platform, key in (
        ("switch", "sleep_timer"),
        ("switch", "breastfeeding_timer"),
        ("select", "breastfeeding_side"),
        ("number", "sleep_duration"),
        ("button", "breastfeeding_log"),
        ("sensor", "awake_since"),
    ):
        assert eid(hass, entry, platform, key) is None
