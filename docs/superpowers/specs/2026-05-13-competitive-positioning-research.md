# LLM-Wiki Competitive Positioning Research

**Date:** 2026-05-13
**Status:** Draft for review
**Scope:** Ground LLM-Wiki against actual GitHub competitors. Pick differentiation bets that compound existing strengths.

This document is not a marketing brief. It is a research artifact whose only job is to help the maintainer decide which next two or three features will most meaningfully separate LLM-Wiki from adjacent projects, without inventing capabilities the codebase cannot deliver.

---

## 0. How to read this document

If you only have ten minutes, read these three sections in order:

1. Section 4 — "Differentiation bets" — ranked table and per-bet sketches.
2. Section 3 — "LLM-Wiki's honest current state" — what to defend, what to fix.
3. Section 5 — "Marketing / positioning" — taglines, comparison table, launch outline.

Everything else (Sections 1, 2, 6) is the evidence that supports those three.

---

## 1. Method and sources

All competitor facts in this document come from the project's own GitHub README, repository metadata, or arXiv abstract, accessed 2026-05-12 / 2026-05-13. Star counts and last-activity windows are approximate (GitHub rounds to one decimal of `k`; commit counts and activity windows reflect what was visible in the README page at fetch time). Every quoted positioning line is verbatim from the project's GitHub "About" field.

A few categories below contain closed-source incumbents (Obsidian, Roam, Notion, Heptabase, Tana, Sourcegraph Cody, Cursor). Where they appear, they are described from public marketing pages, not source-of-truth GitHub data, and flagged as such. They are included because users compare LLM-Wiki to them mentally even though the source comparison is asymmetric.

The LLM-Wiki side of every claim is sourced from this repository, verified by reading:

- `README.md` and the localized `README.{ko,zh,ja,ru,es,fr}.md`
- `llm_wiki/cli.py` (1214 lines, the public CLI surface)
- `llm_wiki/mcp_server.py` (1005 lines, the MCP tools agents see)
- `llm_wiki/research_graph.py` (lines 21-76, the `ResearchNodeType` enum: 41 node types in 5 layers — Field/Taxonomy, Source/Artifact, Concept, Assertion, Synthesis)
- `llm_wiki/site/pages.py` and `llm_wiki/site/__init__.py` (page kinds: sources, concepts, entities, papers, repos, topics, syntheses, questions, timeline, graph)
- `docs/integrations/understand-anything.md`, `docs/integrations/rag-anything.md`
- `docs/superpowers/specs/2026-05-10-rag-anything-integration-design.md`

Where the document says "no competitor does X today," that means: not visible on the project's README or first-page docs as of the access date. It does not mean no work is in flight elsewhere.

---

## 2. Competitor landscape

Six categories. Four to seven projects in each. Each entry: GitHub URL, approximate stars, last-activity bucket (under 6 months / 6-12 months / older), license, the project's own one-line positioning, the killer feature, why an LLM-Wiki user might consider switching, and why they likely will not.

### 2.1 Personal knowledge-graph apps

These are the projects new users will compare LLM-Wiki to in their head. Most are interactive editors; LLM-Wiki is a compiler. They share visual graph view as the lowest-common-denominator feature.

- **Logseq** — <https://github.com/logseq/logseq> — ~42.8k stars, active under 6 months, AGPL-3.0.
  - Own words: "A privacy-first, open-source platform for knowledge management and collaboration."
  - Killer feature: block-level outliner with a DB version in beta (DB graphs, RTC real-time collaboration).
  - Switching pressure: high for users who want to *write* every day in an outliner; LLM-Wiki does not edit, it compiles.
  - Why users stay with LLM-Wiki: LLM-Wiki populates the graph from sources you already have (papers, repos, PDFs) without manual block authoring. Logseq has no concept extraction from external docs.

- **Foam** — <https://github.com/foambubble/foam> — ~17.1k stars, active under 6 months, MIT.
  - Own words: "A personal knowledge management and sharing system for VSCode."
  - Killer feature: wikilinks + reference generation + GitHub Pages publishing, all from inside VSCode.
  - Switching pressure: low — Foam users are markdown-purist authors. LLM-Wiki and Foam can coexist: edit notes with Foam, compile the wiki with LLM-Wiki.
  - Why users stay: Foam has no typed graph, no concept extraction, no MCP, no multimodal ingestion.

- **Dendron** — <https://github.com/dendronhq/dendron> — ~7.4k stars, last activity over 12 months (archived/dormant), GPL-3.0.
  - Own words: "The personal knowledge management (PKM) tool that grows as you do!"
  - Killer feature: schema-driven note hierarchies, autocomplete templates.
  - Switching pressure: near zero — project is effectively stalled. Worth mentioning only because its schema-driven approach is closest in spirit to LLM-Wiki's typed graph and validates the demand.

- **AppFlowy** — <https://github.com/AppFlowy-IO/AppFlowy> — ~70.4k stars, active under 6 months, AGPL-3.0.
  - Own words: "Bring projects, wikis, and teams together with AI. AppFlowy is the AI collaborative workspace where you achieve more without losing control of your data. The leading open source Notion alternative."
  - Killer feature: Notion-style composable blocks (text + databases + kanban + calendar) with AI assistance, Rust backend.
  - Switching pressure: medium for teams who want a Notion replacement. LLM-Wiki is not trying to be Notion.
  - Why users stay: LLM-Wiki is single-user, source-driven, and outputs static HTML. AppFlowy is a stateful Electron app with a database.

