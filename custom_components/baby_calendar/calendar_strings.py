"""Words used in calendar titles, by language.

Titles are built in Python, where the translation files do not reach, so
their words live here. Labels use the same wording as the entities.
"""

from typing import Final

FALLBACK: Final = "en"

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "diaper_wet": "Wet diaper",
        "diaper_dirty": "Dirty diaper",
        "diaper_both": "Wet and dirty diaper",
        "stool_normal": "normal",
        "stool_soft": "soft",
        "stool_hard": "hard",
        "stool_diarrhea": "diarrhea",
        "bottle": "Bottle",
        "bottle_formula": "formula",
        "bottle_breast_milk": "breast milk",
        "breastfeeding": "Breastfeeding",
        "side_left": "left",
        "side_right": "right",
        "sleep": "Sleep",
        "solids": "Solids",
        "in_progress": "in progress",
    },
    "pt": {
        "diaper_wet": "Fralda com xixi",
        "diaper_dirty": "Fralda com cocó",
        "diaper_both": "Fralda com xixi e cocó",
        "stool_normal": "normal",
        "stool_soft": "mole",
        "stool_hard": "duro",
        "stool_diarrhea": "diarreia",
        "bottle": "Biberão",
        "bottle_formula": "fórmula",
        "bottle_breast_milk": "leite materno",
        "breastfeeding": "Mamada",
        "side_left": "esquerda",
        "side_right": "direita",
        "sleep": "Sono",
        "solids": "Sólidos",
        "in_progress": "a decorrer",
    },
}


def words(language: str) -> dict[str, str]:
    """Return the words of a language, such as "pt" or "pt-BR", or English."""
    base = language.split("-")[0].lower() if language else FALLBACK
    return STRINGS.get(base, STRINGS[FALLBACK])


def format_duration(seconds: int) -> str:
    """Format a duration as "45 min", "2 h" or "1 h 20 min"."""
    minutes = round(seconds / 60)
    hours, minutes = divmod(minutes, 60)
    if not hours:
        return f"{minutes} min"
    if not minutes:
        return f"{hours} h"
    return f"{hours} h {minutes} min"


def format_amount(amount: float, language: str) -> str:
    """Format an amount without a needless ".0", with the decimal comma in pt."""
    text = f"{amount:g}"
    return text.replace(".", ",") if language.startswith("pt") else text
