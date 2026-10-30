"""Tests for the calculator history model."""

from datetime import datetime, timezone

from fin_calc.domains.calc.history import History, HistoryEntry


class TestHistoryEntry:
    """Tests for HistoryEntry dataclass."""

    def test_create_entry(self):
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        entry = HistoryEntry(expression="12 + 3", result="15", timestamp=ts)
        assert entry.expression == "12 + 3"
        assert entry.result == "15"
        assert entry.timestamp == ts


class TestHistory:
    """Tests for History model."""

    def test_new_history_is_empty(self):
        history = History()
        assert history.entries == []

    def test_append_entry(self):
        history = History()
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        entry = HistoryEntry(expression="1 + 1", result="2", timestamp=ts)
        history.append(entry)
        assert len(history.entries) == 1
        assert history.entries[0] is entry

    def test_append_preserves_order(self):
        history = History()
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        first = HistoryEntry(expression="1 + 1", result="2", timestamp=ts)
        second = HistoryEntry(expression="3 * 4", result="12", timestamp=ts)
        history.append(first)
        history.append(second)
        assert history.entries[0] is first
        assert history.entries[1] is second

    def test_clear_all(self):
        history = History()
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        history.append(
            HistoryEntry(expression="1 + 1", result="2", timestamp=ts)
        )
        history.clear_all()
        assert history.entries == []

    def test_init_from_entries(self):
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        entries = [HistoryEntry(expression="5 - 2", result="3", timestamp=ts)]
        history = History(entries=entries)
        assert len(history.entries) == 1

    def test_append_unlimited_by_default(self):
        history = History()
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        for i in range(600):
            history.append(
                HistoryEntry(expression=str(i), result=str(i), timestamp=ts),
            )
        assert len(history.entries) == 600

    def test_append_trims_oldest_when_capped(self):
        history = History(max_entries=2)
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        for i in range(3):
            history.append(
                HistoryEntry(expression=str(i), result=str(i), timestamp=ts),
            )
        assert [e.expression for e in history.entries] == ["1", "2"]

    def test_trim_to_drops_oldest(self):
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        entries = [
            HistoryEntry(expression=str(i), result=str(i), timestamp=ts)
            for i in range(5)
        ]
        history = History(entries=entries)
        history.trim_to(2)
        assert [e.expression for e in history.entries] == ["3", "4"]
        assert history.max_entries == 2

    def test_trim_to_none_lifts_cap(self):
        history = History(max_entries=1)
        history.trim_to(None)
        assert history.max_entries is None

    def test_append_with_zero_cap_keeps_nothing(self):
        history = History(max_entries=0)
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        history.append(HistoryEntry(expression="1", result="1", timestamp=ts))
        assert history.entries == []

    def test_trim_to_zero_empties_history(self):
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        entries = [
            HistoryEntry(expression=str(i), result=str(i), timestamp=ts)
            for i in range(3)
        ]
        history = History(entries=entries)
        history.trim_to(0)
        assert history.entries == []

    def test_trim_to_larger_than_length_keeps_all(self):
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        history = History(
            entries=[HistoryEntry(expression="1", result="1", timestamp=ts)],
        )
        history.trim_to(10)
        assert len(history.entries) == 1