- **TiddlyWiki5** — <https://github.com/TiddlyWiki/TiddlyWiki5> — ~8.6k stars, active under 6 months, BSD-3-Clause.
  - Own words: "A self-contained JavaScript wiki for the browser, Node.js, AWS Lambda etc."
  - Killer feature: the entire wiki including editor is a single HTML file you can email.
  - Switching pressure: niche. Different use case (portable personal wiki).
  - Worth keeping in the table because "single static HTML output" is also LLM-Wiki's deployment model — and TiddlyWiki shows that model has a durable audience.

- **Quartz** — <https://github.com/jackyzha0/quartz> — ~12.1k stars, active under 6 months, MIT.
  - Own words: "a fast, batteries-included static-site generator that transforms Markdown content into fully functional websites."
  - Killer feature: out-of-the-box graph view + backlinks for an Obsidian vault, deployed to GitHub Pages in minutes.
  - Switching pressure: this is the closest competitor on the "publish my notes" axis. The user-facing artifact looks similar.
  - Why users stay with LLM-Wiki: Quartz does not extract concepts, does not type its graph, does not ingest PDFs or code, does not expose an MCP server, and does not query over the result. It renders what you wrote. LLM-Wiki renders what was *latent* in what you wrote.

- **Anytype** — <https://github.com/anyproto/anytype-ts> — ~7.5k stars, active under 6 months, "Any Source Available License 1.0".
  - Own words: "Official Anytype client for MacOS, Linux, and Windows."
  - Killer feature: offline-first local-first PKM with p2p sync, zero-knowledge encryption, typed objects.
  - Switching pressure: medium for privacy-focused PKM users.
  - Why users stay: Anytype is a closed protocol on a non-OSI license, no static publishing, no MCP, no compile pipeline.

Closed-source incumbents in the mental comparison: **Obsidian** (the de-facto benchmark for personal knowledge graphs; not OSI-licensed), **Roam Research** (the original networked-thought tool), **Heptabase** (whiteboard PKM with infinite canvas), **Tana** (block + supertag PKM). These do not appear in the source-comparison tables because they are not on GitHub, but the spatial canvas / supertag / time-travel ideas they pioneered are referenced in Section 4's bets.

### 2.2 LLM-aware knowledge bases / agent memory

These are the projects an *engineer* would compare LLM-Wiki to when reading the README. Most are runtime memory backends; LLM-Wiki is a build-time knowledge compiler that also ships a runtime memory backend.

- **Cognee** — <https://github.com/topoteretes/cognee> — ~17.2k stars, active under 6 months, Apache-2.0.
  - Own words: "Memory control plane for AI Agents in 6 lines of code."
  - Killer feature: pluggable `add → cognify → search` pipeline, MCP server, graph + vector hybrid memory.
  - Relationship to LLM-Wiki: already integrated. LLM-Wiki's `cognify` mode and `codex_cognify` mode call Cognee. LLM-Wiki's value-add over plain Cognee is the typed research graph, the static site, the multi-source pipeline, and OAuth-based no-API-key LLM access.

- **Mem0** — <https://github.com/mem0ai/mem0> — ~55.5k stars, active under 6 months, Apache-2.0.
  - Own words: "Universal memory layer for AI Agents."
  - Killer feature: library + self-hosted server + managed cloud, three deployment tiers, citation-grade memory updates.
  - Switching pressure: high for users whose primary need is conversational agent memory, not document-based knowledge.
  - Why users stay with LLM-Wiki: LLM-Wiki is document-and-source-first, not chat-first. There is no overlap on "compile a static knowledge site from your sources."

- **Letta (formerly MemGPT)** — <https://github.com/letta-ai/letta> — ~22.7k stars, active under 6 months, Apache-2.0.
  - Own words: "Letta is the platform for building stateful agents: AI with advanced memory that can learn and self-improve over time."
  - Killer feature: stateful agent runtime, memory blocks, full-featured agents API.
  - Switching pressure: orthogonal. Letta is an agent platform; LLM-Wiki feeds agents.
  - Plausible integration: an LLM-Wiki MCP server could plug into a Letta agent as a tool.

- **Zep** — <https://github.com/getzep/zep> — ~4.6k stars, active under 6 months, Apache-2.0.
  - Own words (page title): "Zep | Examples, Integrations, & More" / "End-to-End Context Engineering Platform."
  - Killer feature: temporal knowledge graph for conversational memory, ontology directory, MCP server.
  - Switching pressure: low for LLM-Wiki users; Zep is conversation-centric.
  - Notable cross-cutting feature: ontology-as-config. Section 4 bet "Schema evolution via config" learns from this.

