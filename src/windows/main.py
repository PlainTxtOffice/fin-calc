"""Launch the requested calculator interface."""

import sys

from src.windows.ui.cli.app import run_app


def main() -> int:
    """Parse launch options and run the selected interface."""
    return run_app()


if __name__ == "__main__":
    sys.exit(main())
