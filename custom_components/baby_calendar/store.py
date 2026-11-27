"""SQLite event store, the only module that touches SQL.

Every method is synchronous and blocks on disk I/O. Call them through
``hass.async_add_executor_job``, never from the event loop.

Times are UTC epoch seconds. Periods are half-open: ``[start_ts, end_ts)``.
"""

import json
import shutil
import sqlite3
import threading
import time
import uuid
from collections.abc import Callable, Collection, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE babies (
    baby_id     TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    removed_ts  INTEGER
);
CREATE TABLE events (
    id          TEXT PRIMARY KEY,
    baby_id     TEXT NOT NULL REFERENCES babies,
    tracker     TEXT NOT NULL,
    start_ts    INTEGER NOT NULL,
    end_ts      INTEGER,
    kind        TEXT,
    amount      REAL,
    data        TEXT NOT NULL,
    notes       TEXT,
    created_ts  INTEGER NOT NULL,
    updated_ts  INTEGER NOT NULL
);
CREATE INDEX events_baby_tracker_start ON events (baby_id, tracker, start_ts);
CREATE INDEX events_baby_start ON events (baby_id, start_ts);
CREATE INDEX events_baby_created ON events (baby_id, created_ts);
"""

# Migration from schema version N to N + 1, keyed by N.
_MIGRATIONS: dict[int, Callable[[sqlite3.Connection], None]] = {}

_EVENT_COLUMNS = (
    "id, baby_id, tracker, start_ts, end_ts, kind, amount, data, notes, "
    "created_ts, updated_ts"
)
_UPDATABLE = frozenset({"start_ts", "end_ts", "kind", "amount", "data", "notes"})


class StoreError(Exception):
    """Base class for event store errors."""


class NewerSchemaError(StoreError):
    """The file was written by a newer version of the integration."""


class UnknownBabyError(StoreError):
    """No baby has this identifier."""


class UnknownEventError(StoreError):
    """No event has this identifier."""


class TimerRunningError(StoreError):
    """The tracker already has an event in progress for this baby."""


@dataclass(frozen=True, slots=True)
class Baby:
    """A row of the babies table."""

    baby_id: str
    name: str
    removed_ts: int | None


@dataclass(frozen=True, slots=True)
class Event:
    """A row of the events table."""

    id: str
    baby_id: str
    tracker: str
    start_ts: int
    end_ts: int | None
    kind: str | None
    amount: float | None
    data: dict[str, Any]
    notes: str | None
    created_ts: int
    updated_ts: int


@dataclass(frozen=True, slots=True)
class PurgeResult:
    """What a purge deleted."""

    babies: int
    events: int


def _event(row: sqlite3.Row) -> Event:
    return Event(
        id=row["id"],
        baby_id=row["baby_id"],
        tracker=row["tracker"],
        start_ts=row["start_ts"],
        end_ts=row["end_ts"],
        kind=row["kind"],
        amount=row["amount"],
        data=json.loads(row["data"]),
        notes=row["notes"],
        created_ts=row["created_ts"],
        updated_ts=row["updated_ts"],
    )


def _baby(row: sqlite3.Row) -> Baby:
    return Baby(baby_id=row["baby_id"], name=row["name"], removed_ts=row["removed_ts"])


def _dump(data: dict[str, Any] | None) -> str:
    return json.dumps(data or {}, sort_keys=True)


def _kinds_clause(kinds: Iterable[str] | None) -> tuple[str, list[str]]:
    if kinds is None:
        return "", []
    values = list(kinds)
    return f" AND kind IN ({', '.join('?' * len(values))})", values


class EventStore:
    """Durable record of babies and their events.

    One connection, shared by all threads and guarded by one lock.
    """

    def __init__(self, path: str | Path) -> None:
        """Remember where the file is. Nothing is opened yet."""
        self._path = Path(path)
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        self._suspended = False

    # ------------------------------------------------------------ lifecycle

    def open(self) -> None:
        """Open the file, creating or migrating the schema as needed."""
        with self._lock:
            self._open()

    def close(self) -> None:
        """Close the file."""
        with self._lock:
            self._close()

    def suspend(self) -> None:
        """Close the file and block every other call until ``resume``.

        Used around a backup, so the file is never copied mid-transaction.
        """
        if self._suspended:
            return
        self._lock.acquire()
        self._suspended = True
        self._close()

    def resume(self) -> None:
        """Reopen the file after ``suspend`` and let waiting calls proceed."""
        if not self._suspended:
            return
        try:
            self._open()
        finally:
            self._suspended = False
            self._lock.release()

    def _open(self) -> None:
        if self._conn is not None:
            return
        conn = self._connect()
        try:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version > SCHEMA_VERSION:
                raise NewerSchemaError(
                    f"{self._path.name} has schema version {version}, but this "
                    f"version of Baby Calendar only knows up to {SCHEMA_VERSION}. "
                    "Update the integration."
                )
            if version == 0:
                # One transaction, so an interrupted first start leaves an
                # empty file and not tables without a version.
                conn.executescript(
                    f"BEGIN;{_SCHEMA}PRAGMA user_version = {SCHEMA_VERSION};COMMIT;"
                )
            elif version < SCHEMA_VERSION:
                conn.close()
                shutil.copyfile(self._path, f"{self._path}.bak")
                conn = self._connect()
                for step in range(version, SCHEMA_VERSION):
                    conn.execute("BEGIN")
                    try:
                        _MIGRATIONS[step](conn)
                        conn.execute(f"PRAGMA user_version = {step + 1}")
                    except BaseException:
                        conn.rollback()
                        raise
                    conn.commit()
        except BaseException:
            conn.close()
            raise
        self._conn = conn

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _require(self) -> sqlite3.Connection:
        if self._conn is None:
            raise StoreError("The event store is closed")
        return self._conn

    # --------------------------------------------------------------- babies

    def create_baby(self, name: str) -> Baby:
        """Add a baby and return it."""
        baby = Baby(baby_id=str(uuid.uuid4()), name=name, removed_ts=None)
        with self._lock:
            conn = self._require()
            with conn:
                conn.execute(
                    "INSERT INTO babies (baby_id, name) VALUES (?, ?)",
                    (baby.baby_id, baby.name),
                )
        return baby

    def get_baby(self, baby_id: str) -> Baby | None:
        """Return a baby, or None when the identifier is unknown."""
        with self._lock:
            row = (
                self._require()
                .execute("SELECT * FROM babies WHERE baby_id = ?", (baby_id,))
                .fetchone()
            )
        return _baby(row) if row else None

    def rename_baby(self, baby_id: str, name: str) -> None:
        """Change a baby's name."""
        self._update_baby("name = ?", (name,), baby_id)

    def mark_removed(self, baby_id: str, *, now: int | None = None) -> None:
        """Detach a baby from its config entry. Its events are kept."""
        removed_ts = int(time.time()) if now is None else now
        self._update_baby("removed_ts = ?", (removed_ts,), baby_id)

    def reattach(self, baby_id: str) -> None:
        """Attach a removed baby to a config entry again."""
        self._update_baby("removed_ts = NULL", (), baby_id)

    def find_removed(self, name: str) -> list[Baby]:
        """Return removed babies with this name, most recently removed first.

        The comparison ignores case.
        """
        with self._lock:
            rows = (
                self._require()
                .execute(
                    "SELECT * FROM babies WHERE removed_ts IS NOT NULL "
                    "ORDER BY removed_ts DESC, rowid DESC"
                )
                .fetchall()
            )
        wanted = name.casefold()
        return [_baby(row) for row in rows if row["name"].casefold() == wanted]

    def purge_removed(self, name: str) -> PurgeResult:
        """Permanently delete every removed baby with this name, and its events.

        Babies that are still attached to a config entry are never touched.
        """
        babies = self.find_removed(name)
        events = 0
        with self._lock:
            conn = self._require()
            with conn:
                for baby in babies:
                    events += conn.execute(
                        "DELETE FROM events WHERE baby_id = ?", (baby.baby_id,)
                    ).rowcount
                    conn.execute(
                        "DELETE FROM babies WHERE baby_id = ? "
                        "AND removed_ts IS NOT NULL",
                        (baby.baby_id,),
                    )
        return PurgeResult(babies=len(babies), events=events)

    def _update_baby(
        self, assignment: str, values: tuple[Any, ...], baby_id: str
    ) -> None:
        with self._lock:
            conn = self._require()
            with conn:
                cursor = conn.execute(
                    f"UPDATE babies SET {assignment} WHERE baby_id = ?",
                    (*values, baby_id),
                )
        if cursor.rowcount == 0:
            raise UnknownBabyError(baby_id)

    # --------------------------------------------------------------- events

    def add_event(
        self,
        *,
        baby_id: str,
        tracker: str,
        start_ts: int,
        end_ts: int | None = None,
        kind: str | None = None,
        amount: float | None = None,
        data: dict[str, Any] | None = None,
        notes: str | None = None,
        now: int | None = None,
    ) -> Event:
        """Record an event and return it."""
        recorded_ts = int(time.time()) if now is None else now
        event = Event(
            id=str(uuid.uuid4()),
            baby_id=baby_id,
            tracker=tracker,
            start_ts=start_ts,
            end_ts=end_ts,
            kind=kind,
            amount=amount,
            data=dict(data or {}),
            notes=notes,
            created_ts=recorded_ts,
            updated_ts=recorded_ts,
        )
        with self._lock:
            conn = self._require()
            try:
                with conn:
                    conn.execute(
                        f"INSERT INTO events ({_EVENT_COLUMNS}) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            event.id,
                            event.baby_id,
                            event.tracker,
                            event.start_ts,
                            event.end_ts,
                            event.kind,
                            event.amount,
                            _dump(event.data),
                            event.notes,
                            event.created_ts,
                            event.updated_ts,
                        ),
                    )
            except sqlite3.IntegrityError as err:
                raise UnknownBabyError(baby_id) from err
        return event

    def get_event(self, event_id: str) -> Event | None:
        """Return an event, or None when the identifier is unknown."""
        with self._lock:
            row = self._select_event(self._require(), event_id)
        return _event(row) if row else None

    def update_event(
        self, event_id: str, changes: dict[str, Any], *, now: int | None = None
    ) -> Event:
        """Change columns of an event and return the result.

        ``changes`` maps column names to new values; a value of None clears
        the column. Columns that are not named keep their value.
        """
        unknown = changes.keys() - _UPDATABLE
        if unknown:
            raise ValueError(f"Cannot update {sorted(unknown)}")
        values = {
            column: _dump(value) if column == "data" else value
            for column, value in changes.items()
        }
        values["updated_ts"] = int(time.time()) if now is None else now
        assignments = ", ".join(f"{column} = ?" for column in values)
        with self._lock:
            conn = self._require()
            with conn:
                cursor = conn.execute(
                    f"UPDATE events SET {assignments} WHERE id = ?",
                    (*values.values(), event_id),
                )
            if cursor.rowcount == 0:
                raise UnknownEventError(event_id)
            row = self._select_event(conn, event_id)
        return _event(row)

    def delete_event(self, event_id: str) -> Event:
        """Permanently delete an event and return what it was."""
        with self._lock:
            conn = self._require()
            row = self._select_event(conn, event_id)
            if row is None:
                raise UnknownEventError(event_id)
            with conn:
                conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
        return _event(row)

    def list_events(
        self,
        baby_id: str,
        start_ts: int,
        end_ts: int,
        tracker: str | None = None,
        timed: Iterable[str] = (),
        trackers: Collection[str] | None = None,
    ) -> list[Event]:
        """Return a baby's events of a period, oldest first.

        An event of a tracker named in ``timed`` is returned when it overlaps
        the period: it starts before the period ends and ends after it starts,
        or is still running. Other events are returned when they start in it.
        ``tracker`` keeps one tracker's events and ``trackers`` those of any
        of several.
        """
        timed = list(timed)
        if timed:
            marks = ", ".join("?" * len(timed))
            query = (
                f"SELECT {_EVENT_COLUMNS} FROM events WHERE baby_id = ? AND ("
                f"(tracker IN ({marks}) AND start_ts < ? "
                "AND (end_ts IS NULL OR end_ts > ?)) "
                f"OR (tracker NOT IN ({marks}) AND start_ts >= ? AND start_ts < ?))"
            )
            params: list[Any] = [
                baby_id,
                *timed,
                end_ts,
                start_ts,
                *timed,
                start_ts,
                end_ts,
            ]
        else:
            query = (
                f"SELECT {_EVENT_COLUMNS} FROM events "
                "WHERE baby_id = ? AND start_ts >= ? AND start_ts < ?"
            )
            params = [baby_id, start_ts, end_ts]
        if tracker is not None:
            query += " AND tracker = ?"
            params.append(tracker)
        if trackers is not None:
            query += f" AND tracker IN ({', '.join('?' * len(trackers))})"
            params.extend(trackers)
        query += " ORDER BY start_ts, created_ts, rowid"
        with self._lock:
            rows = self._require().execute(query, params).fetchall()
        return [_event(row) for row in rows]

    def trackers_with_events(self, baby_id: str) -> set[str]:
        """Return the trackers a baby has at least one event of."""
        with self._lock:
            rows = (
                self._require()
                .execute(
                    "SELECT DISTINCT tracker FROM events WHERE baby_id = ?", (baby_id,)
                )
                .fetchall()
            )
        return {row[0] for row in rows}

    def latest_recorded(self, baby_id: str, tracker: str | None = None) -> Event | None:
        """Return the event that was recorded last, whatever its event time."""
        query = f"SELECT {_EVENT_COLUMNS} FROM events WHERE baby_id = ?"
        params: list[Any] = [baby_id]
        if tracker is not None:
            query += " AND tracker = ?"
            params.append(tracker)
        query += " ORDER BY created_ts DESC, rowid DESC LIMIT 1"
        with self._lock:
            row = self._require().execute(query, params).fetchone()
        return _event(row) if row else None

    # ----------------------------------------------------------- timers

    def start_timer(
        self,
        *,
        baby_id: str,
        tracker: str,
        start_ts: int,
        kind: str | None = None,
        data: dict[str, Any] | None = None,
        notes: str | None = None,
        now: int | None = None,
    ) -> Event:
        """Record an in-progress event of a timed tracker.

        Refused when the tracker already has one running for the baby; the
        check and the insert happen under the same lock.
        """
        recorded_ts = int(time.time()) if now is None else now
        event = Event(
            id=str(uuid.uuid4()),
            baby_id=baby_id,
            tracker=tracker,
            start_ts=start_ts,
            end_ts=None,
            kind=kind,
            amount=None,
            data=dict(data or {}),
            notes=notes,
            created_ts=recorded_ts,
            updated_ts=recorded_ts,
        )
        with self._lock:
            conn = self._require()
            if self._select_running(conn, baby_id, tracker) is not None:
                raise TimerRunningError(tracker)
            try:
                with conn:
                    conn.execute(
                        f"INSERT INTO events ({_EVENT_COLUMNS}) "
                        "VALUES (?, ?, ?, ?, NULL, ?, NULL, ?, ?, ?, ?)",
                        (
                            event.id,
                            baby_id,
                            tracker,
                            start_ts,
                            kind,
                            _dump(event.data),
                            notes,
                            recorded_ts,
                            recorded_ts,
                        ),
                    )
            except sqlite3.IntegrityError as err:
                raise UnknownBabyError(baby_id) from err
        return event

    def running_event(self, baby_id: str, tracker: str) -> Event | None:
        """Return the tracker's in-progress event for the baby, if any.

        Only meaningful for timed trackers: instant events also have no end.
        """
        with self._lock:
            row = self._select_running(self._require(), baby_id, tracker)
        return _event(row) if row else None

    def last_before(self, baby_id: str, tracker: str, before_ts: int) -> Event | None:
        """Return the tracker's latest event that started before a time."""
        with self._lock:
            row = (
                self._require()
                .execute(
                    f"SELECT {_EVENT_COLUMNS} FROM events WHERE baby_id = ? "
                    "AND tracker = ? AND start_ts < ? "
                    "ORDER BY start_ts DESC, created_ts DESC, rowid DESC LIMIT 1",
                    (baby_id, tracker, before_ts),
                )
                .fetchone()
            )
        return _event(row) if row else None

    def last_finished(self, baby_id: str, tracker: str) -> Event | None:
        """Return the tracker's event that ended last."""
        with self._lock:
            row = (
                self._require()
                .execute(
                    f"SELECT {_EVENT_COLUMNS} FROM events WHERE baby_id = ? "
                    "AND tracker = ? AND end_ts IS NOT NULL "
                    "ORDER BY end_ts DESC, created_ts DESC, rowid DESC LIMIT 1",
                    (baby_id, tracker),
                )
                .fetchone()
            )
        return _event(row) if row else None

    @staticmethod
    def _select_running(
        conn: sqlite3.Connection, baby_id: str, tracker: str
    ) -> sqlite3.Row | None:
        return conn.execute(
            f"SELECT {_EVENT_COLUMNS} FROM events WHERE baby_id = ? "
            "AND tracker = ? AND end_ts IS NULL "
            "ORDER BY start_ts DESC, rowid DESC LIMIT 1",
            (baby_id, tracker),
        ).fetchone()

    # ------------------------------------------- helpers for tracker state

    def last_event(
        self, baby_id: str, tracker: str, kinds: Iterable[str] | None = None
    ) -> Event | None:
        """Return the event with the latest event time, optionally by kind."""
        clause, kind_params = _kinds_clause(kinds)
        with self._lock:
            row = (
                self._require()
                .execute(
                    f"SELECT {_EVENT_COLUMNS} FROM events "
                    f"WHERE baby_id = ? AND tracker = ?{clause} "
                    "ORDER BY start_ts DESC, created_ts DESC, rowid DESC LIMIT 1",
                    (baby_id, tracker, *kind_params),
                )
                .fetchone()
            )
        return _event(row) if row else None

    def count_events(
        self,
        baby_id: str,
        tracker: str,
        start_ts: int,
        end_ts: int,
        kinds: Iterable[str] | None = None,
    ) -> int:
        """Count a tracker's events of a period, optionally by kind."""
        return int(
            self._aggregate("COUNT(*)", baby_id, tracker, start_ts, end_ts, kinds)
        )

    def sum_amount(
        self,
        baby_id: str,
        tracker: str,
        start_ts: int,
        end_ts: int,
        kinds: Iterable[str] | None = None,
    ) -> float:
        """Sum the amounts of a tracker's events of a period."""
        return float(
            self._aggregate(
                "COALESCE(SUM(amount), 0)", baby_id, tracker, start_ts, end_ts, kinds
            )
        )

    def _aggregate(
        self,
        expression: str,
        baby_id: str,
        tracker: str,
        start_ts: int,
        end_ts: int,
        kinds: Iterable[str] | None,
    ) -> Any:
        clause, kind_params = _kinds_clause(kinds)
        with self._lock:
            row = (
                self._require()
                .execute(
                    f"SELECT {expression} FROM events WHERE baby_id = ? "
                    f"AND tracker = ? AND start_ts >= ? AND start_ts < ?{clause}",
                    (baby_id, tracker, start_ts, end_ts, *kind_params),
                )
                .fetchone()
            )
        return row[0]

    @staticmethod
    def _select_event(conn: sqlite3.Connection, event_id: str) -> sqlite3.Row | None:
        return conn.execute(
            f"SELECT {_EVENT_COLUMNS} FROM events WHERE id = ?", (event_id,)
        ).fetchone()
