"""Shared fixtures for the Baby Calendar tests."""

from pathlib import Path
from typing import Any

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.baby_calendar.const import (
    CONF_BIRTH_DATE,
    CONF_NAME,
    CONF_TRACKERS,
    DOMAIN,
    TRACKER_KEYS,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Let Home Assistant load the integration from custom_components."""


@pytest.fixture(autouse=True)
def isolated_config_dir(hass: HomeAssistant, tmp_path: Path) -> Path:
    """Give every test its own config directory, so each store starts empty."""
    hass.config.config_dir = str(tmp_path)
    return tmp_path


async def add_baby(
    hass: HomeAssistant,
    name: str = "Alice",
    trackers: list[str] | None = None,
    birth_date: str | None = None,
    history: str | None = None,
) -> ConfigEntry:
    """Add a baby through the config flow and return its config entry.

    ``history`` answers the restore question when a removed baby matches.
    """
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    user_input: dict[str, Any] = {CONF_NAME: name}
    if birth_date:
        user_input[CONF_BIRTH_DATE] = birth_date
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input
    )
    if result["type"] is FlowResultType.MENU:
        assert history is not None, "a removed baby matched; say what to do"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"next_step_id": history}
        )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "trackers"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_TRACKERS: list(TRACKER_KEYS) if trackers is None else trackers},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    return result["result"]
