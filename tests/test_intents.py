"""Tests for the built-in agent's sentences and intents."""

from datetime import timedelta

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Context, HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.baby_calendar.data import async_get_store
from custom_components.baby_calendar.intents import parse_number
from custom_components.baby_calendar.services import now_ts
from custom_components.baby_calendar.voice import VoiceError

from .conftest import add_baby
from .test_diaper import value
from .test_medication import add_medication


async def sentences_ready(hass: HomeAssistant) -> None:
    """Let the debounced sentence files be written and the agent reloaded."""
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=2))
    await hass.async_block_till_done()


@pytest.fixture
async def agent(hass: HomeAssistant) -> None:
    """Set up the built-in conversation agent."""
    assert await async_setup_component(hass, "homeassistant", {})
    assert await async_setup_component(hass, "conversation", {})


async def baby(hass: HomeAssistant, name: str = "Alice", **kwargs) -> ConfigEntry:
    """Add a baby and wait for the sentences."""
    entry = await add_baby(hass, name, **kwargs)
    await sentences_ready(hass)
    return entry


async def say(hass: HomeAssistant, sentence: str, language: str = "pt") -> str:
    """Say a sentence to the built-in agent and return its spoken reply."""
    result = await conversation.async_converse(
        hass, sentence, None, Context(), language=language
    )
    return result.response.speech["plain"]["speech"]


async def events(hass: HomeAssistant, entry: ConfigEntry) -> list:
    """Return the baby's events, oldest first."""
    store = await async_get_store(hass)
    return store.list_events(entry.data["baby_id"], 0, now_ts() + 60)


# ----------------------------------------------------------- recording


@pytest.mark.usefixtures("agent")
async def test_bottle_in_portuguese(hass: HomeAssistant) -> None:
    """A bottle with its amount and content, now, with a spoken reply."""
    entry = await baby(hass)

    reply = await say(hass, "bebeu um biberão de 90 ml de leite artificial")

    [event] = await events(hass, entry)
    assert (event.tracker, event.amount, event.kind) == ("bottle", 90, "formula")
    assert reply.startswith("Registei Bottle 90 ml formula para Alice às ")


@pytest.mark.usefixtures("agent")
async def test_diaper_minutes_ago(hass: HomeAssistant) -> None:
    """Minutes ago sets the time."""
    entry = await baby(hass)

    await say(hass, "mudei uma fralda molhada há 10 minutos")

    [event] = await events(hass, entry)
    assert (event.tracker, event.kind) == ("diaper", "wet")
    assert abs(event.start_ts - (now_ts() - 600)) <= 2


@pytest.mark.usefixtures("agent")
@pytest.mark.parametrize("sentence", ["tem 37,2 graus", "a temperatura é 37.2"])
async def test_temperature(hass: HomeAssistant, sentence: str) -> None:
    """Decimals with a comma or a point."""
    entry = await baby(hass)
    await say(hass, sentence)
    [event] = await events(hass, entry)
    assert event.data.get("value", event.amount) == 37.2


@pytest.mark.usefixtures("agent")
async def test_weight_in_kilos(hass: HomeAssistant) -> None:
    """A weight in kilos is recorded in grams."""
    entry = await baby(hass)
    await say(hass, "pesa 4,2 quilos")
    [event] = await events(hass, entry)
    assert event.data.get("value", event.amount) == 4200


