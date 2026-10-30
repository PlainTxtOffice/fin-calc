"""Compose Typer commands and dispatch explicit interface selections."""

from __future__ import annotations

from typing import Annotated

import typer

from fin_calc.application.startup import launch_interface
from fin_calc.ui.cli.commands import calculate, history
from fin_calc.ui.cli.launch import Interface, choose_interface

app = typer.Typer(
    add_completion=False,
    pretty_exceptions_enable=False,
    rich_markup_mode=None,
    help="Fin Calc: Decimal arithmetic with shared calculation history.",
    epilog=(
        'Examples: fin-calc --cli; fin-calc calculate "0.1 + 0.2". '
        "Use calculate --help for expression syntax. See docs/USER_MANUAL.md."
    ),
)
app.command()(calculate)
app.command(short_help="Show saved expressions and results.")(history)


@app.callback(invoke_without_command=True)
def select_interface(
    ctx: typer.Context,
    *,
    gui: Annotated[
        bool, typer.Option("--gui", help="Open the graphical calculator.")
    ] = False,
    tui: Annotated[
        bool,
        typer.Option("--tui", help="Open the Textual terminal calculator."),
    ] = False,
    cli: Annotated[
        bool, typer.Option("--cli", help="Open the prompt or run a command.")
    ] = False,
) -> None:
    """Select an interface before loading state or importing a toolkit."""
    if sum((gui, tui, cli)) > 1:
        msg = "Use only one of --gui, --tui, or --cli."
        raise typer.BadParameter(msg)
    if ctx.invoked_subcommand is not None:
        if gui or tui:
            msg = "GUI/TUI launch flags cannot be combined with CLI commands."
            raise typer.BadParameter(msg)
        return
    interface: Interface | None = (
        "gui" if gui else "tui" if tui else "cli" if cli else None
    )
    if interface is None:
        interface = choose_interface()
    if interface is not None:
        try:
            status = launch_interface(interface)
        except OSError as error:
            typer.echo(f"Unable to start calculator: {error}", err=True)
            raise typer.Exit(1) from error
        raise typer.Exit(status)


def run_app(args: list[str] | None = None) -> int:
    """Run Typer and return its exit status to the program entrypoint."""
    try:
        app(args=args, prog_name="fin-calc")
    except SystemExit as error:
        return error.code if isinstance(error.code, int) else 1
    return 0
