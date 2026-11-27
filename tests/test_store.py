"""Tests for the SQLite event store."""

import sqlite3
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

from custom_components.baby_calendar import store as store_module
from custom_components.baby_calendar.store import (
    EventStore,
    NewerSchemaError,
    StoreError,
    TimerRunningError,
    UnknownBabyError,
    UnknownEventError,
)

DAY = 86400


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Path of the store file of a test."""
    return tmp_path / "baby_calendar.db"


@pytest.fixture
def store(db_path: Path) -> Iterator[EventStore]:
    """Return an open, empty store."""
    event_store = EventStore(db_path)
    event_store.open()
    yield event_store
    event_store.close()


def _user_version(path: Path) -> int:
    conn = sqlite3.connect(path)
    try:
        return conn.execute("PRAGMA user_version").fetchone()[0]
    finally:
        conn.close()


# ---------------------------------------------------------------- lifecycle


def test_fresh_file_gets_the_schema(db_path: Path, store: EventStore) -> None:
    """A new file is created with both tables and the current version."""
    assert _user_version(db_path) == store_module.SCHEMA_VERSION
    conn = sqlite3.connect(db_path)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    conn.close()
    assert {"babies", "events"} <= tables


def test_reopened_file_keeps_its_data(db_path: Path) -> None:
    """Closing and opening again loses nothing and creates no backup copy."""
    first = EventStore(db_path)
    first.open()
    baby = first.create_baby("Alice")
    event = first.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=100)
    first.close()

    second = EventStore(db_path)
    second.open()
    assert second.get_baby(baby.baby_id) == baby
    assert second.get_event(event.id) == event
    second.close()
    assert not Path(f"{db_path}.bak").exists()


def test_newer_schema_is_refused_and_untouched(db_path: Path) -> None:
    """A file from a newer release fails to open and is left as it was."""
    conn = sqlite3.connect(db_path)
    conn.execute(f"PRAGMA user_version = {store_module.SCHEMA_VERSION + 1}")
    conn.close()
    before = db_path.read_bytes()

    event_store = EventStore(db_path)
    with pytest.raises(NewerSchemaError):
        event_store.open()

    assert db_path.read_bytes() == before
    with pytest.raises(StoreError):
        event_store.create_baby("Alice")


def test_migration_copies_the_file_once(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A migration runs after copying the file to a single .bak, overwritten each time."""
    first = EventStore(db_path)
    first.open()
    baby = first.create_baby("Alice")
    first.close()
    backup = Path(f"{db_path}.bak")

    def add_column(name: str):
        def migrate(conn: sqlite3.Connection) -> None:
            conn.execute(f"ALTER TABLE babies ADD COLUMN {name} TEXT")

        return migrate

    monkeypatch.setattr(store_module, "SCHEMA_VERSION", 2)
    monkeypatch.setitem(store_module._MIGRATIONS, 1, add_column("first"))
    second = EventStore(db_path)
    second.open()
    assert second.get_baby(baby.baby_id) == baby
    second.close()
    assert _user_version(db_path) == 2
    assert _user_version(backup) == 1

    monkeypatch.setattr(store_module, "SCHEMA_VERSION", 3)
    monkeypatch.setitem(store_module._MIGRATIONS, 2, add_column("second"))
    third = EventStore(db_path)
    third.open()
    third.close()
    assert _user_version(db_path) == 3
    assert _user_version(backup) == 2
    assert sorted(path.name for path in db_path.parent.iterdir()) == [
        db_path.name,
        backup.name,
    ]


