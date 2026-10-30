"""Tests for the root calculator window."""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from fin_calc.domains.calc.history import History, HistoryEntry
from fin_calc.config.settings import Settings
from fin_calc.ui.gui.views.theme import get_theme
from fin_calc.ui.gui.views import root_window


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_close_waits_for_pending_history_write(monkeypatch, tmp_path):
    _app()
    writes: list[int] = []

    def write_slowly(history: History, path) -> None:
        time.sleep(0.05)
        writes.append(len(history.entries))
        path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(root_window, "write_history", write_slowly)
    monkeypatch.setattr(root_window, "HISTORY_FILE", tmp_path / "history.json")

    history = History()
    history.append(
        HistoryEntry(
            expression="1 + 1",
            result="2",
            timestamp=datetime.now(tz=UTC),
        ),
    )
    window = root_window.RootWindow(history)

    window._persist_history()
    window.close()

    assert writes == [1]
    assert window._write_pool._shutdown is True


def test_menu_bar_exposes_file_edit_and_help_menus() -> None:
    _app()
    window = root_window.RootWindow(History())

    menu_labels = {
        action.text().replace("&", "") for action in window.menuBar().actions()
    }
    action_labels = {
        action.text().replace("&", "")
        for action in window._menus.file_menu.actions()
        if not action.isSeparator()
    }

    assert menu_labels == {"File", "Edit", "Help"}
    assert action_labels == {"Export History...", "Clear History", "Exit"}


def test_export_history_action_writes_selected_csv(
    monkeypatch, tmp_path
) -> None:
    _app()
    writes: list[tuple[int, Path]] = []
    export_path = tmp_path / "history.csv"
    history = History(
        entries=[
            HistoryEntry(
                expression="1 + 1",
                result="2",
                timestamp=datetime.now(tz=UTC),
            ),
        ],
    )

    def select_export_path(*_args, **_kwargs):
        return str(export_path), "CSV Files (*.csv)"

    def write_export(selected_history: History, selected_path: Path) -> None:
        writes.append((len(selected_history.entries), selected_path))

    monkeypatch.setattr(
        root_window.QFileDialog,
        "getSaveFileName",
        select_export_path,
    )
    monkeypatch.setattr(root_window, "write_history_csv", write_export)
    window = root_window.RootWindow(history)

    window._menus.export_history_action.trigger()

    assert writes == [(1, export_path)]
    assert window.statusBar().currentMessage() == (
        f"Exported history to {export_path}"
    )
    assert "#d6dde8" in window.statusBar().styleSheet()
    assert "#ff6b6b" not in window.statusBar().styleSheet()
    assert window._display._status_label.text() == ""


def test_settings_dialog_ok_applies_and_persists(monkeypatch, tmp_path):
    _app()
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(root_window, "SETTINGS_FILE", settings_file)
    monkeypatch.setattr(root_window, "HISTORY_FILE", tmp_path / "history.json")

    ts = datetime.now(tz=UTC)
    history = History(
        entries=[
            HistoryEntry(expression=str(i), result=str(i), timestamp=ts)
            for i in range(5)
        ],
    )
    window = root_window.RootWindow(history)

    new_settings = Settings(
        decimal_places=2,
        theme="light",
        max_history_entries=2,
    )

    class FakeDialog:
        def __init__(self, settings, parent=None):
            pass

        def exec(self):
            return root_window.QDialog.DialogCode.Accepted

        def selected_settings(self):
            return new_settings

    monkeypatch.setattr(root_window, "SettingsDialog", FakeDialog)
    window._on_open_settings()

    assert window._settings == new_settings
    assert len(history.entries) == 2  # cap trimmed oldest
    assert settings_file.exists()
    window.close()


