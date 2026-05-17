# 快速开始

<!-- translations:start -->
<p align="center"><a href="../quickstart.md">English</a> · <a href="quickstart.ko.md">한국어</a> · <a href="quickstart.zh.md">中文</a> · <a href="quickstart.ja.md">日本語</a> · <a href="quickstart.ru.md">Русский</a> · <a href="quickstart.es.md">Español</a> · <a href="quickstart.fr.md">Français</a> · <a href="quickstart.de.md">Deutsch</a></p>
<!-- translations:end -->
本页展示从已有项目目录到可浏览 LLM-Wiki 的最短路径。

## 1. 运行设置向导

在你想索引的项目中：

```bash
cd /path/to/my-project
llm_wiki project setup
```

向导会检测 `README.md`、`docs`、`src`、`lib`、`app`、`packages`、`data` 等常见 source，然后写入 `.llm-wiki/config.json`。它还会配置默认 Cognee backend，使 `project ask` 可以先尝试 Cognee，再 fallback 到 compiled wiki search。

启用 Understand Anything 和 Cognee runtime memory 的全自动设置：

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

它会做什么：

| Flag | Effect |
|---|---|
| `--with-understand-anything` | 将 UA graph projection 添加为 source。 |
| `--install-understand-anything` | 安装/更新 UA companion skills。 |
| `--understand-anything-platform codex` | 使用 Codex 运行 LLM-Wiki 托管的 UA refresh wrapper。 |
| `--run-cognee` | 在 compile 期间尽力运行 Cognee runtime cognify。 |
| `--install-cognee` | 缺少 Cognee 时用当前 Python 安装它。 |

用户不需要知道 UA install path，也不需要输入 `/understand`；当 UA graph 缺失或过期时，`project compile` 会运行 `project refresh-understand-anything`。

## 2. 编译图和 projections

```bash
llm_wiki project compile
```

`project compile` 会写入持久产物：

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

首次运行后可使用 `--changed-only` 跳过未更改的 markdown 文件，并在没有文件变化时保留之前的 graph。如果启用了 Understand Anything，compile 会先刷新/物化 `.llm-wiki/external/understand-anything.md`；如果启用了 Cognee runtime，它也会在写入 `.llm-wiki/cognee_bundle/` 后尽力更新 Cognee。

## 3. 构建并提供静态 frontend

```bash
llm_wiki project build-site
llm_wiki project serve --port 8765
```

打开：

```text
http://127.0.0.1:8765/
```

<!-- BEGIN: subagent-r-watch -->
### 保存时自动重建

将开发服务器与 polling watcher 配合使用，让 `data/` 和 `docs/` 下的编辑触发增量 recompile：

```bash
# terminal 1
python3 -m http.server 56821 --directory .llm-wiki/site

# terminal 2
llm_wiki project watch
```

`project watch` 每 2 秒 polling，一次 1 秒 debounce，然后运行 `compile --changed-only`。使用 `--once` 进行 cron 风格 rebuild（snapshots vs `.llm-wiki/.watch-cache.json`），用 `--paths <dir>` 添加自定义 watch 目录，用 `--interval` / `--debounce` 调整节奏。
<!-- END: subagent-r-watch -->

所有可见 route（home、sources、concepts、entities、papers、repos、topics、syntheses、questions、timeline、graph 以及 AI siblings）的注释导览见 [`docs/frontend-redesign.md`](frontend-redesign.zh.md)。

Frontend 依赖很轻，会写入：

```text
.llm-wiki/site/index.html
.llm-wiki/site/sessions/index.html
.llm-wiki/site/graph.json
.llm-wiki/site/search-index.json
.llm-wiki/site/llms.txt
```

## 4. 导入本地 agent 会话历史

会话历史导入是显式操作：普通 compile/build 会读取已规范化的会话，但不会自行扫描私有 Claude Code 或 Codex transcript stores。

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

导入的会话会出现在全局 Sessions 区域、站点搜索和首页 Browse 卡片中。会话详情页会把 user/assistant turns 渲染为可读 markdown，把 tool-use blocks 附在前一个 assistant turn 下，并提供用于 `#turn-N` 导航的左侧 turn rail。隐私说明、导入格式和当前 transcript typography map 见 [`docs/session-history.md`](session-history.zh.md)。

## 5. Lint wiki

```bash
llm_wiki project lint
```

遍历 compiled graph + wiki + site，并标记 orphan papers、stale citations、graph 与 wiki/ 之间的 drift、ghost synthesis inputs 等。写入 `.llm-wiki/lint-report.md` 和 `.llm-wiki/lint-report.json`。传入 `--fix-trivial` 可应用安全 auto-fixes（缺失的 `implemented_in` edges、ghost-input pruning），传入 `--severity error` 则只在 error 时让 exit code 失败。

## 6. 查询 wiki

```bash
llm_wiki project query "What is Gaussian Splatting?"
```

默认仅搜索：在 `.llm-wiki/site/search-index.json` 上做 BM25，并从匹配的 `wiki/<kind>/<slug>.md` 抽取 200 字符 excerpt。传入 `--kind papers`（或 `concepts`、`repos` 等）来缩小范围，`--top-k N` 来扩大结果，`--json` 获得结构化输出。添加 `--llm`（或设置 `LLM_WIKI_QUERY_LLM=1`）可请求 Claude 生成带 `[node_id]` citations 的综合答案；`--interactive` 打开 readline REPL，空行或 EOF 退出。`LLM_WIKI_QUERY_DRY_RUN=1` 可在不调用 API 的情况下演练 prompt。

## 7. 导出 agent harness 文件

```bash
llm_wiki project export-agent-harness
```

支持的目标：

- Claude Code
- Codex
- Gemini
- Kiro
- Cursor
- OpenCode

子集示例：

```bash
llm_wiki project export-agent-harness \
  --target claude-code \
  --target cursor \
  --target opencode
```

## 8. 导出 Obsidian vault

```bash
llm_wiki project export-obsidian
```

或写入已有 vault：

```bash
llm_wiki project export-obsidian --vault "$OBSIDIAN_VAULT_PATH"
```

Vault 包含 markdown projections、`.obsidian` defaults、graph coloring、`raw/assets/` 和 Dataview dashboard。

## 9. 配置 MCP

```bash
llm_wiki project mcp-config --server-name my_project_wiki
```

将输出粘贴到 `~/.hermes/config.yaml` 的 `mcp_servers` 下，然后重启 Hermes/gateway。

## 10. Graphiti export / sync

无依赖 episode export：

```bash
llm_wiki project export-graphiti
```

不安装 Graphiti 的 dry-run sync smoke：

```bash
llm_wiki project sync-graphiti --dry-run
```

Live sync 需要 `graphiti_core` 和可访问的 Neo4j backend：

```bash
llm_wiki project sync-graphiti \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-password '<password>'
```

## 11. 部署到 GitHub Pages

将 `.llm-wiki/site/` 中的 compiled site 推送到项目 git origin 的 `gh-pages` 分支：

```bash
llm_wiki project deploy --build --enable-pages
```

`--build` 会先运行 `project compile`，确保 site 是最新的。`--enable-pages` 通过 `gh` CLI 开启 Pages（幂等；如果缺少 `gh` 会提示并跳过）。用 `--dry-run` 在不 push 的情况下 stage 和 commit，用 `--branch` / `--remote` 覆盖默认值，用 `--force` 允许在 dirty working tree 中部署。

站点可通过 `https://<owner>.github.io/<repo>/` 访问。
