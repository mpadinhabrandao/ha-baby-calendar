"""Config and options flows: add, edit and restore a baby from the UI."""

import uuid
from typing import Any, override

import probatio
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BABY_ID,
    CONF_BIRTH_DATE,
    CONF_MEDICATIONS,
    CONF_NAME,
    CONF_TRACKERS,
    DOMAIN,
    MED_ACTIVE,
    MED_DOSE,
    MED_ID,
    MED_NAME,
    MED_SCHEDULE,
    MED_SINCE,
    TRACKER_KEYS,
)
from .data import async_get_store, async_run
from .schedule import SCHEDULE_INTERVAL, SCHEDULE_NONE, SCHEDULE_TIMES, parse_times
from .trackers.medication import medications

STEP_DETAILS = "details"
STEP_MEDICATIONS = "medications"
STEP_ADD_MEDICATION = "add_medication"
STEP_PICK_MEDICATION = "pick_medication"
STEP_HISTORY_RESTORE = "restore"
STEP_HISTORY_START_EMPTY = "start_empty"

ACTION = "action"
ACTION_EDIT = "edit"
ACTION_TOGGLE = "toggle"
ACTION_REMOVE = "remove"

SCHEDULE_TYPE = "schedule_type"
SCHEDULE_TIMES_TEXT = "times"
SCHEDULE_HOURS = "hours"


def _name_schema(name: str = "", birth_date: str | None = None) -> dict[Any, Any]:
    birth = (
        probatio.Optional(CONF_BIRTH_DATE, description={"suggested_value": birth_date})
        if birth_date
        else probatio.Optional(CONF_BIRTH_DATE)
    )
    return {
        probatio.Required(CONF_NAME, default=name): selector.TextSelector(),
        birth: selector.DateSelector(),
    }


def _trackers_schema(enabled: list[str]) -> dict[Any, Any]:
    return {
        probatio.Optional(CONF_TRACKERS, default=enabled): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=list(TRACKER_KEYS),
                multiple=True,
                mode=selector.SelectSelectorMode.LIST,
                translation_key=CONF_TRACKERS,
            )
        )
    }


def _clean_name(user_input: dict[str, Any]) -> str:
    return str(user_input.get(CONF_NAME, "")).strip()


def _name_in_use(hass: HomeAssistant, name: str, ignore_entry_id: str | None) -> bool:
    wanted = name.casefold()
    return any(
        entry.data.get(CONF_NAME, "").casefold() == wanted
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id != ignore_entry_id
    )


def _validate_name(
    hass: HomeAssistant, name: str, ignore_entry_id: str | None = None
) -> dict[str, str]:
    if not name:
        return {CONF_NAME: "name_required"}
    if _name_in_use(hass, name, ignore_entry_id):
        return {CONF_NAME: "name_in_use"}
    return {}


class BabyCalendarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add a baby: name and birth date, history to restore, then trackers."""

    VERSION = 1

    def __init__(self) -> None:
        """Start with nothing chosen."""
        self._name = ""
        self._birth_date: str | None = None
        self._restore_baby_id: str | None = None

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return BabyCalendarOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the name and, optionally, the birth date."""
        errors: dict[str, str] = {}
        if user_input is not None:
            name = _clean_name(user_input)
            errors = _validate_name(self.hass, name)
            if not errors:
                self._name = name
                self._birth_date = user_input.get(CONF_BIRTH_DATE) or None
                store = await async_get_store(self.hass)
                if await async_run(self.hass, store.find_removed, name):
                    return await self.async_step_history()
                return await self.async_step_trackers()
        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema(_name_schema(self._name, self._birth_date)),
            errors=errors,
        )

    async def async_step_history(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask whether to restore the history of a removed baby with this name."""
        return self.async_show_menu(
            step_id="history",
            menu_options=[STEP_HISTORY_RESTORE, STEP_HISTORY_START_EMPTY],
            description_placeholders={CONF_NAME: self._name},
        )

    async def async_step_restore(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Attach the most recently removed baby with this name."""
        store = await async_get_store(self.hass)
        removed = await async_run(self.hass, store.find_removed, self._name)
        self._restore_baby_id = removed[0].baby_id if removed else None
        return await self.async_step_trackers()

    async def async_step_start_empty(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Leave the removed history unattached and create a new baby."""
        self._restore_baby_id = None
        return await self.async_step_trackers()

    async def async_step_trackers(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose which trackers this baby uses."""
        if user_input is None:
            return self.async_show_form(
                step_id="trackers",
                data_schema=probatio.Schema(_trackers_schema(list(TRACKER_KEYS))),
            )

        # The name may have been taken while the flow was open.
        if errors := _validate_name(self.hass, self._name):
            return self.async_abort(reason=errors[CONF_NAME])

        store = await async_get_store(self.hass)
        if self._restore_baby_id is not None:
            baby_id = self._restore_baby_id
            await async_run(self.hass, store.reattach, baby_id)
            await async_run(self.hass, store.rename_baby, baby_id, self._name)
        else:
            baby_id = (
                await async_run(self.hass, store.create_baby, self._name)
            ).baby_id

        await self.async_set_unique_id(baby_id)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=self._name,
            data={CONF_BABY_ID: baby_id, CONF_NAME: self._name},
            options={
                CONF_BIRTH_DATE: self._birth_date,
                CONF_TRACKERS: _ordered(user_input.get(CONF_TRACKERS, [])),
            },
        )


class BabyCalendarOptionsFlow(OptionsFlow):
    """Edit a baby: details and trackers, or its medications."""

    def __init__(self) -> None:
        """Start with no medication picked."""
        self._med_id: str | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose what to edit."""
        return self.async_show_menu(
            step_id="init", menu_options=[STEP_DETAILS, STEP_MEDICATIONS]
        )

    async def async_step_details(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the name, birth date and trackers, and save the changes."""
        entry = self.config_entry
        errors: dict[str, str] = {}
        if user_input is not None:
            name = _clean_name(user_input)
            errors = _validate_name(self.hass, name, entry.entry_id)
            if not errors:
                if name != entry.data[CONF_NAME]:
                    self.hass.config_entries.async_update_entry(
                        entry, title=name, data={**entry.data, CONF_NAME: name}
                    )
                return self.async_create_entry(
                    data={
                        **entry.options,
                        CONF_BIRTH_DATE: user_input.get(CONF_BIRTH_DATE) or None,
                        CONF_TRACKERS: _ordered(user_input.get(CONF_TRACKERS, [])),
                    }
                )

        current = user_input or {
            CONF_NAME: entry.data[CONF_NAME],
            CONF_BIRTH_DATE: entry.options.get(CONF_BIRTH_DATE),
            CONF_TRACKERS: entry.options.get(CONF_TRACKERS, []),
        }
        return self.async_show_form(
            step_id="details",
            data_schema=probatio.Schema(
                {
                    **_name_schema(
                        str(current.get(CONF_NAME, "")), current.get(CONF_BIRTH_DATE)
                    ),
                    **_trackers_schema(list(current.get(CONF_TRACKERS, []))),
                }
            ),
            errors=errors,
        )

    async def async_step_medications(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a medication, or pick one to change."""
        options = [STEP_ADD_MEDICATION]
        if medications(self.config_entry.options):
            options.append(STEP_PICK_MEDICATION)
        return self.async_show_menu(step_id="medications", menu_options=options)

    async def async_step_add_medication(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a medication."""
        self._med_id = None
        return await self.async_step_medication(user_input)

    async def async_step_pick_medication(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick a medication and what to do with it."""
        meds = medications(self.config_entry.options)
        if user_input is not None:
            self._med_id = user_input[MED_ID]
            action = user_input[ACTION]
            if action == ACTION_EDIT:
                return await self.async_step_medication()
            if action == ACTION_TOGGLE:
                return self._save_medications(
                    [
                        _toggled(med) if med[MED_ID] == self._med_id else med
                        for med in meds
                    ]
                )
            return self._save_medications(
                [med for med in meds if med[MED_ID] != self._med_id]
            )

        inactive = _inactive_word(self.hass.config.language)
        choices = [
            selector.SelectOptionDict(
                value=med[MED_ID],
                label=med[MED_NAME]
                if med.get(MED_ACTIVE, True)
                else f"{med[MED_NAME]} ({inactive})",
            )
            for med in meds
        ]
        return self.async_show_form(
            step_id="pick_medication",
            data_schema=probatio.Schema(
                {
                    probatio.Required(MED_ID): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=choices)
                    ),
                    probatio.Required(
                        ACTION, default=ACTION_EDIT
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[ACTION_EDIT, ACTION_TOGGLE, ACTION_REMOVE],
                            mode=selector.SelectSelectorMode.LIST,
                            translation_key="medication_action",
                        )
                    ),
                }
            ),
        )

    async def async_step_medication(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enter a medication's name, dose text and schedule."""
        meds = medications(self.config_entry.options)
        existing = next((m for m in meds if m[MED_ID] == self._med_id), None)
        errors: dict[str, str] = {}
        if user_input is not None:
            medication, errors = _medication_from_input(user_input, meds, existing)
            if medication is not None:
                if existing is None:
                    return self._save_medications([*meds, medication])
                return self._save_medications(
                    [medication if m[MED_ID] == self._med_id else m for m in meds]
                )

        return self.async_show_form(
            step_id="medication",
            data_schema=probatio.Schema(
                _medication_schema(user_input or _medication_values(existing))
            ),
            errors=errors,
        )

    def _save_medications(self, meds: list[dict]) -> ConfigFlowResult:
        """Save the medication list; the entry reloads with the new entities."""
        return self.async_create_entry(
            data={**self.config_entry.options, CONF_MEDICATIONS: meds}
        )


def _inactive_word(language: str) -> str:
    return "inativo" if language.startswith("pt") else "inactive"


def _medication_values(medication: dict | None) -> dict[str, Any]:
    if medication is None:
        return {SCHEDULE_TYPE: SCHEDULE_NONE}
    schedule = medication.get(MED_SCHEDULE, {})
    return {
        MED_NAME: medication[MED_NAME],
        MED_DOSE: medication.get(MED_DOSE) or "",
        SCHEDULE_TYPE: schedule.get("type", SCHEDULE_NONE),
        SCHEDULE_TIMES_TEXT: ", ".join(schedule.get("times", [])),
        SCHEDULE_HOURS: schedule.get("hours"),
    }


def _suggested(key: str, values: dict[str, Any], required: bool = False) -> Any:
    value = values.get(key)
    marker = probatio.Required if required else probatio.Optional
    if value in (None, ""):
        return marker(key)
    return marker(key, description={"suggested_value": value})


def _medication_schema(values: dict[str, Any]) -> dict[Any, Any]:
    return {
        _suggested(MED_NAME, values, required=True): selector.TextSelector(),
        _suggested(MED_DOSE, values): selector.TextSelector(),
        probatio.Required(
            SCHEDULE_TYPE, default=values.get(SCHEDULE_TYPE) or SCHEDULE_NONE
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[SCHEDULE_NONE, SCHEDULE_TIMES, SCHEDULE_INTERVAL],
                mode=selector.SelectSelectorMode.LIST,
                translation_key=SCHEDULE_TYPE,
            )
        ),
        _suggested(SCHEDULE_TIMES_TEXT, values): selector.TextSelector(),
        _suggested(SCHEDULE_HOURS, values): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0, step="any", mode=selector.NumberSelectorMode.BOX
            )
        ),
    }


