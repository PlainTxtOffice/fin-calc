"""Parse explicit setting changes without silently correcting user input."""

from dataclasses import replace

from fin_calc.config.settings import THEMES, Settings
from fin_calc.domains.calc.formatting import MAX_DECIMAL_PLACES
from fin_calc.domains.calc.history import MAX_HISTORY_CAP, MIN_HISTORY_CAP


def _bounded_integer(value: str, minimum: int, maximum: int) -> int:
    if value.isascii() and value.isdecimal():
        number = int(value)
        if minimum <= number <= maximum:
            return number
    msg = f"Use a whole number from {minimum} to {maximum}."
    raise ValueError(msg)


def parse_setting(settings: Settings, name: str, value: str) -> Settings:
    """Return a changed copy, rejecting unknown names and invalid values."""
    name = name.lower().replace("-", "_")
    value = value.lower()
    if name == "decimal_places":
        places = (
            None
            if value == "full"
            else _bounded_integer(value, 0, MAX_DECIMAL_PLACES)
        )
        return replace(settings, decimal_places=places)
    if name == "max_history_entries":
        cap = (
            None
            if value == "unlimited"
            else _bounded_integer(value, MIN_HISTORY_CAP, MAX_HISTORY_CAP)
        )
        return replace(settings, max_history_entries=cap)
    if name == "theme":
        for theme in THEMES:
            if value == theme:
                return replace(settings, theme=theme)
        msg = f"Theme must be one of: {', '.join(THEMES)}."
        raise ValueError(msg)
    msg = f"Unknown setting: {name}. Type config for available options."
    raise ValueError(msg)
