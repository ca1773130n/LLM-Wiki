# 건축학

<!-- translations:start -->
<p align="center"><a href="../architecture.md">English</a> · <a href="architecture.ko.md">한국어</a> · <a href="architecture.zh.md">中文</a> · <a href="architecture.ja.md">日本語</a> · <a href="architecture.ru.md">Русский</a> · <a href="architecture.es.md">Español</a> · <a href="architecture.fr.md">Français</a> · <a href="architecture.de.md">Deutsch</a></p>
<!-- translations:end -->
LLM-Wiki는 소스 자료의 디렉토리를 제어되고 입력된 지식 그래프로 바꾸고 내구성 있는 마크다운 위키 레이어를 통해 해당 그래프를 정적 AI 친화적인 웹 사이트로 프로젝트합니다. 2026년 4월 재설계에서는 Karpathy 3계층 모델을 중심으로 시스템을 재구성했습니다. 원시 증거는 원시 상태로 유지되고, 입력된 그래프는 온톨로지를 관리하며, 마크다운 위키 계층은 그래프와 렌더링된 출력 사이에 위치합니다. 정적 사이트는 이제 스키마로 [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py)의 제어된 온톨로지를 사용하여 그래프를 직접 덤프하는 것이 아니라 위키 레이어의 *렌더러*입니다.

## Karpathy 3층 모델

LLM 친화적인 지식 기반에 대한 Andrej Karpathy의 프레임은 각각 고유한 내구성을 보장하는 세 가지 계층으로 구분됩니다.

| 레이어 | 우려사항 | 레포 위치 | 소유자 |
|---|---|---|---|
| L1 — 원시 소스 | 사용자가 작성하거나 수집한 리터럴 바이트입니다. 추가 전용. | `data/`, `docs/`, `.llm-wiki/config.json`에서 참조되는 프로젝트 트리 | 사용자 |
| L2 — 위키 | YAML 서두가 포함된 입력된 마크다운 페이지(소스, 개념, 엔터티, 논문, 저장소, 주제, 종합, 질문). 멱등성: 각 컴파일을 다시 생성하지만 콘텐츠 해시가 변경될 때만 다시 작성됩니다. | `.llm-wiki/wiki/` | `WikiPageStore`, `WikiLayerProjector`, `SynthesisProjector` |
| L3 — 렌더링됨 | 정적 HTML 사이트, AI 형제 내보내기, 검색 색인, 사이트맵, JSON-LD. 모든 컴파일을 지우고 다시 작성했지만 재실행 시 바이트가 안정적입니다. | `.llm-wiki/site/` | `StaticSiteBuilder` (`llm_wiki/site/`) |

스키마는 세 레이어 모두에 별도의 축으로 위치합니다. `graph.json`의 `ResearchGraph`는 L2 페이지가 연결되는 제어된 온톨로지이며, [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py)의 `ResearchNodeType`/에지 화이트리스트는 어떤 유형이 존재하는지에 대한 정보의 소스입니다.

재설계에서는 L2가 명시적으로 추가되었습니다. 2026년 4월 이전에는 정적 사이트가 `graph.json`에서 바로 투영되었습니다. 위키 레이어는 Obsidian 볼트 내보내기 내부에만 존재했습니다. 이를 분할하면 다음과 같은 정보가 제공됩니다.

- 사람이 편집할 수 있는 단일 표면(Obsidian 또는 마크다운 편집기에서 `.llm-wiki/wiki/` 열기)
- 멱등성 재구축: `project compile`를 다시 실행하면 소스 콘텐츠가 변경되지 않는 한 파일 차이가 전혀 발생하지 않습니다.
- 진화 로그: 합성 페이지는 시간이 지남에 따라 축적되며 프로젝트 자체에 대한 설명을 제공합니다.

## 파이프라인

