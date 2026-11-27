"""Tests for the tools offered to LLM conversation agents."""

from typing import Any

import pytest
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import llm
from homeassistant.setup import async_setup_component

from custom_components.baby_calendar.data import async_get_store
from custom_components.baby_calendar.llm import async_get_tools
from custom_components.baby_calendar.services import now_ts

from .conftest import add_baby
from .test_diaper import value
from .test_medication import add_medication

PREFIX = "baby_calendar__"


def context() -> llm.LLMContext:
    """Return the context of a request from a conversation agent."""
    return llm.LLMContext(
        platform="test",
        context=Context(),
        language="en",
        assistant="conversation",
        device_id=None,
    )


async def api(hass: HomeAssistant) -> llm.APIInstance:
    """Return the Assist API as an agent sees it."""
    await async_setup_component(hass, "homeassistant", {})
    await async_setup_component(hass, "llm", {})
    return await llm.async_get_api(hass, llm.LLM_API_ASSIST, context())


async def tool_names(hass: HomeAssistant) -> set[str]:
    """Return the names of this integration's tools, without the prefix."""
    instance = await api(hass)
    return {
        tool.name.removeprefix(PREFIX)
        for tool in instance.tools
        if tool.name.startswith(PREFIX)
    }


async def call(hass: HomeAssistant, name: str, **args: Any) -> llm.ToolResult:
    """Call one of this integration's tools as an agent does."""
    instance = await api(hass)
    return await instance.async_call_tool(
        llm.ToolInput(tool_name=f"{PREFIX}{name}", tool_args=args)
    )


# ------------------------------------------------------------- recording


async def test_bottle(hass: HomeAssistant) -> None:
    """A bottle is recorded now and described as the calendar titles it."""
    entry = await add_baby(hass)

    result = await call(hass, "log_bottle", amount=90, content="formula")

    assert not result.error
    assert result.data["recorded"] == "🍼 Bottle 90 ml formula"
    assert result.data["baby"] == "Alice"
    assert result.data["entry_id"]
    assert value(hass, entry, "sensor", "bottle_count_today") == "1"


async def test_minutes_ago(hass: HomeAssistant) -> None:
    """Minutes ago sets the time of the entry."""
    await add_baby(hass)

    result = await call(hass, "log_diaper", content="wet", minutes_ago=10)

    event = (await async_get_store(hass)).get_event(result.data["entry_id"])
    assert abs(event.start_ts - (now_ts() - 600)) <= 2


async def test_exact_time(hass: HomeAssistant) -> None:
    """A local date and time sets the time of the entry."""
    await add_baby(hass)
    result = await call(hass, "log_temperature", value=37.2, time="2026-01-02 09:15")
    assert not result.error, result.data
    assert result.data["time"] == "09:15"


async def test_both_time_forms(hass: HomeAssistant) -> None:
    """A time and minutes ago together are refused."""
    entry = await add_baby(hass)

    result = await call(
        hass, "log_diaper", content="wet", minutes_ago=5, time="2026-01-02 09:15"
    )

    assert result.error
    assert value(hass, entry, "sensor", "diaper_changes_today") == "0"


async def test_sleep_timer(hass: HomeAssistant) -> None:
    """Start and stop record a sleep, as the sleep switch does."""
    entry = await add_baby(hass)

    started = await call(hass, "start_sleep", minutes_ago=30)
    assert started.data["recorded"] == "😴 Sleep in progress"
    assert value(hass, entry, "switch", "sleep_timer") == "on"

    stopped = await call(hass, "stop_sleep")

    assert stopped.data["recorded"] == "😴 Sleep 30 min"
    assert value(hass, entry, "switch", "sleep_timer") == "off"


async def test_finished_breastfeed(hass: HomeAssistant) -> None:
    """A breastfeed of a known duration ends now by default."""
    await add_baby(hass)
    result = await call(hass, "log_breastfeeding", duration_minutes=15, side="left")
    assert result.data["recorded"] == "🤱 Breastfeeding left 15 min"


async def test_timer_already_running(hass: HomeAssistant) -> None:
    """Starting a running timer explains why, instead of raising."""
    await add_baby(hass)
    await call(hass, "start_sleep")
    result = await call(hass, "start_sleep")
    assert result.error
    assert result.data["error"]


async def test_dose_by_name(hass: HomeAssistant) -> None:
    """A dose is recorded by the medication's name, in any case."""
    entry = await add_baby(hass)
    await add_medication(hass, entry, name="Paracetamol", dose="5 ml")

    result = await call(hass, "log_medication", medication="paracetamol")

    assert not result.error, result.data
    assert result.data["recorded"] == "💊 Paracetamol"


async def test_unknown_medication(hass: HomeAssistant) -> None:
    """An unknown medication names the active ones."""
    entry = await add_baby(hass)
    await add_medication(hass, entry, name="Paracetamol")
    result = await call(hass, "log_medication", medication="Iron")
    assert result.error
    assert "Paracetamol" in result.data["error"]


