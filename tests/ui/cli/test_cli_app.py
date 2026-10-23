"""Exercise command parsing, launch selection, and persistent calculations."""

import subprocess
import sys

import pytest
from typer.testing import CliRunner

from src.windows.adapters.history_store import load_history
from src.windows.application.session import CalculatorSession
from src.windows.domains.calc.history import History
from src.windows.config.settings import Settings
from src.windows.ui.cli import app as cli_app
from src.windows.ui.cli import commands, launch


@pytest.fixture
def session(monkeypatch, tmp_path):
    session = CalculatorSession(
        History(), Settings(), tmp_path / "history.json"
    )
    monkeypatch.setattr(commands, "configure_logging", lambda: None)
    monkeypatch.setattr(commands, "load_session", lambda: session)
    return session


def test_calculate_and_history_share_saved_state(session):
    runner = CliRunner()
    result = runner.invoke(cli_app.app, ["--cli", "calculate", "0.1 + 0.2"])
    assert result.exit_code == 0, result.output
    assert result.stdout == "0.3\n"
    assert load_history(session.history_path).entries[0].result == "0.3"
    before = session.history_path.read_bytes()
    result = runner.invoke(cli_app.app, ["history"])
    assert result.exit_code == 0
    assert result.stdout == "0.1 + 0.2 = 0.3\n"
    assert session.history_path.read_bytes() == before


def test_calculation_error_and_negative_expression(session):
    runner = CliRunner()
    result = runner.invoke(cli_app.app, ["calculate", "1/0"])
    assert result.exit_code == 1
    assert "Division by zero" in result.output
    assert not session.history_path.exists()
    result = runner.invoke(cli_app.app, ["calculate", "--", "-2 ^ 2"])
    assert result.exit_code == 0
    assert result.stdout == "4\n"


@pytest.mark.parametrize(
    "args",
    [["--gui", "--tui"], ["--cli", "--gui"], ["--tui", "calculate", "1+1"]],
)
def test_conflicting_modes_do_not_launch(monkeypatch, args):
    monkeypatch.setattr(
        cli_app, "launch_interface", lambda _: pytest.fail("unexpected launch")
    )
    assert CliRunner().invoke(cli_app.app, args).exit_code == 2


@pytest.mark.parametrize("mode", ["gui", "tui"])
def test_explicit_mode_launches_only_requested_interface(monkeypatch, mode):
    calls = []
    monkeypatch.setattr(
        cli_app,
        "launch_interface",
        lambda selected: calls.append(selected) or 7,
    )
    result = CliRunner().invoke(cli_app.app, [f"--{mode}"])
    assert result.exit_code == 7
    assert calls == [mode]


def test_no_arguments_noninteractive_fails_without_waiting(monkeypatch):
    monkeypatch.setattr(launch.sys.stdin, "isatty", lambda: False)
    result = CliRunner().invoke(cli_app.app, [])
    assert result.exit_code == 2
    assert "--help" in result.output


def test_chooser_reprompts_and_quit_is_side_effect_free(monkeypatch):
    monkeypatch.setattr(launch.sys.stdin, "isatty", lambda: True)
    answers = iter(["bad", "Q"])
    monkeypatch.setattr(launch.typer, "prompt", lambda _: next(answers))
    monkeypatch.setattr(
        cli_app, "launch_interface", lambda _: pytest.fail("unexpected launch")
    )
    assert cli_app.run_app([]) == 0


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        ["--cli"],
        ["calculate", "--help"],
        ["--cli", "history", "--help"],
    ],
)
def test_help_imports_no_toolkits_and_loads_no_state(monkeypatch, args):
    monkeypatch.setattr(
        commands, "load_session", lambda: pytest.fail("unexpected state load")
    )
    assert CliRunner().invoke(cli_app.app, args).exit_code == 0
    code = (
        "import sys; from src.windows.ui.cli.app import run_app; "
        f"assert run_app({args!r}) == 0; "
        "assert not any(m.startswith(('PySide6', 'textual')) for m in sys.modules)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
