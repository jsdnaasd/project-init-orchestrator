from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PIO_PATH = ROOT / "codex" / "project-init-orchestrator" / "scripts" / "pio.py"


@pytest.fixture(scope="session")
def pio():
    spec = importlib.util.spec_from_file_location(
        "project_init_orchestrator_cli", PIO_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import CLI from {PIO_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def initialized_project(tmp_path: Path, pio):
    pio.initialize_project(
        tmp_path,
        project_name="Demo Project",
        objective="Build a reliable demo application.",
        roles=["implementation"],
    )
    return tmp_path
