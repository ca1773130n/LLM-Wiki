# Demo Corpus + Session Mock Plan

> Plan only — no code yet. Reviewed and accepted by maintainer before authoring begins.

## 1. Why

The current GH Pages dogfood deploy compiles only this repo's own bare contents (73 concepts, 88 entities). Visitors see a graph view that mostly reflects LLM-Wiki's internal docs — not a "what your literature review could look like" or "what your daily research digest could look like" experience. The README pitches a typed knowledge compiler for research, but the live demo doesn't yet demonstrate that.

The demo corpus is a single curated, committed dataset that simulates one developer's weekly research workflow over ~6 weeks. The CI workflow points at it as a secondary source root so the deploy becomes a real product story rather than a recursive doc tour.

## 2. Scope (what the demo MUST show)

The deployed site must let a visitor in 60 seconds understand:

- Papers are first-class entities with typed metadata (authors, arXiv ids, organizations, methods, results).
- Repos are first-class entities with cross-references to the papers they implement.
- Concepts (RLHF, Diffusion, Gaussian Splatting, MoE, etc.) are extracted from prose and link to multiple papers/repos.
- Daily and weekly digests aggregate papers and surface trends — a Synthesis node ties them.
- Open research questions appear as their own kind, cross-referenced from syntheses.
- Agent sessions are part of the wiki — at least one full session shows the agent assembling a digest.
- The graph view has interesting topology (dense concept clusters, paper→repo bridges, cross-week edges).

Out of scope for v1: multilingual demo content (English only), images/PDFs (raganything ingestion is gated separately), live re-compile on the demo (still static).

## 3. Domain choice

**Pick one focused research area.** A focused domain produces a dense graph; a sprawling one produces a thin one. Two candidates:

| Option | Why pick | Why not |
|---|---|---|
| **3D reconstruction / Gaussian Splatting / SLAM** | Hot, lots of public papers, the user's existing local corpus already covers it (validation that the schema works for this domain) | Niche outside CV community |
| **Agent memory + LLM tooling** | Meta-aligned with LLM-Wiki itself (the demo is "research about the project that built it"); good for HN audience | Risk of feeling navel-gazing |

**Recommendation: Option A (3D / Gaussian Splatting).** It's a real research area with clear papers, public OSS repos, and well-known concepts. The meta-option (B) can be a *second* demo corpus later — one demo per audience.

## 4. Corpus content inventory

Sized to produce a graph with ~50 concepts, ~25 papers, ~12 repos, ~8 entities, ~6 syntheses, ~3 open questions.

### 4.1 Papers (25 mock arXiv-style markdown files)

Source: arXiv abstracts are CC0 / no copyright; we can reuse abstracts verbatim from real Gaussian Splatting / 3D reconstruction papers. The metadata (authors, arXiv id, date) stays factual. The "body" of each markdown is a hand-written 200-400 word summary, NOT the paper PDF text.

Layout: `examples/demo-corpus/data/research/papers/<arxiv_id>/{paper.md,abstract.md}`

Each `paper.md` has frontmatter:

```yaml
---
type: Paper
arxiv: 2410.00121
title: "..."
authors: ["..."]
date: 2026-04-10
methods: [GaussianSplatting, Diffusion]
datasets: [Mip-NeRF360, DTU]
metrics: [SSIM, PSNR, LPIPS]
---
```

…and a 200-400 word body mentioning concepts, methods, results in prose so the extractor picks them up.

### 4.2 Repos (12 OSS README mirrors)

Source: GitHub READMEs of real OSS projects in the domain (MIT/Apache/BSD licensed — verified per repo). We mirror the README text into our corpus, NOT the code. Each repo gets a metadata sidecar.

Layout: `examples/demo-corpus/data/research/repos/<org>-<name>/{readme.md,about.md}`

Examples: `graphdeco-inria/gaussian-splatting`, `NVlabs/instant-ngp`, `colmap/colmap`, `nerfstudio-project/nerfstudio`. All MIT/Apache.

### 4.3 Daily digests (6 mock daily-roundup markdown files)

