"""Verify prompt settings persist, validate input, and preserve history."""

import pytest
from typer.testing import CliRunner

from fin_calc.adapters.history_store import load_history
from fin_calc.adapters.settings_store import load_settings
from fin_calc.application import session as session_module
from fin_calc.application import startup
from fin_calc.application.session import CalculatorSession
from fin_calc.config.settings import Settings
from fin_calc.domains.calc.history import History
from fin_calc.ui.cli.app import app


@pytest.fixture
def session(monkeypatch, tmp_path):
    calculator = CalculatorSession(
        History(), Settings(), tmp_path / "history.json",
        tmp_path / "settings.json",
    )
    monkeypatch.setattr(startup, "configure_logging", lambda: None)
    monkeypatch.setattr(startup, "load_session", lambda: calculator)
    monkeypatch.setattr(session_module, "HISTORY_FILE", calculator.history_path)
    monkeypatch.setattr(session_module, "SETTINGS_FILE", calculator.settings_path)
    return calculator


def test_config_display_does_not_write(session):
    result = CliRunner().invoke(app, ["--cli"], input="config\nhelp\nexit\n")
    assert result.exit_code == 0, result.output
    assert "decimal_places = full" in result.stdout
    assert "config <setting> <value>" in result.stdout
    assert not session.settings_path.exists()
    assert not session.history_path.exists()


def test_precision_changes_apply_and_survive_restart(session):
    result = CliRunner().invoke(
        app, ["--cli"],
        input="config decimal_places 4\n1/3\nhistory\nexit\n",
    )
    assert result.exit_code == 0, result.output
    assert "0.3333\n" in result.stdout
    assert "1/3 = 0.3333" in result.stdout
    assert load_history(session.history_path).entries[0].result == "0." + "3" * 28
    restarted = session_module.load_session()
    assert restarted.settings.decimal_places == 4
    assert restarted.calculate("1/3") == "0.3333"
    result = CliRunner().invoke(
        app, ["--cli"], input="config decimal-places full\n1/3\nexit\n"
    )
    assert "0." + "3" * 28 in result.stdout
    assert load_settings(session.settings_path).decimal_places is None


@pytest.mark.parametrize(
    "change",
    ["decimal_places -1", "decimal_places 7", "decimal_places 2.5",
     "max_history_entries 0", "max_history_entries 10001",
     "max_history_entries false", "theme blue", "missing 3", "theme"],
)
def test_invalid_config_keeps_settings_and_prompt(session, change):
    result = CliRunner().invoke(
        app, ["--cli"], input=f"config {change}\n2+2\nexit\n"
    )
    assert result.exit_code == 0, result.output
    assert "Error:" in result.stderr
    assert "4\n" in result.stdout
    assert session.settings == Settings()
    assert not session.settings_path.exists()


def test_history_limit_requires_confirmation_and_applies_on_calculate(session):
    session.calculate("1+1")
    session.calculate("2+2")
    before = session.history_path.read_bytes()
    result = CliRunner().invoke(
        app, ["--cli"], input="config max_history_entries 1\n\nexit\n"
    )
    assert "Settings unchanged." in result.stdout
    assert session.history_path.read_bytes() == before
    assert not session.settings_path.exists()
    result = CliRunner().invoke(
        app, ["--cli"], input="config max_history_entries 1\ny\nexit\n"
    )
    assert "Settings saved." in result.stdout
    assert session.history_path.read_bytes() == before
    assert len(session.history.entries) == 2
    assert len(session_module.load_session().history.entries) == 1
    session.calculate("3+3")
    assert [entry.result for entry in load_history(session.history_path).entries] == ["6"]


def test_theme_and_unlimited_preserve_other_settings(session):
    result = CliRunner().invoke(
        app, ["--cli"],
        input="config decimal_places 2\nconfig theme light\n"
        "config max_history_entries unlimited\nexit\n",
    )
    assert result.exit_code == 0, result.output
    assert load_settings(session.settings_path) == Settings(2, "light", None)
    assert not session.history_path.exists()


def test_settings_write_failure_keeps_active_settings(session, monkeypatch):
    def deny_write(*_args):
        raise PermissionError("settings are read-only")

    monkeypatch.setattr(session_module, "write_settings", deny_write)
    result = CliRunner().invoke(
        app, ["--cli"], input="config decimal_places 2\n1/3\nexit\n"
    )
    assert result.exit_code == 0, result.output
    assert "settings are read-only" in result.stderr
    assert "Settings saved." not in result.stdout
    assert "0." + "3" * 28 in result.stdout
    assert session.settings.decimal_places is None
