# MCP — Tesserae를 Claude Code, Codex, Cursor에 연결하기

<!-- translations:start -->
<p align="center"><a href="../../integrations/mcp.md">English</a> · <a href="mcp.zh.md">中文</a> · <a href="mcp.ja.md">日本語</a> · <a href="mcp.ru.md">Русский</a> · <a href="mcp.es.md">Español</a> · <a href="mcp.fr.md">Français</a> · <a href="mcp.de.md">Deutsch</a></p>
<!-- translations:end -->

Tesserae는 컴파일된 타입 그래프를 MCP를 지원하는 모든 클라이언트(Claude Code, Codex CLI, Cursor, Claude Desktop 등)에 노출하는 [Model Context Protocol](https://modelcontextprotocol.io) stdio 서버를 함께 제공합니다. 이 서버는 세 가지 MCP 표면(**tools**, **resources**, **prompts**)을 모두 광고하므로, 클라이언트는 필요에 따라 그래프를 쿼리할 수도 있고 정형 URI로부터 저렴하게 컨텍스트를 시드할 수도 있습니다.

## 사전 요구사항

서버는 `.tesserae/graph.json`에서 읽어오므로, 한 번의 컴파일이 필요합니다:

```bash
cd /path/to/your-project
tesserae project setup    # interactive; or --yes for non-interactive
tesserae project compile  # deterministic, no LLM calls, no API keys
```

소스가 변경될 때마다 다시 컴파일하세요. 서버는 재시작 없이 다음 tool 호출에서 새 그래프를 자동으로 인식합니다.

## 1) 클라이언트 설정 생성

```bash
tesserae project mcp-config
```

대략 다음과 같은 JSON 스니펫을 출력합니다:

```json
{
  "mcpServers": {
    "tesserae": {
      "command": "python3",
      "args": [
        "-m", "tesserae.mcp_server",
        "--graph", "/path/to/your-project/.tesserae/graph.json"
      ]
    }
  }
}
```

정확한 경로는 현재 프로젝트에 맞춰 채워집니다. 서버 항목 이름을 `tesserae`가 아닌 다른 이름으로 지정하고 싶다면 `--name <alias>`를 전달하세요.

## 2) MCP 클라이언트에 붙여넣기

| 클라이언트 | 설정 위치 |
|---|---|
| Claude Code | `~/.claude/mcp-servers.json` (or `~/.config/claude-code/mcp-servers.json`) |
| Claude Desktop | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Codex CLI | `~/.config/codex/mcp-servers.json` |
| Cursor | Settings → MCP Servers → paste JSON |
| Hermes | `~/.hermes/config.toml` (use the TOML-equivalent block printed by `mcp-config --format hermes`) |

편집 후 클라이언트를 재시작하세요. 다음 세션에서 연결되어 Tesserae 표면이 인식됩니다.

## 3) 클라이언트가 보는 것

### Tools — 모델이 호출하는 도구

| Tool | 용도 |
|---|---|
| `schema` | 통제된 node, edge, wiki-kind 어휘 |
| `graph_summary` | 활성 프로젝트의 노드 및 엣지 개수와 타입 분포 |
| `search_nodes` | 쿼리, 타입, kind로 그래프 노드를 필터링하여 점수 기반 상위 N개 반환 |
| `node_context` | 노드 + 인접 엣지 + 이웃 노드 |
| `search_facts` | 그래프에서 투영된 시간적 사실(Graphiti 스타일) |
| `timeline` | 종단적 관점을 위해 `valid_from` 기준으로 정렬된 사실 |
| `wiki_page` | 노드에 대해 컴파일된 markdown 페이지 본문 |
| `raw_source` | 원본 소스 markdown (16 KB로 제한) |
| `lint_report` | 가장 최근의 컴파일 시점 lint 결과 |
| `ask` | 구성된 메모리 백엔드(raganything, cognee, 또는 컴파일된 위키)를 통한 자연어 Q&A |
| `list_projects` / `register_project` / `activate_project` / `unregister_project` | 다중 프로젝트 레지스트리 제어 |

### Resources — 모델 컨텍스트에 자동 로드

클라이언트가 tool 턴을 소비하지 않고도 리소스 선택기를 통해 가져올 수 있는 URI:

- `tesserae://graph/schema` — `schema` tool과 동일한 페이로드를 정적 컨텍스트로 제공
- `tesserae://graph/summary` — 활성 프로젝트의 요약
- `tesserae://lint-report` — markdown 형식의 최신 lint 보고서

또한 클라이언트가 필요에 따라 구성할 수 있는 URI 템플릿:

- `tesserae://wiki/{kind}/{slug}` — 컴파일된 모든 위키 페이지 본문
- `tesserae://raw/{source_path}` — 모든 원본 소스 markdown

### Prompts — 원클릭 리서치 템플릿

이 항목들은 클라이언트의 슬래시 메뉴(예: Claude Code의 `/` 팔레트)에 표시됩니다:

| Prompt | 인자 | 동작 |
|---|---|---|
| `summarize-paper` | `slug` (필수) | `node_context` + `wiki_page` + 선택적 `raw_source`를 호출한 뒤 기여, 방법 스케치, 핵심 결과, 한계, 관련 노드로 구조화된 요약을 반환합니다 |
| `find-related-work` | `topic` (필수), `limit` | `search_nodes` + `node_context`를 연결하여 관련성 근거와 함께 상위 K개 관련 항목을 반환합니다 |
| `compare-approaches` | `a`, `b` (둘 다 필수) | 양쪽 모두에 대해 `node_context`를 가져오고 성능 주장에 대해 `search_facts`를 가져온 뒤 합성과 함께 나란히 비교한 결과를 반환합니다 |
| `gap-analysis` | `topic` (선택) | 해결되지 않은 미해결 질문, 누락된 벤치마크, 근거가 부족한 주장을 표면화합니다 |
| `triage-open-questions` | _없음_ | 모든 `OpenQuestion` 노드를 나열하고 주제별로 묶은 뒤 우선순위 순서를 제안합니다 |

각 prompt는 모델이 어떤 Tesserae tool을 어떤 순서로 연결해야 하는지를 정확히 알려주는 단일 사용자 메시지로 렌더링되므로, 모델이 매번 표면을 다시 발견할 필요가 없습니다.

## 다중 프로젝트: 하나의 서버에 여러 vault 등록하기

`~/.tesserae/registry.json`에 저장되는 영속 레지스트리를 통해 동일한 MCP 서버가 이름으로 등록된 모든 프로젝트를 해결할 수 있습니다:

```bash
tesserae register-project /path/to/research --name research
tesserae register-project /path/to/notes    --name notes
```

이후 `project` 또는 `graph_path`를 받는 모든 tool은 전체 경로 대신 `project: "research"`를 레지스트리에 대해 해결합니다. 서버는 등록된 `graph_path`가 여전히 존재하는지 검증하고, 재컴파일이 필요한 경우 명확한 오류를 반환합니다.

### 등록된 모든 vault에 대한 팬아웃

`ask` tool은 `scope: "all-registered"`를 받아 등록된 모든 프로젝트를 병렬로 쿼리하고 집계된 결과를 반환합니다:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "Where is splatting used?",
    "scope": "all-registered"
  }
}
```

`scope_aliases: ["research", "notes"]`로 부분집합으로 제한할 수 있습니다.

## 다중 계정 Claude CLI

`ask` tool이 Claude CLI를 통해 라우팅되고 여러 계정(예: `~/.claude`와 `~/.claude-personal2`)이 있다면, 호출마다 `claude_config_dir`을 전달하세요:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "...",
    "claude_config_dir": "/Users/you/.claude-personal2"
  }
}
```

