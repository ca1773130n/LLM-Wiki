# Карта функций

<!-- translations:start -->
<p align="center"><a href="../feature-map.md">English</a> · <a href="feature-map.ko.md">한국어</a> · <a href="feature-map.zh.md">中文</a> · <a href="feature-map.ja.md">日本語</a> · <a href="feature-map.ru.md">Русский</a> · <a href="feature-map.es.md">Español</a> · <a href="feature-map.fr.md">Français</a> · <a href="feature-map.de.md">Deutsch</a></p>
<!-- translations:end -->
Этот документ кратко описывает функции, которые сейчас реализованы в LLM-Wiki, с их статусом, исходными файлами и местом в документации.

Легенда статуса: ✅ поставлено · ⚠ в работе / частично.

## Редизайн фронтенда — апрель 2026

Иерархическая wiki, ориентированная на документы, заменяет прежний дамп графа. См. [`docs/frontend-redesign.md`](frontend-redesign.ru.md) для обзора по маршрутам и [`docs/architecture.md`](architecture.ru.md) для трехслойной модели.

### Wiki-слой (L2 markdown)

| Функция | Статус | Источник | Якорь документации |
|---|---|---|---|
| `WikiPageStore` (идемпотентные записи body-hash, парсер frontmatter) | ✅ | [`llm_wiki/wiki_store.py`](../../llm_wiki/wiki_store.py) | [architecture.md § Карта модулей](architecture.ru.md#wiki--synthesis-l2) |
| `WikiLayerProjector` — одна md-страница на узел wiki-слоя | ✅ | [`llm_wiki/wiki_projector.py`](../../llm_wiki/wiki_projector.py) | [architecture.md § Pipeline](architecture.ru.md#pipeline) |
| Страницы `sources/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Sources](frontend-redesign.ru.md#sources) |
| Страницы `concepts/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Concepts](frontend-redesign.ru.md#concepts) |
| Страницы `entities/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Entities](frontend-redesign.ru.md#entities) |
| Страницы `papers/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Papers](frontend-redesign.ru.md#papers) |
| Страницы `repos/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Repos](frontend-redesign.ru.md#repos) |
| Страницы `topics/` | ✅ | `wiki_projector.py` | [frontend-redesign.md § Topics](frontend-redesign.ru.md#topics) |
| Страницы `questions/` (открытые вопросы) | ✅ | `wiki_projector.py` | [frontend-redesign.md § Questions](frontend-redesign.ru.md#questions) |
| Страницы `syntheses/` | ✅ | [`llm_wiki/synthesis.py`](../../llm_wiki/synthesis.py) | [frontend-redesign.md § Syntheses](frontend-redesign.ru.md#syntheses) |

### Виды синтеза (L2 → производные)

`SynthesisProjector` создает семь детерминированных шаблонов и добавляет узлы `Synthesis` плюс ребра `synthesizes` / `summarizes` обратно в граф.

| Вид | Статус | Источник | Примечания |
|---|---|---|---|
| `pulse` (один глобальный, питает `/`) | ✅ | `synthesis.py` | Пересобирается при каждом compile. |
| `daily_digest` | ✅ | `synthesis.py` | Один на `data/research/daily/<date>/`. |
| `weekly` | ✅ | `synthesis.py` | Один на `data/research/weekly/<iso-week>/`. |
| `topic` | ✅ | `synthesis.py` | Один на кластер `ResearchTopic` / `ApproachFamily` с ≥ 3 papers. |
| `comparison` | ✅ | `synthesis.py` | Один на пару `ApproachFamily`, конкурирующих в одной задаче. |
| `field_overview` | ✅ | `synthesis.py` | Один на `ResearchField`. |
| Сводки, улучшенные LLM (через env-флаг) | ⚠ | только hook | Эвристическая базовая версия поставляется; hook `LLM_WIKI_SYNTHESIS_LLM=1` оставлен как stub. |

### Маршруты статического сайта

| Маршрут | Статус | Источник | Примечания |
|---|---|---|---|
| `/` (главная, hero pulse) | ✅ | [`llm_wiki/site/pages.py`](../../llm_wiki/site/pages.py) `render_home` | Строка статистики + отобранные точки входа + недавняя активность. |
| `/sources/`, `/sources/<slug>.html` | ✅ | `pages.py::render_sources_index`, `render_source_detail` | |
| `/concepts/`, `/concepts/<slug>.html` | ✅ | `pages.py::render_concepts_index`, `render_concept_detail` | |
| `/entities/`, `/entities/<slug>.html` | ✅ | `pages.py::render_entities_index`, `render_entity_detail` | |
| `/papers/`, `/papers/<slug>.html` | ✅ | `pages.py::render_papers_index`, `render_paper_detail` | |
| `/repos/`, `/repos/<slug>.html` | ✅ | `pages.py::render_repos_index`, `render_repo_detail` | |
| `/topics/`, `/topics/<slug>.html` | ✅ | `pages.py::render_topics_index`, `render_topic_detail` | |
| `/syntheses/`, `/syntheses/<slug>.html` | ✅ | `pages.py::render_syntheses_index`, `render_synthesis_detail` | |
| `/questions/`, `/questions/<slug>.html` | ✅ | `pages.py::render_questions_index`, `render_question_detail` | |
| `/timeline/` | ✅ | `pages.py::render_timeline` | Тепловая карта + список дней + рельс synthesis. |
| `/timeline/<YYYY-MM-DD>.html` (детали по дню) | ⚠ | пока n/a | Ячейки тепловой карты временно ведут на исходную страницу `digest.md` соответствующего дня. Subagent P подключает дневные detail-страницы через `StaticSiteBuilder`. |
| `/graph/` (интерактивные 2D + 3D) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, подсказки при наведении, подписи ребер, zoom с привязкой к курсору. |
| `/about.html` | ✅ | `pages.py::render_about` | Schema, информация о сборке. |

### Экспорты, удобные для ИИ

| Артефакт | Статус | Источник | Назначение |
|---|---|---|---|
| Соседний файл `<page>.txt` для каждой страницы | ✅ | [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) `write_siblings` | Текстовый вид одной страницы (без навигации и стилей). |
| Соседний файл `<page>.json` для каждой страницы | ✅ | `exports.py::write_siblings` | `{title, kind, body, body_text, links, source_path, frontmatter}`. |
| `llms.txt` | ✅ | `exports.py::render_llms_txt` | Короткий индекс llmstxt.org. |
| `llms-full.txt` | ✅ | `exports.py::render_llms_full_txt` | Тело всех страниц, ограничено 5 MB. |
| `graph.jsonld` | ✅ | `exports.py::render_graph_jsonld` | schema.org `Dataset`, только узлы wiki-слоя. |
| `graph.json` | ✅ | `__init__.py::write_site` | Полный payload графа (вкл. code nodes для tooling). |
| `search-index.json` | ✅ | [`llm_wiki/site/search.py`](../../llm_wiki/site/search.py) | Палитра + поиск страниц; только типы wiki-слоя. |
| `sitemap.xml` | ✅ | `exports.py::render_sitemap_xml` | Все выпущенные маршруты, `lastmod` из frontmatter. |
| `rss.xml` | ✅ | `exports.py::render_rss_xml` | Последние 30 syntheses. |
| `robots.txt` | ✅ | `exports.py::render_robots_txt` | Разрешительный — crawl + index. |
| `ai-readme.md` | ✅ | `exports.py::render_ai_readme` | Машиночитаемая карта сайта. |
| `manifest.json` | ✅ | `__init__.py::_manifest` | sha256 + размер для каждого выпущенного файла (harness идемпотентности). |

### Визуальный дизайн + UX

| Функция | Статус | Источник | Примечания |
|---|---|---|---|
| Design tokens (светлая + темная темы, терракотовый акцент) | ✅ | [`llm_wiki/site/tokens.py`](../../llm_wiki/site/tokens.py) | Один CSS bundle в `assets/style.css`. |
| Переключатель темы (сохраняется, без вспышки) | ✅ | [`llm_wiki/site/js.py`](../../llm_wiki/site/js.py) | `data-theme="dark"` в `localStorage`, применяется до отрисовки. |
| Поисковая палитра (`cmd+k` / `ctrl+k` / `/`) | ✅ | `js.py` | Нечеткое совпадение по `search-index.json`; список недавних страниц. |
| Липкий правый TOC | ✅ | `pages.py` + `tokens.py` | Только desktop; mobile drawer через `<details>`. |
| Тепловая карта активности с метками месяцев + дней недели | ✅ | `components.py::heatmap_svg` | SVG на 26 недель, ячейки ведут на дневной `digest.md`. |
| Sparkline (по concept/entity) | ✅ | `components.py::sparkline_svg` | Недельные счетчики упоминаний, последние 12 недель. |
| Mobile shell (drawer rail, bottom nav, fluid type) | ✅ | `tokens.py` + `pages.py` | Сенсорные цели ≥ 44 px. |
| Переходы страниц (opacity 120 ms, prefers-reduced-motion) | ✅ | `tokens.py` | |
| 3D + 2D вид графа (hover, подписи ребер, zoom с привязкой к курсору) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, vendored как CDN snapshot. |
| Footer AI-соседей на странице | ✅ | `components.py::ai_siblings_footer` | Inline-ссылки на `.txt` и `.json` текущей страницы. |
| Страницы истории сессий harness | ✅ | [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) + [`llm_wiki/site/sessions.py`](../../llm_wiki/site/sessions.py) | Явный импорт Claude Code/Codex; индекс `/sessions/` и detail-страницы с markdown turns, левым turn rail, свернутым tool use и search entries. |

### Pipeline + CLI

| Функция | Статус | Источник | Примечания |
|---|---|---|---|
| `project compile` вызывает synthesis + wiki + site по порядку | ✅ | [`llm_wiki/project.py`](../../llm_wiki/project.py) | Фаза 3 плана редизайна. |
| `project build-site` standalone | ✅ | `project.py` + [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | Читает `wiki/` + `graph.json`, пишет `site/`. |
| `project serve` локальный HTTP | ✅ | `cli.py` | Простой stdlib server. |
| `project deploy` → GitHub Pages | ✅ | [`llm_wiki/deploy.py`](../../llm_wiki/deploy.py) | Worktree push в `gh-pages`; опциональный `--enable-pages` через `gh` CLI. `--build`, `--dry-run`, `--branch`, `--remote`, `--force`. |
| `project sessions discover/import/list` | ✅ | [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) + `cli.py` | Входящая история сессий для Claude Code/Codex; обнаружение явное и ограничено рабочим каталогом проекта. |
| `project watch` rebuild-on-change | ⚠ | [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | Subagent R завершает polling watcher — поверхность аргументов `--interval`, `--debounce`, `--once`, `--paths`, `--quiet` готова; тело rebuild loop приземляется в этом раунде. |

## Ранее существовавшие функции (перенесены без изменений)

### CLI и установка

- ✅ Устанавливаемый Python package через `pyproject.toml`.
- ✅ Console commands: `llm_wiki`, `llm-wiki`, `llm_wiki_mcp`.
- ✅ `scripts/install.sh` для установки `curl | bash`.
- ✅ Editable installs по умолчанию для быстрой локальной разработки.

### Извлечение

- ✅ Детерминированный extractor исследовательских заметок с контролируемыми словарями nodes/edges.
- ✅ Claude CLI/OAuth extractor для более качественного структурированного извлечения без API keys.
- ✅ Выборочная маршрутизация Claude по glob и budget limit.
- ✅ Детерминированный extractor development-code для Python проектов.
- ✅ Batch ingest с content hashing и поддержкой `--changed-only`.
- ✅ Чтение источников с терпимостью к некорректному UTF-8.

### Управление графом

- ✅ Контролируемый список `ResearchNodeType` — теперь включает `SYNTHESIS`.
- ✅ Контролируемый whitelist edge types — теперь включает `synthesizes`, `summarizes`.
- ✅ Валидация для отклонения schema drift.
- ✅ Каноникализация alias.
- ✅ Review queue для неоднозначных почти-дубликатов nodes.
- ✅ Шаблон review decisions и workflow merge/keep-separate.
- ✅ Сводка трендов корпуса из графов по файлам.

### Персистентность и отчеты

- ✅ Экспорт Graph JSON.
- ✅ SQLite graph store.
- ✅ Опциональный Kuzu graph store.
- ✅ Graph report с counts, evidence coverage, orphan nodes, date buckets, alias-heavy nodes.
- ✅ Competitive report с описанием идей, заимствованных из MegaMem, Graphiti/Zep, MCP graph servers, agentic RAG.

### Project-local workflow

- ✅ `llm_wiki project init`
- ✅ `llm_wiki project ingest`
- ✅ `llm_wiki project compile`
- ✅ `llm_wiki project mcp-config`
- ✅ `llm_wiki project build-site`
- ✅ `llm_wiki project serve`
- ✅ `llm_wiki project deploy` (новое — GitHub Pages)
- ✅ `llm_wiki project sessions discover/import/list` (явный импорт локальной agent-history)
- ⚠ `llm_wiki project watch` (в работе)
- ✅ `llm_wiki project export-agent-harness`
- ✅ `llm_wiki project export-obsidian`
- ✅ `llm_wiki project export-graphiti`
- ✅ `llm_wiki project sync-graphiti`

### Obsidian

- ✅ Готовый к открытию vault export.
- ✅ `.obsidian/app.json` и настройки графа.
- ✅ Markdown projection.
- ✅ Структура `raw/assets/`.
- ✅ `_meta/dashboard.md` с Dataview query.

### Agent harnesses

Создаваемые target files для:

- ✅ Claude Code: `CLAUDE.md`, `.claude/settings.json`
- ✅ Codex: `AGENTS.md`, `mcp.toml`
- ✅ Gemini: `GEMINI.md`, `.gemini/settings.json`
- ✅ Kiro: steering and MCP settings
- ✅ Cursor: project rules and MCP config
- ✅ OpenCode: `AGENTS.md`, `opencode.json`

### Graphiti / temporal facts

- ✅ Проекция temporal facts с полями provenance, currentness, confidence и invalidation.
- ✅ Dependency-free экспорт Graphiti episode JSONL.
- ✅ Smoke `sync-graphiti --dry-run` без установленного Graphiti.
- ✅ Опциональная live sync с `graphiti_core` и Neo4j.

### Cognee

- ✅ Cognee JSONL bundle (`nodes.jsonl`, `edges.jsonl`, `manifest.json`).
- ✅ Опциональный add-only direct import.
- ✅ Опциональный Cognee cognify adapter на базе Codex CLI/OAuth.
- ✅ Детерминированный и Ollama embedding adapter paths для no-API-key smoke/quality workflows.

### MCP server

- ✅ `llm_wiki_mcp` / `python3 -m llm_wiki.mcp_server` поверх stdio JSON-RPC.
- ✅ Tools: `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline`.
- ✅ Multi-project registry.

## Тесты

Текущий набор покрывает:

- ✅ ontology guardrails (вкл. новый узел `Synthesis` + ребра `synthesizes` / `summarizes`);
- ✅ deterministic extraction;
- ✅ parsing/validation обертки Claude CLI;
- ✅ selective Claude routing;
- ✅ workflow canonicalization/review;
- ✅ batch ingest;
- ✅ reports;
- ✅ SQLite/Kuzu persistence;
- ✅ Cognee bundles/import patches;
- ✅ Graphiti export/sync dry-run;
- ✅ project CLI workflow;
- ✅ agent harness export;
- ✅ Obsidian export;
- ✅ frontend generation + link integrity (без `nodes/codeclass-*.html`);
- ✅ wiki store idempotence;
- ✅ synthesis projector golden + idempotence;
- ✅ site components, pages, exports, relevance;
- ✅ форма AI-sibling (`.txt` + `.json` на страницу);
- ✅ end-to-end compile-twice idempotence;
- ✅ package install и installer contract.
