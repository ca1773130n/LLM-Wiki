# Architecture

LLM-Wiki turns source material into a controlled, typed knowledge graph and then projects that graph into formats humans and agents can use.

```text
raw sources
  → deterministic or selective LLM extraction
  → validated ResearchGraph / code graph
  → canonicalization and review queues
  → durable graph artifacts
  → markdown, Obsidian, static site, agent harnesses, MCP, Cognee, Graphiti episodes
```

## Design principles

1. **Raw evidence stays raw.** Source markdown, papers, docs, and code files are treated as evidence. Generated wiki pages and frontend files are projections, not the source of truth.
2. **The graph schema is controlled in code.** LLM output is never allowed to invent arbitrary ontology labels such as `Entity`, `technology`, or `feature`.
3. **Research and development share a pipeline but keep distinct ontology slices.** Papers and claims are modeled differently from source files and functions, while both can be served through the same graph/frontend/MCP layer.
4. **No API-key dependency by default.** Deterministic extraction, CLI/OAuth enrichment, local embeddings, and dependency-free exports are preferred.
5. **Every projection should be reproducible.** `project compile` and `project build-site` can regenerate local artifacts from source files and config.

## Research graph slice

The research slice models literature intelligence:

- `Paper`, `Repository`, `Project`, `Model`
- `ResearchField`, `ResearchTopic`, `ProblemArea`, `ApproachFamily`, `Trend`
- `Dataset`, `Benchmark`, `Metric`, `Result`
- `MethodologicalConcept`, `MathematicalConcept`, `Algorithm`, `ArchitecturePattern`, `Task`, `Capability`
- `Claim`, `ContributionClaim`, `PerformanceClaim`, `ComparisonClaim`, `LimitationClaim`, `CausalClaim`, `OpenQuestion`
- `EvidenceSpan`

Representative edges include:

- `uses`
- `introduces`
- `extends`
- `improves_on`
- `compares_against`
- `addresses`
- `evaluated_on`
- `reports_result`
- `supports_claim`
- `evidenced_by`
- `implemented_in`
- `rising_in`

## Development-code graph slice

The development slice models code projects without pretending source code is the same as paper text:

- `CodeProject`
- `SourceFile`
- `CodeModule`
- `CodeClass`
- `CodeFunction`
- `Dependency`

Representative edges include:

- `contains`
- `defines`
- `imports`
- `calls`
- `documents`

The deterministic Python extractor parses source files with `ast`, records source paths, hashes, classes, functions/methods, and import dependencies.

## Project workspace

Every initialized project owns a local `.llm-wiki/` workspace:

```text
.llm-wiki/
  config.json                 # project name, source kind, source list
  graph.json                  # validated graph JSON
  manifest.json               # changed-only content hashes
  sqlite.db                   # SQLite persistence
  temporal_facts.jsonl        # Graphiti-style temporal fact projection
  graphiti_episodes.jsonl     # dependency-free Graphiti episode export
  report.md                   # graph quality/summary report
  competitive_report.md       # comparison against related memory/KG systems
  markdown_projection/        # human-readable generated markdown
  obsidian_vault/             # ready-to-open Obsidian projection
  agent_harness/              # coding-agent context/config files
  site/                       # static frontend
  cognee_bundle/              # nodes/edges JSONL bundle for Cognee
```

## Frontend

The frontend is intentionally static and dependency-light:

- `index.html` — search and graph browser UI.
- `graph.json` — graph payload for humans and custom tooling.
- `search-index.json` — lightweight client-side search data.
- `llms.txt` — agent-readable summary and entrypoint.

This mirrors the useful part of Pratiyush/llm-wiki's approach: build artifacts that are easy for both humans and language models to inspect.

## MCP server

`llm_wiki_mcp` / `python3 -m llm_wiki.mcp_server` serves a compiled graph over stdio JSON-RPC/MCP with tools such as:

- `schema`
- `graph_summary`
- `search_nodes`
- `node_context`
- `search_facts`
- `timeline`

## External projections

- **Obsidian:** `.obsidian` defaults, graph coloring, markdown projection, Dataview dashboard.
- **Agent harnesses:** Claude Code, Codex, Gemini, Kiro, Cursor, and OpenCode context/config files.
- **Graphiti:** dependency-free episode JSONL plus optional live sync.
- **Cognee:** nodes/edges JSONL bundle and optional direct add/cognify workflows.
- **SQLite/Kuzu:** local graph persistence for inspection and downstream tooling.
