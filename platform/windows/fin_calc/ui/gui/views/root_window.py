"""Main calculator window assembling tape, display, and keypad."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from fin_calc.adapters.history_export import write_history_csv
from fin_calc.adapters.history_store import write_history
from fin_calc.adapters.settings_store import write_settings
from fin_calc.config.path_handler import (
    EXPORTS_DIR,
    HISTORY_FILE,
    SETTINGS_FILE,
)
from fin_calc.config.settings import Settings
from fin_calc.domains.calc.errors import EvaluationError
from fin_calc.domains.calc.evaluator import evaluate
from fin_calc.domains.calc.expression import ExpressionBuilder
from fin_calc.domains.calc.formatting import format_result
from fin_calc.domains.calc.history import History, HistoryEntry
from fin_calc.ui.gui.dialogs.help_dialogs import show_about, show_shortcuts
from fin_calc.ui.gui.dialogs.settings_dialog import SettingsDialog
from fin_calc.ui.gui.menus.menu_bar import MenuBarCallbacks, build_menu_bar
from fin_calc.ui.gui.views.display import DisplayView
from fin_calc.ui.gui.views.keypad import KeypadView
from fin_calc.ui.gui.views.tape import TapeView
from fin_calc.ui.gui.views.theme import apply_theme, get_theme

if TYPE_CHECKING:
    from concurrent.futures import Future

    from PySide6.QtGui import QCloseEvent, QKeyEvent


class RootWindow(QMainWindow):
    """Main calculator window.

    Parameters
    ----------
    history : History
        Pre-loaded history model.
    settings : Settings | None
        Pre-loaded settings; None uses defaults.
    parent : QWidget | None
        Parent widget.

    """

    # Carries a background history-write error to the GUI thread.
    history_write_failed = Signal(str)

    def __init__(
        self,
        history: History,
        settings: Settings | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the main calculator window and wire up its views."""
        super().__init__(parent)
        self.setWindowTitle("Fin Calc")
        self.history_write_failed.connect(self._show_history_write_error)
        self.setMinimumSize(360, 560)

        self._history = history
        self._settings = settings or Settings()
        self._history.trim_to(self._settings.max_history_entries)
        self._builder = ExpressionBuilder()
        self._write_pool = ThreadPoolExecutor(max_workers=1)
        self._menus = build_menu_bar(
            self,
            MenuBarCallbacks(
                export_history=self._on_export_history,
                clear_history=self._on_clear_history,
                open_settings=self._on_open_settings,
                show_about=lambda: show_about(self),
                show_shortcuts=lambda: show_shortcuts(self),
            ),
        )

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._tape = TapeView()
        self._tape.result_clicked.connect(self._on_result_clicked)
        self._tape.clear_history_requested.connect(self._on_clear_history)
        layout.addWidget(self._tape, stretch=6)

        self._display = DisplayView()
        layout.addWidget(self._display, stretch=1)

        self._keypad = KeypadView()
        self._keypad.token_pressed.connect(self._on_token)
        self._keypad.evaluate_pressed.connect(self._on_evaluate)
        self._keypad.clear_pressed.connect(self._on_clear)
        self._keypad.backspace_pressed.connect(self._on_backspace)
        self._keypad.toggle_sign_pressed.connect(self._on_toggle_sign)
        layout.addWidget(self._keypad, stretch=4)

        self._tape.set_decimal_places(self._settings.decimal_places)
        self._apply_theme_styles()
        self._tape.load_entries(self._history.entries)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Forward keyboard input to the keypad or actions."""
        key = event.key()
        text = event.text()

        if key in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            self._on_evaluate()
            return

        if key == Qt.Key.Key_Escape:
            self._on_clear()
        elif key == Qt.Key.Key_Backspace:
            self._on_backspace()
        elif text:
            self._keypad.map_key_press(text)

        self._refresh_display()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Wait for queued history writes before closing."""
        self._write_pool.shutdown(wait=True)
        super().closeEvent(event)

    def _on_token(self, symbol: str) -> None:
        self._display.clear_status()
        if not self._builder.add_symbol(symbol):
            self._display.set_status(f"Invalid input: {symbol}")
        self._refresh_display()

    def _on_evaluate(self) -> None:
        symbols = self._builder.symbol_list()
        if not symbols:
            return
        try:
            result = evaluate(symbols)
        except EvaluationError as err:
            self._display.set_status(str(err))
            return

        result_str = str(result)
        expression_str = self._builder.to_display()
        entry = HistoryEntry(
            expression=expression_str,
            result=result_str,
            timestamp=datetime.now(tz=UTC),
        )
        self._history.append(entry)
        self._tape.add_entry(entry)
        self._persist_history()

        self._builder.clear()
        self._builder.insert_result(result_str)
        self._display.clear_status()
        self._display.set_expression(
            format_result(result_str, self._settings.decimal_places),
        )

    def _on_clear(self) -> None:
        self._builder.clear()
        self._display.clear_status()
        self._refresh_display()

    def _on_backspace(self) -> None:
        self._builder.backspace()
        self._refresh_display()

    def _on_toggle_sign(self) -> None:
        self._builder.toggle_sign()
        self._refresh_display()

    def _on_result_clicked(self, result: str) -> None:
        self._builder.insert_result(result)
        self._display.clear_status()
        self._refresh_display()

    def _on_clear_history(self) -> None:
        answer = QMessageBox.question(
            self,
            "Clear History",
            "Clear all history?\n\n"
            "This removes every saved calculation from the tape.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._history.clear_all()
        self._tape.clear_tape()
        self._persist_history()

    def _on_export_history(self) -> None:
        """Export the current history to a user-selected CSV file."""
        default_path = EXPORTS_DIR / "history.csv"
        selected_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export History",
            str(default_path),
            "CSV Files (*.csv)",
        )
        if not selected_path:
            return

        export_path = Path(selected_path)
        if export_path.suffix.lower() != ".csv":
            export_path = export_path.with_suffix(".csv")

        try:
            write_history_csv(self._history, export_path)
        except OSError as err:
            self.statusBar().showMessage(f"Export failed: {err}")
            return

        self._display.clear_status()
        self.statusBar().showMessage(f"Exported history to {export_path}")

    def _on_open_settings(self) -> None:
        """Open the Settings dialog and apply changes on OK."""
        dialog = SettingsDialog(self._settings, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._apply_settings(dialog.selected_settings())

    def _apply_settings(self, new_settings: Settings) -> None:
        """Apply and persist new settings, restyling and trimming live."""
        self._settings = new_settings

        self._apply_theme_styles()

        self._history.trim_to(new_settings.max_history_entries)
        self._tape.set_decimal_places(new_settings.decimal_places)
        self._tape.clear_tape()
        self._tape.load_entries(self._history.entries)
        self._persist_history()

        try:
            write_settings(new_settings, SETTINGS_FILE)
        except OSError as err:
            self.statusBar().showMessage(f"Saving settings failed: {err}")

        self._refresh_display()

    def _apply_theme_styles(self) -> None:
        """Re-apply the current theme to app palette and styled views."""
        app = QApplication.instance()
        if isinstance(app, QApplication):
            apply_theme(app, self._settings.theme)
        colors = get_theme(self._settings.theme)
        self.statusBar().setStyleSheet(
            f"font-size: 14px; color: {colors.statusbar_fg};"
            f" background: {colors.statusbar_bg}; padding: 3px 8px;",
        )
        self._display.restyle(colors)
        self._tape.restyle(colors)

    def _persist_history(self) -> None:
        """Snapshot entries and write to disk off the GUI thread."""
        snapshot = History(entries=list(self._history.entries))
        future = self._write_pool.submit(write_history, snapshot, HISTORY_FILE)
        future.add_done_callback(self._report_history_write)

    def _report_history_write(self, future: Future[None]) -> None:
        """Forward a failed write from the worker thread to the GUI."""
        error = future.exception()
        if error is not None:
            self.history_write_failed.emit(str(error))

    def _show_history_write_error(self, message: str) -> None:
        self.statusBar().showMessage(f"Saving history failed: {message}")

    def _refresh_display(self) -> None:
        self._display.set_expression(self._builder.to_display())
