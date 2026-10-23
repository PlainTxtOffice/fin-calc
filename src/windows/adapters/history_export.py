"""CSV export adapter for calculator history."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from src.windows.domains.calc.history import History


def write_history_csv(history: History, path: Path) -> None:
    """Write calculator history entries to a CSV file.

    - Parent directories are created when needed.
    - Existing files are overwritten.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as export_file:
        writer = csv.writer(export_file)
        writer.writerow(["timestamp", "expression", "result"])
        for entry in history.entries:
            writer.writerow(
                [
                    entry.timestamp.isoformat(),
                    entry.expression,
                    entry.result,
                ],
            )
