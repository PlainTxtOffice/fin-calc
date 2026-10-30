"""Inspect installer inputs without changing the distribution."""

import json
import sys
from pathlib import Path


def validate(dist: Path, project: Path) -> list[str]:
    """Reject runtime data and portable markers using application paths."""
    sys.path.insert(0, str(project))
    from fin_calc.config import path_handler as paths  # noqa: PLC0415

    if not dist.is_dir():
        return [f"Distribution folder does not exist: {dist}"]
    problems = []
    forbidden = {"portable.marker"}
    for name in (
        "DATA_DIR",
        "LOGS_DIR",
        "EXPORTS_DIR",
        "CACHE_DIR",
        "BACKUPS_DIR",
        "HISTORY_FILE",
        "SETTINGS_FILE",
    ):
        forbidden.add(getattr(paths, name).name.casefold())
    problems = [
        f"Runtime data or private input: {path.relative_to(dist)}"
        for path in dist.rglob("*")
        if path.name.casefold() in forbidden
        or path.name.casefold().endswith(".env")
    ]
    if not any(dist.glob("*.exe")):
        problems.append("Distribution contains no executable.")
    return problems


if __name__ == "__main__":
    sys.stdout.write(json.dumps(validate(Path(sys.argv[1]), Path(sys.argv[2]))))