def _medication_from_input(
    user_input: dict[str, Any], meds: list[dict], existing: dict | None
) -> tuple[dict | None, dict[str, str]]:
    """Validate the form and return the medication to save, or the errors."""
    name = str(user_input.get(MED_NAME, "")).strip()
    if not name:
        return None, {MED_NAME: "name_required"}
    own_id = existing[MED_ID] if existing else None
    if any(
        m[MED_NAME].casefold() == name.casefold() and m[MED_ID] != own_id for m in meds
    ):
        return None, {MED_NAME: "medication_in_use"}

    kind = user_input.get(SCHEDULE_TYPE, SCHEDULE_NONE)
    schedule: dict[str, Any] = {"type": SCHEDULE_NONE}
    if kind == SCHEDULE_TIMES:
        text = str(user_input.get(SCHEDULE_TIMES_TEXT) or "")
        if not text.strip():
            return None, {SCHEDULE_TIMES_TEXT: "times_required"}
        try:
            schedule = {"type": SCHEDULE_TIMES, "times": parse_times(text)}
        except ValueError:
            return None, {SCHEDULE_TIMES_TEXT: "time_invalid"}
    elif kind == SCHEDULE_INTERVAL:
        hours = user_input.get(SCHEDULE_HOURS)
        if hours is None or float(hours) <= 0:
            return None, {SCHEDULE_HOURS: "hours_invalid"}
        schedule = {"type": SCHEDULE_INTERVAL, "hours": float(hours)}

    dose = str(user_input.get(MED_DOSE) or "").strip() or None
    since = existing.get(MED_SINCE) if existing else None
    if since is None or schedule != existing.get(MED_SCHEDULE):
        since = _now_ts()
    return {
        MED_ID: own_id or uuid.uuid4().hex,
        MED_NAME: name,
        MED_DOSE: dose,
        MED_ACTIVE: existing.get(MED_ACTIVE, True) if existing else True,
        MED_SCHEDULE: schedule,
        MED_SINCE: since,
    }, {}


def _toggled(medication: dict) -> dict:
    """Deactivate or reactivate; a reactivated schedule starts now."""
    if medication.get(MED_ACTIVE, True):
        return {**medication, MED_ACTIVE: False}
    return {**medication, MED_ACTIVE: True, MED_SINCE: _now_ts()}


def _now_ts() -> int:
    return int(dt_util.utcnow().timestamp())


def _ordered(trackers: list[str]) -> list[str]:
    """Keep known trackers only, in the integration's own order."""
    return [key for key in TRACKER_KEYS if key in trackers]
