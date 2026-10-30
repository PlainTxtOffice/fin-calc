"""Present settings and confirm potentially destructive retention changes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer

from fin_calc.domains.calc.formatting import MAX_DECIMAL_PLACES
from fin_calc.domains.calc.history import MAX_HISTORY_CAP, MIN_HISTORY_CAP
from fin_calc.ui.cli.settings.values import parse_setting

if TYPE_CHECKING:
    from fin_calc.application.session import CalculatorSession


def show_settings(session: CalculatorSession) -> None:
    """Show saved preferences and the command syntax for changing them."""
    settings = session.settings
    places = settings.decimal_places
    cap = settings.max_history_entries
    typer.echo(f"decimal_places = {'full' if places is None else places}")
    typer.echo(f"max_history_entries = {'unlimited' if cap is None else cap}")
    typer.echo(f"theme = {settings.theme} (graphical interface)")
    typer.echo(
        f"Use config decimal_places <0-{MAX_DECIMAL_PLACES}|full>, "
        f"config max_history_entries <{MIN_HISTORY_CAP}-{MAX_HISTORY_CAP}"
        "|unlimited>, or config theme <dark|light>.\n"
        "Decimal places controls display only; saved results keep full "
        "calculation precision. History limits apply on the next calculation "
        "or restart. Theme does not change this console window."
    )


def run_config(session: CalculatorSession, arguments: list[str]) -> None:
    """Apply a validated setting, keeping the prompt usable after failures."""
    if not arguments or arguments == ["help"]:
        show_settings(session)
        return
    try:
        name, value = arguments
    except ValueError:
        typer.echo("Error: Use config <setting> <value>, or config.", err=True)
        return
    try:
        settings = parse_setting(session.settings, name, value)
        cap = settings.max_history_entries
        if (
            cap is not None
            and cap != session.settings.max_history_entries
            and cap < len(session.history.entries)
        ):
            confirmed = typer.confirm(
                "This limit will discard older history on the next "
                "calculation or restart. Continue?",
                default=False,
            )
            if not confirmed:
                typer.echo("Settings unchanged.")
                return
        session.update_settings(settings)
    except typer.Abort:
        typer.echo("Settings unchanged.")
        return
    except (ValueError, OSError) as error:
        typer.echo(f"Error: {error}", err=True)
        return
    typer.echo("Settings saved.")
    show_settings(session)