def test_failed_migration_changes_nothing(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A migration that fails leaves the file at its old version."""
    EventStore(db_path).open()

    def migrate(conn: sqlite3.Connection) -> None:
        conn.execute("ALTER TABLE babies ADD COLUMN extra TEXT")
        raise RuntimeError("boom")

    monkeypatch.setattr(store_module, "SCHEMA_VERSION", 2)
    monkeypatch.setitem(store_module._MIGRATIONS, 1, migrate)
    with pytest.raises(RuntimeError):
        EventStore(db_path).open()

    assert _user_version(db_path) == 1
    conn = sqlite3.connect(db_path)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(babies)")}
    conn.close()
    assert "extra" not in columns


def test_closed_store_refuses_calls(store: EventStore) -> None:
    """Calls on a closed store fail instead of reopening it silently."""
    store.close()
    with pytest.raises(StoreError):
        store.create_baby("Alice")


def test_writes_from_many_threads_all_land(store: EventStore) -> None:
    """The single connection is safe to use from several threads at once."""
    baby = store.create_baby("Alice")

    def write(offset: int) -> None:
        for index in range(25):
            store.add_event(
                baby_id=baby.baby_id, tracker="diaper", start_ts=offset + index
            )

    threads = [threading.Thread(target=write, args=(n * 100,)) for n in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert store.count_events(baby.baby_id, "diaper", 0, 1000) == 200


def test_suspend_blocks_writes_until_resume(store: EventStore) -> None:
    """A write issued while suspended waits, then completes after resume."""
    baby = store.create_baby("Alice")
    store.suspend()
    done = threading.Event()

    def write() -> None:
        store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=1)
        done.set()

    thread = threading.Thread(target=write)
    thread.start()
    assert not done.wait(0.2)

    store.resume()
    thread.join(timeout=5)
    assert done.is_set()
    assert store.count_events(baby.baby_id, "diaper", 0, 10) == 1


def test_suspend_and_resume_are_idempotent(store: EventStore) -> None:
    """Repeated or unpaired calls neither deadlock nor fail."""
    store.resume()
    store.suspend()
    store.suspend()
    store.resume()
    store.resume()
    assert store.create_baby("Alice").name == "Alice"


# ------------------------------------------------------------------- babies


def test_create_and_get_baby(store: EventStore) -> None:
    """A created baby can be read back and is not removed."""
    baby = store.create_baby("Alice")
    assert baby.removed_ts is None
    assert store.get_baby(baby.baby_id) == baby
    assert store.get_baby("missing") is None


def test_rename_baby(store: EventStore) -> None:
    """Renaming changes the name only."""
    baby = store.create_baby("Alice")
    store.rename_baby(baby.baby_id, "Alícia")
    assert store.get_baby(baby.baby_id).name == "Alícia"


def test_removed_baby_keeps_events_and_can_be_reattached(store: EventStore) -> None:
    """Removal only marks the baby; re-attaching clears the mark."""
    baby = store.create_baby("Alice")
    event = store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=100)

    store.mark_removed(baby.baby_id, now=500)
    assert store.get_baby(baby.baby_id).removed_ts == 500
    assert store.get_event(event.id) == event

    store.reattach(baby.baby_id)
    assert store.get_baby(baby.baby_id).removed_ts is None


def test_find_removed_ignores_case_and_active_babies(store: EventStore) -> None:
    """Only removed babies match, whatever the case, newest removal first."""
    old = store.create_baby("Élise")
    new = store.create_baby("élise")
    store.create_baby("ÉLISE")
    other = store.create_baby("Bruno")
    store.mark_removed(old.baby_id, now=100)
    store.mark_removed(new.baby_id, now=200)
    store.mark_removed(other.baby_id, now=300)

    found = store.find_removed("ÉLISE")
    assert [baby.baby_id for baby in found] == [new.baby_id, old.baby_id]
    assert store.find_removed("Nobody") == []


def test_purge_deletes_only_removed_babies_of_that_name(store: EventStore) -> None:
    """A purge leaves configured babies and other names alone."""
    removed = store.create_baby("Alice")
    active = store.create_baby("alice")
    other = store.create_baby("Bruno")
    for baby in (removed, active, other):
        store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=100)
        store.add_event(baby_id=baby.baby_id, tracker="bottle", start_ts=200)
    store.mark_removed(removed.baby_id)
    store.mark_removed(other.baby_id)

    result = store.purge_removed("ALICE")

    assert (result.babies, result.events) == (1, 2)
    assert store.get_baby(removed.baby_id) is None
    assert store.list_events(removed.baby_id, 0, DAY) == []
    assert len(store.list_events(active.baby_id, 0, DAY)) == 2
    assert len(store.list_events(other.baby_id, 0, DAY)) == 2


def test_purge_of_several_removed_babies_with_one_name(store: EventStore) -> None:
    """Every removed baby sharing the name is deleted and counted."""
    for _ in range(2):
        baby = store.create_baby("Alice")
        store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=100)
        store.mark_removed(baby.baby_id)

    result = store.purge_removed("Alice")
    assert (result.babies, result.events) == (2, 2)
    assert store.purge_removed("Alice").babies == 0


@pytest.mark.parametrize("operation", ["rename", "remove", "reattach"])
def test_baby_operations_reject_unknown_identifiers(
    store: EventStore, operation: str
) -> None:
    """Changing a baby that does not exist is an error."""
    calls = {
        "rename": lambda: store.rename_baby("missing", "Alice"),
        "remove": lambda: store.mark_removed("missing"),
        "reattach": lambda: store.reattach("missing"),
    }
    with pytest.raises(UnknownBabyError):
        calls[operation]()


# ------------------------------------------------------------------- events


def test_add_and_get_event(store: EventStore) -> None:
    """An event is stored with every field and a recording time."""
    baby = store.create_baby("Alice")
    event = store.add_event(
        baby_id=baby.baby_id,
        tracker="bottle",
        start_ts=1000,
        kind="formula",
        amount=90,
        data={"brand": "x"},
        notes="slow feed",
        now=1200,
    )

    assert store.get_event(event.id) == event
    assert event.created_ts == event.updated_ts == 1200
    assert event.end_ts is None
    assert event.data == {"brand": "x"}
    assert store.get_event("missing") is None


def test_add_event_for_unknown_baby(store: EventStore) -> None:
    """An event cannot be recorded for a baby that does not exist."""
    with pytest.raises(UnknownBabyError):
        store.add_event(baby_id="missing", tracker="diaper", start_ts=1)


def test_update_changes_only_named_columns(store: EventStore) -> None:
    """Unnamed columns keep their value and updated_ts moves."""
    baby = store.create_baby("Alice")
    event = store.add_event(
        baby_id=baby.baby_id,
        tracker="diaper",
        start_ts=1000,
        kind="dirty",
        data={"stool": "soft"},
        notes="note",
        now=1000,
    )

    updated = store.update_event(event.id, {"start_ts": 400}, now=2000)

    assert updated.start_ts == 400
    assert (updated.kind, updated.data, updated.notes) == (
        "dirty",
        {"stool": "soft"},
        "note",
    )
    assert (updated.created_ts, updated.updated_ts) == (1000, 2000)
    assert store.get_event(event.id) == updated


def test_update_clears_columns_with_none(store: EventStore) -> None:
    """None clears a column; data becomes an empty object."""
    baby = store.create_baby("Alice")
    event = store.add_event(
        baby_id=baby.baby_id,
        tracker="diaper",
        start_ts=1000,
        kind="dirty",
        data={"stool": "soft"},
        notes="note",
    )

    updated = store.update_event(event.id, {"notes": None, "data": None, "kind": "wet"})

    assert (updated.kind, updated.data, updated.notes) == ("wet", {}, None)


def test_update_rejects_unknown_event_and_columns(store: EventStore) -> None:
    """Unknown identifiers and columns that are not editable are errors."""
    baby = store.create_baby("Alice")
    event = store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=1)

    with pytest.raises(UnknownEventError):
        store.update_event("missing", {"notes": "x"})
    with pytest.raises(ValueError, match="baby_id"):
        store.update_event(event.id, {"baby_id": "other"})
    assert store.get_event(event.id) == event


def test_delete_event(store: EventStore) -> None:
    """Deleting returns the event and removes it; twice is an error."""
    baby = store.create_baby("Alice")
    event = store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=1)

    assert store.delete_event(event.id) == event
    assert store.get_event(event.id) is None
    with pytest.raises(UnknownEventError):
        store.delete_event(event.id)


def test_list_events_by_period_baby_and_tracker(store: EventStore) -> None:
    """A listing holds one baby's events of a half-open period, oldest first."""
    alice = store.create_baby("Alice")
    bruno = store.create_baby("Bruno")
    late = store.add_event(baby_id=alice.baby_id, tracker="bottle", start_ts=DAY + 500)
    early = store.add_event(baby_id=alice.baby_id, tracker="diaper", start_ts=DAY)
    store.add_event(baby_id=alice.baby_id, tracker="diaper", start_ts=DAY - 1)
    store.add_event(baby_id=alice.baby_id, tracker="diaper", start_ts=2 * DAY)
    store.add_event(baby_id=bruno.baby_id, tracker="diaper", start_ts=DAY + 100)

    assert store.list_events(alice.baby_id, DAY, 2 * DAY) == [early, late]
    assert store.list_events(alice.baby_id, DAY, 2 * DAY, "bottle") == [late]
    assert store.list_events(alice.baby_id, 5 * DAY, 6 * DAY) == []


def test_list_events_of_several_trackers(store: EventStore) -> None:
    """A listing by several trackers keeps their events and the timed overlap."""
    alice = store.create_baby("Alice")
    sleep = store.add_event(
        baby_id=alice.baby_id, tracker="sleep", start_ts=DAY - 600, end_ts=DAY + 600
    )
    bottle = store.add_event(
        baby_id=alice.baby_id, tracker="bottle", start_ts=DAY + 100
    )
    store.add_event(baby_id=alice.baby_id, tracker="diaper", start_ts=DAY + 200)

    assert store.list_events(
        alice.baby_id, DAY, 2 * DAY, timed=("sleep",), trackers=("sleep", "bottle")
    ) == [sleep, bottle]
    assert store.list_events(alice.baby_id, DAY, 2 * DAY, trackers=("bottle",)) == [
        bottle
    ]


def test_trackers_with_events(store: EventStore) -> None:
    """Only the trackers a baby has events of, whatever their dates."""
    alice = store.create_baby("Alice")
    bruno = store.create_baby("Bruno")
    store.add_event(baby_id=alice.baby_id, tracker="diaper", start_ts=DAY)
    store.add_event(baby_id=alice.baby_id, tracker="diaper", start_ts=2 * DAY)
    store.add_event(baby_id=alice.baby_id, tracker="pumping", start_ts=0)
    store.add_event(baby_id=bruno.baby_id, tracker="bottle", start_ts=DAY)

    assert store.trackers_with_events(alice.baby_id) == {"diaper", "pumping"}
    assert store.trackers_with_events(store.create_baby("Carla").baby_id) == set()


def test_latest_recorded_follows_recording_order(store: EventStore) -> None:
    """The latest recorded event is not the one with the latest event time."""
    baby = store.create_baby("Alice")
    assert store.latest_recorded(baby.baby_id) is None

    store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=5000, now=5000)
    backdated = store.add_event(
        baby_id=baby.baby_id, tracker="bottle", start_ts=1000, now=5100
    )
    assert store.latest_recorded(baby.baby_id) == backdated

    same_second = store.add_event(
        baby_id=baby.baby_id, tracker="diaper", start_ts=900, now=5100
    )
    assert store.latest_recorded(baby.baby_id) == same_second
    assert store.latest_recorded(baby.baby_id, "bottle") == backdated

    store.delete_event(same_second.id)
    assert store.latest_recorded(baby.baby_id) == backdated