```
data/, docs/, src/                                    (L1 raw)
        │
        ▼  project compile  (llm_wiki/project.py)
┌───────────────────────────┐
│ ResearchGraphExtractor    │   deterministic + selective Claude
│ + canonicalization        │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│ ResearchGraph (graph.json)│   schema: research_graph.py
└───────────┬───────────────┘
            │
            ├──▶ WikiLayerProjector   (one page per L1/L2 node)
            ├──▶ SynthesisProjector   (pulse, daily, weekly, topic, …)
            │
            ▼
┌───────────────────────────┐
│ .llm-wiki/wiki/  (L2 md)  │   sources/, concepts/, entities/,
│                            │   papers/, repos/, topics/,
│                            │   syntheses/, questions/
└───────────┬───────────────┘
            │
            ▼  StaticSiteBuilder.write_site
┌───────────────────────────┐
│ .llm-wiki/site/  (L3 html)│   index.html, <kind>/index.html,
│                            │   <kind>/<slug>.html,
│                            │   per-page .txt + .json siblings,
│                            │   llms.txt, llms-full.txt,
│                            │   graph.json, graph.jsonld,
│                            │   search-index.json,
│                            │   sitemap.xml, rss.xml,
│                            │   robots.txt, ai-readme.md,
│                            │   manifest.json
└───────────────────────────┘
```

모든 단계는 점진적입니다. 그래프 추출기는 `manifest.json` 콘텐츠 해시를 사용하여 변경되지 않은 소스 파일을 건너뜁니다. `WikiPageStore.write_page`는 본문 해시가 이미 디스크에 있는 것과 일치하면 `False`를 반환하고 쓰기를 건너뜁니다. `StaticSiteBuilder`는 `.llm-wiki/site/`를 지우고 다시 작성하지만 출력은 결정적입니다. 아래 "멱등성 이야기"를 참조하세요.

## 모듈 맵

### 위키 + 합성(L2)

| 모듈 | 책임 |
|---|---|
| [`llm_wiki/wiki_store.py`](../../llm_wiki/wiki_store.py) | `WikiPage` 데이터 클래스, 파일 시스템 I/O용 `WikiPageStore`. Stdlib 전용 YAML 하위 집합 앞부분 파서. 신체-해시 멱등성. |
| [`llm_wiki/wiki_projector.py`](../../llm_wiki/wiki_projector.py) | `WikiLayerProjector`: Wiki 레이어 유형의 각 `ResearchGraph` 노드를 오른쪽 `kind/` 폴더의 마크다운 페이지에 매핑합니다. |
| [`llm_wiki/synthesis.py`](../../llm_wiki/synthesis.py) | `SynthesisProjector`: 펄스, daily_digest, 주간, 주제, 비교, field_overview에 대한 결정적 템플릿입니다. `Synthesis` 노드와 `synthesizes` / `summarizes` 에지를 그래프에 다시 추가합니다. |

### 그래프 + 온톨로지

| 모듈 | 책임 |
|---|---|
| [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) | `ResearchNodeType` 열거형(`SYNTHESIS` 포함), 에지 유형 화이트리스트(`synthesizes`, `summarizes` 포함), 검증. |
| [`llm_wiki/canonicalization.py`](../../llm_wiki/canonicalization.py) | 별칭 정규화 + 거의 중복된 검토 대기열. |
| [`llm_wiki/code_graph.py`](../../llm_wiki/code_graph.py) | 개발 슬라이스를 위한 결정적 Python AST 추출기입니다. |
| [`llm_wiki/llm_extractor.py`](../../llm_wiki/llm_extractor.py) | Claude CLI/OAuth 선택적 추출기. |

### 사이트 렌더러(L3)

