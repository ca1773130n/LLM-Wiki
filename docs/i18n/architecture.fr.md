# Architecture

<!-- translations:start -->
<p align="center"><a href="../architecture.md">English</a> · <a href="architecture.ko.md">한국어</a> · <a href="architecture.zh.md">中文</a> · <a href="architecture.ja.md">日本語</a> · <a href="architecture.ru.md">Русский</a> · <a href="architecture.es.md">Español</a> · <a href="architecture.fr.md">Français</a> · <a href="architecture.de.md">Deutsch</a></p>
<!-- translations:end -->
LLM-Wiki transforme un répertoire de matériaux sources en graphe de connaissances contrôlé et typé, puis projette ce graphe à travers une couche wiki markdown durable vers un site web statique adapté à l’IA. La refonte d’avril 2026 a réorganisé le système autour d’un modèle Karpathy à trois couches : les preuves brutes restent brutes, un graphe typé gouverne l’ontologie, et une couche wiki markdown se place entre le graphe et toute sortie rendue. Le site statique est désormais un *moteur de rendu* de cette couche wiki, plutôt qu’un dump direct du graphe, avec l’ontologie contrôlée dans [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) comme schéma.

## Le modèle Karpathy à trois couches

Le cadrage d’Andrej Karpathy pour les bases de connaissances adaptées aux LLM distingue trois couches, chacune avec sa propre garantie de durabilité :

| Couche | Préoccupation | Emplacement dans le dépôt | Propriétaire |
|---|---|---|---|
| L1 — Sources brutes | Les octets littéraux que l’utilisateur a rédigés ou collectés. Append-only. | `data/`, `docs/`, arbres de projet référencés dans `.llm-wiki/config.json` | l’utilisateur |
| L2 — Wiki | Pages markdown typées (sources, concepts, entities, papers, repos, topics, syntheses, questions) avec YAML frontmatter. Idempotent : régénéré à chaque compilation, mais réécrit uniquement lorsque les hashes de contenu changent. | `.llm-wiki/wiki/` | `WikiPageStore`, `WikiLayerProjector`, `SynthesisProjector` |
| L3 — Rendu | Le site HTML statique, les exports AI-sibling, l’index de recherche, les sitemaps, JSON-LD. Effacé et réécrit à chaque compilation, mais stable octet pour octet entre les relances. | `.llm-wiki/site/` | `StaticSiteBuilder` (`llm_wiki/site/`) |

Le schéma traverse les trois couches comme un axe séparé : `ResearchGraph` dans `graph.json` est l’ontologie contrôlée vers laquelle pointent les pages L2, et `ResearchNodeType` / la whitelist des arêtes dans [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) est la source de vérité pour les types qui existent.

La refonte a ajouté explicitement L2. Avant avril 2026, le site statique était projeté directement depuis `graph.json`; la couche wiki n’existait qu’à l’intérieur de l’export Obsidian vault. La séparer nous a donné :

- Une surface unique modifiable par un humain (ouvrez `.llm-wiki/wiki/` dans Obsidian ou n’importe quel éditeur markdown).
- Des reconstructions idempotentes : relancer `project compile` produit zéro diff de fichier sauf si le contenu source a changé.
- Un journal d’évolution : les pages de synthèse s’accumulent au fil du temps et permettent au projet de se raconter lui-même.

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

Chaque étape est incrémentale. L’extracteur de graphe utilise les hashes de contenu de `manifest.json` pour ignorer les fichiers sources inchangés. `WikiPageStore.write_page` renvoie `False` (et saute l’écriture) lorsque le hash du corps correspond à ce qui est déjà sur disque. `StaticSiteBuilder` efface et réécrit `.llm-wiki/site/`, mais sa sortie est déterministe — voir « Récit d’idempotence » ci-dessous.

## Carte des modules

### Wiki + synthèse (L2)

| Module | Responsabilité |
|---|---|
| [`llm_wiki/wiki_store.py`](../../llm_wiki/wiki_store.py) | Dataclass `WikiPage`, `WikiPageStore` pour les I/O du système de fichiers. Parseur YAML-subset frontmatter uniquement stdlib. Idempotence par hash du corps. |
| [`llm_wiki/wiki_projector.py`](../../llm_wiki/wiki_projector.py) | `WikiLayerProjector` : mappe chaque nœud `ResearchGraph` de type wiki-layer vers une page markdown dans le bon dossier `kind/`. |
| [`llm_wiki/synthesis.py`](../../llm_wiki/synthesis.py) | `SynthesisProjector` : modèles déterministes pour pulse, daily_digest, weekly, topic, comparison, field_overview. Ajoute les nœuds `Synthesis` et les arêtes `synthesizes` / `summarizes` dans le graphe. |

