# Bidirektionale Obsidian-Synchronisation — vorgeschlagener Entwurf

<!-- translations:start -->
<p align="center"><a href="../../integrations/obsidian-sync.md">English</a> · <a href="obsidian-sync.ko.md">한국어</a> · <a href="obsidian-sync.zh.md">中文</a> · <a href="obsidian-sync.ja.md">日本語</a> · <a href="obsidian-sync.ru.md">Русский</a> · <a href="obsidian-sync.es.md">Español</a> · <a href="obsidian-sync.fr.md">Français</a></p>
<!-- translations:end -->

> **Status: Vorschlag (2026-05-17).** Dieses Dokument ist eine Design-Spezifikation, noch kein Feature. Es beschreibt, wie Tesserae es Nutzern ermöglichen könnte, projizierte Wiki-Seiten in Obsidian zu bearbeiten und diese Änderungen das nächste `project compile` überleben zu lassen. Die Implementierung hängt davon ab, dass dieser Entwurf landet.

Aktuell ist der [Obsidian-Export](obsidian.de.md) strikt einseitig: Der typisierte Graph in `.tesserae/graph.json` projiziert in den Vault, und `project compile` überschreibt projizierte Dateien. Nutzer haben auch nach der Gegenrichtung gefragt — eine Beschreibung in Obsidian bearbeiten und sehen, dass sie das Recompile überlebt.

Dieses Dokument legt dar, wie das funktionieren würde, ohne das Datenmodell inkohärent zu machen.

## Strategische Verschiebung, klar benannt

Die aktuelle README weist Live-Editing explizit zurück:

> Tesserae entscheidet sich für Compile-from-Source statt Live-Editing. Wer Notizen in einer UI bearbeiten will, nimmt Logseq oder Obsidian.

Bidirektionale Synchronisation **ändert diesen Vertrag** für eine Teilmenge der Felder. Das verdient bewusste Auseinandersetzung. Das Ziel ist nicht „Obsidian wird zum Editor" — sondern „die Obsidian-Edits des Nutzers werden beim Recompile nicht stillschweigend zerstört".

## Die Grundidee: Overlays statt Merges

Statt zu versuchen, zwei auseinanderdriftende Kopien desselben Nodes zu mergen, wird der Vault als **Diff-Layer** über der Projektion behandelt:

```text
source markdown  ──extract──▶  base_graph
                                    +
                              vault_overrides     ◀── computed from vault
                                    ↓
                              final_graph  ──project──▶  vault (.md files)
```

`vault_overrides.json` liegt in `.tesserae/` und wird **berechnet**, nicht von Hand verfasst. Bei jedem Compile durchläuft Tesserae den Vault, vergleicht jede projizierte Seite mit dem, was die vorherige Projektion geschrieben hat, und erfasst jede vom Nutzer eingebrachte Änderung als Overlay-Eintrag. Der finale Graph ist `base_graph` mit angewandten Overlays. Die nächste Projektion schreibt das Ergebnis zurück auf die Platte.

Round-Trip-stabil. Ein erneutes Compile desselben Vaults ohne quellseitige Änderungen erzeugt keine Diffs.

## Eigentümerschaft pro Feld

Jedes Feld eines Nodes hat einen Eigentümer. Die Eigentümerschaft entscheidet, was passiert, wenn Quelle und Vault nicht übereinstimmen.

| Feld | Quelle besitzt | Vault darf überschreiben | Hinweise |
|---|---|---|---|
| `id`, `type` | ja | nein | Schemagesteuert; Extractor-eigen |
| `name` | initial | ja | Nutzer kennt den kanonischen Namen oft besser als der Extractor |
| `aliases` | initial | ja | Append-only aus dem Vault; Vault-Einträge bleiben stets erhalten |
| `description` | initial | **ja** | Die häufigste Obsidian-Bearbeitung |
| `source_path` | ja | nein | Provenienz; lässt sich nicht wegbearbeiten |
| `metadata` (deklarierte Schlüssel) | initial | ja | Z. B. `arxiv_id`, `github_repo` — Nutzer kann korrigieren |
| `metadata.user.*` | n/a | ja | Reservierter Namespace für nutzereigene Schlüssel; Extractor schreibt nie |
| Ausgehende Edges (typisiert) | ja | nein | Edges leben in der Ontologie, nicht im Vault |
| Neue Wikilinks, die der Nutzer tippt | n/a | ja | Werden als `edge_type=user_link` exponiert, in den Graphen geschrieben |
| `<!-- user-notes -->` Body-Block | wird nie geschrieben | wird stets erhalten | Append-only-Zone, die der Projector niemals anfasst |

