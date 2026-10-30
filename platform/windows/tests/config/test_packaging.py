"""Exercise distribution privacy and release validation contracts."""

import importlib.util
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]


def helper(name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / "scripts" / "nuitka" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_privacy_scan_handles_chunk_boundary_and_utf16(tmp_path, monkeypatch):
    monkeypatch.setenv("USERNAME", "private-test-user")
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text('[project]\nauthors = [{email = "private@example.test"}]', encoding="utf-8")
    dist = tmp_path / "main.dist"
    dist.mkdir()
    (dist / "app.exe").write_bytes(b"x" * (1024 * 1024 - 4) + b"private-test-user")
    (dist / "settings.txt").write_bytes("private@example.test".encode("utf-16le"))
    hits = helper("privacy_scan").scan(dist, project, tmp_path)
    assert {hit["term"] for hit in hits} == {"private-test-user", "private@example.test"}


def test_release_validator_reports_without_mutation(tmp_path):
    dist = tmp_path / "main.dist"
    dist.mkdir()
    exe = dist / "Fin Calc.exe"
    exe.write_bytes(b"executable fixture")
    validator = helper("validate_dist")
    assert validator.validate(dist, PROJECT) == []
    saved = dist / "data" / "history.json"
    saved.parent.mkdir()
    saved.write_text("[]", encoding="utf-8")
    marker = dist / "portable.marker"
    marker.touch()
    problems = validator.validate(dist, PROJECT)
    assert any("history.json" in problem for problem in problems)
    assert any("portable.marker" in problem for problem in problems)
    assert saved.read_text(encoding="utf-8") == "[]"
    assert marker.exists()
    assert exe.read_bytes() == b"executable fixture"


def test_release_validator_rejects_missing_outputs(tmp_path):
    validator = helper("validate_dist")
    assert validator.validate(tmp_path / "absent", PROJECT)
    assert validator.validate(tmp_path, PROJECT) == ["Distribution contains no executable."]
