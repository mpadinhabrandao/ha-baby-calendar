"""What the LLM tools and the built-in agent's intents share.

Finding the baby a sentence names, reading when it happened, and describing
what was recorded, in English and Portuguese.
"""

import unicodedata
from datetime import datetime, timedelta
from typing import Any, Final

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.translation import async_get_translations
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .models import BabyConfigEntry
from .services import now_ts
from .store import Event
from .trackers import TRACKERS

TEXTS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "unknown_baby": "No baby named {name}. The babies are: {names}.",
        "which_baby": "Say which baby. The babies are: {names}.",
        "no_babies": "There are no babies in Baby Calendar.",
        "both_times": "Give either a time or minutes ago, not both.",
        "bad_time": "Cannot read the time {time}; use 'YYYY-MM-DD HH:MM'.",
        "recorded": "Recorded {what} for {baby} at {time}.",
        "recorded_span": "Recorded {what} for {baby}, from {time} to {ended}.",
        "deleted": "Deleted {what} for {baby}.",
        "nothing_to_undo": "There is nothing recent to undo.",
        "bad_number": "I could not understand the number {text}.",
    },
    "pt": {
        "unknown_baby": "Não há nenhum bebé chamado {name}. Os bebés são: {names}.",
        "which_baby": "Diz qual bebé. Os bebés são: {names}.",
        "no_babies": "Não há bebés no Baby Calendar.",
        "both_times": "Indica a hora ou há quantos minutos, não as duas.",
        "bad_time": "Não percebi a hora {time}; usa 'AAAA-MM-DD HH:MM'.",
        "recorded": "Registei {what} para {baby} às {time}.",
        "recorded_span": "Registei {what} para {baby}, das {time} às {ended}.",
        "deleted": "Apaguei {what} de {baby}.",
        "nothing_to_undo": "Não há nenhum registo recente para desfazer.",
        "bad_number": "Não percebi o número {text}.",
    },
}


# Tracker names inside error messages, such as "the {tracker} timer".
TRACKER_NAMES: Final[dict[str, dict[str, str]]] = {
    "en": {
        "diaper": "diaper",
        "bottle": "bottle",
        "breastfeeding": "breastfeeding",
        "sleep": "sleep",
        "solids": "solids",
        "pumping": "pumping",
        "weight": "weight",
        "length": "length",
        "temperature": "temperature",
        "medication": "medication",
    },
    "pt": {
        "diaper": "fraldas",
        "bottle": "biberões",
        "breastfeeding": "mama",
        "sleep": "sono",
        "solids": "sólidos",
        "pumping": "extração",
        "weight": "peso",
        "length": "comprimento",
        "temperature": "temperatura",
        "medication": "medicamentos",
    },
}


def _base(language: str | None) -> str:
    base = (language or "en").split("-")[0].lower()
    return base if base in TEXTS else "en"


def text(language: str | None, key: str, **values: Any) -> str:
    """Return a text in a language, such as "pt" or "pt-PT", or English."""
    return TEXTS[_base(language)][key].format(**values)


class VoiceError(Exception):
    """A request that cannot be done, explained in words."""


def plain(value: str) -> str:
    """Return text without case or accents, for matching names."""
    decomposed = unicodedata.normalize("NFKD", value.strip().casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def loaded_babies(hass: HomeAssistant) -> list[BabyConfigEntry]:
    """Return the loaded babies, by name."""
    return sorted(
        hass.config_entries.async_loaded_entries(DOMAIN),
        key=lambda entry: entry.runtime_data.name,
    )


def resolve_baby(
    hass: HomeAssistant, name: str | None, language: str | None = "en"
) -> BabyConfigEntry:
    """Return the baby a name refers to, or the only baby without a name."""
    babies = loaded_babies(hass)
    if not babies:
        raise VoiceError(text(language, "no_babies"))
    names = ", ".join(entry.runtime_data.name for entry in babies)
    if name:
        matches = [e for e in babies if plain(e.runtime_data.name) == plain(name)]
        if len(matches) == 1:
            return matches[0]
        raise VoiceError(text(language, "unknown_baby", name=name, names=names))
    if len(babies) == 1:
        return babies[0]
    raise VoiceError(text(language, "which_baby", names=names))


def resolve_time(args: dict[str, Any], language: str | None = "en") -> datetime | None:
    """Return when it happened from 'time' or 'minutes_ago', or None for now."""
    time, minutes = args.get("time"), args.get("minutes_ago")
    if time is not None and minutes is not None:
        raise VoiceError(text(language, "both_times"))
    if minutes is not None:
        return dt_util.now() - timedelta(minutes=minutes)
    if time is not None:
        when = dt_util.parse_datetime(str(time))
        if when is None:
            raise VoiceError(text(language, "bad_time", time=time))
        return when
    return None


def describe(hass: HomeAssistant, entry: BabyConfigEntry, event: Event) -> dict:
    """Return what was recorded, as the calendar titles it."""
    tracker = TRACKERS[event.tracker]
    info: dict[str, Any] = {
        "recorded": tracker.summary(event, hass.config.language, now_ts()),
        "baby": entry.runtime_data.name,
        "time": clock(event.start_ts),
        "entry_id": event.id,
    }
    if event.end_ts is not None and event.end_ts > event.start_ts:
        info["ended"] = clock(event.end_ts)
        info["duration_minutes"] = round((event.end_ts - event.start_ts) / 60)
    return info


def clock(timestamp: int) -> str:
    """Return a timestamp's local time of day, "HH:MM"."""
    return dt_util.as_local(dt_util.utc_from_timestamp(timestamp)).strftime("%H:%M")


def recorded_text(language: str | None, info: dict[str, Any]) -> str:
    """Return the spoken confirmation of a recorded entry."""
    values = {
        "what": spoken(info["recorded"]),
        "baby": info["baby"],
        "time": info["time"],
    }
    if "ended" in info:
        return text(language, "recorded_span", ended=info["ended"], **values)
    return text(language, "recorded", **values)


def spoken(title: str) -> str:
    """Return a calendar title without its leading emoji, for speech."""
    first, _, rest = title.partition(" ")
    return rest if rest and not any(char.isalnum() for char in first) else title


def error_message(err: HomeAssistantError) -> str:
    """Return an error's message, or its translation key and placeholders."""
    message = str(err)
    if message:
        return message
    placeholders = err.translation_placeholders or {}
    return f"{err.translation_key} {placeholders}".strip()


async def async_error_message(
    hass: HomeAssistant, err: HomeAssistantError, language: str | None
) -> str:
    """Return one of the integration's errors in a language, for speech."""
    if err.translation_domain != DOMAIN or not err.translation_key:
        return error_message(err)
    base = _base(language)
    translations = await async_get_translations(hass, base, "exceptions", [DOMAIN])
    message = translations.get(
        f"component.{DOMAIN}.exceptions.{err.translation_key}.message"
    )
    if not message:
        return error_message(err)
    placeholders = dict(err.translation_placeholders or {})
    if (tracker := placeholders.get("tracker")) in TRACKER_NAMES[base]:
        placeholders["tracker"] = TRACKER_NAMES[base][tracker]
    try:
        return message.format(**placeholders)
    except KeyError:
        return error_message(err)
