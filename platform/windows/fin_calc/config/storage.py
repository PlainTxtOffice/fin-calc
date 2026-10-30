"""Select writable storage for development, installed, and portable runs."""

from __future__ import annotations

import tempfile
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pathlib import Path

StorageMode = Literal[
    "development",
    "installed",
    "portable",
    "portable-fallback",
]


def select_storage(  # noqa: PLR0913 - explicit storage inputs are independently tested.
    *,
    compiled: bool,
    portable: bool,
    development_root: Path,
    executable_dir: Path,
    user_data_dir: Path,
    app_name: str,
) -> tuple[Path, StorageMode]:
    """Select storage, probing portable writes before falling back per user.

    - Creates the portable data folder and briefly opens a temporary probe.
    - Never moves or deletes existing application data.
    """
    if not compiled:
        return development_root, "development"
    if not portable:
        return user_data_dir, "installed"
    portable_root = executable_dir / f"{app_name}-data"
    try:
        portable_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=portable_root):
            pass
    except OSError:
        return user_data_dir, "portable-fallback"
    return portable_root, "portable"


def migrate_legacy_folder(legacy: Path, current: Path) -> bool:
    """Rename a data folder left under an earlier name to the current name.

    - Moves only when the legacy folder exists and the current one does not,
      so it never merges or overwrites data.
    - Leaves the legacy folder in place when the rename fails, and the app
      then starts with a new folder.
    """
    if current.exists() or not legacy.is_dir():
        return False
    try:
        legacy.rename(current)
    except OSError:
        return False
    return True
