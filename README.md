---
last_updated: 2026-10-23
---

<!-- rumdl-disable MD041 -->
<!-- rumdl-disable MD033 -->

<p align="center">
  <img src="assets/icon.svg" alt="Fin Calc logo" width="160">
</p>

<h1 align="center">Fin Calc</h1>

<p align="center">
  Decimal arithmetic. Persistent history. Windows and iOS.
</p>

<p align="center">
  <a href="LICENSE">MIT License</a> ·
  <a href="docs/USER_MANUAL.md">User Manual</a> ·
  <a href="#usage-examples">Getting Started</a>
</p>

<!-- rumdl-enable MD033 -->

## Short Description

Decimal-precision calculator with graphical, terminal, and command-line
interfaces

## Long Description

Fin Calc is a decimal calculator for Windows, iPhone, and iPad. Calculate
expressions, review past results, and keep a persistent calculation history.
The graphical apps include a keypad, calculation tape, display settings, and
CSV export. Windows also offers terminal and command-line interfaces.

Licensed under the [MIT License](LICENSE).

## Usage Examples

### Windows

Requires Python 3.12 or newer. Clone or download this repository, then open
PowerShell in the repository folder and install the application:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e .
```

Choose an interface interactively:

```powershell
.venv/Scripts/python.exe -m src.windows.main
```

Launch directly or run a command:

```powershell
.venv/Scripts/python.exe -m src.windows.main --gui
.venv/Scripts/python.exe -m src.windows.main --tui
.venv/Scripts/python.exe -m src.windows.main --cli calculate "0.1 + 0.2"
.venv/Scripts/python.exe -m src.windows.main history
.venv/Scripts/python.exe -m src.windows.main --help
```

The installed `.venv/Scripts/fin-calc.exe` command accepts the same arguments.
With the virtual environment activated, you can use `fin-calc` directly.
`--cli` alone shows help. CLI commands also work without `--cli`.
Noninteractive runs must supply a command or interface flag; GUI/TUI flags
cannot accompany commands.

In the TUI, type an expression and press Enter. Escape clears input; Ctrl+Q
quits. The result and saved tape use the configured display precision, while
stored results retain full precision. Settings editing and CSV export remain
available in the GUI. History and settings are saved in the repository's
`data/` folder. See the [user manual](docs/USER_MANUAL.md) for more details.

### iPhone and iPad

Requires a Mac with Xcode supporting Swift 6, and an iOS 17 or newer simulator
or device. From the repository folder, open the Xcode project:

```bash
open src/ios/FinCalc.xcodeproj
```

Select the **FinCalc** scheme and a simulator, then choose **Product > Run**.
To run on a physical device, first select your development team in the
FinCalc target's signing settings.

### Example calculations

Example calculations supported by the interface:

```text
0.1 + 0.2 = 0.3
log ( 100 ) = 2
2 ^ 10 = 1024
```
