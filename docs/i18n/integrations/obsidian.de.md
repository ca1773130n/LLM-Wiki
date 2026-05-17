# Obsidian — das kompilierte Wiki als echten Vault öffnen

<!-- translations:start -->
<p align="center"><a href="../../integrations/obsidian.md">English</a> · <a href="obsidian.ko.md">한국어</a> · <a href="obsidian.zh.md">中文</a> · <a href="obsidian.ja.md">日本語</a> · <a href="obsidian.ru.md">Русский</a> · <a href="obsidian.es.md">Español</a> · <a href="obsidian.fr.md">Français</a></p>
<!-- translations:end -->

Der Obsidian-Export von LLM-Wiki verwandelt deinen kompilierten typisierten Graphen in einen echten, opinionierten [Obsidian](https://obsidian.md)-Vault. Kein bloßes Markdown-Verzeichnis — ein Vault mit `.obsidian/`-Konfiguration, typbewussten [Callouts](https://help.obsidian.md/Editing+and+formatting/Callouts), [Dataview](https://blacksmithgu.github.io/obsidian-dataview/)-abfragbarem Frontmatter, einem Vault-Dashboard und einem Index aller `wiki://`-Querverweise zwischen Vaults.

## Voraussetzungen

Kompiliere zuerst das Projekt:

```bash
cd /path/to/your-project
llm_wiki project setup
llm_wiki project compile
```

Der Compile erzeugt `.llm-wiki/graph.json` (die Quelle der Wahrheit) und eine schlichte Markdown-Projektion unter `.llm-wiki/markdown_projection/`. Der Obsidian-Export setzt auf dieser Projektion auf, ergänzt aber auf jeder Seite Obsidian-eigene Anreicherungen.

## 1) Den Vault exportieren

```bash
llm_wiki project export-obsidian --vault ~/Documents/llm-wiki-vault
```

Das Verzeichnis wird angelegt, falls es nicht existiert. Erneutes Ausführen überschreibt es idempotent — die Markdown-Projektion ist deterministisch bei gleichem Graphen.

Was auf der Platte landet:

```text
llm-wiki-vault/
  .obsidian/                  # Obsidian config (app.json, graph.json, plugins)
  README.md                   # Vault entry point
  index.md                    # All nodes grouped by section
  _bridges.md                 # Cross-vault wiki:// references, grouped by alias
  _meta/
    dashboard.md              # Dataview overview tables
  papers/                     # Paper / Repository / SourceDocument pages
  concepts/                   # Concept / Topic / Field / Method / Algorithm pages
  claims/                     # Claim / OpenQuestion / Evidence pages
  raw/                        # Optional raw-source attachments (created lazily)
```

## 2) Das Verzeichnis in Obsidian öffnen

`File → Open vault... → Open folder as vault → ~/Documents/llm-wiki-vault`.

Obsidian erkennt `.obsidian/`, identifiziert das Ganze als echten Vault und lädt ihn. Die Liste der Community-Plugins enthält Dataview; Obsidian wird dich bitten, es zu aktivieren (empfohlen — ohne Dataview werden die dataview-Blöcke nur als Code-Fences gerendert).

`Settings → Community plugins → Browse → "Dataview" → Install → Enable`.

## 3) Rundgang durch den Vault

### Einstiegspunkte

- `README.md` — was dieser Vault ist und wie man ihn aktualisiert
- `index.md` — jeder Node nach Sektion (papers, concepts, claims) mit Wikilinks
- `_meta/dashboard.md` — Dataview-Übersicht: jüngste Seiten, Papers, Concepts/Claims

### Anreicherungen pro Seite

Jede Node-Seite bringt jetzt Folgendes mit:

**Typbewusste Callouts.** Ein semantisches Callout am Seitenanfang macht den Node-Typ auf einen Blick sichtbar:

```markdown
> [!quote] Paper
> The paper triggered a wave of follow-on work: SuGaR aligns Gaussians...

> [!warning] Limitation
> No current method can achieve real-time display rates at 1080p...

> [!question] Open question
> How does dynamic-scene reconstruction scale...
```

Mapping (Auszüge): `Paper → quote`, `Repository → info`, `Contribution → success`, `Performance → info`, `Limitation → warning`, `Causal → important`, `OpenQuestion → question`, `Evidence → example`.

**Dataview-abfragbare Edges.** Das Frontmatter führt die typisierten Edges jetzt als verschachtelte Maps:

```yaml
edges_out:
  uses: [gaussian-splatting, volumetric-rendering]
  part_of: [3d-4d-vision-and-reconstruction]
  supports_claim: [performance-claim-..., comparison-...]
edges_in:
  mentioned_in: [project-pulse, topic-visual-slam]
```

Damit kannst du Queries schreiben wie:

````markdown
```dataview
LIST FROM "papers" WHERE contains(edges_out.uses, "nerf")
```

```dataview
TABLE edges_out.supports_claim AS "Claims"
FROM "papers"
WHERE length(edges_out.supports_claim) > 3
SORT length(edges_out.supports_claim) DESC
LIMIT 10
```
````

**Cross-Vault-Bridges.** Jede `wiki://<alias>/<kind>/<slug>`-URI, die in der Beschreibung oder den Metadaten eines Nodes erwähnt wird, taucht sowohl als Frontmatter-Feld auf:

```yaml
cross_vault: [wiki://research/concepts/rlhf, wiki://notes/papers/arxiv-2510-12323]
```

als auch als Body-Sektion `Cross-vault references`. Der vault-weite Index `_bridges.md` aggregiert jede ausgehende Referenz gruppiert nach Ziel-Alias, sodass du Querverweise zwischen Vaults aus einer einzigen Seite heraus auditieren kannst.

**Related-(Dataview-)Block.** Jede Seite endet mit einer Query, die zurückverlinkende Seiten anzeigt und automatisch befüllt wird:

````markdown
```dataview
LIST
FROM "papers" OR "concepts" OR "claims"
WHERE contains(file.outlinks, this.file.link) AND file.name != this.file.name
SORT file.name
LIMIT 25
```
````

### Vault-Dashboard

`_meta/dashboard.md` bringt Dataview-Blöcke für die nützlichsten Aggregat-Sichten mit: zuletzt aktualisierte Seiten, alle Papers mit Metadaten-Spalten, alle Concepts und Claims nach Typ sortiert. Bearbeite es frei — es ist ein Startpunkt, kein festgeschriebener Vertrag.

### Vault-Graph-Ansicht

Obsidians eingebaute Graph-Ansicht (`Ctrl/Cmd+G`) funktioniert bereits mit den Wikilinks aus den Sektionen `## Outgoing` / `## Incoming`. Die mitgelieferte `.obsidian/graph.json` färbt `papers/`-, `concepts/`- und `claims/`-Pfade zur Orientierung ein. Du kannst darüber Dataview-gefilterte Sichten legen, um feinere Slices zu bekommen.

## Cross-Vault-Workflows

Registriere mehrere LLM-Wiki-Vaults, damit `wiki://`-URIs sich vault-übergreifend auflösen lassen:

```bash
llm_wiki register-project /path/to/research --name research
llm_wiki register-project /path/to/notes    --name notes
```

Exportiere jeden Vault nach der Registrierung erneut. `_bridges.md` zeigt in jedem Export nun auflösbare Referenzen zwischen Vaults, gruppiert nach Alias.

Obsidian selbst folgt `wiki://`-URIs nicht nativ — sie werden als Inline-Text gerendert — aber `_bridges.md` plus die Sektion `Cross-vault references` pro Seite liefern dir einen manuellen Index, bis ein dediziertes Obsidian-Plugin verfügbar ist.

## Refresh-Workflow

Der Obsidian-Vault ist ein **schreibgeschützter Export** des typisierten Graphen. Änderungen in Obsidian fließen nicht zurück nach `.llm-wiki/graph.json`. Um neue Quellen oder Fixes einzubauen:

```bash
# Edit source files under your project's source dirs (NOT the vault), then:
llm_wiki project compile
llm_wiki project export-obsidian --vault ~/Documents/llm-wiki-vault
```

Obsidian lädt geänderte Dateien auf der Platte hot neu. Wenn du im Vault eigene Markdown-Notizen ergänzt hast, die nicht aus dem Graphen projiziert sind (z. B. persönliche Annotationen), bleiben sie erhalten — der Export überschreibt nur Dateien, die er selbst besitzt: unter `papers/`, `concepts/`, `claims/` sowie `index.md`, `_bridges.md`, `_meta/dashboard.md` und `README.md`.

## Wann das vs. die statische Site einsetzen

Die kompilierte HTML-Site (`llm_wiki project build-site` → `.llm-wiki/site/`) ist zum Teilen gedacht — push sie auf GitHub Pages, S3 oder einen beliebigen statischen Host. Der Obsidian-Vault dient dem **lokalen Lesen und Abfragen** mit Dataview und Obsidians Graph-Ansicht. Beide projizieren aus demselben Graphen, sodass sie nie auseinanderdriften.
