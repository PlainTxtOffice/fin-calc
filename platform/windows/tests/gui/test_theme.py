"""Tests for the theme module."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from fin_calc.ui.gui.views.theme import ThemeColors, apply_theme, get_theme


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestGetTheme:
    """Tests for get_theme."""

    def test_dark_matches_legacy_palette(self):
        assert get_theme("dark").window == "#25282d"

    def test_light_differs_from_dark(self):
        assert get_theme("light").window != get_theme("dark").window

    def test_unknown_name_falls_back_to_dark(self):
        assert get_theme("neon") == get_theme("dark")

    def test_all_fields_are_hex_colors(self):
        for theme_name in ("dark", "light"):
            colors = get_theme(theme_name)
            for field_name in ThemeColors.__dataclass_fields__:
                value = getattr(colors, field_name)
                assert QColor(value).isValid(), f"{theme_name}.{field_name}"


class TestApplyTheme:
    """Tests for apply_theme."""

    def test_sets_fusion_style(self):
        app = _app()
        apply_theme(app, "dark")
        assert app.style().objectName() == "fusion"

    def test_dark_palette_window_color(self):
        app = _app()
        apply_theme(app, "dark")
        color = app.palette().color(QPalette.ColorRole.Window)
        assert color == QColor("#25282d")

    def test_light_palette_window_color(self):
        app = _app()
        apply_theme(app, "light")
        color = app.palette().color(QPalette.ColorRole.Window)
        assert color == QColor(get_theme("light").window)
        apply_theme(app, "dark")  # restore for other tests sharing the app