### Graphe + ontologie

| Module | Responsabilité |
|---|---|
| [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) | Enum `ResearchNodeType` (incl. `SYNTHESIS`), whitelist des types d’arêtes (incl. `synthesizes`, `summarizes`), validation. |
| [`llm_wiki/canonicalization.py`](../../llm_wiki/canonicalization.py) | Canonicalisation des alias + file de revue des quasi-doublons. |
| [`llm_wiki/code_graph.py`](../../llm_wiki/code_graph.py) | Extracteur Python AST déterministe pour la tranche développement. |
| [`llm_wiki/llm_extractor.py`](../../llm_wiki/llm_extractor.py) | Extracteur sélectif Claude CLI/OAuth. |

### Rendu du site (L3)

| Module | Responsabilité |
|---|---|
| [`llm_wiki/site/__init__.py`](../../llm_wiki/site/__init__.py) | `StaticSiteBuilder.write_site` : efface + reconstruit le site, parcourt toutes les routes, émet les exports + AI siblings + manifest. |
| [`llm_wiki/site/pages.py`](../../llm_wiki/site/pages.py) | Un moteur de rendu par route (home, indexes, detail pages, timeline, graph, about). `SiteContext` transporte des index précalculés pour que les renderers restent purs. |
| [`llm_wiki/site/components.py`](../../llm_wiki/site/components.py) | Primitives HTML : `breadcrumbs`, `card`, `badge`, `node_table`, `edge_list`, `sparkline_svg`, `heatmap_svg`, `toc`, `page_shell`, `ai_siblings_footer`. |
| [`llm_wiki/site/tokens.py`](../../llm_wiki/site/tokens.py) | Design tokens — variables CSS, thèmes clair + sombre, layout, typographie; tous les composants sont stylés ici. |
| [`llm_wiki/site/js.py`](../../llm_wiki/site/js.py) | Bundle JS client : search palette, theme toggle, sigma + 3D-force graph view. |
| [`llm_wiki/site/markdown.py`](../../llm_wiki/site/markdown.py) | Renderer markdown uniquement stdlib (links, autolinks, code, emphasis, headings). Aucune dépendance externe. |
| [`llm_wiki/site/relevance.py`](../../llm_wiki/site/relevance.py) | Scoring de pertinence à quatre signaux (direct link, source overlap, Adamic-Adar, type affinity), utilisé par chaque section `Related`. |
| [`llm_wiki/site/search.py`](../../llm_wiki/site/search.py) | Constructeur de `search-index.json`. Wiki-layer kinds uniquement. |
| [`llm_wiki/site/sessions.py`](../../llm_wiki/site/sessions.py) | Renderers d’index/détail de sessions pour l’historique harness importé : sections project-memory summary, rail des tours de conversation, rendu de markdown transcript et blocs tool-use repliés. |
| [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) | `llms.txt`, `llms-full.txt`, `graph.jsonld`, `sitemap.xml`, `rss.xml`, `robots.txt`, `ai-readme.md`, siblings `.txt`/`.json` par page. |

### Orchestration du pipeline

