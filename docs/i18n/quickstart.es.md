# Inicio rápido

<!-- translations:start -->
<p align="center"><a href="../quickstart.md">English</a> · <a href="quickstart.ko.md">한국어</a> · <a href="quickstart.zh.md">中文</a> · <a href="quickstart.ja.md">日本語</a> · <a href="quickstart.ru.md">Русский</a> · <a href="quickstart.es.md">Español</a> · <a href="quickstart.fr.md">Français</a> · <a href="quickstart.de.md">Deutsch</a></p>
<!-- translations:end -->
Esta página muestra el camino más corto desde un directorio de proyecto existente hasta un LLM-Wiki navegable.

## 1. Ejecuta el asistente de configuración

Desde el proyecto que quieres indexar:

```bash
cd /path/to/my-project
llm_wiki project setup
```

El asistente detecta fuentes comunes como `README.md`, `docs`, `src`, `lib`, `app`, `packages` y `data`, y luego escribe `.llm-wiki/config.json`. También configura el backend Cognee predeterminado para que `project ask` pueda probar Cognee y hacer fallback a la búsqueda del wiki compilado.

Para una configuración totalmente automática con Understand Anything y Cognee runtime memory activados:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

Qué hace:

| Flag | Effect |
|---|---|
| `--with-understand-anything` | Añade la UA graph projection como source. |
| `--install-understand-anything` | Instala/actualiza las UA companion skills. |
| `--understand-anything-platform codex` | Usa Codex para ejecutar el managed UA refresh wrapper de LLM-Wiki. |
| `--run-cognee` | Ejecuta best-effort Cognee runtime cognify durante compile. |
| `--install-cognee` | Instala Cognee con el Python actual si falta. |

Los usuarios no necesitan conocer la UA install path ni escribir `/understand`; `project compile` ejecuta `project refresh-understand-anything` cuando el UA graph falta o está obsoleto.

## 2. Compila el grafo y las projections

```bash
llm_wiki project compile
```

`project compile` escribe los durable artifacts:

```text
.llm-wiki/
  config.json
  graph.json
  manifest.json
  sqlite.db
  temporal_facts.jsonl
  graphiti_episodes.jsonl
  report.md
  competitive_report.md
  markdown_projection/
  obsidian_vault/
  agent_harness/
  harness_sessions/
  site/
  cognee_bundle/
```

Usa `--changed-only` después de la primera ejecución para omitir archivos markdown sin cambios y preservar el graph anterior cuando no haya cambios. Si Understand Anything está activado, compile primero refresca/materializa `.llm-wiki/external/understand-anything.md`; si Cognee runtime está activado, también actualiza Cognee en modo best-effort después de escribir `.llm-wiki/cognee_bundle/`.

## 3. Construye y sirve el frontend estático

```bash
llm_wiki project build-site
llm_wiki project serve --port 8765
```

Abre:

```text
http://127.0.0.1:8765/
```

<!-- BEGIN: subagent-r-watch -->
### Auto-rebuild al guardar

Combina el dev server con un polling watcher para que las ediciones bajo `data/` y `docs/` disparen un recompile incremental:

```bash
# terminal 1
python3 -m http.server 56821 --directory .llm-wiki/site

# terminal 2
llm_wiki project watch
```

`project watch` hace polling cada 2 s, debounce de 1 s y ejecuta `compile --changed-only`. Usa `--once` para rebuilds tipo cron (snapshots vs `.llm-wiki/.watch-cache.json`), `--paths <dir>` para añadir custom watch dirs y `--interval` / `--debounce` para ajustar la cadence.
<!-- END: subagent-r-watch -->

Para un tour anotado de cada route visible — home, sources, concepts, entities, papers, repos, topics, syntheses, questions, timeline, graph, además de los AI siblings — consulta [`docs/frontend-redesign.md`](frontend-redesign.es.md).

El frontend tiene pocas dependencias y escribe:

```text
.llm-wiki/site/index.html
.llm-wiki/site/sessions/index.html
.llm-wiki/site/graph.json
.llm-wiki/site/search-index.json
.llm-wiki/site/llms.txt
```

## 4. Importa el historial de sesiones de agentes locales

