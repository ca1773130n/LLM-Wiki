# Mapa de funciones

<!-- translations:start -->
<p align="center"><a href="../feature-map.md">English</a> · <a href="feature-map.ko.md">한국어</a> · <a href="feature-map.zh.md">中文</a> · <a href="feature-map.ja.md">日本語</a> · <a href="feature-map.ru.md">Русский</a> · <a href="feature-map.es.md">Español</a> · <a href="feature-map.fr.md">Français</a></p>
<!-- translations:end -->
Este documento resume las funciones implementadas actualmente en LLM-Wiki, con su estado, archivos fuente y dónde están documentadas.

Leyenda de estado: ✅ publicado · ⚠ en progreso / parcial.

## Rediseño del frontend — abril de 2026

Una wiki jerárquica centrada en documentos reemplaza el antiguo volcado de grafos. Consulta [`docs/frontend-redesign.md`](frontend-redesign.es.md) para el recorrido ruta por ruta y [`docs/architecture.md`](architecture.es.md) para el modelo de tres capas.

### Capa wiki (L2 markdown)

| Función | Estado | Fuente | Ancla de documentación |
|---|---|---|---|
| `WikiPageStore` (escrituras idempotentes con body-hash, parser de frontmatter) | ✅ | [`llm_wiki/wiki_store.py`](../../llm_wiki/wiki_store.py) | [architecture.md § Mapa de módulos](architecture.es.md#wiki--synthesis-l2) |
| `WikiLayerProjector` — una página md por nodo de la capa wiki | ✅ | [`llm_wiki/wiki_projector.py`](../../llm_wiki/wiki_projector.py) | [architecture.md § Canalización](architecture.es.md#pipeline) |
| Páginas `sources/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Sources](frontend-redesign.es.md#sources) |
| Páginas `concepts/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Concepts](frontend-redesign.es.md#concepts) |
| Páginas `entities/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Entities](frontend-redesign.es.md#entities) |
| Páginas `papers/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Papers](frontend-redesign.es.md#papers) |
| Páginas `repos/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Repos](frontend-redesign.es.md#repos) |
| Páginas `topics/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Topics](frontend-redesign.es.md#topics) |
| Páginas `questions/` (preguntas abiertas) | ✅ | `wiki_projector.py` | [frontend-redesign.md § Questions](frontend-redesign.es.md#questions) |
| Páginas `syntheses/` | ✅ | [`llm_wiki/synthesis.py`](../../llm_wiki/synthesis.py) | [frontend-redesign.md § Syntheses](frontend-redesign.es.md#syntheses) |

### Tipos de síntesis (L2 → derivado)

`SynthesisProjector` produce siete plantillas deterministas y añade nodos `Synthesis` y aristas `synthesizes` / `summarizes` de vuelta al grafo.

| Tipo | Estado | Fuente | Notas |
|---|---|---|---|
| `pulse` (uno global, alimenta `/`) | ✅ | `synthesis.py` | Se reconstruye en cada compilación. |
| `daily_digest` | ✅ | `synthesis.py` | Uno por `data/research/daily/<date>/`. |
| `weekly` | ✅ | `synthesis.py` | Uno por `data/research/weekly/<iso-week>/`. |
| `topic` | ✅ | `synthesis.py` | Uno por clúster `ResearchTopic` / `ApproachFamily` con ≥ 3 papers. |
| `comparison` | ✅ | `synthesis.py` | Uno por par de `ApproachFamily` que compiten en la misma tarea. |
| `field_overview` | ✅ | `synthesis.py` | Uno por `ResearchField`. |
| Resúmenes mejorados con LLM (activados por variable de entorno) | ⚠ | solo hook | La línea base heurística se entrega; el hook `LLM_WIKI_SYNTHESIS_LLM=1` queda como stub. |

### Rutas del sitio estático

| Ruta | Estado | Fuente | Notas |
|---|---|---|---|
| `/` (inicio, pulse principal) | ✅ | [`llm_wiki/site/pages.py`](../../llm_wiki/site/pages.py) `render_home` | Fila de estadísticas + puntos de entrada curados + actividad reciente. |
| `/sources/`, `/sources/<slug>.html` | ✅ | `pages.py::render_sources_index`, `render_source_detail` | |
| `/concepts/`, `/concepts/<slug>.html` | ✅ | `pages.py::render_concepts_index`, `render_concept_detail` | |
| `/entities/`, `/entities/<slug>.html` | ✅ | `pages.py::render_entities_index`, `render_entity_detail` | |
| `/papers/`, `/papers/<slug>.html` | ✅ | `pages.py::render_papers_index`, `render_paper_detail` | |
| `/repos/`, `/repos/<slug>.html` | ✅ | `pages.py::render_repos_index`, `render_repo_detail` | |
| `/topics/`, `/topics/<slug>.html` | ✅ | `pages.py::render_topics_index`, `render_topic_detail` | |
| `/syntheses/`, `/syntheses/<slug>.html` | ✅ | `pages.py::render_syntheses_index`, `render_synthesis_detail` | |
| `/questions/`, `/questions/<slug>.html` | ✅ | `pages.py::render_questions_index`, `render_question_detail` | |
| `/timeline/` | ✅ | `pages.py::render_timeline` | Mapa de calor + lista de días + carril de síntesis. |
| `/timeline/<YYYY-MM-DD>.html` (detalle por día) | ⚠ | aún n/a | Las celdas del mapa de calor enlazan provisionalmente a la página fuente `digest.md` de ese día. Subagent P está conectando las páginas de detalle diario mediante `StaticSiteBuilder`. |
| `/graph/` (2D + 3D interactivo) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, tooltips al pasar el cursor, etiquetas de aristas, zoom anclado al cursor. |
| `/about.html` | ✅ | `pages.py::render_about` | Esquema, información de compilación. |

### Exportaciones amigables para IA

| Artefacto | Estado | Fuente | Propósito |
|---|---|---|---|
| Archivo hermano `<page>.txt` por página | ✅ | [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) `write_siblings` | Vista en texto plano de una página (sin navegación ni estilos). |
| Archivo hermano `<page>.json` por página | ✅ | `exports.py::write_siblings` | `{title, kind, body, body_text, links, source_path, frontmatter}`. |
| `llms.txt` | ✅ | `exports.py::render_llms_txt` | Índice corto de llmstxt.org. |
| `llms-full.txt` | ✅ | `exports.py::render_llms_full_txt` | Cuerpo de todas las páginas, limitado a 5 MB. |
| `graph.jsonld` | ✅ | `exports.py::render_graph_jsonld` | `Dataset` de schema.org, solo nodos de la capa wiki. |
| `graph.json` | ✅ | `__init__.py::write_site` | Payload completo del grafo (incl. nodos de código para herramientas). |
| `search-index.json` | ✅ | [`llm_wiki/site/search.py`](../../llm_wiki/site/search.py) | Paleta + búsqueda de páginas; solo tipos de la capa wiki. |
| `sitemap.xml` | ✅ | `exports.py::render_sitemap_xml` | Todas las rutas emitidas, `lastmod` desde frontmatter. |
| `rss.xml` | ✅ | `exports.py::render_rss_xml` | Últimas 30 syntheses. |
| `robots.txt` | ✅ | `exports.py::render_robots_txt` | Permisivo — rastrear + indexar. |
| `ai-readme.md` | ✅ | `exports.py::render_ai_readme` | Mapa del sitio legible por máquina. |
| `manifest.json` | ✅ | `__init__.py::_manifest` | sha256 + tamaño de cada archivo emitido (arnés de idempotencia). |

### Diseño visual + UX

| Función | Estado | Fuente | Notas |
|---|---|---|---|
| Tokens de diseño (temas claro + oscuro, acento terracota) | ✅ | [`llm_wiki/site/tokens.py`](../../llm_wiki/site/tokens.py) | Un único paquete CSS en `assets/style.css`. |
| Alternador de tema (persistente, sin destello) | ✅ | [`llm_wiki/site/js.py`](../../llm_wiki/site/js.py) | `data-theme="dark"` en `localStorage`, aplicado antes del pintado. |
| Paleta de búsqueda (`cmd+k` / `ctrl+k` / `/`) | ✅ | `js.py` | Coincidencia difusa sobre `search-index.json`; lista de páginas recientes. |
| TOC derecho fijo | ✅ | `pages.py` + `tokens.py` | Solo escritorio; cajón móvil mediante `<details>`. |
| Mapa de calor de actividad con etiquetas de mes + día de semana | ✅ | `components.py::heatmap_svg` | SVG de 26 semanas, las celdas enlazan al `digest.md` del día. |
| Sparkline (por concepto/entidad) | ✅ | `components.py::sparkline_svg` | Conteos semanales de menciones, últimas 12 semanas. |
| Shell móvil (carril de cajón, navegación inferior, tipografía fluida) | ✅ | `tokens.py` + `pages.py` | Objetivos táctiles ≥ 44 px. |
| Transiciones de página (opacidad 120 ms, prefers-reduced-motion) | ✅ | `tokens.py` | |
| Vista de grafo 3D + 2D (hover, etiquetas de aristas, zoom anclado al cursor) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, vendorizado como snapshot de CDN. |
| Pie de hermanos IA por página | ✅ | `components.py::ai_siblings_footer` | Enlaces en línea al `.txt` y `.json` de la página actual. |
| Páginas de historial de sesiones del arnés | ✅ | [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) + [`llm_wiki/site/sessions.py`](../../llm_wiki/site/sessions.py) | Importación explícita de Claude Code/Codex; índice `/sessions/` y páginas de detalle con turnos markdown, carril izquierdo de turnos, uso de herramientas colapsado y entradas de búsqueda. |

### Canalización + CLI

| Función | Estado | Fuente | Notas |
|---|---|---|---|
| `project compile` llama a synthesis + wiki + site en orden | ✅ | [`llm_wiki/project.py`](../../llm_wiki/project.py) | Fase 3 del plan de rediseño. |
| `project build-site` independiente | ✅ | `project.py` + [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | Lee `wiki/` + `graph.json`, escribe `site/`. |
| `project serve` HTTP local | ✅ | `cli.py` | Servidor stdlib simple. |
| `project deploy` → GitHub Pages | ✅ | [`llm_wiki/deploy.py`](../../llm_wiki/deploy.py) | Push de worktree a `gh-pages`; `--enable-pages` opcional vía CLI `gh`. `--build`, `--dry-run`, `--branch`, `--remote`, `--force`. |
| `project sessions discover/import/list` | ✅ | [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) + `cli.py` | Historial de sesiones entrante para Claude Code/Codex; el descubrimiento es explícito y limitado al directorio de trabajo del proyecto. |
| `project watch` recompila al cambiar | ⚠ | [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | Subagent R está terminando el watcher por sondeo — la superficie de argumentos `--interval`, `--debounce`, `--once`, `--paths`, `--quiet` está lista; el cuerpo del bucle de recompilación se está integrando en esta ronda. |

## Funciones preexistentes (conservadas sin cambios)

### CLI e instalación

- ✅ Paquete Python instalable mediante `pyproject.toml`.
- ✅ Comandos de consola: `llm_wiki`, `llm-wiki`, `llm_wiki_mcp`.
- ✅ `scripts/install.sh` para instalación con `curl | bash`.
- ✅ Instalaciones editables por defecto para desarrollo local rápido.

### Extracción

- ✅ Extractor determinista de notas de investigación con vocabularios controlados de nodos/aristas.
- ✅ Extractor Claude CLI/OAuth para extracción estructurada de mayor calidad sin claves API.
- ✅ Enrutamiento selectivo de Claude por glob y límite de presupuesto.
- ✅ Extractor determinista de código de desarrollo para proyectos Python.
- ✅ Ingesta por lotes con hashing de contenido y soporte `--changed-only`.
- ✅ Lectura de fuentes tolerante a UTF-8 malformado.

### Gobernanza del grafo

- ✅ Lista controlada `ResearchNodeType` — ahora incluye `SYNTHESIS`.
- ✅ Lista blanca controlada de tipos de arista — ahora incluye `synthesizes`, `summarizes`.
- ✅ Validación para rechazar deriva de esquema.
- ✅ Canonicalización de alias.
- ✅ Cola de revisión para nodos casi duplicados ambiguos.
- ✅ Plantilla de decisiones de revisión y flujo de fusionar/mantener separado.
- ✅ Resumen de tendencias del corpus a partir de grafos por archivo.

### Persistencia e informes

- ✅ Exportación Graph JSON.
- ✅ Almacén de grafos SQLite.
- ✅ Almacén de grafos Kuzu opcional.
- ✅ Informe de grafo con conteos, cobertura de evidencia, nodos huérfanos, buckets de fecha y nodos con muchos alias.
- ✅ Informe competitivo que describe ideas absorbidas de MegaMem, Graphiti/Zep, MCP graph servers, agentic RAG.

### Flujo de trabajo local del proyecto

- ✅ `llm_wiki project init`
- ✅ `llm_wiki project ingest`
- ✅ `llm_wiki project compile`
- ✅ `llm_wiki project mcp-config`
- ✅ `llm_wiki project build-site`
- ✅ `llm_wiki project serve`
- ✅ `llm_wiki project deploy` (nuevo — GitHub Pages)
- ✅ `llm_wiki project sessions discover/import/list` (importación explícita de historial de agente local)
- ⚠ `llm_wiki project watch` (en progreso)
- ✅ `llm_wiki project export-agent-harness`
- ✅ `llm_wiki project export-obsidian`
- ✅ `llm_wiki project export-graphiti`
- ✅ `llm_wiki project sync-graphiti`

### Obsidian

- ✅ Exportación de vault lista para abrir.
- ✅ `.obsidian/app.json` y configuración de grafo.
- ✅ Proyección Markdown.
- ✅ Estructura `raw/assets/`.
- ✅ `_meta/dashboard.md` con consulta Dataview.

### Arneses de agente

Archivos de destino generados para:

- ✅ Claude Code: `CLAUDE.md`, `.claude/settings.json`
- ✅ Codex: `AGENTS.md`, `mcp.toml`
- ✅ Gemini: `GEMINI.md`, `.gemini/settings.json`
- ✅ Kiro: steering y configuración MCP
- ✅ Cursor: reglas de proyecto y configuración MCP
- ✅ OpenCode: `AGENTS.md`, `opencode.json`

### Graphiti / hechos temporales

- ✅ Proyección de hechos temporales con campos de procedencia, vigencia, confianza e invalidación.
- ✅ Exportación JSONL de episodios Graphiti sin dependencias.
- ✅ Smoke `sync-graphiti --dry-run` sin Graphiti instalado.
- ✅ Sincronización en vivo opcional con `graphiti_core` y Neo4j.

### Cognee

- ✅ Paquete Cognee JSONL (`nodes.jsonl`, `edges.jsonl`, `manifest.json`).
- ✅ Importación directa opcional solo-adición.
- ✅ Adaptador Cognee cognify opcional respaldado por Codex CLI/OAuth.
- ✅ Rutas de adaptador de embeddings determinista y Ollama para flujos smoke/calidad sin clave API.

### Servidor MCP

- ✅ `llm_wiki_mcp` / `python3 -m llm_wiki.mcp_server` sobre stdio JSON-RPC.
- ✅ Herramientas: `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline`.
- ✅ Registro multiproyecto.

## Pruebas

La suite actual cubre:

- ✅ guardrails de ontología (incl. nuevo nodo `Synthesis` + aristas `synthesizes` / `summarizes`);
- ✅ extracción determinista;
- ✅ parsing/validación del wrapper Claude CLI;
- ✅ enrutamiento selectivo de Claude;
- ✅ flujo de canonicalización/revisión;
- ✅ ingesta por lotes;
- ✅ informes;
- ✅ persistencia SQLite/Kuzu;
- ✅ bundles/import patches de Cognee;
- ✅ exportación/sincronización Graphiti dry-run;
- ✅ flujo CLI del proyecto;
- ✅ exportación de arnés de agente;
- ✅ exportación Obsidian;
- ✅ generación frontend + integridad de enlaces (sin `nodes/codeclass-*.html`);
- ✅ idempotencia del almacén wiki;
- ✅ golden + idempotencia de synthesis projector;
- ✅ componentes, páginas, exportaciones y relevancia del sitio;
- ✅ forma de hermanos IA (`.txt` + `.json` por página);
- ✅ idempotencia end-to-end al compilar dos veces;
- ✅ instalación de paquete y contrato del instalador.