- **GraphRAG (Microsoft)** — <https://github.com/microsoft/graphrag> — ~32.9k stars, active under 6 months, MIT.
  - Own words: "A modular graph-based Retrieval-Augmented Generation (RAG) system."
  - Killer feature: LLM-extracted entity-relationship graph + community-summary global queries, the reference implementation that put graph-RAG on the map.
  - Switching pressure: medium. Engineers evaluating "graph RAG for my corpus" often start here.
  - Why users stay with LLM-Wiki: GraphRAG outputs a graph and a query engine. It does not produce a navigable wiki, does not have project-level CLI ergonomics, and does not include multimodal ingestion or a code graph.

- **LightRAG** — <https://github.com/HKUDS/LightRAG> — ~35.1k stars, active under 6 months, MIT.
  - Own words: "[EMNLP2025] LightRAG: Simple and Fast Retrieval-Augmented Generation."
  - Killer feature: dual-level (local/global) retrieval over an LLM-extracted graph, web UI, rerankers, OpenSearch storage.
  - Relationship to LLM-Wiki: indirect dependency via RAG-Anything. LightRAG is the storage layer underneath RAG-Anything.

- **LlamaIndex** — out of scope for line-level comparison (it is a framework, not a product), but referenced as the alternative for users who want a Python toolkit rather than a CLI tool. LLM-Wiki uses LlamaIndex-style abstractions internally but does not expose them as the surface.

### 2.3 Static markdown / wiki publishers

Already covered partially in 2.1. Adding the docs-tooling projects here for completeness — these are what users pick if they explicitly do *not* want graph features and just want a navigable static site.

- **Quartz** — already in 2.1.
- **MkDocs Material** — most popular static docs theme; no graph view by design.
- **Docusaurus** — Meta's docs framework, plugins for backlinks exist but no first-class graph.
- **mdBook** — Rust-native, used by The Rust Book. Linear table-of-contents, no graph.
- **Starlight (Astro)** — newer docs framework, similar positioning to Docusaurus.

The competitive read here: nobody in the docs-framework space is shipping graph + concept extraction. LLM-Wiki's static-HTML output is unusual *for what it contains*, not for being static.

### 2.4 Code / repo understanding tools

LLM-Wiki has a `CodeGraphExtractor` that builds CodeProject / SourceFile / CodeClass / CodeFunction / CodeModule / Dependency nodes (per `research_graph.py` lines 41-46). These are filtered out of the public MCP surface but available for the typed graph. Adjacent projects:

- **Aider** — <https://github.com/Aider-AI/aider> — ~44.7k stars, active under 6 months, Apache-2.0.
  - Own words: "aider is AI pair programming in your terminal."
  - Killer feature: tree-sitter-based repo-map that gives the LLM a compressed view of the codebase. The repo-map paper / docs are well-cited.
  - Switching pressure: orthogonal. Aider is a coding assistant. LLM-Wiki is a wiki compiler.
  - Idea to absorb: the repo-map quality bar — terse, dense, accurate — is exactly what LLM-Wiki's code-graph pages should aim for.

- **OpenHands** — <https://github.com/OpenHands/OpenHands> — ~73.3k stars, active under 6 months, MIT.
  - Own words: "AI-Driven Development."
  - Killer feature: full autonomous agent runtime with a sandboxed environment.
  - Switching pressure: orthogonal.

- **Sourcegraph Cody** — closed-source as of 2026, but the historical Sourcegraph code intelligence (LSIF + SCIP) remains the benchmark for cross-repo code navigation. Out of scope for direct comparison.

- **Understand Anything** — already an LLM-Wiki adjunct, not a competitor.

The takeaway from this category: code-graph features are valuable but not differentiating on their own. The differentiation is *the same wiki page that shows the code structure also shows the concepts, papers, and benchmarks referenced from that code*. No competitor in this category does that.

### 2.5 Multimodal RAG / ingestion frameworks

- **RAG-Anything** — <https://github.com/HKUDS/RAG-Anything> — ~20.1k stars, active under 6 months, MIT.
  - Own words: "RAG-Anything: All-in-One RAG Framework."
  - Already an LLM-Wiki adjunct.

- **Unstructured.io** — <https://github.com/Unstructured-IO/unstructured> — ~14.7k stars, active under 6 months, Apache-2.0.
  - Own words: "open-source ETL solution for transforming complex documents into clean, structured formats for language models."
  - Killer feature: production-grade element-level partitioning across dozens of formats.

- **Docling** — <https://github.com/docling-project/docling> — ~59.6k stars, active under 6 months, MIT.
  - Own words: "Get your documents ready for gen AI."
  - Killer feature: unified `DoclingDocument` IR, MCP server, plug-and-play LangChain / LlamaIndex / CrewAI / Haystack integrations, audio + ASR, chart understanding.
  - Switching pressure: low — Docling is an ingestion building-block, not a knowledge product.

- **MinerU** — <https://github.com/opendatalab/MinerU> — ~62.8k stars, active under 6 months, AGPL-3.0.
  - Own words: "Transforms complex documents like PDFs and Office docs into LLM-ready markdown/JSON for your Agentic workflows."
  - Killer feature: 109-language OCR, dual VLM+OCR engine, MCP server.
  - Relationship to LLM-Wiki: used through RAG-Anything as a parser option.

- **MarkItDown** — <https://github.com/microsoft/markitdown> — ~123k stars, active under 6 months, MIT.
  - Own words: "Python tool for converting files and office documents to Markdown."
  - Killer feature: simple Python API, AutoGen team backing.

