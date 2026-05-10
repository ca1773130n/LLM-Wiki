# Self-dogfood 데모

<!-- translations:start -->
<p align="center"><a href="../self-dogfood.md">English</a> · <a href="self-dogfood.ko.md">한국어</a> · <a href="self-dogfood.zh.md">中文</a> · <a href="self-dogfood.ja.md">日本語</a> · <a href="self-dogfood.ru.md">Русский</a> · <a href="self-dogfood.es.md">Español</a> · <a href="self-dogfood.fr.md">Français</a></p>
<!-- translations:end -->
이 프로젝트는 자기 자신을 인덱싱할 수 있습니다. self-dogfood 흐름은 LLM-Wiki를 설치하고, 자체 저장소 안에서 설정하고, 자체 docs/source/tests/scripts를 수집하며, 선택적으로 Understand Anything과 Cognee를 새로고침하고, 그래프 아티팩트를 컴파일하고, 정적 웹 프론트엔드를 빌드할 수 있음을 증명합니다.

## 명령

저장소 루트에서:

```bash
# shell 명령이 설치되어 있는지 확인합니다.
./scripts/install.sh --dir "$PWD"
export PATH="$HOME/.local/bin:$PATH"

# 이 저장소를 LLM-Wiki 프로젝트로 설정합니다.
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
  --run-cognee \
  --install-cognee

# 구성된 소스를 컴파일합니다.
llm_wiki project compile

# 정적 프론트엔드를 명시적으로 다시 빌드합니다.
llm_wiki project build-site

# 로컬에서 제공합니다.
llm_wiki project serve --port 8765
```

열기:

```text
http://127.0.0.1:8765/
```

## 생성된 워크스페이스

self-demo는 생성된 아티팩트를 다음 위치에 씁니다:

```text
.llm-wiki/
```

주요 아티팩트:

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

생성된 워크스페이스는 기본적으로 커밋하지 않도록 의도되어 있습니다. 위 명령으로 저장소 소스에서 재현할 수 있습니다.

## 최근 검증된 실행

LLM-Wiki 저장소 자체에서 `2026-04-27 11:11:23 KST`에 검증되었습니다.

```text
install command: ./scripts/install.sh --dir /Users/neo/Developer/Projects/LLM-Wiki --skip-shell-config
setup command:   llm_wiki project setup --yes --name llm_wiki_self --source README.md --source docs --source llm_wiki --source tests --source scripts --with-understand-anything --install-understand-anything --understand-anything-platform codex --run-cognee --install-cognee
ingest command:  llm_wiki project ingest README.md docs --changed-only
compile command: llm_wiki project compile
site command:    llm_wiki project build-site
serve command:   llm_wiki project serve --host 0.0.0.0 --port 56821
local URL:       http://127.0.0.1:56821/
LAN URL:         http://192.168.45.130:56821/
```

최종 아티팩트 수:

```text
nodes:               667
edges:               1020
markdown notes:      684
obsidian notes:      686
agent harness files: 14
cognee nodes:        667
cognee edges:        1020
graphiti episodes:  1020
temporal facts:      1020
site files:          index.html, nodes/index.html, sources/index.html, graph/index.html, graph.json, search-index.json, llms.txt, llms-full.txt, manifest.json, assets/style.css, assets/app.js
node pages:          687
source pages:        56
```

상위 노드 유형:

```text
CodeFunction:    452
Dependency:       55
CodeClass:        54
Concept:          51
SourceFile:       47
SourceDocument:    7
CodeProject:       1
```

브라우저 검증:

```text
loaded title: Home · llm_wiki_self
visible stats: 667 nodes / 1020 edges / 55 sources / 7 types
sources page: source evidence table links to per-source pages
source detail: llm_wiki/frontend.py shows 41 nodes, 54 related edges, type mix, node links, and edge table
search smoke: StaticSiteBuilder returned CodeClass and StaticSiteBuilder.write_site results
console: no JavaScript errors on home, sources, source detail, or graph pages
server: TCP *:56821 LISTEN, serving via --host 0.0.0.0
```

## 이것이 보여주는 것

- 공개 설치 경로가 동작합니다.
- `llm_wiki` shell 명령이 동작합니다.
- 저장소가 프로젝트 로컬 `.llm-wiki` 워크스페이스를 연결할 수 있습니다.
- 연구/문서 markdown과 개발 코드 그래프 노드가 공존할 수 있습니다.
- Markdown, Obsidian, frontend, Graphiti, Cognee, SQLite, report, agent-harness 투영이 하나의 그래프 파이프라인에서 생성됩니다.
- 정적 HTML 프론트엔드는 JavaScript 빌드 단계 없이 프로젝트 그래프를 탐색할 수 있습니다.
