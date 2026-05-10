# Архитектура

<!-- translations:start -->
<p align="center"><a href="../architecture.md">English</a> · <a href="architecture.ko.md">한국어</a> · <a href="architecture.zh.md">中文</a> · <a href="architecture.ja.md">日本語</a> · <a href="architecture.ru.md">Русский</a> · <a href="architecture.es.md">Español</a> · <a href="architecture.fr.md">Français</a></p>
<!-- translations:end -->
LLM-Wiki превращает каталог исходных материалов в контролируемый типизированный граф знаний и проецирует этот граф через долговечный слой markdown-wiki в статический, удобный для ИИ сайт. Редизайн апреля 2026 года реорганизовал систему вокруг трехслойной модели Karpathy: сырые свидетельства остаются сырыми, типизированный граф управляет онтологией, а слой markdown-wiki находится между графом и любым отрендеренным выводом. Статический сайт теперь является *рендерером* этого wiki-слоя, а не прямой выгрузкой графа; контролируемая онтология в [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) служит схемой.

## Трехслойная модель Karpathy

Подход Andrej Karpathy к LLM-friendly базам знаний выделяет три слоя, каждый со своей гарантией долговечности:

| Слой | Зона ответственности | Расположение в репозитории | Владелец |
|---|---|---|---|
| L1 — Сырые источники | Буквальные байты, созданные или собранные пользователем. Только добавление. | `data/`, `docs/`, деревья проектов, указанные в `.llm-wiki/config.json` | пользователь |
| L2 — Wiki | Типизированные markdown-страницы (sources, concepts, entities, papers, repos, topics, syntheses, questions) с YAML frontmatter. Идемпотентный слой: пересоздается при каждой компиляции, но перезаписывается только при изменении хэшей содержимого. | `.llm-wiki/wiki/` | `WikiPageStore`, `WikiLayerProjector`, `SynthesisProjector` |
| L3 — Отрендеренный слой | Статический HTML-сайт, AI-sibling экспорты, поисковый индекс, sitemap, JSON-LD. Очищается и перезаписывается при каждой компиляции, но остается байтово стабильным при повторных запусках. | `.llm-wiki/site/` | `StaticSiteBuilder` (`llm_wiki/site/`) |

Схема проходит через все три слоя как отдельная ось: `ResearchGraph` в `graph.json` — это контролируемая онтология, на которую ссылаются страницы L2, а `ResearchNodeType` / whitelist типов ребер в [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) является источником истины о том, какие типы вообще существуют.

Редизайн явно добавил L2. До апреля 2026 года статический сайт проецировался напрямую из `graph.json`; wiki-слой существовал только внутри экспорта Obsidian vault. Его выделение дало нам:

- Единую поверхность, редактируемую человеком (откройте `.llm-wiki/wiki/` в Obsidian или любом markdown-редакторе).
- Идемпотентные пересборки: повторный запуск `project compile` не дает файловых diff, если исходное содержимое не изменилось.
- Журнал эволюции: страницы синтеза со временем накапливаются и позволяют проекту рассказывать о самом себе.

## Конвейер

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

Каждый шаг инкрементален. Экстрактор графа использует хэши содержимого из `manifest.json`, чтобы пропускать неизмененные исходные файлы. `WikiPageStore.write_page` возвращает `False` (и пропускает запись), когда хэш тела совпадает с тем, что уже есть на диске. `StaticSiteBuilder` очищает и заново записывает `.llm-wiki/site/`, но его вывод детерминирован — см. раздел «История идемпотентности» ниже.

## Карта модулей

### Wiki + синтез (L2)

| Модуль | Ответственность |
|---|---|
| [`llm_wiki/wiki_store.py`](../../llm_wiki/wiki_store.py) | Dataclass `WikiPage`, `WikiPageStore` для файлового I/O. Парсер YAML-subset frontmatter только на stdlib. Идемпотентность по хэшу тела. |
| [`llm_wiki/wiki_projector.py`](../../llm_wiki/wiki_projector.py) | `WikiLayerProjector`: сопоставляет каждый узел `ResearchGraph` wiki-слойного типа с markdown-страницей в соответствующей папке `kind/`. |
| [`llm_wiki/synthesis.py`](../../llm_wiki/synthesis.py) | `SynthesisProjector`: детерминированные шаблоны для pulse, daily_digest, weekly, topic, comparison, field_overview. Добавляет узлы `Synthesis` и ребра `synthesizes` / `summarizes` обратно в граф. |

