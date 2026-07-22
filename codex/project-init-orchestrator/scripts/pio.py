#!/usr/bin/env python3
"""Deterministic execution layer for Project Init Orchestrator."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


VERSION = "0.2.0"
STATE_DIR_NAME = ".project-init-orchestrator"
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "assets" / "templates"
TODO_MARKER = "<!-- TODO:"

PHASE_TRANSITIONS = {
    "initialized": {"clarify"},
    "clarify": {"spec"},
    "spec": {"clarify", "plan"},
    "plan": {"spec", "execute"},
    "execute": {"plan", "verify"},
    "verify": {"execute", "audit"},
    "audit": {"execute", "complete"},
    "complete": set(),
}
EVIDENCE_PHASES = {"verify", "audit", "complete"}
NEXT_STEPS = {
    "initialized": "Inspect the repository and clarify requirements.",
    "clarify": "Resolve open product questions and obtain design approval.",
    "spec": "Complete and review the project spec.",
    "plan": "Create bounded tasks and role policies.",
    "execute": "Execute the next bounded task and record evidence.",
    "verify": "Run verification and resolve any failures.",
    "audit": "Audit requirements, artifacts, and role boundaries.",
    "complete": "No next step; completion evidence has been recorded.",
}
DEFAULT_FORBIDDEN = [
    ".git/**",
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "**/*.key",
    "**/*.pem",
    "secrets/**",
    "**/secrets/**",
]


class OrchestratorError(RuntimeError):
    """Raised when a workflow operation would violate the contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def local_today() -> str:
    return datetime.now().astimezone().date().isoformat()


def resolve_project(project: str | Path) -> Path:
    path = Path(project).expanduser().resolve()
    if not path.is_dir():
        raise OrchestratorError(f"Project directory does not exist: {path}")
    return path


