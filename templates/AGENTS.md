# AGENTS.md

## Project Goal

- Objective:
- Success criteria:
- Non-goals:
- Current phase:

## Goal And Loop Mode

All agents must preserve the project objective until the completion audit proves it is done.

Loop:

1. Read this file, the project spec, task list, and work logs.
2. Select the next highest-value bounded task.
3. Execute only within assigned scope.
4. Record decisions, changes, blockers, and verification evidence.
5. Update task status.
6. Continue until completion is proven or a blocker is documented.

## Repository Structure

| Path | Owner | Purpose | Edit Rules |
| --- | --- | --- | --- |
| `docs/specs/` | Main Agent | Project specs and requirements | Update only through documented decisions |
| `docs/tasks/` | Main Agent | Task tracking and verification evidence | Keep status current |
| `docs/worklogs/` | All Agents | Progress, decisions, blockers, handoffs | Every agent writes its own entries |
| `docs/agents/subagent-briefs/` | Main Agent | Scoped subagent assignments | Main Agent owns brief changes |

## Technology And Commands

Record discovered stack and commands here.

| Purpose | Command | Evidence |
| --- | --- | --- |
| Install dependencies |  |  |
| Run tests |  |  |
| Run lint |  |  |
| Run build |  |  |

## Main Agent Responsibilities

- Maintain goal state and loop progress.
- Ask requirement questions before implementation.
- Write and update the project spec.
- Create task plans and subagent briefs.
- Dispatch bounded subagent work when supported.
- Integrate subagent results and resolve conflicts.
- Verify every completed task.
- Run the final completion audit.

## Subagent Boundaries

Subagents must follow their assigned brief. A subagent may only edit files listed in its allowed scope and must not make product, architecture, security, or scope decisions unless the brief explicitly grants that authority.

Required behavior:

- Read this file before working.
- Read the project spec before working.
- Read the assigned brief before working.
- Write progress to the assigned work log.
- Stop and report when blocked by missing information, permissions, credentials, or scope conflict.

Forbidden behavior:

- Expanding project scope without main-agent approval.
- Editing outside the allowed file list.
- Changing architecture without a recorded decision.
- Silently modifying another role's area.
- Declaring completion without verification evidence.

## Work Logs

Main log: `docs/worklogs/main-worklog.md`

Subagent logs: `docs/worklogs/subagents/<role>-worklog.md`

Each entry must include date, actor, phase, actions, decisions, blockers, evidence, and next step.

## Decision Rules

Record decisions that affect scope, architecture, dependencies, external services, data model, security, user experience, or acceptance criteria.

Decision format:

- Decision:
- Reason:
- Alternatives considered:
- Impact:
- Owner:
- Date:

## Completion Audit

The project is complete only when every item below has concrete evidence:

- Project goal.
- Spec acceptance criteria.
- Task list.
- Tests or verification commands.
- Subagent handoffs.
- Generated artifacts.
- User instructions.
