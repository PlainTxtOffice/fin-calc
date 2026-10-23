"""Initialize state and import only the selected interactive toolkit."""

from __future__ import annotations

from typing import Literal

from src.windows.application.session import load_session
from src.windows.config.logging.log_config import configure_logging


def launch_interface(interface: Literal["gui", "tui"]) -> int:
    """Load saved state and start one interactive interface."""
    configure_logging()
    session = load_session()
    if interface == "gui":
        from src.windows.ui.gui.app import run_app  # noqa: PLC0415

        return run_app(session.history, session.settings)
    from src.windows.ui.tui.app import run_app as run_tui  # noqa: PLC0415

    return run_tui(session)