## Konfliktfälle und Defaults

| Fall | Default | Begründung |
|---|---|---|
| Vault-`description` weicht von der erneut extrahierten Quell-`description` ab | **Vault gewinnt**, Eintrag in `.tesserae/lint-report.md` unter „diverged fields" | Nutzer-Edits respektieren: Der Nutzer wollte die Änderung eindeutig. Der Audit-Trail erlaubt späteres Review. |
| Quelldatei gelöscht, projizierte Seite noch im Vault | Node aus dem Graphen entfernen, in `.tesserae/orphans.md` listen | Die Quelle ist autoritativ für die Existenz; das Orphan-Log lässt dich entscheiden, ob wiederhergestellt oder akzeptiert wird |
| Nutzer hat einen Wikilink auf einen nicht existierenden Slug geschrieben | Tombstone-Node anlegen (Typ `Stub`), im Lint-Report exponieren | Die Nutzer-Intention nicht verwerfen; zum Cleanup flaggen |
| Nutzer hat einen Frontmatter-Schlüssel hinzugefügt, den das Schema nicht kennt | Als `metadata.user.<key>` erhalten, nie überschreiben | Vorwärtskompatibel, ohne den typisierten Graphen zu verschmutzen |
| Zwei Vaults auf verschiedenen Maschinen bearbeiten denselben Node, beide via Obsidian Sync synchronisiert | **Außerhalb des Scopes für v1.** Last-Writer-Wins auf Dateisystemebene. | Echte Multi-Vault-Föderation ist Tier 3; aufschieben, bis ein realer Anwendungsfall vorliegt |

## User-Notes-Append-Zone

Jede projizierte Seite bekommt eine eingezäunte Zone, die der Projector niemals anfasst:

```markdown
> [!quote] Paper
> Headline contribution and method sketch projected from the graph...

<!-- user-notes:start -->

Your notes here. Anything between the markers survives recompile forever.
Wikilinks here become `user_link` edges in the graph on the next pull.

<!-- user-notes:end -->

## Outgoing
- ...
```

