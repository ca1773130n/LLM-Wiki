# Self-Dogfood-Demo

<!-- translations:start -->
<p align="center"><a href="../self-dogfood.md">English</a> · <a href="self-dogfood.ko.md">한국어</a> · <a href="self-dogfood.zh.md">中文</a> · <a href="self-dogfood.ja.md">日本語</a> · <a href="self-dogfood.ru.md">Русский</a> · <a href="self-dogfood.es.md">Español</a> · <a href="self-dogfood.fr.md">Français</a></p>
<!-- translations:end -->
Dieses Projekt kann sich selbst indexieren. Der Self-Dogfood-Flow beweist, dass LLM-Wiki installiert, in seinem eigenen Repository aufgesetzt werden kann, seine eigenen Docs/Source/Tests/Scripts ingestiert, optional Understand Anything und Cognee refresht, Graph-Artefakte kompiliert und das statische Web-Frontend baut.

Derselbe Flow dient gleichzeitig als multimodaler Smoke-Test. Mit `--with-raganything --install-raganything --run-raganything` richtet der Dogfood-Compile RAG-Anything auf das eigene `docs/`-Markdown von LLM-Wiki plus die Bilder unter `docs/assets/` und projekt-level `assets/`. Das validiert die multimodale Pipeline gegen einen echten, projekt-eigenen Nicht-Code-Korpus — abdeckend Screenshots und Diagramme, die die textzentrierten Source-Loader überspringen — ohne ein separates Fixture-Set zu erfinden.

## Befehle

Aus dem Repository-Root:

```bash
# Ensure the shell command is installed.
./scripts/install.sh --dir "$PWD"
export PATH="$HOME/.local/bin:$PATH"

# Set up this repository as an LLM-Wiki project.
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
  --with-raganything \
  --install-raganything \
  --raganything-parser mineru \
  --run-raganything \
  --run-cognee \
  --install-cognee

# Compile the configured sources.
llm_wiki project compile

# Rebuild the static frontend explicitly.
llm_wiki project build-site

# Serve locally.
llm_wiki project serve --port 8765
```

Öffne:

```text
http://127.0.0.1:8765/
```

## Generiertes Workspace

Die Self-Demo schreibt generierte Artefakte unter:

```text
.llm-wiki/
```

Schlüssel-Artefakte:

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

Das generierte Workspace wird absichtlich standardmäßig nicht committet. Es ist mit den obigen Befehlen aus den Repository-Sources reproduzierbar.

## Letzter verifizierter Lauf

Verifiziert am `2026-04-27 11:11:23 KST` aus dem LLM-Wiki-Repository selbst.

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

Finale Artefakt-Counts:

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

Top-Node-Typen:

```text
CodeFunction:    452
Dependency:       55
CodeClass:        54
Concept:          51
SourceFile:       47
SourceDocument:    7
CodeProject:       1
```

Browser-Verifikation:

```text
loaded title: Home · llm_wiki_self
visible stats: 667 nodes / 1020 edges / 55 sources / 7 types
sources page: source evidence table links to per-source pages
source detail: llm_wiki/frontend.py shows 41 nodes, 54 related edges, type mix, node links, and edge table
search smoke: StaticSiteBuilder returned CodeClass and StaticSiteBuilder.write_site results
console: no JavaScript errors on home, sources, source detail, or graph pages
server: TCP *:56821 LISTEN, serving via --host 0.0.0.0
```

## Was das demonstriert

- Der öffentliche Install-Pfad funktioniert.
- Der `llm_wiki`-Shell-Befehl funktioniert.
- Ein Repository kann ein projekt-lokales `.llm-wiki`-Workspace anhängen.
- Research-/Dokumentations-Markdown und Development-Code-Graph-Knoten können koexistieren.
- Markdown-, Obsidian-, Frontend-, Graphiti-, Cognee-, SQLite-, Report- und Agent-Harness-Projektionen werden aus einer Graph-Pipeline produziert.
- Das statische HTML-Frontend kann den Project-Graph ohne JavaScript-Build-Schritt browsen.
