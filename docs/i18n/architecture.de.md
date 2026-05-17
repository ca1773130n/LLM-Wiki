# Architektur

<!-- translations:start -->
<p align="center"><a href="../architecture.md">English</a> · <a href="architecture.ko.md">한국어</a> · <a href="architecture.zh.md">中文</a> · <a href="architecture.ja.md">日本語</a> · <a href="architecture.ru.md">Русский</a> · <a href="architecture.es.md">Español</a> · <a href="architecture.fr.md">Français</a></p>
<!-- translations:end -->
LLM-Wiki verwandelt ein Verzeichnis mit Quellmaterial in einen kontrollierten, typisierten Knowledge Graph und projiziert diesen Graph über eine langlebige Markdown-Wiki-Schicht in eine statische, KI-freundliche Website. Das Redesign vom April 2026 hat das System um ein dreischichtiges Modell nach Karpathy reorganisiert: Rohbelege bleiben roh, ein typisierter Graph regiert die Ontologie, und eine Markdown-Wiki-Schicht sitzt zwischen Graph und gerendertem Output. Die statische Site ist jetzt ein *Renderer* dieser Wiki-Schicht statt einer direkten Ausgabe des Graphen, mit der kontrollierten Ontologie in [`llm_wiki/research_graph.py`](../llm_wiki/research_graph.py) als Schema.

## Das dreischichtige Karpathy-Modell

Andrej Karpathys Framing für LLM-freundliche Wissensdatenbanken unterscheidet drei Schichten, jede mit eigener Beständigkeitsgarantie:

| Schicht | Inhalt | Repo-Ort | Owner |
|---|---|---|---|
| L1 — Rohquellen | Die literalen Bytes, die der Nutzer geschrieben oder gesammelt hat. Append-only. | `data/`, `docs/`, in `.llm-wiki/config.json` referenzierte Projektbäume | der Nutzer |
| L2 — Wiki | Typisierte Markdown-Seiten (sources, concepts, entities, papers, repos, topics, syntheses, questions) mit YAML-Frontmatter. Idempotent: bei jedem Compile neu erzeugt, aber nur überschrieben, wenn sich Content-Hashes ändern. | `.llm-wiki/wiki/` | `WikiPageStore`, `WikiLayerProjector`, `SynthesisProjector` |
| L3 — Rendered | Die statische HTML-Site, AI-Sibling-Exporte, Suchindex, Sitemaps, JSON-LD. Wird bei jedem Compile gelöscht und neu geschrieben, aber Byte-stabil über Reruns. | `.llm-wiki/site/` | `StaticSiteBuilder` (`llm_wiki/site/`) |

Das Schema spannt sich über alle drei Schichten als separate Achse: `ResearchGraph` in `graph.json` ist die kontrollierte Ontologie, gegen die L2-Seiten verlinken, und die `ResearchNodeType`-/Edge-Whitelist in [`llm_wiki/research_graph.py`](../llm_wiki/research_graph.py) ist die Source of Truth dafür, welche Typen überhaupt existieren.

Das Redesign hat L2 explizit hinzugefügt. Vor April 2026 wurde die statische Site direkt aus `graph.json` projiziert; die Wiki-Schicht existierte nur innerhalb des Obsidian-Vault-Exports. Sie herauszulösen brachte uns:

- Eine einzige menschenbearbeitbare Fläche (`.llm-wiki/wiki/` in Obsidian oder jedem Markdown-Editor öffnen).
- Idempotente Rebuilds: ein erneutes `project compile` erzeugt null File-Diffs, solange sich der Source-Content nicht geändert hat.
- Ein Evolutions-Log: Synthese-Seiten sammeln sich über die Zeit an und lassen das Projekt sich selbst erzählen.

## Pipeline

