# Чеклист публикации

<!-- translations:start -->
<p align="center"><a href="../publishing-checklist.md">English</a> · <a href="publishing-checklist.ko.md">한국어</a> · <a href="publishing-checklist.zh.md">中文</a> · <a href="publishing-checklist.ja.md">日本語</a> · <a href="publishing-checklist.ru.md">Русский</a> · <a href="publishing-checklist.es.md">Español</a> · <a href="publishing-checklist.fr.md">Français</a></p>
<!-- translations:end -->
Используйте этот чеклист перед публичной презентацией LLM-Wiki.

## Гигиена репозитория

- [ ] README объясняет, что это за проект и какую проблему он решает.
- [ ] Команда установки работает из свежего shell.
- [ ] Quickstart использует `llm_wiki`, а не `python3 -m`.
- [ ] Документация по архитектуре объясняет raw evidence → graph → projections.
- [ ] Карта функций перечисляет реализованные возможности без преувеличения будущей работы.
- [ ] Документация по истории сессий объясняет явный импорт, проверку приватности, сгенерированные routes и transcript typography.
- [ ] Демо Self-dogfood было запущено и задокументировано.
- [ ] Сгенерированные артефакты воспроизводимы и либо игнорируются, либо намеренно публикуются.

## Проверка

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -q
./scripts/install.sh --help
llm_wiki project setup --help
llm_wiki project compile --help
```

## Self-dogfood

```bash
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
llm_wiki project compile
llm_wiki project sessions list
llm_wiki project build-site
llm_wiki project serve --port 8765
```

## Тезисы для демо

- LLM-Wiki — не универсальный граф именных фраз. Он использует контролируемую ontology.
- Исследовательский и разработческий код используют общую инфраструктуру, но сохраняют разные schema.
- Markdown и HTML — это проекции, а не авторитетные хранилища истины.
- Путь по умолчанию локален и удобен без API key.
- Агентские harness и MCP делают граф пригодным для coding agents.
- Импортированные страницы сессий harness превращают предыдущую работу Claude Code/Codex в доступную для поиска память проекта, сохраняя обнаружение transcript явным.
