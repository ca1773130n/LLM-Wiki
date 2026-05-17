# 빠른 시작

<!-- translations:start -->
<p align="center"><a href="../quickstart.md">English</a> · <a href="quickstart.ko.md">한국어</a> · <a href="quickstart.zh.md">中文</a> · <a href="quickstart.ja.md">日本語</a> · <a href="quickstart.ru.md">Русский</a> · <a href="quickstart.es.md">Español</a> · <a href="quickstart.fr.md">Français</a> · <a href="quickstart.de.md">Deutsch</a></p>
<!-- translations:end -->
이 페이지는 기존 프로젝트 디렉터리에서 탐색 가능한 LLM-Wiki까지 가는 가장 짧은 경로를 보여줍니다.

## 1. 설정 마법사 실행

색인화하려는 프로젝트에서:

```bash
cd /path/to/my-project
llm_wiki project setup
```

마법사는 `README.md`, `docs`, `src`, `lib`, `app`, `packages`, `data` 같은 일반적인 source를 감지한 뒤 `.llm-wiki/config.json`을 씁니다. 또한 기본 Cognee backend를 설정하여 `project ask`가 Cognee를 시도하고 compiled wiki search로 fallback할 수 있게 합니다.

Understand Anything과 Cognee runtime memory를 활성화한 완전 자동 설정:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

수행 내용:

| Flag | Effect |
|---|---|
| `--with-understand-anything` | UA graph projection을 source로 추가합니다. |
| `--install-understand-anything` | UA companion skills를 설치/업데이트합니다. |
| `--understand-anything-platform codex` | Codex를 사용해 LLM-Wiki의 managed UA refresh wrapper를 실행합니다. |
| `--run-cognee` | compile 중 best-effort Cognee runtime cognify를 실행합니다. |
| `--install-cognee` | Cognee가 없으면 현재 Python으로 설치합니다. |

사용자는 UA install path를 알거나 `/understand`를 입력할 필요가 없습니다. UA graph가 없거나 오래되면 `project compile`이 `project refresh-understand-anything`을 실행합니다.

## 2. 그래프와 projection 컴파일

```bash
llm_wiki project compile
```

`project compile`은 durable artifact를 씁니다.

```text
.llm-wiki/
  config.json
  graph.json
  manifest.json
  sqlite.db
  temporal_facts.jsonl
  graphiti_episodes.jsonl
  report.md
  competitive_report.md
  markdown_projection/
  obsidian_vault/
  agent_harness/
  harness_sessions/
  site/
  cognee_bundle/
```

첫 실행 후에는 `--changed-only`를 사용해 변경되지 않은 markdown 파일을 건너뛰면서, 파일 변경이 없을 때 이전 graph를 보존할 수 있습니다. Understand Anything이 활성화되어 있으면 compile은 먼저 `.llm-wiki/external/understand-anything.md`를 refresh/materialize합니다. Cognee runtime이 활성화되어 있으면 `.llm-wiki/cognee_bundle/` 작성 후 best-effort로 Cognee도 업데이트합니다.

## 3. 정적 frontend 빌드 및 제공

```bash
llm_wiki project build-site
llm_wiki project serve --port 8765
```

열기:

```text
http://127.0.0.1:8765/
```

<!-- BEGIN: subagent-r-watch -->
### 저장 시 자동 재빌드

개발 서버를 polling watcher와 함께 사용하면 `data/` 및 `docs/` 아래 편집이 incremental recompile을 트리거합니다.

```bash
# terminal 1
python3 -m http.server 56821 --directory .llm-wiki/site

# terminal 2
llm_wiki project watch
```

`project watch`는 2초마다 polling하고 1초 debounce 후 `compile --changed-only`를 실행합니다. cron 스타일 rebuild에는 `--once`(snapshots vs `.llm-wiki/.watch-cache.json`), custom watch dir 추가에는 `--paths <dir>`, cadence 조정에는 `--interval` / `--debounce`를 사용하세요.
<!-- END: subagent-r-watch -->

보이는 모든 route(home, sources, concepts, entities, papers, repos, topics, syntheses, questions, timeline, graph, AI siblings)에 대한 주석 달린 tour는 [`docs/frontend-redesign.md`](frontend-redesign.ko.md)를 참고하세요.

Frontend는 dependency-light이며 다음을 씁니다.

```text
.llm-wiki/site/index.html
.llm-wiki/site/sessions/index.html
.llm-wiki/site/graph.json
.llm-wiki/site/search-index.json
.llm-wiki/site/llms.txt
```

## 4. 로컬 agent 세션 기록 가져오기