```
data/, docs/, src/                                    (L1 raw)
        │
        ▼  project compile  (llm_wiki/project.py)
┌───────────────────────────┐
│ ResearchGraphExtractor    │   deterministic + selective Claude
│ + canonicalization        │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│ ResearchGraph (graph.json)│   schema: research_graph.py
└───────────┬───────────────┘
            │
            ├──▶ WikiLayerProjector   (one page per L1/L2 node)
            ├──▶ SynthesisProjector   (pulse, daily, weekly, topic, …)
            │
            ▼
┌───────────────────────────┐
│ .llm-wiki/wiki/  (L2 md)  │   sources/, concepts/, entities/,
│                            │   papers/, repos/, topics/,
│                            │   syntheses/, questions/
└───────────┬───────────────┘
            │
            ▼  StaticSiteBuilder.write_site
┌───────────────────────────┐
│ .llm-wiki/site/  (L3 html)│   index.html, <kind>/index.html,
│                            │   <kind>/<slug>.html,
│                            │   per-page .txt + .json siblings,
│                            │   llms.txt, llms-full.txt,
│                            │   graph.json, graph.jsonld,
│                            │   search-index.json,
│                            │   sitemap.xml, rss.xml,
│                            │   robots.txt, ai-readme.md,
│                            │   manifest.json
└───────────────────────────┘
```

Jeder Schritt ist inkrementell. Der Graph-Extraktor nutzt die Content-Hashes aus `manifest.json`, um unveränderte Quelldateien zu überspringen. `WikiPageStore.write_page` gibt `False` zurück (und überspringt den Write), wenn der Body-Hash mit dem auf der Festplatte übereinstimmt. `StaticSiteBuilder` löscht und überschreibt `.llm-wiki/site/`, aber sein Output ist deterministisch — siehe „Idempotenz-Story“ unten.

## Modul-Karte

### Wiki + Synthese (L2)

| Modul | Verantwortung |
|---|---|
| [`llm_wiki/wiki_store.py`](../llm_wiki/wiki_store.py) | `WikiPage`-Dataclass, `WikiPageStore` für Filesystem-I/O. Stdlib-only YAML-Subset-Frontmatter-Parser. Body-Hash-Idempotenz. |
| [`llm_wiki/wiki_projector.py`](../llm_wiki/wiki_projector.py) | `WikiLayerProjector`: bildet jeden `ResearchGraph`-Knoten eines Wiki-Layer-Typs auf eine Markdown-Seite im richtigen `kind/`-Ordner ab. |
| [`llm_wiki/synthesis.py`](../llm_wiki/synthesis.py) | `SynthesisProjector`: deterministische Templates für pulse, daily_digest, weekly, topic, comparison, field_overview. Fügt `Synthesis`-Knoten und `synthesizes`-/`summarizes`-Kanten zurück in den Graph. |

### Graph + Ontologie

| Modul | Verantwortung |
|---|---|
| [`llm_wiki/research_graph.py`](../llm_wiki/research_graph.py) | `ResearchNodeType`-Enum (inkl. `SYNTHESIS`), Edge-Type-Whitelist (inkl. `synthesizes`, `summarizes`), Validierung. |
| [`llm_wiki/canonicalization.py`](../llm_wiki/canonicalization.py) | Alias-Kanonisierung + Near-Duplicate-Review-Queue. |
| [`llm_wiki/code_graph.py`](../llm_wiki/code_graph.py) | Deterministischer Python-AST-Extraktor für den Development-Slice. |
| [`llm_wiki/llm_extractor.py`](../llm_wiki/llm_extractor.py) | Selektiver Extraktor via Claude CLI/OAuth. |

### Site-Renderer (L3)