| 모듈 | 책임 |
|---|---|
| [`llm_wiki/site/__init__.py`](../../llm_wiki/site/__init__.py) | `StaticSiteBuilder.write_site`: 사이트 지우기 + 재구축, 모든 경로 탐색, 내보내기 + AI 형제 + 매니페스트 내보내기. |
| [`llm_wiki/site/pages.py`](../../llm_wiki/site/pages.py) | 경로당 하나의 렌더러(홈, 인덱스, 세부 정보 페이지, 타임라인, 그래프, 정보). `SiteContext`는 미리 계산된 인덱스를 전달하므로 렌더러가 순수하게 유지됩니다. |
| [`llm_wiki/site/components.py`](../../llm_wiki/site/components.py) | HTML 프리미티브: `breadcrumbs`, `card`, `badge`, `node_table`, `edge_list`, `sparkline_svg`, `heatmap_svg`, `toc`, `page_shell`, `ai_siblings_footer`. |
| [`llm_wiki/site/tokens.py`](../../llm_wiki/site/tokens.py) | 디자인 토큰 — CSS 변수, 밝은 + 어두운 테마, 레이아웃, 타이포그래피, 여기에 스타일이 지정된 모든 구성 요소. |
| [`llm_wiki/site/js.py`](../../llm_wiki/site/js.py) | 클라이언트 JS 번들: 검색 팔레트, 테마 토글, 시그마 + 3D-force 그래프 보기. |
| [`llm_wiki/site/markdown.py`](../../llm_wiki/site/markdown.py) | Stdlib 전용 마크다운 렌더러(링크, 자동 링크, 코드, 강조, 제목). 외부 종속성이 없습니다. |
| [`llm_wiki/site/relevance.py`](../../llm_wiki/site/relevance.py) | 모든 `Related` 섹션에서 사용되는 4개 신호 관련성 점수(직접 링크, 소스 중복, Adamic-Adar, 유형 선호도). |
| [`llm_wiki/site/search.py`](../../llm_wiki/site/search.py) | `search-index.json` 빌더. Wiki 레이어 종류에만 해당됩니다. |
| [`llm_wiki/site/sessions.py`](../../llm_wiki/site/sessions.py) | 가져온 하네스 기록을 위한 세션 색인/세부 렌더러: 프로젝트 메모리 요약 섹션, 대화 전환 레일, 마크다운 기록 렌더링 및 축소된 도구 사용 블록. |
| [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) | `llms.txt`, `llms-full.txt`, `graph.jsonld`, `sitemap.xml`, `rss.xml`, `robots.txt`, `ai-readme.md`, 페이지당 `.txt`/`.json` 형제. |

### 파이프라인 오케스트레이션

