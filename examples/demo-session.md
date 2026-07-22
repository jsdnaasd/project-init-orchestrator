# Demo Session

## Codex Prompt

```text
使用 $project-init-orchestrator 初始化这个项目。先建立目标并检查仓库，然后逐个询问需求，完成设计和 spec 后再创建有边界的子 Agent 并持续执行到验证完成。
```

## Deterministic Initialization

```bash
python3 ~/.codex/skills/project-init-orchestrator/scripts/pio.py inspect --project .
python3 ~/.codex/skills/project-init-orchestrator/scripts/pio.py init \
  --project . \
  --name "Example Product" \
  --objective "Build and verify the approved product"
```

Generated structure:

```text
AGENTS.md
.project-init-orchestrator/
├── config.json
├── events.jsonl
├── snapshot.md
└── state.json
docs/
├── agents/subagent-briefs/
├── completion-audit.md
├── specs/<date>-project-spec.md
├── tasks/project-tasks.md
└── worklogs/main-worklog.md
```

## Bounded Delegation

```bash
PIO="$HOME/.codex/skills/project-init-orchestrator/scripts/pio.py"
python3 "$PIO" add-role implementation --project .
python3 "$PIO" set-policy implementation --project . \
  --allow 'src/**' \
  --allow 'tests/**' \
  --forbid 'src/secrets/**'
python3 "$PIO" baseline implementation --project .
```

After the delegated pass:

```bash
python3 "$PIO" audit implementation --project .
python3 "$PIO" validate --project . --stage ready
```

An edit to `README.md` would be reported as `outside-scope`; an edit under `src/secrets/**` would be reported as `forbidden`.