Zwei praktische Effekte:
1. Nutzer können jede Seite annotieren (z. B. „siehe Kapitel 4 meiner Notizen"), ohne sie beim Rebuild zu verlieren.
2. Der Pull-Durchlauf scannt den User-Notes-Block nach Wikilinks und exponiert sie als ontologisch typisierte `user_link`-Edges, was ihnen Graph-Erreichbarkeit verschafft, ohne die formalen Edge-Typen zu verschmutzen.

## Remote-Transport — explizites Nicht-Ziel

Tesserae baut **keinen** Sync-Server, keinen Auth-Layer, keinen Conflict-Resolution-Daemon und keinen gehosteten Vault. „Bidirektional" bedeutet hier „Compile liest aus dem Vault" — wie der Vault auf die Compile-Maschine kommt, ist Sache des Nutzers, gelöst mit Tools, die es längst gibt:

| Stack | Kosten | Hinweise |
|---|---|---|
| Obsidian Sync | Kostenpflichtig, $4-8/Monat | E2E-verschlüsselt, offiziell, denkbar einfach |
| iCloud / Dropbox / OneDrive | Im OS gebündelt | Funktioniert, aber die Konflikt-UX ist unfreundlich |
| Syncthing | Kostenlos, selbst gehostet | Beste Wahl für Single-User-Cross-Device |
| Git (Vault eingecheckt) | Kostenlos | Konflikt-UX ist für technische Nutzer am besten |
| LiveSync (CouchDB-Plugin) | Kostenlos, erfordert Server | Multi-Device in Echtzeit |

Alle fünf sind mit dem Overlay-Modell kompatibel, weil Tesserae den Vault als Dateien-auf-Platte sieht, nicht als Strom von Mutationen.

## CLI-Oberfläche (vorgeschlagen)

```bash
# Pull-only sync (Tier 1a): overlay reader runs as part of compile by default.
tesserae project compile                  # always pulls vault overrides if vault exists

# Inspect what would change before letting compile apply
tesserae project obsidian-sync --dry-run

# Skip the pull for a single compile (recovery mode)
tesserae project compile --no-vault-pull

# Long-running watch (Tier 2)
tesserae project obsidian-sync --watch --vault ~/Documents/tesserae-vault
```

## Phasen

| Tier | Scope | Aufwand |
|---|---|---|
| **1a** | Overlay-Reader: Vault durchlaufen, `vault_overrides.json` bauen, beim Compile anwenden. Lint meldet Divergenzen. | ~3 Tage |
| **1b** | User-Notes-Append-Zonen: Projector fasst `<!-- user-notes:start --> ... <!-- user-notes:end -->`-Blöcke nie an. | ~1 Tag |
| **2** | Watch-Modus: dauerhaft laufendes `obsidian-sync --watch` führt Overlay bei Filesystem-Events erneut aus, fragt vor dem Anwenden nach. | ~1 Woche |
| **3** | Multi-Vault-Föderation: Graph speichert Provenienz pro Vault, unterstützt parallele Edits über synchronisierte Vaults hinweg. | ~1 Monat, aufgeschoben bis zum realen Anwendungsfall |

## Nicht-Ziele (explizit)

- Ein Sync-Server / Auth / gehostetes Backend.
- Kollaboratives Echtzeit-Editing innerhalb von Obsidian (dafür LiveSync nehmen, falls nötig).
- Den Extractor umschreiben, sodass jedes Feld Round-Trip-fähig ist — die Quell-Markdown bleibt kanonisch für alles außerhalb der Override-Tabelle.
- Sync der statischen HTML-Site (`build-site` bleibt rein projektionsbasiert).

## Offene Entscheidungen vor der Implementierung

Diese haben vorgeschlagene Defaults, verdienen aber einen finalen Durchgang, bevor Code landet:

1. **Form des Lint-Reports.** Sollen divergierte Felder als separate Datei `.tesserae/diverged-fields.md` auftauchen oder als neuer Abschnitt im bestehenden `lint-report.md`? Vorschlag: dedizierte Datei, damit sie in Git diffbar bleibt.
2. **Tombstone-Node-Typ.** `Stub` als echten Schematyp hinzufügen oder auf `OpenQuestion` mit einem Diskriminator `_kind: stub` aufsatteln? Vorschlag: echter Typ namens `Stub`, aus öffentlichen Indizes versteckt.
3. **Pull-on-Compile-Default.** Standardmäßig AN oder AUS? Vorschlag: AN, wenn am konfigurierten Pfad ein Vault existiert, mit einer einmaligen Bestätigungsabfrage beim ersten Auslösen, damit Nutzer bewusst zustimmen.
4. **Was zählt für den Diff als „die vorherige Projektion"?** Ein in `.tesserae/vault_snapshot.json` abgelegter Snapshot oder bei jedem Compile spontanes Re-Projizieren? Vorschlag: Snapshot, am Ende jedes Compiles geschrieben. Günstiger und vermeidet, dass Extractor-Nichtdeterminismus ins Overlay leakt.
5. **Mehrsprachige Vault-Projektion.** Heutige Projektion ist einsprachig (die Quelle). Sollen Overlays locale-aware sein (z. B. greift ein Edit an `description` in einem koreanischen Vault-Overlay nur auf die koreanische Projektion)? Vorschlag: außerhalb des Scopes für v1; der Vault ist einsprachig und folgt der primären Sprache des Projekts.

## Wie sich das in `obsidian.md` zeigt

Der nutzergerichtete Guide bleibt fokussiert auf „du kannst den Vault lesen und abfragen". Ein kurzer Abschnitt „Bidirektionale Synchronisation" am Ende wird hierher verlinken, sobald die Implementierung landet, mit einer einzeiligen Zusammenfassung: „Felder in Obsidian bearbeiten, sie überleben das Recompile. Siehe [obsidian-sync.md](obsidian-sync.md) für das vollständige Modell."

Bis dahin bleibt der bestehende Read-only-Disclaimer in `obsidian.md` stehen — dieser Entwurf ist eine Roadmap, kein ausgeliefertes Feature.