# ----------------------------------------------------------- state helpers


def test_helpers_on_an_empty_store(store: EventStore) -> None:
    """With no events there is no last event and the totals are zero."""
    baby = store.create_baby("Alice")
    assert store.last_event(baby.baby_id, "diaper") is None
    assert store.count_events(baby.baby_id, "diaper", 0, DAY) == 0
    assert store.sum_amount(baby.baby_id, "bottle", 0, DAY) == 0.0


def test_last_event_by_tracker_and_kinds(store: EventStore) -> None:
    """The last event is the latest by event time among the wanted kinds."""
    baby = store.create_baby("Alice")
    wet = store.add_event(
        baby_id=baby.baby_id, tracker="diaper", start_ts=800, kind="wet"
    )
    both = store.add_event(
        baby_id=baby.baby_id, tracker="diaper", start_ts=900, kind="both"
    )
    dirty = store.add_event(
        baby_id=baby.baby_id, tracker="diaper", start_ts=1000, kind="dirty"
    )
    store.add_event(baby_id=baby.baby_id, tracker="bottle", start_ts=2000)

    assert store.last_event(baby.baby_id, "diaper") == dirty
    assert store.last_event(baby.baby_id, "diaper", ("wet", "both")) == both
    assert store.last_event(baby.baby_id, "diaper", ("wet",)) == wet
    assert store.last_event(baby.baby_id, "diaper", ("other",)) is None

    store.delete_event(dirty.id)
    assert store.last_event(baby.baby_id, "diaper") == both