- **MegaParse** — <https://github.com/QuivrHQ/MegaParse> — ~7.4k stars, active under 6 months, Apache-2.0.
  - Own words: "File Parser optimised for LLM Ingestion with no loss. Parse PDFs, Docx, PPTx in a format that is ideal for LLMs."

Read: this category is crowded and consolidating around Docling and MinerU as the reference parsers. LLM-Wiki does not need to compete on parsing — it routes to RAG-Anything which routes to MinerU/Docling. The position is "we use the best parser for each format, and we put the result into a typed graph."

### 2.6 Agent-facing MCP servers that index local content

The MCP server ecosystem is younger and noisier. Most servers are either thin wrappers around a single API (filesystem, GitHub, Slack) or thicker servers that re-expose a vector store. LLM-Wiki's MCP server is unusual in that:

1. It exposes a *typed* schema (`schema` tool returns node types + edge types + wiki kinds).
2. It is multi-project (`list_projects`, `activate_project`).
3. It surfaces both graph search (`search_nodes`, `node_context`, `wiki_page`) and natural-language `ask` over the same registry.

Concretely visible competitors:

- **Cognee MCP** — graph + vector memory, single-project per server.
- **Docling MCP** — document parsing as a tool.
- **MinerU MCP** — PDF parsing as a tool.
- **Zep MCP** — temporal-graph memory.
- **filesystem-mcp / various code-search MCP servers** — surface raw files.

No MCP server in this set exposes a schema endpoint that returns the controlled vocabulary of the underlying graph. That is a small but specific differentiator.

---

## 3. LLM-Wiki's honest current state

### 3.1 Strengths to defend

These are observable in the repo today, not aspirational:

- **Multi-source compile in one pipeline.** `llm_wiki project compile` reads markdown, code, optionally Understand Anything code graph artifacts, optionally RAG-Anything multimodal output, and merges them into a single `ResearchGraph`. No competitor in Section 2.1 does this.
- **Typed research graph.** 41 node types across 5 layers (Field/Taxonomy, Source/Artifact, Concept, Assertion, Synthesis) plus a controlled edge-type vocabulary. The schema is exposed via MCP. This is closer to an academic ontology than to a free-form note graph.
- **MCP server with project registry.** Tools: `schema`, `graph_summary`, `search_nodes`, `node_context`, `wiki_page`, `search_facts`, `timeline`, `ask`, plus `list_projects` / `activate_project`. Multi-project resolution lives in `ProjectRegistry` (file-backed at `~/.llm-wiki/registry.json`).
- **Static HTML output.** Host anywhere, no DB, no server. Page kinds: sources, concepts, entities, papers, repos, topics, syntheses, questions, timeline, graph.
- **i18n built into every doc.** Native localized markdown under `docs/i18n/` and `README.{ko,zh,ja,ru,es,fr}.md` mirrors. Most KM tools do not bother.
- **OAuth-based LLM access (no API keys required).** Codex CLI and Claude CLI work out of the box via OAuth; `CLAUDE_CONFIG_DIR` is respected for multi-account setups. This is unusual — most RAG/KM tools require an API key.
- **Companion-tool composition.** Understand Anything and RAG-Anything are first-class adjuncts, not random forks: stable-id manifests, native graph projection, runtime memory backends.
- **Deterministic compile.** Rerunning `project compile` produces byte-identical output per the project's `about` page. That is a Quartz-class property.

### 3.2 Weaknesses to be honest about

These are real, and most have a named competitor that already solved them. The differentiation bets in Section 4 are chosen to address some of these without picking a fight with the projects that already won the relevant axis.

- **Compile latency.** A 1000+ markdown corpus takes ~10 minutes on first pass. `--changed-only` exists but only re-extracts changed files; companion-graph merges and synthesis re-run regardless. Quartz, Foam, and Logseq do not have this problem because they do not run LLM extraction. **No realistic fix** — only mitigation: incremental and streaming. (Bet B1, B6.)
- **No incremental compile beyond `--changed-only`.** Synthesis and projection do not yet hash-cache their inputs. There is a TODO in `project.py` (lines 310-320) acknowledging the graph-merge step exists precisely because previous compile loops lost data. (Bet B1.)
- **Graph view is one frame.** No spatial canvas, no time-travel, no comparison view. Heptabase (closed source), tldraw, and Obsidian Canvas all have richer spatial editing. (Bet B4, B6.)
- **No live edit.** The wiki is generated. You cannot fix a typo in the rendered HTML and round-trip it back to the source markdown. Logseq, Obsidian, Foam, and Dendron all allow direct edit. (Bet B2 considers this; it is hard.)
- **Concept extraction quality is LLM-prompt-bound.** A recent fix removed filename-shaped concept noise; expect more such fixes. There is no in-loop human review to mark a concept as "junk" and have the next compile honor that. (Bet B5 partially addresses.)
- **No mobile-first reading experience.** The static site is responsive but the graph view is not optimized for touch. Logseq and AppFlowy have native mobile apps.
- **Single-user, file-based.** No collaboration, no sync, no auth. Logseq DB version is moving toward RTC; AppFlowy has multi-user.
- **No saved views, dashboards, pinnable queries.** Tana has supertag views; Obsidian has DataView; we have search.
- **Marketing surface is plain README.** No demo site, no comparison table, no public hosted example. Quartz has `quartz.jzhao.xyz`. Cognee has `cognee.ai`. Docling has a docs site with live examples. LLM-Wiki has none. (Bet M1 in Section 5.)

