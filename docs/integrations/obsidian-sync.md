# Obsidian bidirectional sync — proposed design

<!-- translations:start -->
<p align="center"><a href="../i18n/integrations/obsidian-sync.ko.md">한국어</a> · <a href="../i18n/integrations/obsidian-sync.zh.md">中文</a> · <a href="../i18n/integrations/obsidian-sync.ja.md">日本語</a> · <a href="../i18n/integrations/obsidian-sync.ru.md">Русский</a> · <a href="../i18n/integrations/obsidian-sync.es.md">Español</a> · <a href="../i18n/integrations/obsidian-sync.fr.md">Français</a> · <a href="../i18n/integrations/obsidian-sync.de.md">Deutsch</a></p>
<!-- translations:end -->

> **Status: Proposed (2026-05-17).** This document is a design spec, not yet a feature. It describes how LLM-Wiki could let users edit projected wiki pages in Obsidian and have those edits survive the next `project compile`. Implementation is gated on this design landing.

Today the [Obsidian export](obsidian.md) is strictly one-way: the typed graph in `.llm-wiki/graph.json` projects to the vault, and `project compile` overwrites projected files. Users have asked for the opposite direction too — edit a description in Obsidian, see it survive recompile.

This document spells out how that would work without making the data model incoherent.

## Strategic shift, stated plainly

The current README disclaims live editing:

> LLM-Wiki picks compile-from-source over live editing. If you want to edit notes in a UI, use Logseq or Obsidian.

Bidirectional sync **changes that contract** for a subset of fields. Worth being deliberate. The goal is not "Obsidian becomes the editor" — it's "the user's Obsidian edits aren't silently destroyed on recompile".

## The core idea: overlays, not merges

Rather than trying to merge two diverging copies of the same node, treat the vault as a **diff layer** over the projection:

```text
source markdown  ──extract──▶  base_graph
                                    +
                              vault_overrides     ◀── computed from vault
                                    ↓
                              final_graph  ──project──▶  vault (.md files)
```

`vault_overrides.json` lives in `.llm-wiki/` and is **computed**, not authored. On each compile, LLM-Wiki walks the vault, compares each projected page against what the previous projection wrote, and records every user-introduced change as an overlay entry. The final graph is `base_graph` with overlays applied. The next projection writes the result back to disk.

Round-trip stable. Recompiling the same vault with no source-side changes produces no diffs.

## Per-field ownership

Each field on a node has an owner. Ownership decides what happens when source and vault disagree.

| Field | Source-owns | Vault may override | Notes |
|---|---|---|---|
| `id`, `type` | yes | no | Schema-controlled; extractor-owned |
| `name` | initial | yes | User often knows canonical name better than the extractor |
| `aliases` | initial | yes | Append-only from vault; vault entries always preserved |
| `description` | initial | **yes** | The most common Obsidian edit |
| `source_path` | yes | no | Provenance; can't be edited away |
| `metadata` (declared keys) | initial | yes | E.g. `arxiv_id`, `github_repo` — user can correct |
| `metadata.user.*` | n/a | yes | Reserved namespace for user-only keys; extractor never writes |
| Outgoing edges (typed) | yes | no | Edges live in the ontology, not the vault |
| New wikilinks the user types | n/a | yes | Surfaced as `edge_type=user_link`, written to graph |
| `<!-- user-notes -->` body block | never written | always preserved | Append-only zone the projector never touches |

## Conflict cases and defaults

| Case | Default | Why |
|---|---|---|
| Vault `description` differs from re-extracted source `description` | **Vault wins**, log to `.llm-wiki/lint-report.md` under "diverged fields" | User-edit-respects: the user clearly intended the edit. Audit trail lets you review later. |
| Source file deleted, projected page still in vault | Remove node from graph, list in `.llm-wiki/orphans.md` | Source is authoritative for existence; orphan log lets you decide whether to restore or accept |
| User wrote a wikilink to a slug that doesn't exist | Create tombstone node (type `Stub`), surface in lint report | Don't drop the user intent; flag it for cleanup |
| User added a frontmatter key the schema doesn't know | Preserve as `metadata.user.<key>`, never overwrite | Forward-compatible without polluting the typed graph |
| Two vaults on different machines edit the same node, both synced via Obsidian Sync | **Out of scope for v1.** Last-writer wins at the filesystem level. | True multi-vault federation is Tier 3; defer until a real use case |

