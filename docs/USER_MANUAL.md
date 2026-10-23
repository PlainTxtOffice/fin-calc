---
last_updated: 2026-10-22
version: 0.2.0
product_version: "0.1.0"
generated_from: "dev-docs/specs/USER_MANUAL_SPEC.md"
---

# User Manual

## 1. Overview

Fin Calc is a desktop calculator for decimal-precision arithmetic. It provides
an expression display, keypad input, a persistent calculation tape, keyboard
input, settings, and CSV history export.

Supported interfaces are the PySide6 GUI, Textual TUI, and Typer CLI. They use
the same Decimal evaluator, saved settings, and calculation history. This
manual covers the development checkout workflow.

Verified from: `README.md`; `src/windows/ui/gui/views/root_window.py`

## 2. System Requirements

- Python 3.12 or newer.
- PySide6 6.7 or newer.
- Textual 6.6 or newer and Typer 0.21 or newer.
- A Python environment with the project dependencies installed.

The supported operating-system matrix is Unknown.

Verified from: `pyproject.toml`

## 3. Installation & Setup

1. Open a terminal at the repository root.
1. Create a Python virtual environment with `python -m venv .venv`.
1. Install the project and its dependencies:

   ```powershell
   .venv/Scripts/python.exe -m pip install -e ".[dev]"
   ```

1. Start the calculator with the command in the CLI Usage section.
1. Verify setup by entering `0.1 + 0.2` and confirming the result is `0.3`.

Use `.venv/Scripts/python.exe` to run the project. Installation also adds a
`fin-calc` command to the environment's Scripts directory.

Verified from: `pyproject.toml`; `README.md`

## 4. Using the Program in VS Code

Open the repository folder in VS Code, select the project virtual environment,
and open an integrated terminal at the repository root. Run:

```powershell
python -m src.windows.main
```

No repository task file was found. Launch and debug task details are Unknown.

Verified from: `README.md`; `.vscode/settings.json`

## 5. VS Code Tasks

Not Applicable. No `.vscode/tasks.json` file was found.

Verified from: `.vscode/`

## 6. CLI Usage

Run from the repository root. Without arguments, an interactive terminal shows
an interface chooser; `q` exits without loading application state. Redirected
input does not trigger a prompt and requires an explicit command or flag.

```powershell
.venv/Scripts/python.exe -m src.windows.main --gui
.venv/Scripts/python.exe -m src.windows.main --tui
.venv/Scripts/python.exe -m src.windows.main --cli calculate "0.1 + 0.2"
.venv/Scripts/python.exe -m src.windows.main calculate -- "-2 ^ 2"
.venv/Scripts/python.exe -m src.windows.main history
.venv/Scripts/python.exe -m src.windows.main --help
```

`--gui`, `--tui`, and `--cli` are mutually exclusive. GUI/TUI flags cannot be
combined with commands. CLI commands may omit `--cli`; `--cli` alone shows
help. Help never launches a toolkit or loads saved state. Use
`calculate --help` or `history --help` for command help.

`calculate` prints the result and saves successful calculations to history.
`history` prints retained expressions and results without writing the history
file. Invalid input or a write failure returns a nonzero exit status. Quote
expressions; put `--` before an expression beginning with `-`.

Text input supports decimal and scientific notation, `+`, `-`, `*`, `/`, `^`,
parentheses, and base-10 `log(x)`. Unary minus binds tighter than powers:
`-2 ^ 2` yields `4`. Inputs are limited to 2,048 characters and 128 tokens;
unsupported characters are rejected.

### Terminal interface

In the Textual TUI, enter an expression and press Enter to calculate and save.
The tape shows retained history. Escape clears the current input without
deleting history; Ctrl+Q quits. Errors appear beside the input so it can be
corrected. Display precision, history limits, and light/dark theme are loaded
from the same settings file as the GUI. Change settings, reuse tape results,
clear saved history, or export CSV through the GUI; those controls are not yet
provided in the TUI or CLI.

Verified from: `src/windows/main.py`; `src/windows/ui/cli/app.py`;
`src/windows/ui/cli/commands.py`; `src/windows/ui/tui/app.py`;
`src/windows/application/session.py`; `README.md`

## 7. GUI Usage

The main window contains a calculation tape, expression display, and keypad.

1. Enter digits and operators with the keypad or keyboard.
1. Press Enter or Return to evaluate the expression.
1. Click a result in the tape to reuse it in a new expression.
1. Use Backspace to remove the last input character.
1. Use Escape to clear the current expression.
1. Open File to export or clear history, or to exit.
1. Open Edit > Settings to change display and history preferences.
1. Open Help for keyboard shortcuts or application information.

Supported examples include `0.1 + 0.2`, `2 ^ 10`, and `log ( 100 )`.

Verified from: `src/windows/ui/gui/views/root_window.py`;
`src/windows/ui/gui/menus/menu_bar.py`;
`src/windows/ui/gui/dialogs/help_dialogs.py`; `README.md`

## 8. Configuration

