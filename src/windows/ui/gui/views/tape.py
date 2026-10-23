"""Scrollable history tape widget with clickable results."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from src.windows.domains.calc.formatting import format_result
from src.windows.ui.gui.views.theme import get_theme

if TYPE_CHECKING:
    from PySide6.QtGui import QContextMenuEvent

    from src.windows.domains.calc.history import HistoryEntry
    from src.windows.ui.gui.views.theme import ThemeColors


class TapeView(QWidget):
    """Scrollable tape showing past calculations.

    Emits ``result_clicked`` with the result string when a user
    clicks an entry.

    Parameters
    ----------
    parent : QWidget | None
        Parent widget.

    """

    result_clicked = Signal(str)
    clear_history_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the tape view widget.

        Parameters
        ----------
        parent : QWidget | None
            Parent widget.

        """
        super().__init__(parent)
        self._list = QListWidget()
        self.restyle(get_theme("dark"))
        self._list.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel,
        )
        self._list.itemClicked.connect(self._on_item_clicked)

        self._scroll_anim = QPropertyAnimation(
            self._list.verticalScrollBar(),
            b"value",
        )
        self._scroll_anim.setDuration(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._list)

        self._results: list[str] = []
        self._decimal_places: int | None = None

    def add_entry(self, entry: HistoryEntry) -> None:
        """Append a history entry to the tape and scroll to it."""
        display_text = f"{entry.expression} = {
            format_result(entry.result, self._decimal_places)
        }"
        item = QListWidgetItem(display_text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._list.addItem(item)
        self._results.append(entry.result)
        self._smooth_scroll_to_bottom()

    def load_entries(self, entries: list[HistoryEntry]) -> None:
        """Load a batch of entries (e.g. from persistence on startup)."""
        for entry in entries:
            display_text = (
                f"{entry.expression}"
                f" = {format_result(entry.result, self._decimal_places)}"
            )
            item = QListWidgetItem(display_text)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._list.addItem(item)
            self._results.append(entry.result)
        if entries:
            self._smooth_scroll_to_bottom()

    def clear_tape(self) -> None:
        """Remove all entries from the tape display."""
        self._list.clear()
        self._results.clear()

    def restyle(self, colors: ThemeColors) -> None:
        """Apply theme colors to the tape list."""
        self._list.setStyleSheet(
            f"font-size: 16px; background: {colors.tape_bg}; color: {
                colors.tape_fg
            };",
        )

    def set_decimal_places(self, decimal_places: int | None) -> None:
        """Set the display precision used for rendered results."""
        self._decimal_places = decimal_places

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        """Show a right-click context menu with a Clear History option."""
        if not self._results:
            return
        menu = QMenu(self)
        clear_action = menu.addAction("Clear History")
        action = menu.exec(event.globalPos())
        if action == clear_action:
            self.clear_history_requested.emit()

    def _smooth_scroll_to_bottom(self) -> None:
        """Animate the scrollbar to the bottom of the list."""
        QTimer.singleShot(0, self._animate_scroll)

    def _animate_scroll(self) -> None:
        scrollbar = self._list.verticalScrollBar()
        self._scroll_anim.stop()
        self._scroll_anim.setStartValue(scrollbar.value())
        self._scroll_anim.setEndValue(scrollbar.maximum())
        self._scroll_anim.start()

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        row = self._list.row(item)
        if 0 <= row < len(self._results):
            self.result_clicked.emit(self._results[row])