### 3.3 What competitors already solved (so we should not try)

- **Document parsing accuracy.** Docling and MinerU are the standard. Use them through RAG-Anything; do not build a fourth parser.
- **Long-term agent memory at conversation scale.** Mem0 and Letta own this. LLM-Wiki should not pretend to be a conversation memory layer.
- **Block-level editor UX.** Logseq, AppFlowy, and Anytype have multi-year head-starts. Do not chase.
- **Real-time collaboration.** Out of scope for a static-output project.

---

## 4. Differentiation bets

### 4.1 Summary table (ranked by impact / tractability balance)

| # | Bet | Effort | Impact | Risk |
|---|-----|--------|--------|------|
| B1 | Streaming compile with live wiki preview | M | High | Medium |
| B2 | Cross-project graph linking via the registry **(shipped)** | S | High | Low |
| B3 | Per-page embedded ask box | S | High | Low |
| B4 | Spatial canvas mode for graph subsets | M | Medium | Medium |
| B5 | Schema evolution via config (user-defined node types) | M | Medium | Low |
| B6 | Agent-driven compile journal page | S | Medium | Low |
| B7 | Demo site + comparison story | S | Decisive (marketing) | Low |

Ranking heuristic: B7 is decisive *for adoption* but not for the product. B1 / B2 / B3 are the three product bets the maintainer should pick from for the next sprint. B4 and B5 are second-wave. B6 is a small unlock that compounds the "agent memory compiler" framing.

### 4.2 Detail

#### B1. Streaming compile with live wiki preview

**Why this matters.** The single biggest user-experience gap is the 10-minute compile-blindness on first run. Today users start `project compile`, see a progress bar, and wait. If the partial graph were rendered incrementally — paper pages appearing as papers are extracted, concept pages filling in as concepts are discovered, the graph view re-laying-out as nodes arrive — the same compile becomes a watched process rather than a tax. No competitor in Section 2 ships this for KG-based wikis: Quartz does not run extraction, Logseq does not have an extraction phase, GraphRAG's pipeline is opaque.

**What it would look like.** `project compile --watch` starts a local server immediately, opens the wiki in the browser, and the wiki updates section-by-section as the extractor emits nodes. The graph view animates in. A small "compile status" widget in the header shows "extracted 412 / ~2400 nodes, currently processing `papers/transformer.md`". The user can click any half-extracted page and read it; the page shows what is provisional.

**Implementation sketch.**

- Emit a `ResearchGraph` delta stream from the extractor (already partially in place — `BatchIngestRunner` knows about per-file extraction).
- Add a `frontend.py`-level SSE or websocket endpoint that pushes graph deltas to the browser.
- Reuse `wiki_projector.partition_graph` per delta and write affected pages incrementally.
- The graph view's `build_graph_payload_split` already chunks by kind; bind it to the same SSE channel.
- Compile becomes idempotent at the page level: late-arriving deltas overwrite the page in-place.

**Risk.** Page consistency during compile (a concept page might link to a paper page that is not yet written). Mitigation: render placeholders for unknown links, fix on the next delta. Determinism is preserved because the final state is identical to today's batch compile.

**Differentiates from.** Quartz (one-shot build, no progressive), Logseq (no compile concept), Cognee (no static site), GraphRAG (CLI pipeline, no live view).

#### B2. Cross-project graph linking via the registry

**Why this matters.** The registry already exists (`~/.llm-wiki/registry.json`, shared by CLI and MCP). Today each registered project is an island. If a node in project A could reference a node in project B by stable id — `wiki://other-project/concepts/attention-mechanism` — the graph view could show both clouds with bridges, and `wiki_page` lookups could resolve cross-project. Several users will register one project per problem domain (research, work, side-projects) and will want them to talk.

**What it would look like.** In any source markdown, `[[wiki://research/concepts/RLHF]]` resolves at compile time to the canonical node in the `research` registered project. The graph view has a toggle "show cross-project edges". The MCP `ask` tool can be scoped to a single project or to "any registered project". The wiki's `/about` page lists incoming cross-project references.

**Implementation sketch.**

- Extend `node_href` and `_canonical_slug` to recognize the `wiki://<project>/...` scheme.
- Add a `cross_project_resolve(uri)` helper that uses `ProjectRegistry` to map `<project>` → root and looks up the slug in that project's manifest.
- Update `build_graph_payload_split` to optionally pull bridge nodes from registered siblings (lazy load, keyed by project alias).
- MCP `wiki_page` and `ask` already accept `--project`; add `--scope all-registered` for cross-project queries.

**Effort: S.** No new data model — only resolver wiring and a tiny graph-view affordance.

**Risk.** Stale links if a sibling project is unregistered. Mitigation: degrade to a tombstone page that says "node X was in project Y, which is no longer registered."

