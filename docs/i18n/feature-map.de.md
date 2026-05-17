# Feature-Map

<!-- translations:start -->
<p align="center"><a href="../feature-map.md">English</a> · <a href="feature-map.ko.md">한국어</a> · <a href="feature-map.zh.md">中文</a> · <a href="feature-map.ja.md">日本語</a> · <a href="feature-map.ru.md">Русский</a> · <a href="feature-map.es.md">Español</a> · <a href="feature-map.fr.md">Français</a></p>
<!-- translations:end -->
Dieses Dokument fasst die aktuell in Tesserae implementierten Features zusammen, mit Status, Source-Dateien und Verweisen darauf, wo sie dokumentiert sind.

Status-Legende: ✅ ausgeliefert · ⚠ in Arbeit / teilweise.

## Frontend-Redesign — April 2026

Ein dokument-zentriertes, hierarchisches Wiki ersetzt den alten Graph-Dump. Siehe [`docs/frontend-redesign.md`](frontend-redesign.de.md) für die Route-für-Route-Tour und [`docs/architecture.md`](architecture.de.md) für das Drei-Schichten-Modell.

### Wiki-Layer (L2 Markdown)

| Feature | Status | Source | Doc-Anker |
|---|---|---|---|
| `WikiPageStore` (idempotente Body-Hash-Writes, Frontmatter-Parser) | ✅ | [`tesserae/wiki_store.py`](../tesserae/wiki_store.py) | [architecture.md § Module map](architecture.de.md#wiki--synthese-l2) |
| `WikiLayerProjector` — eine md-Seite pro Wiki-Layer-Knoten | ✅ | [`tesserae/wiki_projector.py`](../tesserae/wiki_projector.py) | [architecture.md § Pipeline](architecture.de.md#pipeline) |
| `sources/`-Seiten | ✅ | `wiki_projector.py` | [frontend-redesign.md § Sources](frontend-redesign.de.md#sources) |
| `concepts/`-Seiten | ✅ | `wiki_projector.py` | [frontend-redesign.md § Concepts](frontend-redesign.de.md#concepts) |
| `entities/`-Seiten | ✅ | `wiki_projector.py` | [frontend-redesign.md § Entities](frontend-redesign.de.md#entities) |
| `papers/`-Seiten | ✅ | `wiki_projector.py` | [frontend-redesign.md § Papers](frontend-redesign.de.md#papers) |
| `repos/`-Seiten | ✅ | `wiki_projector.py` | [frontend-redesign.md § Repos](frontend-redesign.de.md#repos) |
| `topics/`-Seiten | ✅ | `wiki_projector.py` | [frontend-redesign.md § Topics](frontend-redesign.de.md#topics) |
| `questions/`-Seiten (Open Questions) | ✅ | `wiki_projector.py` | [frontend-redesign.md § Questions](frontend-redesign.de.md#questions) |
| `syntheses/`-Seiten | ✅ | [`tesserae/synthesis.py`](../tesserae/synthesis.py) | [frontend-redesign.md § Syntheses](frontend-redesign.de.md#syntheses) |

### Synthese-Kinds (L2 → derived)

`SynthesisProjector` produziert sieben deterministische Templates und fügt `Synthesis`-Knoten + `synthesizes`/`summarizes`-Kanten zurück in den Graph.

| Kind | Status | Source | Hinweise |
|---|---|---|---|
| `pulse` (eine global, treibt `/`) | ✅ | `synthesis.py` | Bei jedem Compile neu gebaut. |
| `daily_digest` | ✅ | `synthesis.py` | Eine pro `data/research/daily/<date>/`. |
| `weekly` | ✅ | `synthesis.py` | Eine pro `data/research/weekly/<iso-week>/`. |
| `topic` | ✅ | `synthesis.py` | Eine pro `ResearchTopic`-/`ApproachFamily`-Cluster ≥ 3 Papers. |
| `comparison` | ✅ | `synthesis.py` | Eine pro Paar von `ApproachFamily`, die auf derselben Task konkurrieren. |
| `field_overview` | ✅ | `synthesis.py` | Eine pro `ResearchField`. |
| LLM-aufgewertete Summaries (env-flag) | ⚠ | nur Hook | Heuristik-Baseline geliefert; Hook `TESSERAE_SYNTHESIS_LLM=1` als Stub belassen. |

### Static-Site-Routen

| Route | Status | Source | Hinweise |
|---|---|---|---|
| `/` (Home, Hero-Pulse) | ✅ | [`tesserae/site/pages.py`](../tesserae/site/pages.py) `render_home` | Stat-Row + kuratierte Einstiegspunkte + Recent Activity. |
| `/sources/`, `/sources/<slug>.html` | ✅ | `pages.py::render_sources_index`, `render_source_detail` | |
| `/concepts/`, `/concepts/<slug>.html` | ✅ | `pages.py::render_concepts_index`, `render_concept_detail` | |
| `/entities/`, `/entities/<slug>.html` | ✅ | `pages.py::render_entities_index`, `render_entity_detail` | |
| `/papers/`, `/papers/<slug>.html` | ✅ | `pages.py::render_papers_index`, `render_paper_detail` | |
| `/repos/`, `/repos/<slug>.html` | ✅ | `pages.py::render_repos_index`, `render_repo_detail` | |
| `/topics/`, `/topics/<slug>.html` | ✅ | `pages.py::render_topics_index`, `render_topic_detail` | |
| `/syntheses/`, `/syntheses/<slug>.html` | ✅ | `pages.py::render_syntheses_index`, `render_synthesis_detail` | |
| `/questions/`, `/questions/<slug>.html` | ✅ | `pages.py::render_questions_index`, `render_question_detail` | |
| `/timeline/` | ✅ | `pages.py::render_timeline` | Heatmap + Tagesliste + Synthesis-Rail. |
| `/timeline/<YYYY-MM-DD>.html` (Per-Day-Detail) | ⚠ | n/a yet | Heatmap-Zellen verlinken interimsweise auf die Source-Seite `digest.md` des Tages. Subagent P verdrahtet die Per-Day-Detailseiten durch `StaticSiteBuilder`. |
| `/graph/` (interaktiv 2D + 3D) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, Hover-Tooltips, Edge-Labels, Cursor-verankerter Zoom. |
| `/about.html` | ✅ | `pages.py::render_about` | Schema, Build-Info. |

### KI-freundliche Exporte

| Artefakt | Status | Source | Zweck |
|---|---|---|---|
| Per-Page-`<page>.txt`-Sibling | ✅ | [`tesserae/site/exports.py`](../tesserae/site/exports.py) `write_siblings` | Plain-Text-View einer Seite (keine Nav, kein Styling). |
| Per-Page-`<page>.json`-Sibling | ✅ | `exports.py::write_siblings` | `{title, kind, body, body_text, links, source_path, frontmatter}`. |
| `llms.txt` | ✅ | `exports.py::render_llms_txt` | llmstxt.org-Kurzindex. |
| `llms-full.txt` | ✅ | `exports.py::render_llms_full_txt` | Jeder Page-Body, gedeckelt bei 5 MB. |
| `graph.jsonld` | ✅ | `exports.py::render_graph_jsonld` | schema.org `Dataset`, nur Wiki-Layer-Knoten. |
| `graph.json` | ✅ | `__init__.py::write_site` | Volles Graph-Payload (inkl. Code-Knoten für Tooling). |
| `search-index.json` | ✅ | [`tesserae/site/search.py`](../tesserae/site/search.py) | Palette + Page-Search; nur Wiki-Layer-Kinds. |
| `sitemap.xml` | ✅ | `exports.py::render_sitemap_xml` | Jede emittierte Route, `lastmod` aus dem Frontmatter. |
| `rss.xml` | ✅ | `exports.py::render_rss_xml` | Letzte 30 Syntheses. |
| `robots.txt` | ✅ | `exports.py::render_robots_txt` | Permissiv — crawl + index. |
| `ai-readme.md` | ✅ | `exports.py::render_ai_readme` | Maschinenlesbare Site-Map. |
| `manifest.json` | ✅ | `__init__.py::_manifest` | sha256 + Size für jede emittierte Datei (Idempotenz-Harness). |

### Visuelles Design + UX

| Feature | Status | Source | Hinweise |
|---|---|---|---|
| Design Tokens (Light + Dark Themes, Terracotta-Akzent) | ✅ | [`tesserae/site/tokens.py`](../tesserae/site/tokens.py) | Ein CSS-Bundle in `assets/style.css`. |
| Theme-Toggle (persistent, kein Flash) | ✅ | [`tesserae/site/js.py`](../tesserae/site/js.py) | `data-theme="dark"` im `localStorage`, vor Paint angewendet. |
| Search-Palette (`cmd+k` / `ctrl+k` / `/`) | ✅ | `js.py` | Fuzzy-Match über `search-index.json`; Recent-Page-Liste. |
| Sticky-Right-TOC | ✅ | `pages.py` + `tokens.py` | Nur Desktop; Mobile-Drawer via `<details>`. |
| Activity-Heatmap mit Monats- + Wochentag-Labels | ✅ | `components.py::heatmap_svg` | 26-Wochen-SVG, Zellen verlinken auf `digest.md` des Tages. |
| Sparkline (pro Concept/Entity) | ✅ | `components.py::sparkline_svg` | Wöchentliche Mention-Counts, letzte 12 Wochen. |
| Mobile-Shell (Drawer-Rail, Bottom-Nav, fluide Schrift) | ✅ | `tokens.py` + `pages.py` | Touch-Hit-Targets ≥ 44 px. |
| Page Transitions (120 ms Opacity, prefers-reduced-motion) | ✅ | `tokens.py` | |
| 3D + 2D Graph-View (Hover, Edge-Labels, Cursor-verankerter Zoom) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, als CDN-Snapshot vendored. |
| Per-Page AI-Siblings-Footer | ✅ | `components.py::ai_siblings_footer` | Inline-Links zur `.txt` und `.json` der aktuellen Seite. |
| Harness-Session-History-Seiten | ✅ | [`tesserae/harness_sessions.py`](../tesserae/harness_sessions.py) + [`tesserae/site/sessions.py`](../tesserae/site/sessions.py) | Expliziter Claude-Code/Codex-Import; `/sessions/`-Index- und Detailseiten mit Markdown-Turns, Left-Turn-Rail, eingeklapptem Tool-Use und Such-Einträgen. |

### Pipeline + CLI

| Feature | Status | Source | Hinweise |
|---|---|---|---|
| `project compile` ruft Synthese + Wiki + Site in Reihenfolge auf | ✅ | [`tesserae/project.py`](../tesserae/project.py) | Phase 3 des Redesign-Plans. |
| `project build-site` standalone | ✅ | `project.py` + [`tesserae/cli.py`](../tesserae/cli.py) | Liest `wiki/` + `graph.json`, schreibt `site/`. |
| `project serve` lokaler HTTP-Server | ✅ | `cli.py` | Plain Stdlib-Server. |
| `project deploy` → GitHub Pages | ✅ | [`tesserae/deploy.py`](../tesserae/deploy.py) | Worktree-Push nach `gh-pages`; optional `--enable-pages` via `gh`-CLI. `--build`, `--dry-run`, `--branch`, `--remote`, `--force`. |
| `project sessions discover/import/list` | ✅ | [`tesserae/harness_sessions.py`](../tesserae/harness_sessions.py) + `cli.py` | Inbound-Session-Historie für Claude Code/Codex; Discovery ist explizit und scoped auf das Project-Working-Directory. |
| `project watch` Rebuild-on-Change | ⚠ | [`tesserae/cli.py`](../tesserae/cli.py) | Subagent R schließt den Polling-Watcher ab — Arg-Fläche `--interval`, `--debounce`, `--once`, `--paths`, `--quiet` steht; der Rebuild-Loop-Body landet in dieser Runde. |

## Vorhandene Features (unverändert übernommen)

### CLI und Installation

- ✅ Installierbares Python-Package via `pyproject.toml`.
- ✅ Console-Commands: `tesserae`, `tesserae`, `tesserae_mcp`.
- ✅ `scripts/install.sh` für `curl | bash`-Installation.
- ✅ Editable Installs als Default für schnelle lokale Entwicklung.

### Extraktion

- ✅ Deterministischer Research-Note-Extraktor mit kontrollierten Node-/Edge-Vokabularien.
- ✅ Claude-CLI-/OAuth-Extraktor für höhere Qualität strukturierter Extraktion ohne API-Keys.
- ✅ Selektives Claude-Routing per Glob und Budget-Limit.
- ✅ Deterministischer Development-Code-Extraktor für Python-Projekte.
- ✅ Batch-Ingest mit Content-Hashing und `--changed-only`-Support.
- ✅ Tolerantes Lesen malformed UTF-8 Quellen.

### Graph-Governance

- ✅ Kontrollierte `ResearchNodeType`-Liste — enthält jetzt `SYNTHESIS`.
- ✅ Kontrollierte Edge-Type-Whitelist — enthält jetzt `synthesizes`, `summarizes`.
- ✅ Validierung, die Schema-Drift ablehnt.
- ✅ Alias-Kanonisierung.
- ✅ Review-Queue für mehrdeutige Near-Duplicate-Knoten.
- ✅ Review-Decisions-Template und Merge/Keep-Separate-Workflow.
- ✅ Korpus-Trend-Zusammenfassung aus Per-File-Graphen.

### Persistenz und Reports

- ✅ Graph-JSON-Export.
- ✅ SQLite-Graph-Store.
- ✅ Optionaler Kuzu-Graph-Store.
- ✅ Graph-Report mit Counts, Evidence-Coverage, Orphan-Nodes, Date-Buckets, Alias-Heavy-Nodes.
- ✅ Competitive-Report, der absorbierte Ideen aus MegaMem, Graphiti/Zep, MCP-Graph-Servern und Agentic RAG beschreibt.

### Projekt-lokaler Workflow

- ✅ `tesserae project init`
- ✅ `tesserae project ingest`
- ✅ `tesserae project compile`
- ✅ `tesserae project mcp-config`
- ✅ `tesserae project build-site`
- ✅ `tesserae project serve`
- ✅ `tesserae project deploy` (neu — GitHub Pages)
- ✅ `tesserae project sessions discover/import/list` (expliziter Import lokaler Agent-Historie)
- ⚠ `tesserae project watch` (in Arbeit)
- ✅ `tesserae project export-agent-harness`
- ✅ `tesserae project export-obsidian`
- ✅ `tesserae project export-graphiti`
- ✅ `tesserae project sync-graphiti`

### Obsidian

- ✅ Bereit-zu-öffnen-Vault-Export.
- ✅ `.obsidian/app.json` und Graph-Settings.
- ✅ Markdown-Projektion.
- ✅ `raw/assets/`-Struktur.
- ✅ `_meta/dashboard.md` mit Dataview-Query.

### Agent-Harnesses

Generierte Zieldateien für:

- ✅ Claude Code: `CLAUDE.md`, `.claude/settings.json`
- ✅ Codex: `AGENTS.md`, `mcp.toml`
- ✅ Gemini: `GEMINI.md`, `.gemini/settings.json`
- ✅ Kiro: Steering- und MCP-Settings
- ✅ Cursor: Project-Rules und MCP-Config
- ✅ OpenCode: `AGENTS.md`, `opencode.json`

### Graphiti / temporale Fakten

- ✅ Temporal-Fact-Projektion mit Provenance-, Currentness-, Confidence- und Invalidation-Feldern.
- ✅ Dependency-freier Graphiti-Episode-JSONL-Export.
- ✅ `sync-graphiti --dry-run`-Smoke ohne installiertes Graphiti.
- ✅ Optionaler Live-Sync mit `graphiti_core` und Neo4j.

### Cognee

- ✅ Cognee-JSONL-Bundle (`nodes.jsonl`, `edges.jsonl`, `manifest.json`).
- ✅ Optionaler Add-only-Direkt-Import.
- ✅ Optionaler Codex-CLI/OAuth-gestützter Cognee-Cognify-Adapter.
- ✅ Deterministische und Ollama-Embedding-Adapter-Pfade für No-API-Key-Smoke-/Quality-Workflows.

### MCP-Server

- ✅ `tesserae_mcp` / `python3 -m tesserae.mcp_server` über Stdio-JSON-RPC.
- ✅ Tools: `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline`.
- ✅ Multi-Project-Registry.

## Tests

Die aktuelle Suite deckt ab:

- ✅ Ontologie-Guardrails (inkl. neuem `Synthesis`-Knoten + `synthesizes`-/`summarizes`-Kanten);
- ✅ deterministische Extraktion;
- ✅ Claude-CLI-Wrapper-Parsing/Validierung;
- ✅ selektives Claude-Routing;
- ✅ Kanonisierungs-/Review-Workflow;
- ✅ Batch-Ingest;
- ✅ Reports;
- ✅ SQLite-/Kuzu-Persistenz;
- ✅ Cognee-Bundles/Import-Patches;
- ✅ Graphiti-Export/Sync-Dry-Run;
- ✅ Project-CLI-Workflow;
- ✅ Agent-Harness-Export;
- ✅ Obsidian-Export;
- ✅ Frontend-Generation + Link-Integrität (kein `nodes/codeclass-*.html`);
- ✅ Wiki-Store-Idempotenz;
- ✅ Synthesis-Projector-Golden + Idempotenz;
- ✅ Site-Components, Pages, Exports, Relevance;
- ✅ AI-Sibling-Shape (`.txt` + `.json` pro Seite);
- ✅ End-to-End-Compile-twice-Idempotenz;
- ✅ Package-Install und Installer-Contract.
