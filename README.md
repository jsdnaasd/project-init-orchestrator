# Project Init Orchestrator

Project Init Orchestrator is a reusable workflow package for starting coding projects with disciplined agent coordination before implementation.

It installs:

- A Codex Skill: `project-init-orchestrator`
- A Claude Code command: `/project-init-orchestrator`
- Shared project templates for `AGENTS.md`, specs, tasks, work logs, subagent briefs, and completion audits

The workflow is strict by design. It makes the main agent establish a goal, ask project questions, write control documents, define subagent boundaries, and then continue through a documented loop until the work is complete or genuinely blocked.

## What It Creates In A Target Project

When triggered in a project, the workflow creates or updates:

- `AGENTS.md`
- `docs/specs/<YYYY-MM-DD>-project-spec.md`
- `docs/tasks/project-tasks.md`
- `docs/worklogs/main-worklog.md`
- `docs/worklogs/subagents/<role>-worklog.md`
- `docs/agents/subagent-briefs/<role>.md`
- `docs/completion-audit.md` or an equivalent final audit file

## Core Behavior

The main agent must:

1. Create or confirm goal mode.
2. Inspect the current project.
3. Use `superpowers:brainstorming` when available.
4. Ask focused project questions before implementation.
5. Write `AGENTS.md`.
6. Write a project spec.
7. Create tasks, work logs, and subagent briefs.
8. Keep subagents bounded by their briefs.
9. Run a loop: clarify, design, document, plan, execute, verify, review, continue.
10. Complete only after a requirement-by-requirement audit has evidence.

If a platform has no native goal mode, the workflow emulates goal mode in `docs/worklogs/main-worklog.md`. If native subagents are unavailable, the main agent simulates subagent roles with separate briefs and work logs.

## Install

Clone the repository, then run:

```bash
./install.sh
```

The installer copies:

- Codex Skill to `${CODEX_HOME:-$HOME/.codex}/skills/project-init-orchestrator`
- Claude Code command to `$HOME/.claude/commands/project-init-orchestrator.md`
- Shared templates to `$HOME/.project-init-orchestrator/templates`

To preview without writing files:

```bash
DRY_RUN=1 ./install.sh
```

## Manual Install

Codex:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex/project-init-orchestrator "${CODEX_HOME:-$HOME/.codex}/skills/project-init-orchestrator"
```

Claude Code:

```bash
mkdir -p "$HOME/.claude/commands"
cp claude-code/commands/project-init-orchestrator.md "$HOME/.claude/commands/project-init-orchestrator.md"
```

Shared templates:

```bash
mkdir -p "$HOME/.project-init-orchestrator"
cp -R templates "$HOME/.project-init-orchestrator/templates"
```

## Trigger In Codex

Use a prompt like:

```text
Use $project-init-orchestrator to initialize this project with goals, specs, AGENTS.md, bounded subagents, and work logs.
```

## Trigger In Claude Code

Use:

```text
/project-init-orchestrator initialize this project
```

## Template Files

The `templates/` directory contains:

- `AGENTS.md`: project constitution for all agents
- `SPEC.md`: project spec structure
- `TASKS.md`: task tracking with owner, status, dependency, and evidence fields
- `WORKLOG.md`: persistent goal and loop state plus progress entries
- `SUBAGENT_BRIEF.md`: bounded subagent assignment
- `COMPLETION_AUDIT.md`: final evidence review

## Platform Limits

Codex and Claude Code do not always expose the same tools. This package preserves the workflow contract even when a feature is missing:

- No native goal mode: write persistent goal state in the main work log.
- No native subagents: simulate role-bounded passes with separate briefs and logs.
- No brainstorming skill: perform manual clarification and design gating.
- No tests yet: record available verification and add test setup tasks when required.

## Validate This Repository

Run:

```bash
python3 scripts/validate_repository.py
```

To validate the Codex Skill with the bundled skill validator, run it in a Python environment that has PyYAML installed:

```bash
python3 /Users/Zhuanz1/.codex/skills/.system/skill-creator/scripts/quick_validate.py codex/project-init-orchestrator
```
