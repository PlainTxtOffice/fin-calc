"""JSON file persistence for application settings.

Invalid or missing files always produce default Settings; loading
never raises to the caller.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from fin_calc.config.settings import DEFAULT_THEME, THEMES, Settings, Theme
from fin_calc.domains.calc.formatting import MAX_DECIMAL_PLACES
from fin_calc.domains.calc.history import MAX_HISTORY_CAP, MIN_HISTORY_CAP

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def _read_optional_bounded_int(
    raw: object,
    minimum: int,
    maximum: int,
) -> int | None:
    """Return raw as an int clamped to maximum, or None if invalid.

    Parameters
    ----------
    raw : object
        The raw JSON value to validate.
    minimum : int
        The smallest acceptable value; values below this are rejected.
    maximum : int
        The largest acceptable value; values above this are clamped down
        to it rather than rejected.

    Returns
    -------
    int | None
        The value (clamped to `maximum`) if `raw` is an int >= `minimum`,
        else None.

    """
    if isinstance(raw, int) and not isinstance(raw, bool) and raw >= minimum:
        return min(raw, maximum)
    return None


def _read_history_cap(raw: dict) -> int | None:
    """Read the history cap, distinguishing absent, null, and invalid.

    Parameters
    ----------
    raw : dict
        The decoded settings JSON object.

    Returns
    -------
    int | None
        An explicit JSON ``null`` means unlimited (None); a missing or
        invalid value falls back to the default cap; valid ints are
        clamped to the maximum.

    """
    if "max_history_entries" not in raw:
        return Settings().max_history_entries
    value = raw["max_history_entries"]
    if value is None:
        return None
    validated = _read_optional_bounded_int(
        value,
        minimum=MIN_HISTORY_CAP,
        maximum=MAX_HISTORY_CAP,
    )
    if validated is None:
        return Settings().max_history_entries
    return validated


def _read_theme(raw: object) -> Theme:
    """Return raw as a known theme name, or the default theme.

    Parameters
    ----------
    raw : object
        The raw JSON value to validate.

    Returns
    -------
    Theme
        The matching theme name, else ``DEFAULT_THEME``.

    """
    for name in THEMES:
        if raw == name:
            return name
    return DEFAULT_THEME


def load_settings(path: Path) -> Settings:
    """Load settings from a JSON file.

    Parameters
    ----------
    path : Path
        Path to the settings JSON file.

    Returns
    -------
    Settings
        Loaded settings; individual invalid fields fall back to their
        defaults, and a missing or corrupt file yields all defaults.

    """
    if not path.exists():
        return Settings()
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            return Settings()
        raw = json.loads(text)
    except (OSError, ValueError):
        logger.exception("Failed to load settings from %s", path)
        return Settings()
    if not isinstance(raw, dict):
        logger.error("Settings JSON root must be an object: %s", path)
        return Settings()

    return Settings(
        decimal_places=_read_optional_bounded_int(
            raw.get("decimal_places"),
            minimum=0,
            maximum=MAX_DECIMAL_PLACES,
        ),
        theme=_read_theme(raw.get("theme")),
        max_history_entries=_read_history_cap(raw),
    )


def write_settings(settings: Settings, path: Path) -> None:
    """Write settings to a JSON file.

    Parameters
    ----------
    settings : Settings
        The settings to persist.
    path : Path
        Path to the settings JSON file.

    """
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = {
        "decimal_places": settings.decimal_places,
        "theme": settings.theme,
        "max_history_entries": settings.max_history_entries,
    }
    try:
        path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    except OSError:
        logger.exception("Failed to write settings to %s", path)
        raise