| Modul | Verantwortung |
|---|---|
| [`llm_wiki/site/__init__.py`](../llm_wiki/site/__init__.py) | `StaticSiteBuilder.write_site`: löscht und baut die Site neu, läuft jede Route durch, gibt Exporte + AI-Siblings + Manifest aus. |
| [`llm_wiki/site/pages.py`](../llm_wiki/site/pages.py) | Ein Renderer pro Route (home, indexes, detail pages, timeline, graph, about). `SiteContext` trägt vorberechnete Indizes, damit Renderer pur bleiben. |
| [`llm_wiki/site/components.py`](../llm_wiki/site/components.py) | HTML-Primitive: `breadcrumbs`, `card`, `badge`, `node_table`, `edge_list`, `sparkline_svg`, `heatmap_svg`, `toc`, `page_shell`, `ai_siblings_footer`. |
| [`llm_wiki/site/tokens.py`](../llm_wiki/site/tokens.py) | Design Tokens — CSS-Variablen, Light- + Dark-Themes, Layout, Typografie, hier werden alle Komponenten gestylt. |
| [`llm_wiki/site/js.py`](../llm_wiki/site/js.py) | Client-JS-Bundle: Search-Palette, Theme-Toggle, Sigma + 3D-Force-Graph-Ansicht. |
| [`llm_wiki/site/markdown.py`](../llm_wiki/site/markdown.py) | Stdlib-only Markdown-Renderer (Links, Autolinks, Code, Hervorhebungen, Überschriften). Keine externe Abhängigkeit. |
| [`llm_wiki/site/relevance.py`](../llm_wiki/site/relevance.py) | Vier-Signal-Relevanz-Scoring (direkter Link, Source-Overlap, Adamic-Adar, Typ-Affinität), das von jedem `Related`-Abschnitt benutzt wird. |
| [`llm_wiki/site/search.py`](../llm_wiki/site/search.py) | Builder für `search-index.json`. Nur Wiki-Layer-Kinds. |
| [`llm_wiki/site/sessions.py`](../llm_wiki/site/sessions.py) | Session-Index/Detail-Renderer für importierte Harness-Historie: Project-Memory-Summary-Sections, Conversation-Turn-Rail, Markdown-Transcript-Rendering und eingeklappte Tool-Use-Blöcke. |
| [`llm_wiki/site/exports.py`](../llm_wiki/site/exports.py) | `llms.txt`, `llms-full.txt`, `graph.jsonld`, `sitemap.xml`, `rss.xml`, `robots.txt`, `ai-readme.md`, Per-Page-`.txt`/`.json`-Siblings. |

### Pipeline-Orchestrierung

| Modul | Verantwortung |
|---|---|
| [`llm_wiki/project.py`](../llm_wiki/project.py) | `ProjectWiki.compile`: treibt Extraktion → Graph → Wiki-Layer → Site. Besitzt `ProjectPaths` (`config`, `graph`, `manifest`, `wiki`, `site`, etc.). |
| [`llm_wiki/cli.py`](../llm_wiki/cli.py) | Alle `llm_wiki project …`-Subcommands, inklusive `compile`, `build-site`, `serve`, `watch`, `deploy`. |
| [`llm_wiki/deploy.py`](../llm_wiki/deploy.py) | `project deploy`: pusht `.llm-wiki/site/` auf einen `gh-pages`-Branch via Worktree, aktiviert optional Pages via `gh`. |

### Externe Adapter (in dieser Runde unverändert)

| Modul | Verantwortung |
|---|---|
| [`llm_wiki/obsidian_adapter.py`](../llm_wiki/obsidian_adapter.py) | Obsidian-Vault-Projektion (Graph-Coloring, Dataview-Dashboard, Roh-Assets). |
| [`llm_wiki/agent_harness.py`](../llm_wiki/agent_harness.py) | Harness-Exporte für Claude Code / Codex / Gemini / Kiro / Cursor / OpenCode. |
| [`llm_wiki/harness_sessions.py`](../llm_wiki/harness_sessions.py) | Inbound Discovery, Normalisierung und Storage von Claude-Code-/Codex-Sessions unter `.llm-wiki/harness_sessions/` plus redigierte Markdown-Zusammenfassungen. |
| [`llm_wiki/graphiti_adapter.py`](../llm_wiki/graphiti_adapter.py) | Temporal-Fact-JSONL + optionaler Live-Sync mit Graphiti. |
| [`llm_wiki/cognee_adapter.py`](../llm_wiki/cognee_adapter.py) | Cognee-Nodes/Edges-JSONL-Bundle und direkter Add-/Cognify-Pfad. |
| [`llm_wiki/mcp_server.py`](../llm_wiki/mcp_server.py) | MCP-Stdio-Server, der `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline` exponiert. |

