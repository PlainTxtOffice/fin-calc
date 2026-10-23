"""Compose and launch the Textual calculator."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer, Header, Input, RichLog, Static

from src.windows.domains.calc.errors import EvaluationError
from src.windows.domains.calc.formatting import format_result

if TYPE_CHECKING:
    from src.windows.application.session import CalculatorSession


class CalculatorApp(App[None]):
    """Present expression entry, results, and persisted calculation history."""

    TITLE = "Fin Calc"
    CSS = """
    #tape { height: 1fr; border: round $primary; }
    #result { height: auto; min-height: 3; padding: 1; }
    #expression { margin: 0 1 1 1; }
    """
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("escape", "clear_input", "Clear input"),
    ]

    def __init__(self, session: CalculatorSession) -> None:
        """Use a loaded session without opening files during composition."""
        super().__init__()
        self.session = session
        self.theme = (
            "textual-light"
            if session.settings.theme == "light"
            else "textual-dark"
        )

    def compose(self) -> ComposeResult:
        """Create the history tape, result area, and expression field."""
        yield Header()
        yield RichLog(id="tape", wrap=True, markup=False, highlight=False)
        yield Static(
            "Enter an expression and press Enter.", id="result", markup=False
        )
        yield Input(
            placeholder="Example: 0.1 + 0.2 or log(100)", id="expression"
        )
        yield Footer()

    def _refresh_tape(self) -> None:
        tape = self.query_one("#tape", RichLog)
        tape.clear()
        for entry in self.session.history.entries:
            result = format_result(
                entry.result, self.session.settings.decimal_places
            )
            tape.write(f"{entry.expression} = {result}")

    def on_mount(self) -> None:
        """Display the saved tape and focus expression entry."""
        self._refresh_tape()
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Delegate calculation and persistence, keeping errors in the UI."""
        output = self.query_one("#result", Static)
        try:
            result = self.session.calculate(event.value)
        except (EvaluationError, OSError) as error:
            output.update(f"Error: {error}")
            return
        output.update(f"Result: {result}")
        self._refresh_tape()
        event.input.clear()

    def action_clear_input(self) -> None:
        """Clear expression entry without deleting saved history."""
        self.query_one(Input).clear()
        self.query_one("#result", Static).update(
            "Enter an expression and press Enter."
        )


def run_app(session: CalculatorSession) -> int:
    """Run the terminal interface and return its process exit status."""
    app = CalculatorApp(session)
    app.run()
    return app.return_code or 0
