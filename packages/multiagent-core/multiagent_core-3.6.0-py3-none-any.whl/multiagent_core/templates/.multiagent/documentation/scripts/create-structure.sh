#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[create-structure] %s\n' "$*"
}

usage() {
  cat <<'USAGE'
Usage: create-structure.sh [--project-root PATH] [--dry-run]

Bootstraps the basic documentation scaffolding for a project. The script creates
`docs/` (if missing) and copies a single universal README template. All content
intelligence is delegated to documentation subagents.

Options:
  --project-root PATH  Operate on a specific project directory (defaults to CWD)
  --dry-run            Show actions without writing to disk
  -h, --help           Display this help text
USAGE
}

resolve_root() {
  local provided="$1"
  if [[ -n "$provided" ]]; then
    printf '%s' "$(cd "$provided" && pwd)"
    return 0
  fi

  if command -v git >/dev/null 2>&1; then
    if git_root=$(git rev-parse --show-toplevel 2>/dev/null); then
      printf '%s' "$git_root"
      return 0
    fi
  fi

  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  printf '%s' "$(cd "$script_dir/../../.." && pwd)"
}

ensure_memory_templates() {
  local memory_dir="$1"
  local dry_run="$2"

  if [[ "$dry_run" == 'true' ]]; then
    log "[dry-run] would ensure documentation memory templates exist"
    return 0
  fi

  mkdir -p "$memory_dir"
  for template in template-status.json doc-registry.json consistency-check.json update-history.json; do
    local path="$memory_dir/$template"
    if [[ ! -f "$path" ]]; then
      case "$template" in
        template-status.json)
          cat >"$path" <<'JSON'
{
  "project_type": null,
  "project_name": null,
  "initialized": null,
  "templates": {}
}
JSON
          ;;
        doc-registry.json)
          cat >"$path" <<'JSON'
{
  "documents": {},
  "last_updated": null
}
JSON
          ;;
        consistency-check.json)
          cat >"$path" <<'JSON'
{
  "last_check": null,
  "issues": []
}
JSON
          ;;
        update-history.json)
          cat >"$path" <<'JSON'
{
  "updates": [],
  "total_updates": 0,
  "last_update": null
}
JSON
          ;;
      esac
      log "seeded documentation memory template ${template}"
    fi
  done
}

copy_readme_template() {
  local template_root="$1"
  local target_file="$2"
  local dry_run="$3"

  mkdir -p "$(dirname "$target_file")"

  if [[ "$dry_run" == 'true' ]]; then
    log "[dry-run] would copy README template to ${target_file#$PROJECT_ROOT/}"
    return 0
  fi

  if [[ -f "$target_file" ]]; then
    log "found existing docs/README.md; leaving in place"
    return 0
  fi

  local source="$template_root/README.template.md"
  if [[ ! -f "$source" ]]; then
    log "README template not found at $source" >&2
    return 1
  fi

  cp "$source" "$target_file"
  log "created docs/README.md from template"
}

main() {
  local project_root_arg=""
  local dry_run='false'

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --project-root)
        project_root_arg="$2"
        shift 2
        ;;
      --dry-run)
        dry_run='true'
        shift
        ;;
      -h|--help)
        usage
        return 0
        ;;
      *)
        printf 'Unknown argument: %s\n' "$1" >&2
        usage >&2
        return 1
        ;;
    esac
  done

  PROJECT_ROOT="$(resolve_root "$project_root_arg")"
  TEMPLATE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../templates" && pwd)"
  MEMORY_ROOT="$PROJECT_ROOT/.multiagent/documentation/memory"

  log "project root: $PROJECT_ROOT"

  if [[ "$dry_run" == 'true' ]]; then
    log "[dry-run] would ensure docs/ directory"
  else
    mkdir -p "$PROJECT_ROOT/docs"
  fi

  copy_readme_template "$TEMPLATE_ROOT" "$PROJECT_ROOT/docs/README.md" "$dry_run"
  ensure_memory_templates "$MEMORY_ROOT" "$dry_run"

  log "documentation scaffolding ready"
}

main "$@"
