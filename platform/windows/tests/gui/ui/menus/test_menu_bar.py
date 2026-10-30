"""Tests for the menu bar builder."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMainWindow

from fin_calc.ui.gui.menus.menu_bar import MenuBarCallbacks, build_menu_bar


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _build(calls: list[str]):
    window = QMainWindow()
    parts = build_menu_bar(
        window,
        MenuBarCallbacks(
            export_history=lambda: calls.append("export"),
            clear_history=lambda: calls.append("clear"),
            open_settings=lambda: calls.append("settings"),
            show_about=lambda: calls.append("about"),
            show_shortcuts=lambda: calls.append("shortcuts"),
        ),
    )
    return window, parts


def test_edit_menu_contains_settings_action():
    _app()
    calls: list[str] = []
    _window, parts = _build(calls)

    edit_actions = [a.text() for a in parts.edit_menu.actions()]
    assert "Settings..." in edit_actions


def test_help_menu_contains_about_and_shortcuts():
    _app()
    calls: list[str] = []
    _window, parts = _build(calls)

    help_actions = [a.text() for a in parts.help_menu.actions()]
    assert "About" in help_actions
    assert "Keyboard Shortcuts" in help_actions


def test_actions_trigger_callbacks():
    _app()
    calls: list[str] = []
    _window, parts = _build(calls)

    parts.settings_action.trigger()
    parts.about_action.trigger()
    parts.shortcuts_action.trigger()

    assert calls == ["settings", "about", "shortcuts"]
