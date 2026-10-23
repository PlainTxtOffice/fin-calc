"""Coordinate text calculations with saved history and display settings."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from src.windows.adapters.history_store import load_history, write_history
from src.windows.adapters.settings_store import load_settings
from src.windows.config.path_handler import HISTORY_FILE, SETTINGS_FILE
from src.windows.domains.calc.evaluator import evaluate
from src.windows.domains.calc.formatting import format_result
from src.windows.domains.calc.history import History, HistoryEntry
from src.windows.domains.calc.parsing import parse_expression

if TYPE_CHECKING:
    from pathlib import Path

    from src.windows.config.settings import Settings


@dataclass
class CalculatorSession:
    """Own the history and settings for one running interface."""

    history: History
    settings: Settings
    history_path: Path

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
    return CalculatorSession(history, settings, HISTORY_FILE)
