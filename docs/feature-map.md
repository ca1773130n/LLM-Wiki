# Feature Map

This document summarizes the features currently implemented in LLM-Wiki.

## CLI and installation

- Installable Python package via `pyproject.toml`.
- Console commands:
  - `llm_wiki`
  - `llm-wiki`
  - `llm_wiki_mcp`
- `scripts/install.sh` for `curl | bash` installation.
- Editable installs by default for fast local development.

## Extraction

- Deterministic research-note extractor with controlled node/edge vocabularies.
- Claude CLI/OAuth extractor for higher-quality structured extraction without API keys.
- Selective Claude routing by glob and budget limit.
- Deterministic development-code extractor for Python projects.
- Batch ingest with content hashing and `--changed-only` support.
- Malformed UTF-8 tolerant source reading.

## Graph governance

- Controlled `ResearchNodeType` list.
- Controlled edge type whitelist.
- Validation to reject schema drift.
- Alias canonicalization.
- Review queue for ambiguous near-duplicate nodes.
- Review decisions template and merge/keep-separate workflow.
- Corpus trend summarization from per-file graphs.

## Persistence and reports

- Graph JSON export.
- SQLite graph store.
- Optional Kuzu graph store.
- Graph report with counts, evidence coverage, orphan nodes, date buckets, and alias-heavy nodes.
- Competitive report describing absorbed ideas from MegaMem, Graphiti/Zep, MCP graph servers, and agentic RAG systems.

## Project-local workflow

- `llm_wiki project init`
- `llm_wiki project ingest`
- `llm_wiki project compile`
- `llm_wiki project mcp-config`
- `llm_wiki project build-site`
- `llm_wiki project serve`
- `llm_wiki project export-agent-harness`
- `llm_wiki project export-obsidian`
- `llm_wiki project export-graphiti`
- `llm_wiki project sync-graphiti`

## Frontend

- Static site generation into `.llm-wiki/site/`.
- Research/development split view.
- Client-side search index.
- `llms.txt` for agent-readable site context.
- No npm or bundler dependency.

## Obsidian

- Ready-to-open vault export.
- `.obsidian/app.json` and graph settings.
- Markdown projection.
- `raw/assets/` structure.
- `_meta/dashboard.md` with Dataview query.

## Agent harnesses

Generated target files for:

- Claude Code: `CLAUDE.md`, `.claude/settings.json`
- Codex: `AGENTS.md`, `mcp.toml`
- Gemini: `GEMINI.md`, `.gemini/settings.json`
- Kiro: steering and MCP settings
- Cursor: project rules and MCP config
- OpenCode: `AGENTS.md`, `opencode.json`

## Graphiti / temporal facts

- Temporal fact projection with provenance, currentness, confidence, and invalidation fields.
- Dependency-free Graphiti episode JSONL export.
- `sync-graphiti --dry-run` smoke without Graphiti installed.
- Optional live sync with `graphiti_core` and Neo4j.

## Cognee

- Cognee JSONL bundle (`nodes.jsonl`, `edges.jsonl`, `manifest.json`).
- Optional add-only direct import.
- Optional Codex CLI/OAuth-backed Cognee cognify adapter.
- Deterministic and Ollama embedding adapter paths for no-API-key smoke/quality workflows.

## Tests

The current suite covers:

- ontology guardrails;
- deterministic extraction;
- Claude CLI wrapper parsing/validation;
- selective Claude routing;
- canonicalization/review workflow;
- batch ingest;
- reports;
- SQLite/Kuzu persistence;
- Cognee bundles/import patches;
- Graphiti export/sync dry-run;
- project CLI workflow;
- agent harness export;
- Obsidian export;
- frontend generation;
- package install and installer contract.