서버는 해당 호출 동안에만 `CLAUDE_CONFIG_DIR`을 export하고 이후 이전 값을 복원합니다. 호출 간 누수가 없습니다.

## 검증

MCP 클라이언트를 재시작한 뒤 연결을 확인하세요:

- Claude Code: `/mcp`에 `tesserae`가 tool 개수와 함께 나열되어야 합니다.
- Cursor: 채팅 바의 MCP 아이콘에 `tesserae: connected`와 tool/resource/prompt 개수가 표시되어야 합니다.
- Codex / Hermes: 이름으로 임의의 tool(예: `schema`)을 호출하고 응답을 확인하세요.

아무것도 나타나지 않는다면 `--graph`가 기존 `.tesserae/graph.json`을 가리키는지 다시 확인하세요 — 서버는 이제 시작 시점과 모든 tool 호출 시점에 이를 검증하므로, 조용한 500 대신 명확한 오류 메시지를 보게 됩니다.

## 어디에 적합한가

MCP 서버는 타입 그래프에 대한 **읽기 인터페이스**입니다. **쓰기 경로**(소스 수집, 재컴파일, RAG-Anything 또는 Understand-Anything 같은 동반 도구 갱신)에는 CLI를 직접 사용하세요. 둘은 분리되어 있습니다: CLI는 `.tesserae/`를 업데이트하고, MCP 서버는 다음 tool 호출 시 그곳에 있는 것을 읽습니다.
