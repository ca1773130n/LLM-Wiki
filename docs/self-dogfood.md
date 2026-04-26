# Self-dogfood Demo

This project can index itself. The self-dogfood flow proves that LLM-Wiki can be installed, initialized inside its own repository, ingest its own docs/source/tests/scripts, compile graph artifacts, and build the static web frontend.

## Commands

From the repository root:

```bash
# Ensure the shell command is installed.
./scripts/install.sh --dir "$PWD"
export PATH="$HOME/.local/bin:$PATH"

# Initialize this repository as an LLM-Wiki project.
llm_wiki project init \
  --name llm_wiki_self \
  --source-kind Repository \
  --source README.md \
  --source docs \
  --source llm_wiki \
  --source tests \
  --source scripts

# Ingest/compile the configured sources.
llm_wiki project compile --changed-only

# Rebuild the static frontend explicitly.
llm_wiki project build-site

# Serve locally.
llm_wiki project serve --port 8765
```

Open:

```text
http://127.0.0.1:8765/
```

## Generated workspace

The self-demo writes generated artifacts under:

```text
.llm-wiki/
```

Key artifacts:

```text
.llm-wiki/config.json
.llm-wiki/graph.json
.llm-wiki/manifest.json
.llm-wiki/sqlite.db
.llm-wiki/report.md
.llm-wiki/competitive_report.md
.llm-wiki/temporal_facts.jsonl
.llm-wiki/graphiti_episodes.jsonl
.llm-wiki/markdown_projection/
.llm-wiki/obsidian_vault/
.llm-wiki/agent_harness/
.llm-wiki/site/
.llm-wiki/cognee_bundle/
```

The generated workspace is intentionally not committed by default. It is reproducible from the repository source with the commands above.

## Latest verified run

Verified on `2026-04-27 07:07:55 KST` from the LLM-Wiki repository itself.

```text
install command: ./scripts/install.sh --dir /Users/neo/Developer/Projects/LLM-Wiki --skip-shell-config
init command:    llm_wiki project init --name llm_wiki_self --source-kind Repository --source README.md --source docs --source llm_wiki --source tests --source scripts
ingest command:  llm_wiki project ingest README.md docs --changed-only
compile command: llm_wiki project compile
site command:    llm_wiki project build-site
serve command:   llm_wiki project serve --port 56821
browser URL:     http://127.0.0.1:56821/
```

Final artifact counts:

```text
nodes:              594
edges:              960
markdown notes:     596
obsidian notes:     598
agent harness files: 14
cognee nodes:       594
cognee edges:       960
graphiti episodes: 960
temporal facts:     960
site files:         index.html, graph.json, search-index.json, llms.txt
```

Top node types:

```text
CodeFunction:          420
Dependency:             55
CodeClass:              53
SourceFile:             46
Repository:              7
EvidenceSpan:            4
Claim:                   2
ResearchField:           1
MethodologicalConcept:   1
ApproachFamily:          1
```

Browser verification:

```text
loaded title: llm_wiki_self
visible stats: 594 nodes / 960 edges
search smoke: CodeGraphExtractor returned CodeClass/CodeFunction results
```

## What this demonstrates

- Public install path works.
- `llm_wiki` shell command works.
- A repository can attach a project-local `.llm-wiki` workspace.
- Research/documentation markdown and development-code graph nodes can coexist.
- Markdown, Obsidian, frontend, Graphiti, Cognee, SQLite, report, and agent-harness projections are produced from one graph pipeline.
- The static HTML frontend can browse the project graph without a JavaScript build step.