**Differentiates from.** Every personal-knowledge tool in Section 2.1 — none of them have a cross-vault linking primitive at this level. Obsidian has vault-internal links only.

**Status (shipped).** Implemented in `llm_wiki/cross_project.py` (`parse_wiki_uri`, `cross_project_resolve`, `render_cross_project_link`, `find_wiki_uris_in_text`), wired into `build_graph_payload` (bridge nodes with `group="external"` + cross-project edges), `site/js.py` (violet palette + "Cross-project bridges" toolbar toggle), and `site/tokens.py` (tombstone / unbuilt / broken link CSS). The MCP `ask` tool and the top-level `llm_wiki ask` CLI gained `scope` / `scope_aliases` arguments; `scope="all-registered"` fans out and returns `{"scope", "question", "by_project"}`. Tests in `tests/test_cross_project.py` and `tests/test_cli_ask_scope.py`.

#### B3. Per-page embedded ask box

**Why this matters.** The runtime ask works at the CLI and MCP level today. Putting it inside every concept / paper / repo page changes the read experience. Users land on `concepts/RLHF.html` and the page has an inline "ask anything about this concept" box that queries the local memory backend (RAG-Anything or Cognee) scoped to the relevant subgraph. This is the kind of feature you can only ship if you already have a typed graph *and* a runtime backend — which is exactly LLM-Wiki's situation.

**What it would look like.** Bottom of every detail page: a chat-style box with placeholder text "Ask about this page". Submitted question is sent to a local endpoint (`localhost:8765/ask?node=concept:rlhf`) that calls `llm_wiki.query.ask_project` with the page's node id as a scope hint. Answer streams back; citations are inline links to other wiki pages.

**Implementation sketch.**

- Add a small JS island in `site/pages.py` for the ask widget (the rest of the site stays static).
- `project serve` already exists; extend the local server to accept POST `/ask` with `{node_id, question}` and delegate to `ask_project`.
- Pass `node_id` as a context hint to the backend; for RAG-Anything, prepend the subgraph rooted at that node to the query.
- For deployed static sites without a local server: hide the widget. Optional: ship a "host this with `llm_wiki serve` to enable ask" footer.

**Effort: S.** Most pieces are already in place — `ask_project` is the existing entry point, the static page only needs a fetch wrapper.

**Risk.** Backend may be slow or absent; widget needs graceful degradation. Deployed static-only sites lose the feature.

**Differentiates from.** Cognee, Mem0, Letta — all have backends; none put the backend inside a static knowledge page. LightRAG has a web UI but it is a separate app, not a per-page widget.

#### B4. Spatial canvas mode for graph subsets

**Why this matters.** The current graph view is force-directed and full-corpus. For a 2400-node graph it is dense to the point of being a single hairball after partition. Users who want to "spread out attention", "compare two papers", or "build a poster of the RLHF subgraph" need a spatial canvas where they pin, group, and annotate. Heptabase and Obsidian Canvas have this. None of the open-source PKM tools in Section 2.1 have it integrated with a typed graph.

**What it would look like.** A new top-level route `/canvas` that opens a tldraw-like infinite canvas. Users drag wiki nodes onto the canvas; the canvas saves layout to `.llm-wiki/canvases/<name>.json` (deterministic, committable). Pins, groups, and freehand annotations are first-class. Each canvas is itself a wiki page (a new node kind `Canvas` in the schema).

**Implementation sketch.**

- Bundle `tldraw` as a JS island, mounted at `/canvas/<slug>.html`.
- Persist canvas state as JSON under `.llm-wiki/canvases/`; project compile picks it up and renders as static HTML (read-only) plus a "open in editor" link.
- Add `Canvas` to `ResearchNodeType` enum (impact: one enum line, one routing entry in `pages.py`).
- Edges from canvas pins to underlying wiki nodes use the existing edge vocabulary (`mentions`, `derived_from`).

**Effort: M.** Most of the cost is the editor integration and persistence, not the graph plumbing.

**Risk.** Canvas state can drift from the underlying graph if nodes are renamed or removed. Mitigation: canvases store stable ids and degrade on missing nodes.

**Differentiates from.** Quartz, Foam, Dendron, Logseq (no spatial canvas). Obsidian Canvas exists but is not on top of a typed graph.

#### B5. Schema evolution via config (user-defined node types)

**Why this matters.** Today the 41 node types are hardcoded in `ResearchNodeType` (an enum). For users whose domain is not LLM research — say, a security team with `Incident`, `RootCause`, `Mitigation`, `RFC` — the schema is rigid. Zep solved this with an ontology directory. LLM-Wiki has the wrong shape today.

**What it would look like.** A new `.llm-wiki/schema/custom_types.yaml` declares additional node types and edges. Example:

```yaml
node_types:
  Incident:
    layer: source
    description: A security incident or postmortem
    icon: warning
  RootCause:
    layer: assertion
edge_types:
  caused_by:
    from: [Incident]
    to: [RootCause]
```

`project compile` reads the file, augments the `ALLOWED_NODE_TYPES` set, and the LLM extractor receives the extended schema in its system prompt.

**Implementation sketch.**

