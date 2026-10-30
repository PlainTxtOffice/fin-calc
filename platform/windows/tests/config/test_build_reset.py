"""Verify explicit reset stays inside isolated application-data folders."""

import os
import subprocess
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / "scripts/nuitka/BuildSupport.psm1"


def test_reset_is_opt_in_and_preserves_neighboring_data(tmp_path):
    user = tmp_path / "user"
    output = tmp_path / "output"
    targets = [user / "fin-calc", output / "fin-calc-data"]
    for target in targets:
        target.mkdir(parents=True)
        (target / "history.json").write_text("test data", encoding="utf-8")
    neighbor = user / "other.txt"
    neighbor.write_text("preserve", encoding="utf-8")
    script = tmp_path / "reset.ps1"
    script.write_text(
        "param($Module, $Output, [switch]$Reset)\n"
        "$ErrorActionPreference = 'Stop'\n"
        "Import-Module $Module -Force\n"
        "$config = [pscustomobject]@{AppDataName='fin-calc';Output=$Output}\n"
        "Show-PersistedData $config -Portable -ResetRuntimeDefaults:$Reset\n",
        encoding="utf-8",
    )
    command = ["pwsh", "-NoProfile", "-File", str(script), str(MODULE), str(output)]
    env = {**os.environ, "LOCALAPPDATA": str(user)}
    subprocess.run(command, env=env, check=True, capture_output=True, timeout=30)
    assert all(target.exists() for target in targets)
    subprocess.run(command + ["-Reset"], env=env, check=True, capture_output=True, timeout=30)
    assert all(not target.exists() for target in targets)
    assert neighbor.read_text(encoding="utf-8") == "preserve"
