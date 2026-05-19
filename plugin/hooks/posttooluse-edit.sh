#!/usr/bin/env bash
# Tesserae plugin — PostToolUse hook matching Edit | Write | MultiEdit.
# When the edited file path is under docs/, queue an incremental
# `tesserae project compile --changed-only`, debounced via a lock
# file to once per 60 seconds. Disabled by default; opt-in via
# .claude/tesserae.local.md frontmatter `hooks.posttooluse_edit: true`.

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_lib.sh
. "${HERE}/_lib.sh"

if [[ "$(read_plugin_setting posttooluse_edit)" != "true" ]]; then
  exit 0
fi

# Path-based filtering happens HERE (matchers only match event/tool
# names, not paths — per the plugin manifest contract). We parse the
# stdin JSON's tool_input.file_path to decide whether to fire.
hook_input=$(cat)
file_path=$(echo "$hook_input" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null)
[[ -n "$file_path" ]] || exit 0

# Only react to edits under docs/ (the spec's chosen scope to avoid
# noise on every source-code edit).
case "$file_path" in
  */docs/*) ;;
  *) exit 0 ;;
esac

project_root="$(resolve_project_root)"
[[ -d "${project_root}/.tesserae" ]] || exit 0
tesserae_bin=$(find_tesserae) || exit 0

# Debounce via a lock file at .tesserae/.recompile.lock. Skip the
# recompile if the lock was touched within the last 60 seconds.
lock_file="${project_root}/.tesserae/.recompile.lock"
now=$(date -u +%s)
if [[ -f "$lock_file" ]]; then
  if last_run=$(cat "$lock_file" 2>/dev/null) && [[ "$last_run" =~ ^[0-9]+$ ]]; then
    if (( now - last_run < 60 )); then
      log_to ".posttooluse-edit-hook.log" "debounced (last run was $(( now - last_run ))s ago) for $file_path"
      exit 0
    fi
  fi
fi
echo "$now" > "$lock_file" 2>/dev/null || true

# Background the incremental compile so the user's edit doesn't block.
log_file="${project_root}/.tesserae/.posttooluse-edit-hook.log"
{
  echo "==== $(date -u +%FT%TZ) — incremental recompile for ${file_path} ===="
  "$tesserae_bin" project compile --changed-only 2>&1 || echo "(compile --changed-only failed)"
} >> "$log_file" 2>&1 &
disown 2>/dev/null || true

exit 0
