"""Intents for Home Assistant's built-in conversation agent.

The managed sentence files (see sentences.py) turn sentences into these
intents. Each handler records through the actions' code and answers in the
sentence's language.
"""

import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Final, override

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import intent
from homeassistant.util import dt as dt_util
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN
from .models import BabyConfigEntry
from .services import (
    async_delete,
    async_log,
    async_log_dose,
    async_start_timer,
    async_stop_timer,
    entry_for_baby,
    event_and_entry,
    find_medication,
)
from .store import Event
from .trackers import TRACKERS
from .trackers.timed import TimedTracker
from .voice import (
    VoiceError,
    async_error_message,
    describe,
    recorded_text,
    resolve_baby,
    spoken,
    text,
)

INTENT_PREFIX: Final = "BabyCalendar"
# A voice entry can be undone this long after it was recorded.
VOICE_UNDO_WINDOW: Final = timedelta(minutes=10)

_NUMBER = re.compile(r"^\d+(?:[.,]\d+)?$")


@dataclass(slots=True)
class _LastVoiceEntry:
    event_id: str
    recorded_at: datetime


# The last entry recorded by voice, per baby id, for undo.
DATA_LAST: HassKey[dict[str, _LastVoiceEntry]] = HassKey(f"{DOMAIN}_voice_last")


def intent_type(name: str) -> str:
    """Return the intent type of an action, such as "LogBottle"."""
    return f"{INTENT_PREFIX}{name}"


def _slot(intent_obj: intent.Intent, name: str) -> Any:
    slot = intent_obj.slots.get(name)
    return None if slot is None else slot.get("value")


def parse_number(raw: Any, language: str) -> float:
    """Read "90", "37,2" or "37.2" (also "37 vírgula 2") as a number."""
    if isinstance(raw, int | float):
        return float(raw)
    value = re.sub(r"\s*(vírgula|virgula|point)\s*", ".", str(raw).strip().lower())
    if not _NUMBER.match(value):
        raise VoiceError(text(language, "bad_number", text=raw))
    return float(value.replace(",", "."))


def _loaded(hass: HomeAssistant, entry_id: str) -> BabyConfigEntry | None:
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        return None
    return entry if entry.state is ConfigEntryState.LOADED else None


def _baby(hass: HomeAssistant, intent_obj: intent.Intent) -> BabyConfigEntry:
    """Return the baby a sentence names, its medication's owner, or the only one.

    The baby and medication slots carry entry ids, from the generated lists.
    """
    if (entry_id := _slot(intent_obj, "baby")) and (entry := _loaded(hass, entry_id)):
        return entry
    medication = str(_slot(intent_obj, "medication") or "")
    if medication and (entry := _loaded(hass, medication.partition(":")[0])):
        return entry
    return resolve_baby(hass, None, intent_obj.language)


def _when(intent_obj: intent.Intent) -> datetime | None:
    minutes = _slot(intent_obj, "minutes")
    return None if minutes is None else dt_util.now() - timedelta(minutes=int(minutes))


Record = Callable[[HomeAssistant, BabyConfigEntry, intent.Intent], Awaitable[Event]]


class BabyIntentHandler(intent.IntentHandler):
    """Record through ``record`` and answer with what was recorded."""

    def __init__(self, name: str, record: Record) -> None:
        """Create the handler of one intent."""
        self.intent_type = intent_type(name)
        self._record = record

    @override
    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Record the entry and set the spoken reply."""
        hass, language = intent_obj.hass, intent_obj.language
        response = intent_obj.create_response()
        try:
            entry = _baby(hass, intent_obj)
            event = await self._record(hass, entry, intent_obj)
        except VoiceError as err:
            response.async_set_speech(str(err))
            return response
        except HomeAssistantError as err:
            response.async_set_speech(await async_error_message(hass, err, language))
            return response
        remember(hass, entry, event)
        response.async_set_speech(recorded_text(language, describe(hass, entry, event)))
        return response


@callback
def remember(hass: HomeAssistant, entry: BabyConfigEntry, event: Event) -> None:
    """Keep the entry a sentence recorded, for undo."""
    hass.data.setdefault(DATA_LAST, {})[entry.runtime_data.baby_id] = _LastVoiceEntry(
        event.id, dt_util.utcnow()
    )


def _fields(intent_obj: intent.Intent) -> dict[str, Any]:
    """Return a tracker's fields from the slots that carry them."""
    language = intent_obj.language
    fields: dict[str, Any] = {}
    for name in ("content", "stool", "side"):
        if (value := _slot(intent_obj, name)) is not None:
            fields[name] = value
    if (amount := _slot(intent_obj, "amount")) is not None:
        fields["amount"] = parse_number(amount, language)
    if (raw := _slot(intent_obj, "value")) is not None:
        number = parse_number(raw, language)
        if _slot(intent_obj, "unit") == "kg":
            number *= 1000
        fields["value"] = number
    return fields


