"""Static/base path constants for development and packaged builds."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fin_calc.config.storage import migrate_legacy_folder, select_storage

IS_COMPILED = bool(
    globals().get("__compiled__", False) or getattr(sys, "frozen", False),
)
APP_DATA_DIR_NAME = "fin-calc"
# Builds before 2026-10-28 used this folder name; compiled builds rename it.
LEGACY_APP_DATA_DIR_NAME = "Fin Calc"
DEV_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = DEV_ROOT
USER_DATA_DIR = Path(
    os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local",
) / APP_DATA_DIR_NAME
EXECUTABLE_DIR = Path(
    getattr(globals().get("__compiled__"), "containing_dir", "")
    or Path(sys.argv[0]).resolve().parent,
)
IS_PORTABLE = (BUNDLE_ROOT / "portable.marker").is_file()
if IS_COMPILED:
    migrate_legacy_folder(
        USER_DATA_DIR.with_name(LEGACY_APP_DATA_DIR_NAME),
        USER_DATA_DIR,
    )
    if IS_PORTABLE:
        migrate_legacy_folder(
            EXECUTABLE_DIR / f"{LEGACY_APP_DATA_DIR_NAME}-data",
            EXECUTABLE_DIR / f"{APP_DATA_DIR_NAME}-data",
        )
ROOT_DIR, STORAGE_MODE = select_storage(
    compiled=IS_COMPILED,
    portable=IS_PORTABLE,
    development_root=DEV_ROOT,
    executable_dir=EXECUTABLE_DIR,
    user_data_dir=USER_DATA_DIR,
    app_name=APP_DATA_DIR_NAME,
)
ASSETS_DIR = BUNDLE_ROOT / "assets"
ICON_FILE = ASSETS_DIR / "icon.ico"
LOGS_DIR = ROOT_DIR / "logs"
EXPORTS_DIR = ROOT_DIR / "exports"
BACKUPS_DIR = EXPORTS_DIR / "backups"
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
HISTORY_FILE = DATA_DIR / "history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
