---
description: Print instructions for running the interactive Tesserae setup wizard (must be in a terminal — not slash-runnable).
argument-hint: ""
allowed-tools:
  - "Bash(printf:*)"
disable-model-invocation: true
---

The Tesserae setup wizard is interactive — it prompts for wiki name, sources, and companion-tool selections, then writes `.tesserae/config.json`. Claude Code slash commands run in a non-interactive shell with no stdin attached, so the wizard's first `input()` call hits EOF immediately and aborts.

Run it from a real terminal instead:

!`printf '\n  Run this in a terminal (NOT inside a Claude Code slash command):\n\n    cd %s\n    tesserae project setup\n\n  Once `.tesserae/` exists in your project, every other /tesserae:* command works inline from this session.\n\n' "$PWD"`
