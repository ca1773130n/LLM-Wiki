# MCP — LLM-Wiki を Claude Code、Codex、Cursor に接続する

<!-- translations:start -->
<p align="center"><a href="../../integrations/mcp.md">English</a> · <a href="mcp.ko.md">한국어</a> · <a href="mcp.zh.md">中文</a> · <a href="mcp.ru.md">Русский</a> · <a href="mcp.es.md">Español</a> · <a href="mcp.fr.md">Français</a> · <a href="mcp.de.md">Deutsch</a></p>
<!-- translations:end -->

LLM-Wiki は [Model Context Protocol](https://modelcontextprotocol.io) の stdio サーバーを同梱しており、コンパイル済みの型付きグラフを任意の MCP 対応クライアント（Claude Code、Codex CLI、Cursor、Claude Desktop など）に公開します。サーバーは MCP の 3 つの完全な面 — **tools**、**resources**、**prompts** — を提供するため、クライアントはオンデマンドでグラフを問い合わせることも、正規化された URI から低コストでコンテキストを供給することもできます。

## 前提条件

サーバーは `.llm-wiki/graph.json` を読み込むため、最初に一度コンパイルしておく必要があります:

```bash
cd /path/to/your-project
llm_wiki project setup    # interactive; or --yes for non-interactive
llm_wiki project compile  # deterministic, no LLM calls, no API keys
```

ソースが変わったらいつでも再コンパイルしてください。サーバーは再起動なしで次回の tool 呼び出し時に新しいグラフを読み込みます。

## 1) クライアント設定を生成する

```bash
llm_wiki project mcp-config
```

おおよそ次のような JSON スニペットを出力します:

```json
{
  "mcpServers": {
    "llm-wiki": {
      "command": "python3",
      "args": [
        "-m", "llm_wiki.mcp_server",
        "--graph", "/path/to/your-project/.llm-wiki/graph.json"
      ]
    }
  }
}
```

正確なパスは現在のプロジェクトから補完されます。サーバーエントリー名を `llm-wiki` 以外にしたい場合は `--name <alias>` を渡してください。

## 2) MCP クライアントに貼り付ける

| クライアント | 設定ファイルの場所 |
|---|---|
| Claude Code | `~/.claude/mcp-servers.json`（または `~/.config/claude-code/mcp-servers.json`） |
| Claude Desktop | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Codex CLI | `~/.config/codex/mcp-servers.json` |
| Cursor | Settings → MCP Servers → JSON を貼り付け |
| Hermes | `~/.hermes/config.toml`（`mcp-config --format hermes` が出力する TOML 相当ブロックを使用） |

編集後はクライアントを再起動してください。次のセッションで接続され、LLM-Wiki のサーフェスが検出されます。

## 3) クライアントから見えるもの

### Tools — モデルから呼び出される

| Tool | 用途 |
|---|---|
| `schema` | 管理された node、edge、wiki-kind の語彙 |
| `graph_summary` | アクティブなプロジェクトの node + edge 数と種別分布 |
| `search_nodes` | グラフ node をクエリ・type・kind でフィルタし、スコア順の上位 N 件を返す |
| `node_context` | ある node とその接続 edge、隣接 node |
| `search_facts` | グラフから射影された時系列ファクト（Graphiti スタイル） |
| `timeline` | `valid_from` で順序付けられたファクトの縦断的ビュー |
| `wiki_page` | ある node に対するコンパイル済み markdown ページ本文 |
| `raw_source` | 元のソース markdown（16 KB を上限としてキャップ） |
| `lint_report` | 直近のコンパイル時 lint 結果 |
| `ask` | 設定されたメモリバックエンド（raganything、cognee、またはコンパイル済み wiki）経由の自然言語 Q&A |
| `list_projects` / `register_project` / `activate_project` / `unregister_project` | マルチプロジェクトレジストリの制御 |

### Resources — モデルのコンテキストへ自動的に読み込まれる

クライアントが tool turn を消費せずに resource picker から取り込める URI:

- `llm-wiki://graph/schema` — `schema` tool と同じペイロードを静的コンテキストとして提供
- `llm-wiki://graph/summary` — アクティブなプロジェクトのサマリー
- `llm-wiki://lint-report` — 直近の lint レポートを markdown として提供

加えて、クライアントがオンデマンドで構築できる URI テンプレート:

- `llm-wiki://wiki/{kind}/{slug}` — コンパイル済み wiki ページ本文
- `llm-wiki://raw/{source_path}` — 任意の生ソース markdown

### Prompts — ワンクリックのリサーチテンプレート

これらはクライアントのスラッシュメニュー（例: Claude Code の `/` パレット）に表示されます:

| Prompt | 引数 | 動作 |
|---|---|---|
| `summarize-paper` | `slug`（必須） | `node_context` + `wiki_page` + 任意の `raw_source` を呼び出し、貢献、手法のスケッチ、主要な結果、限界、関連 node を含む構造化サマリーを返す |
| `find-related-work` | `topic`（必須）、`limit` | `search_nodes` + `node_context` を連鎖させて、関連度の根拠付きで上位 K 件の関連項目を返す |
| `compare-approaches` | `a`、`b`（両方必須） | 両者に対して `node_context` を取得し、性能主張については `search_facts` を取得; 統合付きの並列比較を返す |
| `gap-analysis` | `topic`（任意） | 未解決の論点、欠落しているベンチマーク、根拠の薄い主張を浮かび上がらせる |
| `triage-open-questions` | _なし_ | すべての `OpenQuestion` node を列挙し、トピックでグルーピングし、優先順位を提案する |

各 prompt は単一のユーザーメッセージにレンダリングされ、モデルに対してどの LLM-Wiki tool をどう連鎖させるかを正確に伝えるため、モデルが毎回サーフェスを再発見する必要はありません。

## マルチプロジェクト: 1 つのサーバーに複数のヴォルトを登録する

`~/.llm-wiki/registry.json` の永続レジストリにより、同じ MCP サーバーが任意の登録済みプロジェクトを名前で解決できます:

```bash
llm_wiki register-project /path/to/research --name research
llm_wiki register-project /path/to/notes    --name notes
```

これ以降、`project` または `graph_path` を受け取るすべての tool は、フルパスを必要とせず `project: "research"` をレジストリで解決します。サーバーは登録済みの `graph_path` がまだ存在するかも検証し、再コンパイルが必要な場合は明確なエラーを返します。

### 登録済みすべてのヴォルトへのファンアウト

`ask` tool は `scope: "all-registered"` を受け取り、登録済みのすべてのプロジェクトに並列でクエリして集約結果を返します:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "Where is splatting used?",
    "scope": "all-registered"
  }
}
```

`scope_aliases: ["research", "notes"]` で対象を絞り込めます。

## マルチアカウントの Claude CLI

`ask` tool が Claude CLI 経由でルーティングされ、複数アカウント（例: `~/.claude` と `~/.claude-personal2`）を使っている場合は、呼び出しごとに `claude_config_dir` を渡してください:

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "...",
    "claude_config_dir": "/Users/you/.claude-personal2"
  }
}
```

サーバーはその呼び出しの間だけ `CLAUDE_CONFIG_DIR` をエクスポートし、終了後に元の値を復元します。呼び出し間でリークしません。

## 動作確認

MCP クライアントを再起動した後、接続を確認します:

- Claude Code: `/mcp` に `llm-wiki` が tool 数とともに表示されるはずです。
- Cursor: チャットバーの MCP アイコンに `llm-wiki: connected` と tool/resource/prompt の件数が表示されるはずです。
- Codex / Hermes: 任意の tool（例: `schema`）を名前で呼び出してレスポンスを確認してください。

何も現れない場合、`--graph` が既存の `.llm-wiki/graph.json` を指しているか再確認してください — サーバーは起動時および各 tool 呼び出し時にこれを検証するようになり、サイレントな 500 ではなく明確なエラーメッセージが表示されます。

## どこに位置づけられるか

MCP サーバーは型付きグラフへの**読み取りインタフェース**です。**書き込み経路**（ソースの取り込み、再コンパイル、RAG-Anything や Understand-Anything のような連携ツールの更新）には CLI を直接使ってください。両者は疎結合です: CLI が `.llm-wiki/` を更新し、MCP サーバーは次の tool 呼び出しでそこにあるものを読み取ります。
