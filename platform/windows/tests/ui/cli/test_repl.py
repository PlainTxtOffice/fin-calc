"""Verify repeated input, persistence, recovery, and prompt shutdown."""

from io import StringIO

import pytest
from typer.testing import CliRunner

from fin_calc.adapters.history_store import load_history
from fin_calc.application import session as session_module
from fin_calc.application import startup
from fin_calc.application.session import CalculatorSession
from fin_calc.config.settings import Settings
from fin_calc.domains.calc.history import History
from fin_calc.ui.cli import app as cli_app
from fin_calc.ui.cli import launch, repl


@pytest.fixture
def session(monkeypatch, tmp_path):
    calculator = CalculatorSession(
        History(), Settings(decimal_places=2), tmp_path / "history.json"
    )
    monkeypatch.setattr(startup, "configure_logging", lambda: None)
    monkeypatch.setattr(startup, "load_session", lambda: calculator)
    return calculator


def test_repl_calculates_repeatedly_and_saves_precision(session, monkeypatch):
    loads = []
    monkeypatch.setattr(
        startup, "load_session", lambda: loads.append(True) or session
    )
    result = CliRunner().invoke(
        cli_app.app, ["--cli"], input="1/3\n-2 ^ 2\nhistory\nexit\n9+9\n"
    )
    assert result.exit_code == 0, result.output
    assert "0.33\n" in result.stdout
    assert "4.00\n" in result.stdout
    assert "1/3 = 0.33" in result.stdout
    entries = load_history(session.history_path).entries
    assert [entry.expression for entry in entries] == ["1/3", "-2 ^ 2"]
    assert entries[0].result == "0." + "3" * 28
    assert len(loads) == 1


def test_repl_recovers_from_invalid_expressions(session):
    result = CliRunner().invoke(
        cli_app.app, ["--cli"], input="1/0\nnot an expression\n2+2\nquit\n"
    )
    assert result.exit_code == 0, result.output
    assert "Division by zero" in result.stderr
    assert result.stderr.count("Error:") == 2
    assert "4.00\n" in result.stdout
    assert [entry.result for entry in load_history(session.history_path).entries] == ["4"]


def test_repl_recovers_from_failed_save(session, monkeypatch):
    write_history = session_module.write_history
    attempts = []

    def write_once_writable(history, path):
        attempts.append(True)
        if len(attempts) == 1:
            raise PermissionError("history is read-only")
        write_history(history, path)

    monkeypatch.setattr(session_module, "write_history", write_once_writable)
    result = CliRunner().invoke(
        cli_app.app, ["--cli"], input="1+1\n3+3\nexit\n"
    )
    assert result.exit_code == 0, result.output
    assert "history is read-only" in result.stderr
    assert "2.00\n" not in result.stdout
    assert "6.00\n" in result.stdout
    assert [entry.result for entry in session.history.entries] == ["6"]
    assert [entry.result for entry in load_history(session.history_path).entries] == ["6"]


@pytest.mark.parametrize("ending", ["exit\n", "QUIT\n", ""])
def test_repl_help_blank_and_eof_do_not_save(session, ending):
    result = CliRunner().invoke(
        cli_app.app, ["--cli"], input="\n  \nhelp\nhistory\n" + ending
    )
    assert result.exit_code == 0, result.output
    assert "Expressions need no quotes" in result.stdout
    assert not result.stderr
    assert not session.history_path.exists()


def test_repl_ctrl_c_exits_cleanly(session, monkeypatch, capsys):
    def interrupt(_):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)
    assert repl.run_repl(session) == 0
    assert not capsys.readouterr().err
    assert not session.history_path.exists()


def test_menu_selection_opens_repl(session, monkeypatch, capsys):
    terminal = StringIO("3\n2+3\nexit\n")
    monkeypatch.setattr(terminal, "isatty", lambda: True)
    monkeypatch.setattr(launch.sys, "stdin", terminal)
    assert cli_app.run_app([]) == 0
    output = capsys.readouterr().out
    assert "CLI prompt" in output
    assert "5.00\n" in output
    assert load_history(session.history_path).entries[0].result == "5"


def test_repl_startup_failure_is_reported(monkeypatch):
    def fail_load():
        raise PermissionError("cannot open data folder")

    monkeypatch.setattr(startup, "configure_logging", lambda: None)
    monkeypatch.setattr(startup, "load_session", fail_load)
    result = CliRunner().invoke(cli_app.app, ["--cli"], input="exit\n")
    assert result.exit_code == 1
    assert "Unable to start calculator: cannot open data folder" in result.stderr
    assert "fin-calc>" not in result.stdout
