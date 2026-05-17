# Publishing-Checkliste

<!-- translations:start -->
<p align="center"><a href="../publishing-checklist.md">English</a> · <a href="publishing-checklist.ko.md">한국어</a> · <a href="publishing-checklist.zh.md">中文</a> · <a href="publishing-checklist.ja.md">日本語</a> · <a href="publishing-checklist.ru.md">Русский</a> · <a href="publishing-checklist.es.md">Español</a> · <a href="publishing-checklist.fr.md">Français</a></p>
<!-- translations:end -->
Nutze diese Checkliste, bevor du LLM-Wiki öffentlich präsentierst.

## Repository-Hygiene

- [ ] Die README erklärt, was das Projekt ist und welches Problem es löst.
- [ ] Der Install-Befehl funktioniert aus einer frischen Shell.
- [ ] Der Quickstart nutzt `llm_wiki`, nicht `python3 -m`.
- [ ] Die Architektur-Docs erklären Rohbelege → Graph → Projektionen.
- [ ] Die Feature-Map listet implementierte Features, ohne zukünftige Arbeit zu überverkaufen.
- [ ] Die Session-History-Docs erklären expliziten Import, Privacy-Review, generierte Routen und Transcript-Typografie.
- [ ] Die Self-Dogfood-Demo wurde ausgeführt und dokumentiert.
- [ ] Generierte Artefakte sind reproduzierbar und entweder ignoriert oder absichtlich veröffentlicht.
- [ ] RAG-Anything-Index aktualisiert (falls aktiviert).

## Verifikation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -q
./scripts/install.sh --help
llm_wiki project setup --help
llm_wiki project compile --help
```

## Self-Dogfood

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
  --with-raganything \
  --install-raganything \
  --raganything-parser mineru \
  --run-raganything \
  --run-cognee \
  --install-cognee
llm_wiki project compile
llm_wiki project sessions list
llm_wiki project build-site
llm_wiki project serve --port 8765
```

## Demo-Talking-Points

- LLM-Wiki ist kein generischer Noun-Phrase-Graph. Er nutzt eine kontrollierte Ontologie.
- Research- und Development-Code teilen sich die Infrastruktur, behalten aber distinkte Schemas.
- Markdown und HTML sind Projektionen, keine maßgeblichen Wahrheits-Stores.
- Der Default-Pfad ist lokal und no-API-Key-freundlich.
- Agent-Harnesses und MCP machen den Graph für Coding-Agenten nutzbar.
- Importierte Harness-Session-Seiten verwandeln frühere Claude-Code-/Codex-Arbeit in durchsuchbares Projektgedächtnis, während die Transcript-Discovery explizit bleibt.
