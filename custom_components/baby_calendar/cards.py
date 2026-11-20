"""Serve the cards' module and add it to every dashboard."""

import hashlib
import logging
from pathlib import Path
from typing import Final

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

URL_BASE: Final = f"/{DOMAIN}/frontend"
MODULE: Final = "baby-calendar-cards.js"
FOLDER: Final = Path(__file__).parent / "frontend"


async def async_register_cards(hass: HomeAssistant) -> None:
    """Serve the bundle and load it in every dashboard.

    The URL carries a hash of the bundle, so a changed bundle is fetched
    again instead of coming from the browser's cache. The integration's
    version is not enough: an install from a commit keeps the same one.
    """
    if hass.http is None:  # pragma: no cover - http is a dependency
        return
    await hass.http.async_register_static_paths(
        [StaticPathConfig(URL_BASE, str(FOLDER), True)]
    )
    if "frontend" not in hass.config.components:
        _LOGGER.debug("The frontend is not loaded; the cards are not added")
        return
    # Imported here: the frontend is an after dependency, absent in tests.
    from homeassistant.components.frontend import add_extra_js_url  # noqa: PLC0415

    digest = await hass.async_add_executor_job(bundle_hash)
    add_extra_js_url(hass, module_url(digest))


def bundle_hash() -> str:
    """Return a short hash of the bundle's content."""
    return hashlib.sha256((FOLDER / MODULE).read_bytes()).hexdigest()[:12]


def module_url(digest: str) -> str:
    """Return the module's URL for a bundle hash."""
    return f"{URL_BASE}/{MODULE}?v={digest}"
