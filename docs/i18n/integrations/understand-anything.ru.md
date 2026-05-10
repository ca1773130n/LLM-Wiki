# Сопутствующий рабочий процесс Understand Anything

<!-- translations:start -->
<p align="center"><a href="../../integrations/understand-anything.md">English</a> · <a href="understand-anything.ko.md">한국어</a> · <a href="understand-anything.zh.md">中文</a> · <a href="understand-anything.ja.md">日本語</a> · <a href="understand-anything.ru.md">Русский</a> · <a href="understand-anything.es.md">Español</a> · <a href="understand-anything.fr.md">Français</a></p>
<!-- translations:end -->
[Understand Anything](https://github.com/Lum1104/Understand-Anything) и LLM-Wiki — взаимодополняющие проекты.

- Understand Anything хорошо создает граф знаний кодовой базы и интерактивную панель.
- LLM-Wiki сосредоточен на долговременной памяти агентов: документах, компиляции markdown/wiki, статической публикации, истории сессий и экспортах для агентов.

LLM-Wiki не должен встраивать или поглощать Understand Anything. Рассматривайте его как независимый сопутствующий инструмент, который может создавать полезные графовые артефакты.

## Зачем использовать оба?

Understand Anything может записывать:

```text
.understand-anything/knowledge-graph.json
```

Этот граф фиксирует структуру кода: файлы, функции, классы, модули, концепции, зависимости, слои и туры.

Затем LLM-Wiki может сохранить этот артефакт вместе с остальной памятью проекта:

- исходные документы и markdown-страницы;
- файлы репозитория;
- исследовательские заметки;
- локальную историю сессий Claude Code / Codex;
- сгенерированные статические wiki-страницы;
- 2D / 3D представления сайта графа;
- `llms.txt`, `llms-full.txt`, `search-index.json`, `graph.json` и агентские sibling-файлы для каждой страницы.

## Текущий рабочий процесс с низким трением

Рекомендуемый путь — мастер настройки:

```bash
llm_wiki project setup
```

Выберите Understand Anything на шаге сопутствующих инструментов. LLM-Wiki установит/обновит сопутствующие skills по запросу и запишет управляемую команду обновления в `.llm-wiki/config.json`. Последующие вызовы `llm_wiki project compile` будут автоматически запускать эту обертку, когда граф UA отсутствует или устарел.

Для неинтерактивной автоматизации используйте:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex
llm_wiki project compile
```

Сохраненная команда принадлежит LLM-Wiki, а не является тем, что пользователь должен придумать сам:

```bash
llm_wiki project refresh-understand-anything --platform codex
```

Во время компиляции LLM-Wiki:

1. проверяет, существует ли `.understand-anything/knowledge-graph.json` и совпадает ли он с текущим git-коммитом, когда доступны метаданные;
2. запускает настроенную агентскую платформу (`codex`, `opencode` или `claude`) только когда граф отсутствует/устарел или обновление принудительное;
3. проверяет, что граф был записан;
4. материализует `.llm-wiki/external/understand-anything.md`;
5. продолжает обычную компиляцию памяти.

Можно принудительно выполнить все настроенные внешние команды обновления перед компиляцией:

```bash
llm_wiki project compile --refresh-external-tools
```

Нужен также Cognee? Добавьте флаги runtime-памяти в ту же команду setup:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

## Ручной эквивалент

Предпочтителен управляемый путь настройки. Если вы намеренно хотите использовать UA вне LLM-Wiki, сначала запустите Understand Anything в вашей агентской среде:

```bash
/understand
```

Затем выполните `llm_wiki project setup --with-understand-anything`, чтобы LLM-Wiki записал источник markdown-проекции. Прямые JSON-файлы сохраняются как сырые сопутствующие артефакты, а не как вручную введенные пути источников.

```bash
llm_wiki project setup --with-understand-anything
llm_wiki project compile
llm_wiki project build-site
```

Если также нужна локальная память агентских сессий:

```bash
llm_wiki project sessions discover --import
llm_wiki project build-site
```

## Возможный будущий мост

Будущий необязательный мост мог бы более напрямую сопоставлять схему графа Understand Anything с typed graph ontology в LLM-Wiki.

Вероятное сопоставление:

| Understand Anything | направление LLM-Wiki |
|---|---|
| `project` | метаданные репозитория/проекта |
| `nodes[type=file]` | узлы исходников/документов/файлов |
| `nodes[type=function]` | узлы функций/символов кода |
| `nodes[type=class]` | узлы классов/символов кода |
| `nodes[type=module]` | узлы модулей/пакетов |
| `nodes[type=concept]` | узлы концепций |
| `edges[type=imports]` | ребра импортов/зависимостей |
| `edges[type=contains]` | ребра включения |
| `edges[type=calls]` | ребра вызовов/ссылок |
| `layers[]` | метаданные архитектурной группировки |
| `tour[]` | страницы онбординга/синтеза |

Сохраняйте этот мост необязательным и внешним, если оба проекта не договорятся о стабильном контракте обмена.

## Принцип сотрудничества

Не представляйте LLM-Wiki как замену Understand Anything.

Лучшее позиционирование:

- Understand Anything помогает разработчику понять кодовую базу сейчас.
- LLM-Wiki помогает агентам со временем помнить, искать, цитировать, обновлять и публиковать знания проекта.
