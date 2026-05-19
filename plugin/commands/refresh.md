---
description: Refresh the Tesserae project — import new sessions, compile, sync vault.
argument-hint: ""
allowed-tools:
  - "Bash(tesserae sessions discover:*)"
  - "Bash(tesserae project compile:*)"
  - "Bash(tesserae project obsidian-sync:*)"
---

Run the three-step refresh cycle for the current Tesserae project: import any new Claude Code / Codex sessions that ran inside this project, recompile the graph, then sync the vault projection back to Obsidian. Use this after you've made significant edits or just finished an agent session whose insights you want captured in the next compile's graph.

!`tesserae sessions discover --import`
!`tesserae project compile`
!`tesserae project obsidian-sync`

After all three commands finish, summarise the new state in one line: total node count, total edge count, number of imported sessions, vault orphans pruned (if any). Read the values from the compile output above.
