"""Tests for history export adapters."""

from datetime import UTC, datetime
from pathlib import Path

from fin_calc.adapters.history_export import write_history_csv
from fin_calc.domains.calc.history import History, HistoryEntry


def test_write_history_csv_exports_entries(tmp_path: Path) -> None:
    """Verify calculator history can be exported as CSV."""
    export_path = tmp_path / "exports" / "history.csv"
    timestamp = datetime(2026, 6, 2, 12, 30, tzinfo=UTC)
    history = History(
        entries=[
            HistoryEntry(
                expression="1 + 1",
                result="2",
                timestamp=timestamp,
            ),
        ],
    )

    write_history_csv(history, export_path)

    assert export_path.read_text(encoding="utf-8").splitlines() == [
        "timestamp,expression,result",
        "2026-06-02T12:30:00+00:00,1 + 1,2",
    ]