def test_count_and_sum_for_a_period(store: EventStore) -> None:
    """Counts and sums cover one baby, one tracker and a half-open period."""
    alice = store.create_baby("Alice")
    bruno = store.create_baby("Bruno")
    for start_ts, kind in ((10, "wet"), (20, "dirty"), (30, "both"), (DAY, "wet")):
        store.add_event(
            baby_id=alice.baby_id, tracker="diaper", start_ts=start_ts, kind=kind
        )
    store.add_event(baby_id=bruno.baby_id, tracker="diaper", start_ts=15, kind="wet")
    for start_ts, amount in ((10, 90), (20, 120.5), (DAY, 60)):
        store.add_event(
            baby_id=alice.baby_id, tracker="bottle", start_ts=start_ts, amount=amount
        )

    assert store.count_events(alice.baby_id, "diaper", 0, DAY) == 3
    assert store.count_events(alice.baby_id, "diaper", 0, DAY, ("wet", "both")) == 2
    assert store.count_events(alice.baby_id, "diaper", 0, DAY, ("dirty", "both")) == 2
    assert store.count_events(alice.baby_id, "bottle", 0, DAY) == 2
    assert store.sum_amount(alice.baby_id, "bottle", 0, DAY) == 210.5
    assert store.sum_amount(alice.baby_id, "diaper", 0, DAY) == 0.0


