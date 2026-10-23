"""Tests for the calculator keypad view."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton

from src.windows.ui.gui.views.keypad import KeypadView


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_keypad_does_not_show_clear_entry_button() -> None:
    """Verify backspace is the only single-entry correction control."""
    _app()
    keypad = KeypadView()

    labels = {button.text() for button in keypad.findChildren(QPushButton)}

    assert "CE" not in labels
    assert "\u2190" in labels


def test_l_key_maps_to_log_token() -> None:
    """Typing 'l' or 'L' enters the log function from the keyboard."""
    _app()
    keypad = KeypadView()
    received: list[str] = []
    keypad.token_pressed.connect(received.append)

    keypad.map_key_press("l")
    keypad.map_key_press("L")

    assert received == ["log", "log"]


def test_buttons_do_not_take_focus() -> None:
    """Buttons must not grab focus, so Space never re-triggers them."""
    _app()
    keypad = KeypadView()

    policies = {
        button.focusPolicy() for button in keypad.findChildren(QPushButton)
    }

    assert policies == {Qt.FocusPolicy.NoFocus}


def test_keypad_buttons_follow_live_palette_change() -> None:
    """Buttons must pick up palette changes from live theme switches."""
    from PySide6.QtGui import QColor

    from src.windows.ui.gui.views.theme import apply_theme, get_theme

    app = _app()
    apply_theme(app, "dark")
    keypad = KeypadView()
    keypad.show()  # polish widgets; the bug only appears once polished
    app.processEvents()
    apply_theme(app, "light")
    app.processEvents()
    button = keypad.findChildren(QPushButton)[0]
    assert button.palette().button().color() == QColor(
        get_theme("light").button
    )
    apply_theme(app, "dark")  # restore for other tests