| 모듈 | 책임 |
|---|---|
| [`llm_wiki/project.py`](../../llm_wiki/project.py) | `ProjectWiki.compile`: 추출 → 그래프 → 위키 레이어 → 사이트를 구동합니다. `ProjectPaths`(`config`, `graph`, `manifest`, `wiki`, `site` 등)를 소유합니다. |
| [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | `compile`, `build-site`, `serve`, `watch`, `deploy`를 포함한 모든 `llm_wiki project …` 하위 명령. |
| [`llm_wiki/deploy.py`](../../llm_wiki/deploy.py) | `project deploy`: 작업 트리를 통해 `.llm-wiki/site/`를 `gh-pages` 분기에 푸시하고 선택적으로 `gh`를 통해 페이지를 활성화합니다. |

### 외부 어댑터(이번 라운드에서는 변경되지 않음)

| 모듈 | 책임 |
|---|---|
| [`llm_wiki/obsidian_adapter.py`](../../llm_wiki/obsidian_adapter.py) | Obsidian 볼트 투영(그래프 색상 지정, Dataview 대시보드, 원시 자산). |
| [`llm_wiki/agent_harness.py`](../../llm_wiki/agent_harness.py) | Claude 코드 / Codex / Gemini / Kiro / Cursor / OpenCode 하네스 수출. |
| [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) | 인바운드 Claude 코드/Codex 세션 검색, 정규화, `.llm-wiki/harness_sessions/` 하의 저장 및 수정된 마크다운 요약. |
| [`llm_wiki/graphiti_adapter.py`](../../llm_wiki/graphiti_adapter.py) | 임시 사실 JSONL + 선택적 라이브 Graphiti 동기화. |
| [`llm_wiki/cognee_adapter.py`](../../llm_wiki/cognee_adapter.py) | Cognee 노드/에지 JSONL 번들 및 직접 추가/인식 경로. |
| [`llm_wiki/mcp_server.py`](../../llm_wiki/mcp_server.py) | `schema`, `graph_summary`, `search_nodes`, `node_context`, `search_facts`, `timeline`를 노출하는 MCP stdio 서버입니다. |

## 프로젝트 작업공간 레이아웃

```text
.llm-wiki/
  config.json                 project name, source kind, source list
  graph.json                  validated ResearchGraph (incl. Synthesis nodes)
  manifest.json               per-source content hashes (input dedup)
  sqlite.db                   SQLite graph store
  temporal_facts.jsonl        Graphiti-style temporal projection
  graphiti_episodes.jsonl     dependency-free Graphiti episode export
  report.md                   graph quality / summary
  competitive_report.md       comparison vs. MegaMem / Graphiti / others
  markdown_projection/        flat human-readable markdown
  obsidian_vault/             Obsidian projection w/ .obsidian/, raw/assets/
  agent_harness/              Claude Code / Codex / etc. harness files
  harness_sessions/           imported local Claude Code/Codex sessions
  cognee_bundle/              Cognee nodes/edges/manifest JSONL
  wiki/                       L2 markdown wiki — see below
  site/                       L3 static site — see below
```

### `.llm-wiki/wiki/` (L2)

```text
wiki/
  sources/<slug>.md           raw documents from data/ + docs/, with frontmatter
  concepts/<slug>.md          Concept / TechnicalTerm / Algorithm / etc.
  entities/<slug>.md          Model / Dataset / Benchmark / Metric / Org / Person
  papers/<slug>.md            Paper hub
  repos/<slug>.md             Repository / Project / CodeProject
  topics/<slug>.md            ResearchField / ResearchTopic / ApproachFamily / Trend
  syntheses/<slug>.md         pulse, daily_digest, weekly, topic, comparison, field_overview
  questions/<slug>.md         OpenQuestion
```

각 파일은 직접 편집할 수 있습니다. 다음 컴파일에서는 본문 해시가 프로젝터가 작성하는 것과 다른 한 사용자 편집을 존중합니다. (본문만 편집하면 승리하며, 머리말 편집은 머리말이 재생성되기 때문에 다음 컴파일에서 패합니다.) Obsidian 사용자는 `.llm-wiki/wiki/`를 직접 열 수 있습니다. 기존 `obsidian_vault/` 어댑터는 대체품이 아닌 별도의 프로젝션입니다.

### `.llm-wiki/site/` (L3)

```text
site/
  index.html                  home + project pulse
  about.html                  schema, build info
  assets/{style.css,app.js}   single CSS bundle + single JS bundle
  sources/index.html
  sources/<slug>.html
  sources/<slug>.txt          AI sibling — plain text
  sources/<slug>.json         AI sibling — structured record
  concepts/…  entities/…  papers/…  repos/…  topics/…  syntheses/…  questions/…
  sessions/index.html          imported harness-session index
  sessions/<project>/<id>.html session detail: summary, metadata, turn rail, markdown turns, collapsed tools
  timeline/index.html
  graph/index.html            interactive 2D + 3D force layout
  graph.json                  full graph payload (incl. code nodes, for tooling)
  graph.jsonld                schema.org Dataset, wiki-layer nodes only
  search-index.json           palette + page search; wiki-layer kinds only
  llms.txt                    llmstxt.org — short index
  llms-full.txt               llmstxt.org — every page body, capped 5MB
  sitemap.xml                 every emitted route
  rss.xml                     last 30 syntheses
  robots.txt                  permissive (crawl + index)
  ai-readme.md                machine-readable site map
  manifest.json               sha256 + size for every emitted file
```

## 의도적으로 제외된 내용

재설계에서는 코드 클래스 및 코드 기능 노드가 `graph.json`에 유지되지만(MCP, Cognee 및 Graphiti 소비자는 여전히 이를 볼 수 있음) HTML 페이지를 얻지 못하고 `search-index.json`에 나타나지 않으며 탐색에 나타나지 않습니다. 이것이 바로 사용자 대면 계약입니다. 위키는 기능 브라우저가 아닌 문서 우선 지식 기반입니다.

구체적으로, `StaticSiteBuilder`는 유형이 L2 위키 종류 맵(`llm_wiki/wiki_projector.py::_KIND_FOR_TYPE`)에 없는 모든 노드를 건너뜁니다.

- L2 + L3에서 제외: `CodeClass`, `CodeFunction`, `CodeModule`, `Dependency`, `EvidenceSpan`, `SourceFile`, 모든 `Claim` 변형(`Claim`, `ContributionClaim`, `PerformanceClaim`, `ComparisonClaim`, `LimitationClaim`, `CausalClaim`).
- 여전히 나타나는 표면: 글머리 기호, 배지, 이웃 수 또는 관련 위키 페이지의 인라인 및 다운스트림 도구용 `graph.json`에서 발췌한 증거.

코드 수준 검색이 필요한 경우 소스 트리에서 LSP/호출 그래프 도구를 직접 가리키십시오. 이는 "이 프로젝트가 알고 있는 내용에 대한 위키"와는 다른 문제입니다.

## 멱등성 이야기

재설계는 **변경되지 않은 입력에 대해 두 개의 연속 `project compile` 실행에서 바이트 동일한 출력**을 목표로 합니다. 조각들:

1. **소스 추출**은 `manifest.json` 콘텐츠 해시를 사용합니다. 변경되지 않은 파일은 건너뛰므로 그래프가 안정적으로 유지됩니다.
2. **Wiki 레이어 쓰기**는 본문 수준에서 멱등성을 갖습니다. `WikiPageStore.write_page`는 기존 파일을 읽고, 앞부분을 제거하고, 본문을 sha256s로 처리하고, 새 본문이 동일하게 해시되면 단락합니다. 새 앞부분의 `generated_at` 타임스탬프가 다른 경우에도 마찬가지입니다. 이것은 재구축 시 git diff를 단단히 유지하는 핵심 트릭입니다.
3. **합성 출력**은 머리말에 `content_hash: sha256-…`를 포함합니다. 본문 해시는 `generated_at` 없이 계산되므로 동일한 그래프에서 반복 컴파일하면 동일한 해시가 생성되고 `Synthesis` 노드는 그래프 메타데이터에 동일한 `content_hash`를 전달합니다.
4. **사이트 렌더링**은 `write_site` 시작 부분에서 `site/`를 지운 다음 결정론적으로 씁니다. 경로가 정렬되고 사전이 `sort_keys=True`로 덤프되고 `manifest.json`가 `sorted(rglob("*"))`를 통해 이동됩니다. 두 번 실행하면 매니페스트를 포함하여 바이트와 동일한 파일이 생성됩니다.

이는 `tests/test_site_pages.py` 및 `tests/test_project_e2e_redesign.py`의 종단 간 연기로 확인됩니다(두 번 컴파일, 사이트 비교, 파일 델타 0 예상).

## 스케일링 노트

- **그래프 보기 노드 캡.** [`MAX_GRAPH_NODES = 1500`](../../llm_wiki/site/pages.py)는 대화형 강제 레이아웃에 대한 페이지 내장 페이로드를 제한합니다. ~1500개 노드를 초과하면 중급 하드웨어에서 브라우저 측 시뮬레이션이 느려지므로 개수가 한도를 초과하면 페이지에서 가장 낮은 등급의 Wiki 레이어 노드를 먼저 삭제합니다. 내보낸 `graph.json`는 영향을 받지 않습니다. 항상 전체 그래프를 포함합니다. 코드 노드는 한도가 적용되기 전에 필터링됩니다.
- **`llms-full.txt` 캡.** [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py)에는 5MB 안전 캡이 적용됩니다. 캡에 도달하면 파일은 `[TRUNCATED — see graph.jsonld for the full set]` 마커로 끝납니다. JSON-LD 소비자가 전체 세트를 기대하기 때문에 `graph.jsonld`에는 제한이 없습니다.
- **색인 검색.** Wiki 레이어 종류에만 해당됩니다. 코드 그래프 노드는 `search-index.json`를 입력하지 않습니다. dogfood 코퍼스의 재설계 목표는 500KB 미만이며 현재는 그 수준에 훨씬 못 미치고 있습니다.
- **페이지당 바이트 예산(경험 법칙).** 각 세부 정보 페이지 < 60KB gz HTML, 공유 CSS < 30KB, 공유 JS < 25KB, 그래프 페이지에만 시그마 공급업체(~60KB). 그래프 보기는 한 번 로드된 3D-force-graph + Three.js를 사용합니다. 다른 모든 페이지는 바닐라 상태를 유지합니다.
- **dogfood의 컴파일 시간.** 최근 개발 컴퓨터에서는 최대 300개의 마크다운 파일이 5초 이내에 추출됩니다. 사이트 렌더링은 ~2초를 더 추가합니다. 위키 레이어의 멱등성은 후속 컴파일이 변경된 경로만 건드린다는 것을 의미합니다.

## 프런트엔드 상호 작용 표면

- **검색 팔레트** — `cmd+k` / `ctrl+k` / `/`. 위키 종류로 범위가 지정된 `search-index.json`에 대한 퍼지 일치입니다. 최근 페이지는 `localStorage`에 유지되었습니다.
- **테마 토글** — 오른쪽 상단 버튼; `data-theme="dark"`는 `localStorage`에 저장되며 플래시를 방지하기 위해 페인트 전에 적용됩니다.
- **고정된 오른쪽 목차** — 데스크탑에만 해당; 모바일에서는 `<details>` 서랍으로 축소됩니다. 페이지 본문의 `<h2>` / `<h3>`에서 생성됩니다.
- **활동 히트맵** — 월 + 평일 라벨이 포함된 26주 SVG입니다. 셀은 해당 날짜의 `digest.md` 소스 페이지가 있는 경우 해당 페이지로 연결됩니다. (일별 타임라인 세부정보 페이지 — `/timeline/<YYYY-MM-DD>.html` —는 명시적인 후속 작업이며 `render_timeline`의 인라인 공지에 플래그가 지정되어 있습니다. ⚠ 진행 중입니다.)
- **그래프 보기** — `/graph/`. 호버 도구 설명, 가장자리 레이블, 커서 고정 확대/축소 및 2D 대체 보기가 포함된 3D 힘 레이아웃(3d-force-graph + Three.js). 노드 색상은 `ResearchNodeType`에서 나옵니다.
- **모바일 셸** — 서랍 레일, 하단 탐색, 유체 유형, 터치 안전 히트 대상(≥ 44px).

## 테스트 전략

- **유닛** — `tests/test_wiki_store.py`, `tests/test_synthesis.py`, `tests/test_site_components.py`, `tests/test_site_pages.py`, `tests/test_site_exports.py`, `tests/test_relevance.py`.
- **멱등성** — `tests/test_project_e2e_redesign.py`는 두 번 컴파일하고 `wiki/` 및 `site/`에서 제로 차이를 주장합니다.
- **링크 무결성** — `tests/test_frontend.py`는 href에 대해 방출된 모든 HTML을 구문 분석하고 모든 내부 링크가 생성된 파일로 확인된다고 주장합니다. `nodes/codeclass-*.html`는 생산되지 않습니다.
- **AI 형제** — 모든 `path/foo.html`에 대해 테스트 스위트는 `path/foo.txt` 및 `path/foo.json`가 존재한다고 주장합니다. JSON은 `{title, kind, body, links}`를 구문 분석하고 포함합니다.
- **극작가 없음** — `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`의 바닐라 pytest.

## 관련 문서

- [빠른 시작](quickstart.ko.md) — `project init`에서 탐색 가능한 사이트까지의 최소 경로입니다.
- [프런트엔드 재설계 연습](frontend-redesign.ko.md) — 주석이 달린 모든 경로 둘러보기.
- [기능 맵](feature-map.ko.md) — 무엇이 배송되고, 무엇이 진행 중인지, 파일 포인터가 포함되어 있습니다.
- [Self-dogfood 데모](self-dogfood.ko.md) — 자체 저장소에 대해 LLM-Wiki를 실행합니다.
