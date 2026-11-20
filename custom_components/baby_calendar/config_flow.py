"""Config flow for Baby Calendar."""

from homeassistant.config_entries import ConfigFlow

from .const import DOMAIN


class BabyCalendarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add a baby from the UI."""

    VERSION = 1
