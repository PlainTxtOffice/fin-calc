"""Tests for the About and Keyboard Shortcuts dialogs."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QWidget

from fin_calc.ui.gui.dialogs import help_dialogs


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_version_matches_pyproject():
    import tomllib
    from pathlib import Path

    pyproject = Path(__file__).resolve().parents[4] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert help_dialogs.APP_VERSION == data["project"]["version"]


def test_show_about_includes_name_and_version(monkeypatch):
    _app()
    captured: dict[str, str] = {}

    def fake_about(parent, title, text):
        captured["title"] = title
        captured["text"] = text

    monkeypatch.setattr(help_dialogs.QMessageBox, "about", fake_about)
    help_dialogs.show_about(QWidget())

    assert captured["title"] == "About Fin Calc"
    assert captured["text"].startswith("Fin Calc ")
    assert help_dialogs.APP_VERSION in captured["text"]


def test_show_shortcuts_lists_key_bindings(monkeypatch):
    _app()
    captured: dict[str, str] = {}

    def fake_information(parent, title, text):
        captured["title"] = title
        captured["text"] = text

    monkeypatch.setattr(
        help_dialogs.QMessageBox,
        "information",
        fake_information,
    )
    help_dialogs.show_shortcuts(QWidget())

    assert "Shortcuts" in captured["title"]
    for token in ("Enter", "Esc", "Backspace", "L — insert log"):
        assert token in captured["text"]
