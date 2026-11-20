"""Tests for what the integration provides to its cards."""

from http import HTTPStatus
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.baby_calendar.cards import MODULE, URL_BASE, module_url
from custom_components.baby_calendar.const import CONF_BABY_ID, DOMAIN

from .conftest import add_baby
from .test_medication import add_medication, device_id, med_by_name


async def subscribe(hass: HomeAssistant, client) -> list:
    """Subscribe to the babies and return the first message's babies."""
    await client.send_json({"id": 1, "type": f"{DOMAIN}/subscribe_babies"})
    result = await client.receive_json()
    assert result["success"]
    event = await client.receive_json()
    return event["event"]["babies"]


async def next_babies(client) -> list:
    """Return the babies of the next message."""
    return (await client.receive_json())["event"]["babies"]


async def test_babies_message(hass: HomeAssistant, hass_ws_client) -> None:
    """Each baby with its device, trackers, medications and entity ids."""
    entry = await add_baby(hass, "Alice")
    await add_medication(hass, entry, name="Vitamin D", dose="1 drop")
    client = await hass_ws_client(hass)

    [baby] = await subscribe(hass, client)

    assert baby["name"] == "Alice"
    assert baby["entry_id"] == entry.entry_id
    assert baby["device_id"] == device_id(hass, entry)
    assert "diaper" in baby["trackers"]
    assert baby["entities"]["diaper_wet"].startswith("button.")
    assert baby["entities"]["stool_prompt"].startswith("binary_sensor.")
    assert baby["entities"]["breastfeeding_last"].startswith("sensor.")
    [med] = baby["medications"]
    assert (med["name"], med["dose"]) == ("Vitamin D", "1 drop")
    assert med["id"] == med_by_name(entry, "Vitamin D")["id"]
    assert set(med["entities"]) == {"take", "last_dose", "doses_today"}
    assert not any(key.startswith("med_") for key in baby["entities"])


async def test_non_administrator(
    hass: HomeAssistant, hass_ws_client, hass_read_only_access_token: str
) -> None:
    """A user who is not an administrator receives the babies too."""
    await add_baby(hass, "Alice")
    client = await hass_ws_client(hass, hass_read_only_access_token)

    babies = await subscribe(hass, client)

    assert [baby["name"] for baby in babies] == ["Alice"]


async def test_medication_added(hass: HomeAssistant, hass_ws_client) -> None:
    """Adding a medication sends the baby again with it."""
    entry = await add_baby(hass, "Alice")
    client = await hass_ws_client(hass)
    await subscribe(hass, client)

    await add_medication(hass, entry, name="Iron")

    # The reload unloads the baby, then sets it up again: the last message
    # has the baby with its new medication.
    messages = [await next_babies(client)]
    while messages[-1] == []:
        messages.append(await next_babies(client))
    [baby] = messages[-1]
    assert [med["name"] for med in baby["medications"]] == ["Iron"]


async def test_baby_removed(hass: HomeAssistant, hass_ws_client) -> None:
    """Removing a baby sends the babies without it."""
    alice = await add_baby(hass, "Alice")
    await add_baby(hass, "Bruno")
    client = await hass_ws_client(hass)
    assert len(await subscribe(hass, client)) == 2

    await hass.config_entries.async_remove(alice.entry_id)
    await hass.async_block_till_done()

    babies = await next_babies(client)
    assert [baby["name"] for baby in babies] == ["Bruno"]
    assert alice.data[CONF_BABY_ID] not in str(babies)


async def test_module_served(hass: HomeAssistant, hass_client) -> None:
    """The bundle is served under the integration's path."""
    await add_baby(hass)
    client = await hass_client()

    response = await client.get(f"{URL_BASE}/{MODULE}")

    assert response.status == HTTPStatus.OK


async def test_module_added_to_dashboards(hass: HomeAssistant) -> None:
    """With the frontend loaded, the module URL carrying the version is added."""
    hass.config.components.add("frontend")
    with patch(
        "homeassistant.components.frontend.add_extra_js_url"
    ) as add_extra_js_url:
        assert await async_setup_component(hass, DOMAIN, {})

    [(_, url)] = [call.args for call in add_extra_js_url.call_args_list]
    assert url.startswith(f"{URL_BASE}/{MODULE}?v=")
    assert url == module_url(url.rpartition("=")[2])
    assert url.rpartition("=")[2] != ""
