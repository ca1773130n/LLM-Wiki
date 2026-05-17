# Harness-Session-Historie

<!-- translations:start -->
<p align="center"><a href="../session-history.md">English</a> · <a href="session-history.ko.md">한국어</a> · <a href="session-history.zh.md">中文</a> · <a href="session-history.ja.md">日本語</a> · <a href="session-history.ru.md">Русский</a> · <a href="session-history.es.md">Español</a> · <a href="session-history.fr.md">Français</a></p>
<!-- translations:end -->
LLM-Wiki kann lokale AI-Agent-Transkripte importieren und sie als Projektgedächtnis unter dem `sessions/`-Bereich der statischen Site rendern.

Dieses Feature ist absichtlich von `export-agent-harness` getrennt:

- `export-agent-harness` ist Outbound-Kontext für Tools wie Claude Code, Codex, Gemini, Cursor, Kiro und OpenCode.
- `project sessions ...` ist Inbound-Historie: es normalisiert frühere Claude-Code-/Codex-Sessions für das aktuelle Projekt, speichert sie unter `.llm-wiki/harness_sessions/` und lässt `project build-site` Session-Index-/Detailseiten veröffentlichen.

## Privacy-Modell

Session-Import ist explizit. Ein normaler `project compile` oder `project build-site` liest bereits normalisierte Sessions aus `.llm-wiki/harness_sessions/`, scrapet aber nicht überraschend private Harness-Transcript-Verzeichnisse.

Importierte Session-Records sind lokale Projektartefakte. Überprüfe sie, bevor du eine öffentliche Site publishst, besonders wenn deine Transkripte Secrets, private Pfade, Kundendaten oder unveröffentlichten Code enthalten können.

## Lokale Sessions entdecken und importieren

Aus dem Projekt-Root:

```bash
llm_wiki project sessions discover --import
```

Discovery scannt lokale Claude-Code- und Codex-Transcript-Roots, die zum aktuellen Projekt-Working-Directory gehören. Nutze `--root`, um ein bestimmtes Config-Directory zu scannen, und wiederhole `--harness`, um die Discovery einzugrenzen:

```bash
llm_wiki project sessions discover \
  --root ~/.claude \
  --root ~/.codex \
  --harness claude-code \
  --harness codex \
  --import
```

Ohne `--import` druckt Discovery, was sie gefunden hat, ohne normalisierte Session-Records zu schreiben.

## Normalisiertes JSON direkt importieren

Wenn ein anderes Tool bereits normalisiertes `HarnessSession`-JSON erzeugt hat, importiere eine Datei oder eine Liste von Dateien:

```bash
llm_wiki project sessions import path/to/session.json path/to/more-sessions.json
```

Jeder Input darf ein Session-Objekt oder eine Liste von Session-Objekten enthalten.

## Importierte Sessions auflisten

```bash
llm_wiki project sessions list
```

Sessions werden hier abgelegt:

```text
.llm-wiki/harness_sessions/
  manifest.json
  <harness>/
    <session>.json
    <session>.md
```

## Statische Session-Seiten bauen

Nach dem Import von Sessions die Site neu bauen:

```bash
llm_wiki project build-site
```

Die Site emittiert:

```text
.llm-wiki/site/sessions/index.html
.llm-wiki/site/sessions/<project>/<session>.html
```

Die generierte Site verlinkt Sessions von der globalen Rail, den Home-Browse-Cards, Such-Einträgen und dem Breadcrumb-Trail jeder Session-Detail-Seite.

## Layout der Session-Detail-Seite

Session-Detailseiten nutzen die geteilte Static-Site-Shell statt eines standalone Transcript-Dumps. Sie enthalten:

- Hero und Stat-Strip;
- High-Level-Summary;
- Timeline- und Size-Metadaten;
- Decisions, Files, Commands, Tools und Errors, wenn vorhanden;
- eingeklappten Subagent-Baum;
- Turn-by-Turn-User-/Assistant-Conversation;
- eingeklappte Tool-Use-Blöcke, angehängt unter dem vorhergehenden Assistant-Turn;
- eine Left-Conversation-Rail, die auf `#turn-N`-Anker verlinkt.

Conversation-Markdown wird durch den Site-Markdown-Renderer gerendert. Semantische Flächen wie Inline-Code, explizites Command-/Tag-Markup, Pfade, Filenames und Hashtags werden zu kompakten Chips dekoriert; zufällig großgeschriebene Nomen werden nicht automatisch chipfiziert.

Aktuelle Transcript-Typografie:

| Fläche | Selector | Größe |
|---|---|---|
| Conversation-Markdown-Prosa | `.session-turn-text`, Prose-Kinder | `8px` |
| Generische Conversation-Code-Fences | `.session-turn-text pre` | `10px` |
| Bash-/Shell-Fenced-Code-Content | `.session-code-block code.language-bash`, `.language-sh`, `.language-shell`, `.language-zsh` | `11px` |
| Tool-Details/Summary | `.session-tool-details`, `.session-tool-details > summary` | `10px` |
| Tool-Use-Header | `.session-tool-use-header` | `8px` |
| Tool-Payload-Text | `.session-tool-use-text` | `6px` |

## Publishing-Checkliste für Sessions

Bevor du eine öffentliche Site mit Sessions deployst:

1. Führe `llm_wiki project sessions list` aus und bestätige, dass der Count wie erwartet ist.
2. Inspiziere `.llm-wiki/harness_sessions/` auf sensible Inhalte.
3. Baue neu mit `llm_wiki project build-site`.
4. Öffne `sessions/index.html` und mindestens eine Session-Detail-Seite lokal.
5. Bestätige, dass Tool-Blöcke standardmäßig eingeklappt sind und Raw-Tool-Payloads zum Publishen akzeptabel sind.
6. Deploye mit `llm_wiki project deploy --build`, sobald der Source-Tree committet ist.
