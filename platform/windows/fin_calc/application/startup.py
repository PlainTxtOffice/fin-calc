"""Initialize state and import only the selected interactive toolkit."""

from __future__ import annotations

from typing import Literal

from fin_calc.application.session import load_session
from fin_calc.config.logging.log_config import configure_logging


def launch_interface(interface: Literal["gui", "tui", "cli"]) -> int:
    """Load saved state and start one interactive interface."""
    configure_logging()
    session = load_session()
    if interface == "cli":
        from fin_calc.ui.cli.repl import run_repl  # noqa: PLC0415

        return run_repl(session)
    if interface == "gui":
        from fin_calc.ui.gui.app import run_app  # noqa: PLC0415

        return run_app(session.history, session.settings)
    from fin_calc.ui.tui.app import run_app as run_tui  # noqa: PLC0415

    return run_tui(session)
