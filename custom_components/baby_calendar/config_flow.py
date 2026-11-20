"""Config and options flows: add, edit and restore a baby from the UI."""

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

from .const import (
    CONF_BABY_ID,
    CONF_BIRTH_DATE,
    CONF_NAME,
    CONF_TRACKERS,
    DOMAIN,
    TRACKER_KEYS,
)
from .data import async_get_store, async_run

STEP_HISTORY_RESTORE = "restore"
STEP_HISTORY_START_EMPTY = "start_empty"


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
    """Edit a baby's name, birth date and trackers."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the current values and save the changes."""
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
            step_id="init",
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


def _ordered(trackers: list[str]) -> list[str]:
    """Keep known trackers only, in the integration's own order."""
    return [key for key in TRACKER_KEYS if key in trackers]
