# Understand-Anything-Companion-Workflow

<!-- translations:start -->
<p align="center"><a href="../../integrations/understand-anything.md">English</a> · <a href="understand-anything.ko.md">한국어</a> · <a href="understand-anything.zh.md">中文</a> · <a href="understand-anything.ja.md">日本語</a> · <a href="understand-anything.ru.md">Русский</a> · <a href="understand-anything.es.md">Español</a> · <a href="understand-anything.fr.md">Français</a></p>
<!-- translations:end -->

[Understand Anything](https://github.com/Lum1104/Understand-Anything) und LLM-Wiki sind komplementäre Projekte.

- Understand Anything ist stark darin, einen Codebase-Knowledge-Graph und ein interaktives Dashboard zu erzeugen.
- LLM-Wiki konzentriert sich auf langlebige Agent-Memory: Docs, Markdown-/Wiki-Kompilation, statisches Publishing, Session-History und agent-orientierte Exports.

LLM-Wiki sollte Understand Anything weder vendoren noch absorbieren. Behandle es als unabhängigen Companion, der nützliche Graph-Artefakte produziert.

## Warum beides nutzen?

Understand Anything kann Folgendes schreiben:

```text
.understand-anything/knowledge-graph.json
```

Dieser Graph erfasst Code-Struktur wie Dateien, Funktionen, Klassen, Module, Konzepte, Abhängigkeiten, Layer und Touren.

LLM-Wiki kann dieses Artefakt dann neben dem restlichen Projektgedächtnis aufbewahren:

- Quell-Docs und Markdown-Seiten;
- Repository-Dateien;
- Research-Notizen;
- lokale Claude Code- / Codex-Session-History;
- generierte statische Wiki-Seiten;
- 2D-/3D-Graph-Website-Sichten;
- `llms.txt`, `llms-full.txt`, `search-index.json`, `graph.json` und Per-Page-Agent-Geschwister.

## Aktueller reibungsarmer Workflow

Empfohlen ist der Setup-Wizard:

```bash
llm_wiki project setup
```

Wähle im Schritt „Companion-Tools“ Understand Anything aus. LLM-Wiki installiert/aktualisiert die Companion-Skills auf Wunsch und schreibt einen verwalteten Refresh-Befehl in `.llm-wiki/config.json`. Künftige `llm_wiki project compile`-Aufrufe führen diesen Wrapper automatisch aus, wenn der UA-Graph fehlt oder veraltet ist.

Für nicht-interaktive Automatisierung:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex
llm_wiki project compile
```

Der hinterlegte Befehl gehört LLM-Wiki — nichts, was sich der Nutzer ausdenken muss:

```bash
llm_wiki project refresh-understand-anything --platform codex
```

Während des Compiles geht LLM-Wiki so vor:

1. prüft, ob `.understand-anything/knowledge-graph.json` existiert und mit dem aktuellen git-commit übereinstimmt, sofern Metadaten verfügbar sind;
2. führt die konfigurierte Agent-Plattform (`codex`, `opencode` oder `claude`) nur dann aus, wenn der Graph fehlt/veraltet ist oder ein Refresh erzwungen wurde;
3. verifiziert, dass der Graph geschrieben wurde;
4. materialisiert `.llm-wiki/external/understand-anything.md`;
5. setzt die normale Memory-Kompilation fort.

Du kannst vor einem Compile alle konfigurierten externen Refresh-Befehle erzwingen:

```bash
llm_wiki project compile --refresh-external-tools
```

Cognee zusätzlich nötig? Füge die Runtime-Memory-Flags im selben Setup-Befehl hinzu:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

## Manuelles Äquivalent

Der verwaltete Setup-Pfad ist vorzuziehen. Wenn du UA absichtlich außerhalb von LLM-Wiki nutzen willst, starte Understand Anything zuerst in deiner Agent-Umgebung:

```bash
/understand
```

Führe danach `llm_wiki project setup --with-understand-anything` aus, damit LLM-Wiki die Quelle der Markdown-Projektion festhält. Direkte JSON-Dateien werden als rohe Companion-Artefakte gehalten, nicht als handgepflegte Source-Pfade.

```bash
llm_wiki project setup --with-understand-anything
llm_wiki project compile
llm_wiki project build-site
```

Wenn du zusätzlich lokale Agent-Session-Memory möchtest:

```bash
llm_wiki project sessions discover --import
llm_wiki project build-site
```

## Native Graph-Synchronisation

LLM-Wiki behält die Markdown-Projektion jetzt für die Lesbarkeit bei und importiert den UA-Graphen zusätzlich nativ während des Compiles, sofern das konfigurierte Tool `sync_mode: native_graph` verwendet.

Der native Adapter liest `.understand-anything/knowledge-graph.json`, mappt UA-Nodes/Edges in die kontrollierte Ontologie von LLM-Wiki und schreibt ein Sync-Manifest:

```text
.llm-wiki/external/understand-anything-sync.json
```

Aktuelles Mapping:

| Understand Anything | LLM-Wiki-Ziel |
|---|---|
| `project` | Repository-/Projekt-Metadaten |
| `nodes[type=file]` | `SourceFile` nodes |
| `nodes[type=function]` / `method` | `CodeFunction` nodes |
| `nodes[type=class]` / `component` | `CodeClass` nodes |
| `nodes[type=module]` / `package` | `CodeModule` nodes |
| `nodes[type=concept]` / `topic` | kanonische `Concept` nodes |
| `nodes[type=feature]` / `capability` | `Capability` nodes |
| `edges[type=imports]` | `imports` edges |
| `edges[type=contains]` | `contains` edges |
| `edges[type=calls]` | `calls` edges |
| unbekannte Edge-Typen | `shares_concept_with` mit `ua_edge_type`-Metadaten |

Die Synchronisation von Concepts erfolgt kanonisiert statt blind dupliziert. Wenn UA `Mermaid Rendering` ausgibt und LLM-Wiki bereits `Mermaid rendering` kennt, behält der Compile einen Concept-Node und ergänzt UA-Provenance unter `metadata.external_refs`.

LLM-Wiki bleibt der Memory-Compiler; UA bleibt ein eigenständiger Companion-Graph-Generator.

## Kollaborationsprinzip

LLM-Wiki nicht als Ersatz für Understand Anything framen.

Eine bessere Rahmung:

- Understand Anything hilft einem Entwickler, eine Codebase jetzt zu verstehen.
- LLM-Wiki hilft Agenten, Projektwissen über die Zeit zu erinnern, zu durchsuchen, zu zitieren, zu aktualisieren und zu publizieren.
