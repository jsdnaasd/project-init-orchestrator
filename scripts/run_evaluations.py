#!/usr/bin/env python3
"""Run deterministic behavioral scenarios for the Codex Skill execution layer."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
PIO_PATH = ROOT / "codex" / "project-init-orchestrator" / "scripts" / "pio.py"


def load_pio():
    spec = importlib.util.spec_from_file_location("pio_evaluation_target", PIO_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {PIO_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def initialize(pio, project: Path, roles: list[str] | None = None):
    return pio.initialize_project(
        project,
        project_name="Evaluation Project",
        objective="Verify deterministic project orchestration.",
        roles=roles or [],
    )


def scenario_empty_initialization(pio, project: Path) -> str:
    initialize(pio, project, ["implementation"])
    report = pio.validate_project(project, "structure")
    assert report["passed"]
    return "All required control and state artifacts were created."


def scenario_idempotent_rerun(pio, project: Path) -> str:
    initialize(pio, project)
    before = {
        path.relative_to(project).as_posix(): path.read_bytes()
        for path in project.rglob("*")
        if path.is_file()
    }
    result = initialize(pio, project)
    after = {
        path.relative_to(project).as_posix(): path.read_bytes()
        for path in project.rglob("*")
        if path.is_file()
    }
    assert result["created"] == []
    assert before == after
    return "A second run produced no file changes."


def scenario_preserve_existing_agents(pio, project: Path) -> str:
    existing = project / "AGENTS.md"
    existing.write_text("# User-owned rules\n", encoding="utf-8")
    result = initialize(pio, project)
    assert existing.read_text(encoding="utf-8") == "# User-owned rules\n"
    assert "AGENTS.md" in result["preserved"]
    return "Existing AGENTS.md content was preserved byte-for-byte."


def scenario_invalid_transition(pio, project: Path) -> str:
    initialize(pio, project)
    try:
        pio.transition_project(project, "complete", evidence="invalid shortcut")
    except pio.OrchestratorError:
        return "The initialized-to-complete shortcut was rejected."
    raise AssertionError("Invalid transition was accepted")


def prepare_policy_project(pio, project: Path):
    initialize(pio, project, ["implementation"])
    (project / "src").mkdir()
    (project / "src" / "app.py").write_text("VERSION = 1\n", encoding="utf-8")
    (project / "README.md").write_text("before\n", encoding="utf-8")
    pio.set_role_policy(
        project,
        "implementation",
        allowed_paths=["src/**"],
        forbidden_paths=["src/secrets/**"],
    )
    pio.capture_baseline(project, "implementation")


def scenario_allowed_boundary(pio, project: Path) -> str:
    prepare_policy_project(pio, project)
    (project / "src" / "app.py").write_text("VERSION = 2\n", encoding="utf-8")
    report = pio.audit_role(project, "implementation")
    assert report["passed"] and report["allowed"] == ["src/app.py"]
    return "A change inside src/** passed the role audit."


def scenario_forbidden_boundary(pio, project: Path) -> str:
    prepare_policy_project(pio, project)
    secret = project / "src" / "secrets" / "token.txt"
    secret.parent.mkdir(parents=True)
    secret.write_text("secret", encoding="utf-8")
    report = pio.audit_role(project, "implementation")
    assert not report["passed"]
    assert {item["path"] for item in report["violations"]} == {"src/secrets/token.txt"}
    return "A forbidden sensitive path was detected."


def scenario_outside_scope(pio, project: Path) -> str:
    prepare_policy_project(pio, project)
    (project / "README.md").write_text("after\n", encoding="utf-8")
    report = pio.audit_role(project, "implementation")
    assert not report["passed"]
    assert report["violations"] == [{"path": "README.md", "reason": "outside-scope"}]
    return "A change outside src/** was detected."


def scenario_readiness_gate(pio, project: Path) -> str:
    initialize(pio, project)
    report = pio.validate_project(project, "ready")
    assert not report["passed"]
    assert any("TODO" in error for error in report["errors"])
    return "Unresolved requirements prevented implementation readiness."


def scenario_inspection_is_read_only(pio, project: Path) -> str:
    (project / "pyproject.toml").write_text(
        "[project]\nname='eval'\n", encoding="utf-8"
    )
    report = pio.inspect_project(project)
    assert report["stacks"] == ["python"]
    assert not (project / ".project-init-orchestrator").exists()
    return "Inspection detected Python and performed no writes."


def scenario_context_snapshot(pio, project: Path) -> str:
    initialize(pio, project)
    pio.log_event(
        project,
        event_type="decision",
        actor="main",
        message="Keep the evaluation deterministic.",
    )
    result = pio.compact_context(project, recent_limit=2)
    snapshot = (project / ".project-init-orchestrator" / "snapshot.md").read_text(
        encoding="utf-8"
    )
    assert result["total_events"] == 2
    assert "Keep the evaluation deterministic." in snapshot
    return "A two-event source log produced a concise recoverable snapshot."


SCENARIOS: list[tuple[str, str, Callable]] = [
    ("empty-initialization", "initialization", scenario_empty_initialization),
    ("idempotent-rerun", "idempotency", scenario_idempotent_rerun),
    ("preserve-existing-agents", "idempotency", scenario_preserve_existing_agents),
    ("invalid-transition", "state-machine", scenario_invalid_transition),
    ("allowed-boundary", "boundary-audit", scenario_allowed_boundary),
    ("forbidden-boundary", "boundary-audit", scenario_forbidden_boundary),
    ("outside-scope", "boundary-audit", scenario_outside_scope),
    ("readiness-gate", "validation", scenario_readiness_gate),
    ("read-only-inspection", "inspection", scenario_inspection_is_read_only),
    ("context-snapshot", "context", scenario_context_snapshot),
]


def run_evaluations() -> dict:
    pio = load_pio()
    results = []
    for name, category, scenario in SCENARIOS:
        with tempfile.TemporaryDirectory(prefix=f"pio-eval-{name}-") as directory:
            try:
                detail = scenario(pio, Path(directory))
            except Exception as exc:  # evaluation must preserve the failure detail
                results.append(
                    {
                        "name": name,
                        "category": category,
                        "passed": False,
                        "detail": f"{type(exc).__name__}: {exc}",
                    }
                )
            else:
                results.append(
                    {
                        "name": name,
                        "category": category,
                        "passed": True,
                        "detail": detail,
                    }
                )
    passed = sum(item["passed"] for item in results)
    boundary = [item for item in results if item["category"] == "boundary-audit"]
    return {
        "tool_version": pio.VERSION,
        "scenario_count": len(results),
        "passed_count": passed,
        "success_rate": round(passed / len(results), 4),
        "boundary_detection_rate": round(
            sum(item["passed"] for item in boundary) / len(boundary), 4
        ),
        "results": results,
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Project Init Orchestrator Evaluation Report",
        "",
        f"- Tool version: {report['tool_version']}",
        f"- Behavioral scenarios: {report['scenario_count']}",
        f"- Passed: {report['passed_count']}",
        f"- Scenario success rate: {report['success_rate'] * 100:.0f}%",
        f"- Boundary audit scenario pass rate: {report['boundary_detection_rate'] * 100:.0f}%",
        "",
        "These are deterministic local scenarios, not claims about model quality or production reliability.",
        "",
        "| Scenario | Category | Result | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["results"]:
        result = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"| {item['name']} | {item['category']} | {result} | {item['detail']} |"
        )
    lines.extend(
        [
            "",
            "## Reproduce",
            "",
            "```bash",
            "python3 scripts/run_evaluations.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write docs/evaluation-report.md and docs/evaluation-report.json",
    )
    args = parser.parse_args()
    report = run_evaluations()
    if args.write:
        (ROOT / "docs" / "evaluation-report.md").write_text(
            markdown_report(report), encoding="utf-8"
        )
        (ROOT / "docs" / "evaluation-report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed_count"] == report["scenario_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
