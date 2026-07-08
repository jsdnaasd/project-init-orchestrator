#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
codex_home="${CODEX_HOME:-$HOME/.codex}"
codex_dest="$codex_home/skills/project-init-orchestrator"
claude_dest="$HOME/.claude/commands/project-init-orchestrator.md"
shared_dest="$HOME/.project-init-orchestrator/templates"
dry_run="${DRY_RUN:-0}"

say() {
  printf '%s\n' "$*"
}

copy_dir() {
  local src="$1"
  local dest="$2"
  if [ "$dry_run" = "1" ]; then
    say "[dry-run] mkdir -p $(dirname "$dest")"
    say "[dry-run] rm -rf $dest"
    say "[dry-run] cp -R $src $dest"
    return
  fi
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -R "$src" "$dest"
}

copy_file() {
  local src="$1"
  local dest="$2"
  if [ "$dry_run" = "1" ]; then
    say "[dry-run] mkdir -p $(dirname "$dest")"
    say "[dry-run] cp $src $dest"
    return
  fi
  mkdir -p "$(dirname "$dest")"
  cp "$src" "$dest"
}

require_path() {
  local path="$1"
  if [ ! -e "$path" ]; then
    say "Missing required path: $path" >&2
    exit 1
  fi
}

require_path "$repo_root/codex/project-init-orchestrator"
require_path "$repo_root/claude-code/commands/project-init-orchestrator.md"
require_path "$repo_root/templates"

say "Installing Project Init Orchestrator"
say "Repository: $repo_root"

copy_dir "$repo_root/codex/project-init-orchestrator" "$codex_dest"
copy_file "$repo_root/claude-code/commands/project-init-orchestrator.md" "$claude_dest"
copy_dir "$repo_root/templates" "$shared_dest"

say ""
say "Installed paths:"
say "- Codex Skill: $codex_dest"
say "- Claude Code command: $claude_dest"
say "- Shared templates: $shared_dest"
say ""
say "Trigger examples:"
say "- Codex: Use \$project-init-orchestrator to initialize this project."
say "- Claude Code: /project-init-orchestrator initialize this project"
