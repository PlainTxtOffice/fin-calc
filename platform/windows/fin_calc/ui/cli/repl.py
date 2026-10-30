"""Read expressions repeatedly and present saved calculation results."""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer

from fin_calc.domains.calc.errors import EvaluationError
from fin_calc.ui.cli.commands import show_history

if TYPE_CHECKING:
    from fin_calc.application.session import CalculatorSession

_HELP = (
    "Enter an expression, such as 125 * 1.08, and press Enter.\n"
    "Supports +, -, *, /, ^, parentheses, and log(x) (base 10).\n"
    "Expressions need no quotes; negative numbers need no -- prefix.\n"
    "history: show saved calculations; help: show this help.\n"
    "exit or quit: leave the prompt. Ctrl+C or end of input also exits.\n"
    "Successful calculations are saved with full precision."
)


def _read_expressions(session: CalculatorSession) -> None:
    """Read commands until exit, saving results and reporting errors."""
    while True:
        expression = input("fin-calc> ").strip()
        if not expression:
            continue
        command = expression.lower()
        if command in {"exit", "quit"}:
            return
        if command == "help":
            typer.echo(_HELP)
        elif command == "history":
            show_history(session)
        else:
            try:
                result = session.calculate(expression)
            except (EvaluationError, OSError) as error:
                typer.echo(f"Error: {error}", err=True)
            else:
                typer.echo(result)


def run_repl(session: CalculatorSession) -> int:
    """Run a persistent prompt until exit, EOF, or Ctrl+C.

    Each successful calculation is saved immediately through the session.
    Invalid expressions and failed saves print an error and allow retrying.
    Normal exit, EOF, and Ctrl+C return status zero.
    """
    typer.echo("Fin Calc — type help for commands, exit to quit.")
    try:
        _read_expressions(session)
    except (EOFError, KeyboardInterrupt):
        typer.echo()
    return 0
