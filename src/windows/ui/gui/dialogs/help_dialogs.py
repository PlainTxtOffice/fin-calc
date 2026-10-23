"""About and Keyboard Shortcuts dialogs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

# Keep in sync with [project] version in pyproject.toml.
APP_VERSION = "0.1.0"

SHORTCUTS_TEXT = (
    "Enter / Return — evaluate the expression\n"
    "Esc — clear the current expression\n"
    "Backspace — delete the last character\n"
    "Digits and operators (0-9 . + - * / ^ ( )) — press keypad buttons"
)


def show_about(parent: QWidget) -> None:
    """Show the About dialog.

    Parameters
    ----------
    parent : QWidget
        Parent window for the modal dialog.

    """
    QMessageBox.about(
        parent,
        "About fin_calc",
        f"fin_calc {APP_VERSION}\n\n"
        "A Decimal-based desktop calculator with a persistent tape.",
    )


def show_shortcuts(parent: QWidget) -> None:
    """Show the Keyboard Shortcuts dialog.

    Parameters
    ----------
    parent : QWidget
        Parent window for the modal dialog.

    """
    QMessageBox.information(parent, "Keyboard Shortcuts", SHORTCUTS_TEXT)
