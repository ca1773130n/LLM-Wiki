#!/usr/bin/env bash
# Print a compact Tesserae project status: graph node/edge counts,
# last-compile timestamp, session count. Pure read — never mutates.
# Designed for `/tesserae:status` in the Claude Code plugin.

set -uo pipefail

project_root="${1:-$PWD}"
tdir="${project_root}/.tesserae"

if [[ ! -d "$tdir" ]]; then
  echo "Tesserae status: no .tesserae/ in ${project_root}" >&2
  echo "  Run /tesserae:setup or 'tesserae project setup' to initialise this project."
  exit 1
fi

# Node + edge counts from graph.json. Prefer jq; fall back to a tiny
# python one-liner. Both surface zero if the file is missing or
# unparseable rather than failing the whole status print.
nodes="?"
edges="?"
if [[ -f "${tdir}/graph.json" ]]; then
  if command -v jq >/dev/null 2>&1; then
    nodes=$(jq -r '.nodes | length' "${tdir}/graph.json" 2>/dev/null || echo "?")
    edges=$(jq -r '.edges | length' "${tdir}/graph.json" 2>/dev/null || echo "?")
  elif command -v python3 >/dev/null 2>&1; then
    counts=$(python3 -c "
import json, sys
try:
    g = json.load(open(sys.argv[1]))
    print(len(g.get('nodes', [])), len(g.get('edges', [])))
except Exception:
    print('? ?')
" "${tdir}/graph.json" 2>/dev/null || echo "? ?")
    nodes="${counts% *}"
    edges="${counts#* }"
  fi
fi

# Last build timestamp from the JSONL ledger.
last_build="never"
if [[ -f "${tdir}/.build-history.jsonl" ]]; then
  last_line=$(tail -n 1 "${tdir}/.build-history.jsonl" 2>/dev/null || echo "")
  if [[ -n "$last_line" ]]; then
    if command -v jq >/dev/null 2>&1; then
      last_build=$(echo "$last_line" | jq -r '.timestamp // .at // empty' 2>/dev/null || echo "unknown")
    else
      # Best-effort grep for "timestamp" or "at" field.
      last_build=$(echo "$last_line" | grep -oE '"(timestamp|at)"[[:space:]]*:[[:space:]]*"[^"]+"' | head -1 | sed -E 's/.*"([^"]+)"$/\1/')
      [[ -z "$last_build" ]] && last_build="unknown"
    fi
  fi
fi

# Session count from the harness_sessions manifest.
sessions=0
if [[ -f "${tdir}/harness_sessions/manifest.json" ]]; then
  if command -v jq >/dev/null 2>&1; then
    sessions=$(jq -r '.sessions | length' "${tdir}/harness_sessions/manifest.json" 2>/dev/null || echo "0")
  else
    sessions=$(grep -c '"id"' "${tdir}/harness_sessions/manifest.json" 2>/dev/null || echo "0")
  fi
fi

# Vault path if configured.
vault="(not configured)"
if [[ -f "${tdir}/config.json" ]] && command -v jq >/dev/null 2>&1; then
  vault=$(jq -r '.obsidian.vault_path // "(not configured)"' "${tdir}/config.json" 2>/dev/null || echo "(not configured)")
fi

cat <<EOT
Tesserae status — ${project_root}
  graph:         ${nodes} nodes, ${edges} edges
  last compile:  ${last_build}
  sessions:      ${sessions}
  obsidian:      ${vault}

Quick actions:
  /tesserae:refresh         — import sessions + recompile + sync vault
  /tesserae:ask "…"         — query the compiled graph
  /tesserae:serve           — preview the static site
EOT
