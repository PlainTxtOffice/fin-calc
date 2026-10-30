"""Verify calculator workflows preserve precision and report write failures."""

from pathlib import Path

import pytest

from fin_calc.adapters.history_store import load_history, write_history
from fin_calc.application.session import CalculatorSession
from fin_calc.domains.calc.errors import EvaluationError
from fin_calc.domains.calc.history import History
from fin_calc.config.settings import Settings


def test_history_roundtrip_retains_precision_and_applies_cap(tmp_path):
    path = tmp_path / "history.json"
    session = CalculatorSession(
        History(), Settings(decimal_places=2, max_history_entries=1), path
    )
    assert session.calculate("1 / 3") == "0.33"
    assert load_history(path).entries[0].result.startswith("0.333333333")
    assert session.calculate("2 + 2") == "4.00"
    assert len(session.history.entries) == 1
    assert load_history(path).entries[0].expression == "2 + 2"


def test_invalid_expression_does_not_write(tmp_path):
    path = tmp_path / "history.json"
    session = CalculatorSession(History(), Settings(), path)
    with pytest.raises(EvaluationError):
        session.calculate("1/0")
    assert not path.exists()
    assert not session.history.entries


def test_write_failure_does_not_claim_saved_result(monkeypatch, tmp_path):
    path = tmp_path / "history.json"
    session = CalculatorSession(History(), Settings(), path)

    def deny_write(*args, **kwargs):
        raise PermissionError("read-only history")

    monkeypatch.setattr(Path, "write_text", deny_write)
    with pytest.raises(PermissionError):
        write_history(History(), path)
    with pytest.raises(PermissionError):
        session.calculate("1+1")
    assert not session.history.entries
