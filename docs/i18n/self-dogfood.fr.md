# Démo Self-dogfood

<!-- translations:start -->
<p align="center"><a href="../self-dogfood.md">English</a> · <a href="self-dogfood.ko.md">한국어</a> · <a href="self-dogfood.zh.md">中文</a> · <a href="self-dogfood.ja.md">日本語</a> · <a href="self-dogfood.ru.md">Русский</a> · <a href="self-dogfood.es.md">Español</a> · <a href="self-dogfood.fr.md">Français</a> · <a href="self-dogfood.de.md">Deutsch</a></p>
<!-- translations:end -->
Ce projet peut s'indexer lui-même. Le flux self-dogfood prouve que LLM-Wiki peut être installé, configuré dans son propre dépôt, ingérer ses propres docs/source/tests/scripts, rafraîchir optionnellement Understand Anything et Cognee, compiler des artefacts de graphe et construire le frontend web statique.

## Commandes

Depuis la racine du dépôt :

```bash
# Vérifiez que la commande shell est installée.
./scripts/install.sh --dir "$PWD"
export PATH="$HOME/.local/bin:$PATH"

# Configurez ce dépôt comme projet LLM-Wiki.
llm_wiki project setup \
  --yes \
  --name llm_wiki_self \
  --source README.md \
  --source docs \
  --source llm_wiki \
  --source tests \
  --source scripts \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee

# Compilez les sources configurées.
llm_wiki project compile

# Reconstruisez explicitement le frontend statique.
llm_wiki project build-site

# Servez localement.
llm_wiki project serve --port 8765
```

Ouvrir :

```text
http://127.0.0.1:8765/
```

## Workspace généré

La self-demo écrit les artefacts générés sous :

```text
.llm-wiki/
```

Artefacts clés :

```text
.llm-wiki/config.json
.llm-wiki/graph.json
.llm-wiki/manifest.json
.llm-wiki/sqlite.db
.llm-wiki/report.md
.llm-wiki/competitive_report.md
.llm-wiki/temporal_facts.jsonl
.llm-wiki/graphiti_episodes.jsonl
.llm-wiki/markdown_projection/
.llm-wiki/obsidian_vault/
.llm-wiki/agent_harness/
.llm-wiki/site/
.llm-wiki/cognee_bundle/
```

Le workspace généré n'est intentionnellement pas committé par défaut. Il est reproductible depuis les sources du dépôt avec les commandes ci-dessus.

## Dernière exécution vérifiée

Vérifié le `2026-04-27 11:11:23 KST` depuis le dépôt LLM-Wiki lui-même.

```text
install command: ./scripts/install.sh --dir /Users/neo/Developer/Projects/LLM-Wiki --skip-shell-config
setup command:   llm_wiki project setup --yes --name llm_wiki_self --source README.md --source docs --source llm_wiki --source tests --source scripts --with-understand-anything --install-understand-anything --understand-anything-platform codex --run-cognee --install-cognee
ingest command:  llm_wiki project ingest README.md docs --changed-only
compile command: llm_wiki project compile
site command:    llm_wiki project build-site
serve command:   llm_wiki project serve --host 0.0.0.0 --port 56821
local URL:       http://127.0.0.1:56821/
LAN URL:         http://192.168.45.130:56821/
```

Décompte final des artefacts :

```text
nodes:               667
edges:               1020
markdown notes:      684
obsidian notes:      686
agent harness files: 14
cognee nodes:        667
cognee edges:        1020
graphiti episodes:  1020
temporal facts:      1020
site files:          index.html, nodes/index.html, sources/index.html, graph/index.html, graph.json, search-index.json, llms.txt, llms-full.txt, manifest.json, assets/style.css, assets/app.js
node pages:          687
source pages:        56
```

Principaux types de nœuds :

```text
CodeFunction:    452
Dependency:       55
CodeClass:        54
Concept:          51
SourceFile:       47
SourceDocument:    7
CodeProject:       1
```

Vérification dans le navigateur :

```text
loaded title: Home · llm_wiki_self
visible stats: 667 nodes / 1020 edges / 55 sources / 7 types
sources page: source evidence table links to per-source pages
source detail: llm_wiki/frontend.py shows 41 nodes, 54 related edges, type mix, node links, and edge table
search smoke: StaticSiteBuilder returned CodeClass and StaticSiteBuilder.write_site results
console: no JavaScript errors on home, sources, source detail, or graph pages
server: TCP *:56821 LISTEN, serving via --host 0.0.0.0
```

## Ce que cela démontre

- Le chemin d'installation public fonctionne.
- La commande shell `llm_wiki` fonctionne.
- Un dépôt peut attacher un workspace `.llm-wiki` local au projet.
- Le markdown de recherche/documentation et les nœuds de graphe du code de développement peuvent coexister.
- Les projections Markdown, Obsidian, frontend, Graphiti, Cognee, SQLite, report et agent-harness sont produites depuis un seul pipeline de graphe.
- Le frontend HTML statique peut parcourir le graphe du projet sans étape de build JavaScript.