def _log(key: str) -> Record:
    tracker = TRACKERS[key]

    async def record(
        hass: HomeAssistant, entry: BabyConfigEntry, intent_obj: intent.Intent
    ) -> Event:
        return await async_log(
            hass, entry, tracker, _fields(intent_obj), when=_when(intent_obj)
        )

    return record


def _start(key: str) -> Record:
    tracker = TRACKERS[key]
    assert isinstance(tracker, TimedTracker)

    async def record(
        hass: HomeAssistant, entry: BabyConfigEntry, intent_obj: intent.Intent
    ) -> Event:
        return await async_start_timer(
            hass, entry, tracker, _fields(intent_obj), when=_when(intent_obj)
        )

    return record


def _stop(key: str) -> Record:
    tracker = TRACKERS[key]
    assert isinstance(tracker, TimedTracker)

    async def record(
        hass: HomeAssistant, entry: BabyConfigEntry, intent_obj: intent.Intent
    ) -> Event:
        return await async_stop_timer(hass, entry, tracker, when=_when(intent_obj))

    return record


async def _dose(
    hass: HomeAssistant, entry: BabyConfigEntry, intent_obj: intent.Intent
) -> Event:
    # The medication slot is "<entry_id>:<medication name>".
    name = str(_slot(intent_obj, "medication") or "").partition(":")[2]
    return await async_log_dose(
        hass, entry, find_medication(entry, name), when=_when(intent_obj)
    )


class UndoIntentHandler(intent.IntentHandler):
    """Delete the last entry recorded by voice, within the undo window."""

    intent_type = intent_type("Undo")

    @override
    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Delete the most recent voice entry of the named or only baby."""
        hass, language = intent_obj.hass, intent_obj.language
        response = intent_obj.create_response()
        last = hass.data.get(DATA_LAST, {})
        cutoff = dt_util.utcnow() - VOICE_UNDO_WINDOW
        try:
            wanted = _slot(intent_obj, "baby")
            baby_ids = (
                [_baby(hass, intent_obj).runtime_data.baby_id] if wanted else list(last)
            )
        except VoiceError as err:
            response.async_set_speech(str(err))
            return response
        recent = [
            (item.recorded_at, baby_id)
            for baby_id in baby_ids
            if (item := last.get(baby_id)) and item.recorded_at >= cutoff
        ]
        if not recent:
            response.async_set_speech(text(language, "nothing_to_undo"))
            return response
        _, baby_id = max(recent)
        item = last.pop(baby_id)
        entry = entry_for_baby(hass, baby_id)
        try:
            if entry is None:
                raise VoiceError(text(language, "nothing_to_undo"))
            event, entry = await event_and_entry(hass, item.event_id)
            await async_delete(hass, entry, event)
        except VoiceError as err:
            response.async_set_speech(str(err))
            return response
        except HomeAssistantError:
            response.async_set_speech(text(language, "nothing_to_undo"))
            return response
        info = describe(hass, entry, event)
        response.async_set_speech(
            text(language, "deleted", what=spoken(info["recorded"]), baby=info["baby"])
        )
        return response


def handlers() -> list[intent.IntentHandler]:
    """Return every intent handler of the integration."""
    result: list[intent.IntentHandler] = []
    for key, tracker in TRACKERS.items():
        name = key.title().replace("_", "")
        if isinstance(tracker, TimedTracker):
            result += [
                BabyIntentHandler(f"Start{name}", _start(key)),
                BabyIntentHandler(f"Stop{name}", _stop(key)),
            ]
        elif key != "medication":
            result.append(BabyIntentHandler(f"Log{name}", _log(key)))
    result.append(BabyIntentHandler("LogMedication", _dose))
    result.append(UndoIntentHandler())
    return result


@callback
def async_register_intents(hass: HomeAssistant) -> None:
    """Register the intents once, when the integration is set up."""
    for handler in handlers():
        intent.async_register(hass, handler)
