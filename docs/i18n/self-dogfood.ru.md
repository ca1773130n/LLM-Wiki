# Демо Self-dogfood

<!-- translations:start -->
<p align="center"><a href="../self-dogfood.md">English</a> · <a href="self-dogfood.ko.md">한국어</a> · <a href="self-dogfood.zh.md">中文</a> · <a href="self-dogfood.ja.md">日本語</a> · <a href="self-dogfood.ru.md">Русский</a> · <a href="self-dogfood.es.md">Español</a> · <a href="self-dogfood.fr.md">Français</a></p>
<!-- translations:end -->
Этот проект может индексировать сам себя. Поток self-dogfood доказывает, что LLM-Wiki можно установить, настроить внутри собственного репозитория, загрузить собственные docs/source/tests/scripts, при необходимости обновить Understand Anything и Cognee, скомпилировать графовые артефакты и собрать статический веб-фронтенд.

## Команды

Из корня репозитория:

```bash
# Убедитесь, что shell-команда установлена.
./scripts/install.sh --dir "$PWD"
export PATH="$HOME/.local/bin:$PATH"

# Настройте этот репозиторий как проект LLM-Wiki.
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

# Скомпилируйте настроенные источники.
llm_wiki project compile

# Явно пересоберите статический фронтенд.
llm_wiki project build-site

# Запустите локальную раздачу.
llm_wiki project serve --port 8765
```

Откройте:

```text
http://127.0.0.1:8765/
```

## Сгенерированное рабочее пространство

self-demo записывает сгенерированные артефакты в:

```text
.llm-wiki/
```

Ключевые артефакты:

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

Сгенерированное рабочее пространство намеренно не коммитится по умолчанию. Оно воспроизводимо из исходников репозитория с помощью команд выше.

## Последний проверенный запуск

Проверено `2026-04-27 11:11:23 KST` из самого репозитория LLM-Wiki.

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

Итоговые счетчики артефактов:

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

Основные типы узлов:

```text
CodeFunction:    452
Dependency:       55
CodeClass:        54
Concept:          51
SourceFile:       47
SourceDocument:    7
CodeProject:       1
```

Проверка в браузере:

```text
loaded title: Home · llm_wiki_self
visible stats: 667 nodes / 1020 edges / 55 sources / 7 types
sources page: source evidence table links to per-source pages
source detail: llm_wiki/frontend.py shows 41 nodes, 54 related edges, type mix, node links, and edge table
search smoke: StaticSiteBuilder returned CodeClass and StaticSiteBuilder.write_site results
console: no JavaScript errors on home, sources, source detail, or graph pages
server: TCP *:56821 LISTEN, serving via --host 0.0.0.0
```

## Что это демонстрирует

- Публичный путь установки работает.
- Shell-команда `llm_wiki` работает.
- Репозиторий может подключить локальное для проекта рабочее пространство `.llm-wiki`.
- Исследовательский/документационный markdown и графовые узлы разработческого кода могут сосуществовать.
- Проекции Markdown, Obsidian, frontend, Graphiti, Cognee, SQLite, report и agent-harness создаются из одного графового конвейера.
- Статический HTML-фронтенд может просматривать граф проекта без шага сборки JavaScript.