@pytest.mark.usefixtures("agent")
async def test_sleep_in_english(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Fell asleep starts the timer, woke up stops it."""
    entry = await baby(hass)

    await say(hass, "Alice fell asleep", "en")
    assert value(hass, entry, "switch", "sleep_timer") == "on"
    freezer.tick(timedelta(minutes=40))
    reply = await say(hass, "Alice woke up", "en")

    assert value(hass, entry, "switch", "sleep_timer") == "off"
    assert reply.startswith("Recorded Sleep 40 min for Alice, from ")


@pytest.mark.usefixtures("agent")
async def test_breastfeeding(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Start and stop the breastfeeding timer, with a side."""
    entry = await baby(hass)
    await say(hass, "começa a mama esquerda")
    freezer.tick(timedelta(minutes=12))
    await say(hass, "acabou a mama")
    [event] = await events(hass, entry)
    assert (event.tracker, event.kind) == ("breastfeeding", "left")
    assert event.end_ts - event.start_ts == 12 * 60


@pytest.mark.usefixtures("agent")
async def test_dose_by_name(hass: HomeAssistant) -> None:
    """A dose of a medication named in the sentence."""
    entry = await baby(hass)
    await add_medication(hass, entry, name="Vitamina D")
    await sentences_ready(hass)

    await say(hass, "dei a vitamina D")

    [event] = await events(hass, entry)
    assert event.tracker == "medication"


@pytest.mark.usefixtures("agent")
async def test_named_baby(hass: HomeAssistant) -> None:
    """With two babies the sentence names one."""
    await baby(hass, "Alice")
    bruno = await baby(hass, "Bruno")

    await say(hass, "o Bruno adormeceu")

    assert value(hass, bruno, "switch", "sleep_timer") == "on"


# --------------------------------------------------------------- replies


@pytest.mark.usefixtures("agent")
async def test_two_babies_unnamed(hass: HomeAssistant) -> None:
    """Without a name and with two babies, the reply asks which."""
    alice = await baby(hass, "Alice")
    await baby(hass, "Bruno")

    reply = await say(hass, "mudei uma fralda suja")

    assert "Alice" in reply
    assert "Bruno" in reply
    assert await events(hass, alice) == []


@pytest.mark.usefixtures("agent")
async def test_tracker_not_enabled(hass: HomeAssistant) -> None:
    """A tracker the baby does not have is refused with a reply."""
    entry = await baby(hass, trackers=["diaper"])
    reply = await say(hass, "comeu sólidos")
    assert reply == "O registo de sólidos não está ativo para Alice."
    assert await events(hass, entry) == []


@pytest.mark.usefixtures("agent")
async def test_built_in_sentences_still_work(hass: HomeAssistant) -> None:
    """A built-in sentence is not taken by ours."""
    await baby(hass)
    result = await conversation.async_converse(
        hass, "que horas são", None, Context(), language="pt"
    )
    assert result.response.intent is not None
    assert not result.response.intent.intent_type.startswith("BabyCalendar")


# ------------------------------------------------------------------ undo


@pytest.mark.usefixtures("agent")
async def test_undo(hass: HomeAssistant) -> None:
    """Undo deletes the last voice entry."""
    entry = await baby(hass)
    await say(hass, "bebeu 60 ml")

    reply = await say(hass, "desfaz o último registo")

    assert await events(hass, entry) == []
    assert reply.startswith("Apaguei Bottle 60 ml de Alice")


@pytest.mark.usefixtures("agent")
async def test_undo_too_late(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A voice entry older than 10 minutes is not undone."""
    entry = await baby(hass)
    await say(hass, "bebeu 60 ml")
    freezer.tick(timedelta(minutes=30))

    reply = await say(hass, "desfaz o último registo")

    assert len(await events(hass, entry)) == 1
    assert reply == "Não há nenhum registo recente para desfazer."


def test_parse_number() -> None:
    """Digits with a comma or a point, and nothing else."""
    assert parse_number("37,2", "pt") == 37.2
    assert parse_number("37.2", "en") == 37.2
    assert parse_number("37 vírgula 2", "pt") == 37.2
    assert parse_number(90, "pt") == 90
    with pytest.raises(VoiceError):
        parse_number("muito", "pt")


@pytest.mark.usefixtures("agent")
@pytest.mark.parametrize(
    ("sentence", "language"),
    [
        ("She drank 90 ml of formula", "en"),
        ("Changed a wet diaper", "en"),
        ("I pumped 80 ml from the left side", "en"),
        ("Weighs 4.2 kilos", "en"),
        ("Is 52 cm long", "en"),
        ("Ate solids", "en"),
        ("ela bebeu 60 ml", "pt"),
        ("fralda suja mole", "pt"),
        ("tirei 80 ml de leite do lado esquerdo", "pt"),
        ("pesa 4200 gramas", "pt"),
        ("mede 52 centímetros", "pt"),
        ("comeu sólidos", "pt"),
    ],
)
async def test_readme_sentences(
    hass: HomeAssistant, sentence: str, language: str
) -> None:
    """The README's example sentences each record an entry."""
    entry = await baby(hass)
    await say(hass, sentence, language)
    assert len(await events(hass, entry)) == 1


@pytest.mark.usefixtures("agent")
@pytest.mark.parametrize(
    ("start", "stop", "language"),
    [
        ("comecei a dar de mamar na direita", "parei de dar de mamar", "pt"),
        ("estou a dar de mamar", "terminei de dar de mamar", "pt"),
        ("a dar de mamar na esquerda", "já mamou", "pt"),
        ("começa a mama", "parei a mamada", "pt"),
        ("I started feeding on the left side", "stopped feeding", "en"),
        ("feeding on the right", "done feeding", "en"),
        ("started feeding", "finished feeding", "en"),
    ],
)
async def test_timer_phrasings(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    start: str,
    stop: str,
    language: str,
) -> None:
    """Common ways of saying a feed started and stopped."""
    entry = await baby(hass)

    await say(hass, start, language)
    assert value(hass, entry, "switch", "breastfeeding_timer") == "on"
    freezer.tick(timedelta(minutes=30))
    await say(hass, stop, language)

    assert value(hass, entry, "switch", "breastfeeding_timer") == "off"
    [event] = await events(hass, entry)
    assert event.end_ts - event.start_ts == 30 * 60


@pytest.mark.usefixtures("agent")
async def test_side_from_phrasing(hass: HomeAssistant) -> None:
    """The side said is the side recorded."""
    entry = await baby(hass)
    await say(hass, "comecei a dar de mamar na direita")
    [event] = await events(hass, entry)
    assert event.kind == "right"


@pytest.mark.usefixtures("agent")
async def test_stopped_timer_reply(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A stopped timer's reply says from when to when."""
    freezer.move_to(dt_util.as_utc(dt_util.now().replace(hour=23, minute=24, second=0)))
    await baby(hass)
    await say(hass, "comecei a dar de mamar na direita")
    freezer.tick(timedelta(minutes=30))

    reply = await say(hass, "parei de dar de mamar")

    assert reply.endswith(", das 23:24 às 23:54.")


@pytest.mark.usefixtures("agent")
@pytest.mark.parametrize(
    "sentence", ["acorda", "que horas são", "liga a luz da cozinha"]
)
async def test_timer_phrasings_leave_built_ins(
    hass: HomeAssistant, sentence: str
) -> None:
    """Our phrasings do not take built-in sentences."""
    entry = await baby(hass)
    result = await conversation.async_converse(
        hass, sentence, None, Context(), language="pt"
    )
    intent = result.response.intent
    assert intent is None or not intent.intent_type.startswith("BabyCalendar")
    assert await events(hass, entry) == []
