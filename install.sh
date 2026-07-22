#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_directory="$repository_root/codex/project-init-orchestrator"
codex_root="${CODEX_HOME:-${HOME}/.codex}"
skills_directory="$codex_root/skills"
destination="$skills_directory/project-init-orchestrator"
dry_run="${DRY_RUN:-0}"
action="install"

say() {
  printf '%s\n' "$*"
}

usage() {
  say "Usage: ./install.sh [--install|--uninstall] [--dry-run]"
  say ""
  say "Installs only the Codex Project Init Orchestrator Skill."
}

for argument in "$@"; do
  case "$argument" in
    --install)
      action="install"
      ;;
    --uninstall)
      action="uninstall"
      ;;
    --dry-run)
      dry_run="1"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      say "Unknown argument: $argument" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ "$dry_run" != "0" ] && [ "$dry_run" != "1" ]; then
  say "DRY_RUN must be 0 or 1" >&2
  exit 2
fi

if [ ! -f "$source_directory/SKILL.md" ] || [ ! -f "$source_directory/scripts/pio.py" ]; then
  say "Incomplete Skill source: $source_directory" >&2
  exit 1
fi

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_destination="$skills_directory/project-init-orchestrator.backup-$timestamp-$$"

if [ "$action" = "uninstall" ]; then
  if [ ! -e "$destination" ]; then
    say "Project Init Orchestrator is not installed at $destination"
    exit 0
  fi
  if [ "$dry_run" = "1" ]; then
    say "[dry-run] mv $destination $backup_destination"
    exit 0
  fi
  mkdir -p "$skills_directory"
  mv "$destination" "$backup_destination"
  say "Uninstalled Project Init Orchestrator without deleting it."
  say "Recovery backup: $backup_destination"
  exit 0
fi

if [ "$dry_run" = "1" ]; then
  say "[dry-run] mkdir -p $skills_directory"
  if [ -e "$destination" ]; then
    say "[dry-run] mv $destination $backup_destination"
  fi
  say "[dry-run] cp -R $source_directory $destination"
  say "[dry-run] verify $destination/SKILL.md and $destination/scripts/pio.py"
  exit 0
fi

mkdir -p "$skills_directory"
staging_directory="$skills_directory/.project-init-orchestrator.install-$$"
moved_existing="0"

rollback() {
  if [ -e "$staging_directory" ]; then
    rm -rf -- "$staging_directory"
  fi
  if [ "$moved_existing" = "1" ] && [ ! -e "$destination" ] && [ -e "$backup_destination" ]; then
    mv "$backup_destination" "$destination"
  fi
}
trap rollback EXIT INT TERM

if [ -e "$destination" ]; then
  mv "$destination" "$backup_destination"
  moved_existing="1"
fi

cp -R "$source_directory" "$staging_directory"
mv "$staging_directory" "$destination"

if [ ! -f "$destination/SKILL.md" ] || [ ! -f "$destination/scripts/pio.py" ]; then
  say "Installed Skill failed verification" >&2
  exit 1
fi

moved_existing="0"
trap - EXIT INT TERM

say "Installed Project Init Orchestrator for Codex."
say "Skill: $destination"
if [ -e "$backup_destination" ]; then
  say "Previous installation backup: $backup_destination"
fi
say "Trigger: Use \$project-init-orchestrator to initialize this project."
