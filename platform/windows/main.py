"""Launch the packaged GUI by default while preserving explicit CLI options."""

import sys

from fin_calc.ui.cli.app import run_app

if __name__ == "__main__":
    sys.exit(run_app(sys.argv[1:] or ["--gui"]))
