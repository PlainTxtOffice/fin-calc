"""History model for the calculator domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

DEFAULT_HISTORY_CAP = 1000
MIN_HISTORY_CAP = 1
MAX_HISTORY_CAP = 10_000


@dataclass
class HistoryEntry:
    """A single calculation record.

    Parameters
    ----------
    expression : str
        The expression as entered (e.g. "12 + 3").
    result : str
        The Decimal result as a string (e.g. "15").
    timestamp : datetime
        When the calculation was performed.

    """

    expression: str
    result: str
    timestamp: datetime


@dataclass
class History:
    """In-memory ordered list of calculation history entries.

    Parameters
    ----------
    entries : list[HistoryEntry]
        Pre-existing entries to initialize with.
    max_entries : int | None
        Maximum retained entries; None means unlimited.

    """

    entries: list[HistoryEntry] = field(default_factory=list)
    max_entries: int | None = None

    def append(self, entry: HistoryEntry) -> None:
        """Add a new entry, trimming the oldest if over the cap.

        A cap of 0 means no entries are retained.
        """
        self.entries.append(entry)
        self.trim_to(self.max_entries)

    def trim_to(self, max_entries: int | None) -> None:
        """Set a new cap and drop the oldest entries beyond it.

        A cap of 0 empties the history.
        """
        self.max_entries = max_entries
        if max_entries is not None and len(self.entries) > max_entries:
            del self.entries[: len(self.entries) - max_entries]

    def clear_all(self) -> None:
        """Remove all entries from the history."""
        self.entries.clear()