| Module | Responsabilité |
|---|---|
| [`llm_wiki/project.py`](../../llm_wiki/project.py) | `ProjectWiki.compile` : pilote extraction → graph → wiki layer → site. Possède `ProjectPaths` (`config`, `graph`, `manifest`, `wiki`, `site`, etc.). |
| [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | Toutes les sous-commandes `llm_wiki project …`, dont `compile`, `build-site`, `serve`, `watch`, `deploy`. |
| [`llm_wiki/deploy.py`](../../llm_wiki/deploy.py) | `project deploy` : pousse `.llm-wiki/site/` vers une branche `gh-pages` via worktree, active éventuellement Pages via `gh`. |

### Adaptateurs externes (inchangés dans ce cycle)

| Module | Responsabilité |
|---|---|
| [`llm_wiki/obsidian_adapter.py`](../../llm_wiki/obsidian_adapter.py) | Projection Obsidian vault (coloration du graphe, Dataview dashboard, raw assets). |
| [`llm_wiki/agent_harness.py`](../../llm_wiki/agent_harness.py) | Exports harness Claude Code / Codex / Gemini / Kiro / Cursor / OpenCode. |
| [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) | Découverte des sessions entrantes Claude Code/Codex, normalisation, stockage sous `.llm-wiki/harness_sessions/`, et résumés markdown expurgés. |
| [`llm_wiki/graphiti_adapter.py`](../../llm_wiki/graphiti_adapter.py) | Temporal-fact JSONL + synchronisation live Graphiti optionnelle. |
| [`llm_wiki/cognee_adapter.py`](../../llm_wiki/cognee_adapter.py) | Bundle JSONL de nœuds/arêtes Cognee et chemin direct add/cognify. |
| [`llm_wiki/mcp_server.py`](../../llm_wiki/mcp_server.py) | Serveur MCP stdio exposant `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline`. |

## Layout du workspace projet

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

Chaque fichier est modifiable à la main ; la prochaine compilation respecte les modifications utilisateur tant que le hash du corps diffère de ce que le projector écrirait. (Modifier seulement le corps gagne ; modifier le frontmatter perd à la compilation suivante parce que le frontmatter est régénéré.) Les utilisateurs d’Obsidian peuvent ouvrir `.llm-wiki/wiki/` directement ; l’adaptateur `obsidian_vault/` existant est une projection séparée, pas un substitut.

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

## Ce qui est volontairement exclu

La refonte a tracé une ligne explicite : les nœuds code-class et code-function restent dans `graph.json` (donc les consommateurs MCP, Cognee et Graphiti les voient toujours), mais ils n’obtiennent jamais de pages HTML, n’apparaissent jamais dans `search-index.json` et n’apparaissent jamais dans la navigation. C’est le contrat côté utilisateur : le wiki est une base de connaissances orientée documents, pas un navigateur de fonctions.

Concrètement, `StaticSiteBuilder` ignore tout nœud dont le type n’est pas dans la map des types wiki L2 (`llm_wiki/wiki_projector.py::_KIND_FOR_TYPE`) :

- Exclus de L2 + L3 : `CodeClass`, `CodeFunction`, `CodeModule`, `Dependency`, `EvidenceSpan`, `SourceFile`, toutes les variantes `Claim` (`Claim`, `ContributionClaim`, `PerformanceClaim`, `ComparisonClaim`, `LimitationClaim`, `CausalClaim`).
- Surfaces où ils apparaissent encore : comme bullets, badges, neighbor counts ou evidence excerpts inline dans les pages wiki liées, et dans `graph.json` pour le downstream tooling.

Si vous avez besoin de navigation au niveau code, pointez un outil LSP / call-graph directement vers l’arbre source — c’est un problème différent de « wiki de ce que ce projet sait ».

## Récit d’idempotence

La refonte vise une **sortie identique octet pour octet sur deux exécutions consécutives de `project compile` avec des entrées inchangées**. Les éléments :

1. **L’extraction des sources** utilise les hashes de contenu de `manifest.json` ; les fichiers inchangés sont ignorés, donc le graphe reste stable.
2. **Les écritures de la couche wiki** sont idempotentes au niveau du corps. `WikiPageStore.write_page` lit le fichier existant, retire le frontmatter, calcule le sha256 du corps, et court-circuite si le nouveau corps a le même hash — même si le nouveau frontmatter a un timestamp `generated_at` différent. C’est l’astuce clé qui garde les git diffs serrés lors des reconstructions.
3. **La sortie de synthèse** porte `content_hash: sha256-…` dans son frontmatter. Le hash du corps est calculé sans `generated_at`, donc des compilations répétées sur le même graphe produisent le même hash, et les nœuds `Synthesis` portent le même `content_hash` dans les métadonnées du graphe.
4. **Le rendu du site** efface `site/` au début de `write_site`, puis écrit de façon déterministe : les routes sont triées, les dictionnaires dumpés avec `sort_keys=True`, `manifest.json` parcouru via `sorted(rglob("*"))`. Deux exécutions produisent des fichiers identiques octet pour octet, y compris le manifest.

Ceci est vérifié par `tests/test_site_pages.py` et le smoke end-to-end dans `tests/test_project_e2e_redesign.py` (compiler deux fois, diff des sites, attendre zéro delta de fichier).

## Notes de mise à l’échelle

- **Limite de nœuds de la vue graphe.** [`MAX_GRAPH_NODES = 1500`](../../llm_wiki/site/pages.py) borne le payload embarqué dans la page pour le layout de force interactif. Au-delà d’environ 1500 nœuds, la simulation côté navigateur devient lente sur du matériel moyen ; la page retire donc d’abord les nœuds wiki-layer de plus faible degré lorsque le nombre dépasse la limite. Le `graph.json` exporté n’est pas affecté — il contient toujours le graphe complet. Les code nodes sont filtrés avant l’application de la limite.
- **Limite de `llms-full.txt`.** Une limite de sécurité de 5 MB s’applique dans [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) ; si la limite est atteinte, le fichier se termine par le marqueur `[TRUNCATED — see graph.jsonld for the full set]`. `graph.jsonld` n’est pas limité parce que les consommateurs JSON-LD attendent l’ensemble complet.
- **Index de recherche.** Wiki-layer kinds uniquement. Les code-graph nodes n’entrent jamais dans `search-index.json` ; l’objectif de refonte est < 500 KB pour le corpus dogfood et nous sommes largement en dessous aujourd’hui.
- **Budget d’octets par page (règle empirique).** Chaque detail page < 60 KB gz HTML, shared CSS < 30 KB, shared JS < 25 KB, sigma vendor seulement sur la graph page (~60 KB). La graph view utilise 3D-force-graph + Three.js chargés une seule fois ; toutes les autres pages restent vanilla.
- **Temps de compilation sur dogfood.** ~300 fichiers markdown s’extraient en moins de 5 s sur une machine de dev récente ; le rendu du site ajoute encore ~2 s. L’idempotence de la couche wiki signifie que les compilations suivantes ne touchent que les chemins modifiés.

## Surface d’interaction frontend

- **Search palette** — `cmd+k` / `ctrl+k` / `/`. Fuzzy match sur `search-index.json`, limité aux wiki kinds. Les pages récentes sont persistées dans `localStorage`.
- **Theme toggle** — bouton en haut à droite ; `data-theme="dark"` est stocké dans `localStorage` et appliqué avant le paint pour éviter le flash.
- **Sticky right TOC** — desktop uniquement ; se replie en drawer `<details>` sur mobile. Généré depuis les `<h2>` / `<h3>` dans le corps de page.
- **Activity heatmap** — SVG de 26 semaines avec labels month + weekday. Les cellules pointent vers la source page `digest.md` du jour quand elle existe. (Per-day timeline detail pages — `/timeline/<YYYY-MM-DD>.html` — est un follow-up explicite ; la notice inline dans `render_timeline` le signale. ⚠ in-progress.)
- **Graph view** — `/graph/`. 3D force layout (3d-force-graph + Three.js) avec hover tooltips, edge labels, zoom ancré au curseur et 2D fallback view. Les couleurs de nœuds viennent de `ResearchNodeType`.
- **Mobile shell** — drawer rail, bottom nav, fluid type, touch-safe hit targets (≥ 44 px).

## Stratégie de test

- **Unit** — `tests/test_wiki_store.py`, `tests/test_synthesis.py`, `tests/test_site_components.py`, `tests/test_site_pages.py`, `tests/test_site_exports.py`, `tests/test_relevance.py`.
- **Idempotence** — `tests/test_project_e2e_redesign.py` compile deux fois et affirme zéro diff dans `wiki/` et `site/`.
- **Intégrité des liens** — `tests/test_frontend.py` parse chaque HTML émis pour les hrefs et affirme que chaque lien interne se résout vers un fichier généré. Aucun `nodes/codeclass-*.html` n’est produit.
- **AI siblings** — pour chaque `path/foo.html`, la suite de tests affirme que `path/foo.txt` et `path/foo.json` existent ; le JSON se parse et contient `{title, kind, body, links}`.
- **Pas de Playwright** — pytest vanilla sous `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

## Documents liés

- [Démarrage rapide](quickstart.fr.md) — chemin minimal de `project init` à un site navigable.
- [Parcours de la refonte frontend](frontend-redesign.fr.md) — visite annotée de chaque route.
- [Carte des fonctionnalités](feature-map.fr.md) — ce qui est livré, ce qui est in-progress, avec pointeurs de fichiers.
- [Démo self-dogfood](self-dogfood.fr.md) — exécuter LLM-Wiki sur son propre dépôt.
