"""Tests for the history store adapter."""

from datetime import datetime, timezone
from pathlib import Path

from fin_calc.adapters.history_store import load_history, write_history
from fin_calc.domains.calc.history import History, HistoryEntry


class TestHistoryStoreRoundTrip:
    """Tests for JSON persistence round-trip."""

    def test_write_then_load(self, tmp_path: Path):
        file = tmp_path / "history.json"
        ts = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
        history = History()
        history.append(HistoryEntry("1 + 1", "2", ts))
        history.append(HistoryEntry("3 * 4", "12", ts))

        write_history(history, file)
        loaded = load_history(file)

        assert len(loaded.entries) == 2
        assert loaded.entries[0].expression == "1 + 1"
        assert loaded.entries[0].result == "2"
        assert loaded.entries[1].expression == "3 * 4"

    def test_load_nonexistent_file(self, tmp_path: Path):
        file = tmp_path / "missing.json"
        loaded = load_history(file)
        assert loaded.entries == []

    def test_load_empty_file(self, tmp_path: Path):
        file = tmp_path / "empty.json"
        file.write_text("")
        loaded = load_history(file)
        assert loaded.entries == []

    def test_load_corrupt_file(self, tmp_path: Path):
        file = tmp_path / "bad.json"
        file.write_text("{not valid json!!!")
        loaded = load_history(file)
        assert loaded.entries == []

    def test_load_non_list_json(self, tmp_path: Path):
        file = tmp_path / "bad_shape.json"
        file.write_text('{"expression": "1 + 1"}')
        loaded = load_history(file)
        assert loaded.entries == []

    def test_load_entry_with_missing_field(self, tmp_path: Path):
        file = tmp_path / "bad_entry.json"
        file.write_text('[{"expression": "1 + 1", "result": "2"}]')
        loaded = load_history(file)
        assert loaded.entries == []

    def test_timestamp_preserved(self, tmp_path: Path):
        file = tmp_path / "history.json"
        ts = datetime(2026, 3, 30, 14, 30, 15, tzinfo=timezone.utc)
        history = History()
        history.append(HistoryEntry("5 + 5", "10", ts))

        write_history(history, file)
        loaded = load_history(file)

        assert loaded.entries[0].timestamp == ts
