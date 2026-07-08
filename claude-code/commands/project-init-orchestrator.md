# Project Init Orchestrator

Use this command to initialize or restart a coding project with disciplined project control before implementation.

## Command Intent

You are the Main Agent. Your job is to establish a persistent project goal, clarify requirements, create project control documents, define bounded subagent roles, maintain work logs, and then run an execution loop until the project is complete or genuinely blocked.

Do not start feature implementation until the project goal, `AGENTS.md`, project spec, task list, and subagent boundaries are documented.

## Required Workflow

Run the following sequence in order.

### 1. Inspect The Repository

Check the current project state:

- Current directory.
- Git status.
- Existing `AGENTS.md`, `CLAUDE.md`, specs, README files, package manifests, test configs, and source layout.
- Existing conventions and commands.
- Recent commits when available.

If the repository is empty, record that and use the default artifact paths.

### 2. Establish Goal Mode

If Claude Code has an active goal or planning mechanism available in the current environment, use it. If not, emulate goal mode in `docs/worklogs/main-worklog.md`.

The persistent goal record must include:

- Objective.
- Current phase.
- Loop status.
- Last verified state.
- Next step.
- Blockers.
- Completion evidence.

Do not shrink or redefine the objective to match partial progress.

### 3. Clarify Requirements

Ask focused questions one at a time until the project is clear enough to write a spec.

Cover:

- Project purpose.
- Target users.
- Core workflows.
- In-scope work.
- Out-of-scope work.
- Technical constraints.
- Integrations and external services.
- Success criteria.
- Acceptance tests or verification evidence.
- Risks, credentials, approvals, or sensitive operations.
- Desired autonomy level after initialization.

If a brainstorming or design skill is available, use it before implementation. If no such skill exists, follow the same design gate manually and record the fallback in the main work log.

After the project details are collected, do not require the user to manually drive routine next steps. Continue the loop unless the missing information affects scope, risk, product direction, credentials, external access, or acceptance criteria.

### 4. Create Project Artifacts

Create or update these files unless the project already has equivalent paths:

- `AGENTS.md`
- `docs/specs/<YYYY-MM-DD>-project-spec.md`
- `docs/tasks/project-tasks.md`
- `docs/worklogs/main-worklog.md`
- `docs/worklogs/subagents/<role>-worklog.md`
- `docs/agents/subagent-briefs/<role>.md`

Use templates from the workflow repository when available. When installed with `install.sh`, shared templates are normally available at `$HOME/.project-init-orchestrator/templates`.

- `templates/AGENTS.md`
- `templates/SPEC.md`
- `templates/TASKS.md`
- `templates/WORKLOG.md`
- `templates/SUBAGENT_BRIEF.md`
- `templates/COMPLETION_AUDIT.md`

If templates are unavailable, generate files with the same sections described in this command.

### 5. Write AGENTS.md

`AGENTS.md` is binding for all agents. It must define:

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

Forbidden behavior must be explicit:

- No scope expansion without main-agent approval.
- No undocumented architecture changes.
- No edits outside assigned ownership.
- No silent changes to another agent's area.
- No completion claim without verification evidence.

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

Before implementation, review the spec for placeholders, contradictions, ambiguous requirements, and uncontrolled scope.

### 7. Plan Tasks And Subagents

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

If native subagents are available, dispatch one bounded subagent per independent role. If native subagents are not available, simulate subagent roles with separate briefs, separate work log entries, and bounded passes by the Main Agent.

### 8. Run The Loop

Repeat until completion or a proven blocker:

1. Read goal state, spec, task list, and work logs.
2. Select the next highest-value task.
3. Execute directly or dispatch a bounded subagent.
4. Record decisions, changes, blockers, and evidence.
5. Verify the result with tests, commands, review, or artifact inspection.
6. Update task status and logs.
7. Integrate subagent outputs.
8. Continue without asking the user to drive routine next steps.

### 9. Completion Audit

Before final response, create or update `docs/completion-audit.md` or an equivalent project audit file.

Audit every explicit requirement:

- Goal objective.
- `AGENTS.md` rules.
- Spec acceptance criteria.
- Task list.
- Subagent brief outputs.
- Test and verification commands.
- Generated artifacts.
- User instructions from the conversation.

For each item, cite concrete evidence from files, command output, tests, rendered artifacts, or logs. Treat uncertain or indirect evidence as incomplete. Continue working if any required item is missing.

## Platform Fallbacks

- If native goal mode is unavailable, emulate it in the main work log.
- If native subagents are unavailable, simulate role-bounded passes with briefs and logs.
- If a brainstorming skill is unavailable, do manual clarification and design gating.
- If tests do not exist, document the verification that was possible and add test setup tasks when the project requires them.

## Trigger Examples

- `/project-init-orchestrator initialize this project`
- `/project-init-orchestrator set up the workflow before implementation`
- `/project-init-orchestrator create AGENTS.md, spec, subagent briefs, and work logs`
