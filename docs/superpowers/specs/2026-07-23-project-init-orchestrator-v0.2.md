# Project Init Orchestrator v0.2 Design

## Objective

Upgrade the repository from an instruction-only, dual-platform workflow into a Codex-only Skill with a deterministic execution layer. Preserve the existing spec-first and bounded-agent philosophy while making initialization, state persistence, validation, context snapshots, and file-boundary auditing executable and testable.

## Product Boundary

Version 0.2 is a Codex Skill plus a standard-library Python CLI. It does not implement its own language model, background daemon, or cross-platform agent runtime. Codex remains responsible for interviews, reasoning, native goal tools, and native subagent dispatch when those capabilities exist.

The CLI is responsible for operations that should not depend on prompt compliance:

- Creating project control artifacts without overwriting existing files.
- Persisting loop state and append-only events.
- Enforcing valid phase transitions.
- Producing compact project snapshots for context recovery.
- Recording role policies and detecting changed files outside allowed scope.
- Validating structure, implementation readiness, and completion evidence.

## Skill Package

The installed Skill must be self-contained:

```text
project-init-orchestrator/
├── SKILL.md
├── agents/openai.yaml
├── scripts/pio.py
├── assets/templates/
└── references/
```

No Claude Code command or external shared-template directory is installed. Templates used to produce project files live under `assets/templates/`.

## CLI Contract

The CLI entrypoint is:

```bash
python3 <skill-dir>/scripts/pio.py <command> --project <path>
```

Required commands:

- `inspect`: report repository characteristics without writing.
- `init`: create control artifacts and persistent state idempotently.
- `status`: return the current structured state.
- `transition`: enforce the documented loop state machine.
- `log`: append a decision, progress, blocker, verification, or handoff event.
- `compact`: regenerate a concise snapshot while preserving the complete event log.
- `add-role`: create a bounded role, brief, and work log.
- `set-policy`: configure allowed and forbidden path patterns for a role.
- `baseline`: capture file hashes before delegated work.
- `audit`: compare the current tree with the role baseline and classify allowed, forbidden, and out-of-scope changes.
- `validate`: check `structure`, `ready`, or `complete` requirements.

All commands return machine-readable JSON and use a non-zero exit status for invalid input or failed validation.

## Persistent State

Each initialized project receives:

```text
.project-init-orchestrator/
├── config.json
├── state.json
├── events.jsonl
├── snapshot.md
├── baselines/
└── audits/
```

`events.jsonl` is append-only. `snapshot.md` contains current goal, phase, next step, role policies, blockers, evidence, event counts, and recent events. Compaction never deletes the source event log.

## Loop State Machine

The normal path is:

```text
initialized -> clarify -> spec -> plan -> execute -> verify -> audit -> complete
```

Controlled backward edges support iteration:

- `spec -> clarify`
- `plan -> spec`
- `execute -> plan`
- `verify -> execute`
- `audit -> execute`

Entering `verify`, `audit`, or `complete` requires evidence. Invalid transitions fail without mutating state.

## Boundary Audit

Each non-main role starts with no write permission. The main Agent must explicitly configure allowed paths before delegation. Default sensitive patterns remain forbidden even when an allow pattern is broad.

`baseline` records hashes for visible project files while excluding `.git/`, ignored files, and `.project-init-orchestrator/`. `audit` compares the current tree to that baseline and classifies each changed path as:

- allowed;
- forbidden by role or global policy;
- outside the role's declared scope.

The report is saved under `.project-init-orchestrator/audits/` and also appended to the event log.

## Installation Safety

`install.sh` installs only the Codex Skill. Existing installations are moved to timestamped sibling backups before replacement. Uninstall is recoverable: it moves the installed Skill to a backup rather than deleting it. Dry-run mode performs no writes.

## Verification

Pytest must cover:

- artifact generation and idempotency;
- preservation of existing project files;
- valid and invalid phase transitions;
- evidence gates;
- event logging and compact snapshots;
- stack inspection;
- role policy setup, baseline capture, and boundary violations;
- structure and readiness validation;
- dry-run, backup, reinstall, and recoverable uninstall behavior.

The repository must also include:

- GitHub Actions CI;
- an MIT license;
- a deterministic evaluation script and generated report;
- a public example;
- release-ready Chinese documentation and honest resume copy.

## Acceptance Criteria

1. The Skill is self-contained and passes the Codex Skill validator.
2. The CLI uses only the Python standard library and all required commands work from the installed Skill directory.
3. Tests cover critical initialization, state, audit, validation, and installer behavior.
4. Re-running initialization produces no unintended changes and never overwrites existing artifacts.
5. A forbidden or out-of-scope file change produces a failed audit with concrete paths.
6. The installer never permanently deletes an existing installation.
7. README claims are limited to behavior proven by tests or evaluation evidence.
8. CI, repository validation, installation smoke tests, and the evaluation suite pass before release.
