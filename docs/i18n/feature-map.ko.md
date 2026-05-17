# 기능 맵

<!-- translations:start -->
<p align="center"><a href="../feature-map.md">English</a> · <a href="feature-map.ko.md">한국어</a> · <a href="feature-map.zh.md">中文</a> · <a href="feature-map.ja.md">日本語</a> · <a href="feature-map.ru.md">Русский</a> · <a href="feature-map.es.md">Español</a> · <a href="feature-map.fr.md">Français</a> · <a href="feature-map.de.md">Deutsch</a></p>
<!-- translations:end -->
이 문서는 LLM-Wiki에 현재 구현된 기능을 상태, 소스 파일, 문서화 위치와 함께 요약합니다.

상태 범례: ✅ 출시됨 · ⚠ 진행 중 / 부분 구현.

## 프런트엔드 재설계 — 2026년 4월

기존 그래프 덤프를 문서 우선의 계층형 위키가 대체합니다. 경로별 둘러보기는 [`docs/frontend-redesign.md`](frontend-redesign.ko.md)를, 3계층 모델은 [`docs/architecture.md`](architecture.ko.md)를 참고하세요.

### 위키 계층 (L2 markdown)

| 기능 | 상태 | 소스 | 문서 앵커 |
|---|---|---|---|
| `WikiPageStore` (멱등 body-hash 쓰기, frontmatter 파서) | ✅ | [`llm_wiki/wiki_store.py`](../../llm_wiki/wiki_store.py) | [architecture.md § 모듈 맵](architecture.ko.md#wiki--synthesis-l2) |
| `WikiLayerProjector` — 위키 계층 노드마다 md 페이지 1개 | ✅ | [`llm_wiki/wiki_projector.py`](../../llm_wiki/wiki_projector.py) | [architecture.md § 파이프라인](architecture.ko.md#pipeline) |
| `sources/` 페이지 | ✅ | `wiki_projector.py` | [frontend-redesign.md § Sources](frontend-redesign.ko.md#sources) |
| `concepts/` 페이지 | ✅ | `wiki_projector.py` | [frontend-redesign.md § Concepts](frontend-redesign.ko.md#concepts) |
| `entities/` 페이지 | ✅ | `wiki_projector.py` | [frontend-redesign.md § Entities](frontend-redesign.ko.md#entities) |
| `papers/` 페이지 | ✅ | `wiki_projector.py` | [frontend-redesign.md § Papers](frontend-redesign.ko.md#papers) |
| `repos/` 페이지 | ✅ | `wiki_projector.py` | [frontend-redesign.md § Repos](frontend-redesign.ko.md#repos) |
| `topics/` 페이지 | ✅ | `wiki_projector.py` | [frontend-redesign.md § Topics](frontend-redesign.ko.md#topics) |
| `questions/` 페이지 (열린 질문) | ✅ | `wiki_projector.py` | [frontend-redesign.md § Questions](frontend-redesign.ko.md#questions) |
| `syntheses/` 페이지 | ✅ | [`llm_wiki/synthesis.py`](../../llm_wiki/synthesis.py) | [frontend-redesign.md § Syntheses](frontend-redesign.ko.md#syntheses) |

### 합성 종류 (L2 → 파생)

`SynthesisProjector`는 7개의 결정적 템플릿을 생성하고 `Synthesis` 노드와 `synthesizes` / `summarizes` 엣지를 그래프에 다시 추가합니다.

| 종류 | 상태 | 소스 | 비고 |
|---|---|---|---|
| `pulse` (전역 1개, `/` 구동) | ✅ | `synthesis.py` | 컴파일할 때마다 재생성됩니다. |
| `daily_digest` | ✅ | `synthesis.py` | `data/research/daily/<date>/`마다 1개. |
| `weekly` | ✅ | `synthesis.py` | `data/research/weekly/<iso-week>/`마다 1개. |
| `topic` | ✅ | `synthesis.py` | 논문 3편 이상인 `ResearchTopic` / `ApproachFamily` 클러스터마다 1개. |
| `comparison` | ✅ | `synthesis.py` | 같은 작업에서 경쟁하는 `ApproachFamily` 쌍마다 1개. |
| `field_overview` | ✅ | `synthesis.py` | `ResearchField`마다 1개. |
| LLM으로 업그레이드된 요약 (환경 플래그) | ⚠ | 훅만 있음 | 휴리스틱 기준선은 제공됨; `LLM_WIKI_SYNTHESIS_LLM=1` 훅은 스텁으로 남겨둠. |

### 정적 사이트 경로

| 경로 | 상태 | 소스 | 비고 |
|---|---|---|---|
| `/` (홈, 히어로 pulse) | ✅ | [`llm_wiki/site/pages.py`](../../llm_wiki/site/pages.py) `render_home` | 통계 행 + 큐레이션된 진입점 + 최근 활동. |
| `/sources/`, `/sources/<slug>.html` | ✅ | `pages.py::render_sources_index`, `render_source_detail` | |
| `/concepts/`, `/concepts/<slug>.html` | ✅ | `pages.py::render_concepts_index`, `render_concept_detail` | |
| `/entities/`, `/entities/<slug>.html` | ✅ | `pages.py::render_entities_index`, `render_entity_detail` | |
| `/papers/`, `/papers/<slug>.html` | ✅ | `pages.py::render_papers_index`, `render_paper_detail` | |
| `/repos/`, `/repos/<slug>.html` | ✅ | `pages.py::render_repos_index`, `render_repo_detail` | |
| `/topics/`, `/topics/<slug>.html` | ✅ | `pages.py::render_topics_index`, `render_topic_detail` | |
| `/syntheses/`, `/syntheses/<slug>.html` | ✅ | `pages.py::render_syntheses_index`, `render_synthesis_detail` | |
| `/questions/`, `/questions/<slug>.html` | ✅ | `pages.py::render_questions_index`, `render_question_detail` | |
| `/timeline/` | ✅ | `pages.py::render_timeline` | 히트맵 + 날짜 목록 + synthesis 레일. |
| `/timeline/<YYYY-MM-DD>.html` (일별 상세) | ⚠ | 아직 없음 | 임시로 히트맵 셀은 해당 날짜의 `digest.md` 소스 페이지로 연결됩니다. Subagent P가 `StaticSiteBuilder`를 통해 일별 상세 페이지를 연결하고 있습니다. |
| `/graph/` (대화형 2D + 3D) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, 호버 툴팁, 엣지 라벨, 커서 기준 줌. |
| `/about.html` | ✅ | `pages.py::render_about` | 스키마, 빌드 정보. |

### AI 친화적 내보내기

| 산출물 | 상태 | 소스 | 목적 |
|---|---|---|---|
| 페이지별 `<page>.txt` 형제 파일 | ✅ | [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) `write_siblings` | 한 페이지의 일반 텍스트 보기(내비게이션, 스타일 없음). |
| 페이지별 `<page>.json` 형제 파일 | ✅ | `exports.py::write_siblings` | `{title, kind, body, body_text, links, source_path, frontmatter}`. |
| `llms.txt` | ✅ | `exports.py::render_llms_txt` | llmstxt.org 짧은 색인. |
| `llms-full.txt` | ✅ | `exports.py::render_llms_full_txt` | 모든 페이지 본문, 5 MB로 제한. |
| `graph.jsonld` | ✅ | `exports.py::render_graph_jsonld` | schema.org `Dataset`, 위키 계층 노드만. |
| `graph.json` | ✅ | `__init__.py::write_site` | 전체 그래프 페이로드(도구용 코드 노드 포함). |
| `search-index.json` | ✅ | [`llm_wiki/site/search.py`](../../llm_wiki/site/search.py) | 팔레트 + 페이지 검색; 위키 계층 종류만. |
| `sitemap.xml` | ✅ | `exports.py::render_sitemap_xml` | 생성된 모든 경로, `lastmod`는 frontmatter에서 가져옴. |
| `rss.xml` | ✅ | `exports.py::render_rss_xml` | 최근 30개 syntheses. |
| `robots.txt` | ✅ | `exports.py::render_robots_txt` | 허용적 — 크롤링 + 색인. |
| `ai-readme.md` | ✅ | `exports.py::render_ai_readme` | 기계 판독 가능 사이트 맵. |
| `manifest.json` | ✅ | `__init__.py::_manifest` | 생성된 모든 파일의 sha256 + 크기(멱등성 하니스). |

### 시각 디자인 + UX

| 기능 | 상태 | 소스 | 비고 |
|---|---|---|---|
| 디자인 토큰(라이트 + 다크 테마, 테라코타 강조색) | ✅ | [`llm_wiki/site/tokens.py`](../../llm_wiki/site/tokens.py) | `assets/style.css`의 단일 CSS 번들. |
| 테마 토글(지속 저장, 깜빡임 없음) | ✅ | [`llm_wiki/site/js.py`](../../llm_wiki/site/js.py) | `localStorage`의 `data-theme="dark"`, 페인트 전에 적용. |
| 검색 팔레트(`cmd+k` / `ctrl+k` / `/`) | ✅ | `js.py` | `search-index.json`에 대한 퍼지 매칭; 최근 페이지 목록. |
| 고정 오른쪽 TOC | ✅ | `pages.py` + `tokens.py` | 데스크톱 전용; 모바일은 `<details>` 기반 드로어. |
| 월 + 요일 라벨이 있는 활동 히트맵 | ✅ | `components.py::heatmap_svg` | 26주 SVG, 셀은 해당 날짜의 `digest.md`로 연결. |
| 스파크라인(개념/엔티티별) | ✅ | `components.py::sparkline_svg` | 주간 언급 횟수, 최근 12주. |
| 모바일 셸(드로어 레일, 하단 내비게이션, 유동형 글자 크기) | ✅ | `tokens.py` + `pages.py` | 터치 대상 ≥ 44 px. |
| 페이지 전환(120 ms 불투명도, prefers-reduced-motion) | ✅ | `tokens.py` | |
| 3D + 2D 그래프 보기(호버, 엣지 라벨, 커서 기준 줌) | ✅ | `pages.py::render_graph_view` + `js.py` | 3d-force-graph + Three.js, CDN 스냅샷으로 벤더링. |
| 페이지별 AI 형제 파일 푸터 | ✅ | `components.py::ai_siblings_footer` | 현재 페이지의 `.txt` 및 `.json`으로 가는 인라인 링크. |
| 하니스 세션 기록 페이지 | ✅ | [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) + [`llm_wiki/site/sessions.py`](../../llm_wiki/site/sessions.py) | 명시적 Claude Code/Codex 가져오기; markdown 턴, 왼쪽 턴 레일, 접힌 도구 사용, 검색 항목을 갖춘 `/sessions/` 색인 및 상세 페이지. |

### 파이프라인 + CLI

| 기능 | 상태 | 소스 | 비고 |
|---|---|---|---|
| `project compile`은 synthesis + wiki + site를 순서대로 호출 | ✅ | [`llm_wiki/project.py`](../../llm_wiki/project.py) | 재설계 계획의 3단계. |
| `project build-site` 독립 실행 | ✅ | `project.py` + [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | `wiki/` + `graph.json`을 읽고 `site/`를 작성. |
| `project serve` 로컬 HTTP | ✅ | `cli.py` | 순수 stdlib 서버. |
| `project deploy` → GitHub Pages | ✅ | [`llm_wiki/deploy.py`](../../llm_wiki/deploy.py) | `gh-pages`로 worktree push; `gh` CLI를 통한 선택적 `--enable-pages`. `--build`, `--dry-run`, `--branch`, `--remote`, `--force`. |
| `project sessions discover/import/list` | ✅ | [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) + `cli.py` | Claude Code/Codex용 인바운드 세션 기록; 탐색은 명시적이며 프로젝트 작업 디렉터리로 범위가 제한됨. |
| `project watch` 변경 시 재빌드 | ⚠ | [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | Subagent R이 폴링 watcher를 마무리 중 — `--interval`, `--debounce`, `--once`, `--paths`, `--quiet` 인자 표면은 준비됨; 재빌드 루프 본문은 이번 라운드에 반영 중. |

## 기존 기능 (변경 없이 유지)

### CLI 및 설치

- ✅ `pyproject.toml`을 통한 설치 가능한 Python 패키지.
- ✅ 콘솔 명령: `llm_wiki`, `llm-wiki`, `llm_wiki_mcp`.
- ✅ `curl | bash` 설치용 `scripts/install.sh`.
- ✅ 빠른 로컬 개발을 위해 기본적으로 editable 설치.

### 추출

- ✅ 제어된 노드/엣지 어휘를 사용하는 결정적 연구 노트 추출기.
- ✅ API 키 없이 더 높은 품질의 구조화 추출을 위한 Claude CLI/OAuth 추출기.
- ✅ glob 및 예산 한도에 따른 선택적 Claude 라우팅.
- ✅ Python 프로젝트용 결정적 개발 코드 추출기.
- ✅ 콘텐츠 해싱 및 `--changed-only` 지원이 있는 배치 수집.
- ✅ 잘못된 UTF-8에 관대한 소스 읽기.

### 그래프 거버넌스

- ✅ 제어된 `ResearchNodeType` 목록 — 이제 `SYNTHESIS` 포함.
- ✅ 제어된 엣지 타입 허용 목록 — 이제 `synthesizes`, `summarizes` 포함.
- ✅ 스키마 드리프트를 거부하는 검증.
- ✅ 별칭 정규화.
- ✅ 모호한 준중복 노드를 위한 리뷰 큐.
- ✅ 리뷰 결정 템플릿 및 병합/별도 유지 워크플로.
- ✅ 파일별 그래프에서 코퍼스 추세 요약.

### 영속성 및 보고서

- ✅ Graph JSON 내보내기.
- ✅ SQLite 그래프 저장소.
- ✅ 선택적 Kuzu 그래프 저장소.
- ✅ 개수, 증거 범위, 고아 노드, 날짜 버킷, 별칭이 많은 노드가 포함된 그래프 보고서.
- ✅ MegaMem, Graphiti/Zep, MCP graph servers, agentic RAG에서 흡수한 아이디어를 설명하는 경쟁 보고서.

### 프로젝트 로컬 워크플로

- ✅ `llm_wiki project init`
- ✅ `llm_wiki project ingest`
- ✅ `llm_wiki project compile`
- ✅ `llm_wiki project mcp-config`
- ✅ `llm_wiki project build-site`
- ✅ `llm_wiki project serve`
- ✅ `llm_wiki project deploy` (신규 — GitHub Pages)
- ✅ `llm_wiki project sessions discover/import/list` (명시적 로컬 에이전트 기록 가져오기)
- ⚠ `llm_wiki project watch` (진행 중)
- ✅ `llm_wiki project export-agent-harness`
- ✅ `llm_wiki project export-obsidian`
- ✅ `llm_wiki project export-graphiti`
- ✅ `llm_wiki project sync-graphiti`

### Obsidian

- ✅ 바로 열 수 있는 vault 내보내기.
- ✅ `.obsidian/app.json` 및 그래프 설정.
- ✅ Markdown 투영.
- ✅ `raw/assets/` 구조.
- ✅ Dataview 쿼리가 있는 `_meta/dashboard.md`.

### 에이전트 하니스

생성되는 대상 파일:

- ✅ Claude Code: `CLAUDE.md`, `.claude/settings.json`
- ✅ Codex: `AGENTS.md`, `mcp.toml`
- ✅ Gemini: `GEMINI.md`, `.gemini/settings.json`
- ✅ Kiro: steering 및 MCP 설정
- ✅ Cursor: 프로젝트 규칙 및 MCP 구성
- ✅ OpenCode: `AGENTS.md`, `opencode.json`

### Graphiti / 시간적 사실

- ✅ provenance, currentness, confidence, invalidation 필드가 포함된 시간적 사실 투영.
- ✅ 의존성 없는 Graphiti episode JSONL 내보내기.
- ✅ Graphiti가 설치되지 않은 상태의 `sync-graphiti --dry-run` 스모크.
- ✅ `graphiti_core` 및 Neo4j를 사용한 선택적 라이브 동기화.

### Cognee

- ✅ Cognee JSONL 번들(`nodes.jsonl`, `edges.jsonl`, `manifest.json`).
- ✅ 선택적 add-only 직접 가져오기.
- ✅ 선택적 Codex CLI/OAuth 기반 Cognee cognify 어댑터.
- ✅ API 키 없는 스모크/품질 워크플로를 위한 결정적 및 Ollama 임베딩 어댑터 경로.

### MCP 서버

- ✅ stdio JSON-RPC 기반 `llm_wiki_mcp` / `python3 -m llm_wiki.mcp_server`.
- ✅ 도구: `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline`.
- ✅ 다중 프로젝트 레지스트리.

## 테스트

현재 테스트 스위트의 범위:

- ✅ 온톨로지 가드레일(새 `Synthesis` 노드 + `synthesizes` / `summarizes` 엣지 포함);
- ✅ 결정적 추출;
- ✅ Claude CLI 래퍼 파싱/검증;
- ✅ 선택적 Claude 라우팅;
- ✅ 정규화/리뷰 워크플로;
- ✅ 배치 수집;
- ✅ 보고서;
- ✅ SQLite/Kuzu 영속성;
- ✅ Cognee 번들/가져오기 패치;
- ✅ Graphiti 내보내기/동기화 dry-run;
- ✅ 프로젝트 CLI 워크플로;
- ✅ 에이전트 하니스 내보내기;
- ✅ Obsidian 내보내기;
- ✅ 프런트엔드 생성 + 링크 무결성(`nodes/codeclass-*.html` 없음);
- ✅ 위키 저장소 멱등성;
- ✅ synthesis projector golden + 멱등성;
- ✅ 사이트 컴포넌트, 페이지, 내보내기, 관련성;
- ✅ AI 형제 파일 형태(페이지별 `.txt` + `.json`);
- ✅ end-to-end 두 번 컴파일 멱등성;
- ✅ 패키지 설치 및 설치 프로그램 계약.