세션 기록 import는 명시적입니다. 일반 compile/build는 이미 정규화된 세션을 읽지만 private Claude Code 또는 Codex transcript store를 자체적으로 스캔하지 않습니다.

```bash
# Preview matching Claude Code/Codex sessions for this project:
llm_wiki project sessions discover

# Normalize and store them under .llm-wiki/harness_sessions/:
llm_wiki project sessions discover --import

# Confirm the imported set:
llm_wiki project sessions list

# Rebuild so sessions/index.html and session detail pages are emitted:
llm_wiki project build-site
```

가져온 세션은 global Sessions section, site search, home Browse cards에 나타납니다. 세션 detail page는 user/assistant turn을 읽기 쉬운 markdown으로 렌더링하고, tool-use block을 앞선 assistant turn 아래 붙이며, `#turn-N` navigation을 위한 왼쪽 turn rail을 제공합니다. privacy notes, import formats, 현재 transcript typography map은 [`docs/session-history.md`](session-history.ko.md)를 참고하세요.

## 5. Wiki lint

```bash
llm_wiki project lint
```

Compiled graph + wiki + site를 순회하면서 orphan papers, stale citations, graph와 wiki/ 간 drift, ghost synthesis inputs 등을 표시합니다. `.llm-wiki/lint-report.md`와 `.llm-wiki/lint-report.json`을 씁니다. 안전한 auto-fix(missing `implemented_in` edges, ghost-input pruning)를 적용하려면 `--fix-trivial`, error일 때만 exit code 실패를 원하면 `--severity error`를 전달하세요.

## 6. Wiki 질의

```bash
llm_wiki project query "What is Gaussian Splatting?"
```

기본은 search-only입니다. `.llm-wiki/site/search-index.json` 위의 BM25와 일치하는 `wiki/<kind>/<slug>.md`에서 가져온 200자 excerpt를 사용합니다. 좁히려면 `--kind papers`(또는 `concepts`, `repos` 등), 넓히려면 `--top-k N`, structured output은 `--json`을 전달하세요. `[node_id]` citation이 있는 합성 답변을 Claude에 요청하려면 `--llm`을 추가하거나 `LLM_WIKI_QUERY_LLM=1`을 설정합니다. `--interactive`는 readline REPL을 열며 blank line 또는 EOF로 종료합니다. `LLM_WIKI_QUERY_DRY_RUN=1`은 API 호출 없이 prompt를 실행해 봅니다.

## 7. Agent harness 파일 export

```bash
llm_wiki project export-agent-harness
```

지원 target:

- Claude Code
- Codex
- Gemini
- Kiro
- Cursor
- OpenCode

부분 예시:

```bash
llm_wiki project export-agent-harness \
  --target claude-code \
  --target cursor \
  --target opencode
```

## 8. Obsidian vault export

```bash
llm_wiki project export-obsidian
```

또는 기존 vault에 쓰기:

```bash
llm_wiki project export-obsidian --vault "$OBSIDIAN_VAULT_PATH"
```

Vault에는 markdown projections, `.obsidian` defaults, graph coloring, `raw/assets/`, Dataview dashboard가 포함됩니다.

## 9. MCP 설정

```bash
llm_wiki project mcp-config --server-name my_project_wiki
```

출력을 `~/.hermes/config.yaml`의 `mcp_servers` 아래 붙여 넣은 뒤 Hermes/gateway를 재시작하세요.

## 10. Graphiti export / sync

Dependency-free episode export:

```bash
llm_wiki project export-graphiti
```

Graphiti 설치 없이 dry-run sync smoke:

```bash
llm_wiki project sync-graphiti --dry-run
```

Live sync에는 `graphiti_core`와 접근 가능한 Neo4j backend가 필요합니다.

```bash
llm_wiki project sync-graphiti \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-password '<password>'
```

## 11. GitHub Pages에 배포

`.llm-wiki/site/`의 compiled site를 프로젝트 git origin의 `gh-pages` branch로 push합니다.

```bash
llm_wiki project deploy --build --enable-pages
```

`--build`는 먼저 `project compile`을 실행해 site를 최신으로 만듭니다. `--enable-pages`는 `gh` CLI를 통해 Pages를 켭니다(idempotent, `gh`가 없으면 hint와 함께 skip). push 없이 stage/commit하려면 `--dry-run`, default override에는 `--branch` / `--remote`, dirty working tree에서 배포 허용에는 `--force`를 사용하세요.

사이트는 `https://<owner>.github.io/<repo>/`에서 접근할 수 있습니다.
