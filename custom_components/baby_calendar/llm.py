"""Tools for LLM conversation agents that use the Assist API.

An agent such as OpenAI or Anthropic calls these to record entries, start
and stop timers, record doses and undo, through the same code as the actions.
"""

import unicodedata
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import Any, Final, override

import probatio
from homeassistant.components.llm import LLMTools
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.llm import (
    LLM_API_ASSIST,
    LLMContext,
    Tool,
    ToolAnnotations,
    ToolInput,
    ToolResult,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MED_DOSE, MED_NAME
from .models import BabyConfigEntry
from .services import (
    async_delete,
    async_log,
    async_log_dose,
    async_log_duration,
    async_start_timer,
    async_stop_timer,
    event_and_entry,
    find_medication,
    now_ts,
)
from .store import Event
from .trackers import TRACKERS
from .trackers.base import Tracker
from .trackers.bottle import CONTENTS as BOTTLE_CONTENTS
from .trackers.breastfeeding import SIDES as BREAST_SIDES
from .trackers.diaper import CONTENTS as DIAPER_CONTENTS
from .trackers.diaper import STOOLS
from .trackers.medication import medications
from .trackers.pumping import SIDES as PUMPING_SIDES
from .trackers.timed import TimedTracker

PREFIX: Final = f"{DOMAIN}__"
MAX_MINUTES_AGO: Final = 7 * 24 * 60

_RECORDS = ToolAnnotations(
    read_only=False, destructive=False, idempotent=False, open_world=False
)
_DELETES = ToolAnnotations(
    read_only=False, destructive=True, idempotent=False, open_world=False
)

# What each tracker's tools take, besides the baby, the time and the notes.
# The keys match the trackers' own fields, which they validate again.
_FIELDS: Final[dict[str, dict[Any, Any]]] = {
    "diaper": {
        probatio.Required(
            "content",
            description="wet = pee only, dirty = poop only, both = pee and poop",
        ): probatio.In(DIAPER_CONTENTS),
        probatio.Optional(
            "stool", description="Consistency of the poop, only for a dirty diaper"
        ): probatio.In(STOOLS),
    },
    "bottle": {
        probatio.Required("amount", description="Amount drunk, in ml"): probatio.Coerce(
            float
        ),
        probatio.Optional("content", description="What the bottle held"): probatio.In(
            BOTTLE_CONTENTS
        ),
    },
    "breastfeeding": {
        probatio.Optional("side", description="Breast fed from"): probatio.In(
            BREAST_SIDES
        ),
    },
    "sleep": {},
    "solids": {},
    "pumping": {
        probatio.Required(
            "amount", description="Amount pumped, in ml"
        ): probatio.Coerce(float),
        probatio.Optional("side", description="Breast pumped"): probatio.In(
            PUMPING_SIDES
        ),
    },
    "weight": {
        probatio.Required("value", description="Weight in grams"): probatio.Coerce(
            float
        ),
    },
    "length": {
        probatio.Required(
            "value", description="Length in centimetres"
        ): probatio.Coerce(float),
    },
    "temperature": {
        probatio.Required(
            "value", description="Body temperature in degrees Celsius"
        ): probatio.Coerce(float),
    },
}

_WHAT: Final = {
    "diaper": "a diaper change",
    "bottle": "a bottle feed",
    "breastfeeding": "a finished breastfeed of a known duration",
    "sleep": "a finished sleep of a known duration",
    "solids": "a meal of solid food; put what was eaten in the notes",
    "pumping": "breast milk pumped",
    "weight": "the baby's weight",
    "length": "the baby's length",
    "temperature": "the baby's body temperature",
}

_BABY = probatio.Optional(
    "baby", description="The baby's name; may be left out when there is only one baby"
)
_TIME = probatio.Optional(
    "time",
    description="Local date and time it happened, 'YYYY-MM-DD HH:MM'; leave out for now",
)
_MINUTES_AGO = probatio.Optional(
    "minutes_ago", description="How many minutes ago it happened; leave out for now"
)
_NOTES = probatio.Optional("notes", description="Free text to keep with the entry")


class ToolError(Exception):
    """A tool call that cannot be done, explained to the model."""


def _plain(text: str) -> str:
    """Return text without case or accents, for matching names."""
    decomposed = unicodedata.normalize("NFKD", text.strip().casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _babies(hass: HomeAssistant) -> list[BabyConfigEntry]:
    return sorted(
        hass.config_entries.async_loaded_entries(DOMAIN),
        key=lambda entry: entry.runtime_data.name,
    )


def resolve_baby(hass: HomeAssistant, name: str | None) -> BabyConfigEntry:
    """Return the baby a name refers to, or the only baby without a name."""
    babies = _babies(hass)
    names = ", ".join(entry.runtime_data.name for entry in babies)
    if name:
        matches = [e for e in babies if _plain(e.runtime_data.name) == _plain(name)]
        if len(matches) == 1:
            return matches[0]
        raise ToolError(f"No baby named {name!r}. The babies are: {names}.")
    if len(babies) == 1:
        return babies[0]
    raise ToolError(f"Say which baby. The babies are: {names}.")


def resolve_time(args: dict[str, Any]) -> datetime | None:
    """Return when it happened from 'time' or 'minutes_ago', or None for now."""
    time, minutes = args.get("time"), args.get("minutes_ago")
    if time is not None and minutes is not None:
        raise ToolError("Give either time or minutes_ago, not both.")
    if minutes is not None:
        return dt_util.now() - timedelta(minutes=minutes)
    if time is not None:
        when = dt_util.parse_datetime(str(time))
        if when is None:
            raise ToolError(f"Cannot read the time {time!r}; use 'YYYY-MM-DD HH:MM'.")
        return when
    return None


def describe(hass: HomeAssistant, entry: BabyConfigEntry, event: Event) -> dict:
    """Return what was recorded, as the calendar titles it."""
    tracker = TRACKERS[event.tracker]
    start = dt_util.as_local(dt_util.utc_from_timestamp(event.start_ts))
    return {
        "recorded": tracker.summary(event, hass.config.language, now_ts()),
        "baby": entry.runtime_data.name,
        "time": start.strftime("%H:%M"),
        "entry_id": event.id,
    }


def _message(err: HomeAssistantError) -> str:
    text = str(err)
    if text:
        return text
    placeholders = err.translation_placeholders or {}
    return f"{err.translation_key} {placeholders}".strip()


class BabyTool(Tool):
    """A Baby Calendar tool: resolves the baby and reports errors as data."""

    integration = DOMAIN
    annotations = _RECORDS

    def __init__(
        self,
        name: str,
        description: str,
        fields: dict[Any, Any],
        run: Callable[[HomeAssistant, BabyConfigEntry, dict], Awaitable[Event]] | None,
        *,
        with_baby: bool = True,
        with_time: bool = True,
    ) -> None:
        """Create a tool that runs ``run`` for the resolved baby."""
        self.name = f"{PREFIX}{name}"
        self.description = description
        schema: dict[Any, Any] = {}
        if with_baby:
            schema[_BABY] = str
        schema |= fields
        if with_time:
            schema[_TIME] = str
            schema[_MINUTES_AGO] = probatio.All(
                probatio.Coerce(int), probatio.Range(min=0, max=MAX_MINUTES_AGO)
            )
            schema[_NOTES] = str
        self.parameters = probatio.Schema(schema)
        self._run = run
        self._with_baby = with_baby

    @override
    async def async_call(
        self, hass: HomeAssistant, tool_input: ToolInput, llm_context: LLMContext
    ) -> ToolResult:
        """Validate the arguments, record and describe the entry."""
        try:
            args = self.parameters(tool_input.tool_args)
            entry = resolve_baby(hass, args.get("baby")) if self._with_baby else None
            event, entry = await self._call(hass, entry, args)
        except (ToolError, probatio.Invalid) as err:
            return ToolResult(data={"error": str(err)}, error=True)
        except HomeAssistantError as err:
            return ToolResult(data={"error": _message(err)}, error=True)
        return ToolResult(data=describe(hass, entry, event))

    async def _call(
        self, hass: HomeAssistant, entry: BabyConfigEntry | None, args: dict
    ) -> tuple[Event, BabyConfigEntry]:
        assert entry is not None
        assert self._run is not None
        return await self._run(hass, entry, args), entry


def _tracker_fields(tracker: Tracker, args: dict) -> dict[str, Any]:
    fields = {
        str(key): args[str(key)] for key in _FIELDS[tracker.key] if str(key) in args
    }
    try:
        return probatio.Schema(tracker.log_fields)(fields)
    except probatio.Invalid as err:
        raise ToolError(f"Invalid {tracker.key}: {err}") from err


def _log_tool(tracker: Tracker) -> Tool:
    async def run(hass: HomeAssistant, entry: BabyConfigEntry, args: dict) -> Event:
        return await async_log(
            hass,
            entry,
            tracker,
            _tracker_fields(tracker, args),
            when=resolve_time(args),
            notes=args.get("notes"),
        )

    return BabyTool(
        f"log_{tracker.key}", f"Record {_WHAT[tracker.key]}.", _FIELDS[tracker.key], run
    )


def _timed_tools(tracker: TimedTracker) -> list[Tool]:
    duration = probatio.Required(
        "duration_minutes", description="How long it lasted, in minutes"
    )

    async def log(hass: HomeAssistant, entry: BabyConfigEntry, args: dict) -> Event:
        return await async_log_duration(
            hass,
            entry,
            tracker,
            _tracker_fields(tracker, args),
            timedelta(minutes=args["duration_minutes"]),
            end=resolve_time(args),
            notes=args.get("notes"),
        )

    async def start(hass: HomeAssistant, entry: BabyConfigEntry, args: dict) -> Event:
        return await async_start_timer(
            hass,
            entry,
            tracker,
            _tracker_fields(tracker, args),
            when=resolve_time(args),
            notes=args.get("notes"),
        )

    async def stop(hass: HomeAssistant, entry: BabyConfigEntry, args: dict) -> Event:
        return await async_stop_timer(hass, entry, tracker, when=resolve_time(args))

    what = "breastfeed" if tracker.key == "breastfeeding" else "sleep"
    return [
        BabyTool(
            f"log_{tracker.key}",
            f"Record {_WHAT[tracker.key]}. The time is when it ended.",
            {
                duration: probatio.All(probatio.Coerce(float), probatio.Range(min=1)),
                **_FIELDS[tracker.key],
            },
            log,
        ),
        BabyTool(
            f"start_{tracker.key}",
            f"Start the {what} timer, when the baby starts to {what}.",
            _FIELDS[tracker.key],
            start,
        ),
        BabyTool(
            f"stop_{tracker.key}",
            f"Stop the running {what} timer and record the {what}.",
            {},
            stop,
        ),
    ]


def _medication_tool() -> Tool:
    async def run(hass: HomeAssistant, entry: BabyConfigEntry, args: dict) -> Event:
        try:
            medication = find_medication(entry, args["medication"])
        except HomeAssistantError as err:
            names = [med[MED_NAME] for med in medications(entry.options, active=True)]
            raise ToolError(
                f"{entry.runtime_data.name} has no active medication "
                f"{args['medication']!r}. Active: {', '.join(names) or 'none'}."
            ) from err
        return await async_log_dose(
            hass, entry, medication, when=resolve_time(args), notes=args.get("notes")
        )

    return BabyTool(
        "log_medication",
        "Record a dose of one of the baby's medications, given by its name.",
        {probatio.Required("medication", description="The medication's name"): str},
        run,
    )


class DeleteEntryTool(BabyTool):
    """Undo an entry another tool recorded."""

    annotations = _DELETES

    def __init__(self) -> None:
        """Create the undo tool."""
        super().__init__(
            "delete_entry",
            "Delete an entry recorded by mistake, by the entry_id a tool returned.",
            {probatio.Required("entry_id"): str},
            None,
            with_baby=False,
            with_time=False,
        )

    @override
    async def _call(
        self, hass: HomeAssistant, entry: BabyConfigEntry | None, args: dict
    ) -> tuple[Event, BabyConfigEntry]:
        event, entry = await event_and_entry(hass, args["entry_id"])
        await async_delete(hass, entry, event)
        return event, entry

    @override
    async def async_call(
        self, hass: HomeAssistant, tool_input: ToolInput, llm_context: LLMContext
    ) -> ToolResult:
        """Delete the entry and say what was deleted."""
        result = await super().async_call(hass, tool_input, llm_context)
        if result.error:
            return result
        data = dict(result.data)
        data["deleted"] = data.pop("recorded")
        return ToolResult(data=data)


def _prompt(babies: list[BabyConfigEntry]) -> str:
    lines = [
        "Baby Calendar records baby care entries with the baby_calendar__ tools.",
        "Babies:",
    ]
    for entry in babies:
        data = entry.runtime_data
        trackers = ", ".join(key for key in TRACKERS if key in data.trackers) or "none"
        meds = [
            f"{med[MED_NAME]} ({med[MED_DOSE]})" if med.get(MED_DOSE) else med[MED_NAME]
            for med in medications(entry.options, active=True)
        ]
        line = f"- {data.name}: trackers {trackers}"
        if meds:
            line += f"; medications {', '.join(meds)}"
        lines.append(line)
    now = dt_util.now().strftime("%Y-%m-%d %H:%M")
    lines += [
        f"Current local time: {now}.",
        "After recording, confirm in one short sentence what was recorded and when. "
        "To undo, delete the entry by the entry_id the tool returned.",
    ]
    return "\n".join(lines)


@callback
def async_get_tools(
    hass: HomeAssistant, llm_context: LLMContext, api_id: str
) -> LLMTools | None:
    """Return the tools of the trackers in use, with the babies as context."""
    if api_id != LLM_API_ASSIST:
        return None
    babies = _babies(hass)
    if not babies:
        return None
    enabled = {key for entry in babies for key in entry.runtime_data.trackers}
    tools: list[Tool] = []
    for key, tracker in TRACKERS.items():
        if key not in enabled or key not in _FIELDS:
            continue
        if isinstance(tracker, TimedTracker):
            tools.extend(_timed_tools(tracker))
        else:
            tools.append(_log_tool(tracker))
    if any(medications(entry.options, active=True) for entry in babies):
        tools.append(_medication_tool())
    tools.append(DeleteEntryTool())
    return LLMTools(tools=tools, prompt=_prompt(babies))
