# RAG-Anything Multimodal-Companion

<!-- translations:start -->
<p align="center"><a href="../../integrations/rag-anything.md">English</a> · <a href="rag-anything.ko.md">한국어</a> · <a href="rag-anything.zh.md">中文</a> · <a href="rag-anything.ja.md">日本語</a> · <a href="rag-anything.ru.md">Русский</a> · <a href="rag-anything.es.md">Español</a> · <a href="rag-anything.fr.md">Français</a></p>
<!-- translations:end -->

[RAG-Anything](https://github.com/HKUDS/RAG-Anything) ist ein multimodales RAG-Framework (auf LightRAG aufbauend), das PDFs, Office-Dokumente, Bilder und Formeln über MinerU/Docling/PaddleOCR parst. LLM-Wiki integriert es sowohl als multimodale Ingestion-Pipeline (native Graph-Projektion im UA-Stil) als auch als Runtime-Memory-Backend neben Cognee.

## Warum beides nutzen?

- LLM-Wiki — langlebige Agent-Memory, Wiki-Kompilation, Graph-Projektion.
- RAG-Anything — multimodale Ingestion + LightRAG-Retrieval zur Laufzeit.

Die beiden ergänzen sich: RAG-Anything bringt PDF-/Office-/Bildverständnis mit, das die text-orientierten Source-Loader von LLM-Wiki nicht liefern; LLM-Wiki hält die langlebige, abfragbare Memory, die über Sessions hinweg bestehen bleibt.

## Aktueller reibungsarmer Workflow

Empfohlen ist der Setup-Wizard:

```bash
llm_wiki project setup
```

Für die Automatisierung:

```bash
llm_wiki project setup \
  --yes \
  --with-raganything \
  --install-raganything \
  --raganything-parser mineru \
  --run-raganything
llm_wiki project compile
```

Der Setup-Wizard installiert `raganything` und `docling` zusammen. MinerU bleibt opt-in: installiere es nur dann mit `pip install 'mineru[core]'`, wenn du PDFs oder Bilder ingestieren willst.

LLM-Wiki hinterlegt einen verwalteten Refresh-Befehl, statt von Nutzern zu verlangen, sich einen auszudenken:

```bash
llm_wiki project refresh-raganything --parser mineru
```

Während des Compiles geht LLM-Wiki so vor:

1. prüft, ob `.llm-wiki/external/raganything/manifest.json` existiert und mit dem aktuellen git-commit übereinstimmt (über den hinterlegten `meta.json#gitCommitHash`);
2. führt den verwalteten Refresh-Wrapper aus, wenn dieser fehlt/veraltet ist oder `--refresh-external-tools` übergeben wurde;
3. erkennt nicht-Code-Quellen (PDFs, Office-Dokumente, Bilder, Markdown) und parst sie mit dem konfigurierten Parser;
4. schreibt `manifest.json` + `meta.json`;
5. setzt die normale Memory-Kompilation fort.

Du kannst vor einem Compile alle konfigurierten externen Refresh-Befehle erzwingen:

```bash
llm_wiki project compile --refresh-external-tools
```

## Manuelles Äquivalent

```bash
pip install 'raganything[all]'
python -m llm_wiki.raganything_refresh --project . --parser mineru
llm_wiki project compile
```

## Compile-Zeit vs. Laufzeit

LLM-Wiki trennt die Integration sauber:

- **Compile-time-Parsing** (`refresh-raganything` und `compile`): führt die Parser direkt aus — natives Lesen für `.md/.txt/.rst`, `docling.DocumentConverter` für alles andere. Die vollständige Pipeline von RAG-Anything wird hier *nicht* angestoßen, sodass für einen erfolgreichen Compile keine LLM-/Embedding-/Vision-Keys nötig sind.
- **Runtime-Queries** (`project ask`): `raganything_query.py` instanziiert `RAGAnything` mit den im Projekt konfigurierten LLM-/Embedding-/Vision-Funktionen und führt `aquery` gegen den Store von LightRAG aus. Dieser Pfad benötigt API-Keys.

Die Trennung sorgt dafür, dass `compile` schnell, deterministisch und key-frei ist; nur Retrieval-Operationen verursachen LLM-Token-Kosten.

## Native Graph-Synchronisation

LLM-Wiki importiert das geparste Manifest nativ während des Compiles, sofern das konfigurierte Tool `sync_mode: native_graph` verwendet.

Der native Adapter liest `.llm-wiki/external/raganything/manifest.json`, projiziert jedes geparste Dokument in einen `SourceFile`-Node mit Metadaten zu multimodalen Blöcken und schreibt ein Sync-Manifest:

```text
.llm-wiki/external/raganything-sync.json
```

Aktuelles Mapping:

| RAG-Anything | LLM-Wiki-Ziel |
|---|---|
| `documents[*]` | `SourceFile` node, `metadata.parser="raganything"` |
| `content_list[type=text]` | in `SourceFile.description` eingefaltet; Concepts über den bestehenden Extractor |
| `content_list[type=image]` | `SourceFile.metadata.multimodal_blocks[]` (`img_path`, `caption`) |
| `content_list[type=table]` | `SourceFile.metadata.multimodal_blocks[]` (`table_body`, `caption`) |
| `content_list[type=equation]` | `SourceFile.metadata.multimodal_blocks[]` und `metadata.equations[]` (LaTeX preserved) |

Die Provenance bleibt an jedem Node erhalten:

```json
{"system": "rag-anything", "id": "doc-<sha256>", "type": "document", "artifact": ".llm-wiki/external/raganything/manifest.json"}
```

Hinweis: Die interaktive Graph-Ansicht blendet Nodes der `sources`-Gruppe standardmäßig aus, um den Fokus auf Concepts und Entities zu legen — projizierte raganything-SourceDocuments bleiben in `graph.json` (MCP, Cognee, Suche und Per-Page-Wiki-Ansichten sehen sie weiterhin), sie überfluten nur nicht die Canvas. Setze `graph_view.show_sources = true` in `.llm-wiki/config.json`, um die dichte Ansicht zurückzuholen.

## Runtime-Memory-Backend

`memory_backends.raganything` (Standardwert von `default_raganything_backend_config`) koexistiert mit Cognee. `project ask` probiert die Backends in Prioritätsreihenfolge; die projektspezifische Priorität lässt sich über `memory_backends.priority` setzen. RAG-Anything ist opt-in (default `enabled: false`); das Setup-Flag `--with-raganything` aktiviert es.

### LLM-Provider (kein API-Key nötig)

Das Runtime-Backend von RAG-Anything braucht ein LLM, um Anfragen zu beantworten. LLM-Wiki nutzt standardmäßig die bestehenden OAuth-basierten CLI-Integrationen — kein API-Key erforderlich:

| Provider | Authentifizierung | Setup-Flag |
|---|---|---|
| `codex` (default) | `codex`-CLI-OAuth (du hast dich einmal mit `codex login` angemeldet) | `--raganything-llm-provider codex` |
| `claude` | `claude -p`-CLI; berücksichtigt `CLAUDE_CONFIG_DIR` für Multi-Account-Setups | `--raganything-llm-provider claude --raganything-claude-config-dir ~/.claude-personal2` |

Für Multi-Account-Setups von Claude (z. B. `~/.claude-personal1`, `~/.claude-personal2`) übergib `--raganything-claude-config-dir <path>` beim Setup. Das Runtime-Backend exportiert vor jedem Aufruf `CLAUDE_CONFIG_DIR=<path>`, sodass die Auth des gewählten Accounts verwendet wird, ohne deinen Standard-`~/.claude` zu berühren.

### Embeddings

| Provider | Wann verwenden |
|---|---|
| `deterministic` (default) | Keine externen Abhängigkeiten. Hash-basiert; geringe semantische Qualität, aber ausreichend, damit LightRAG einen Index aufbauen kann. Solide Baseline, um zu zeigen, dass die Integration funktioniert. |
| `ollama` | Lokales Ollama mit Embedding-Modell (z. B. `nomic-embed-text`). Übergib `--raganything-embedding ollama`; das Backend zeigt standardmäßig auf `http://localhost:11434`. |

Direkte OpenAI-Embedding-Unterstützung ist in v1 nicht über diese Flags verdrahtet — wer einen OpenAI-Key besitzt, kann `OPENAI_API_KEY` setzen und `memory_backends.raganything.embedding.provider` direkt in `.llm-wiki/config.json` überschreiben (RAGAnything zieht die env var über die LightRAG-Defaults nach).

### Aufruf über die CLI

```bash
# Auto mode: tries RAG-Anything (when enabled), then Cognee, then compiled-wiki search.
llm_wiki project ask "What does the integration spec say about parser routing?"

# Force a specific backend.
llm_wiki project ask "..." --backend raganything
llm_wiki project ask "..." --backend cognee
llm_wiki project ask "..." --backend wiki
```

`--backend raganything` ruft `llm_wiki.raganything_query.query` direkt auf. Ein relativer `working_dir` in `memory_backends.raganything` wird vor dem Aufruf gegen die Projekt-Root aufgelöst.

### Top-Level-`ask` (nutzt die Multi-Projekt-Registry)

Für Workflows, in denen du über mehrere registrierte LLM-Wiki-Projekte hinweg fragen willst, ohne in jedes hineinzucden, löst der Top-Level-Befehl `llm_wiki ask` das Projekt über die persistente Registry auf, die er mit dem MCP-Server teilt:

```bash
# One-time: register your projects (saved to ~/.llm-wiki/registry.json).
llm_wiki wiki register ~/Developer/Projects/LLM-Wiki --name llm-wiki --activate
llm_wiki wiki register ~/Developer/Projects/Other --name other

# List registered projects.
llm_wiki wiki list

# Ask the currently active project.
llm_wiki ask "How does the parser routing work?"

# Ask a specific registered project (no need to activate it).
llm_wiki ask "What is the architecture?" --wiki other

# Force a backend or pass a direct path.
llm_wiki ask "..." --wiki llm-wiki --backend raganything --json
llm_wiki ask "..." --project /tmp/somewhere
```

Die Dispatch-Logik — `--project > --wiki > active project` — ist in `_top_level_ask_handler` implementiert; die Antwortformatierung und Backend-Auswahl wird über `llm_wiki.query.ask_project` mit `project ask` und dem MCP-Tool `ask` geteilt. Die Registry ist datei-gestützt (standardmäßig `~/.llm-wiki/registry.json`), bleibt also über Sessions erhalten und ist mit der Projektliste des MCP-Servers synchron.

#### Über mehrere Vaults abfragen (`--scope all-registered`)

Bet B2 — wenn du mehrere registrierte Projekte hast (Research-Vault, Work-Vault, Side-Project-Vault) und dieselbe Frage gegen alle stellen willst, nutze `--scope all-registered`:

```bash
# Fan out across every registered project. The aggregated envelope is
# {"scope": "all-registered", "question": "...", "by_project": {"<alias>": <envelope>}}.
llm_wiki ask "What did I write about RLHF?" --scope all-registered --json

# Restrict to a hand-picked subset of aliases.
llm_wiki ask "..." --scope all-registered --scope-aliases research side-projects
```

Der Handler iteriert die registrierten Projekte in alphabetischer Reihenfolge, ruft für jedes `ask_project` auf und aggregiert die per-Projekt-Envelopes. Ein einzelnes fehlschlagendes Projekt — fehlende Config, RAG-Anything nicht aktiviert, Cognee down — wird im Slot des jeweiligen Alias als `{"error": "..."}` festgehalten und bricht den Rest des Fan-out nie ab. Dasselbe `scope`-Argument akzeptiert auch das MCP-Tool `ask`, sodass MCP-gesteuerte Coding-Agenten denselben Fan-out ohne zusätzliche Verkabelung bekommen.

### Multi-Projekt-Registry (`llm_wiki wiki`)

| Befehl | Zweck |
| --- | --- |
| `llm_wiki wiki list [--json]` | Listet registrierte Projekte und zeigt, welches aktiv ist. |
| `llm_wiki wiki register <path> [--name <alias>] [--activate]` | Fügt ein Projekt der Registry hinzu; der Alias wird standardmäßig vom bereinigten Verzeichnisnamen abgeleitet. |
| `llm_wiki wiki activate <name>` | Markiert einen Eintrag als aktives Projekt für nachfolgende `llm_wiki ask`-Aufrufe ohne `--wiki`. |
| `llm_wiki wiki unregister <name>` | Entfernt einen Eintrag; löscht den Aktiv-Pointer, falls dieser passte. |

Diese Befehle arbeiten direkt auf `llm_wiki.mcp_server.ProjectRegistry` — kein MCP-Roundtrip — und lassen sich ohne laufenden MCP-Server skripten.

### Aufruf aus MCP

Der stdio-MCP-Server stellt ein `ask`-Tool mit demselben Backend-Selektor bereit:

```json
{
  "name": "ask",
  "arguments": {
    "question": "What does the integration spec say about parser routing?",
    "backend": "auto",
    "project": "llm_wiki"
  }
}
```

Die Dispatch-Reihenfolge (`raganything` → `cognee` → kompilierte Wiki-Suche) und die `working_dir`-Auflösung spiegeln exakt den CLI-Handler, sodass Coding-Agenten und menschliche Bediener auf dieselben Antworten konvergieren.

## Systemvoraussetzungen

- **Python 3.10+** ist für RAG-Anything erforderlich (das Upstream-Paket `raganything` ≥1.3.0 hängt transitiv von `mineru[core]` ab, das wiederum Python 3.10+ verlangt). Auf älteren Python-Versionen deaktiviert LLM-Wiki die Integration mit einer klaren Warnung, statt stillschweigend einen kaputten Platzhalter zu installieren.
- **LibreOffice** zum Parsen von `.doc/.docx/.ppt/.pptx/.xls/.xlsx` — separat über den Paketmanager deiner Plattform installieren. RAG-Anything überspringt Office-Dokumente mit einer Warnung, wenn LibreOffice fehlt.
- **MinerU-Modellgewichte** werden beim ersten Parse heruntergeladen und gecached (mehrere GB). Folgeläufe nutzen den Cache wieder.
- **OpenAI-kompatible LLM-/Embedding-/Vision-Keys** für das Runtime-Memory-Backend (`OPENAI_API_KEY`, `OPENAI_BASE_URL`). Der Parser-only-Modus benötigt keine Keys.

## Parser-Routing

LLM-Wiki routet Quellen pro Dateiendung automatisch an den passenden Parser:

| Endung | Parser | Begründung |
|---|---|---|
| `.md`, `.markdown`, `.txt`, `.rst` | `docling` | Leichtgewichtig; kein MinerU-Modell-Download. |
| `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx` | `docling` | Bessere Erhaltung der Office-Struktur laut Upstream. |
| `.pdf`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp` | konfigurierter Default (`--raganything-parser`, default `mineru`) | OCR + Tabellenextraktion. |

Überschreibe pro Bucket mit `--text-parser` und `--office-parser` an `refresh-raganything`. Der konfigurierte Default gilt weiterhin für PDFs und Bilder.

Bevor die Parse-Schleife läuft, prüft LLM-Wiki, ob das Python-Paket jedes benötigten Parsers importierbar ist (`importlib.import_module(...)`), und bricht früh mit einem einzigen aggregierten Fehler ab, der jeden fehlenden Parser und seinen Install-Befehl listet. Wir verwenden bewusst nicht das Upstream-`RAGAnything.check_parser_installation()`, weil es nur den auf der Instanz konfigurierten Parser inspiziert und zusätzlich Model-Weight-Readiness-Checks bündelt, die nicht in eine Pre-Flight-Stage passen.

LLM-Wiki wählt zudem den Konstruktor-Zeit-Parser von `RAGAnything` aus der tatsächlichen Routing-Verteilung (der am häufigsten gewählte Parser gewinnt) statt direkt aus `--raganything-parser`. Damit wird der Fehlerfall vermieden, dass `RAGAnything.__init__` einen schweren Parser (z. B. `mineru`) initialisiert, dessen Modellgewichte noch nicht auf der Platte liegen, und so den gesamten Lauf zerschießt, bevor per-call-`parser=`-Overrides greifen können. Das Flag `--raganything-parser` steuert weiterhin den Default für nicht-Text-, nicht-Office-Quellen (PDFs, Bilder).

### Parser-Pakete

Der Compile-time-Parse-Pfad verwendet `docling.DocumentConverter` direkt für jede nicht-Text-Quelle; einmal installiert, bist du abgedeckt:

| Parser | Install-Befehl |
|---|---|
| `docling` (compile-time-Default für alles außer nativem Text) | mitgeliefert, wenn du `--with-raganything --install-raganything` ausführst (oder eigenständig `pip install docling`) |
| `paddleocr` (optionale OCR-Alternative) | `pip install 'raganything[paddleocr]>=1.3.0'` und `pip install paddlepaddle` (plattformspezifisches Wheel) |

> Hinweis: `mineru` wird derzeit **nicht zur Compile-time aufgerufen**. Der Compile-Pfad umgeht die volle Pipeline von RAG-Anything (die LLM-/Embedding-/Vision-Callables erfordern würde) und routet jede nicht-Text-Quelle direkt durch docling. MinerU-Unterstützung ist für einen künftigen Direct-Import-Pfad reserviert, der eine extern erzeugte `content_list.json` einliest.

Wenn ein konfigurierter Parser fehlt, bricht `refresh-raganything` früh ab — listet jeden fehlenden Parser in einem einzigen Fehler mit dem passenden Install-Befehl auf — statt in Per-File-Fehler zu kaskadieren.

### Per-Page-Ask-Widget

Jede Detailseite (Concept, Paper, Repo, Synthesis, Entity, Topic, Question, Source) enthält ein Inline-„Ask about this page“-Widget. Es POSTet an `/api/ask` der lokalen `llm_wiki project serve`-Instanz, ruft `llm_wiki.query.ask_project` auf und rendert die Antwort inline. Das Widget setzt der Frage des Nutzers den Node-Namen der aktuellen Seite als natürlich-sprachlichen Kontext-Hinweis voran (z. B. `` About `<NodeName>`: <question> ``); ein künftiger PR kann echtes Subgraph-Scoping direkt in `ask_project` einhängen.

Das Widget erkennt beim Laden die Backend-Verfügbarkeit über `/api/ask/health`. Wenn das Wiki statisch ausgeliefert wird (GitHub Pages, `file://`, S3, beliebiger statischer Host), kollabiert das Widget zu einer einzeiligen Notiz, die Leser zu `llm_wiki project serve` für die lokale interaktive Nutzung verweist. Keine Requests schlagen fehl, und nichts blockiert das Page-Rendering — das Widget ist eine deferred JS-Insel, getrennt vom schwereren Graph-Bundle.

In Kombination mit der Multi-Projekt-Registry (`llm_wiki wiki register`) kannst du das Wiki jedes registrierten Projekts aus jeder seiner Detailseiten heraus befragen.

## Kollaborationsprinzip

LLM-Wiki bleibt der Memory-Compiler. RAG-Anything bleibt ein eigenständiger Companion: ein multimodaler Parser plus LightRAG-Retrieval-Engine.