La importación de historial de sesiones es explícita: compile/build normal lee sesiones ya normalizadas, pero no escanea por sí solo almacenes privados de transcript de Claude Code o Codex.

```bash
# Preview matching Claude Code/Codex sessions for this project:
llm_wiki project sessions discover

# Normalize and store them under .llm-wiki/harness_sessions/:
llm_wiki project sessions discover --import

# Confirm the imported set:
llm_wiki project sessions list

# Rebuild so sessions/index.html and session detail pages are emitted:
llm_wiki project build-site
```

Las sesiones importadas aparecen en la sección global Sessions, la búsqueda del sitio y las tarjetas Browse de inicio. Las páginas de detalle renderizan turnos user/assistant como markdown legible, adjuntan tool-use blocks bajo el turno assistant anterior y exponen un turn rail izquierdo para navegación `#turn-N`. Consulta [`docs/session-history.md`](session-history.es.md) para notas de privacidad, formatos de importación y el mapa actual de transcript typography.

## 5. Lint del wiki

```bash
llm_wiki project lint
```

Recorre el compiled graph + wiki + site y marca orphan papers, stale citations, drift entre graph y wiki/, ghost synthesis inputs y más. Escribe `.llm-wiki/lint-report.md` y `.llm-wiki/lint-report.json`. Pasa `--fix-trivial` para aplicar auto-fixes seguros (missing `implemented_in` edges, ghost-input pruning) y `--severity error` para fallar el exit code solo con errors.

## 6. Consulta el wiki

```bash
llm_wiki project query "What is Gaussian Splatting?"
```

Por defecto solo búsqueda: BM25 sobre `.llm-wiki/site/search-index.json`, con un excerpt de 200 caracteres tomado del `wiki/<kind>/<slug>.md` coincidente. Pasa `--kind papers` (o `concepts`, `repos`, etc.) para acotar, `--top-k N` para ampliar y `--json` para salida estructurada. Añade `--llm` (o define `LLM_WIKI_QUERY_LLM=1`) para pedir a Claude una respuesta sintetizada con citations `[node_id]`; `--interactive` abre un REPL readline — línea en blanco o EOF sale. `LLM_WIKI_QUERY_DRY_RUN=1` ejercita el prompt sin llamada API.

## 7. Exporta archivos agent harness

```bash
llm_wiki project export-agent-harness
```

Targets soportados:

- Claude Code
- Codex
- Gemini
- Kiro
- Cursor
- OpenCode

Subset de ejemplo:

```bash
llm_wiki project export-agent-harness \
  --target claude-code \
  --target cursor \
  --target opencode
```

## 8. Exporta un vault de Obsidian

```bash
llm_wiki project export-obsidian
```

O escribe en un vault existente:

```bash
llm_wiki project export-obsidian --vault "$OBSIDIAN_VAULT_PATH"
```

El vault incluye markdown projections, defaults de `.obsidian`, graph coloring, `raw/assets/` y un dashboard Dataview.

## 9. Configura MCP

```bash
llm_wiki project mcp-config --server-name my_project_wiki
```

Pega la salida bajo `mcp_servers` en `~/.hermes/config.yaml`, luego reinicia Hermes/gateway.

## 10. Graphiti export / sync

Episode export sin dependencias:

```bash
llm_wiki project export-graphiti
```

Dry-run sync smoke sin Graphiti instalado:

```bash
llm_wiki project sync-graphiti --dry-run
```

Live sync requiere `graphiti_core` y un backend Neo4j alcanzable:

```bash
llm_wiki project sync-graphiti \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-password '<password>'
```

## 11. Despliega en GitHub Pages

Haz push del compiled site en `.llm-wiki/site/` a la rama `gh-pages` del git origin del proyecto:

```bash
llm_wiki project deploy --build --enable-pages
```

`--build` ejecuta `project compile` primero para que el site esté fresco. `--enable-pages` activa Pages mediante la CLI `gh` (idempotente; se omite con una pista si falta `gh`). Usa `--dry-run` para stage y commit sin push, `--branch` / `--remote` para reemplazar defaults y `--force` para permitir desplegar con un working tree dirty.

El sitio queda accesible en `https://<owner>.github.io/<repo>/`.
