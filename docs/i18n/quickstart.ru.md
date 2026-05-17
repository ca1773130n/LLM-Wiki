# Быстрый старт

<!-- translations:start -->
<p align="center"><a href="../quickstart.md">English</a> · <a href="quickstart.ko.md">한국어</a> · <a href="quickstart.zh.md">中文</a> · <a href="quickstart.ja.md">日本語</a> · <a href="quickstart.ru.md">Русский</a> · <a href="quickstart.es.md">Español</a> · <a href="quickstart.fr.md">Français</a> · <a href="quickstart.de.md">Deutsch</a></p>
<!-- translations:end -->
Эта страница показывает самый короткий путь от существующего каталога проекта до просматриваемого LLM-Wiki.

## 1. Запустите мастер настройки

Из проекта, который вы хотите проиндексировать:

```bash
cd /path/to/my-project
llm_wiki project setup
```

Мастер обнаруживает обычные sources вроде `README.md`, `docs`, `src`, `lib`, `app`, `packages` и `data`, затем записывает `.llm-wiki/config.json`. Он также настраивает backend Cognee по умолчанию, чтобы `project ask` мог попробовать Cognee и fallback к compiled wiki search.

Полностью автоматическая настройка с включёнными Understand Anything и Cognee runtime memory:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

Что это делает:

| Flag | Effect |
|---|---|
| `--with-understand-anything` | Добавляет UA graph projection как source. |
| `--install-understand-anything` | Устанавливает/обновляет UA companion skills. |
| `--understand-anything-platform codex` | Использует Codex для запуска managed UA refresh wrapper LLM-Wiki. |
| `--run-cognee` | Запускает best-effort Cognee runtime cognify во время compile. |
| `--install-cognee` | Устанавливает Cognee текущим Python, если он отсутствует. |

Пользователям не нужно знать UA install path или вводить `/understand`; `project compile` запускает `project refresh-understand-anything`, когда UA graph отсутствует или устарел.

## 2. Скомпилируйте граф и projections

```bash
llm_wiki project compile
```

`project compile` записывает durable artifacts:

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

После первого запуска используйте `--changed-only`, чтобы пропускать неизменённые markdown-файлы и сохранять предыдущий graph, когда файлы не менялись. Если Understand Anything включён, compile сначала refresh/materialize `.llm-wiki/external/understand-anything.md`; если включён Cognee runtime, он также best-effort обновляет Cognee после записи `.llm-wiki/cognee_bundle/`.

## 3. Соберите и запустите статический frontend

```bash
llm_wiki project build-site
llm_wiki project serve --port 8765
```

Откройте:

```text
http://127.0.0.1:8765/
```

<!-- BEGIN: subagent-r-watch -->
### Автопересборка при сохранении

Совместите dev server с polling watcher, чтобы правки в `data/` и `docs/` запускали incremental recompile:

```bash
# terminal 1
python3 -m http.server 56821 --directory .llm-wiki/site

# terminal 2
llm_wiki project watch
```

`project watch` выполняет polling каждые 2 s, debounce 1 s и запускает `compile --changed-only`. Используйте `--once` для cron-style rebuilds (snapshots vs `.llm-wiki/.watch-cache.json`), `--paths <dir>` для custom watch dirs и `--interval` / `--debounce` для настройки cadence.
<!-- END: subagent-r-watch -->

Аннотированный tour по всем видимым route — home, sources, concepts, entities, papers, repos, topics, syntheses, questions, timeline, graph, плюс AI siblings — см. в [`docs/frontend-redesign.md`](frontend-redesign.ru.md).

Frontend имеет мало зависимостей и записывает:

```text
.llm-wiki/site/index.html
.llm-wiki/site/sessions/index.html
.llm-wiki/site/graph.json
.llm-wiki/site/search-index.json
.llm-wiki/site/llms.txt
```

## 4. Импортируйте локальную историю agent-сессий

Импорт истории сессий явный: обычные compile/build читают уже нормализованные сессии, но не сканируют сами по себе приватные transcript stores Claude Code или Codex.

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

Импортированные сессии появляются в global Sessions section, site search и home Browse cards. Страницы detail сессий рендерят user/assistant turns как читаемый markdown, прикрепляют tool-use blocks под предыдущим assistant turn и показывают левый turn rail для навигации `#turn-N`. Privacy notes, import formats и текущую transcript typography map см. в [`docs/session-history.md`](session-history.ru.md).

## 5. Lint wiki

```bash
llm_wiki project lint
```

Обходит compiled graph + wiki + site и отмечает orphan papers, stale citations, drift между graph и wiki/, ghost synthesis inputs и другое. Записывает `.llm-wiki/lint-report.md` и `.llm-wiki/lint-report.json`. Передайте `--fix-trivial`, чтобы применить безопасные auto-fixes (missing `implemented_in` edges, ghost-input pruning), и `--severity error`, чтобы exit code падал только на errors.

## 6. Запрос к wiki

```bash
llm_wiki project query "What is Gaussian Splatting?"
```

По умолчанию только поиск — BM25 по `.llm-wiki/site/search-index.json` с 200-char excerpt из подходящего `wiki/<kind>/<slug>.md`. Передайте `--kind papers` (или `concepts`, `repos` и т. д.), чтобы сузить, `--top-k N`, чтобы расширить, и `--json` для структурированного вывода. Добавьте `--llm` (или установите `LLM_WIKI_QUERY_LLM=1`), чтобы попросить Claude синтезировать ответ с citations `[node_id]`; `--interactive` открывает readline REPL — пустая строка или EOF выходят. `LLM_WIKI_QUERY_DRY_RUN=1` проверяет prompt без API-вызова.

## 7. Экспортируйте agent harness files

```bash
llm_wiki project export-agent-harness
```

Поддерживаемые targets:

- Claude Code
- Codex
- Gemini
- Kiro
- Cursor
- OpenCode

Пример subset:

```bash
llm_wiki project export-agent-harness \
  --target claude-code \
  --target cursor \
  --target opencode
```

## 8. Экспортируйте Obsidian vault

```bash
llm_wiki project export-obsidian
```

Или запишите в существующий vault:

```bash
llm_wiki project export-obsidian --vault "$OBSIDIAN_VAULT_PATH"
```

Vault включает markdown projections, defaults `.obsidian`, graph coloring, `raw/assets/` и Dataview dashboard.

## 9. Настройте MCP

```bash
llm_wiki project mcp-config --server-name my_project_wiki
```

Вставьте вывод под `mcp_servers` в `~/.hermes/config.yaml`, затем перезапустите Hermes/gateway.

## 10. Graphiti export / sync

Dependency-free episode export:

```bash
llm_wiki project export-graphiti
```

Dry-run sync smoke без установленного Graphiti:

```bash
llm_wiki project sync-graphiti --dry-run
```

Live sync требует `graphiti_core` и доступный Neo4j backend:

```bash
llm_wiki project sync-graphiti \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-password '<password>'
```

## 11. Деплой на GitHub Pages

Push compiled site из `.llm-wiki/site/` в branch `gh-pages` git origin проекта:

```bash
llm_wiki project deploy --build --enable-pages
```

`--build` сначала запускает `project compile`, чтобы site был свежим. `--enable-pages` включает Pages через `gh` CLI (idempotent; пропускается с подсказкой, если `gh` отсутствует). Используйте `--dry-run`, чтобы stage и commit без push, `--branch` / `--remote` для переопределения defaults и `--force`, чтобы разрешить деплой с dirty working tree.

Сайт станет доступен по `https://<owner>.github.io/<repo>/`.
