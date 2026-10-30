---
last_updated: 2026-10-30
version: 5.2.0
product_versions:
  windows: "0.1.0"
  ios: "0.1.0"
  android: "0.1.0"
generated_from: "dev-docs/specs/USER_MANUAL_SPEC.instructions.md"
---

# User Manual

## Overview

Fin Calc is a calculator for exact decimal arithmetic. It adds, subtracts,
multiplies, divides, raises to powers, and takes base-10 logarithms using
decimal numbers, so `0.1 + 0.2` gives `0.3` rather than a binary rounding
error. Every successful calculation is saved to a scrolling list called the
tape, which you can reuse, clear, and export as a CSV file.

Fin Calc is for anyone who wants predictable decimal results and a running
record of their calculations, such as when checking figures or totals.

<!-- Verified from: platform/windows/pyproject.toml [project.description] -->
<!-- Verified from: platform/windows/fin_calc/domains/calc/evaluator.py [evaluate] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow] -->

Fin Calc runs on three platforms. Each keeps its own saved history and
settings; nothing is synchronized between them.

| Platform | Interfaces | Version |
| --- | --- | --- |
| Windows | Graphical window, terminal interface, and command line | 0.1.0 |
| iOS (iPhone and iPad) | Touch app | 0.1.0 |
| Android | Touch app | 0.1.0 |

<!-- Verified from: platform/windows/fin_calc/ui/cli/app.py [select_interface] -->
<!-- Verified from: platform/windows/pyproject.toml [project.version] -->
<!-- Verified from: platform/ios/FinCalc.xcodeproj/project.pbxproj [MARKETING_VERSION, TARGETED_DEVICE_FAMILY] -->
<!-- Verified from: platform/ios/FinCalc/Config/PathHandler.swift [PathHandler] -->
<!-- Verified from: platform/android/app/build.gradle.kts [versionName] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorModel.kt [CalculatorModel] -->

## Installation and Setup

### Check System Requirements

| Platform | Requirement |
| --- | --- |
| Windows | Python 3.12 or newer. The supported Windows versions are Unknown. |
| iOS | iOS or iPadOS 26.4 or newer on an iPhone or iPad. |
| Android | Android 8.0 (API level 26) or newer. |

<!-- Verified from: platform/windows/pyproject.toml [requires-python] -->
<!-- Verified from: platform/ios/FinCalc.xcodeproj/project.pbxproj [IPHONEOS_DEPLOYMENT_TARGET, TARGETED_DEVICE_FAMILY] -->
<!-- Verified from: platform/android/app/build.gradle.kts [minSdk] -->

The Windows version also needs the PySide6 (6.7 or newer), Textual (6.6 or
newer), and Typer (0.21 or newer) packages. The installation step below
installs them for you.

<!-- Verified from: platform/windows/pyproject.toml [project.dependencies] -->

### Install Fin Calc

#### Install on Windows

Fin Calc for Windows runs from its project folder inside a Python virtual
environment. Where to download the project folder is Unknown.

1. Install Python 3.12 or newer.
1. Open PowerShell in the project's `platform/windows/` folder.
1. Create the virtual environment:

   ```powershell
   python -m venv .venv
   ```

1. Install Fin Calc and its required packages into the environment:

   ```powershell
   .venv/Scripts/python.exe -m pip install --editable .
   ```

1. Confirm the installation by showing the help text:

   ```powershell
   .venv/Scripts/python.exe -m fin_calc.main --help
   ```

   The help starts with
   `Fin Calc: Decimal arithmetic with shared calculation history.`