### Граф + онтология

| Модуль | Ответственность |
|---|---|
| [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) | Enum `ResearchNodeType` (включая `SYNTHESIS`), whitelist типов ребер (включая `synthesizes`, `summarizes`), валидация. |
| [`llm_wiki/canonicalization.py`](../../llm_wiki/canonicalization.py) | Каноникализация алиасов + очередь проверки почти дублирующихся сущностей. |
| [`llm_wiki/code_graph.py`](../../llm_wiki/code_graph.py) | Детерминированный Python AST extractor для среза разработки. |
| [`llm_wiki/llm_extractor.py`](../../llm_wiki/llm_extractor.py) | Селективный extractor через Claude CLI/OAuth. |

### Рендерер сайта (L3)

| Модуль | Ответственность |
|---|---|
| [`llm_wiki/site/__init__.py`](../../llm_wiki/site/__init__.py) | `StaticSiteBuilder.write_site`: очищает + пересобирает сайт, обходит все маршруты, генерирует экспорты + AI siblings + manifest. |
| [`llm_wiki/site/pages.py`](../../llm_wiki/site/pages.py) | По одному рендереру на маршрут (home, indexes, detail pages, timeline, graph, about). `SiteContext` передает предварительно рассчитанные индексы, чтобы рендереры оставались чистыми. |
| [`llm_wiki/site/components.py`](../../llm_wiki/site/components.py) | HTML-примитивы: `breadcrumbs`, `card`, `badge`, `node_table`, `edge_list`, `sparkline_svg`, `heatmap_svg`, `toc`, `page_shell`, `ai_siblings_footer`. |
| [`llm_wiki/site/tokens.py`](../../llm_wiki/site/tokens.py) | Design tokens — CSS variables, light + dark themes, layout, typography; здесь стилизованы все компоненты. |
| [`llm_wiki/site/js.py`](../../llm_wiki/site/js.py) | Клиентский JS bundle: search palette, theme toggle, sigma + 3D-force graph view. |
| [`llm_wiki/site/markdown.py`](../../llm_wiki/site/markdown.py) | Markdown-рендерер только на stdlib (links, autolinks, code, emphasis, headings). Без внешней зависимости. |
| [`llm_wiki/site/relevance.py`](../../llm_wiki/site/relevance.py) | Оценка релевантности по четырем сигналам (direct link, source overlap, Adamic-Adar, type affinity), используемая каждым разделом `Related`. |
| [`llm_wiki/site/search.py`](../../llm_wiki/site/search.py) | Сборщик `search-index.json`. Только wiki-layer kinds. |
| [`llm_wiki/site/sessions.py`](../../llm_wiki/site/sessions.py) | Рендереры индекса/деталей сессий для импортированной harness history: секции project-memory summary, лента ходов разговора, рендеринг markdown transcript и свернутые блоки tool-use. |
| [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) | `llms.txt`, `llms-full.txt`, `graph.jsonld`, `sitemap.xml`, `rss.xml`, `robots.txt`, `ai-readme.md`, per-page `.txt`/`.json` siblings. |

### Оркестрация конвейера