def state_dir(project: Path) -> Path:
    return project / STATE_DIR_NAME


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OrchestratorError(f"Missing orchestrator state: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OrchestratorError(f"Invalid JSON in {path}: {exc}") from exc


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    _write_text_atomic(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _append_event(project: Path, event: dict[str, Any]) -> dict[str, Any]:
    event = {"timestamp": utc_now(), **event}
    path = state_dir(project) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def _load_events(project: Path) -> list[dict[str, Any]]:
    path = state_dir(project) / "events.jsonl"
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise OrchestratorError(
                f"Invalid event JSON at {path}:{line_number}: {exc}"
            ) from exc
    return events


def _slug_role(role: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", role.strip().lower()).strip("-")
    if not slug:
        raise OrchestratorError(f"Invalid role name: {role!r}")
    return slug


def _normalize_patterns(patterns: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    for raw in patterns:
        pattern = raw.strip().replace("\\", "/")
        while pattern.startswith("./"):
            pattern = pattern[2:]
        if not pattern or pattern.startswith("/") or ".." in Path(pattern).parts:
            raise OrchestratorError(f"Unsafe path pattern: {raw!r}")
        if pattern not in normalized:
            normalized.append(pattern)
    return normalized


def _render(template_name: str, values: dict[str, str]) -> str:
    template_path = TEMPLATE_DIR / template_name
    if not template_path.is_file():
        raise OrchestratorError(f"Missing bundled template: {template_path}")
    rendered = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    unresolved = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", rendered)))
    if unresolved:
        raise OrchestratorError(
            f"Unresolved template values in {template_name}: {', '.join(unresolved)}"
        )
    return rendered


def _create_if_missing(
    path: Path, content: str, result: dict[str, list[str]], project: Path
) -> None:
    relative = path.relative_to(project).as_posix()
    if path.exists():
        result["preserved"].append(relative)
        return
    _write_text_atomic(path, content)
    result["created"].append(relative)


def inspect_project(project: str | Path) -> dict[str, Any]:
    root = resolve_project(project)
    stack_checks = [
        ("node", ["package.json"]),
        ("python", ["pyproject.toml", "requirements.txt", "setup.py"]),
        ("go", ["go.mod"]),
        ("rust", ["Cargo.toml"]),
        ("java", ["pom.xml", "build.gradle", "build.gradle.kts"]),
    ]
    stacks = [
        name
        for name, manifests in stack_checks
        if any((root / manifest).is_file() for manifest in manifests)
    ]
    commands: list[str] = []
    package_path = root / "package.json"
    if package_path.is_file():
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
            scripts = package.get("scripts", {})
            for script, command in [
                ("test", "npm test"),
                ("lint", "npm run lint"),
                ("build", "npm run build"),
            ]:
                if script in scripts:
                    commands.append(command)
        except json.JSONDecodeError:
            commands.append("npm test")
    if "python" in stacks:
        commands.append("python -m pytest")
    if "go" in stacks:
        commands.append("go test ./...")
    if "rust" in stacks:
        commands.append("cargo test")

    git_root = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    controls = [
        path
        for path in [
            "AGENTS.md",
            "CLAUDE.md",
            "README.md",
            "docs/specs",
            "docs/tasks",
            "docs/worklogs",
        ]
        if (root / path).exists()
    ]
    return {
        "project": str(root),
        "git_repository": git_root.returncode == 0,
        "git_root": git_root.stdout.strip() if git_root.returncode == 0 else None,
        "stacks": stacks,
        "commands": commands,
        "existing_controls": controls,
    }


def initialize_project(
    project: str | Path,
    *,
    project_name: str,
    objective: str,
    roles: Iterable[str] = (),
) -> dict[str, Any]:
    root = resolve_project(project)
    if not project_name.strip() or not objective.strip():
        raise OrchestratorError("Project name and objective are required")
    orchestrator_dir = state_dir(root)
    config_path = orchestrator_dir / "config.json"
    state_path = orchestrator_dir / "state.json"
    result: dict[str, list[str]] = {"created": [], "preserved": []}

    if config_path.exists() or state_path.exists():
        if not config_path.is_file() or not state_path.is_file():
            raise OrchestratorError("Orchestrator state is partially initialized")
        config = _read_json(config_path)
        state = _read_json(state_path)
        if (
            config.get("project_name") != project_name
            or state.get("objective") != objective
        ):
            raise OrchestratorError(
                "Project is already initialized with a different name or objective"
            )
        for role in roles:
            slug = _slug_role(role)
            if slug not in config.get("roles", {}):
                add_role(root, slug)
                result["created"].append(f"role:{slug}")
        return result

    today = local_today()
    role_slugs = [_slug_role(role) for role in roles]
    role_slugs = list(dict.fromkeys(role_slugs))
    spec_path = f"docs/specs/{today}-project-spec.md"
    artifacts = {
        "agents": "AGENTS.md",
        "spec": spec_path,
        "tasks": "docs/tasks/project-tasks.md",
        "main_worklog": "docs/worklogs/main-worklog.md",
        "completion_audit": "docs/completion-audit.md",
    }
    config = {
        "schema_version": 1,
        "tool_version": VERSION,
        "project_name": project_name.strip(),
        "objective": objective.strip(),
        "created_at": utc_now(),
        "artifacts": artifacts,
        "global_forbidden_paths": DEFAULT_FORBIDDEN,
        "roles": {
            role: {"allowed_paths": [], "forbidden_paths": []} for role in role_slugs
        },
    }
    state = {
        "schema_version": 1,
        "tool_version": VERSION,
        "project_name": project_name.strip(),
        "objective": objective.strip(),
        "phase": "initialized",
        "status": "active",
        "iteration": 0,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "next_step": NEXT_STEPS["initialized"],
        "blockers": [],
        "evidence": [],
    }
    orchestrator_dir.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(config_path, config)
    _write_json_atomic(state_path, state)
    result["created"].extend(
        [f"{STATE_DIR_NAME}/config.json", f"{STATE_DIR_NAME}/state.json"]
    )

    role_table = "| Main Agent | Orchestration and integration | Project-wide |"
    if role_slugs:
        role_table += "\n" + "\n".join(
            f"| {role} | Bounded delegated work | No writes until policy is configured |"
            for role in role_slugs
        )
    common = {
        "PROJECT_NAME": project_name.strip(),
        "OBJECTIVE": objective.strip(),
        "DATE": today,
        "ROLES_TABLE": role_table,
    }
    _create_if_missing(root / "AGENTS.md", _render("AGENTS.md", common), result, root)
    _create_if_missing(root / spec_path, _render("SPEC.md", common), result, root)
    _create_if_missing(
        root / artifacts["tasks"], _render("TASKS.md", common), result, root
    )
    _create_if_missing(
        root / artifacts["main_worklog"], _render("WORKLOG.md", common), result, root
    )
    _create_if_missing(
        root / artifacts["completion_audit"],
        _render("COMPLETION_AUDIT.md", common),
        result,
        root,
    )
    for role in role_slugs:
        _create_role_artifacts(root, role, common, result)

    _append_event(
        root,
        {
            "type": "initialized",
            "actor": "main",
            "message": f"Initialized {project_name.strip()} with {len(role_slugs)} bounded roles.",
            "phase": "initialized",
        },
    )
    result["created"].append(f"{STATE_DIR_NAME}/events.jsonl")
    compact_context(root)
    result["created"].append(f"{STATE_DIR_NAME}/snapshot.md")
    return result


def _create_role_artifacts(
    project: Path,
    role: str,
    common: dict[str, str],
    result: dict[str, list[str]],
) -> None:
    values = {
        **common,
        "ROLE": role,
        "ALLOWED_PATHS": "- No write paths configured. Run `set-policy` before delegation.",
        "FORBIDDEN_PATHS": "- Global sensitive paths and every path outside the allow list.",
    }
    brief = project / "docs" / "agents" / "subagent-briefs" / f"{role}.md"
    worklog = project / "docs" / "worklogs" / "subagents" / f"{role}-worklog.md"
    _create_if_missing(brief, _render("SUBAGENT_BRIEF.md", values), result, project)
    _create_if_missing(worklog, _render("SUBAGENT_WORKLOG.md", values), result, project)


def add_role(project: str | Path, role: str) -> dict[str, Any]:
    root = resolve_project(project)
    slug = _slug_role(role)
    config_path = state_dir(root) / "config.json"
    config = _read_json(config_path)
    if slug in config.get("roles", {}):
        return {"role": slug, "created": [], "preserved": [f"role:{slug}"]}
    config.setdefault("roles", {})[slug] = {
        "allowed_paths": [],
        "forbidden_paths": [],
    }
    _write_json_atomic(config_path, config)
    result: dict[str, list[str]] = {"created": [], "preserved": []}
    common = {
        "PROJECT_NAME": config["project_name"],
        "OBJECTIVE": config["objective"],
        "DATE": local_today(),
        "ROLES_TABLE": "",
    }
    _create_role_artifacts(root, slug, common, result)
    _append_event(
        root,
        {
            "type": "role-added",
            "actor": "main",
            "message": f"Added bounded role {slug}; no write paths are allowed yet.",
            "phase": _read_json(state_dir(root) / "state.json")["phase"],
        },
    )
    compact_context(root)
    return {"role": slug, **result}


def set_role_policy(
    project: str | Path,
    role: str,
    *,
    allowed_paths: Iterable[str],
    forbidden_paths: Iterable[str] = (),
) -> dict[str, Any]:
    root = resolve_project(project)
    slug = _slug_role(role)
    config_path = state_dir(root) / "config.json"
    config = _read_json(config_path)
    if slug not in config.get("roles", {}):
        raise OrchestratorError(f"Unknown role: {slug}. Add it before setting policy.")
    policy = {
        "allowed_paths": _normalize_patterns(allowed_paths),
        "forbidden_paths": _normalize_patterns(forbidden_paths),
    }
    config["roles"][slug] = policy
    _write_json_atomic(config_path, config)
    _append_event(
        root,
        {
            "type": "policy-updated",
            "actor": "main",
            "message": f"Updated path policy for {slug}.",
            "role": slug,
            "policy": policy,
            "phase": _read_json(state_dir(root) / "state.json")["phase"],
        },
    )
    compact_context(root)
    return {"role": slug, **policy}


def transition_project(
    project: str | Path,
    phase: str,
    *,
    evidence: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    root = resolve_project(project)
    target = phase.strip().lower()
    state_path = state_dir(root) / "state.json"
    state = _read_json(state_path)
    current = state["phase"]
    if state.get("status") == "blocked":
        raise OrchestratorError("Project is blocked; unblock it before transitioning")
    if target not in PHASE_TRANSITIONS.get(current, set()):
        raise OrchestratorError(f"Invalid transition: {current} -> {target}")
    if target in EVIDENCE_PHASES and not (evidence and evidence.strip()):
        raise OrchestratorError(f"Transition to {target} requires evidence")

    if target == "execute" and current != "execute":
        state["iteration"] = int(state.get("iteration", 0)) + 1
    state["phase"] = target
    state["status"] = "complete" if target == "complete" else "active"
    state["updated_at"] = utc_now()
    state["next_step"] = NEXT_STEPS[target]
    if evidence:
        state.setdefault("evidence", []).append(
            {"phase": target, "value": evidence.strip(), "timestamp": utc_now()}
        )
    _write_json_atomic(state_path, state)
    _append_event(
        root,
        {
            "type": "transition",
            "actor": "main",
            "message": note or f"Transitioned from {current} to {target}.",
            "from": current,
            "phase": target,
            "evidence": evidence,
        },
    )
    compact_context(root)
    return state


def block_project(project: str | Path, reason: str) -> dict[str, Any]:
    root = resolve_project(project)
    if not reason.strip():
        raise OrchestratorError("A blocker reason is required")
    path = state_dir(root) / "state.json"
    state = _read_json(path)
    blocker = {"reason": reason.strip(), "timestamp": utc_now(), "resolved": False}
    state.setdefault("blockers", []).append(blocker)
    state["status"] = "blocked"
    state["updated_at"] = utc_now()
    _write_json_atomic(path, state)
    _append_event(
        root,
        {
            "type": "blocker",
            "actor": "main",
            "message": reason.strip(),
            "phase": state["phase"],
        },
    )
    compact_context(root)
    return state


def unblock_project(project: str | Path, note: str) -> dict[str, Any]:
    root = resolve_project(project)
    if not note.strip():
        raise OrchestratorError("An unblock note is required")
    path = state_dir(root) / "state.json"
    state = _read_json(path)
    for blocker in state.get("blockers", []):
        if not blocker.get("resolved"):
            blocker["resolved"] = True
            blocker["resolution"] = note.strip()
            blocker["resolved_at"] = utc_now()
    state["status"] = "active"
    state["updated_at"] = utc_now()
    _write_json_atomic(path, state)
    _append_event(
        root,
        {
            "type": "unblocked",
            "actor": "main",
            "message": note.strip(),
            "phase": state["phase"],
        },
    )
    compact_context(root)
    return state


def log_event(
    project: str | Path,
    *,
    event_type: str,
    actor: str,
    message: str,
) -> dict[str, Any]:
    root = resolve_project(project)
    allowed_types = {"progress", "decision", "blocker", "verification", "handoff"}
    if event_type not in allowed_types:
        raise OrchestratorError(
            f"Unknown event type {event_type!r}; choose from {sorted(allowed_types)}"
        )
    if not actor.strip() or not message.strip():
        raise OrchestratorError("Actor and message are required")
    state = _read_json(state_dir(root) / "state.json")
    event = _append_event(
        root,
        {
            "type": event_type,
            "actor": actor.strip(),
            "message": message.strip(),
            "phase": state["phase"],
        },
    )
    compact_context(root)
    return event


def compact_context(project: str | Path, recent_limit: int = 10) -> dict[str, Any]:
    root = resolve_project(project)
    if recent_limit < 1:
        raise OrchestratorError("recent_limit must be at least 1")
    config = _read_json(state_dir(root) / "config.json")
    state = _read_json(state_dir(root) / "state.json")
    events = _load_events(root)
    recent = events[-recent_limit:]
    unresolved = [
        item for item in state.get("blockers", []) if not item.get("resolved")
    ]
    lines = [
        "# Project Context Snapshot",
        "",
        f"- Generated: {utc_now()}",
        f"- Project: {state['project_name']}",
        f"- Objective: {state['objective']}",
        f"- Phase: {state['phase']}",
        f"- Status: {state['status']}",
        f"- Iteration: {state['iteration']}",
        f"- Next step: {state['next_step']}",
        f"- Total events: {len(events)}",
        f"- Unresolved blockers: {len(unresolved)}",
        "",
        "## Role Policies",
        "",
    ]
    roles = config.get("roles", {})
    if roles:
        for role, policy in sorted(roles.items()):
            allowed = ", ".join(policy.get("allowed_paths", [])) or "none"
            forbidden = (
                ", ".join(policy.get("forbidden_paths", [])) or "global policy only"
            )
            lines.append(f"- {role}: allow [{allowed}]; forbid [{forbidden}]")
    else:
        lines.append("- No delegated roles have been created.")
    lines.extend(["", "## Evidence", ""])
    if state.get("evidence"):
        for evidence in state["evidence"][-10:]:
            lines.append(f"- {evidence['phase']}: {evidence['value']}")
    else:
        lines.append("- No verification evidence recorded yet.")
    lines.extend(["", "## Recent Events", ""])
    if recent:
        for event in recent:
            message = str(event.get("message", "")).replace("\n", " ")
            lines.append(
                f"- {event.get('timestamp')} [{event.get('type')}] "
                f"{event.get('actor')}: {message}"
            )
    else:
        lines.append("- No events recorded.")
    _write_text_atomic(state_dir(root) / "snapshot.md", "\n".join(lines) + "\n")
    return {"total_events": len(events), "recent_events": len(recent)}


def _visible_files(
    project: Path, include_ignored_patterns: Iterable[str] = ()
) -> dict[str, str]:
    git_files = subprocess.run(
        ["git", "-C", str(project), "ls-files", "-co", "--exclude-standard", "-z"],
        capture_output=True,
        check=False,
    )
    candidates: list[Path] = []
    if git_files.returncode == 0:
        for raw in git_files.stdout.split(b"\0"):
            if raw:
                candidates.append(project / os.fsdecode(raw))
        ignored_files = subprocess.run(
            [
                "git",
                "-C",
                str(project),
                "ls-files",
                "--others",
                "--ignored",
                "--exclude-standard",
                "-z",
            ],
            capture_output=True,
            check=False,
        )
        if ignored_files.returncode == 0:
            for raw in ignored_files.stdout.split(b"\0"):
                if not raw:
                    continue
                relative = os.fsdecode(raw).replace("\\", "/")
                if _matches(relative, include_ignored_patterns):
                    candidates.append(project / relative)
    else:
        candidates = [
            path for path in project.rglob("*") if path.is_file() or path.is_symlink()
        ]

    hashes: dict[str, str] = {}
    for path in dict.fromkeys(candidates):
        try:
            relative = path.relative_to(project).as_posix()
        except ValueError:
            continue
        if relative == STATE_DIR_NAME or relative.startswith(f"{STATE_DIR_NAME}/"):
            continue
        if relative == ".git" or relative.startswith(".git/"):
            continue
        digest = hashlib.sha256()
        try:
            if path.is_symlink():
                digest.update(b"symlink\0")
                digest.update(os.fsencode(os.readlink(path)))
            elif path.is_file():
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
            else:
                continue
        except OSError as exc:
            raise OrchestratorError(f"Cannot hash {path}: {exc}") from exc
        hashes[relative] = digest.hexdigest()
    return dict(sorted(hashes.items()))


def capture_baseline(project: str | Path, role: str) -> dict[str, Any]:
    root = resolve_project(project)
    slug = _slug_role(role)
    config = _read_json(state_dir(root) / "config.json")
    if slug not in config.get("roles", {}):
        raise OrchestratorError(f"Unknown role: {slug}")
    effective_forbidden = [
        *config.get("global_forbidden_paths", []),
        *config["roles"][slug].get("forbidden_paths", []),
    ]
    baseline = {
        "schema_version": 1,
        "role": slug,
        "captured_at": utc_now(),
        "policy": config["roles"][slug],
        "global_forbidden_paths": config.get("global_forbidden_paths", []),
        "files": _visible_files(root, effective_forbidden),
    }
    path = state_dir(root) / "baselines" / f"{slug}.json"
    _write_json_atomic(path, baseline)
    _append_event(
        root,
        {
            "type": "baseline",
            "actor": "main",
            "message": f"Captured {len(baseline['files'])} files for role {slug}.",
            "role": slug,
            "phase": _read_json(state_dir(root) / "state.json")["phase"],
        },
    )
    compact_context(root)
    return {"role": slug, "file_count": len(baseline["files"]), "path": str(path)}


def _matches(path: str, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if pattern == "**" or fnmatch.fnmatchcase(path, pattern):
            return True
        if pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]):
            return True
        if pattern.endswith("/**") and path == pattern[:-3].rstrip("/"):
            return True
    return False


def audit_role(project: str | Path, role: str) -> dict[str, Any]:
    root = resolve_project(project)
    slug = _slug_role(role)
    config = _read_json(state_dir(root) / "config.json")
    if slug not in config.get("roles", {}):
        raise OrchestratorError(f"Unknown role: {slug}")
    baseline_path = state_dir(root) / "baselines" / f"{slug}.json"
    baseline = _read_json(baseline_path)
    if baseline.get("policy") != config["roles"][slug] or baseline.get(
        "global_forbidden_paths"
    ) != config.get("global_forbidden_paths", []):
        raise OrchestratorError(
            f"Path policy for {slug} changed after baseline; capture a new baseline"
        )
    before = baseline.get("files", {})
    policy = config["roles"][slug]
    forbidden_patterns = [
        *config.get("global_forbidden_paths", []),
        *policy.get("forbidden_paths", []),
    ]
    after = _visible_files(root, forbidden_patterns)
    changed = sorted(
        path for path in set(before) | set(after) if before.get(path) != after.get(path)
    )
    allowed_patterns = policy.get("allowed_paths", [])
    allowed: list[str] = []
    violations: list[dict[str, str]] = []
    for path in changed:
        if _matches(path, forbidden_patterns):
            violations.append({"path": path, "reason": "forbidden"})
        elif not _matches(path, allowed_patterns):
            violations.append({"path": path, "reason": "outside-scope"})
        else:
            allowed.append(path)
    report = {
        "schema_version": 1,
        "role": slug,
        "audited_at": utc_now(),
        "passed": not violations,
        "changed": changed,
        "allowed": allowed,
        "violations": violations,
    }
    report_path = state_dir(root) / "audits" / f"{utc_stamp()}-{slug}.json"
    _write_json_atomic(report_path, report)
    _append_event(
        root,
        {
            "type": "boundary-audit",
            "actor": "main",
            "message": (
                f"Boundary audit for {slug}: {len(allowed)} allowed, "
                f"{len(violations)} violations."
            ),
            "role": slug,
            "passed": report["passed"],
            "report": str(report_path.relative_to(root)),
            "phase": _read_json(state_dir(root) / "state.json")["phase"],
        },
    )
    compact_context(root)
    return report


def validate_project(project: str | Path, stage: str = "structure") -> dict[str, Any]:
    root = resolve_project(project)
    if stage not in {"structure", "ready", "complete"}:
        raise OrchestratorError(f"Unknown validation stage: {stage}")
    errors: list[str] = []
    warnings: list[str] = []
    config_path = state_dir(root) / "config.json"
    state_path = state_dir(root) / "state.json"
    try:
        config = _read_json(config_path)
        state = _read_json(state_path)
    except OrchestratorError as exc:
        return {"stage": stage, "passed": False, "errors": [str(exc)], "warnings": []}

    required = [
        config_path,
        state_path,
        state_dir(root) / "events.jsonl",
        state_dir(root) / "snapshot.md",
        *[root / path for path in config.get("artifacts", {}).values()],
    ]
    for role in config.get("roles", {}):
        required.extend(
            [
                root / "docs" / "agents" / "subagent-briefs" / f"{role}.md",
                root / "docs" / "worklogs" / "subagents" / f"{role}-worklog.md",
            ]
        )
    for path in required:
        if not path.is_file():
            errors.append(f"Missing required file: {path.relative_to(root)}")
    if config.get("schema_version") != 1 or state.get("schema_version") != 1:
        errors.append("Unsupported or missing schema version")
    if state.get("phase") not in PHASE_TRANSITIONS:
        errors.append(f"Unknown state phase: {state.get('phase')}")

    if stage in {"ready", "complete"} and not errors:
        documents = [
            root / config["artifacts"]["agents"],
            root / config["artifacts"]["spec"],
            root / config["artifacts"]["tasks"],
            *[
                root / "docs" / "agents" / "subagent-briefs" / f"{role}.md"
                for role in config.get("roles", {})
            ],
        ]
        for path in documents:
            if TODO_MARKER in path.read_text(encoding="utf-8"):
                errors.append(f"TODO placeholders remain in {path.relative_to(root)}")
        spec_text = (root / config["artifacts"]["spec"]).read_text(encoding="utf-8")
        if "- [ ]" not in spec_text and "- [x]" not in spec_text.lower():
            errors.append("Project spec has no acceptance criteria checklist")
        for role, policy in config.get("roles", {}).items():
            if not policy.get("allowed_paths"):
                warnings.append(
                    f"Role {role} has no write paths and cannot modify files"
                )

    if stage == "complete" and not errors:
        if state.get("phase") != "complete" or state.get("status") != "complete":
            errors.append("Project state is not complete")
        audit_path = root / config["artifacts"]["completion_audit"]
        audit_text = audit_path.read_text(encoding="utf-8")
        if "Unverified" in audit_text or "- [ ]" in audit_text:
            errors.append("Completion audit still contains unverified items")

    return {
        "stage": stage,
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def status_project(project: str | Path) -> dict[str, Any]:
    root = resolve_project(project)
    return _read_json(state_dir(root) / "state.json")


def _print_json(value: Any, *, stream=None) -> None:
    output = sys.stdout if stream is None else stream
    print(json.dumps(value, indent=2, ensure_ascii=False), file=output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pio",
        description="Project Init Orchestrator executable workflow for Codex.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)

    def project_argument(command: argparse.ArgumentParser) -> None:
        command.add_argument("--project", default=".", help="Target project directory")

    inspect_command = commands.add_parser(
        "inspect", help="Inspect a repository without writing"
    )
    project_argument(inspect_command)

    init_command = commands.add_parser(
        "init", help="Initialize project control artifacts"
    )
    project_argument(init_command)
    init_command.add_argument("--name", required=True, help="Project name")
    init_command.add_argument(
        "--objective", required=True, help="Persistent project objective"
    )
    init_command.add_argument(
        "--role", action="append", default=[], help="Bounded role name"
    )

    for name, help_text in [
        ("status", "Show persistent goal and loop state"),
        ("resume", "Show state and compact context for resuming work"),
    ]:
        command = commands.add_parser(name, help=help_text)
        project_argument(command)

    transition_command = commands.add_parser(
        "transition", help="Move to an allowed loop phase"
    )
    project_argument(transition_command)
    transition_command.add_argument("phase", choices=sorted(PHASE_TRANSITIONS))
    transition_command.add_argument("--evidence")
    transition_command.add_argument("--note")

    block_command = commands.add_parser(
        "block", help="Record a blocker and pause transitions"
    )
    project_argument(block_command)
    block_command.add_argument("--reason", required=True)

    unblock_command = commands.add_parser(
        "unblock", help="Resolve blockers and resume transitions"
    )
    project_argument(unblock_command)
    unblock_command.add_argument("--note", required=True)

    log_command = commands.add_parser("log", help="Append a structured work event")
    project_argument(log_command)
    log_command.add_argument(
        "--type",
        required=True,
        choices=["progress", "decision", "blocker", "verification", "handoff"],
    )
    log_command.add_argument("--actor", required=True)
    log_command.add_argument("--message", required=True)

    compact_command = commands.add_parser(
        "compact", help="Regenerate a compact context snapshot"
    )
    project_argument(compact_command)
    compact_command.add_argument("--recent", type=int, default=10)

    role_command = commands.add_parser(
        "add-role", help="Add a bounded role and its documents"
    )
    project_argument(role_command)
    role_command.add_argument("role")

    policy_command = commands.add_parser("set-policy", help="Set role path permissions")
    project_argument(policy_command)
    policy_command.add_argument("role")
    policy_command.add_argument("--allow", action="append", default=[])
    policy_command.add_argument("--forbid", action="append", default=[])

    baseline_command = commands.add_parser(
        "baseline", help="Capture files before delegated work"
    )
    project_argument(baseline_command)
    baseline_command.add_argument("role")

    audit_command = commands.add_parser(
        "audit", help="Audit role changes against path policy"
    )
    project_argument(audit_command)
    audit_command.add_argument("role")

    validate_command = commands.add_parser(
        "validate", help="Validate workflow evidence"
    )
    project_argument(validate_command)
    validate_command.add_argument(
        "--stage", choices=["structure", "ready", "complete"], default="structure"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            result = inspect_project(args.project)
        elif args.command == "init":
            result = initialize_project(
                args.project,
                project_name=args.name,
                objective=args.objective,
                roles=args.role,
            )
        elif args.command in {"status", "resume"}:
            result = status_project(args.project)
            if args.command == "resume":
                result = {
                    "state": result,
                    "snapshot": str(
                        state_dir(resolve_project(args.project)) / "snapshot.md"
                    ),
                }
        elif args.command == "transition":
            result = transition_project(
                args.project, args.phase, evidence=args.evidence, note=args.note
            )
        elif args.command == "block":
            result = block_project(args.project, args.reason)
        elif args.command == "unblock":
            result = unblock_project(args.project, args.note)
        elif args.command == "log":
            result = log_event(
                args.project,
                event_type=args.type,
                actor=args.actor,
                message=args.message,
            )
        elif args.command == "compact":
            result = compact_context(args.project, args.recent)
        elif args.command == "add-role":
            result = add_role(args.project, args.role)
        elif args.command == "set-policy":
            result = set_role_policy(
                args.project,
                args.role,
                allowed_paths=args.allow,
                forbidden_paths=args.forbid,
            )
        elif args.command == "baseline":
            result = capture_baseline(args.project, args.role)
        elif args.command == "audit":
            result = audit_role(args.project, args.role)
        elif args.command == "validate":
            result = validate_project(args.project, args.stage)
        else:
            parser.error(f"Unhandled command: {args.command}")
            return 2
    except OrchestratorError as exc:
        _print_json({"error": str(exc)}, stream=sys.stderr)
        return 2

    _print_json(result)
    if args.command in {"validate", "audit"} and not result.get("passed", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
