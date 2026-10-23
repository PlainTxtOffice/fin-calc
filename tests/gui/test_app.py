"""Tests for application-wide theme and icon setup."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.windows.config.path_handler import ICON_FILE
from src.windows.ui.gui.app import apply_theme


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_apply_theme_uses_fusion_style() -> None:
    """One consistent style instead of half system, half hardcoded dark."""
    app = _app()
    apply_theme(app)

    assert app.style().objectName() == "fusion"


def test_apply_theme_sets_window_icon() -> None:
    """The taskbar/titlebar icon comes from assets/icon.ico."""
    app = _app()
    apply_theme(app)

    assert ICON_FILE.exists()
    assert not app.windowIcon().isNull()
