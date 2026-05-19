# Tesserae — Claude Code plugin

Slash commands, hooks, a skill, and MCP auto-registration for [Tesserae](https://github.com/ca1773130n/Tesserae) — the typed-graph project-memory compiler.

## Install

Requires `tesserae` already installed (`pip install tesserae` or `pipx install tesserae`).

```bash
# In a Claude Code session
/plugin install https://github.com/ca1773130n/Tesserae plugin/

# Or from a local checkout
/plugin install /path/to/Tesserae/plugin/
```

## What you get

Until later phases land, the plugin ships:

- **MCP auto-registration** for the `tesserae_mcp` server. After install, the agent can call `mcp__plugin_tesserae_tesserae__ask`, `…__search_nodes`, `…__list_sessions`, etc. without any manual `claude_desktop_config.json` editing.

Subsequent phases add slash commands (`/tesserae:compile`, `/tesserae:ask`, …), a skill (`using-tesserae`), and four hooks. See [`docs/superpowers/plans/2026-05-19-claude-code-plugin-plan.md`](../docs/superpowers/plans/2026-05-19-claude-code-plugin-plan.md) for status.

## Verify

```
/plugin list           # tesserae should appear
/mcp                   # a `tesserae` MCP server should be registered
```

If the MCP server is missing, check that the `tesserae_mcp` binary is on your `PATH`:

```bash
which tesserae_mcp
```

## Uninstall

```
/plugin uninstall tesserae
```

Plugin uninstall is reversible and does not touch any project's `.tesserae/` directory.
