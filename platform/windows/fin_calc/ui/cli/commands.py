"""Present calculation results and saved history on the command line."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import typer

from fin_calc.application.session import load_session
from fin_calc.config.logging.log_config import configure_logging
from fin_calc.domains.calc.errors import EvaluationError
from fin_calc.domains.calc.formatting import format_history_line

if TYPE_CHECKING:
    from fin_calc.application.session import CalculatorSession


def show_history(session: CalculatorSession) -> None:
    """Print saved expressions using the session's display settings."""
    for entry in session.history.entries:
        typer.echo(
            format_history_line(entry, session.settings.decimal_places),
        )


def calculate(
    expression: Annotated[
        str, typer.Argument(help="Quoted arithmetic expression.")
    ],
) -> None:
    """Evaluate an expression and save it to the calculation history.

    Quote expressions, for example: calculate "0.1 + 0.2". Supports +, -, *,
    /, ^, parentheses, and log(x) (base 10). Use calculate -- "-2 ^ 2" for
    expressions starting with a minus sign. Text input allows 2,048 characters
    and 128 tokens. Saved results retain full precision.
    """
    configure_logging()
    try:
        result = load_session().calculate(expression)
    except (EvaluationError, OSError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1) from error
    typer.echo(result)


def history() -> None:
    """Show saved expressions and results without changing the history file."""
    configure_logging()
    try:
        session = load_session()
    except OSError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1) from error
    show_history(session)
