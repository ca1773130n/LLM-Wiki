# Self-dogfood 演示

<!-- translations:start -->
<p align="center"><a href="../self-dogfood.md">English</a> · <a href="self-dogfood.ko.md">한국어</a> · <a href="self-dogfood.zh.md">中文</a> · <a href="self-dogfood.ja.md">日本語</a> · <a href="self-dogfood.ru.md">Русский</a> · <a href="self-dogfood.es.md">Español</a> · <a href="self-dogfood.fr.md">Français</a> · <a href="self-dogfood.de.md">Deutsch</a></p>
<!-- translations:end -->
此项目可以索引自身。self-dogfood 流程证明 LLM-Wiki 可以被安装、在自己的仓库内设置、摄取自己的 docs/source/tests/scripts、可选地刷新 Understand Anything 和 Cognee、编译图谱产物，并构建静态 Web 前端。

## 命令

从仓库根目录：

```bash
# 确保 shell 命令已安装。
./scripts/install.sh --dir "$PWD"
export PATH="$HOME/.local/bin:$PATH"

# 将此仓库设置为 LLM-Wiki 项目。
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

# 编译已配置的源。
llm_wiki project compile

# 显式重建静态前端。
llm_wiki project build-site

# 在本地提供服务。
llm_wiki project serve --port 8765
```

打开：

```text
http://127.0.0.1:8765/
```

## 生成的工作区

self-demo 会把生成的产物写入：

```text
.llm-wiki/
```

关键产物：

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

生成的工作区默认有意不提交。它可以通过上面的命令从仓库源复现。

## 最新已验证运行

已于 `2026-04-27 11:11:23 KST` 从 LLM-Wiki 仓库自身验证。

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

最终产物计数：

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

主要节点类型：

```text
CodeFunction:    452
Dependency:       55
CodeClass:        54
Concept:          51
SourceFile:       47
SourceDocument:    7
CodeProject:       1
```

浏览器验证：

```text
loaded title: Home · llm_wiki_self
visible stats: 667 nodes / 1020 edges / 55 sources / 7 types
sources page: source evidence table links to per-source pages
source detail: llm_wiki/frontend.py shows 41 nodes, 54 related edges, type mix, node links, and edge table
search smoke: StaticSiteBuilder returned CodeClass and StaticSiteBuilder.write_site results
console: no JavaScript errors on home, sources, source detail, or graph pages
server: TCP *:56821 LISTEN, serving via --host 0.0.0.0
```

## 这展示了什么

- 公开安装路径可用。
- `llm_wiki` shell 命令可用。
- 仓库可以附加一个项目本地的 `.llm-wiki` 工作区。
- 研究/文档 markdown 和开发代码图谱节点可以共存。
- Markdown、Obsidian、frontend、Graphiti、Cognee、SQLite、report 和 agent-harness 投影由同一条图谱流水线生成。
- 静态 HTML 前端可以在没有 JavaScript 构建步骤的情况下浏览项目图谱。
