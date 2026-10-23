"""Named color themes and application-wide palette setup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QIcon, QPalette

from src.windows.config.path_handler import ICON_FILE

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class ThemeColors:
    """Hex colors for one theme, covering palette roles and view styles."""

    window: str
    window_text: str
    base: str
    alternate_base: str
    text: str
    button: str
    button_text: str
    tooltip_base: str
    tooltip_text: str
    highlight: str
    highlighted_text: str
    placeholder_text: str
    display_bg: str
    display_fg: str
    error_fg: str
    tape_bg: str
    tape_fg: str
    statusbar_bg: str
    statusbar_fg: str


_DARK = ThemeColors(
    window="#25282d",
    window_text="#d6dde8",
    base="#1e1e1e",
    alternate_base="#2d2d2d",
    text="#e6e6e6",
    button="#33373d",
    button_text="#e6e6e6",
    tooltip_base="#25282d",
    tooltip_text="#d6dde8",
    highlight="#3d6fa5",
    highlighted_text="#ffffff",
    placeholder_text="#8a919c",
    display_bg="#1e1e1e",
    display_fg="#ffffff",
    error_fg="#ff6b6b",
    tape_bg="#2d2d2d",
    tape_fg="#cccccc",
    statusbar_bg="#25282d",
    statusbar_fg="#d6dde8",
)

_LIGHT = ThemeColors(
    window="#f2f3f5",
    window_text="#1f2328",
    base="#ffffff",
    alternate_base="#e8eaed",
    text="#1f2328",
    button="#dfe3e8",
    button_text="#1f2328",
    tooltip_base="#f2f3f5",
    tooltip_text="#1f2328",
    highlight="#3d6fa5",
    highlighted_text="#ffffff",
    placeholder_text="#6b7280",
    display_bg="#ffffff",
    display_fg="#111111",
    error_fg="#c62828",
    tape_bg="#ffffff",
    tape_fg="#333333",
    statusbar_bg="#e3e6ea",
    statusbar_fg="#2b3138",
)

THEMES: dict[str, ThemeColors] = {"dark": _DARK, "light": _LIGHT}


def get_theme(name: str) -> ThemeColors:
    """Return the named theme's colors, falling back to dark.

    Parameters
    ----------
    name : str
        Theme name ("dark" or "light").

    """
    return THEMES.get(name, _DARK)


def apply_theme(app: QApplication, theme_name: str = "dark") -> None:
    """Apply the named theme's palette and the window icon.

    Uses the Fusion style so every widget matches the theme colors
    used by the display and tape views.

    Parameters
    ----------
    app : QApplication
        The running application.
    theme_name : str
        Theme name ("dark" or "light"); unknown names fall back to dark.

    """
    colors = get_theme(theme_name)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(colors.window))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.window_text))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors.base))
    palette.setColor(
        QPalette.ColorRole.AlternateBase,
        QColor(colors.alternate_base),
    )
    palette.setColor(QPalette.ColorRole.Text, QColor(colors.text))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors.button))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.button_text))
    palette.setColor(
        QPalette.ColorRole.ToolTipBase,
        QColor(colors.tooltip_base),
    )
    palette.setColor(
        QPalette.ColorRole.ToolTipText,
        QColor(colors.tooltip_text),
    )
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.highlight))
    palette.setColor(
        QPalette.ColorRole.HighlightedText,
        QColor(colors.highlighted_text),
    )
    palette.setColor(
        QPalette.ColorRole.PlaceholderText,
        QColor(colors.placeholder_text),
    )
    app.setPalette(palette)

    if ICON_FILE.exists():
        app.setWindowIcon(QIcon(str(ICON_FILE)))