| Модуль | Ответственность |
|---|---|
| [`llm_wiki/project.py`](../../llm_wiki/project.py) | `ProjectWiki.compile`: управляет extraction → graph → wiki layer → site. Владеет `ProjectPaths` (`config`, `graph`, `manifest`, `wiki`, `site` и т. д.). |
| [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | Все подкоманды `llm_wiki project …`, включая `compile`, `build-site`, `serve`, `watch`, `deploy`. |
| [`llm_wiki/deploy.py`](../../llm_wiki/deploy.py) | `project deploy`: отправляет `.llm-wiki/site/` в ветку `gh-pages` через worktree, опционально включает Pages через `gh`. |

### Внешние адаптеры (без изменений в этом раунде)

| Модуль | Ответственность |
|---|---|
| [`llm_wiki/obsidian_adapter.py`](../../llm_wiki/obsidian_adapter.py) | Проекция Obsidian vault (раскраска графа, Dataview dashboard, raw assets). |
| [`llm_wiki/agent_harness.py`](../../llm_wiki/agent_harness.py) | Экспорты harness для Claude Code / Codex / Gemini / Kiro / Cursor / OpenCode. |
| [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) | Обнаружение входящих сессий Claude Code/Codex, нормализация, хранение в `.llm-wiki/harness_sessions/` и редактированные markdown-сводки. |
| [`llm_wiki/graphiti_adapter.py`](../../llm_wiki/graphiti_adapter.py) | Temporal-fact JSONL + опциональная live Graphiti sync. |
| [`llm_wiki/cognee_adapter.py`](../../llm_wiki/cognee_adapter.py) | JSONL bundle узлов/ребер Cognee и прямой путь add/cognify. |
| [`llm_wiki/mcp_server.py`](../../llm_wiki/mcp_server.py) | MCP stdio server, exposing `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline`. |

## Структура рабочего пространства проекта

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

Каждый файл можно редактировать вручную; следующая компиляция уважает пользовательские правки, пока хэш тела отличается от того, что записал бы projector. (Правка только body выигрывает; правка frontmatter проигрывает при следующей компиляции, потому что frontmatter генерируется заново.) Пользователи Obsidian могут открывать `.llm-wiki/wiki/` напрямую; существующий адаптер `obsidian_vault/` — отдельная проекция, а не замена.

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

## Что намеренно исключено

Редизайн провел явную границу: узлы code-class и code-function остаются в `graph.json` (поэтому потребители MCP, Cognee и Graphiti все еще их видят), но никогда не получают HTML-страниц, не появляются в `search-index.json` и не появляются в навигации. Это пользовательский контракт — wiki является knowledge base, ориентированной на документы, а не браузером функций.

Конкретно, `StaticSiteBuilder` пропускает любой узел, тип которого отсутствует в карте L2 wiki kinds (`llm_wiki/wiki_projector.py::_KIND_FOR_TYPE`):

- Исключены из L2 + L3: `CodeClass`, `CodeFunction`, `CodeModule`, `Dependency`, `EvidenceSpan`, `SourceFile`, все варианты `Claim` (`Claim`, `ContributionClaim`, `PerformanceClaim`, `ComparisonClaim`, `LimitationClaim`, `CausalClaim`).
- Где они все еще появляются: как bullets, badges, neighbor counts или evidence excerpts inline на связанных wiki-страницах, а также в `graph.json` для downstream tooling.

Если нужен просмотр на уровне кода, направьте LSP / call-graph tool прямо на дерево исходников — это другая задача, чем «wiki о том, что знает этот проект».

## История идемпотентности

Редизайн стремится к **байтово идентичному выводу при двух последовательных запусках `project compile` на неизмененных входных данных**. Составные части:

1. **Извлечение источников** использует хэши содержимого `manifest.json`; неизмененные файлы пропускаются, поэтому граф остается стабильным.
2. **Запись wiki-слоя** идемпотентна на уровне тела. `WikiPageStore.write_page` читает существующий файл, удаляет frontmatter, вычисляет sha256 тела и быстро завершает работу, если новое тело хэшируется так же — даже если новый frontmatter имеет другой timestamp `generated_at`. Это ключевой прием, который сохраняет git diff компактным при пересборке.
3. **Вывод синтеза** несет `content_hash: sha256-…` во frontmatter. Хэш тела вычисляется без `generated_at`, поэтому повторные компиляции на том же графе дают тот же хэш, а узлы `Synthesis` несут тот же `content_hash` в метаданных графа.
4. **Рендеринг сайта** очищает `site/` в начале `write_site`, затем пишет детерминированно: маршруты сортируются, словари выгружаются с `sort_keys=True`, `manifest.json` обходится через `sorted(rglob("*"))`. Два запуска создают байтово идентичные файлы, включая manifest.

Это проверяется в `tests/test_site_pages.py` и end-to-end smoke в `tests/test_project_e2e_redesign.py` (две компиляции, сравнение сайтов, ожидается нулевой file delta).

## Заметки о масштабировании

- **Лимит узлов graph view.** [`MAX_GRAPH_NODES = 1500`](../../llm_wiki/site/pages.py) ограничивает встроенный в страницу payload для интерактивной force layout. После примерно 1500 узлов браузерная симуляция становится медленной на среднем железе, поэтому при превышении лимита страница сначала отбрасывает wiki-layer узлы с наименьшей степенью. Экспортированный `graph.json` не затрагивается — он всегда содержит полный граф. Code nodes фильтруются до применения лимита.
- **Лимит `llms-full.txt`.** В [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) действует защитный лимит 5 MB; если лимит достигнут, файл заканчивается маркером `[TRUNCATED — see graph.jsonld for the full set]`. `graph.jsonld` не ограничен, потому что consumers JSON-LD ожидают полный набор.
- **Поисковый индекс.** Только wiki-layer kinds. Code-graph nodes никогда не попадают в `search-index.json`; цель редизайна для dogfood corpus — < 500 KB, и сегодня мы значительно ниже этого значения.
- **Бюджет байтов на страницу (эмпирическое правило).** Каждая detail page < 60 KB gz HTML, shared CSS < 30 KB, shared JS < 25 KB, sigma vendor только на graph page (~60 KB). Graph view использует 3D-force-graph + Three.js, загруженные один раз; все остальные страницы остаются vanilla.
- **Время компиляции на dogfood.** ~300 markdown-файлов извлекаются менее чем за 5 s на современной dev-машине; рендер сайта добавляет еще ~2 s. Идемпотентность wiki-слоя означает, что последующие компиляции затрагивают только измененные пути.

## Поверхность frontend-взаимодействий

- **Search palette** — `cmd+k` / `ctrl+k` / `/`. Fuzzy match по `search-index.json`, ограниченный wiki kinds. Последние страницы сохраняются в `localStorage`.
- **Theme toggle** — кнопка справа сверху; `data-theme="dark"` хранится в `localStorage` и применяется до paint, чтобы избежать flash.
- **Sticky right TOC** — только desktop; на mobile сворачивается в drawer `<details>`. Генерируется из `<h2>` / `<h3>` в body страницы.
- **Activity heatmap** — 26-недельный SVG с month + weekday labels. Ячейки ссылаются на source page `digest.md` соответствующего дня, если она существует. (Per-day timeline detail pages — `/timeline/<YYYY-MM-DD>.html` — явный follow-up; inline notice в `render_timeline` отмечает это. ⚠ in-progress.)
- **Graph view** — `/graph/`. 3D force layout (3d-force-graph + Three.js) с hover tooltips, edge labels, cursor-anchored zoom и 2D fallback view. Цвета узлов берутся из `ResearchNodeType`.
- **Mobile shell** — drawer rail, bottom nav, fluid type, touch-safe hit targets (≥ 44 px).

## Стратегия тестирования

- **Unit** — `tests/test_wiki_store.py`, `tests/test_synthesis.py`, `tests/test_site_components.py`, `tests/test_site_pages.py`, `tests/test_site_exports.py`, `tests/test_relevance.py`.
- **Идемпотентность** — `tests/test_project_e2e_redesign.py` компилирует дважды и проверяет нулевые diff в `wiki/` и `site/`.
- **Целостность ссылок** — `tests/test_frontend.py` парсит все выпущенные HTML для hrefs и проверяет, что каждая внутренняя ссылка разрешается в сгенерированный файл. `nodes/codeclass-*.html` не создается.
- **AI siblings** — для каждого `path/foo.html` test suite проверяет наличие `path/foo.txt` и `path/foo.json`; JSON парсится и содержит `{title, kind, body, links}`.
- **Без Playwright** — vanilla pytest при `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

## Связанные документы

- [Быстрый старт](quickstart.ru.md) — минимальный путь от `project init` до browsable site.
- [Обзор frontend-редизайна](frontend-redesign.ru.md) — аннотированный tour каждого маршрута.
- [Карта функций](feature-map.ru.md) — что shipped, что in-progress, с указателями на файлы.
- [Self-dogfood demo](self-dogfood.ru.md) — запуск LLM-Wiki против собственного репозитория.
