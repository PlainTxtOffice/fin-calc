"""Expression display and status line widget."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from fin_calc.ui.gui.views.theme import get_theme

if TYPE_CHECKING:
    from fin_calc.ui.gui.views.theme import ThemeColors


class DisplayView(QWidget):
    """Shows the current expression and a status/error line.

    Parameters
    ----------
    parent : QWidget | None
        Parent widget.

    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the display view widget."""
        super().__init__(parent)
        self._expression_label = QLabel("")
        self._expression_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        self._expression_label.setMinimumHeight(40)

        self._status_label = QLabel("")
        self._status_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

        self.restyle(get_theme("dark"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._expression_label)
        layout.addWidget(self._status_label)

    def set_expression(self, text: str) -> None:
        """Update the expression display text."""
        self._expression_label.setText(text)

    def set_status(self, text: str) -> None:
        """Update the status/error display text."""
        self._status_label.setText(text)

    def clear_status(self) -> None:
        """Clear the status line."""
        self._status_label.setText("")

    def restyle(self, colors: ThemeColors) -> None:
        """Apply theme colors to the expression and status labels."""
        self._expression_label.setStyleSheet(
            "font-size: 24px; padding: 4px;"
            f" background: {colors.display_bg}; color: {colors.display_fg};",
        )
        self._status_label.setStyleSheet(
            f"font-size: 14px; padding: 2px; color: {colors.error_fg};",
        )