## User-notes append zone

Every projected page gets a fenced zone the projector never touches:

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

Two practical effects:
1. Users can annotate any page (e.g. "see chapter 4 of my notes") without losing it on rebuild.
2. The pull pass scans the user-notes block for wikilinks and surfaces them as ontology-typed `user_link` edges, giving them graph reachability without polluting the formal edge types.

## Remote transport — explicit non-goal

LLM-Wiki does **not** build a sync server, auth layer, conflict-resolution daemon, or hosted vault. "Bidirectional" here means "compile reads from the vault" — what gets the vault to the machine doing the compile is the user's problem, solved by tools that already exist:

| Stack | Cost | Notes |
|---|---|---|
| Obsidian Sync | Paid, $4-8/mo | E2E-encrypted, official, dead simple |
| iCloud / Dropbox / OneDrive | Bundled with the OS | Works but conflict UX is hostile |
| Syncthing | Free, self-hosted | Best for solo cross-device |
| Git (vault committed) | Free | Conflict UX is best for technical users |
| LiveSync (CouchDB plugin) | Free, requires server | Real-time multi-device |

All five are compatible with the overlay model because LLM-Wiki sees the vault as files-on-disk, not as a stream of mutations.

## CLI surface (proposed)

```bash
# Pull-only sync (Tier 1a): overlay reader runs as part of compile by default.
llm_wiki project compile                  # always pulls vault overrides if vault exists

# Inspect what would change before letting compile apply
llm_wiki project obsidian-sync --dry-run

# Skip the pull for a single compile (recovery mode)
llm_wiki project compile --no-vault-pull

# Long-running watch (Tier 2)
llm_wiki project obsidian-sync --watch --vault ~/Documents/llm-wiki-vault
```

## Phasing

| Tier | Scope | Effort |
|---|---|---|
| **1a** | Overlay reader: walk vault, build `vault_overrides.json`, apply at compile. Lint reports divergences. | ~3 days |
| **1b** | User-notes append zones: projector never touches `<!-- user-notes:start --> ... <!-- user-notes:end -->` blocks. | ~1 day |
| **2** | Watch mode: long-running `obsidian-sync --watch` re-runs overlay on filesystem events, prompts before applying. | ~1 week |
| **3** | Multi-vault federation: graph stores per-vault provenance, supports concurrent edits across synced vaults. | ~1 month, deferred until real use case |

## Non-goals (explicitly)

- A sync server / auth / hosted backend.
- Real-time collaborative editing inside Obsidian (use LiveSync if you need this).
- Rewriting the extractor to round-trip every field — the source markdown stays canonical for everything outside the override table.
- Sync of the static HTML site (`build-site` remains projection-only).

## Open decisions before implementation

These have proposed defaults but warrant a final pass before code lands:

1. **Lint report shape.** Should diverged fields surface as a separate `.llm-wiki/diverged-fields.md` file, or as a new section in the existing `lint-report.md`? Proposed: dedicated file so it can be diffed in git.
2. **Tombstone node type.** Add `Stub` as a real schema type, or piggyback on `OpenQuestion` with a `_kind: stub` discriminator? Proposed: real type, named `Stub`, hidden from public indexes.
3. **Pull-on-compile default.** Default ON or default OFF? Proposed: ON when a vault exists at the configured path, with a one-time confirmation prompt the first time it activates so users opt-in deliberately.
4. **What counts as "the previous projection" for diffing?** Snapshot stored in `.llm-wiki/vault_snapshot.json`, or re-project on the fly each compile? Proposed: snapshot, written at end of every compile. Cheaper and avoids extractor non-determinism leaking into the overlay.
5. **Multi-language vault projection.** Today's projection is single-language (the source). Should overlays be locale-aware (e.g. an edit to `description` in a Korean vault overlay applies only to the Korean projection)? Proposed: out of scope for v1; vault is single-language matching the project's primary language.

## How this shows up in `obsidian.md`

The user-facing guide stays focused on "you can read and query the vault". A short "Bidirectional sync" section at the end will link here once implementation lands, with a one-line summary: "Edit fields in Obsidian, they survive recompile. See [obsidian-sync.md](obsidian-sync.md) for the full model."

Until then, the existing read-only disclaimer in `obsidian.md` stays — this design is a roadmap, not a shipped feature.