async def test_out_of_range(hass: HomeAssistant) -> None:
    """A reading the tracker refuses is explained, and nothing is recorded."""
    await add_baby(hass)
    result = await call(hass, "log_temperature", value=55)
    assert result.error
    assert result.data["error"]


# ----------------------------------------------------------- the baby


async def test_name_left_out(hass: HomeAssistant) -> None:
    """With one baby the name can be left out."""
    await add_baby(hass, "Duarte")
    result = await call(hass, "log_diaper", content="dirty")
    assert result.data["baby"] == "Duarte"


async def test_name_without_accents(hass: HomeAssistant) -> None:
    """A name matches without regard to case or accents."""
    await add_baby(hass, "Inês")
    await add_baby(hass, "Bruno")
    result = await call(hass, "log_diaper", baby="ines", content="wet")
    assert result.data["baby"] == "Inês"


async def test_two_babies_no_name(hass: HomeAssistant) -> None:
    """With two babies a name is needed, and the error names them."""
    await add_baby(hass, "Alice")
    await add_baby(hass, "Bruno")

    result = await call(hass, "log_diaper", content="wet")

    assert result.error
    assert "Alice" in result.data["error"]
    assert "Bruno" in result.data["error"]


async def test_unknown_baby(hass: HomeAssistant) -> None:
    """An unknown name is refused."""
    await add_baby(hass, "Alice")
    result = await call(hass, "log_diaper", baby="Carla", content="wet")
    assert result.error
    assert "Alice" in result.data["error"]


# ------------------------------------------------------- which tools


async def test_diapers_only(hass: HomeAssistant) -> None:
    """Only the diaper tool and the undo tool for a diapers-only baby."""
    await add_baby(hass, trackers=["diaper"])
    assert await tool_names(hass) == {"log_diaper", "delete_entry"}


async def test_every_tracker(hass: HomeAssistant) -> None:
    """Every tracker's tools, and the dose tool with a medication."""
    entry = await add_baby(hass)
    await add_medication(hass, entry, name="Iron")
    assert await tool_names(hass) == {
        "log_diaper",
        "log_bottle",
        "log_breastfeeding",
        "start_breastfeeding",
        "stop_breastfeeding",
        "log_sleep",
        "start_sleep",
        "stop_sleep",
        "log_solids",
        "log_pumping",
        "log_weight",
        "log_length",
        "log_temperature",
        "log_medication",
        "delete_entry",
    }


async def test_no_babies(hass: HomeAssistant) -> None:
    """No tools without a baby, and none for other APIs."""
    assert await tool_names(hass) == set()
    await add_baby(hass)
    assert async_get_tools(hass, context(), "other_api") is None


async def test_tracker_not_enabled_for_the_baby(hass: HomeAssistant) -> None:
    """A tool offered for one baby is refused for a baby without it."""
    await add_baby(hass, "Alice", trackers=["bottle"])
    bruno = await add_baby(hass, "Bruno", trackers=["diaper"])

    result = await call(hass, "log_bottle", baby="Bruno", amount=60)

    assert result.error
    assert value(hass, bruno, "sensor", "diaper_changes_today") == "0"


@pytest.mark.parametrize(
    ("name", "args"),
    [
        ("log_diaper", {"content": "dirty", "stool": "soft"}),
        ("log_bottle", {"amount": 120, "content": "breast_milk"}),
        ("log_breastfeeding", {"duration_minutes": 10, "side": "right"}),
        ("log_sleep", {"duration_minutes": 45}),
        ("log_solids", {"notes": "banana"}),
        ("log_pumping", {"amount": 80, "side": "both"}),
        ("log_weight", {"value": 4200}),
        ("log_length", {"value": 52.5}),
        ("log_temperature", {"value": 37.2}),
    ],
)
async def test_each_log_tool(hass: HomeAssistant, name: str, args: dict) -> None:
    """Each log tool records with valid fields."""
    await add_baby(hass)
    result = await call(hass, name, **args)
    assert not result.error, result.data


# ------------------------------------------------------ prompt and undo


async def test_prompt(hass: HomeAssistant) -> None:
    """The prompt lists the babies, their trackers, medications and the time."""
    entry = await add_baby(hass, "Duarte", trackers=["diaper", "bottle"])
    await add_medication(hass, entry, name="Vitamina D", dose="1 gota")

    prompt = (await api(hass)).api_prompt

    assert "Duarte: trackers diaper, bottle" in prompt
    assert "Vitamina D (1 gota)" in prompt
    assert "Current local time:" in prompt


async def test_undo(hass: HomeAssistant) -> None:
    """The undo tool deletes the entry by the id another tool returned."""
    entry = await add_baby(hass)
    logged = await call(hass, "log_bottle", amount=90)

    result = await call(hass, "delete_entry", entry_id=logged.data["entry_id"])

    assert not result.error, result.data
    assert result.data["deleted"] == "🍼 Bottle 90 ml"
    assert value(hass, entry, "sensor", "bottle_count_today") == "0"


async def test_undo_unknown(hass: HomeAssistant) -> None:
    """An unknown entry id is refused."""
    await add_baby(hass)
    result = await call(hass, "delete_entry", entry_id="nope")
    assert result.error