Format: a fabricated daily roundup that bundles 3-5 of the papers/repos with one-line commentary. Mimics how a researcher might journal their daily reading.

Layout: `examples/demo-corpus/data/research/daily/2026-04-{10,15,20,25,30}/digest.md`, `2026-05-05/digest.md`.

### 4.4 Weekly syntheses (2 hand-written syntheses)

Format: 800-word essays synthesizing the daily digests for that week. Pulls out a trend ("Gaussian Splatting is converging with SLAM"), grounded in the papers cited. Hand-written by us (Claude can draft).

Layout: `examples/demo-corpus/data/research/weekly/2026-W17/synthesis.md`, `2026-W18/synthesis.md`.

### 4.5 Open questions (3 written-by-us research gaps)

One-paragraph each, framed as questions the corpus surfaces but doesn't yet answer.

Layout: `examples/demo-corpus/data/research/questions/*.md`.

### 4.6 README + frontpage for the corpus

`examples/demo-corpus/README.md` explains what visitors are looking at: "This is a curated 6-week research log on Gaussian Splatting and 3D reconstruction. The papers are real (abstracts via arXiv CC0). The repo READMEs mirror MIT/Apache OSS projects. Daily digests, weekly syntheses, and open questions are synthetic narrative glue, hand-written for the demo."

## 5. Agent-session conversation mock

One full session showing a realistic "agent assembles a weekly digest" workflow. Format must match the existing `.agent-sessions/` JSONL conventions (read `llm_wiki/harness_sessions.py` for the exact shape).

### 5.1 Plot

User: "Compile this week's research digest on Gaussian Splatting."

Agent over 15-20 turns:
1. Searches the corpus for recent papers (tool call → `mcp__llm_wiki__search_nodes`).
2. Pulls 5 paper pages (`mcp__llm_wiki__wiki_page`).
3. Reads 2 repo READMEs.
4. Notices a recurring concept (`Multi-View Consistency`) that none of the papers fully solve.
5. Drafts an Open Question node about it.
6. Synthesizes a 600-word weekly digest with citations.
7. Writes the digest back to disk via tool use.

### 5.2 Realism rules

- Every tool call must be one the LLM-Wiki MCP server actually exposes (verified against `llm_wiki/mcp_server.py`).
- All cited papers/repos must exist in the demo corpus (§4.1, §4.2).
- The agent's "scratch reasoning" between turns should be 1-2 sentences max — not an essay. Realistic agent transcripts are terse.
- Final synthesis output becomes the file `examples/demo-corpus/data/research/weekly/2026-W18/synthesis.md` referenced in §4.4 (i.e., session and synthesis are mutually consistent).

Layout: `examples/demo-corpus/.agent-sessions/2026-05-12-weekly-digest/transcript.jsonl`.

## 6. Authoring approach

### 6.1 Who writes the content

| Piece | Source | Effort |
|---|---|---|
| Paper abstracts | arXiv (verbatim, CC0) | trivial |
| Paper bodies (200-400 words each) | Drafted by Claude per paper, fact-checked against the abstract | 25 × 10min = ~4h |
| Repo READMEs | Mirrored from public GitHub (license check first) | 12 × 5min = ~1h |
| Repo `about.md` (one-line cross-references) | Drafted by us | 12 × 5min = ~1h |
| Daily digests | Drafted by us, cross-referencing real corpus files | 6 × 15min = ~1.5h |
| Weekly syntheses | Drafted by us | 2 × 30min = ~1h |
| Open questions | Drafted by us | 3 × 10min = ~0.5h |
| Agent session | Drafted by us in JSONL | 1 × 90min = ~1.5h |
| Corpus README + glue | Drafted by us | ~30min |

Total: ~11 hours of focused authoring. A focused subagent can do it in 2-3 dispatches of ~3-4h each.

### 6.2 License hygiene

For every external source mirrored into the corpus, record the source URL + license in a `LICENSES.md` sidecar at the corpus root. Reject any source that isn't CC0 / MIT / Apache / BSD. arXiv abstracts are explicitly CC0 per arXiv terms of use.

## 7. CI integration