# ------------------------------------------------------------------- timers


def test_start_and_stop_a_timer(store: EventStore) -> None:
    """A started timer is the running event until its end is set."""
    baby = store.create_baby("Alice")
    assert store.running_event(baby.baby_id, "sleep") is None

    event = store.start_timer(baby_id=baby.baby_id, tracker="sleep", start_ts=100)

    assert event.end_ts is None
    assert store.running_event(baby.baby_id, "sleep") == event
    store.update_event(event.id, {"end_ts": 400})
    assert store.running_event(baby.baby_id, "sleep") is None
    assert store.last_finished(baby.baby_id, "sleep").end_ts == 400


def test_second_start_is_refused(store: EventStore) -> None:
    """Only one timer per tracker and baby runs; others are independent."""
    alice = store.create_baby("Alice")
    bruno = store.create_baby("Bruno")
    first = store.start_timer(baby_id=alice.baby_id, tracker="sleep", start_ts=100)

    with pytest.raises(TimerRunningError):
        store.start_timer(baby_id=alice.baby_id, tracker="sleep", start_ts=200)

    store.start_timer(baby_id=alice.baby_id, tracker="breastfeeding", start_ts=200)
    store.start_timer(baby_id=bruno.baby_id, tracker="sleep", start_ts=200)
    assert store.running_event(alice.baby_id, "sleep") == first


def test_overlap_listing(store: EventStore) -> None:
    """Timed events overlapping the period at either edge are listed."""
    baby = store.create_baby("Alice")
    before = store.add_event(
        baby_id=baby.baby_id, tracker="sleep", start_ts=50, end_ts=150
    )
    after = store.add_event(
        baby_id=baby.baby_id, tracker="sleep", start_ts=180, end_ts=300
    )
    store.add_event(baby_id=baby.baby_id, tracker="sleep", start_ts=10, end_ts=100)
    running = store.start_timer(
        baby_id=baby.baby_id, tracker="breastfeeding", start_ts=20
    )
    diaper = store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=120)
    store.add_event(baby_id=baby.baby_id, tracker="diaper", start_ts=50)

    listed = store.list_events(baby.baby_id, 100, 200, timed=("sleep", "breastfeeding"))

    assert [event.id for event in listed] == [
        running.id,
        before.id,
        diaper.id,
        after.id,
    ]


def test_last_before(store: EventStore) -> None:
    """The latest event starting before a time is found."""
    baby = store.create_baby("Alice")
    old = store.add_event(baby_id=baby.baby_id, tracker="sleep", start_ts=50, end_ts=60)
    store.add_event(baby_id=baby.baby_id, tracker="sleep", start_ts=100, end_ts=160)
    assert store.last_before(baby.baby_id, "sleep", 100) == old
    assert store.last_before(baby.baby_id, "sleep", 50) is None
