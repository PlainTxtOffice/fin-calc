"""PySide6 application setup and launch."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication

from src.windows.config.settings import DEFAULT_THEME
from src.windows.ui.gui.views.root_window import RootWindow
from src.windows.ui.gui.views.theme import apply_theme

if TYPE_CHECKING:
    from src.windows.config.settings import Settings
    from src.windows.domains.calc.history import History

__all__ = ["apply_theme", "run_app"]


def run_app(history: History, settings: Settings | None = None) -> int:
    """Create the QApplication, show the main window, and start the event loop.

    Parameters
    ----------
    history : History
        Pre-loaded history model from the adapter.
    settings : Settings | None
        Pre-loaded settings; None uses defaults.

    Returns
    -------
    int
        Exit code from the Qt event loop.

    """
    app = QApplication([])
    theme_name = settings.theme if settings is not None else DEFAULT_THEME
    apply_theme(app, theme_name)
    window = RootWindow(history, settings=settings)
    window.show()
    return app.exec()
