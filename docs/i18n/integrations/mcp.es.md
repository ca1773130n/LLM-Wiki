# MCP — conecta Tesserae con Claude Code, Codex, Cursor

<!-- translations:start -->
<p align="center"><a href="../../integrations/mcp.md">English</a> · <a href="mcp.ko.md">한국어</a> · <a href="mcp.zh.md">中文</a> · <a href="mcp.ja.md">日本語</a> · <a href="mcp.ru.md">Русский</a> · <a href="mcp.fr.md">Français</a> · <a href="mcp.de.md">Deutsch</a></p>
<!-- translations:end -->

Tesserae incluye un servidor stdio de [Model Context Protocol](https://modelcontextprotocol.io) que expone el grafo tipado compilado a cualquier cliente compatible con MCP: Claude Code, Codex CLI, Cursor, Claude Desktop y otros. El servidor anuncia las tres superficies completas de MCP — **tools**, **resources** y **prompts** — de modo que los clientes pueden tanto consultar el grafo bajo demanda como sembrar contexto de forma económica a partir de URIs canónicas.

## Requisitos previos

El servidor lee desde `.tesserae/graph.json`, por lo que se requiere una compilación inicial:

```bash
cd /path/to/your-project
tesserae project setup    # interactive; or --yes for non-interactive
tesserae project compile  # deterministic, no LLM calls, no API keys
```

Recompila siempre que cambien tus fuentes. El servidor recogerá el nuevo grafo en la siguiente llamada a una tool sin necesidad de reiniciar.

## 1) Generar la configuración del cliente

```bash
tesserae project mcp-config
```

Imprime un fragmento JSON aproximadamente así:

```json
{
  "mcpServers": {
    "tesserae": {
      "command": "python3",
      "args": [
        "-m", "tesserae.mcp_server",
        "--graph", "/path/to/your-project/.tesserae/graph.json"
      ]
    }
  }
}
```

La ruta exacta se completa a partir del proyecto actual. Pasa `--name <alias>` si quieres un nombre de entrada de servidor distinto a `tesserae`.

## 2) Pégalo en tu cliente MCP

| Cliente | Ubicación de la configuración |
|---|---|
| Claude Code | `~/.claude/mcp-servers.json` (o `~/.config/claude-code/mcp-servers.json`) |
| Claude Desktop | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Codex CLI | `~/.config/codex/mcp-servers.json` |
| Cursor | Settings → MCP Servers → pega el JSON |
| Hermes | `~/.hermes/config.toml` (usa el bloque equivalente en TOML impreso por `mcp-config --format hermes`) |

Reinicia el cliente después de editarlo. La siguiente sesión se conectará y descubrirá la superficie de Tesserae.

## 3) Lo que ve el cliente

### Tools — invocadas por el modelo

| Tool | Propósito |
|---|---|
| `schema` | Vocabulario controlado de nodos, aristas y wiki-kinds |
| `graph_summary` | Conteo de nodos y aristas y distribución de tipos del proyecto activo |
| `search_nodes` | Filtra nodos del grafo por consulta, tipo, kind, con top-N ordenado por puntaje |
| `node_context` | Un nodo + sus aristas incidentes + nodos vecinos |
| `search_facts` | Hechos temporales proyectados desde el grafo (al estilo Graphiti) |
| `timeline` | Hechos ordenados por `valid_from` para una vista longitudinal |
| `wiki_page` | El cuerpo de la página markdown compilada de un nodo |
| `raw_source` | El markdown fuente original (limitado a 16 KB) |
| `lint_report` | Los hallazgos de lint más recientes en tiempo de compilación |
| `ask` | Preguntas y respuestas en lenguaje natural a través del backend de memoria configurado (raganything, cognee, o wiki compilada) |
| `list_projects` / `register_project` / `activate_project` / `unregister_project` | Control del registro multiproyecto |

### Resources — cargados automáticamente al contexto del modelo

URIs que el cliente puede incorporar mediante su selector de recursos sin gastar un turno de tool:

- `tesserae://graph/schema` — la misma carga útil que la tool `schema`, lista como contexto estático
- `tesserae://graph/summary` — resumen del proyecto activo
- `tesserae://lint-report` — el último lint report en markdown

Además de plantillas de URI que el cliente puede construir bajo demanda:

- `tesserae://wiki/{kind}/{slug}` — el cuerpo de cualquier página wiki compilada
- `tesserae://raw/{source_path}` — cualquier markdown fuente sin procesar

### Prompts — plantillas de investigación de un solo clic

Aparecen en el menú de comandos del cliente (por ejemplo, la paleta `/` de Claude Code):

| Prompt | Argumentos | Qué hace |
|---|---|---|
| `summarize-paper` | `slug` (obligatorio) | Llama a `node_context` + `wiki_page` + opcionalmente `raw_source`, y devuelve un resumen estructurado: contribución, esbozo del método, resultados destacados, limitaciones, nodos relacionados |
| `find-related-work` | `topic` (obligatorio), `limit` | Encadena `search_nodes` + `node_context` para los top-K elementos relacionados con justificaciones de relevancia |
| `compare-approaches` | `a`, `b` (ambos obligatorios) | Recupera `node_context` para ambos + `search_facts` para reclamos de rendimiento; devuelve una comparación lado a lado con síntesis |
| `gap-analysis` | `topic` (opcional) | Saca a la luz preguntas abiertas no resueltas, benchmarks faltantes y afirmaciones poco respaldadas |
| `triage-open-questions` | _ninguno_ | Lista todos los nodos `OpenQuestion`, los agrupa por tema y propone un orden de prioridad |

Cada prompt se renderiza como un único mensaje de usuario que le indica al modelo exactamente qué tools de Tesserae encadenar, así el modelo no tiene que redescubrir la superficie cada vez.

## Multiproyecto: registra varias vaults bajo un mismo servidor

Un registro persistente en `~/.tesserae/registry.json` permite que el mismo servidor MCP resuelva cualquier proyecto registrado por nombre:

```bash
tesserae register-project /path/to/research --name research
tesserae register-project /path/to/notes    --name notes
```

A partir de esto, cada tool que acepte `project` o `graph_path` resolverá `project: "research"` contra el registro en lugar de necesitar una ruta completa. El servidor incluso valida que el `graph_path` registrado siga existiendo y devuelve un error claro si hace falta recompilar.

### Fan-out sobre cada vault registrada

La tool `ask` acepta `scope: "all-registered"` para consultar cada proyecto registrado en paralelo y devolver resultados agregados:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "Where is splatting used?",
    "scope": "all-registered"
  }
}
```

Restringe a un subconjunto con `scope_aliases: ["research", "notes"]`.

## Claude CLI multicuenta

Si tu tool `ask` se enruta a través de la Claude CLI y tienes varias cuentas (por ejemplo, `~/.claude` y `~/.claude-personal2`), pasa `claude_config_dir` por llamada:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "...",
    "claude_config_dir": "/Users/you/.claude-personal2"
  }
}
```

El servidor exporta `CLAUDE_CONFIG_DIR` solo durante esa llamada y restaura el valor anterior al terminar. Sin filtraciones entre llamadas.

## Verificación

Después de reiniciar tu cliente MCP, confirma la conexión:

- Claude Code: `/mcp` debería listar `tesserae` con el conteo de tools.
- Cursor: el icono MCP en la barra de chat debería mostrar `tesserae: connected` con los conteos de tools/resources/prompts.
- Codex / Hermes: invoca cualquier tool por nombre (por ejemplo, `schema`) y revisa la respuesta.

Si no aparece nada, verifica que `--graph` apunte a un `.tesserae/graph.json` existente — el servidor ahora valida esto al arrancar y en cada llamada a tool, así que verás un mensaje de error claro en lugar de un 500 silencioso.

## Dónde encaja esto

El servidor MCP es la **interfaz de lectura** al grafo tipado. Para la **ruta de escritura** (ingestar fuentes, recompilar, refrescar herramientas acompañantes como RAG-Anything o Understand-Anything) usa la CLI directamente. Ambas están desacopladas: la CLI actualiza `.tesserae/`, y el servidor MCP lee lo que haya allí en la siguiente llamada a tool.
