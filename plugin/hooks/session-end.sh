#!/usr/bin/env bash
# Tesserae plugin — SessionEnd hook.
# Backgrounds `tesserae sessions discover --import && tesserae project
# compile` so the conversation just-ended becomes graph nodes for the
# next session. Always exit 0 — never block session close.

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_lib.sh
. "${HERE}/_lib.sh"

if [[ "$(read_plugin_setting session_end)" != "true" ]]; then
  exit 0
fi

project_root="$(resolve_project_root)"
[[ -d "${project_root}/.tesserae" ]] || exit 0

tesserae_bin=$(find_tesserae) || {
  log_to ".session-end-hook.log" "skipped: tesserae binary not found on PATH"
  exit 0
}

# Background the import+compile. Detach via setsid where available so
# the process survives the session close cleanly; fall back to plain
# nohup. Output goes to the hook log for post-hoc debugging.
log_file="${project_root}/.tesserae/.session-end-hook.log"
{
  echo "==== $(date -u +%FT%TZ) — session-end refresh starting ===="
  "$tesserae_bin" sessions discover --import 2>&1 || echo "(sessions discover --import failed; continuing to compile anyway)"
  "$tesserae_bin" project compile 2>&1 || echo "(project compile failed)"
  echo "==== $(date -u +%FT%TZ) — done ===="
} >> "$log_file" 2>&1 &
disown 2>/dev/null || true

exit 0