## Projekt-Workspace-Layout

```text
.llm-wiki/
  config.json                 project name, source kind, source list
  graph.json                  validated ResearchGraph (incl. Synthesis nodes)
  manifest.json               per-source content hashes (input dedup)
  sqlite.db                   SQLite graph store
  temporal_facts.jsonl        Graphiti-style temporal projection
  graphiti_episodes.jsonl     dependency-free Graphiti episode export
  report.md                   graph quality / summary
  competitive_report.md       comparison vs. MegaMem / Graphiti / others
  markdown_projection/        flat human-readable markdown
  obsidian_vault/             Obsidian projection w/ .obsidian/, raw/assets/
  agent_harness/              Claude Code / Codex / etc. harness files
  harness_sessions/           imported local Claude Code/Codex sessions
  cognee_bundle/              Cognee nodes/edges/manifest JSONL
  wiki/                       L2 markdown wiki — see below
  site/                       L3 static site — see below
```

### `.llm-wiki/wiki/` (L2)

```text
wiki/
  sources/<slug>.md           raw documents from data/ + docs/, with frontmatter
  concepts/<slug>.md          Concept / TechnicalTerm / Algorithm / etc.
  entities/<slug>.md          Model / Dataset / Benchmark / Metric / Org / Person
  papers/<slug>.md            Paper hub
  repos/<slug>.md             Repository / Project / CodeProject
  topics/<slug>.md            ResearchField / ResearchTopic / ApproachFamily / Trend
  syntheses/<slug>.md         pulse, daily_digest, weekly, topic, comparison, field_overview
  questions/<slug>.md         OpenQuestion
```

Jede Datei ist von Hand editierbar; der nächste Compile respektiert Nutzer-Edits, solange der Body-Hash von dem abweicht, was der Projector schreiben würde. (Nur den Body zu bearbeiten gewinnt; das Frontmatter zu bearbeiten verliert beim nächsten Compile, weil das Frontmatter neu erzeugt wird.) Obsidian-Nutzer können `.llm-wiki/wiki/` direkt öffnen; der bestehende `obsidian_vault/`-Adapter ist eine separate Projektion, kein Ersatz.

### `.llm-wiki/site/` (L3)

```text
site/
  index.html                  home + project pulse
  about.html                  schema, build info
  assets/{style.css,app.js}   single CSS bundle + single JS bundle
  sources/index.html
  sources/<slug>.html
  sources/<slug>.txt          AI sibling — plain text
  sources/<slug>.json         AI sibling — structured record
  concepts/…  entities/…  papers/…  repos/…  topics/…  syntheses/…  questions/…
  sessions/index.html          imported harness-session index
  sessions/<project>/<id>.html session detail: summary, metadata, turn rail, markdown turns, collapsed tools
  timeline/index.html
  graph/index.html            interactive 2D + 3D force layout
  graph.json                  full graph payload (incl. code nodes, for tooling)
  graph.jsonld                schema.org Dataset, wiki-layer nodes only
  search-index.json           palette + page search; wiki-layer kinds only
  llms.txt                    llmstxt.org — short index
  llms-full.txt               llmstxt.org — every page body, capped 5MB
  sitemap.xml                 every emitted route
  rss.xml                     last 30 syntheses
  robots.txt                  permissive (crawl + index)
  ai-readme.md                machine-readable site map
  manifest.json               sha256 + size for every emitted file
```

## Was bewusst ausgeschlossen ist

