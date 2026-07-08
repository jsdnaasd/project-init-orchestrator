---
name: project-init-orchestrator
description: Disciplined project initialization workflow for new or restarted coding projects. Use when the user wants Codex to set up a project before implementation, create AGENTS.md, write specs, enable goal/loop execution, coordinate bounded subagents, maintain work logs, or establish a reusable multi-agent project workflow.
---

# Project Init Orchestrator

Use this skill to initialize a project before implementation. The goal is to make the main agent create durable project control documents, ask the right questions, define agent boundaries, and then run a documented loop until the project is complete or genuinely blocked.

## Hard Rules

1. Do not start implementation before the project goal, project spec, task plan, and agent boundaries are documented.
2. Create or confirm a persistent goal at the start. If native goal mode exists, use it. If it does not exist, emulate goal mode in `docs/worklogs/main-worklog.md`.
3. Use loop execution after the initial questions are answered: clarify, design, document, plan, execute, verify, review, and continue.
4. Use `superpowers:brainstorming` when it is available. Follow its gate: no implementation before design approval.
5. Do not dispatch or simulate subagents until each subagent has a written brief with scope, allowed files, forbidden files, expected output, verification, and work log location.
6. Require every agent, including the main agent, to write progress, decisions, blockers, and handoffs to work logs.
7. Treat `AGENTS.md`, the project spec, and the assigned subagent brief as binding instructions for subagent scope.
8. Before declaring completion, run a requirement-by-requirement audit against the goal, spec, task list, tests, and produced artifacts.

## Initialization Sequence

Run these steps in order.

### 1. Inspect Context

Read the current repository state before asking detailed questions:

- Current working directory and Git status.
- Existing `AGENTS.md`, `CLAUDE.md`, specs, README files, package manifests, test configs, and source layout.
- Recent commits when available.
- Existing project conventions that should override the default templates.

If the project is empty, say so and continue with the default artifact paths.

### 2. Establish Goal Mode

Create or confirm the project goal before writing implementation code.

If a native goal tool is available, create a goal with the user's actual objective and keep it active until completion. If no native goal tool exists, write the goal state into `docs/worklogs/main-worklog.md` with:

- Objective.
- Current phase.
- Loop status.
- Last verified state.
- Next step.
- Blockers.
- Completion evidence.

Do not redefine the goal to match partial progress.

### 3. Clarify Requirements

Use `superpowers:brainstorming` when available. Ask focused questions one at a time until the following are clear enough to write a spec:

- Project purpose.
- Target users.
- Core workflows.
- In-scope work.
- Out-of-scope work.
- Technical constraints.
- Integrations and external services.
- Success criteria.
- Acceptance tests or verification evidence.
- Risks, sensitive operations, credentials, or approvals.
- Preferred degree of autonomy after initialization.

After the user answers the core questions, avoid making them manually drive routine next steps. Continue through the loop unless a later decision affects scope, risk, credentials, external access, product direction, or acceptance criteria.

### 4. Create Project Artifacts

Create or update these artifacts unless the repository already has equivalent files:

- `AGENTS.md`
- `docs/specs/<YYYY-MM-DD>-project-spec.md`
- `docs/tasks/project-tasks.md`
- `docs/worklogs/main-worklog.md`
- `docs/worklogs/subagents/<role>-worklog.md` for each planned subagent role
- `docs/agents/subagent-briefs/<role>.md` for each planned subagent role

Use repository conventions when they are clearer than these default paths, but record any path changes in `AGENTS.md` and the main work log.

### 5. Write AGENTS.md

`AGENTS.md` must define:

- Project goal and non-goals.
- Repository structure and directory responsibilities.
- Technology stack and local commands discovered so far.
- Coding, testing, documentation, review, and security standards.
- Main-agent responsibilities.
- Subagent roles and boundaries.
- Allowed edit zones.
- Forbidden edit zones.
- Work log requirements.
- Decision and escalation rules.
- Completion audit requirements.

Make forbidden behavior explicit: no scope expansion, no undocumented architectural changes, no edits outside assigned ownership, no silent changes to another agent's area, and no completion claim without evidence.

### 6. Write The Project Spec

The spec must include:

- Background and problem statement.
- Target users and core use cases.
- Scope and non-scope.
- Functional requirements.
- Non-functional requirements.
- Architecture and module boundaries.
- Data flow and external dependencies.
- Error handling and edge cases.
- Testing and verification strategy.
- Acceptance criteria.
- Risks, assumptions, and open questions.

Self-review the spec before implementation. Fix placeholders, contradictions, ambiguous requirements, and uncontrolled scope.

### 7. Plan Work And Subagents

Create `docs/tasks/project-tasks.md` with:

- Task id.
- Owner.
- Status.
- Dependencies.
- Files or directories in scope.
- Verification command or evidence.
- Work log link.

Create each subagent brief with:

- Role name.
- Objective.
- Inputs.
- Allowed files and directories.
- Forbidden files and decisions.
- Required output.
- Verification requirements.
- Work log path.
- Handoff requirements.

Subagents may communicate through work logs and explicit handoffs. They may not broaden scope or edit outside their assigned area.

### 8. Run The Orchestration Loop

Repeat until completion or a proven blocker:

1. Read goal state, spec, task list, and work logs.
2. Select the next highest-value task.
3. Execute directly or dispatch a bounded subagent.
4. Record decisions, changes, blockers, and evidence.
5. Verify the result with tests, commands, review, or artifact inspection.
6. Update task status and logs.
7. Integrate subagent outputs.
8. Continue without asking the user to drive routine next steps.

Ask the user only when the missing information changes project scope, risk, product direction, credentials, external access, or acceptance criteria.

### 9. Completion Audit

Before final response, audit every explicit requirement:

- Goal objective.
- `AGENTS.md` rules.
- Spec acceptance criteria.
- Task list.
- Subagent brief outputs.
- Test and verification commands.
- Generated artifacts.
- User instructions from the conversation.

For each item, identify concrete evidence from files, command output, tests, rendered artifacts, or logs. Treat uncertain or indirect evidence as incomplete. Continue working if any required item is missing.

## Platform Fallbacks

- If native goal mode is unavailable, emulate it in the main work log.
- If native subagents are unavailable, simulate subagent roles with separate briefs, logs, and bounded passes performed by the main agent.
- If `superpowers:brainstorming` is unavailable, follow the clarification and design gate manually and record that fallback in the work log.
- If the repository cannot run tests yet, record what verification was possible and what must be added.

## Template Use

When this skill is used from the full GitHub package, prefer the templates in the repository `templates/` directory. When installed with `install.sh`, shared templates are copied to `$HOME/.project-init-orchestrator/templates`. If the templates are unavailable after installation, generate files that contain the same sections listed in this skill.
