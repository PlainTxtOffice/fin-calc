# Fin Calc Windows builds

Run these commands from `platform/windows/`. The scripts also resolve their
paths correctly when invoked from another directory.

```powershell
./scripts/nuitka/standalone.ps1 -Commercial
./scripts/nuitka/onefile.ps1 -Commercial
./scripts/nuitka/standalone.ps1 -Console
```

There are two build entrypoints and three variants:

| Variant | Output | Runtime storage |
| --- | --- | --- |
| Standalone release | `build/standalone/main.dist/Fin Calc.exe` | `%LOCALAPPDATA%/fin-calc` |
| Onefile release | `build/onefile/Fin Calc.exe` | `fin-calc-data` beside the executable |
| Standalone console | `build/standalone-console/main.dist/Fin Calc.exe` | `%LOCALAPPDATA%/fin-calc` |

A portable copy falls back to the per-user folder when its neighboring data
folder cannot be written. The application logs that fallback. Development runs
use the Windows project root, including `data/`, `logs/`, and `exports/` there.
Existing repository-root data is not moved or deleted automatically.

The packaged program opens the GUI by default. Explicit commands and interface
flags remain available, for example `"Fin Calc.exe" --cli calculate "1 + 2"`.
Use the console variant from an existing terminal when diagnosing failures.
The console switch changes neither the application logging level nor compiler
debug settings. Both standalone variants share the same saved data.

## Prerequisites and overrides

Use the Python-created `.venv` with the project dependencies, Nuitka, MSVC, and
`zstandard` for compressed onefile builds. Commercial installation is documented
in the private `installing_nuitka.md`; do not copy its access token elsewhere.
Public clones may use free Nuitka by omitting `-Commercial`. Every distributed
release must use `-Commercial`, which enables constant encryption. Optional data
embedding and traceback encryption are not enabled.

Both entrypoints accept `PythonExecutable`, `OutputDirectory`, and
`OutputFilename`; relative paths resolve from the Windows project root.

```powershell
./scripts/nuitka/standalone.ps1 -Console -Commercial -OutputDirectory build/diagnostic
./scripts/nuitka/onefile.ps1 -PythonExecutable C:/Python313/python.exe
```

The executable name defaults to `Fin Calc.exe`. Metadata, including the
confirmed company and copyright, comes from `pyproject.toml`. The Windows
project's `assets/icon.ico` is explicitly bundled. Live history and settings are
never bundled.

`UseCurrentDefaultPaths` reports an unsupported-operation error because this
application has no configurable default-path file. Live settings are never
bundled.

`ResetRuntimeDefaults` explicitly deletes `%LOCALAPPDATA%/fin-calc` before
building. In onefile mode it also deletes `fin-calc-data` in the selected output
directory. This removes saved history, settings, logs, and exports in those
folders. It is off by default. Without it, existing data is preserved and a
warning identifies persisted data that may affect smoke tests. Reset checks
reject unexpected folder names and symbolic links or junctions. Locked files
stop the build with instructions to close running application instances.

```powershell
./scripts/nuitka/standalone.ps1 -Commercial -ResetRuntimeDefaults
```

## Validation and distribution

Builds scan unpacked `main.dist` executables and text data for the username,
source paths, and author emails in UTF-8 and UTF-16LE. Matches are warnings for
manual review, since short usernames can match unrelated bytes. A free build
also warns that constants are not encrypted.

Standalone builds run the report-only release validator. It rejects runtime
folders and files derived from the application's path definitions, `.env` files,
and portable markers. There is no bundled defaults file to validate for absolute
paths. Missing distribution folders and missing executables are errors.

Run smoke tests on a **copy** of `main.dist`, never on the installer input
itself. For onefile, ship the executable alone; never include its generated data
folder. Never distribute compiler intermediate directories, build reports, or
crash reports. Generated outputs remain ignored by Git; the maintained scripts,
helpers, and this README are versioned.

## Advanced Installer

Use only `build/standalone/main.dist` as installer input, install under Program
Files, and keep `%LOCALAPPDATA%/fin-calc` on uninstall so reinstalls retain
data. Do not package `standalone-console`.

Add this pre-build event, with its working directory set to `platform/windows/`:

```powershell
pwsh -NoProfile -File scripts/nuitka/validate_release.ps1
```

For a custom release directory, pass `-DistPath` explicitly. The validator exits
1 for problems and 0 for a clean folder, and never changes files. It requires
the project Python environment. Builds retain Nuitka intermediates. Cleanup must
target only generated variant directories; cleanup must not touch the maintained
`scripts/nuitka/` folder.

Reference:
[Nuitka user manual](https://nuitka.net/user-documentation/user-manual.html).
