"""Tests for the Settings dialog."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from fin_calc.config.settings import Settings
from fin_calc.ui.gui.dialogs.settings_dialog import SettingsDialog


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dialog_reflects_current_settings():
    _app()
    dialog = SettingsDialog(
        Settings(decimal_places=2, theme="light", max_history_entries=100),
    )

    assert dialog._precision_combo.currentData() == 2
    assert dialog._theme_combo.currentData() == "light"
    assert not dialog._unlimited_check.isChecked()
    assert dialog._cap_spin.value() == 100


def test_dialog_reflects_defaults():
    _app()
    dialog = SettingsDialog(Settings())

    assert dialog._precision_combo.currentData() is None
    assert dialog._theme_combo.currentData() == "dark"
    assert not dialog._unlimited_check.isChecked()
    assert dialog._cap_spin.value() == 1000


def test_dialog_reflects_unlimited():
    _app()
    dialog = SettingsDialog(Settings(max_history_entries=None))

    assert dialog._unlimited_check.isChecked()
    assert not dialog._cap_spin.isEnabled()


def test_selected_settings_returns_edited_values():
    _app()
    dialog = SettingsDialog(Settings())

    dialog._precision_combo.setCurrentIndex(
        dialog._precision_combo.findData(3),
    )
    dialog._theme_combo.setCurrentIndex(dialog._theme_combo.findData("light"))
    dialog._unlimited_check.setChecked(False)
    dialog._cap_spin.setValue(50)

    selected = dialog.selected_settings()
    assert selected == Settings(
        decimal_places=3,
        theme="light",
        max_history_entries=50,
    )


def test_unlimited_checkbox_toggles_spinbox():
    _app()
    dialog = SettingsDialog(Settings(max_history_entries=10))

    assert dialog._cap_spin.isEnabled()
    dialog._unlimited_check.setChecked(True)
    assert not dialog._cap_spin.isEnabled()
    assert dialog.selected_settings().max_history_entries is None
