"""Prompt for an interface only when interactive input is available."""

from __future__ import annotations

import sys
from typing import Literal

import typer

Interface = Literal["gui", "tui", "cli"]
_CHOICES: dict[str, Interface] = {
    "1": "gui",
    "gui": "gui",
    "2": "tui",
    "tui": "tui",
    "3": "cli",
    "cli": "cli",
}


def choose_interface() -> Interface | None:
    """Return the selected interface, or None when the user quits."""
    if not sys.stdin.isatty():
        msg = "Choose --gui, --tui, --cli, or a command; use --help for usage."
        raise typer.BadParameter(msg)
    typer.echo(
        "Choose an interface:\n"
        "  1. GUI (python -m src.windows.main --gui)\n"
        "  2. TUI (python -m src.windows.main --tui)\n"
        "  3. CLI help (python -m src.windows.main --cli)\n"
        "  q. Quit",
    )
    while True:
        choice = typer.prompt("Selection").strip().lower()
        if choice in {"q", "quit"}:
            return None
        if choice in _CHOICES:
            return _CHOICES[choice]
        typer.echo("Enter 1, 2, 3, or q.")
