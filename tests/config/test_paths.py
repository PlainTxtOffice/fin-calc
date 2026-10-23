"""Verify development storage paths after moving the Windows application."""

from pathlib import Path

from src.windows.config.path_handler import (
    ASSETS_DIR,
    DATA_DIR,
    DEV_ROOT,
    EXPORTS_DIR,
    LOGS_DIR,
)


def test_development_paths_use_repository_root():
    root = Path(__file__).resolve().parents[2]
    assert DEV_ROOT == root
    assert ASSETS_DIR == root / "assets"
    assert DATA_DIR == root / "data"
    assert EXPORTS_DIR == root / "exports"
    assert LOGS_DIR == root / "logs"
