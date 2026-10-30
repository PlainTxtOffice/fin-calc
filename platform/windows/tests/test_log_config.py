"""Tests for application log file naming."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from fin_calc.config.logging import log_config
from fin_calc.config.path_handler import APP_DATA_DIR_NAME

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture
def logs_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Point logging at a temporary folder and close handlers afterwards."""
    monkeypatch.setattr(log_config, "LOGS_DIR", tmp_path)
    yield tmp_path
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()


def test_default_log_name_uses_app_data_dir_name(logs_dir: Path) -> None:
    """Name the log after APP_DATA_DIR_NAME when no project name is given."""
    log_config.configure_logging()

    log_name = APP_DATA_DIR_NAME.replace(" ", "_")
    assert (logs_dir / f"{log_name}.log").is_file()


def test_project_name_replaces_spaces(logs_dir: Path) -> None:
    """Name the log after the given project name with spaces replaced."""
    log_config.configure_logging("Fin Calc")

    assert (logs_dir / "Fin_Calc.log").is_file()