- Move `ResearchNodeType` from a closed enum to an open `NodeTypeRegistry` class (preserve a `.builtin()` set for back-compat).
- Add a YAML loader that merges custom types in at compile entry.
- Plumb the extended schema through the LLM extractor prompt and through `mcp_server.schema` so MCP clients see the augmented vocabulary.
- Page routing (`ROUTE_FOR_KIND` in `site/pages.py`) needs a fallback for custom kinds — default to `/entities/` or a new `/custom/` route.

**Effort: M.** The hardest part is the migration from `Enum` to a registry without breaking existing call sites; the rest is mechanical.

**Risk.** Custom node types degrade extraction quality if the LLM does not have examples. Mitigation: require the user to provide 1-3 example sentences per custom type in the YAML.

**Differentiates from.** Every other tool in Section 2.1 and 2.2 except Zep. Zep does this for conversational ontology; LLM-Wiki would do it for document ontology.

#### B6. Agent-driven compile journal page

**Why this matters.** The project already runs agents (Codex / Claude CLI) during compile. Today their output is discarded after the graph is updated. If each compile emitted a markdown journal page — "what I learned this run, what changed, what is now confusing" — the wiki gains a self-narrating history. The page becomes a synthesis node (`Synthesis` type already exists) tagged with the compile timestamp. Over time these pages are themselves searchable.

**What it would look like.** After `project compile` finishes, a new `syntheses/compile-2026-05-13.md` page is generated. Sections: "new concepts this run", "deleted/merged concepts", "papers added", "open questions raised by the LLM", "files the extractor flagged as ambiguous". The synthesis page is linked from `/timeline` and from `/about`.

**Implementation sketch.**

- Hook into the existing `AgentHarness` / `harness_sessions.py` infrastructure — sessions already record agent transcripts.
- Add a `SynthesisJournalWriter` that runs at the end of compile, reads the harness session, and emits a `Synthesis` node with structured sections.
- The journal node uses the existing page rendering pipeline (no new route).
- The agent is the same Codex / Claude CLI you already authenticated with; no new dependency.

**Effort: S.** The bones exist (`harness_sessions.py`, `Synthesis` node type, `temporal.py` for timeline integration).

**Risk.** Token cost on every compile. Mitigation: gate behind `--journal` flag; default off.

**Differentiates from.** Every competitor — nobody generates a build-log knowledge page that is itself part of the knowledge base.

#### B7. Demo site + comparison story (marketing bet)

**Why this matters.** This is the gating bet. The maintainer's stated goal — "appealing" — is gated on having a hosted demo any GitHub visitor can click. The product is invisible behind a README until then. See Section 5 for the marketing breakdown.

**Effort: S.** A 1-2 day push.

**Impact: Decisive for adoption, neutral for product.**

---

## 5. Marketing / positioning

### 5.1 Tagline candidates

Each tested against three filters: (a) is it specific, (b) does it tell you something no competitor can say, (c) is it under 12 words.

1. **"A typed knowledge graph compiled from your sources, served as a static wiki."**
   - Specific: yes. Differentiated: only Quartz is static; only GraphRAG is typed; only LLM-Wiki is both, plus has compile-from-source. Length: 13 words, slightly over.
   - Best if you want the literal description.

2. **"Compile your sources into a typed wiki agents can read."**
   - Specific: yes. Differentiated: "agents can read" is the MCP angle. Length: 10 words.
   - Best if you want the agent-facing audience.

3. **"Multi-source knowledge compiler with a typed graph and MCP server."**
   - Specific: yes. Differentiated: explicit feature triple. Length: 11 words.
   - Best for HN headline.

4. **"From papers, code, and PDFs to a navigable wiki — no API key required."**
   - Specific: yes. Differentiated: the OAuth-no-API-key angle is genuinely uncommon. Length: 13 words.
   - Best for developer-audience launch.

5. **"A wiki you compile, not write."**
   - Specific: less so. Differentiated: punchy, captures the model. Length: 6 words.
   - Best for Twitter; risk is sounding glib.

**Recommendation if forced to pick one:** option 2 — *"Compile your sources into a typed wiki agents can read."* It is short, mentions the unique compile-step, hints at typing, and surfaces the MCP angle without naming the protocol.

### 5.2 Comparison table

Rows: features that matter for the audience LLM-Wiki is trying to win.
Columns: the four closest open-source competitors + LLM-Wiki.

| Feature | LLM-Wiki | Quartz | Logseq | Cognee | Foam |
|---|---|---|---|---|---|
| Static HTML output | yes | yes | partial (export) | no | partial (publish) |
| Built-in graph view | yes | yes | yes | yes (separate UI) | yes (VSCode) |
| Typed node schema | yes (41 types) | no | partial (tags) | yes | no |
| Concept extraction from sources | yes (LLM) | no | no | yes | no |
| Multimodal ingestion (PDF/image) | yes (via RAG-Anything) | no | partial (embeds) | yes | no |
| Code-graph ingestion | yes | no | no | partial | no |
| MCP server | yes | no | no | yes | no |
| Multi-project registry | yes | no | yes (graphs) | partial | no |
| Works without API key (OAuth) | yes | n/a | n/a | no | n/a |
| Multi-language i18n docs | yes | partial | yes | partial | partial |
| Deterministic byte-identical compile | yes | yes | n/a | no | n/a |
| Per-page ask widget (proposed B3) | not yet | no | no | no | no |
| Live edit | no | partial | yes | n/a | yes |
| Mobile-first reading | no | yes | yes | n/a | n/a |
| Real-time collaboration | no | no | yes (DB beta) | no | no |