| Key or file | Type | Default | Description | Verified from |
| --- | --- | --- | --- | --- |
| `data/history.json` | JSON file | Empty history when absent | Stores calculation entries. | `src/windows/config/path_handler.py`; `src/windows/adapters/history_store.py` |
| `data/settings.json` | JSON file | `dark`, full precision, 1000 entries | Stores application settings. | `src/windows/config/path_handler.py`; `src/windows/config/settings.py` |
| Decimal places | Setting | Full precision | Select full precision or 0 through 6 places. | `src/windows/ui/gui/dialogs/settings_dialog.py` |
| Theme | Setting | Dark | Select Dark or Light. | `src/windows/ui/gui/dialogs/settings_dialog.py` |
| Max history entries | Setting | 1000 | Retain 1 through 10,000 entries, or select Unlimited. | `src/windows/ui/gui/dialogs/settings_dialog.py` |

The application uses repository-local `data/` paths in the development
checkout. Settings are saved when accepted in the Settings dialog.

Verified from: `src/windows/config/path_handler.py`;
`src/windows/ui/gui/dialogs/settings_dialog.py`;
`src/windows/ui/gui/views/root_window.py`

## 9. Outputs, Exports, and Files

- `data/history.json` stores the persistent calculation history.
- `data/settings.json` stores the selected settings.
- `exports/history.csv` is the default suggested CSV export path. The export
  dialog allows another CSV destination.
- `logs/` is the configured log directory.

History is also kept in the in-memory tape while the application is running.

Verified from: `src/windows/config/path_handler.py`;
`src/windows/ui/gui/views/root_window.py`;
`src/windows/adapters/history_export.py`

## 10. Feature Reference

| Feature | Behavior | Verified from |
| --- | --- | --- |
| Decimal arithmetic | Evaluates expressions with `Decimal` values. | `src/windows/domains/calc/evaluator.py` |
| Operators | Supports `+`, `-`, `*`, `/`, and `^`. | `src/windows/domains/calc/evaluator.py` |
| Parentheses | Supports grouped expressions. | `src/windows/domains/calc/evaluator.py` |
| Base-10 logarithm | Supports `log(expression)` for positive values. | `src/windows/domains/calc/evaluator.py` |
| Tape history | Records expressions, results, and UTC timestamps. | `src/windows/ui/gui/views/root_window.py`; `src/windows/domains/calc/history.py` |
| History reuse | Clicking a tape result inserts it into the current expression. | `src/windows/ui/gui/views/root_window.py` |
| History export | Writes the current history to a CSV file. | `src/windows/ui/gui/views/root_window.py`; `src/windows/adapters/history_export.py` |
| Display settings | Controls decimal places and theme. | `src/windows/ui/gui/dialogs/settings_dialog.py` |
| History limit | Trims retained entries to the configured cap. | `src/windows/domains/calc/history.py`; `src/windows/ui/gui/views/root_window.py` |

Division by zero, invalid expressions, invalid logarithm domains, mismatched
parentheses, and out-of-range results are reported as evaluation errors.

Verified from: `src/windows/domains/calc/evaluator.py`;
`src/windows/ui/gui/views/root_window.py`

## 11. Troubleshooting

| Symptom | Likely cause | Resolution | Verified from |
| --- | --- | --- | --- |
| The window does not start | Dependencies are unavailable. | Activate the project environment and install the project dependencies. | `pyproject.toml`; `src/windows/main.py` |
| Saved history is missing | The history file is absent, empty, or invalid. | Check `data/history.json`; the application starts with empty history when it cannot load valid entries. | `src/windows/adapters/history_store.py` |
| An expression is rejected | The expression is invalid or uses an unsupported domain. | Check operators, parentheses, division values, and logarithm input. | `src/windows/domains/calc/evaluator.py` |
| CSV export reports an error | The selected destination cannot be written. | Choose a writable `.csv` destination. | `src/windows/ui/gui/views/root_window.py` |

Verified from: `src/windows/adapters/history_store.py`;
`src/windows/domains/calc/evaluator.py`;
`src/windows/ui/gui/views/root_window.py`

## 12. FAQ

### Does Fin Calc preserve decimal arithmetic?

Yes. It evaluates with Python `Decimal`, so `0.1 + 0.2` produces `0.3`.

Verified from: `README.md`; `src/windows/domains/calc/evaluator.py`

### Where is calculation history stored?

In `data/history.json` in the development checkout.

Verified from: `src/windows/config/path_handler.py`;
`src/windows/adapters/history_store.py`

### Can I change the theme and history size?

Yes. Use Edit > Settings to select the theme, decimal display, and history
limit.

Verified from: `src/windows/ui/gui/menus/menu_bar.py`;
`src/windows/ui/gui/dialogs/settings_dialog.py`

## 13. Glossary

- **Decimal arithmetic**: Arithmetic based on decimal values rather than binary
  floating-point values.
- **Expression**: The calculation currently being entered, such as `2 + 3`.
- **Tape**: The scrollable list of previous calculations and results.
- **History entry**: A stored expression, result, and UTC timestamp.
- **Full precision**: Displaying the calculated result without a configured
  decimal-place limit.

Verified from: `README.md`; `src/windows/domains/calc/history.py`;
`src/windows/config/settings.py`
