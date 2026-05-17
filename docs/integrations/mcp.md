# MCP — wire LLM-Wiki into Claude Code, Codex, Cursor

<!-- translations:start -->
<p align="center"><a href="../i18n/integrations/mcp.ko.md">한국어</a> · <a href="../i18n/integrations/mcp.zh.md">中文</a> · <a href="../i18n/integrations/mcp.ja.md">日本語</a> · <a href="../i18n/integrations/mcp.ru.md">Русский</a> · <a href="../i18n/integrations/mcp.es.md">Español</a> · <a href="../i18n/integrations/mcp.fr.md">Français</a></p>
<!-- translations:end -->

LLM-Wiki ships a [Model Context Protocol](https://modelcontextprotocol.io) stdio server that exposes the compiled typed graph to any MCP-aware client: Claude Code, Codex CLI, Cursor, Claude Desktop, and others. The server advertises three full MCP surfaces — **tools**, **resources**, and **prompts** — so clients can both query the graph on demand and seed context cheaply from canonical URIs.

## Prerequisites

The server reads from `.llm-wiki/graph.json`, so a one-time compile is required:

```bash
cd /path/to/your-project
llm_wiki project setup    # interactive; or --yes for non-interactive
llm_wiki project compile  # deterministic, no LLM calls, no API keys
```

Recompile any time your sources change. The server will pick up the new graph on the next tool call without needing to restart.

## 1) Generate the client config

```bash
llm_wiki project mcp-config
```

Prints a JSON snippet roughly like:

```json
{
  "mcpServers": {
    "llm-wiki": {
      "command": "python3",
      "args": [
        "-m", "llm_wiki.mcp_server",
        "--graph", "/path/to/your-project/.llm-wiki/graph.json"
      ]
    }
  }
}
```

The exact path is filled in from the current project. Pass `--name <alias>` if you want a different server entry name than `llm-wiki`.

## 2) Paste it into your MCP client

| Client | Config location |
|---|---|
| Claude Code | `~/.claude/mcp-servers.json` (or `~/.config/claude-code/mcp-servers.json`) |
| Claude Desktop | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Codex CLI | `~/.config/codex/mcp-servers.json` |
| Cursor | Settings → MCP Servers → paste JSON |
| Hermes | `~/.hermes/config.toml` (use the TOML-equivalent block printed by `mcp-config --format hermes`) |

Restart the client after editing. The next session will connect and discover the LLM-Wiki surface.

## 3) What the client sees

### Tools — invoked by the model

| Tool | Purpose |
|---|---|
| `schema` | Controlled node, edge, and wiki-kind vocabulary |
| `graph_summary` | Node + edge counts and type distributions for the active project |
| `search_nodes` | Filter graph nodes by query, type, kind, with score-ranked top-N |
| `node_context` | A node + its incident edges + neighbouring nodes |
| `search_facts` | Temporal facts projected from the graph (Graphiti-style) |
| `timeline` | Facts ordered by `valid_from` for a longitudinal view |
| `wiki_page` | The compiled markdown page body for a node |
| `raw_source` | The original source markdown (capped at 16 KB) |
| `lint_report` | The latest compile-time lint findings |
| `ask` | Natural-language Q&A via the configured memory backend (raganything, cognee, or compiled wiki) |
| `list_projects` / `register_project` / `activate_project` / `unregister_project` | Multi-project registry control |

### Resources — auto-loaded into the model's context

URIs the client can pull in via its resource picker without burning a tool turn:

- `llm-wiki://graph/schema` — same payload as the `schema` tool, ready as static context
- `llm-wiki://graph/summary` — summary of the active project
- `llm-wiki://lint-report` — the latest lint report as markdown

Plus URI templates the client can construct on demand:

- `llm-wiki://wiki/{kind}/{slug}` — any compiled wiki page body
- `llm-wiki://raw/{source_path}` — any raw source markdown

### Prompts — one-click research templates

These appear in the client's slash menu (e.g. Claude Code's `/` palette):

| Prompt | Arguments | What it does |
|---|---|---|
| `summarize-paper` | `slug` (required) | Calls `node_context` + `wiki_page` + optional `raw_source`, then returns a structured summary: contribution, method sketch, headline results, limitations, related nodes |
| `find-related-work` | `topic` (required), `limit` | Chains `search_nodes` + `node_context` for the top-K related items with relevance justifications |
| `compare-approaches` | `a`, `b` (both required) | Pulls `node_context` for both + `search_facts` for performance claims; returns side-by-side comparison with synthesis |
| `gap-analysis` | `topic` (optional) | Surfaces unresolved open questions, missing benchmarks, under-evidenced claims |
| `triage-open-questions` | _none_ | Lists every `OpenQuestion` node, groups by topic, proposes a priority order |

Each prompt renders to a single user message that tells the model exactly which LLM-Wiki tools to chain, so the model doesn't have to rediscover the surface every time.

## Multi-project: register several vaults under one server

A persistent registry at `~/.llm-wiki/registry.json` lets the same MCP server resolve any registered project by name:

```bash
llm_wiki register-project /path/to/research --name research
llm_wiki register-project /path/to/notes    --name notes
```

After this, every tool that accepts `project` or `graph_path` will resolve `project: "research"` against the registry instead of needing a full path. The server even validates that the registered `graph_path` still exists and returns a clear error if a recompile is needed.

### Fan-out across every registered vault

The `ask` tool accepts `scope: "all-registered"` to query every registered project in parallel and return aggregated results:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "Where is splatting used?",
    "scope": "all-registered"
  }
}
```

Restrict to a subset with `scope_aliases: ["research", "notes"]`.

## Multi-account Claude CLI

If your `ask` tool routes through the Claude CLI and you have multiple accounts (e.g. `~/.claude` and `~/.claude-personal2`), pass `claude_config_dir` per call:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "...",
    "claude_config_dir": "/Users/you/.claude-personal2"
  }
}
```

The server exports `CLAUDE_CONFIG_DIR` for the duration of that call only and restores the previous value afterwards. No leakage between calls.

## Verification

After restarting your MCP client, confirm the connection:

- Claude Code: `/mcp` should list `llm-wiki` with the tool count.
- Cursor: the MCP icon in the chat bar should show `llm-wiki: connected` with tool/resource/prompt counts.
- Codex / Hermes: invoke any tool by name (e.g. `schema`) and check the response.

If nothing appears, double-check that `--graph` points at an existing `.llm-wiki/graph.json` — the server now validates this on startup and on every tool call, so you'll see a clear error message instead of a silent 500.

## Where this fits

The MCP server is the **read interface** to the typed graph. For the **write path** (ingesting sources, recompiling, refreshing companion tools like RAG-Anything or Understand-Anything) use the CLI directly. The two are decoupled: the CLI updates `.llm-wiki/`, the MCP server reads whatever's there on the next tool call.
