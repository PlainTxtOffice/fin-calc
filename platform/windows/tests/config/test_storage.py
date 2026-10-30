"""Verify storage selection without touching real user state."""

import tomllib
from pathlib import Path

from fin_calc.config import path_handler, storage


def arguments(tmp_path):
    return dict(compiled=True, portable=False, development_root=tmp_path / "dev",
                executable_dir=tmp_path / "exe", user_data_dir=tmp_path / "user" / "fin-calc",
                app_name="fin-calc")


def test_development_does_not_create_data(tmp_path):
    args = arguments(tmp_path)
    args["compiled"] = False
    assert storage.select_storage(**args) == (args["development_root"], "development")
    assert not args["development_root"].exists()


def test_installed_uses_per_user_storage(tmp_path):
    args = arguments(tmp_path)
    assert storage.select_storage(**args) == (args["user_data_dir"], "installed")
    assert not args["user_data_dir"].exists()


def test_portable_preserves_data_and_removes_probe(tmp_path):
    args = arguments(tmp_path)
    args["portable"] = True
    root = args["executable_dir"] / "fin-calc-data"
    root.mkdir(parents=True)
    saved = root / "sentinel.txt"
    saved.write_text("preserve", encoding="utf-8")
    assert storage.select_storage(**args) == (root, "portable")
    assert list(root.iterdir()) == [saved]
    assert saved.read_text(encoding="utf-8") == "preserve"


def test_portable_write_failure_falls_back(tmp_path, monkeypatch):
    args = arguments(tmp_path)
    args["portable"] = True
    def denied(*args, **kwargs):
        raise PermissionError("read-only")
    monkeypatch.setattr(storage.tempfile, "TemporaryFile", denied)
    assert storage.select_storage(**args) == (args["user_data_dir"], "portable-fallback")


def test_storage_metadata_matches_runtime():
    project = Path(__file__).resolve().parents[2]
    config = tomllib.loads((project / "pyproject.toml").read_text(encoding="utf-8"))
    assert config["tool"]["fin_calc"]["app-data-dir"] == path_handler.APP_DATA_DIR_NAME


def test_compiled_paths_use_bundle_and_original_executable(tmp_path, monkeypatch):
    from types import SimpleNamespace

    bundle = tmp_path / "unpacked"
    bundle.mkdir()
    (bundle / "portable.marker").touch()
    executable = tmp_path / "portable"
    local = tmp_path / "local"
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    namespace = {
        "__file__": str(bundle / "fin_calc" / "config" / "path_handler.py"),
        "__compiled__": SimpleNamespace(containing_dir=str(executable)),
    }
    source = Path(path_handler.__file__).read_text(encoding="utf-8")
    exec(compile(source, "path_handler.py", "exec"), namespace)
    assert namespace["ROOT_DIR"] == executable / "fin-calc-data"
    assert namespace["ASSETS_DIR"] == bundle / "assets"
    assert namespace["STORAGE_MODE"] == "portable"
    assert namespace["USER_DATA_DIR"] == local / "fin-calc"


def test_legacy_folder_is_renamed_when_only_it_exists(tmp_path):
    legacy = tmp_path / "Fin Calc"
    (legacy / "data").mkdir(parents=True)
    (legacy / "data" / "history.json").write_text("[]", encoding="utf-8")
    current = tmp_path / "fin-calc"
    assert storage.migrate_legacy_folder(legacy, current) is True
    assert not legacy.exists()
    assert (current / "data" / "history.json").read_text(encoding="utf-8") == "[]"


def test_legacy_folder_never_overwrites_current_data(tmp_path):
    legacy = tmp_path / "Fin Calc"
    legacy.mkdir()
    current = tmp_path / "fin-calc"
    current.mkdir()
    (current / "keep.txt").write_text("current", encoding="utf-8")
    assert storage.migrate_legacy_folder(legacy, current) is False
    assert legacy.is_dir()
    assert (current / "keep.txt").read_text(encoding="utf-8") == "current"


def test_missing_legacy_folder_is_ignored(tmp_path):
    current = tmp_path / "fin-calc"
    assert storage.migrate_legacy_folder(tmp_path / "Fin Calc", current) is False
    assert not current.exists()


def test_failed_rename_keeps_the_legacy_folder(tmp_path, monkeypatch):
    legacy = tmp_path / "Fin Calc"
    legacy.mkdir()
    def locked(self, target):
        raise PermissionError("in use")
    monkeypatch.setattr(Path, "rename", locked)
    assert storage.migrate_legacy_folder(legacy, tmp_path / "fin-calc") is False
    assert legacy.is_dir()


def test_compiled_build_migrates_legacy_folders(tmp_path, monkeypatch):
    from types import SimpleNamespace

    bundle = tmp_path / "unpacked"
    bundle.mkdir()
    (bundle / "portable.marker").touch()
    executable = tmp_path / "portable"
    (executable / "Fin Calc-data").mkdir(parents=True)
    (executable / "Fin Calc-data" / "saved.txt").write_text("portable", encoding="utf-8")
    local = tmp_path / "local"
    (local / "Fin Calc").mkdir(parents=True)
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    namespace = {
        "__file__": str(bundle / "fin_calc" / "config" / "path_handler.py"),
        "__compiled__": SimpleNamespace(containing_dir=str(executable)),
    }
    source = Path(path_handler.__file__).read_text(encoding="utf-8")
    exec(compile(source, "path_handler.py", "exec"), namespace)
    assert namespace["ROOT_DIR"] == executable / "fin-calc-data"
    assert (executable / "fin-calc-data" / "saved.txt").read_text(encoding="utf-8") == "portable"
    assert (local / "fin-calc").is_dir()
    assert not (local / "Fin Calc").exists()
