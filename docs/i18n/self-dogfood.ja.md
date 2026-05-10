# Self-dogfood デモ

<!-- translations:start -->
<p align="center"><a href="../self-dogfood.md">English</a> · <a href="self-dogfood.ko.md">한국어</a> · <a href="self-dogfood.zh.md">中文</a> · <a href="self-dogfood.ja.md">日本語</a> · <a href="self-dogfood.ru.md">Русский</a> · <a href="self-dogfood.es.md">Español</a> · <a href="self-dogfood.fr.md">Français</a></p>
<!-- translations:end -->
このプロジェクトは自分自身をインデックスできます。self-dogfood フローは、LLM-Wiki をインストールし、自身のリポジトリ内で設定し、自身の docs/source/tests/scripts を取り込み、任意で Understand Anything と Cognee を更新し、グラフ成果物をコンパイルし、静的 Web フロントエンドをビルドできることを証明します。

## コマンド

リポジトリルートから:

```bash
# shell コマンドがインストールされていることを確認します。
./scripts/install.sh --dir "$PWD"
export PATH="$HOME/.local/bin:$PATH"

# このリポジトリを LLM-Wiki プロジェクトとして設定します。
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

# 設定済みソースをコンパイルします。
llm_wiki project compile

# 静的フロントエンドを明示的に再ビルドします。
llm_wiki project build-site

# ローカルで配信します。
llm_wiki project serve --port 8765
```

開く:

```text
http://127.0.0.1:8765/
```

## 生成されるワークスペース

self-demo は生成された成果物を次の場所に書き込みます:

```text
.llm-wiki/
```

主要な成果物:

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

生成されたワークスペースは、デフォルトではコミットしないことを意図しています。上記のコマンドでリポジトリソースから再現できます。

## 最新の検証済み実行

LLM-Wiki リポジトリ自身から `2026-04-27 11:11:23 KST` に検証済みです。

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

最終成果物数:

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

上位ノードタイプ:

```text
CodeFunction:    452
Dependency:       55
CodeClass:        54
Concept:          51
SourceFile:       47
SourceDocument:    7
CodeProject:       1
```

ブラウザ検証:

```text
loaded title: Home · llm_wiki_self
visible stats: 667 nodes / 1020 edges / 55 sources / 7 types
sources page: source evidence table links to per-source pages
source detail: llm_wiki/frontend.py shows 41 nodes, 54 related edges, type mix, node links, and edge table
search smoke: StaticSiteBuilder returned CodeClass and StaticSiteBuilder.write_site results
console: no JavaScript errors on home, sources, source detail, or graph pages
server: TCP *:56821 LISTEN, serving via --host 0.0.0.0
```

## これが示すこと

- 公開インストール経路が動作します。
- `llm_wiki` shell コマンドが動作します。
- リポジトリはプロジェクトローカルの `.llm-wiki` ワークスペースを接続できます。
- 研究/ドキュメント markdown と開発コードのグラフノードが共存できます。
- Markdown、Obsidian、frontend、Graphiti、Cognee、SQLite、report、agent-harness の投影が 1 つのグラフパイプラインから生成されます。
- 静的 HTML フロントエンドは、JavaScript ビルド手順なしでプロジェクトグラフを閲覧できます。