No softening: where LLM-Wiki is behind, it says no. The point of the table is for users to see which trade they are making.

### 5.3 What the demo site should show

Pick three demos. One sentence each.

1. **Self-hosting demo.** The LLM-Wiki repo compiled by LLM-Wiki, hosted at (proposed) `llm-wiki.dev`. Lets visitors browse the wiki of the project they are reading about — meta, but immediately shows what the output looks like for a real codebase.

2. **A research-corpus demo.** A curated paper set (say, 30 papers on RLHF and reasoning) compiled into a wiki. Visitors see concept pages, paper pages, and the graph view densely populated. This is the "what your literature review could look like" pitch.

3. **A repo-understanding demo.** A small but real OSS project compiled by LLM-Wiki, showing the code-graph pages, the cross-references to external papers cited in code comments, and the per-page ask widget. This is the "what `aider --map` could become if it were also a wiki" pitch.

Each demo should ship with a "compile this yourself in 3 commands" callout.

### 5.4 HN / Twitter launch story outline

**Angle.** Not "I built a knowledge graph." Not "I built another RAG." The angle is *the compile model* — LLM-Wiki produces a deterministic static wiki from messy sources, the same way a build tool produces a binary from source. This positions LLM-Wiki next to Quartz on the static-output axis and next to GraphRAG on the typed-graph axis, but the *unique* claim is that it is the only project that sits at the intersection and also exposes an MCP server.

**Draft post copy.**

> I have been building LLM-Wiki, a knowledge-graph compiler for projects that have outgrown their docs but not yet earned a custom UI. Point it at a folder of markdown, code, and PDFs; it returns a typed graph (41 node types, controlled edge vocabulary), a static HTML wiki, and an MCP server that lets agents query the same graph the humans read. It uses Codex or Claude CLI over OAuth, so the default path is free of API keys. It composes Understand Anything for code graphs and RAG-Anything for multimodal sources rather than reinventing those.
>
> The compile model is the part I think is interesting. Most knowledge tools are editors (Logseq, Obsidian, AppFlowy) or runtimes (Cognee, Mem0, Letta). LLM-Wiki is a build tool: deterministic output, reruns produce byte-identical pages, the graph view and the wiki and the MCP server are three views of the same artifact. The wiki is meant to be regenerated, not maintained. I would love feedback on whether this framing lands — and on whether the next thing I should build is streaming compile (watch the wiki render in real time) or per-page ask boxes (chat with any concept page using your local memory backend). Repo, comparison table, and a demo wiki of the project's own source are linked.

**Twitter thread version.** Six tweets, one feature per tweet, last tweet links the demo. Lead with the compile-model framing, not the feature list.

---

## 6. Open questions for the maintainer

These are decisions Section 4 does not make for you. They are listed here because each one shifts which bets are tractable.

1. **Hosted demo policy.** Are you willing to run a free-tier hosted compile so HN visitors can try without cloning? If yes, B7 is two days. If no, B7 is "demo videos + GitHub Pages-hosted pre-compiled examples," which is one day but lower impact.

2. **Editor relationship.** Do you want LLM-Wiki to remain compile-only forever, or do you eventually want to ship an editor? The honest answer drives whether B2 (cross-project linking, no editor needed) or B4 (spatial canvas, soft editor) goes first. The case for "compile-only forever" is that it leaves Logseq / AppFlowy / Foam alone to do the editor job; the case against is that users will keep asking.

3. **MCP-first vs static-first audience.** B3 (per-page ask box) shines for static-first readers. B6 (compile journal) shines for agent-first operators. Pick which audience is the explicit primary for the next launch.

4. **Custom-schema use case priority.** B5 is a 1-3 week task that pays back only if there is a non-research user segment you want to attract (security incidents, RFCs, product specs). If LLM-Wiki stays explicitly research-focused, defer B5 indefinitely.

5. **Companion-tool drift risk.** RAG-Anything and Understand Anything are external. If either project deprecates, ships a breaking change, or changes license, LLM-Wiki's multimodal and code-graph stories degrade. Worth pinning explicit version constraints in the integration docs.

---

## 7. Recommendation

If the maintainer picks two bets, pick **B7 + B3** (demo site + per-page ask). The first makes the product visible; the second is the visible product. Total effort: under two weeks. Risk: low.

If three bets, add **B2** (cross-project linking). It is the smallest of the three product bets, leverages existing registry infrastructure, and produces a screenshot for the launch post that no competitor can match.

If four bets, add **B1** (streaming compile). This is the deepest investment but solves the single most-cited weakness in Section 3.2 and makes the product feel alive instead of batch.

The three bets to *not* pick first: B4 (canvas — wait until the demo proves the audience is here), B5 (schema config — wait until a non-research user actually asks), B6 (compile journal — wait until B1 is done so the journal has streaming context to summarize).

---

*End of document.*
