"""Calculator button grid with keyboard input forwarding."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QPushButton, QSizePolicy, QWidget

if TYPE_CHECKING:
    from collections.abc import Callable

BUTTON_LAYOUT: list[list[str]] = [
    ["log", "(", ")", "C", ""],
    ["7", "8", "9", "/", "^"],
    ["4", "5", "6", "*", "\u2190"],
    ["1", "2", "3", "-", "="],
    ["0", ".", "\u00b1", "+", ""],
]

KEY_MAP: dict[str, str] = {
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    ".": ".",
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "^": "^",
    "(": "(",
    ")": ")",
    "l": "log",
    "L": "log",
}


class KeypadView(QWidget):
    """Grid of calculator buttons.

    Emits signals for each button type rather than handling
    logic directly.

    Parameters
    ----------
    parent : QWidget | None
        Parent widget.

    """

    token_pressed = Signal(str)
    evaluate_pressed = Signal()
    clear_pressed = Signal()
    backspace_pressed = Signal()
    toggle_sign_pressed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the keypad view with calculator buttons."""
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setSpacing(2)

        for row_idx, row in enumerate(BUTTON_LAYOUT):
            for col_idx, label in enumerate(row):
                if not label:
                    continue
                btn = QPushButton(label)
                btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                btn.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Expanding,
                )
                btn.setMinimumHeight(50)
                # Use QFont, not a stylesheet: any stylesheet pins the
                # button's palette so live theme switches stop applying.
                font = btn.font()
                font.setPixelSize(18)
                btn.setFont(font)
                btn.clicked.connect(self._make_click_callback(label))
                if label == "=":
                    layout.addWidget(btn, row_idx, col_idx, 2, 1)
                else:
                    layout.addWidget(btn, row_idx, col_idx)

    def _make_click_callback(self, label: str) -> Callable[[], None]:
        """Return a slot closure for the given button label."""

        def on_click() -> None:
            self._route_button(label)

        return on_click

    def _route_button(self, label: str) -> None:
        if label == "=":
            self.evaluate_pressed.emit()
        elif label == "C":
            self.clear_pressed.emit()
        elif label == "\u2190":
            self.backspace_pressed.emit()
        elif label == "\u00b1":
            self.toggle_sign_pressed.emit()
        else:
            self.token_pressed.emit(label)

    def map_key_press(self, key_text: str) -> None:
        """Translate a keyboard key string into the appropriate signal."""
        if key_text in KEY_MAP:
            self.token_pressed.emit(KEY_MAP[key_text])
