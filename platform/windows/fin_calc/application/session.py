"""Coordinate text calculations with saved history and display settings."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from fin_calc.adapters.history_store import load_history, write_history
from fin_calc.adapters.settings_store import load_settings, write_settings
from fin_calc.config.path_handler import HISTORY_FILE, SETTINGS_FILE
from fin_calc.domains.calc.evaluator import evaluate
from fin_calc.domains.calc.formatting import format_result
from fin_calc.domains.calc.history import History, HistoryEntry
from fin_calc.domains.calc.parsing import parse_expression

if TYPE_CHECKING:
    from pathlib import Path

    from fin_calc.config.settings import Settings


@dataclass
class CalculatorSession:
    """Own the history and settings for one running interface."""

    history: History
    settings: Settings
    history_path: Path
    settings_path: Path = SETTINGS_FILE

    def update_settings(self, settings: Settings) -> None:
        """Persist settings before applying them to this session.

        History limits take effect at the next calculation or session load.
        A failed settings write leaves the active settings unchanged.
        """
        write_settings(settings, self.settings_path)
        self.settings = settings

    def calculate(self, expression: str) -> str:
        """Evaluate and save an expression, returning its display result.

        Failed calculations or writes leave the in-memory history unchanged.
        Stored results retain full Decimal precision.
        """
        result = str(evaluate(parse_expression(expression)))
        entry = HistoryEntry(expression.strip(), result, datetime.now(tz=UTC))
        updated = History(
            entries=list(self.history.entries),
            max_entries=self.settings.max_history_entries,
        )
        updated.append(entry)
        write_history(updated, self.history_path)
        self.history.entries[:] = updated.entries
        return format_result(result, self.settings.decimal_places)


def load_session() -> CalculatorSession:
    """Load the same history and settings used by the graphical interface."""
    history = load_history(HISTORY_FILE)
    settings = load_settings(SETTINGS_FILE)
    history.trim_to(settings.max_history_entries)
    return CalculatorSession(history, settings, HISTORY_FILE, SETTINGS_FILE)
