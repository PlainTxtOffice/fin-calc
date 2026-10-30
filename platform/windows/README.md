# Fin Calc for Windows

This directory is the Python project root. It contains `pyproject.toml`, the
`fin_calc/` package, Windows tests, and the local `.venv/` environment.

See the [product overview](../../README.md) and
[user manual](../../docs/USER_MANUAL.md) for application behavior. Shared
documentation and assets remain at repository level.

## Development

Run from this directory with Python 3.12 or newer:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install --upgrade "pip>=25.1"
.venv/Scripts/python.exe -m pip install --editable ".[dev]"
.venv/Scripts/python.exe -m fin_calc.main
.venv/Scripts/python.exe -m pytest -p no:cacheprovider
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m mypy fin_calc
```

For Markdown checks, run `platform/windows/.venv/Scripts/rumdl.exe check` from
the repository root; configuration lives in `.rumdl.toml` there.

The local [LICENSE](LICENSE) is a distribution copy of the
[repository license](../../LICENSE). Keep them identical when changing
licensing.