Two changes to the existing `.github/workflows/build-demo.yml`:

1. Add `--source examples/demo-corpus/data` and `--source examples/demo-corpus/.agent-sessions` to the `project setup --yes ...` step.
2. Add `examples/demo-corpus/README.md` and `examples/demo-corpus/.agent-sessions/*` as additional ingested sources.

The repo's own contents are also still compiled (so the README, docs/, etc. still appear on the deploy). The demo corpus stacks on top.

Acceptance check: after CI runs, the deploy's `/concepts/` index page should show ≥40 concepts and `/papers/` should show ≥20. The graph view at `/graph/index.html` should have a recognizable density cluster around the Gaussian Splatting concept.

## 8. Effort + sequencing

| Phase | Effort | Output |
|---|---|---|
| Phase 1 — License hygiene + arXiv mirror | 30min | `examples/demo-corpus/LICENSES.md`, 25 abstract.md files (CC0 verbatim) |
| Phase 2 — Paper bodies | 4h | 25 × `paper.md` files with frontmatter + 200-400 word summaries |
| Phase 3 — Repo READMEs | 2h | 12 × `readme.md` + `about.md` files |
| Phase 4 — Digests, syntheses, questions | 3h | 6 daily + 2 weekly + 3 questions + corpus README |
| Phase 5 — Agent session transcript | 1.5h | one realistic JSONL session that cross-references the corpus |
| Phase 6 — CI wiring + verify deploy | 30min | workflow edit + reverify GH Pages |

**Total: ~11.5h, dispatchable in 2-3 subagent waves.** Phase 1 and Phase 2 must run sequentially (bodies cite the abstracts). Phases 3, 4 can run in parallel after Phase 2. Phase 5 depends on the corpus being authored. Phase 6 is trivial.

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Fabricated paper bodies feel hollow | Limit body content to claims the abstract supports; don't invent results. |
| Daily digests feel uniform | Vary tone, length, and which concepts get singled out. Some days have 3 papers, some have 5. |
| Agent session feels scripted | Use real LLM-Wiki MCP tool names + plausible noisy intermediate steps (one false-positive search, one re-fetch). |
| Demo gets stale as upstream papers/repos evolve | Pin everything to a snapshot date (today). Don't promise "live" data. |
| Licensing audit reveals a non-permissive source | LICENSES.md is the gate. Reject anything not green. |

## 10. Open decisions for the maintainer

1. **Domain confirmation.** Stick with Gaussian Splatting / 3D reconstruction, or pick agent-memory + LLM-tooling? Recommendation in §3.
2. **Corpus size.** 25 papers / 12 repos is calibrated for a navigable demo. Want bigger (e.g., 50/25) for a denser graph? More work but more impressive.
3. **Session count.** One end-to-end session, or two (one digest, one paper-deep-dive)? Recommendation is one for v1; second one is a fast follow.
4. **Localization.** Demo content stays English-only for v1. If you want multilingual demo content too, that doubles the authoring time.

## 11. Acceptance criteria

After the corpus + workflow change ships and the next CI run completes:

- [ ] `https://ca1773130n.github.io/LLM-Wiki/concepts/` shows ≥40 concepts.
- [ ] `https://ca1773130n.github.io/LLM-Wiki/papers/` shows ≥20 papers, all with non-empty bodies.
- [ ] `https://ca1773130n.github.io/LLM-Wiki/repos/` shows ≥10 repos.
- [ ] `https://ca1773130n.github.io/LLM-Wiki/syntheses/` shows ≥2 weekly syntheses + 6 daily digests.
- [ ] `https://ca1773130n.github.io/LLM-Wiki/questions/` shows 3 open questions.
- [ ] `https://ca1773130n.github.io/LLM-Wiki/sessions/` shows the demo session transcript.
- [ ] `https://ca1773130n.github.io/LLM-Wiki/graph/` has a visible dense cluster around "Gaussian Splatting" or whichever core concept gets seeded.
- [ ] `examples/demo-corpus/LICENSES.md` lists every external source.
- [ ] No CI regression — workflow still finishes in <2 minutes.