Das Redesign hat eine klare Linie gezogen: Code-Class- und Code-Function-Knoten bleiben in `graph.json` (damit MCP-, Cognee- und Graphiti-Consumer sie weiterhin sehen), bekommen aber nie HTML-Seiten, tauchen nie in `search-index.json` auf und erscheinen nie in der Navigation. Das ist der Vertrag nach außen — das Wiki ist eine dokument-zentrierte Wissensdatenbank, kein Function-Browser.

Konkret überspringt `StaticSiteBuilder` jeden Knoten, dessen Typ nicht in der L2-Wiki-Kind-Map (`llm_wiki/wiki_projector.py::_KIND_FOR_TYPE`) steht:

- Ausgeschlossen aus L2 + L3: `CodeClass`, `CodeFunction`, `CodeModule`, `Dependency`, `EvidenceSpan`, `SourceFile`, alle `Claim`-Varianten (`Claim`, `ContributionClaim`, `PerformanceClaim`, `ComparisonClaim`, `LimitationClaim`, `CausalClaim`).
- Flächen, wo sie weiterhin auftauchen: als Bullets, Badges, Neighbour-Counts oder Evidence-Excerpts inline auf verwandten Wiki-Seiten, und in `graph.json` für Downstream-Tooling.

Wenn du Code-Level-Browsing brauchst, richte ein LSP- / Call-Graph-Tool direkt auf den Source-Tree — das ist ein anderes Problem als „Wiki von dem, was dieses Projekt weiß“.

## Idempotenz-Story

Das Redesign zielt auf **byte-identischen Output über zwei aufeinanderfolgende `project compile`-Läufe bei unveränderten Inputs**. Die Bausteine:

1. **Source-Extraktion** nutzt die Content-Hashes aus `manifest.json`; unveränderte Dateien werden übersprungen, der Graph bleibt stabil.
2. **Wiki-Layer-Writes** sind auf Body-Ebene idempotent. `WikiPageStore.write_page` liest die existierende Datei, entfernt Frontmatter, sha256t den Body und kurzschließt, wenn der neue Body denselben Hash ergibt — auch wenn das neue Frontmatter einen anderen `generated_at`-Timestamp hat. Das ist der Schlüsseltrick, der git-Diffs beim Rebuild eng hält.
3. **Synthesis-Output** trägt einen `content_hash: sha256-…` im Frontmatter. Der Body-Hash wird ohne `generated_at` berechnet, sodass wiederholte Compiles auf demselben Graph denselben Hash erzeugen, und `Synthesis`-Knoten tragen denselben `content_hash` in den Graph-Metadaten.
4. **Site-Rendering** löscht `site/` zu Beginn von `write_site` und schreibt dann deterministisch: Routen sind sortiert, Dicts werden mit `sort_keys=True` gedumpt, `manifest.json` läuft über `sorted(rglob("*"))`. Zwei Läufe erzeugen byte-identische Dateien inklusive Manifest.

Das wird durch `tests/test_site_pages.py` und den End-to-End-Smoke in `tests/test_project_e2e_redesign.py` verifiziert (zweimal compilen, Sites diffen, null Deltas erwarten).

## Skalierungsnotizen

