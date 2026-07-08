# Project Init Orchestrator

> A disciplined startup workflow for Codex, Claude Code, and multi-agent coding projects.

`Project Init Orchestrator` helps an AI coding agent start a project the right way: define the goal, ask the important questions, write `AGENTS.md`, create a spec, assign bounded subagents, maintain work logs, and keep moving through a documented loop until the work is complete.

It is built for people who do not want an agent to jump straight into coding before the project has clear scope, boundaries, acceptance criteria, and collaboration rules.

## Why This Exists

Agentic coding breaks down when the first few minutes are messy:

- The agent starts implementation before requirements are clear.
- Subagents overlap, duplicate work, or edit outside their scope.
- There is no durable `AGENTS.md`.
- The spec is missing, vague, or never reviewed.
- Progress lives only in chat history.
- The user has to keep manually pushing the agent after every step.

This project turns project startup into a repeatable operating system.

## What It Installs

| Platform | Installed Artifact | Purpose |
| --- | --- | --- |
| Codex | `project-init-orchestrator` Skill | Native Codex workflow entrypoint |
| Claude Code | `/project-init-orchestrator` command | Native Claude Code command |
| Shared | Project templates | `AGENTS.md`, spec, tasks, logs, subagent briefs, audit |

## Core Workflow

When triggered, the main agent must:

1. Establish or emulate goal mode.
2. Inspect the current repository.
3. Use `superpowers:brainstorming` when available.
4. Ask focused questions before implementation.
5. Write or update `AGENTS.md`.
6. Write a project spec.
7. Create a task plan.
8. Define bounded subagent briefs.
9. Maintain main-agent and subagent work logs.
10. Run a loop: clarify, design, document, plan, execute, verify, review, continue.
11. Complete only after a requirement-by-requirement audit has evidence.

The workflow is intentionally strict. It favors a clean start over fast but fragile implementation.

## Generated Project Files

In a target project, the workflow creates or updates:

```text
AGENTS.md
docs/specs/<YYYY-MM-DD>-project-spec.md
docs/tasks/project-tasks.md
docs/worklogs/main-worklog.md
docs/worklogs/subagents/<role>-worklog.md
docs/agents/subagent-briefs/<role>.md
docs/completion-audit.md
```

## Install

Clone this repository, then run:

```bash
./install.sh
```

The installer copies:

- Codex Skill to `${CODEX_HOME:-$HOME/.codex}/skills/project-init-orchestrator`
- Claude Code command to `$HOME/.claude/commands/project-init-orchestrator.md`
- Shared templates to `$HOME/.project-init-orchestrator/templates`

Preview the installation without writing files:

```bash
DRY_RUN=1 ./install.sh
```

## Manual Install

Install the Codex Skill:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex/project-init-orchestrator "${CODEX_HOME:-$HOME/.codex}/skills/project-init-orchestrator"
```

Install the Claude Code command:

```bash
mkdir -p "$HOME/.claude/commands"
cp claude-code/commands/project-init-orchestrator.md "$HOME/.claude/commands/project-init-orchestrator.md"
```

Install shared templates:

```bash
mkdir -p "$HOME/.project-init-orchestrator"
cp -R templates "$HOME/.project-init-orchestrator/templates"
```

## Use In Codex

Start a new project conversation and say:

```text
Use $project-init-orchestrator to initialize this project with goals, specs, AGENTS.md, bounded subagents, and work logs.
```

## Use In Claude Code

Run:

```text
/project-init-orchestrator initialize this project
```

## Templates

The `templates/` directory contains:

- `AGENTS.md`: project constitution for all agents
- `SPEC.md`: project requirements, architecture, risks, and acceptance criteria
- `TASKS.md`: task ownership, status, dependencies, and evidence
- `WORKLOG.md`: persistent goal state, loop state, decisions, blockers, and progress
- `SUBAGENT_BRIEF.md`: scoped assignment for each subagent
- `COMPLETION_AUDIT.md`: final evidence review before completion

## Platform Fallbacks

Codex and Claude Code do not always expose identical runtime tools. The workflow keeps the same discipline with fallbacks:

- No native goal mode: write persistent goal state in `docs/worklogs/main-worklog.md`.
- No native subagents: simulate bounded roles with briefs and logs.
- No brainstorming skill: perform manual clarification and design gating.
- No tests yet: record available verification and create test setup tasks when needed.

## Validate

Run:

```bash
python3 scripts/validate_repository.py
```

Validate the Codex Skill with the bundled skill validator in a Python environment that has PyYAML:

```bash
python3 /Users/Zhuanz1/.codex/skills/.system/skill-creator/scripts/quick_validate.py codex/project-init-orchestrator
```

## Project Philosophy

This workflow treats project initialization as part of engineering quality.

Good agents should not only write code. They should preserve intent, respect boundaries, record decisions, coordinate collaborators, and prove completion with evidence.

`Project Init Orchestrator` gives them the structure to do that from the first message.
