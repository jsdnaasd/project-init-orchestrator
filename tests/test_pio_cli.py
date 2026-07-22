from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PIO_PATH = ROOT / "codex" / "project-init-orchestrator" / "scripts" / "pio.py"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_init_creates_artifacts_and_persistent_state(tmp_path: Path, pio):
    result = pio.initialize_project(
        tmp_path,
        project_name="Example",
        objective="Ship an example safely.",
        roles=["implementation", "verification"],
    )

    assert result["created"]
    assert (tmp_path / "AGENTS.md").is_file()
    specs = list((tmp_path / "docs" / "specs").glob("*-project-spec.md"))
    assert specs
    assert specs[0].name.startswith(datetime.now().astimezone().date().isoformat())
    assert (tmp_path / "docs" / "tasks" / "project-tasks.md").is_file()
    assert (tmp_path / "docs" / "worklogs" / "main-worklog.md").is_file()
    assert (
        tmp_path / "docs" / "agents" / "subagent-briefs" / "implementation.md"
    ).is_file()

    state = read_json(tmp_path / ".project-init-orchestrator" / "state.json")
    config = read_json(tmp_path / ".project-init-orchestrator" / "config.json")
    assert state["phase"] == "initialized"
    assert state["objective"] == "Ship an example safely."
    assert config["roles"]["implementation"]["allowed_paths"] == []
    assert (tmp_path / ".project-init-orchestrator" / "events.jsonl").is_file()
    assert "Ship an example safely." in (
        tmp_path / ".project-init-orchestrator" / "snapshot.md"
    ).read_text(encoding="utf-8")


def test_init_is_idempotent_and_preserves_existing_agents(tmp_path: Path, pio):
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Existing project rules\n", encoding="utf-8")

    first = pio.initialize_project(
        tmp_path,
        project_name="Existing",
        objective="Preserve existing files.",
        roles=[],
    )
    before = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    second = pio.initialize_project(
        tmp_path,
        project_name="Existing",
        objective="Preserve existing files.",
        roles=[],
    )
    after = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    assert agents.read_text(encoding="utf-8") == "# Existing project rules\n"
    assert "AGENTS.md" in first["preserved"]
    assert second["created"] == []
    assert before == after


def test_state_machine_enforces_transitions_and_evidence(
    initialized_project: Path, pio
):
    with pytest.raises(pio.OrchestratorError, match="Invalid transition"):
        pio.transition_project(initialized_project, "complete", evidence="too early")

    for phase in ["clarify", "spec", "plan", "execute"]:
        pio.transition_project(initialized_project, phase)

    with pytest.raises(pio.OrchestratorError, match="requires evidence"):
        pio.transition_project(initialized_project, "verify")

    state = pio.transition_project(
        initialized_project,
        "verify",
        evidence="python3 -m pytest passed",
    )
    assert state["phase"] == "verify"
    assert state["iteration"] == 1
    assert state["evidence"][-1]["value"] == "python3 -m pytest passed"


