#!/usr/bin/env python3
from pathlib import Path
import os
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "README.md",
    "install.sh",
    "codex/project-init-orchestrator/SKILL.md",
    "codex/project-init-orchestrator/agents/openai.yaml",
    "claude-code/commands/project-init-orchestrator.md",
    "templates/AGENTS.md",
    "templates/SPEC.md",
    "templates/TASKS.md",
    "templates/WORKLOG.md",
    "templates/SUBAGENT_BRIEF.md",
    "templates/COMPLETION_AUDIT.md",
    "docs/superpowers/specs/2026-07-07-project-init-orchestrator-design.md",
    "docs/superpowers/specs/2026-07-07-project-init-orchestrator-design.zh.md",
    "docs/superpowers/plans/2026-07-08-project-init-orchestrator.md",
]


CONTENT_CHECKS = {
    "codex/project-init-orchestrator/SKILL.md": [
        "goal mode",
        "loop execution",
        "superpowers:brainstorming",
        "AGENTS.md",
        "docs/specs/",
        "subagent brief",
        "work logs",
        "Completion Audit",
    ],
    "claude-code/commands/project-init-orchestrator.md": [
        "Goal Mode",
        "Run The Loop",
        "AGENTS.md",
        "project spec",
        "subagent brief",
        "work logs",
        "Completion Audit",
    ],
    "README.md": [
        "Codex",
        "Claude Code",
        "install.sh",
        "AGENTS.md",
        "goal",
        "loop",
        "subagent",
        "work log",
    ],
}


TEMPLATE_HEADINGS = {
    "templates/AGENTS.md": [
        "## Project Goal",
        "## Goal And Loop Mode",
        "## Main Agent Responsibilities",
        "## Subagent Boundaries",
        "## Work Logs",
        "## Completion Audit",
    ],
    "templates/SPEC.md": [
        "## Background",
        "## Scope",
        "## Functional Requirements",
        "## Architecture",
        "## Testing And Verification",
        "## Acceptance Criteria",
    ],
    "templates/TASKS.md": [
        "## Goal",
        "## Loop State",
        "## Tasks",
        "## Dispatch Rules",
    ],
    "templates/WORKLOG.md": [
        "## Goal State",
        "## Agent Identity",
        "## Entries",
        "## Decision Log",
        "## Completion Evidence",
    ],
    "templates/SUBAGENT_BRIEF.md": [
        "## Role",
        "## Objective",
        "## Allowed Scope",
        "## Forbidden Scope",
        "## Verification",
        "## Handoff Requirements",
    ],
    "templates/COMPLETION_AUDIT.md": [
        "## Objective",
        "## Evidence Summary",
        "## Verification Commands",
        "## Completion Decision",
    ],
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def validate_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail("Missing files: " + ", ".join(missing))


def validate_install_executable() -> None:
    install = ROOT / "install.sh"
    if not os.access(install, os.X_OK):
        fail("install.sh is not executable")


def validate_skill_frontmatter() -> None:
    text = read("codex/project-init-orchestrator/SKILL.md")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("Codex Skill is missing YAML-like frontmatter")
    frontmatter = match.group(1)
    for key in ["name:", "description:"]:
        if key not in frontmatter:
            fail(f"Codex Skill frontmatter missing {key}")
    if "project-init-orchestrator" not in frontmatter:
        fail("Codex Skill frontmatter does not name project-init-orchestrator")


def validate_content_terms() -> None:
    for path, terms in CONTENT_CHECKS.items():
        text = read(path)
        missing = [term for term in terms if term not in text]
        if missing:
            fail(f"{path} missing required terms: {', '.join(missing)}")


def validate_templates() -> None:
    for path, headings in TEMPLATE_HEADINGS.items():
        text = read(path)
        missing = [heading for heading in headings if heading not in text]
        if missing:
            fail(f"{path} missing required headings: {', '.join(missing)}")


def main() -> None:
    validate_required_files()
    validate_install_executable()
    validate_skill_frontmatter()
    validate_content_terms()
    validate_templates()
    print("Repository validation passed.")


if __name__ == "__main__":
    main()
