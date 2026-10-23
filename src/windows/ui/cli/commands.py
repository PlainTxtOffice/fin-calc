"""Present calculation results and saved history on the command line."""

from __future__ import annotations

from typing import Annotated

import typer

from src.windows.application.session import load_session
from src.windows.config.logging.log_config import configure_logging
from src.windows.domains.calc.errors import EvaluationError
from src.windows.domains.calc.formatting import format_result


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
    for entry in session.history.entries:
        result = format_result(entry.result, session.settings.decimal_places)
        typer.echo(f"{entry.expression} = {result}")
