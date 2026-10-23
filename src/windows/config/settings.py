"""User-configurable application settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.windows.domains.calc.history import DEFAULT_HISTORY_CAP

Theme = Literal["dark", "light"]
THEMES: tuple[Theme, ...] = ("dark", "light")
DEFAULT_THEME: Theme = "dark"


@dataclass
class Settings:
    """User-configurable application settings.

    Parameters
    ----------
    decimal_places : int | None
        Decimal places shown for results; None means full precision.
    theme : Theme
        Theme name, "dark" or "light".
    max_history_entries : int | None
        Maximum retained history entries; None means unlimited.

    """

    decimal_places: int | None = None
    theme: Theme = DEFAULT_THEME
    max_history_entries: int | None = DEFAULT_HISTORY_CAP
