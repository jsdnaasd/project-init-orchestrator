---
name: project-init-orchestrator
description: Initialize and govern new or restarted Codex projects with an executable goal/loop workflow, AGENTS.md, reviewed specs, persistent state, bounded subagent briefs, path policies, work logs, context snapshots, validation gates, and completion evidence. Use when the user asks Codex to set up a project before implementation, clarify requirements, create project control documents, coordinate subagents, prevent scope violations, resume a long-running project, or audit whether work is actually complete.
---

# Project Init Orchestrator

Initialize the project with the bundled CLI, then use Codex for requirement reasoning and bounded execution. Treat CLI failures as workflow failures; do not replace deterministic checks with prose.

## Hard Rules

1. Do not implement before the objective, approved design, spec, task plan, and role boundaries exist.
2. Create a native main goal when the host exposes goal tools. Always mirror durable state through the CLI.
3. Give every delegated role a logical goal, brief, path policy, work log, baseline, and post-work audit.
4. Use `superpowers:brainstorming` when installed. Otherwise use [references/workflow.md](references/workflow.md) and record the fallback.
5. Never treat a simulated role pass as native parallel subagent execution.
6. Never claim completion while `validate --stage complete` fails.

## Locate The CLI

Set the absolute path to this Skill's script:

```bash
PIO="<this-skill-directory>/scripts/pio.py"
python3 "$PIO" --version
```

Read [references/cli.md](references/cli.md) when exact command syntax is needed.

## Initialize

Run inspection before asking repository-specific questions:

```bash
python3 "$PIO" inspect --project .
```

Create the native goal when available. Then initialize persistent state with the user's actual objective. Do not weaken the objective to match partial progress.

```bash
python3 "$PIO" init --project . --name "<project name>" --objective "<objective>"
python3 "$PIO" validate --project . --stage structure
python3 "$PIO" transition clarify --project .
```

Initialization preserves existing files. Inspect preserved artifacts and merge requirements deliberately instead of overwriting them.

## Clarify And Approve Design

Read [references/workflow.md](references/workflow.md). Ask one focused question at a time until purpose, users, workflows, scope, constraints, integrations, risk, success measures, and acceptance evidence are clear.

Present the proposed design and obtain approval. Fill all TODO markers in `AGENTS.md`, the spec, and task plan. Record decisions:

```bash
python3 "$PIO" log --project . --type decision --actor main --message "<decision>"
python3 "$PIO" transition spec --project .
python3 "$PIO" transition plan --project .
```

Ask again only when a missing decision changes scope, product direction, risk, credentials, external access, or acceptance criteria.

## Create Bounded Roles

Create only roles justified by independent work or review. For every role:

```bash
python3 "$PIO" add-role <role> --project .
python3 "$PIO" set-policy <role> --project . --allow '<path/**>' --forbid '<sensitive/**>'
python3 "$PIO" baseline <role> --project .
```

Complete the generated brief before dispatch. Give the role the current `AGENTS.md`, spec, task, `.project-init-orchestrator/snapshot.md`, and relevant logs.

After delegated work returns, run:

```bash
python3 "$PIO" audit <role> --project .
```

Investigate every forbidden or out-of-scope path before integrating output.

## Run The Loop

Before implementation, require:

```bash
python3 "$PIO" validate --project . --stage ready
python3 "$PIO" transition execute --project .
```

Repeat until complete:

1. Read goal state, spec, tasks, snapshot, and work logs.
2. Select the highest-value dependency-ready task.
3. Execute directly or dispatch a bounded role.
4. Log progress, decisions, blockers, verification, and handoffs.
5. Run tests and role boundary audits.
6. Transition to `verify` with concrete evidence.
7. Return to `execute` on failure or advance to `audit` on success.
8. Continue without asking the user to drive routine steps.

Use `block` only for a genuine blocker and `unblock` after resolution. Use `compact` after long phases; it preserves the full event log while regenerating a concise snapshot.

## Complete

Audit every explicit requirement against direct evidence. Complete `docs/completion-audit.md`, then run:

```bash
python3 "$PIO" transition audit --project . --evidence "<verification summary>"
python3 "$PIO" transition complete --project . --evidence "<audit summary>"
python3 "$PIO" validate --project . --stage complete
```

If validation fails, continue the loop. Report native capability limitations honestly in the final response.
