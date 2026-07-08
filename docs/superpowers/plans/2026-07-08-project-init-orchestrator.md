# Project Init Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable dual-platform workflow package that installs a Codex Skill and Claude Code command for disciplined project initialization with goals, loops, specs, bounded subagents, work logs, and main-agent orchestration.

**Architecture:** The repository will contain platform-native entrypoints plus shared templates. Codex uses `codex/project-init-orchestrator/SKILL.md`; Claude Code uses `claude-code/commands/project-init-orchestrator.md`; both point agents toward the same artifact templates and workflow contract. A shell installer copies these files into user tool directories, and validation scripts prove that required files and required workflow terms are present.

**Tech Stack:** Markdown, YAML, POSIX shell, Python 3 validation script, Codex Skill format, Claude Code command Markdown.

---

### Task 1: Scaffold Codex Skill

**Files:**
- Create: `codex/project-init-orchestrator/SKILL.md`
- Create: `codex/project-init-orchestrator/agents/openai.yaml`

- [ ] **Step 1: Run the system skill initializer**

Run:

```bash
/Users/Zhuanz1/.codex/skills/.system/skill-creator/scripts/init_skill.py project-init-orchestrator --path codex --interface display_name="Project Init Orchestrator" --interface short_description="Disciplined multi-agent project startup" --interface default_prompt="Use $project-init-orchestrator to initialize this project with goals, specs, AGENTS.md, bounded subagents, and work logs."
```

Expected: creates `codex/project-init-orchestrator/SKILL.md` and `codex/project-init-orchestrator/agents/openai.yaml`.

- [ ] **Step 2: Replace generated Skill content**

Write `SKILL.md` with frontmatter and workflow instructions requiring goal mode, loop mode, `superpowers:brainstorming`, `AGENTS.md`, specs, tasks, work logs, subagent briefs, main-agent orchestration, platform fallbacks, and completion audits.

- [ ] **Step 3: Validate Skill frontmatter**

Run:

```bash
/Users/Zhuanz1/.codex/skills/.system/skill-creator/scripts/quick_validate.py codex/project-init-orchestrator
```

Expected: validation passes.

### Task 2: Add Shared Templates

**Files:**
- Create: `templates/AGENTS.md`
- Create: `templates/SPEC.md`
- Create: `templates/TASKS.md`
- Create: `templates/WORKLOG.md`
- Create: `templates/SUBAGENT_BRIEF.md`
- Create: `templates/COMPLETION_AUDIT.md`

- [ ] **Step 1: Create artifact templates**

Write templates that a triggered agent can copy into a target project. Each template must include goal state, loop state, ownership boundaries, allowed and forbidden edits, required evidence, and handoff requirements where relevant.

- [ ] **Step 2: Check templates for required sections**

Run:

```bash
python3 scripts/validate_repository.py
```

Expected: validation passes after Task 4 creates the script.

### Task 3: Add Claude Code Command

**Files:**
- Create: `claude-code/commands/project-init-orchestrator.md`

- [ ] **Step 1: Write command content**

Write a Claude Code command that implements the same workflow contract as the Codex Skill, including goal-mode fallback, loop continuation, project questions, `AGENTS.md`, specs, subagent briefs, work logs, and completion audit.

- [ ] **Step 2: Check command parity**

Run:

```bash
python3 scripts/validate_repository.py
```

Expected: validation confirms Claude Code command includes required workflow terms.

### Task 4: Add Installer and Repository Validation

**Files:**
- Create: `install.sh`
- Create: `scripts/validate_repository.py`

- [ ] **Step 1: Write installer**

Write `install.sh` so it supports real install and `DRY_RUN=1`. It must copy the Codex Skill into `${CODEX_HOME:-$HOME/.codex}/skills/project-init-orchestrator` and the Claude Code command into `$HOME/.claude/commands/project-init-orchestrator.md`.

- [ ] **Step 2: Write repository validator**

Write `scripts/validate_repository.py` to assert required files exist, required content terms appear, templates contain required headings, and `install.sh` is executable.

- [ ] **Step 3: Validate dry-run installation**

Run:

```bash
DRY_RUN=1 HOME="$(mktemp -d)" CODEX_HOME="$(mktemp -d)/codex" ./install.sh
```

Expected: prints intended copy operations without writing to real user directories.

### Task 5: Add README and Completion Audit

**Files:**
- Create: `README.md`
- Create: `docs/completion-audit.md`

- [ ] **Step 1: Write GitHub README**

Document what the workflow does, installation, manual install, Codex trigger, Claude Code trigger, generated files, goal/loop behavior, subagent boundaries, and platform fallbacks.

- [ ] **Step 2: Write completion audit**

Write `docs/completion-audit.md` mapping every acceptance criterion in the design spec to concrete repository evidence.

- [ ] **Step 3: Run all validations**

Run:

```bash
/Users/Zhuanz1/.codex/skills/.system/skill-creator/scripts/quick_validate.py codex/project-init-orchestrator
python3 scripts/validate_repository.py
DRY_RUN=1 HOME="$(mktemp -d)" CODEX_HOME="$(mktemp -d)/codex" ./install.sh
git status --short
```

Expected: validators pass, installer dry-run succeeds, and only intended project files are changed.

- [ ] **Step 4: Commit implementation**

Run:

```bash
git add README.md install.sh scripts codex claude-code templates docs
git commit -m "Add dual-platform project init orchestrator"
```

Expected: implementation commit created on `codex/project-init-orchestrator`.
