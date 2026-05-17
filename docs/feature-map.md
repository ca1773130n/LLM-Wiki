# Feature Map

<!-- translations:start -->
<p align="center"><a href="i18n/feature-map.ko.md">한국어</a> · <a href="i18n/feature-map.zh.md">中文</a> · <a href="i18n/feature-map.ja.md">日本語</a> · <a href="i18n/feature-map.ru.md">Русский</a> · <a href="i18n/feature-map.es.md">Español</a> · <a href="i18n/feature-map.fr.md">Français</a> · <a href="../i18n/feature-map.de.md">Deutsch</a></p>
<!-- translations:end -->
This document summarizes the features currently implemented in Tesserae, with status, source files, and where they're documented.

Status legend: ✅ shipped · ⚠ in-progress / partial.

## Frontend redesign — April 2026

Document-first, hierarchical wiki replaces the old graph dump. See [`docs/frontend-redesign.md`](frontend-redesign.md) for the route-by-route tour and [`docs/architecture.md`](architecture.md) for the three-layer model.

### Wiki layer (L2 markdown)

| Feature | Status | Source | Doc anchor |
|---|---|---|---|
| `WikiPageStore` (idempotent body-hash writes, frontmatter parser) | ✅ | [`tesserae/wiki_store.py`](../tesserae/wiki_store.py) | [architecture.md § Module map](architecture.md#wiki--synthesis-l2) |
| `WikiLayerProjector` — one md page per wiki-layer node | ✅ | [`tesserae/wiki_projector.py`](../tesserae/wiki_projector.py) | [architecture.md § Pipeline](architecture.md#pipeline) |
| `sources/` pages | ✅ | `wiki_projector.py` | [frontend-redesign.md § Sources](frontend-redesign.md#sources) |
| `concepts/` pages | ✅ | `wiki_projector.py` | [frontend-redesign.md § Concepts](frontend-redesign.md#concepts) |
| `entities/` pages | ✅ | `wiki_projector.py` | [frontend-redesign.md § Entities](frontend-redesign.md#entities) |
| `papers/` pages | ✅ | `wiki_projector.py` | [frontend-redesign.md § Papers](frontend-redesign.md#papers) |
| `repos/` pages | ✅ | `wiki_projector.py` | [frontend-redesign.md § Repos](frontend-redesign.md#repos) |
| `topics/` pages | ✅ | `wiki_projector.py` | [frontend-redesign.md § Topics](frontend-redesign.md#topics) |
| `questions/` pages (Open questions) | ✅ | `wiki_projector.py` | [frontend-redesign.md § Questions](frontend-redesign.md#questions) |
| `syntheses/` pages | ✅ | [`tesserae/synthesis.py`](../tesserae/synthesis.py) | [frontend-redesign.md § Syntheses](frontend-redesign.md#syntheses) |

### Synthesis kinds (L2 → derived)

`SynthesisProjector` produces seven deterministic templates and adds `Synthesis` nodes + `synthesizes` / `summarizes` edges back into the graph.

| Kind | Status | Source | Notes |
|---|---|---|---|
| `pulse` (one global, drives `/`) | ✅ | `synthesis.py` | Rebuilt every compile. |
| `daily_digest` | ✅ | `synthesis.py` | One per `data/research/daily/<date>/`. |
| `weekly` | ✅ | `synthesis.py` | One per `data/research/weekly/<iso-week>/`. |
| `topic` | ✅ | `synthesis.py` | One per `ResearchTopic` / `ApproachFamily` cluster ≥ 3 papers. |
| `comparison` | ✅ | `synthesis.py` | One per pair of `ApproachFamily` competing on the same task. |
| `field_overview` | ✅ | `synthesis.py` | One per `ResearchField`. |
| LLM-upgraded summaries (env-flagged) | ⚠ | hook only | Heuristic baseline ships; `TESSERAE_SYNTHESIS_LLM=1` hook left as a stub. |

### Static site routes

| Route | Status | Source | Notes |
|---|---|---|---|
| `/` (home, hero pulse) | ✅ | [`tesserae/site/pages.py`](../tesserae/site/pages.py) `render_home` | Stat row + curated entry points + recent activity. |
| `/sources/`, `/sources/<slug>.html` | ✅ | `pages.py::render_sources_index`, `render_source_detail` | |
| `/concepts/`, `/concepts/<slug>.html` | ✅ | `pages.py::render_concepts_index`, `render_concept_detail` | |
| `/entities/`, `/entities/<slug>.html` | ✅ | `pages.py::render_entities_index`, `render_entity_detail` | |
| `/papers/`, `/papers/<slug>.html` | ✅ | `pages.py::render_papers_index`, `render_paper_detail` | |
| `/repos/`, `/repos/<slug>.html` | ✅ | `pages.py::render_repos_index`, `render_repo_detail` | |
| `/topics/`, `/topics/<slug>.html` | ✅ | `pages.py::render_topics_index`, `render_topic_detail` | |
| `/syntheses/`, `/syntheses/<slug>.html` | ✅ | `pages.py::render_syntheses_index`, `render_synthesis_detail` | |
| `/questions/`, `/questions/<slug>.html` | ✅ | `pages.py::render_questions_index`, `render_question_detail` | |
| `/timeline/` | ✅ | `pages.py::render_timeline` | Heatmap + day list + synthesis rail. |
| `/timeline/<YYYY-MM-DD>.html` (per-day detail) | ⚠ | n/a yet | Heatmap cells link to the day's `digest.md` source page as an interim. Subagent P is wiring the per-day detail pages through `StaticSiteBuilder`. |
| `/graph/` (interactive 2D + 3D) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, hover tooltips, edge labels, cursor-anchored zoom. |
| `/about.html` | ✅ | `pages.py::render_about` | Schema, build info. |

### AI-friendly exports

| Artifact | Status | Source | Purpose |
|---|---|---|---|
| Per-page `<page>.txt` sibling | ✅ | [`tesserae/site/exports.py`](../tesserae/site/exports.py) `write_siblings` | Plain-text view of one page (no nav, no styling). |
| Per-page `<page>.json` sibling | ✅ | `exports.py::write_siblings` | `{title, kind, body, body_text, links, source_path, frontmatter}`. |
| `llms.txt` | ✅ | `exports.py::render_llms_txt` | llmstxt.org short index. |
| `llms-full.txt` | ✅ | `exports.py::render_llms_full_txt` | Every page body, capped at 5 MB. |
| `graph.jsonld` | ✅ | `exports.py::render_graph_jsonld` | schema.org `Dataset`, wiki-layer nodes only. |
| `graph.json` | ✅ | `__init__.py::write_site` | Full graph payload (incl. code nodes for tooling). |
| `search-index.json` | ✅ | [`tesserae/site/search.py`](../tesserae/site/search.py) | Palette + page search; wiki-layer kinds only. |
| `sitemap.xml` | ✅ | `exports.py::render_sitemap_xml` | Every emitted route, `lastmod` from frontmatter. |
| `rss.xml` | ✅ | `exports.py::render_rss_xml` | Last 30 syntheses. |
| `robots.txt` | ✅ | `exports.py::render_robots_txt` | Permissive — crawl + index. |
| `ai-readme.md` | ✅ | `exports.py::render_ai_readme` | Machine-readable site map. |
| `manifest.json` | ✅ | `__init__.py::_manifest` | sha256 + size for every emitted file (idempotence harness). |

### Visual design + UX

| Feature | Status | Source | Notes |
|---|---|---|---|
| Design tokens (light + dark themes, terracotta accent) | ✅ | [`tesserae/site/tokens.py`](../tesserae/site/tokens.py) | One CSS bundle in `assets/style.css`. |
| Theme toggle (persisted, no flash) | ✅ | [`tesserae/site/js.py`](../tesserae/site/js.py) | `data-theme="dark"` in `localStorage`, applied pre-paint. |
| Search palette (`cmd+k` / `ctrl+k` / `/`) | ✅ | `js.py` | Fuzzy match over `search-index.json`; recent-page list. |
| Sticky right TOC | ✅ | `pages.py` + `tokens.py` | Desktop only; mobile drawer via `<details>`. |
| Activity heatmap with month + weekday labels | ✅ | `components.py::heatmap_svg` | 26-week SVG, cells link to the day's `digest.md`. |
| Sparkline (per concept/entity) | ✅ | `components.py::sparkline_svg` | Weekly mention counts, last 12 weeks. |
| Mobile shell (drawer rail, bottom nav, fluid type) | ✅ | `tokens.py` + `pages.py` | Touch hit targets ≥ 44 px. |
| Page transitions (120 ms opacity, prefers-reduced-motion) | ✅ | `tokens.py` | |
| 3D + 2D graph view (hover, edge labels, cursor-anchored zoom) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, vendored as a CDN snapshot. |
| Per-page AI siblings footer | ✅ | `components.py::ai_siblings_footer` | Inline links to the `.txt` and `.json` for the current page. |
| Harness session history pages | ✅ | [`tesserae/harness_sessions.py`](../tesserae/harness_sessions.py) + [`tesserae/site/sessions.py`](../tesserae/site/sessions.py) | Explicit Claude Code/Codex import; `/sessions/` index and detail pages with markdown turns, left turn rail, collapsed tool use, and search entries. |

### Pipeline + CLI

| Feature | Status | Source | Notes |
|---|---|---|---|
| `project compile` calls synthesis + wiki + site in order | ✅ | [`tesserae/project.py`](../tesserae/project.py) | Phase 3 of the redesign plan. |
| `project build-site` standalone | ✅ | `project.py` + [`tesserae/cli.py`](../tesserae/cli.py) | Reads `wiki/` + `graph.json`, writes `site/`. |
| `project serve` local HTTP | ✅ | `cli.py` | Plain stdlib server. |
| `project deploy` → GitHub Pages | ✅ | [`tesserae/deploy.py`](../tesserae/deploy.py) | Worktree push to `gh-pages`; optional `--enable-pages` via `gh` CLI. `--build`, `--dry-run`, `--branch`, `--remote`, `--force`. |
| `project sessions discover/import/list` | ✅ | [`tesserae/harness_sessions.py`](../tesserae/harness_sessions.py) + `cli.py` | Inbound session history for Claude Code/Codex; discovery is explicit and scoped to the project working directory. |
| `project watch` rebuild-on-change | ⚠ | [`tesserae/cli.py`](../tesserae/cli.py) | Subagent R is finishing the polling watcher — `--interval`, `--debounce`, `--once`, `--paths`, `--quiet` arg surface is in place; the rebuild loop body is being landed in this round. |

## Pre-existing features (carried forward unchanged)

### CLI and installation

- ✅ Installable Python package via `pyproject.toml`.
- ✅ Console commands: `tesserae`, `tesserae`, `tesserae_mcp`.
- ✅ `scripts/install.sh` for `curl | bash` installation.
- ✅ Editable installs by default for fast local development.

### Extraction

- ✅ Deterministic research-note extractor with controlled node/edge vocabularies.
- ✅ Claude CLI/OAuth extractor for higher-quality structured extraction without API keys.
- ✅ Selective Claude routing by glob and budget limit.
- ✅ Deterministic development-code extractor for Python projects.
- ✅ Batch ingest with content hashing and `--changed-only` support.
- ✅ Malformed UTF-8 tolerant source reading.

### Graph governance

- ✅ Controlled `ResearchNodeType` list — now includes `SYNTHESIS`.
- ✅ Controlled edge type whitelist — now includes `synthesizes`, `summarizes`.
- ✅ Validation to reject schema drift.
- ✅ Alias canonicalization.
- ✅ Review queue for ambiguous near-duplicate nodes.
- ✅ Review decisions template and merge/keep-separate workflow.
- ✅ Corpus trend summarization from per-file graphs.

### Persistence and reports

- ✅ Graph JSON export.
- ✅ SQLite graph store.
- ✅ Optional Kuzu graph store.
- ✅ Graph report with counts, evidence coverage, orphan nodes, date buckets, alias-heavy nodes.
- ✅ Competitive report describing absorbed ideas from MegaMem, Graphiti/Zep, MCP graph servers, agentic RAG.

### Project-local workflow

- ✅ `tesserae project init`
- ✅ `tesserae project ingest`
- ✅ `tesserae project compile`
- ✅ `tesserae project mcp-config`
- ✅ `tesserae project build-site`
- ✅ `tesserae project serve`
- ✅ `tesserae project deploy` (new — GitHub Pages)
- ✅ `tesserae project sessions discover/import/list` (explicit local agent-history import)
- ⚠ `tesserae project watch` (in-progress)
- ✅ `tesserae project export-agent-harness`
- ✅ `tesserae project export-obsidian`
- ✅ `tesserae project export-graphiti`
- ✅ `tesserae project sync-graphiti`

### Obsidian

- ✅ Ready-to-open vault export.
- ✅ `.obsidian/app.json` and graph settings.
- ✅ Markdown projection.
- ✅ `raw/assets/` structure.
- ✅ `_meta/dashboard.md` with Dataview query.

### Agent harnesses

Generated target files for:

- ✅ Claude Code: `CLAUDE.md`, `.claude/settings.json`
- ✅ Codex: `AGENTS.md`, `mcp.toml`
- ✅ Gemini: `GEMINI.md`, `.gemini/settings.json`
- ✅ Kiro: steering and MCP settings
- ✅ Cursor: project rules and MCP config
- ✅ OpenCode: `AGENTS.md`, `opencode.json`

### Graphiti / temporal facts

- ✅ Temporal fact projection with provenance, currentness, confidence, and invalidation fields.
- ✅ Dependency-free Graphiti episode JSONL export.
- ✅ `sync-graphiti --dry-run` smoke without Graphiti installed.
- ✅ Optional live sync with `graphiti_core` and Neo4j.

### Cognee

- ✅ Cognee JSONL bundle (`nodes.jsonl`, `edges.jsonl`, `manifest.json`).
- ✅ Optional add-only direct import.
- ✅ Optional Codex CLI/OAuth-backed Cognee cognify adapter.
- ✅ Deterministic and Ollama embedding adapter paths for no-API-key smoke/quality workflows.

### MCP server

- ✅ `tesserae_mcp` / `python3 -m tesserae.mcp_server` over stdio JSON-RPC.
- ✅ Tools: `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline`.
- ✅ Multi-project registry.

## Tests

The current suite covers:

- ✅ ontology guardrails (incl. new `Synthesis` node + `synthesizes` / `summarizes` edges);
- ✅ deterministic extraction;
- ✅ Claude CLI wrapper parsing/validation;
- ✅ selective Claude routing;
- ✅ canonicalization/review workflow;
- ✅ batch ingest;
- ✅ reports;
- ✅ SQLite/Kuzu persistence;
- ✅ Cognee bundles/import patches;
- ✅ Graphiti export/sync dry-run;
- ✅ project CLI workflow;
- ✅ agent harness export;
- ✅ Obsidian export;
- ✅ frontend generation + link integrity (no `nodes/codeclass-*.html`);
- ✅ wiki store idempotence;
- ✅ synthesis projector golden + idempotence;
- ✅ site components, pages, exports, relevance;
- ✅ AI-sibling shape (`.txt` + `.json` per page);
- ✅ end-to-end compile-twice idempotence;
- ✅ package install and installer contract.