Installing also adds a `fin-calc` command at `.venv/Scripts/fin-calc.exe`.
Install with `--editable` as shown so that your saved data stays in the
`platform/windows/` folder; see [Your Data Files](#your-data-files).

<!-- Verified from: platform/windows/pyproject.toml [project.scripts, requires-python] -->
<!-- Verified from: platform/windows/fin_calc/ui/cli/app.py [app] -->
<!-- Verified from: platform/windows/fin_calc/config/path_handler.py [DEV_ROOT, ROOT_DIR] -->

A packaged Windows program also exists. It opens the graphical window when
started without options and stores its data in a different folder; see
[Data Files on Windows](#data-files-on-windows). Where to obtain a packaged
copy is Unknown.

<!-- Verified from: platform/windows/main.py -->
<!-- Verified from: platform/windows/fin_calc/config/path_handler.py [IS_COMPILED, USER_DATA_DIR] -->

#### Install on iOS

Unknown. No App Store or TestFlight release is available. The app's bundle
identifier is `com.tripp.fin-calc` and its Home Screen name is **Fin Calc**.

<!-- Verified from: platform/ios/FinCalc.xcodeproj/project.pbxproj [PRODUCT_BUNDLE_IDENTIFIER, INFOPLIST_KEY_CFBundleDisplayName] -->

#### Install on Android

Unknown. No published store release was found. The app's application ID is
`com.tripp.fincalc` and its launcher name is **Fin Calc**. The app
requests no special permissions, such as network or storage access.

<!-- Verified from: platform/android/app/build.gradle.kts [applicationId] -->
<!-- Verified from: platform/android/app/src/main/res/values/strings.xml [app_name] -->
<!-- Verified from: platform/android/app/src/main/AndroidManifest.xml -->

### Set Up Fin Calc for First Use

No setup is required. On first start, Fin Calc uses its default settings: full
precision, the Dark theme, and a limit of 1,000 saved history entries. The
first calculation or settings change creates the data files. To change the
defaults, see [Settings and Preferences](#settings-and-preferences).

<!-- Verified from: platform/windows/fin_calc/config/settings.py [Settings] -->
<!-- Verified from: platform/windows/fin_calc/adapters/history_store.py [load_history, write_history] -->
<!-- Verified from: platform/ios/FinCalc/Config/Settings.swift [Settings] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/config/Settings.kt [Settings] -->

## Starting the Program

### Start Fin Calc

#### Start on Windows

Run every command from the `platform/windows/` folder.

| To open | Command |
| --- | --- |
| A menu that asks which interface to use | `.venv/Scripts/python.exe -m fin_calc.main` |
| The graphical window | `.venv/Scripts/python.exe -m fin_calc.main --gui` |
| The terminal interface | `.venv/Scripts/python.exe -m fin_calc.main --tui` |
| The command-line help | `.venv/Scripts/python.exe -m fin_calc.main --cli` |

You can use `.venv/Scripts/fin-calc.exe` in place of
`.venv/Scripts/python.exe -m fin_calc.main` in any command, for example
`.venv/Scripts/fin-calc.exe --gui`.

<!-- Verified from: platform/windows/fin_calc/ui/cli/app.py [select_interface] -->
<!-- Verified from: platform/windows/pyproject.toml [project.scripts] -->

When you start without an option, Fin Calc shows this menu:

```text
Choose an interface:
  1. GUI (python -m fin_calc.main --gui)
  2. TUI (python -m fin_calc.main --tui)
  3. CLI prompt (python -m fin_calc.main --cli)
  q. Quit
Selection:
```

Type `1`, `2`, or `3` (or `gui`, `tui`, or `cli`) and press **Enter**. Type
`q` to leave without starting. Any other entry shows
`Enter 1, 2, 3, or q.` If input comes from a file or another program instead
of the keyboard, the menu is not shown; give an option or a command instead.

<!-- Verified from: platform/windows/fin_calc/ui/cli/launch.py [choose_interface] -->

What to expect on startup:

- **Graphical window**: a window titled **Fin Calc** opens with your saved
  tape, an empty display, and the keypad.
- **Terminal interface**: the screen shows a **Fin Calc** header, your saved
  tape, the prompt `Enter an expression and press Enter.`, and an entry field
  with the hint `Example: 0.1 + 0.2 or log(100)`.
- **Command line**: `--cli` opens a persistent `fin-calc>` prompt. Commands
  such as `calculate` print their output and return to the system shell. See
  [Use the Windows Command Line](#use-the-windows-command-line).

If the saved data folder cannot be used, Fin Calc prints
`Unable to start calculator:` followed by the reason.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow.__init__] -->
<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp.compose] -->
<!-- Verified from: platform/windows/fin_calc/ui/cli/app.py [select_interface] -->

A packaged Windows program opens the graphical window when started without
options. It accepts the same options and commands.

<!-- Verified from: platform/windows/main.py -->

#### Start on iOS

Tap **Fin Calc** on the Home Screen. The calculator opens with your saved tape
at the top, the display showing `0`, and the keypad below. When the tape is
empty, it shows `Calculations appear here`.

<!-- Verified from: platform/ios/FinCalc/FinCalcApp.swift [FinCalcApp] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/TapeView.swift [TapeView] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/DisplayView.swift [DisplayView] -->

#### Start on Android

Tap **Fin Calc** in the app launcher. While saved data loads, the status line
shows `Loading…` and the **⋮** menu does not open. If the saved data cannot be
read, the status line shows
`Could not load saved history and settings. Defaults are in use.`

<!-- Verified from: platform/android/app/src/main/AndroidManifest.xml -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorModel.kt [ScreenState, CalculatorModel.init] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/MainActivity.kt [showMenu] -->

### Quit Fin Calc

#### Quit on Windows

- **Graphical window**: choose **File** > **Exit**, or close the window.
  Fin Calc finishes saving history before it closes.
- **Terminal interface**: press **Ctrl+Q**.
- **Command line**: at `fin-calc>`, type `exit` or `quit`, press **Ctrl+C**, or
  end input (**Ctrl+Z**, then **Enter** on Windows). One-shot commands end on
  their own.

<!-- Verified from: platform/windows/fin_calc/ui/gui/menus/menu_bar.py [build_menu_bar] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow.closeEvent] -->
<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp.BINDINGS] -->

#### Quit on iOS

The app has no quit command. Leave it as you leave any app. Fin Calc finishes
saving history when it moves to the background.

<!-- Verified from: platform/ios/FinCalc/FinCalcApp.swift [FinCalcApp.body] -->

#### Quit on Android

The app has no quit command. Leave it as you leave any app. Each change is
saved as soon as it is made.

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorSession.kt [commit] -->

## Getting Around

The touch apps and the Windows graphical window share the same layout:

- **Tape**: the list of saved calculations, each shown as
  `expression = result`, newest at the bottom.
- **Display**: the expression you are entering, or the result after you
  evaluate. A status line under it shows errors.
- **Keypad**: number, operator, and action keys.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow.__init__] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.body] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/ui/CalculatorView.kt [CalculatorView] -->

The keypad has these keys on every platform:

| Key | What it does |
| --- | --- |
| **0**–**9**, **.** | Enter a number. |
| **+**, **-**, **\***, **/**, **^** | Add, subtract, multiply, divide, or raise to a power. |
| **(**, **)** | Group part of an expression. |
| **log** | Start a base-10 logarithm, such as `log ( 100 )`. |
| **±** | Change the sign of the number being entered. |
| **C** | Clear the whole expression. History is not affected. |
| **←** (Windows) or **⌫** (iOS, Android) | Delete the last character. |
| **=** | Evaluate the expression and save it to the tape. |

The iOS and Android keys show **×** for multiply and **÷** for divide. The iOS
display and tape also show these symbols.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/keypad.py [BUTTON_LAYOUT] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/KeypadView.swift [KeypadView.rows, KeyLabels] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/TapeView.swift [TapeView.row] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/ui/KeypadView.kt [KeypadView] -->

### Tour the Calculator

#### Tour the Windows Graphical Window

The window has a menu bar with **File**, **Edit**, and **Help** menus, then
the tape, the display, and the keypad. Error messages appear in red under the
expression. Messages about exports and settings appear in the status bar at
the bottom of the window. You can also type on the keyboard instead of
clicking keys.

<!-- Verified from: platform/windows/fin_calc/ui/gui/menus/menu_bar.py [build_menu_bar] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/display.py [DisplayView] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._on_export_history, RootWindow.keyPressEvent] -->

#### Tour the Windows Terminal Interface

The terminal interface has a header, a bordered tape, a result line, an entry
field, and a footer that includes **Quit** (**Ctrl+Q**) and **Clear input**
(**Esc**). You type whole expressions into the entry field. The tape is for
reading only.

<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp] -->

#### Tour the Windows Command Line

Start with `--cli` to keep a `fin-calc>` prompt open for repeated calculations.
Type an expression without quotes and press **Enter**. Use `history` to show
saved calculations, `help` for instructions, and `exit` or `quit` to leave.

One-shot use has the form `fin_calc.main [OPTION] COMMAND [ARGUMENT]`.
The commands are `calculate` and `history`. Add `--help` after any command to
see its help.

<!-- Verified from: platform/windows/fin_calc/ui/cli/app.py [app] -->

#### Tour the iOS Screen

The top bar shows **Fin Calc**, a **History** menu (clock icon) on the left,
and a **Settings** button (gear icon) on the right. Below are the tape, the
display, and the keypad, which fills the lower half of the screen. On iPhone
the app stays in portrait; on iPad it turns with the device. When an error
appears, the device gives error haptic feedback.

<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.toolbarContent, RootView.body] -->
<!-- Verified from: platform/ios/FinCalc.xcodeproj/project.pbxproj [INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone, INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad] -->

#### Tour the Android Screen

The top bar shows **Fin Calc** and a **⋮** button that opens the menu. In
portrait, the tape is above the display and keypad. In landscape, the tape is
on the left and the display and keypad are on the right.

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/MainActivity.kt [buildViews] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/ui/CalculatorView.kt [CalculatorView.init] -->

### Find Help

| Platform | Where to find help |
| --- | --- |
| Windows graphical window | **Help** > **Keyboard Shortcuts** lists keyboard keys. **Help** > **About** shows the version. |
| Windows command line | Add `--help`, as in `.venv/Scripts/python.exe -m fin_calc.main calculate --help`. |
| iOS | **Settings** > **About** shows the version. |
| Android | **⋮** > **About** shows the version and short tips. **⋮** > **Privacy Policy** opens the privacy policy. |

<!-- Verified from: platform/windows/fin_calc/ui/gui/dialogs/help_dialogs.py [show_about, show_shortcuts] -->
<!-- Verified from: platform/windows/fin_calc/ui/cli/commands.py [calculate] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/SettingsView.swift [SettingsView.body] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/MainActivity.kt [showMenu] -->

## Everyday Tasks

### Enter and Evaluate an Expression

Expressions use numbers, `+`, `-`, `*`, `/`, `^`, parentheses, and `log( )`
for base-10 logarithms. Operators follow the usual order: parentheses and
`log` first, then a leading minus sign, then powers, then multiplication and
division, then addition and subtraction. Powers group from the right, so
`2 ^ 3 ^ 2` is `512`. A leading minus sign belongs to its number, so
`-2 ^ 2` is `4`.

<!-- Verified from: platform/windows/fin_calc/domains/calc/evaluator.py [module docstring, _Parser] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/Evaluator.swift [Evaluator] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/Evaluator.kt [Evaluator] -->
<!-- Verified from: platform/android/app/src/test/resources/python-reference.json -->

Results that cannot be calculated show one of these messages:

| Message | Meaning |
| --- | --- |
| `Division by zero` | The expression divides by zero. |
| `Log undefined for non-positive values` | `log` was given zero or a negative number. |
| `Expected '(' after log` | `log` is not followed by an opening parenthesis. |
| `Mismatched parentheses` | An opening parenthesis has no matching closing one. |
| `Invalid exponentiation:` followed by the values | The power cannot be calculated, such as `0 ^ 0` or a fractional power of a negative number. |
| `Result out of range` | The result is too large or too small. See [Understand Precision and Limits](#understand-precision-and-limits). |
| `Unexpected end of expression` | The expression ends with an operator. |
| `Unexpected token after expression` | Something follows a complete expression, such as `2(3)` typed on Windows. |

An unmatched parenthesis inside `log` shows
`Mismatched parentheses in log` on Windows and iOS.

<!-- Verified from: platform/windows/fin_calc/domains/calc/evaluator.py [_Parser] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/Evaluator.swift [Parser] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/DecimalMath.swift [power] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/Evaluator.kt [Parser] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/DecimalMath.kt [power] -->

When you build an expression with keys, Fin Calc ignores keys that do not fit
at that point and shows `Invalid input:` followed by the key. For example:

- A number cannot directly follow `)` or `log`, and `(` or `log` cannot
  directly follow a number. Type an operator between them.
- `)` is accepted only when an opening parenthesis is still open.
- A number can have only one decimal point. Starting a number with `.`
  enters `0.`.
- After an operator or `(`, the `-` key starts a negative number. Other
  operators after an operator are ignored.

<!-- Verified from: platform/windows/fin_calc/domains/calc/expression.py [ExpressionBuilder] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._on_token] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/ExpressionBuilder.swift [ExpressionBuilder] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/ExpressionBuilder.kt [ExpressionBuilder] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorSession.kt [press] -->

#### Enter an Expression on Windows

In the graphical window:

1. Click keypad keys, or type digits, `.`, `+`, `-`, `*`, `/`, `^`, `(`, and
   `)` on the keyboard. Press **L** to enter `log`.
1. Press **Enter** or click **=**.

The display shows the result, and the calculation is added to the tape.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/keypad.py [KEY_MAP] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow.keyPressEvent, RootWindow._on_evaluate] -->

In the terminal interface:

1. Type the whole expression in the entry field, such as `0.1 + 0.2` or
   `log(100)`.
1. Press **Enter**.

The result line shows `Result:` and the answer, the tape updates, and the
entry field clears. If the expression is not valid, the result line shows
`Error:` and the reason, and your entry stays so you can correct it.

<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp.on_input_submitted] -->

On the command line, from `platform/windows/`:

```powershell
.venv/Scripts/python.exe -m fin_calc.main calculate "0.1 + 0.2"
```

Fin Calc prints `0.3` and saves the calculation. Quote the expression. If it
starts with a minus sign, put `--` before it:

```powershell
.venv/Scripts/python.exe -m fin_calc.main calculate -- "-2 ^ 2"
```

<!-- Verified from: platform/windows/fin_calc/ui/cli/commands.py [calculate] -->

Typed expressions in the terminal interface and on the command line follow
these rules:

- Numbers may use scientific notation, such as `1.5e3`.
- Spaces are optional between symbols, but a space never joins two numbers.
- The limit is 2,048 characters and 128 symbols.
- Any other character, such as `x` or `,`, shows
  `Invalid input at character` and its position.

<!-- Verified from: platform/windows/fin_calc/domains/calc/parsing.py [parse_expression] -->

#### Enter an Expression on iOS

1. Tap keypad keys. With a hardware keyboard, you can also type digits and
   operators, and press **L** for `log`.
1. Tap **=**, or press **Return** on a hardware keyboard.

The display shows the result, and the calculation is added to the tape. You
can select and copy the display text.

<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.pressHardwareKey] -->
<!-- Verified from: platform/ios/FinCalc/Application/CalculatorSession.swift [evaluate] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/DisplayView.swift [DisplayView] -->

#### Enter an Expression on Android

1. Tap keypad keys.
1. Tap **=**.

The display shows the result, and the calculation is added to the tape. You
can select and copy the display text. The keypad stops accepting keys when the
expression reaches 128 symbols or 2,048 characters.

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorSession.kt [press, calculate] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/ui/CalculatorView.kt [CalculatorView] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/ExpressionBuilder.kt [add] -->

### Correct or Clear the Current Expression

These keys change only the expression you are entering. They never change the
saved tape.

| To | Windows graphical window | iOS | Android |
| --- | --- | --- | --- |
| Delete the last character | **←** or **Backspace** | **⌫**, or **Delete** on a hardware keyboard | **⌫** |
| Clear the whole expression | **C** or **Esc** | **C**, or **Esc** on a hardware keyboard | **C** |
| Change the sign of the current number | **±** | **±** | **±** |

Deleting removes one digit of a number, or the whole last operator,
parenthesis, or `log`. In the Windows terminal interface, edit the entry field
as usual, or press **Esc** to clear it.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow.keyPressEvent] -->
<!-- Verified from: platform/windows/fin_calc/domains/calc/expression.py [ExpressionBuilder.backspace, ExpressionBuilder.toggle_sign] -->
<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp.action_clear_input] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.pressHardwareKey] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/ExpressionBuilder.kt [backspace, toggleSign] -->

### Continue From a Result

After you evaluate, the result stays in the display as the start of the next
expression. This applies to the Windows graphical window, iOS, and Android.

- Press an operator to continue from the result, such as `+ 5`.
- Press a digit, `.`, `(`, or **log** to start a new expression instead.

Continuing uses the result's full precision, even when the display rounds it.

<!-- Verified from: platform/windows/fin_calc/domains/calc/expression.py [ExpressionBuilder.insert_result, ExpressionBuilder._continue_from_result] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/ExpressionBuilder.swift [continueFromResult] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/ExpressionBuilder.kt [add] -->

### Reuse a Result From the Tape

A tape result can be placed into the current expression with its full
precision. It is added only at the start of an expression or after an
operator or `(`; if the expression ends with a number, nothing happens.

<!-- Verified from: platform/windows/fin_calc/domains/calc/expression.py [ExpressionBuilder.insert_result] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/ExpressionBuilder.swift [insertResult] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/ExpressionBuilder.kt [insertResult] -->

#### Reuse a Result on Windows

In the graphical window, click a line on the tape. The terminal interface and
command line cannot reuse results.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/tape.py [TapeView._on_item_clicked] -->
<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp.compose] -->

#### Reuse a Result on iOS

Tap a line on the tape. You can also touch and hold a line, then choose
**Use Result**, or choose **Copy Result** to copy the full-precision result.

<!-- Verified from: platform/ios/FinCalc/UI/Views/TapeView.swift [TapeView.row] -->

#### Reuse a Result on Android

Tap a line on the tape.

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/ui/TapeView.kt [Rows.onBindViewHolder] -->

### Review Saved History

The tape shows your saved calculations in every interface, oldest at the top.
Results on the tape follow the **Decimal places** setting. To list saved
history on the Windows command line, from `platform/windows/`:

```powershell
.venv/Scripts/python.exe -m fin_calc.main history
```

Each line has the form `expression = result`. The command only reads the
history; it does not change it.

<!-- Verified from: platform/windows/fin_calc/ui/cli/commands.py [history] -->
<!-- Verified from: platform/windows/fin_calc/domains/calc/formatting.py [format_history_line] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/TapeView.swift [TapeView.row] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/ui/TapeView.kt [Rows.onBindViewHolder] -->

Fin Calc keeps up to the history limit set in
[Settings and Preferences](#settings-and-preferences) and removes the oldest
calculations first when the limit is reached.

<!-- Verified from: platform/windows/fin_calc/domains/calc/history.py [History.append] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/History.swift [History.append] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/History.kt [trimHistory] -->

### Clear Saved History

Clearing removes every saved calculation on that device. It cannot be undone,
so export the history first if you want to keep it.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._on_clear_history] -->
<!-- Verified from: platform/ios/FinCalc/Application/CalculatorSession.swift [clearHistory] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorSession.kt [clearHistory] -->

#### Clear History on Windows

In the graphical window, choose **File** > **Clear History**, or right-click
the tape and choose **Clear History**. In the **Clear History** confirmation,
choose **Yes** to clear, or **No** to keep your history. The terminal interface
and command line cannot clear history.

<!-- Verified from: platform/windows/fin_calc/ui/gui/menus/menu_bar.py [build_menu_bar] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/tape.py [TapeView.contextMenuEvent] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._on_clear_history] -->

#### Clear History on iOS

1. Tap the **History** menu.
1. Tap **Clear History**.
1. In the `Clear All History?` confirmation, tap **Clear History**.

**Clear History** is unavailable when the tape is empty.

<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.toolbarContent, RootView.body] -->

#### Clear History on Android

1. Tap **⋮** > **Clear History**.
1. In the `Clear History?` confirmation, tap **Clear**, or **Cancel** to keep
   your history.

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/MainActivity.kt [showMenu] -->

### Understand Precision and Limits

Fin Calc keeps 28 significant digits and rounds half to even. For example,
`1 / 3` gives `0.3333333333333333333333333333` on every platform. The
**Decimal places** setting only rounds what you see; saved and reused results
keep their full precision.

<!-- Verified from: platform/windows/fin_calc/domains/calc/evaluator.py [evaluate] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/DecimalMath.swift [DecimalMath.precision, roundToPrecision] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/DecimalMath.kt [context] -->
<!-- Verified from: platform/android/app/src/test/resources/python-reference.json -->

The platforms differ in range and in how full-precision results look:

| Platform | Range of results | How full-precision results look |
| --- | --- | --- |
| Windows | Much wider than the mobile apps; for example, `10 ^ 1000000` is `Result out of range`. | Very small results can use scientific notation, such as `1E-7`. Some results keep trailing zeros, such as `2.000000000000000000000000000` for `log(100)`. |
| iOS | About 1E-128 to 1E165. | Plain digits. |
| Android | Powers of ten from -9,999 to 9,999. | Plain digits with trailing zeros removed, such as `1000` for `500 + 500`. Results beyond 28 digits from the decimal point use scientific notation. |

Logarithms and fractional powers are computed differently on each platform,
so their last digit can differ between platforms.

<!-- Verified from: platform/windows/fin_calc/domains/calc/evaluator.py [evaluate] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/DecimalMath.swift [exp, log10] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/DecimalMath.kt [checked, ln, exp] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorSession.kt [calculate] -->

## Settings and Preferences

All platforms have the same three settings. Changes take effect as soon as
you save them and are kept between runs.

| Setting | Default | Accepted values | How to change it |
| --- | --- | --- | --- |
| **Decimal places** | Full precision | **Full precision**, or 0 through 6 | Settings on each platform |
| **Theme** | Dark | **Dark** or **Light** | Settings on each platform |
| Maximum history entries | 1,000 | 1 through 10,000, or **Unlimited** | Settings on each platform |

<!-- Verified from: platform/windows/fin_calc/config/settings.py [Settings] -->
<!-- Verified from: platform/windows/fin_calc/domains/calc/history.py [DEFAULT_HISTORY_CAP, MIN_HISTORY_CAP, MAX_HISTORY_CAP] -->
<!-- Verified from: platform/windows/fin_calc/domains/calc/formatting.py [MAX_DECIMAL_PLACES] -->
<!-- Verified from: platform/ios/FinCalc/Config/Settings.swift [Settings] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/config/Settings.kt [Settings] -->

- **Decimal places** rounds results on the display and tape. Rounding is half
  to even, so `1.245` shows as `1.24` and `1.255` as `1.26` at two places.
  Shorter results are padded with zeros. If rounding would need more than 28
  digits, the full result is shown.
- **Theme** switches between dark and light colors.
- Maximum history entries sets how many calculations are kept. Lowering it
  removes the oldest calculations right away.

<!-- Verified from: platform/windows/fin_calc/domains/calc/formatting.py [format_result] -->
<!-- Verified from: platform/ios/FinCalc/Domains/Calc/Formatting.swift [formatResult] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/Formatting.kt [formatResult] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._apply_settings] -->
<!-- Verified from: platform/ios/FinCalc/Application/CalculatorSession.swift [applySettings] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorSession.kt [updateSettings] -->

### Change Settings

#### Change Settings on Windows

1. In the graphical window, choose **Edit** > **Settings...**.
1. Choose **Decimal places:** and **Theme:**.
1. Set **Max history entries:**, or select **Unlimited**.
1. Click **OK** to apply, or **Cancel** to discard.

The terminal interface and command line use the same settings but cannot
change them; they read the settings each time they start. If the settings
cannot be saved, the status bar shows `Saving settings failed:` and the
reason, and the new settings apply only until you close the window. You can
also edit the settings file by hand; see
[Edit the Windows Data Files](#edit-the-windows-data-files).

<!-- Verified from: platform/windows/fin_calc/ui/gui/dialogs/settings_dialog.py [SettingsDialog] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._on_open_settings, RootWindow._apply_settings] -->
<!-- Verified from: platform/windows/fin_calc/application/session.py [load_session] -->
<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp.__init__] -->

#### Change Settings on iOS

1. Tap **Settings**.
1. Under **Display**, choose **Decimal places** and **Theme**.
1. Under **History**, turn **Unlimited** on, or turn it off and enter
   **Max entries**.
1. Tap **Save** to apply, or **Cancel** to discard.

A **Max entries** value outside 1 to 10,000 is changed to the nearest allowed
value when you save. If the settings cannot be saved, the status line shows
`Settings could not be saved`.

<!-- Verified from: platform/ios/FinCalc/UI/Views/SettingsView.swift [SettingsView.body, selectedSettings] -->
<!-- Verified from: platform/ios/FinCalc/Application/CalculatorSession.swift [applySettings] -->

#### Change Settings on Android

1. Tap **⋮** > **Settings**.
1. Choose **Decimal places** and **Theme**.
1. Turn **Unlimited history** on, or turn it off and enter
   **Maximum history entries (1–10,000)**.
1. Tap **Save** to apply, or **Cancel** to discard.

If the limit is not a whole number from 1 to 10,000, the field shows
`Enter a whole number from 1 to 10,000` and the dialog stays open. If the
settings cannot be saved, the status line shows
`Could not save. Your previous history is unchanged.` and your previous
settings stay in effect.

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/ui/SettingsDialog.kt [showSettings] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorModel.kt [submit] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorSession.kt [commit] -->

## Importing and Exporting

You can export your saved history as a CSV file on every platform. Fin Calc
cannot import history or other files. Exports always contain full-precision
results, whatever the **Decimal places** setting.

<!-- Verified from: platform/windows/fin_calc/adapters/history_export.py [write_history_csv] -->
<!-- Verified from: platform/ios/FinCalc/Adapters/HistoryExport.swift [formatCSV] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/adapters/HistoryExport.kt [write] -->

### Export History to CSV

#### Export on Windows

1. In the graphical window, choose **File** > **Export History...**.
1. In the **Export History** dialog, keep the suggested `history.csv` in the
   `exports` folder, or choose another location and name.
1. Click **Save**.

If the name does not end in `.csv`, Fin Calc adds it. A file with the same
name is replaced. The status bar shows `Exported history to` and the path, or
`Export failed:` and the reason. The terminal interface and command line
cannot export.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._on_export_history] -->
<!-- Verified from: platform/windows/fin_calc/config/path_handler.py [EXPORTS_DIR] -->
<!-- Verified from: platform/windows/fin_calc/adapters/history_export.py [write_history_csv] -->

#### Export on iOS

1. Tap the **History** menu.
1. Tap **Export CSV**.
1. In the share sheet, choose where to send or save `history.csv`.

**Export CSV** is unavailable when the tape is empty.

<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.toolbarContent, HistoryCSV] -->

#### Export on Android

1. Tap **⋮** > **Export History**.
1. In Android's file picker, choose a folder. The suggested name is
   `fin-calc-history.csv`.
1. Confirm the save in the file picker.

Choosing an existing file replaces its contents. When the export succeeds, the
status line shows `History exported.` If it fails, the status line shows
`Could not export history. Choose another location and try again.`

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/MainActivity.kt [export, showMenu] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorModel.kt [export] -->

### Read the Exported CSV File

The file is UTF-8 text with a header row and one row per calculation, oldest
first.

| Column | What it contains |
| --- | --- |
| `timestamp` | When the calculation was made, as an ISO 8601 date and time in UTC. |
| `expression` | The expression as shown on the tape. |
| `result` | The full-precision result. |

A field that contains a comma, quotation mark, or line break is enclosed in
quotation marks. Example from Windows:

```csv
timestamp,expression,result
2026-10-25T14:03:07.512345+00:00,0.1 + 0.2,0.3
2026-10-25T14:03:20.104211+00:00,1 / 3,0.3333333333333333333333333333
```

<!-- Verified from: platform/windows/fin_calc/adapters/history_export.py [write_history_csv] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._on_evaluate] -->

The details differ by platform:

| Platform | Timestamp example | Line endings |
| --- | --- | --- |
| Windows | `2026-10-25T14:03:07.512345+00:00` | CRLF |
| iOS | `2026-10-25T14:03:07Z` | CRLF |
| Android | `2026-10-25T14:03:07.512Z` (fraction length varies) | LF |

<!-- Verified from: platform/windows/fin_calc/adapters/history_export.py [write_history_csv] -->
<!-- Verified from: platform/ios/FinCalc/Adapters/HistoryExport.swift [formatCSV] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/adapters/HistoryExport.kt [write] -->

## Commands and Shortcuts

### Use the Windows Command Line

Run from `platform/windows/` as
`.venv/Scripts/python.exe -m fin_calc.main` or `.venv/Scripts/fin-calc.exe`,
followed by one of these:

| Command or option | Accepted values | What it does |
| --- | --- | --- |
| (none) | None | Shows the interface menu. |
| `--gui` | None | Opens the graphical window. |
| `--tui` | None | Opens the terminal interface. |
| `--cli` | None, or a command | Alone, opens the persistent calculator prompt. With a command, runs it once. |
| `calculate EXPRESSION` | A quoted expression | Prints the result, rounded to **Decimal places**, and saves it to history. |
| `history` | None | Prints saved history without changing it. |
| `--help` | None | Shows help for Fin Calc or for the command it follows. |
| `--` | Placed before an expression | Lets an expression start with a minus sign. |

Use only one of `--gui`, `--tui`, and `--cli`, and do not combine `--gui` or
`--tui` with a command. A command ends with status 0 on success and 1 when the
expression is invalid or history cannot be saved or read; it prints `Error:`
and the reason. Incorrect options end with status 2.

<!-- Verified from: platform/windows/fin_calc/ui/cli/app.py [select_interface, run_app] -->
<!-- Verified from: platform/windows/fin_calc/ui/cli/commands.py [calculate, history] -->
<!-- Verified from: platform/windows/fin_calc/application/session.py [CalculatorSession.calculate] -->

#### Use the Persistent Prompt

Start it from `platform/windows/`:

```powershell
.venv/Scripts/python.exe -m fin_calc.main --cli
```

Enter expressions directly, without quotes or the `calculate` command:

```text
fin-calc> 125 * 1.08
135
fin-calc> 135 / 12
11.25
fin-calc> history
125 * 1.08 = 135
135 / 12 = 11.25
fin-calc> exit
```

The example assumes empty history and full-precision display. Each successful
calculation is saved immediately. Results and `history` use the display
settings loaded at startup; saved results retain full precision. Negative
expressions need no `--` prefix here.

Use `help` to see supported syntax and commands. Blank lines are ignored.
Invalid expressions and failed saves print `Error:` and keep the prompt open so
you can try again. Type `exit` or `quit`, press **Ctrl+C**, or end input to
leave with status 0. On Windows, **Ctrl+Z** followed by **Enter** ends input.
Redirected input is read one line at a time until it ends; use the one-shot
`calculate` command when a script needs a nonzero status for a failed
calculation.

<!-- Verified from: platform/windows/fin_calc/ui/cli/repl.py [run_repl, _read_expressions] -->
<!-- Verified from: platform/windows/fin_calc/ui/cli/commands.py [show_history] -->

### Use Menu Commands

#### Menu Commands on Windows

| Menu | Command | Shortcut | What it does |
| --- | --- | --- | --- |
| **File** | **Export History...** | None | Saves history to a CSV file. |
| **File** | **Clear History** | None | Removes all saved history after confirmation. |
| **File** | **Exit** | None | Closes the window. |
| **Edit** | **Settings...** | None | Opens the settings. |
| **Help** | **Keyboard Shortcuts** | None | Lists keyboard keys. |
| **Help** | **About** | None | Shows the version. |
| Tape (right-click) | **Clear History** | None | Removes all saved history after confirmation. |

Press **Alt+F**, **Alt+E**, or **Alt+H** to open the **File**, **Edit**, or
**Help** menu.

<!-- Verified from: platform/windows/fin_calc/ui/gui/menus/menu_bar.py [build_menu_bar] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/tape.py [TapeView.contextMenuEvent] -->

#### Menu Commands on iOS

| Menu | Command | Shortcut | What it does |
| --- | --- | --- | --- |
| **History** | **Export CSV** | None | Shares history as a CSV file. |
| **History** | **Clear History** | None | Removes all saved history after confirmation. |
| **Settings** button | None | None | Opens the settings. |
| Tape line (touch and hold) | **Use Result** | None | Places the result in the expression. |
| Tape line (touch and hold) | **Copy Result** | None | Copies the full-precision result. |

<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.toolbarContent] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/TapeView.swift [TapeView.row] -->

#### Menu Commands on Android

| Menu | Command | Shortcut | What it does |
| --- | --- | --- | --- |
| **⋮** | **Settings** | None | Opens the settings. |
| **⋮** | **Export History** | None | Saves history to a CSV file. |
| **⋮** | **Clear History** | None | Removes all saved history after confirmation. |
| **⋮** | **Privacy Policy** | None | Opens `https://plaintxtoffice.com/privacy-policy/` in a browser, or shows the address if no browser is available. |
| **⋮** | **About** | None | Shows the version and short tips. |

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/MainActivity.kt [showMenu] -->

### Use Keyboard Shortcuts

| Platform | Key | What it does |
| --- | --- | --- |
| Windows graphical window | **Enter** or **Return** | Evaluates the expression. |
| Windows graphical window | **Esc** | Clears the expression. |
| Windows graphical window | **Backspace** | Deletes the last character. |
| Windows graphical window | **0**–**9**, **.**, **+**, **-**, **\***, **/**, **^**, **(**, **)** | Enters that key. |
| Windows graphical window | **L** | Enters `log`. |
| Windows terminal interface | **Enter** | Calculates and saves the entry. |
| Windows terminal interface | **Esc** | Clears the entry field. |
| Windows terminal interface | **Ctrl+Q** | Quits. |
| iOS with a hardware keyboard | **Return** | Evaluates the expression. |
| iOS with a hardware keyboard | **Esc** | Clears the expression. |
| iOS with a hardware keyboard | **Delete** | Deletes the last character. |
| iOS with a hardware keyboard | **0**–**9**, **.**, **+**, **-**, **\***, **/**, **^**, **(**, **)** | Enters that key. |
| iOS with a hardware keyboard | **L** | Enters `log`. |

The **±** key has no keyboard shortcut. Fin Calc for Android has no keyboard
shortcuts.

<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow.keyPressEvent] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/keypad.py [KEY_MAP] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/dialogs/help_dialogs.py [SHORTCUTS_TEXT] -->
<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp.BINDINGS, CalculatorApp.on_input_submitted] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.pressHardwareKey] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/MainActivity.kt -->

## Your Data Files

Fin Calc saves your history and settings automatically. Each platform keeps
its own files, and the location cannot be changed.

### Find Your Data Files

#### Data Files on Windows

| File or folder | Purpose |
| --- | --- |
| `data/history.json` | Saved history. |
| `data/settings.json` | Saved settings. |
| `exports/` | Suggested folder for CSV exports. |
| `logs/` | Log files for troubleshooting. |

These are inside a data folder that depends on how you run Fin Calc:

| How you run Fin Calc | Data folder |
| --- | --- |
| From the project folder | `platform/windows/` |
| Packaged program | `%LOCALAPPDATA%/fin-calc/` |
| Packaged program set up as portable | `fin-calc-data/` next to the program, or `%LOCALAPPDATA%/fin-calc/` if that folder cannot be written |

Builds before 2026-10-28 used `Fin Calc/` and `Fin Calc-data/`. The program
renames an old folder to the new name on first launch when the new folder does
not exist yet.

The graphical window, terminal interface, and command line share the same
files.

<!-- Verified from: platform/windows/fin_calc/config/path_handler.py [ROOT_DIR, DATA_DIR, HISTORY_FILE, SETTINGS_FILE, EXPORTS_DIR, LOGS_DIR, USER_DATA_DIR] -->
<!-- Verified from: platform/windows/fin_calc/config/storage.py [select_storage] -->
<!-- Verified from: platform/windows/fin_calc/application/session.py [load_session] -->

#### Data Files on iOS

History and settings are saved as `history.json` and `settings.json` in a
`FinCalc` folder inside the app's private storage. The app does not show these
files in the Files app, so they cannot be edited by hand. Use
[Export on iOS](#export-on-ios) to keep a copy of your history.

<!-- Verified from: platform/ios/FinCalc/Config/PathHandler.swift [PathHandler] -->
<!-- Verified from: platform/ios/FinCalc.xcodeproj/project.pbxproj -->

#### Data Files on Android

History and settings are saved together in one private file, `calculator.json`.
It cannot be edited by hand. Uninstalling the app or clearing its data removes
your history and settings. Android backup and device transfer are turned off
for this app, so export anything you want to keep first.

<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorModel.kt [CalculatorModel.init] -->
<!-- Verified from: platform/android/app/src/main/AndroidManifest.xml [android:allowBackup] -->
<!-- Verified from: platform/android/app/src/main/res/xml/data_extraction_rules.xml -->

### Edit the Windows Data Files

You can edit the Windows data files in a text editor. Close every Fin Calc
window first, because Fin Calc rewrites the files as you use it, and keep a
copy in case of a mistake. If a file cannot be read, Fin Calc starts with
empty history or default settings and overwrites the file at the next save.

<!-- Verified from: platform/windows/fin_calc/adapters/history_store.py [load_history, write_history] -->
<!-- Verified from: platform/windows/fin_calc/adapters/settings_store.py [load_settings, write_settings] -->

`settings.json` is a JSON object:

```json
{
  "decimal_places": null,
  "theme": "dark",
  "max_history_entries": 1000
}
```

| Field | Required | What to enter |
| --- | --- | --- |
| `decimal_places` | No | `null` for full precision, or a whole number from 0 to 6. Larger numbers are treated as 6; other values mean full precision. |
| `theme` | No | `"dark"` or `"light"`. Other values mean dark. |
| `max_history_entries` | No | `null` for unlimited, or a whole number from 1 to 10,000. Larger numbers are treated as 10,000; a missing or other value means 1,000. |

<!-- Verified from: platform/windows/fin_calc/adapters/settings_store.py [load_settings, _read_optional_bounded_int, _read_history_cap, _read_theme] -->

`history.json` is a JSON list with one object per calculation, oldest first:

```json
[
  {
    "expression": "0.1 + 0.2",
    "result": "0.3",
    "timestamp": "2026-10-25T14:03:07.512345+00:00"
  }
]
```

| Field | Required | What to enter |
| --- | --- | --- |
| `expression` | Yes | The expression text shown on the tape. |
| `result` | Yes | The result as text. |
| `timestamp` | Yes | An ISO 8601 date and time. |

If any entry is missing a field or has an unreadable timestamp, Fin Calc
ignores the whole file and starts with empty history.

<!-- Verified from: platform/windows/fin_calc/adapters/history_store.py [_load_entries, write_history] -->

### Find Windows Log Files

Fin Calc for Windows writes a log to the `logs/` folder in its data folder.
The log file is named after the data folder, such as `windows.log` when
running from the project folder. Each log file is limited to about 1 MB, and
up to three older copies are kept. The iOS and Android apps do not create log
files you can open.

<!-- Verified from: platform/windows/fin_calc/config/logging/log_config.py [configure_logging, MAX_LOG_BYTES, LOG_BACKUP_COUNT] -->
<!-- Verified from: platform/ios/FinCalc/Adapters/HistoryStore.swift [HistoryStore.logger] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorModel.kt [CalculatorModel] -->

## Troubleshooting

| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| Windows prints `Choose --gui, --tui, --cli, or a command; use --help for usage.` | Input does not come from the keyboard, so the interface menu cannot be shown. | Add `--gui`, `--tui`, `--cli`, or a command. |
| Windows prints `Use only one of --gui, --tui, or --cli.` | More than one interface option was given. | Give only one. |
| Windows prints `GUI/TUI launch flags cannot be combined with CLI commands.` | `--gui` or `--tui` was used with `calculate` or `history`. | Remove the option, or use `--cli`. |
| Windows prints `Unable to start calculator:` | The data folder cannot be created or written. | Make sure the data folder in [Data Files on Windows](#data-files-on-windows) is writable. |
| An expression starting with `-` is treated as an option on the Windows command line | The minus sign looks like an option. | Put `--` before the expression, as in `calculate -- "-2 ^ 2"`. |
| `Invalid input at character` appears | A typed expression contains an unsupported character, such as `x` or `,`. | Use only numbers, `+`, `-`, `*`, `/`, `^`, parentheses, and `log`. |
| `Invalid input:` and a key appear | The key does not fit at that point in the expression. | See [Enter and Evaluate an Expression](#enter-and-evaluate-an-expression). |
| `Result out of range` appears | The result is too large or too small for the platform. | See [Understand Precision and Limits](#understand-precision-and-limits). |
| Saved history is empty after starting | The history file could not be read. | On Windows, check `data/history.json` against [Edit the Windows Data Files](#edit-the-windows-data-files) before your next calculation overwrites it. |
| Settings returned to their defaults | The settings file was missing or had invalid values. | Choose your settings again. |
| Android shows `Could not load saved history and settings. Defaults are in use.` | The saved file could not be read. | Choose your settings again. Saved history could not be recovered by the app. |
| Android shows `Could not save. Your previous history is unchanged.` | The device could not save the change. | Free up storage and try again. |
| Android shows `Could not export history. Choose another location and try again.` | The chosen location cannot be written. | Choose another folder or storage provider. |
| iOS shows `History could not be saved` or `Settings could not be saved` | The device could not save the change. | Free up storage and try again. |
| Windows status bar shows `Export failed:` | The chosen location cannot be written. | Choose a writable folder. |
| Windows status bar shows `Saving history failed:` | The history file could not be written. | Free up storage or check that the data folder is writable, then make another calculation. |
| iOS **Export CSV** or **Clear History** is unavailable | The tape is empty. | Make a calculation first. |
| The Android **⋮** menu does not open | Saved data is still loading. | Wait until `Loading…` disappears. |
| Older calculations disappeared | The history limit was reached or lowered. | Raise the maximum history entries or choose **Unlimited**. |

<!-- Verified from: platform/windows/fin_calc/ui/cli/launch.py [choose_interface] -->
<!-- Verified from: platform/windows/fin_calc/ui/cli/app.py [select_interface] -->
<!-- Verified from: platform/windows/fin_calc/ui/cli/commands.py [calculate] -->
<!-- Verified from: platform/windows/fin_calc/domains/calc/parsing.py [parse_expression] -->
<!-- Verified from: platform/windows/fin_calc/adapters/history_store.py [load_history] -->
<!-- Verified from: platform/windows/fin_calc/adapters/settings_store.py [load_settings] -->
<!-- Verified from: platform/windows/fin_calc/ui/gui/views/root_window.py [RootWindow._on_export_history] -->
<!-- Verified from: platform/ios/FinCalc/Application/CalculatorSession.swift [writeHistory, applySettings] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/RootView.swift [RootView.toolbarContent] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorModel.kt [CalculatorModel.init, submit] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorSession.kt [calculate] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/Formatting.kt [formatResult] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/MainActivity.kt [showMenu] -->

## FAQ

### Why does 0.1 + 0.2 give exactly 0.3?

Fin Calc calculates with decimal numbers rather than binary floating point,
so decimal fractions are exact.

<!-- Verified from: platform/windows/fin_calc/domains/calc/evaluator.py [evaluate] -->
<!-- Verified from: platform/android/app/src/test/resources/python-reference.json -->

### Why does -2 ^ 2 give 4?

A leading minus sign belongs to its number, so `-2 ^ 2` means `(-2) ^ 2`. To
get `-4`, enter `0 - 2 ^ 2`.

<!-- Verified from: platform/windows/fin_calc/domains/calc/evaluator.py [module docstring] -->

### Does the Decimal places setting change my saved results?

No. It only rounds what you see. Saved, reused, copied, and exported results
keep their full precision.

<!-- Verified from: platform/windows/fin_calc/domains/calc/formatting.py [format_result] -->
<!-- Verified from: platform/ios/FinCalc/UI/Views/TapeView.swift [TapeView.row] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/Formatting.kt [formatResult] -->

### Is my history shared between devices or platforms?

No. Each device keeps its own history and settings. Export a CSV file to move
a record of your calculations elsewhere.

<!-- Verified from: platform/windows/fin_calc/config/path_handler.py [HISTORY_FILE] -->
<!-- Verified from: platform/ios/FinCalc/Config/PathHandler.swift [PathHandler] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/application/CalculatorModel.kt [CalculatorModel.init] -->

### Can I undo Clear History?

No. Export your history first if you might need it.

<!-- Verified from: platform/windows/fin_calc/domains/calc/history.py [History.clear_all] -->

### Can I change settings from the Windows terminal interface or command line?

No. Use **Edit** > **Settings...** in the graphical window, or edit
`settings.json` while Fin Calc is closed. The terminal interface and command
line use the new settings the next time they start.

<!-- Verified from: platform/windows/fin_calc/application/session.py [load_session] -->

### Why does the same logarithm differ in its last digit on another platform?

Each platform computes logarithms and fractional powers its own way, so the
28th digit can differ.

<!-- Verified from: platform/ios/FinCalc/Domains/Calc/DecimalMath.swift [DecimalMath] -->
<!-- Verified from: platform/android/app/src/main/java/com/plaintxtoffice/fincalc/domains/calc/DecimalMath.kt [ln, exp] -->

## Glossary

- **CSV**: comma-separated values, a text file format that spreadsheet
  programs can open.
- **Decimal places**: the number of digits shown after the decimal point.
- **Expression**: the calculation you are entering, such as `2 + 3`.
- **Full precision**: showing a result with all of its calculated digits.
- **Graphical window**: the Windows interface with menus, a tape, and a
  clickable keypad.
- **History entry**: one saved calculation, with its expression, result, and
  time.
- **History limit**: the maximum number of calculations Fin Calc keeps.
- **Rounding half to even**: rounding a value exactly halfway between two
  choices to the one with an even last digit.
- **Scientific notation**: writing a number as digits and a power of ten,
  such as `1E+3` for 1,000 or `1E-7` for 0.0000001.
- **Significant digits**: the digits of a number from its first nonzero
  digit.
- **Tape**: the list of saved calculations.
- **Terminal interface**: the Windows interface that runs inside a terminal
  window.

<!-- Verified from: platform/windows/fin_calc/domains/calc/history.py [HistoryEntry] -->
<!-- Verified from: platform/windows/fin_calc/domains/calc/formatting.py [format_result] -->
<!-- Verified from: platform/windows/fin_calc/ui/tui/app.py [CalculatorApp] -->
