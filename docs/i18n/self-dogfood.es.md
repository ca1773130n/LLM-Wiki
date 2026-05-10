# Demo Self-dogfood

<!-- translations:start -->
<p align="center"><a href="../self-dogfood.md">English</a> · <a href="self-dogfood.ko.md">한국어</a> · <a href="self-dogfood.zh.md">中文</a> · <a href="self-dogfood.ja.md">日本語</a> · <a href="self-dogfood.ru.md">Русский</a> · <a href="self-dogfood.es.md">Español</a> · <a href="self-dogfood.fr.md">Français</a></p>
<!-- translations:end -->
Este proyecto puede indexarse a sí mismo. El flujo self-dogfood demuestra que LLM-Wiki puede instalarse, configurarse dentro de su propio repositorio, ingerir sus propios docs/source/tests/scripts, actualizar opcionalmente Understand Anything y Cognee, compilar artefactos de grafo y construir el frontend web estático.

## Comandos

Desde la raíz del repositorio:

```bash
# Asegúrate de que el comando de shell esté instalado.
./scripts/install.sh --dir "$PWD"
export PATH="$HOME/.local/bin:$PATH"

# Configura este repositorio como un proyecto LLM-Wiki.
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

# Compila las fuentes configuradas.
llm_wiki project compile

# Reconstruye explícitamente el frontend estático.
llm_wiki project build-site

# Sirve localmente.
llm_wiki project serve --port 8765
```

Abre:

```text
http://127.0.0.1:8765/
```

## Workspace generado

La self-demo escribe los artefactos generados bajo:

```text
.llm-wiki/
```

Artefactos clave:

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

El workspace generado no se confirma por defecto de forma intencional. Es reproducible desde el código fuente del repositorio con los comandos anteriores.

## Última ejecución verificada

Verificado el `2026-04-27 11:11:23 KST` desde el propio repositorio LLM-Wiki.

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

Conteos finales de artefactos:

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

Tipos de nodo principales:

```text
CodeFunction:    452
Dependency:       55
CodeClass:        54
Concept:          51
SourceFile:       47
SourceDocument:    7
CodeProject:       1
```

Verificación en navegador:

```text
loaded title: Home · llm_wiki_self
visible stats: 667 nodes / 1020 edges / 55 sources / 7 types
sources page: source evidence table links to per-source pages
source detail: llm_wiki/frontend.py shows 41 nodes, 54 related edges, type mix, node links, and edge table
search smoke: StaticSiteBuilder returned CodeClass and StaticSiteBuilder.write_site results
console: no JavaScript errors on home, sources, source detail, or graph pages
server: TCP *:56821 LISTEN, serving via --host 0.0.0.0
```

## Qué demuestra esto

- La ruta de instalación pública funciona.
- El comando de shell `llm_wiki` funciona.
- Un repositorio puede adjuntar un workspace `.llm-wiki` local al proyecto.
- El markdown de investigación/documentación y los nodos de grafo de código de desarrollo pueden coexistir.
- Las proyecciones Markdown, Obsidian, frontend, Graphiti, Cognee, SQLite, report y agent-harness se producen desde una sola canalización de grafo.
- El frontend HTML estático puede explorar el grafo del proyecto sin un paso de compilación JavaScript.