def test_settings_dialog_cancel_changes_nothing(monkeypatch, tmp_path):
    _app()
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(root_window, "SETTINGS_FILE", settings_file)

    window = root_window.RootWindow(History())
    original = window._settings

    class FakeDialog:
        def __init__(self, settings, parent=None):
            pass

        def exec(self):
            return root_window.QDialog.DialogCode.Rejected

        def selected_settings(self):  # pragma: no cover - must not be called
            raise AssertionError("selected_settings called on cancel")

    monkeypatch.setattr(root_window, "SettingsDialog", FakeDialog)
    window._on_open_settings()

    assert window._settings == original
    assert not settings_file.exists()
    window.close()


def test_startup_trims_history_to_cap():
    _app()
    ts = datetime.now(tz=UTC)
    history = History(
        entries=[
            HistoryEntry(expression=str(i), result=str(i), timestamp=ts)
            for i in range(5)
        ],
    )
    window = root_window.RootWindow(
        history,
        settings=Settings(max_history_entries=3),
    )
    assert len(history.entries) == 3
    window.close()


def test_tape_renders_with_precision():
    _app()
    ts = datetime.now(tz=UTC)
    history = History(
        entries=[
            HistoryEntry(
                expression="1 / 3", result="0.3333333333", timestamp=ts
            ),
        ],
    )
    window = root_window.RootWindow(
        history,
        settings=Settings(decimal_places=2),
    )
    item_text = window._tape._list.item(0).text()
    assert item_text == "1 / 3 = 0.33"
    # Clicking still inserts the full-precision value.
    assert window._tape._results == ["0.3333333333"]
    window.close()


def test_enter_key_evaluation_respects_precision(monkeypatch, tmp_path):
    _app()
    monkeypatch.setattr(root_window, "HISTORY_FILE", tmp_path / "history.json")
    window = root_window.RootWindow(
        History(), settings=Settings(decimal_places=2)
    )
    for token in ("1", "/", "3"):
        window._on_token(token)

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent

    event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Return,
        Qt.KeyboardModifier.NoModifier,
    )
    window.keyPressEvent(event)

    assert window._display._expression_label.text() == "0.33"
    window.close()


def test_display_restyle_uses_theme_colors():
    _app()
    window = root_window.RootWindow(History())
    light = get_theme("light")
    window._display.restyle(light)
    assert light.display_bg in window._display._expression_label.styleSheet()
    window.close()


def _history_with_one_entry() -> History:
    history = History()
    history.append(
        HistoryEntry(
            expression="1 + 1",
            result="2",
            timestamp=datetime.now(tz=UTC),
        ),
    )
    return history


def test_window_title_uses_product_name():
    _app()
    window = root_window.RootWindow(History())

    assert window.windowTitle() == "Fin Calc"


def test_clear_history_asks_before_clearing(monkeypatch, tmp_path):
    _app()
    monkeypatch.setattr(root_window, "HISTORY_FILE", tmp_path / "history.json")
    window = root_window.RootWindow(_history_with_one_entry())
    answers = [root_window.QMessageBox.StandardButton.No]
    monkeypatch.setattr(
        root_window.QMessageBox,
        "question",
        lambda *_args: answers.pop(0),
    )

    window._on_clear_history()
    assert len(window._history.entries) == 1

    answers.append(root_window.QMessageBox.StandardButton.Yes)
    window._on_clear_history()
    assert window._history.entries == []
    window.close()


def test_failed_history_write_is_shown(monkeypatch, tmp_path):
    app = _app()

    def fail_write(history: History, path) -> None:
        message = "disk full"
        raise OSError(message)

    monkeypatch.setattr(root_window, "write_history", fail_write)
    monkeypatch.setattr(root_window, "HISTORY_FILE", tmp_path / "history.json")
    window = root_window.RootWindow(_history_with_one_entry())

    window._persist_history()
    window._write_pool.shutdown(wait=True)
    deadline = time.monotonic() + 2
    while "disk full" not in window.statusBar().currentMessage():
        assert time.monotonic() < deadline
        app.processEvents()

    assert window.statusBar().currentMessage() == "Saving history failed: disk full"
