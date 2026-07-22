#!/usr/bin/env python3
"""Validate the release structure without external dependencies."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "codex" / "project-init-orchestrator"

REQUIRED_FILES = [
    "VERSION",
    "LICENSE",
    "README.md",
    "install.sh",
    ".github/workflows/ci.yml",
    "codex/project-init-orchestrator/SKILL.md",
    "codex/project-init-orchestrator/agents/openai.yaml",
    "codex/project-init-orchestrator/scripts/pio.py",
    "codex/project-init-orchestrator/references/workflow.md",
    "codex/project-init-orchestrator/references/cli.md",
    "codex/project-init-orchestrator/assets/templates/AGENTS.md",
    "codex/project-init-orchestrator/assets/templates/SPEC.md",
    "codex/project-init-orchestrator/assets/templates/TASKS.md",
    "codex/project-init-orchestrator/assets/templates/WORKLOG.md",
    "codex/project-init-orchestrator/assets/templates/SUBAGENT_BRIEF.md",
    "codex/project-init-orchestrator/assets/templates/SUBAGENT_WORKLOG.md",
    "codex/project-init-orchestrator/assets/templates/COMPLETION_AUDIT.md",
    "scripts/run_evaluations.py",
    "tests/test_pio_cli.py",
    "tests/test_installer.py",
    "docs/architecture.md",
    "docs/security-review.md",
    "docs/evaluation-report.md",
    "docs/evaluation-report.json",
    "docs/RESUME.zh-CN.md",
    "examples/demo-session.md",
]

FORBIDDEN_PATHS = [
    "claude-code/commands/project-init-orchestrator.md",
    "templates/AGENTS.md",
]

TEMPLATE_TOKENS = {
    "AGENTS.md": ["{{PROJECT_NAME}}", "{{OBJECTIVE}}", "{{ROLES_TABLE}}"],
    "SPEC.md": ["{{PROJECT_NAME}}", "{{OBJECTIVE}}", "{{DATE}}"],
    "TASKS.md": ["{{PROJECT_NAME}}", "{{OBJECTIVE}}"],
    "WORKLOG.md": ["{{PROJECT_NAME}}", "{{OBJECTIVE}}", "{{DATE}}"],
    "SUBAGENT_BRIEF.md": ["{{ROLE}}", "{{ALLOWED_PATHS}}", "{{FORBIDDEN_PATHS}}"],
    "SUBAGENT_WORKLOG.md": ["{{ROLE}}", "{{OBJECTIVE}}"],
    "COMPLETION_AUDIT.md": ["{{PROJECT_NAME}}", "{{OBJECTIVE}}"],
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def validate_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))
    present_legacy = [path for path in FORBIDDEN_PATHS if (ROOT / path).exists()]
    if present_legacy:
        fail("Legacy dual-platform paths remain: " + ", ".join(present_legacy))


def validate_executables() -> None:
    for relative in [
        "install.sh",
        "scripts/validate_repository.py",
        "scripts/run_evaluations.py",
        "codex/project-init-orchestrator/scripts/pio.py",
    ]:
        if not os.access(ROOT / relative, os.X_OK):
            fail(f"Expected executable file: {relative}")


def validate_skill() -> None:
    text = read("codex/project-init-orchestrator/SKILL.md")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md has no YAML frontmatter")
    keys = [
        line.split(":", 1)[0].strip()
        for line in match.group(1).splitlines()
        if ":" in line
    ]
    if keys != ["name", "description"]:
        fail(f"SKILL.md frontmatter must contain only name and description, got {keys}")
    required_terms = [
        "native main goal",
        "transition",
        "set-policy",
        "baseline",
        "audit",
        "validate --stage complete",
        "references/workflow.md",
        "references/cli.md",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        fail("SKILL.md missing workflow terms: " + ", ".join(missing))

    metadata = read("codex/project-init-orchestrator/agents/openai.yaml")
    for term in ["display_name", "short_description", "$project-init-orchestrator"]:
        if term not in metadata:
            fail(f"agents/openai.yaml missing {term}")


def validate_templates() -> None:
    directory = SKILL / "assets" / "templates"
    for filename, tokens in TEMPLATE_TOKENS.items():
        text = (directory / filename).read_text(encoding="utf-8")
        missing = [token for token in tokens if token not in text]
        if missing:
            fail(f"{filename} missing template tokens: {', '.join(missing)}")


def validate_version() -> None:
    version = read("VERSION").strip()
    cli = read("codex/project-init-orchestrator/scripts/pio.py")
    if f'VERSION = "{version}"' not in cli:
        fail("VERSION does not match pio.py")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"VERSION is not semantic: {version}")


def validate_commands() -> None:
    commands = [
        ["bash", "-n", str(ROOT / "install.sh")],
        [sys.executable, str(SKILL / "scripts" / "pio.py"), "--version"],
        [sys.executable, str(SKILL / "scripts" / "pio.py"), "--help"],
    ]
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            fail(f"Command failed: {' '.join(command)}\n{result.stderr}")


def validate_readme() -> None:
    text = read("README.md")
    required = [
        "Codex-only",
        "10/10",
        "pio.py",
        "events.jsonl",
        "outside-scope",
        "能力边界",
        "MIT",
    ]
    missing = [term for term in required if term not in text]
    if missing:
        fail("README.md missing release content: " + ", ".join(missing))


def main() -> None:
    validate_files()
    validate_executables()
    validate_skill()
    validate_templates()
    validate_version()
    validate_commands()
    validate_readme()
    print("Repository validation passed for Project Init Orchestrator v0.2.0.")


if __name__ == "__main__":
    main()