- **Graph-View-Knoten-Cap.** [`MAX_GRAPH_NODES = 1500`](../llm_wiki/site/pages.py) begrenzt das in die Seite eingebettete Payload für das interaktive Force-Layout. Jenseits von ~1500 Knoten wird die Browser-Simulation auf Mid-Range-Hardware träge, daher droppt die Seite zuerst die Wiki-Layer-Knoten mit dem niedrigsten Grad, sobald der Count das Cap überschreitet. Die exportierte `graph.json` ist davon unberührt — sie enthält immer den vollen Graph. Code-Knoten werden vor dem Cap herausgefiltert.
- **`llms-full.txt`-Cap.** Ein Safety-Cap von 5 MB greift in [`llm_wiki/site/exports.py`](../llm_wiki/site/exports.py); die Datei endet mit einem `[TRUNCATED — see graph.jsonld for the full set]`-Marker, wenn der Cap erreicht wird. `graph.jsonld` ist uncapped, weil JSON-LD-Consumer das volle Set erwarten.
- **Search-Index.** Nur Wiki-Layer-Kinds. Code-Graph-Knoten landen nie in `search-index.json`; das Redesign-Ziel ist < 500 KB für den Dogfood-Korpus und wir liegen heute deutlich darunter.
- **Per-Page-Byte-Budget (Faustregel).** Jede Detailseite < 60 KB gz HTML, shared CSS < 30 KB, shared JS < 25 KB, Sigma-Vendor nur auf der Graph-Seite (~60 KB). Die Graph-Ansicht nutzt 3D-force-graph + Three.js, einmal geladen; alle anderen Seiten bleiben vanilla.
- **Compile-Zeit auf Dogfood.** ~300 Markdown-Dateien extrahieren in unter 5 s auf einer aktuellen Dev-Maschine; das Site-Rendering fügt weitere ~2 s hinzu. Die Idempotenz der Wiki-Schicht sorgt dafür, dass nachfolgende Compiles nur die geänderten Pfade berühren.

## Frontend-Interaktionsfläche

- **Search-Palette** — `cmd+k` / `ctrl+k` / `/`. Fuzzy-Match über `search-index.json`, gescopet auf Wiki-Kinds. Recent Pages werden in `localStorage` persistiert.
- **Theme-Toggle** — Button oben rechts; `data-theme="dark"` wird in `localStorage` gespeichert und vor dem Paint angewendet, um Flash zu vermeiden.
- **Sticky-Right-TOC** — nur Desktop; kollabiert auf Mobile zu einem `<details>`-Drawer. Erzeugt aus `<h2>` / `<h3>` im Body.
- **Activity-Heatmap** — 26-Wochen-SVG mit Monats- + Wochentag-Labels. Zellen verlinken auf die Source-Seite `digest.md` des Tages, falls eine existiert. (Per-Day-Timeline-Detailseiten — `/timeline/<YYYY-MM-DD>.html` — sind ein expliziter Follow-up; der Inline-Hinweis in `render_timeline` markiert es. ⚠ in Arbeit.)
- **Graph-View** — `/graph/`. 3D-Force-Layout (3d-force-graph + Three.js) mit Hover-Tooltips, Edge-Labels, Cursor-verankertem Zoom und einer 2D-Fallback-View. Knotenfarben kommen aus `ResearchNodeType`.
- **Mobile-Shell** — Drawer-Rail, Bottom-Nav, fluide Schrift, touch-sichere Hit-Targets (≥ 44 px).

## Test-Strategie

- **Unit** — `tests/test_wiki_store.py`, `tests/test_synthesis.py`, `tests/test_site_components.py`, `tests/test_site_pages.py`, `tests/test_site_exports.py`, `tests/test_relevance.py`.
- **Idempotenz** — `tests/test_project_e2e_redesign.py` compilet zweimal und prüft auf null Diffs in `wiki/` und `site/`.
- **Link-Integrität** — `tests/test_frontend.py` parst jedes emittierte HTML nach hrefs und prüft, dass jeder interne Link auf eine erzeugte Datei zeigt. Es wird kein `nodes/codeclass-*.html` produziert.
- **AI-Siblings** — für jedes `path/foo.html` prüft die Test-Suite, dass `path/foo.txt` und `path/foo.json` existieren; das JSON parst und enthält `{title, kind, body, links}`.
- **Kein Playwright** — vanilla pytest unter `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

## Verwandte Dokumentation

- [Quickstart](quickstart.de.md) — minimaler Pfad von `project init` zu einer browserbaren Site.
- [Frontend-Redesign-Walkthrough](frontend-redesign.de.md) — annotierte Tour durch jede Route.
- [Feature-Map](feature-map.de.md) — was geliefert ist, was in Arbeit ist, mit File-Pointern.
- [Self-Dogfood-Demo](self-dogfood.de.md) — LLM-Wiki gegen das eigene Repo laufen lassen.
