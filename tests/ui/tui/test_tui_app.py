"""Drive actual Textual input, error recovery, history, and quit bindings."""

import asyncio

from textual.widgets import Input, RichLog, Static

from src.windows.adapters.history_store import load_history
from src.windows.application.session import CalculatorSession
from src.windows.domains.calc.history import History
from src.windows.config.settings import Settings
from src.windows.ui.tui.app import CalculatorApp


def test_terminal_calculation_error_recovery_and_quit(tmp_path):
    session = CalculatorSession(
        History(), Settings(decimal_places=2), tmp_path / "history.json"
    )

    async def exercise():
        app = CalculatorApp(session)
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.press(*"0.1+0.2", "enter")
            assert "0.30" in str(app.query_one("#result", Static).content)
            assert load_history(session.history_path).entries[0].result == "0.3"
            assert app.query_one(RichLog).lines
            await pilot.press(*"1/0", "enter")
            assert "Division by zero" in str(
                app.query_one("#result", Static).content
            )
            assert len(session.history.entries) == 1
            await pilot.press("escape")
            assert app.query_one(Input).value == ""
            await pilot.press(*"2^10", "enter")
            assert session.history.entries[-1].result == "1024"
            await pilot.press("ctrl+q")
        assert app.return_code == 0

    asyncio.run(exercise())


def test_terminal_loads_history_and_reports_save_errors(tmp_path, monkeypatch):
    session = CalculatorSession(
        History(), Settings(theme="light"), tmp_path / "history.json"
    )
    session.calculate("2+3")

    def deny_write(*args):
        raise PermissionError("read-only history")

    async def exercise():
        app = CalculatorApp(session)
        async with app.run_test(size=(80, 24)) as pilot:
            assert app.theme == "textual-light"
            assert app.query_one(RichLog).lines
            monkeypatch.setattr(
                "src.windows.application.session.write_history", deny_write
            )
            await pilot.press(*"3+4", "enter")
            assert "read-only history" in str(
                app.query_one("#result", Static).content
            )
            assert len(session.history.entries) == 1

    asyncio.run(exercise())