def test_log_and_compact_preserve_events(initialized_project: Path, pio):
    pio.log_event(
        initialized_project,
        event_type="decision",
        actor="main",
        message="Use the standard library only.",
    )
    result = pio.compact_context(initialized_project, recent_limit=2)

    events = (
        (initialized_project / ".project-init-orchestrator" / "events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    snapshot = (
        initialized_project / ".project-init-orchestrator" / "snapshot.md"
    ).read_text(encoding="utf-8")
    assert len(events) >= 2
    assert result["total_events"] == len(events)
    assert "Use the standard library only." in snapshot
    assert "Recent Events" in snapshot


def test_inspect_detects_stack_without_writing(tmp_path: Path, pio):
    (tmp_path / "package.json").write_text(
        '{"scripts":{"test":"vitest"}}', encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\n", encoding="utf-8"
    )

    report = pio.inspect_project(tmp_path)

    assert report["stacks"] == ["node", "python"]
    assert "npm test" in report["commands"]
    assert not (tmp_path / ".project-init-orchestrator").exists()


def test_boundary_audit_accepts_allowed_changes(initialized_project: Path, pio):
    source = initialized_project / "src"
    source.mkdir()
    app = source / "app.py"
    app.write_text("VERSION = 1\n", encoding="utf-8")
    pio.set_role_policy(
        initialized_project,
        "implementation",
        allowed_paths=["src/**"],
        forbidden_paths=["src/secrets/**"],
    )
    pio.capture_baseline(initialized_project, "implementation")

    app.write_text("VERSION = 2\n", encoding="utf-8")
    report = pio.audit_role(initialized_project, "implementation")

    assert report["passed"] is True
    assert report["allowed"] == ["src/app.py"]
    assert report["violations"] == []


def test_boundary_audit_detects_forbidden_and_out_of_scope_changes(
    initialized_project: Path, pio
):
    (initialized_project / "src" / "secrets").mkdir(parents=True)
    (initialized_project / "src" / "secrets" / "token.txt").write_text(
        "before", encoding="utf-8"
    )
    readme = initialized_project / "README.md"
    readme.write_text("before\n", encoding="utf-8")
    pio.set_role_policy(
        initialized_project,
        "implementation",
        allowed_paths=["src/**"],
        forbidden_paths=["src/secrets/**"],
    )
    pio.capture_baseline(initialized_project, "implementation")

    (initialized_project / "src" / "secrets" / "token.txt").write_text(
        "after", encoding="utf-8"
    )
    readme.write_text("after\n", encoding="utf-8")
    report = pio.audit_role(initialized_project, "implementation")

    by_path = {item["path"]: item["reason"] for item in report["violations"]}
    assert report["passed"] is False
    assert by_path["src/secrets/token.txt"] == "forbidden"
    assert by_path["README.md"] == "outside-scope"


def test_validation_distinguishes_structure_and_readiness(
    initialized_project: Path, pio
):
    structure = pio.validate_project(initialized_project, stage="structure")
    ready = pio.validate_project(initialized_project, stage="ready")

    assert structure["passed"] is True
    assert ready["passed"] is False
    assert any("TODO" in error for error in ready["errors"])


@pytest.mark.integration
def test_cli_help_and_status(initialized_project: Path):
    help_result = subprocess.run(
        [sys.executable, str(PIO_PATH), "--help"],
        text=True,
        capture_output=True,
        check=False,
    )
    status_result = subprocess.run(
        [
            sys.executable,
            str(PIO_PATH),
            "status",
            "--project",
            str(initialized_project),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert help_result.returncode == 0
    assert "Project Init Orchestrator" in help_result.stdout
    assert status_result.returncode == 0
    assert json.loads(status_result.stdout)["phase"] == "initialized"


def test_block_unblock_and_transition_guard(initialized_project: Path, pio):
    blocked = pio.block_project(initialized_project, "Waiting for an API credential.")
    assert blocked["status"] == "blocked"
    with pytest.raises(pio.OrchestratorError, match="unblock"):
        pio.transition_project(initialized_project, "clarify")

    active = pio.unblock_project(initialized_project, "Use the approved local fixture.")
    assert active["status"] == "active"
    assert active["blockers"][0]["resolved"] is True
    assert pio.transition_project(initialized_project, "clarify")["phase"] == "clarify"


def test_add_role_and_policy_input_errors(tmp_path: Path, pio):
    pio.initialize_project(
        tmp_path,
        project_name="Roles",
        objective="Exercise role management.",
        roles=[],
    )
    added = pio.add_role(tmp_path, "Visual QA")
    duplicate = pio.add_role(tmp_path, "visual-qa")

    assert added["role"] == "visual-qa"
    assert duplicate["created"] == []
    with pytest.raises(pio.OrchestratorError, match="Unknown role"):
        pio.set_role_policy(
            tmp_path, "missing", allowed_paths=["src/**"], forbidden_paths=[]
        )
    with pytest.raises(pio.OrchestratorError, match="Unsafe path pattern"):
        pio.set_role_policy(
            tmp_path,
            "visual-qa",
            allowed_paths=["../outside/**"],
            forbidden_paths=[],
        )


def test_initialization_rejects_partial_or_conflicting_state(tmp_path: Path, pio):
    state_directory = tmp_path / ".project-init-orchestrator"
    state_directory.mkdir()
    (state_directory / "config.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(pio.OrchestratorError, match="partially initialized"):
        pio.initialize_project(
            tmp_path,
            project_name="Partial",
            objective="Reject partial state.",
            roles=[],
        )

    other = tmp_path / "other"
    other.mkdir()
    pio.initialize_project(
        other,
        project_name="Original",
        objective="Keep the original objective.",
        roles=[],
    )
    with pytest.raises(pio.OrchestratorError, match="different name or objective"):
        pio.initialize_project(
            other,
            project_name="Changed",
            objective="Replace the objective.",
            roles=[],
        )
    second = pio.initialize_project(
        other,
        project_name="Original",
        objective="Keep the original objective.",
        roles=["review"],
    )
    assert second["created"] == ["role:review"]


def test_complete_validation_path(tmp_path: Path, pio):
    pio.initialize_project(
        tmp_path,
        project_name="Complete",
        objective="Prove completion validation.",
        roles=[],
    )
    config = read_json(tmp_path / ".project-init-orchestrator" / "config.json")
    for key in ["agents", "spec", "tasks"]:
        path = tmp_path / config["artifacts"][key]
        text = re.sub(
            r"<!-- TODO:.*?-->",
            "Defined and verified.",
            path.read_text(encoding="utf-8"),
        )
        path.write_text(text, encoding="utf-8")

    assert pio.validate_project(tmp_path, "ready")["passed"] is True
    for phase in ["clarify", "spec", "plan", "execute"]:
        pio.transition_project(tmp_path, phase)
    pio.transition_project(tmp_path, "verify", evidence="tests passed")
    pio.transition_project(tmp_path, "audit", evidence="audit passed")
    pio.transition_project(tmp_path, "complete", evidence="all criteria mapped")

    audit_path = tmp_path / config["artifacts"]["completion_audit"]
    audit = re.sub(
        r"<!-- TODO:.*?-->",
        "Verified evidence",
        audit_path.read_text(encoding="utf-8"),
    )
    audit = audit.replace("Unverified", "Complete").replace("- [ ]", "- [x]")
    audit_path.write_text(audit, encoding="utf-8")

    assert pio.validate_project(tmp_path, "complete")["passed"] is True


def test_validation_and_event_errors(initialized_project: Path, pio):
    with pytest.raises(pio.OrchestratorError, match="Unknown validation stage"):
        pio.validate_project(initialized_project, "unknown")
    with pytest.raises(pio.OrchestratorError, match="Unknown event type"):
        pio.log_event(
            initialized_project,
            event_type="unknown",
            actor="main",
            message="invalid",
        )
    with pytest.raises(pio.OrchestratorError, match="at least 1"):
        pio.compact_context(initialized_project, 0)
    with pytest.raises(pio.OrchestratorError, match="Missing orchestrator state"):
        pio.audit_role(initialized_project, "implementation")


def test_git_repository_baseline_and_invalid_package_json(tmp_path: Path, pio):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "package.json").write_text("{invalid", encoding="utf-8")
    inspection = pio.inspect_project(tmp_path)
    assert inspection["git_repository"] is True
    assert inspection["commands"] == ["npm test"]

    pio.initialize_project(
        tmp_path,
        project_name="Git",
        objective="Exercise Git-aware scanning.",
        roles=["review"],
    )
    pio.set_role_policy(
        tmp_path, "review", allowed_paths=["package.json"], forbidden_paths=[]
    )
    baseline = pio.capture_baseline(tmp_path, "review")
    assert baseline["file_count"] >= 1


def test_audit_detects_gitignored_secret_and_nested_secret(tmp_path: Path, pio):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")
    (tmp_path / ".env").write_text("TOKEN=before\n", encoding="utf-8")
    nested_secret = tmp_path / "src" / "secrets" / "token.txt"
    nested_secret.parent.mkdir(parents=True)
    nested_secret.write_text("before\n", encoding="utf-8")
    pio.initialize_project(
        tmp_path,
        project_name="Sensitive",
        objective="Detect ignored and nested sensitive files.",
        roles=["implementation"],
    )
    pio.set_role_policy(
        tmp_path, "implementation", allowed_paths=["**"], forbidden_paths=[]
    )
    pio.capture_baseline(tmp_path, "implementation")

    (tmp_path / ".env").write_text("TOKEN=after\n", encoding="utf-8")
    nested_secret.write_text("after\n", encoding="utf-8")
    report = pio.audit_role(tmp_path, "implementation")

    assert report["passed"] is False
    assert {item["path"] for item in report["violations"]} == {
        ".env",
        "src/secrets/token.txt",
    }
    assert {item["reason"] for item in report["violations"]} == {"forbidden"}


def test_audit_tracks_symlink_target_and_rejects_policy_drift(tmp_path: Path, pio):
    project = tmp_path / "project"
    project.mkdir()
    first_target = tmp_path / "first.txt"
    second_target = tmp_path / "second.txt"
    first_target.write_text("first\n", encoding="utf-8")
    second_target.write_text("second\n", encoding="utf-8")
    links = project / "links"
    links.mkdir()
    current = links / "current"
    current.symlink_to(first_target)
    pio.initialize_project(
        project,
        project_name="Symlink",
        objective="Detect link and policy changes.",
        roles=["review"],
    )
    pio.set_role_policy(
        project, "review", allowed_paths=["links/**"], forbidden_paths=[]
    )
    pio.capture_baseline(project, "review")

    current.unlink()
    current.symlink_to(second_target)
    report = pio.audit_role(project, "review")
    assert report["passed"] is True
    assert report["allowed"] == ["links/current"]

    pio.set_role_policy(project, "review", allowed_paths=["**"], forbidden_paths=[])
    with pytest.raises(pio.OrchestratorError, match="changed after baseline"):
        pio.audit_role(project, "review")


def invoke_main(pio, capsys, arguments: list[str], expected_code: int = 0):
    code = pio.main(arguments)
    captured = capsys.readouterr()
    assert code == expected_code, captured.err
    output = captured.out if expected_code != 2 else captured.err
    return json.loads(output)


def test_main_dispatches_all_cli_commands(tmp_path: Path, pio, capsys):
    project_args = ["--project", str(tmp_path)]
    assert invoke_main(pio, capsys, ["inspect", *project_args])["project"] == str(
        tmp_path
    )
    invoke_main(
        pio,
        capsys,
        [
            "init",
            *project_args,
            "--name",
            "CLI",
            "--objective",
            "Exercise command dispatch.",
        ],
    )
    assert invoke_main(pio, capsys, ["status", *project_args])["phase"] == "initialized"
    assert "snapshot" in invoke_main(pio, capsys, ["resume", *project_args])
    invoke_main(pio, capsys, ["transition", "clarify", *project_args])
    invoke_main(
        pio,
        capsys,
        [
            "log",
            *project_args,
            "--type",
            "progress",
            "--actor",
            "main",
            "--message",
            "CLI dispatch works.",
        ],
    )
    invoke_main(pio, capsys, ["compact", *project_args, "--recent", "3"])
    invoke_main(pio, capsys, ["add-role", "implementation", *project_args])
    invoke_main(
        pio,
        capsys,
        [
            "set-policy",
            "implementation",
            *project_args,
            "--allow",
            "src/**",
            "--forbid",
            "src/secrets/**",
        ],
    )
    invoke_main(pio, capsys, ["baseline", "implementation", *project_args])
    assert invoke_main(pio, capsys, ["audit", "implementation", *project_args])[
        "passed"
    ]
    assert invoke_main(
        pio, capsys, ["validate", *project_args, "--stage", "structure"]
    )["passed"]
    invoke_main(pio, capsys, ["block", *project_args, "--reason", "Temporary"])
    invoke_main(pio, capsys, ["unblock", *project_args, "--note", "Resolved"])

    failed = invoke_main(
        pio,
        capsys,
        ["transition", "complete", *project_args, "--evidence", "too early"],
        expected_code=2,
    )
    assert "Invalid transition" in failed["error"]
    assert (
        invoke_main(
            pio,
            capsys,
            ["validate", *project_args, "--stage", "ready"],
            expected_code=1,
        )["passed"]
        is False
    )
