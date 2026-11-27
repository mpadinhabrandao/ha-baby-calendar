"""Tests for the sentence files written for the built-in agent."""

import logging

import pytest
import yaml
from homeassistant.core import HomeAssistant

from custom_components.baby_calendar.sentences import HEADER, sentence_path

from .test_intents import agent, baby, events, say, sentences_ready  # noqa: F401
from .test_medication import add_medication


def read(hass: HomeAssistant, language: str) -> dict:
    """Return a written sentence file, after checking its header."""
    content = sentence_path(hass, language).read_text(encoding="utf-8")
    assert content.startswith(f"{HEADER}\n")
    return yaml.safe_load(content)


def baby_names(hass: HomeAssistant, language: str) -> set[str]:
    """Return the baby names a file lists."""
    return {value["in"] for value in read(hass, language)["lists"]["baby"]["values"]}


@pytest.mark.usefixtures("agent")
async def test_written_for_each_language(hass: HomeAssistant) -> None:
    """Both languages get a file with the babies, accentless names too."""
    await baby(hass, "Inês")

    assert baby_names(hass, "pt") == {"Inês", "ines"}
    assert baby_names(hass, "en") == {"Inês", "ines"}
    assert "BabyCalendarLogMedication" not in read(hass, "pt")["intents"]


@pytest.mark.usefixtures("agent")
async def test_new_baby(hass: HomeAssistant) -> None:
    """Adding a baby rewrites the files and its name works at once."""
    await baby(hass, "Alice")
    bruno = await baby(hass, "Bruno")

    assert baby_names(hass, "pt") == {"Alice", "Bruno"}
    await say(hass, "Bruno adormeceu")
    assert len(await events(hass, bruno)) == 1


@pytest.mark.usefixtures("agent")
async def test_medications_listed(hass: HomeAssistant) -> None:
    """Active medications are listed, with their baby."""
    entry = await baby(hass)
    await add_medication(hass, entry, name="Vitamina D")
    await sentences_ready(hass)

    values = read(hass, "pt")["lists"]["medication"]["values"]

    assert {"in": "Vitamina D", "out": f"{entry.entry_id}:Vitamina D"} in values


@pytest.mark.usefixtures("agent")
async def test_a_file_of_the_user(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    """A file without the header is left alone, with one warning."""
    path = sentence_path(hass, "pt")
    path.parent.mkdir(parents=True)
    path.write_text("language: pt\nintents: {}\n", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        await baby(hass, "Alice")
        await baby(hass, "Bruno")

    assert path.read_text(encoding="utf-8") == "language: pt\nintents: {}\n"
    assert caplog.text.count("not written by Baby Calendar") == 1
    assert baby_names(hass, "en") == {"Alice", "Bruno"}


@pytest.mark.usefixtures("agent")
async def test_last_baby_removed(hass: HomeAssistant) -> None:
    """Removing the last baby deletes the files; the first keeps them."""
    alice = await baby(hass, "Alice")
    bruno = await baby(hass, "Bruno")

    await hass.config_entries.async_remove(alice.entry_id)
    await sentences_ready(hass)
    assert baby_names(hass, "pt") == {"Bruno"}

    await hass.config_entries.async_remove(bruno.entry_id)
    await sentences_ready(hass)
    assert not sentence_path(hass, "pt").exists()
    assert not sentence_path(hass, "en").exists()


@pytest.mark.usefixtures("agent")
async def test_user_file_survives_removal(hass: HomeAssistant) -> None:
    """Removing the last baby does not delete a file of the user's."""
    path = sentence_path(hass, "en")
    path.parent.mkdir(parents=True)
    path.write_text("language: en\nintents: {}\n", encoding="utf-8")
    entry = await baby(hass)

    await hass.config_entries.async_remove(entry.entry_id)
    await sentences_ready(hass)

    assert path.exists()
