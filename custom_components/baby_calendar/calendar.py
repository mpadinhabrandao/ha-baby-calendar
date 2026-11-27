"""Calendar entities: a baby's recorded events as timelines, one per group."""

from dataclasses import replace
from datetime import date, datetime
from typing import Any, Final, override

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityFeature,
    CalendarEvent,
)
from homeassistant.components.calendar.const import (
    EVENT_DESCRIPTION,
    EVENT_END,
    EVENT_RRULE,
    EVENT_START,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MED_NAME, TRACKER_MEDICATION
from .data import async_get_store, async_run
from .entity import BabyEntity
from .models import BabyConfigEntry
from .services import async_delete, async_update_fields, event_and_entry, now_ts
from .store import Event
from .trackers import CALENDAR_GROUPS, CALENDAR_KEY_PREFIX, TIMED_TRACKERS, TRACKERS
from .trackers.medication import current_name

# Length of the block an instantaneous event fills in the calendar.
INSTANT_LENGTH: Final = 5 * 60


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BabyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the baby's calendars of the groups decided at setup."""
    async_add_entities(
        BabyCalendar(entry, group) for group in entry.runtime_data.calendar_groups
    )


def _utc(ts: int) -> datetime:
    return dt_util.utc_from_timestamp(ts)


class BabyCalendar(BabyEntity, CalendarEntity):
    """The recorded events of one baby from the trackers of one group.

    A view over the event store: no events are created here, and edits go
    through the same checks as the update_event and delete_event actions.
    """

    _attr_icon = "mdi:calendar-heart"
    _attr_supported_features = (
        CalendarEntityFeature.UPDATE_EVENT | CalendarEntityFeature.DELETE_EVENT
    )

    def __init__(self, entry: BabyConfigEntry, group: str) -> None:
        """Create the calendar of one group of one baby."""
        super().__init__(entry, f"{CALENDAR_KEY_PREFIX}{group}")
        self.trackers = CALENDAR_GROUPS[group]
        self.timed = tuple(key for key in self.trackers if key in TIMED_TRACKERS)

    def _to_calendar_event(self, event: Event, now: int) -> CalendarEvent:
        tracker = TRACKERS[event.tracker]
        if event.tracker == TRACKER_MEDICATION:
            event = replace(
                event,
                data={**event.data, MED_NAME: current_name(self.entry.options, event)},
            )
        if not tracker.timed:
            end_ts = event.start_ts + INSTANT_LENGTH
        elif event.end_ts is None:
            # Up to now, rounded up to the next minute.
            end_ts = max(now - now % 60 + 60, event.start_ts + 60)
        else:
            end_ts = event.end_ts
        return CalendarEvent(
            start=_utc(event.start_ts),
            end=_utc(end_ts),
            summary=tracker.summary(event, self.hass.config.language, now),
            description=event.notes or "",
            uid=event.id,
        )

    @property
    @override
    def event(self) -> CalendarEvent | None:
        """Return the timed event in progress, if any; instants never are."""
        data = self.coordinator.data
        now = now_ts()
        for key in self.timed:
            if key in data and (running := data[key][f"{key}_running"]):
                return self._to_calendar_event(running, now)
        return None

    @override
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        store = await async_get_store(hass)
        events = await async_run(
            hass,
            store.list_events,
            self.entry.runtime_data.baby_id,
            int(start_date.timestamp()),
            int(end_date.timestamp()),
            None,
            self.timed,
            self.trackers,
        )
        now = now_ts()
        return [self._to_calendar_event(event, now) for event in events]

    async def _own_event(self, uid: str) -> Event:
        event, entry = await event_and_entry(self.hass, uid)
        if entry.entry_id != self.entry.entry_id or event.tracker not in self.trackers:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="unknown_event",
                translation_placeholders={"event_id": uid},
            )
        return event

    @override
    async def async_update_event(
        self,
        uid: str,
        event: dict[str, Any],
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        if event.get(EVENT_RRULE):
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="calendar_no_recurrence"
            )
        start = event[EVENT_START]
        if not isinstance(start, datetime) and isinstance(start, date):
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="calendar_no_all_day"
            )
        stored = await self._own_event(uid)
        tracker = TRACKERS[stored.tracker]

        when = start if int(start.timestamp()) != stored.start_ts else None
        end = None
        dtend = event.get(EVENT_END)
        if (
            tracker.timed
            and stored.end_ts is not None
            and isinstance(dtend, datetime)
            and int(dtend.timestamp()) != stored.end_ts
        ):
            end = dtend

        notes = event.get(EVENT_DESCRIPTION) or None
        notes_changed = notes != stored.notes
        # The title is generated, so a title edited in the calendar is ignored.
        await async_update_fields(
            self.hass,
            self.entry,
            stored,
            {},
            when=when,
            end=end,
            notes=notes if notes_changed and notes else None,
            clear_notes=notes_changed and notes is None,
        )

    @override
    async def async_delete_event(
        self,
        uid: str,
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        await async_delete(self.hass, self.entry, await self._own_event(uid))
