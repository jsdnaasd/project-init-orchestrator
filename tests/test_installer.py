from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.sh"


def run_installer(codex_home: Path, *args: str, dry_run: bool = False):
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    if dry_run:
        env["DRY_RUN"] = "1"
    return subprocess.run(
        [str(INSTALLER), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.integration
def test_installer_dry_run_makes_no_changes(tmp_path: Path):
    codex_home = tmp_path / "codex"

    result = run_installer(codex_home, "--install", dry_run=True)

    assert result.returncode == 0
    assert "dry-run" in result.stdout
    assert not codex_home.exists()


@pytest.mark.integration
def test_reinstall_backs_up_existing_skill(tmp_path: Path):
    codex_home = tmp_path / "codex"
    first = run_installer(codex_home, "--install")
    destination = codex_home / "skills" / "project-init-orchestrator"
    marker = destination / "user-marker.txt"
    marker.write_text("preserve me", encoding="utf-8")

    second = run_installer(codex_home, "--install")
    backups = sorted((codex_home / "skills").glob("project-init-orchestrator.backup-*"))

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert (destination / "scripts" / "pio.py").is_file()
    assert backups
    assert (backups[-1] / "user-marker.txt").read_text(
        encoding="utf-8"
    ) == "preserve me"


@pytest.mark.integration
def test_uninstall_is_recoverable(tmp_path: Path):
    codex_home = tmp_path / "codex"
    assert run_installer(codex_home, "--install").returncode == 0
    destination = codex_home / "skills" / "project-init-orchestrator"

    result = run_installer(codex_home, "--uninstall")
    backups = sorted((codex_home / "skills").glob("project-init-orchestrator.backup-*"))

    assert result.returncode == 0, result.stderr
    assert not destination.exists()
    assert backups
    assert (backups[-1] / "SKILL.md").is_file()
