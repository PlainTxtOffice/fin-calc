"""Modal dialog for editing application settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QSpinBox,
    QVBoxLayout,
)

from fin_calc.config.settings import Settings
from fin_calc.domains.calc.formatting import MAX_DECIMAL_PLACES
from fin_calc.domains.calc.history import (
    DEFAULT_HISTORY_CAP,
    MAX_HISTORY_CAP,
    MIN_HISTORY_CAP,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class SettingsDialog(QDialog):
    """Edit decimal precision, theme, and history cap.

    Parameters
    ----------
    settings : Settings
        Current settings used to pre-populate the controls.
    parent : QWidget | None
        Parent widget.

    """

    def __init__(
        self,
        settings: Settings,
        parent: QWidget | None = None,
    ) -> None:
        """Build the dialog controls from the current settings."""
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self._precision_combo = QComboBox()
        self._precision_combo.addItem("Full precision", userData=None)
        for places in range(MAX_DECIMAL_PLACES + 1):
            self._precision_combo.addItem(str(places), userData=places)
        self._precision_combo.setCurrentIndex(
            self._precision_combo.findData(settings.decimal_places),
        )

        self._theme_combo = QComboBox()
        self._theme_combo.addItem("Dark", userData="dark")
        self._theme_combo.addItem("Light", userData="light")
        self._theme_combo.setCurrentIndex(
            self._theme_combo.findData(settings.theme),
        )

        self._cap_spin = QSpinBox()
        self._cap_spin.setRange(MIN_HISTORY_CAP, MAX_HISTORY_CAP)
        self._cap_spin.setValue(
            settings.max_history_entries or DEFAULT_HISTORY_CAP,
        )

        self._unlimited_check = QCheckBox("Unlimited")
        self._unlimited_check.setChecked(settings.max_history_entries is None)
        self._unlimited_check.toggled.connect(self._cap_spin.setDisabled)
        self._cap_spin.setDisabled(self._unlimited_check.isChecked())

        cap_row = QHBoxLayout()
        cap_row.addWidget(self._cap_spin)
        cap_row.addWidget(self._unlimited_check)

        form = QFormLayout()
        form.addRow("Decimal places:", self._precision_combo)
        form.addRow("Theme:", self._theme_combo)
        form.addRow("Max history entries:", cap_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def selected_settings(self) -> Settings:
        """Return a Settings built from the current control values."""
        max_entries = (
            None
            if self._unlimited_check.isChecked()
            else self._cap_spin.value()
        )
        return Settings(
            decimal_places=self._precision_combo.currentData(),
            theme=self._theme_combo.currentData(),
            max_history_entries=max_entries,
        )
