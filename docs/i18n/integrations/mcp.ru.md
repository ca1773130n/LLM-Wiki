# MCP — подключение LLM-Wiki к Claude Code, Codex, Cursor

<!-- translations:start -->
<p align="center"><a href="../../integrations/mcp.md">English</a> · <a href="mcp.ko.md">한국어</a> · <a href="mcp.zh.md">中文</a> · <a href="mcp.ja.md">日本語</a> · <a href="mcp.es.md">Español</a> · <a href="mcp.fr.md">Français</a></p>
<!-- translations:end -->

LLM-Wiki поставляется со stdio-сервером [Model Context Protocol](https://modelcontextprotocol.io), который открывает скомпилированный типизированный граф любому MCP-совместимому клиенту: Claude Code, Codex CLI, Cursor, Claude Desktop и другим. Сервер объявляет три полноценные поверхности MCP — **tools**, **resources** и **prompts** — поэтому клиенты могут как запрашивать граф по требованию, так и дешево подгружать контекст из канонических URI.

## Предварительные требования

Сервер читает из `.llm-wiki/graph.json`, поэтому требуется однократная компиляция:

```bash
cd /path/to/your-project
llm_wiki project setup    # interactive; or --yes for non-interactive
llm_wiki project compile  # deterministic, no LLM calls, no API keys
```

Перекомпилируйте при каждом изменении источников. Сервер подхватит новый граф при следующем вызове инструмента без необходимости перезапуска.

## 1) Сгенерируйте конфиг клиента

```bash
llm_wiki project mcp-config
```

Выводит JSON-фрагмент, примерно такой:

```json
{
  "mcpServers": {
    "llm-wiki": {
      "command": "python3",
      "args": [
        "-m", "llm_wiki.mcp_server",
        "--graph", "/path/to/your-project/.llm-wiki/graph.json"
      ]
    }
  }
}
```

Точный путь подставляется из текущего проекта. Передайте `--name <alias>`, если хотите задать имя записи сервера, отличное от `llm-wiki`.

## 2) Вставьте его в свой MCP-клиент

| Клиент | Расположение конфига |
|---|---|
| Claude Code | `~/.claude/mcp-servers.json` (или `~/.config/claude-code/mcp-servers.json`) |
| Claude Desktop | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Codex CLI | `~/.config/codex/mcp-servers.json` |
| Cursor | Settings → MCP Servers → вставьте JSON |
| Hermes | `~/.hermes/config.toml` (используйте TOML-эквивалентный блок, выводимый `mcp-config --format hermes`) |

После редактирования перезапустите клиент. Следующая сессия подключится и обнаружит поверхность LLM-Wiki.

## 3) Что видит клиент

### Tools — вызываются моделью

| Инструмент | Назначение |
|---|---|
| `schema` | Управляемый словарь node, edge и wiki-kind |
| `graph_summary` | Количество узлов и рёбер и распределение типов для активного проекта |
| `search_nodes` | Фильтрация узлов графа по запросу, типу, виду, с топ-N по релевантности |
| `node_context` | Узел + его инцидентные рёбра + соседние узлы |
| `search_facts` | Временные факты, спроецированные из графа (в стиле Graphiti) |
| `timeline` | Факты, упорядоченные по `valid_from`, для лонгитюдного представления |
| `wiki_page` | Тело скомпилированной markdown-страницы для узла |
| `raw_source` | Исходный markdown (с ограничением до 16 KB) |
| `lint_report` | Последние находки lint, полученные на этапе компиляции |
| `ask` | Вопрос–ответ на естественном языке через настроенный бэкенд памяти (raganything, cognee или скомпилированную wiki) |
| `list_projects` / `register_project` / `activate_project` / `unregister_project` | Управление реестром нескольких проектов |

### Resources — автоматически подгружаются в контекст модели

URI, которые клиент может подтянуть через свой пикер ресурсов, не тратя ход инструмента:

- `llm-wiki://graph/schema` — та же полезная нагрузка, что и у инструмента `schema`, готовая как статический контекст
- `llm-wiki://graph/summary` — сводка по активному проекту
- `llm-wiki://lint-report` — последний lint-отчет в виде markdown

Плюс шаблоны URI, которые клиент может конструировать по требованию:

- `llm-wiki://wiki/{kind}/{slug}` — тело любой скомпилированной wiki-страницы
- `llm-wiki://raw/{source_path}` — любой исходный markdown

### Prompts — исследовательские шаблоны в один клик

Эти шаблоны появляются в slash-меню клиента (например, в палитре `/` Claude Code):

| Промпт | Аргументы | Что делает |
|---|---|---|
| `summarize-paper` | `slug` (обязательный) | Вызывает `node_context` + `wiki_page` + опционально `raw_source`, затем возвращает структурированное саммари: вклад, набросок метода, ключевые результаты, ограничения, связанные узлы |
| `find-related-work` | `topic` (обязательный), `limit` | Объединяет `search_nodes` + `node_context` для топ-K связанных элементов с обоснованиями релевантности |
| `compare-approaches` | `a`, `b` (оба обязательные) | Подтягивает `node_context` для обоих + `search_facts` для заявлений о производительности; возвращает сравнение бок о бок с синтезом |
| `gap-analysis` | `topic` (необязательный) | Выявляет нерешенные открытые вопросы, отсутствующие бенчмарки, недостаточно подкрепленные утверждения |
| `triage-open-questions` | _нет_ | Перечисляет все узлы `OpenQuestion`, группирует по теме, предлагает порядок приоритетов |

Каждый промпт рендерится в одно пользовательское сообщение, которое точно сообщает модели, какие инструменты LLM-Wiki связать в цепочку, чтобы модель не пересоткрывала поверхность каждый раз заново.

## Multi-project: регистрация нескольких vault под одним сервером

Постоянный реестр в `~/.llm-wiki/registry.json` позволяет одному и тому же MCP-серверу разрешать любой зарегистрированный проект по имени:

```bash
llm_wiki register-project /path/to/research --name research
llm_wiki register-project /path/to/notes    --name notes
```

После этого каждый инструмент, принимающий `project` или `graph_path`, будет разрешать `project: "research"` по реестру, не требуя полного пути. Сервер даже проверяет, что зарегистрированный `graph_path` всё ещё существует, и возвращает понятную ошибку, если нужна перекомпиляция.

### Fan-out по всем зарегистрированным vault

Инструмент `ask` принимает `scope: "all-registered"` для параллельного запроса по каждому зарегистрированному проекту и возврата агрегированных результатов:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "Where is splatting used?",
    "scope": "all-registered"
  }
}
```

Ограничьте подмножеством через `scope_aliases: ["research", "notes"]`.

## Multi-account Claude CLI

Если ваш инструмент `ask` маршрутизируется через Claude CLI и у вас несколько аккаунтов (например, `~/.claude` и `~/.claude-personal2`), передавайте `claude_config_dir` для каждого вызова:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "...",
    "claude_config_dir": "/Users/you/.claude-personal2"
  }
}
```

Сервер экспортирует `CLAUDE_CONFIG_DIR` только на время этого вызова и восстанавливает предыдущее значение после. Никаких утечек между вызовами.

## Проверка

После перезапуска MCP-клиента подтвердите соединение:

- Claude Code: `/mcp` должен показать `llm-wiki` с количеством инструментов.
- Cursor: иконка MCP в чате должна показывать `llm-wiki: connected` с количеством tools/resources/prompts.
- Codex / Hermes: вызовите любой инструмент по имени (например, `schema`) и проверьте ответ.

Если ничего не появляется, дважды проверьте, что `--graph` указывает на существующий `.llm-wiki/graph.json` — сервер теперь валидирует это при старте и при каждом вызове инструмента, так что вы увидите понятное сообщение об ошибке вместо безмолвного 500.

## Где это уместно

MCP-сервер — это **интерфейс чтения** типизированного графа. Для **пути записи** (загрузка источников, перекомпиляция, обновление сопутствующих инструментов вроде RAG-Anything или Understand-Anything) используйте CLI напрямую. Эти две части развязаны: CLI обновляет `.llm-wiki/`, а MCP-сервер читает то, что там лежит, при следующем вызове инструмента.
