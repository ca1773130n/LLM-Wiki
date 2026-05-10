# クイックスタート

<!-- translations:start -->
<p align="center"><a href="../quickstart.md">English</a> · <a href="quickstart.ko.md">한국어</a> · <a href="quickstart.zh.md">中文</a> · <a href="quickstart.ja.md">日本語</a> · <a href="quickstart.ru.md">Русский</a> · <a href="quickstart.es.md">Español</a> · <a href="quickstart.fr.md">Français</a></p>
<!-- translations:end -->
このページは、既存のプロジェクトディレクトリから閲覧可能な LLM-Wiki までの最短ルートを示します。

## 1. セットアップウィザードを実行

インデックスしたいプロジェクトで:

```bash
cd /path/to/my-project
llm_wiki project setup
```

ウィザードは `README.md`、`docs`、`src`、`lib`、`app`、`packages`、`data` などの一般的な source を検出し、`.llm-wiki/config.json` を書き込みます。またデフォルトの Cognee backend を設定し、`project ask` が Cognee を試してから compiled wiki search に fallback できるようにします。

Understand Anything と Cognee runtime memory を有効にした完全自動セットアップ:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

実行内容:

| Flag | Effect |
|---|---|
| `--with-understand-anything` | UA graph projection を source として追加します。 |
| `--install-understand-anything` | UA companion skills をインストール/更新します。 |
| `--understand-anything-platform codex` | Codex を使って LLM-Wiki の managed UA refresh wrapper を実行します。 |
| `--run-cognee` | compile 中に best-effort の Cognee runtime cognify を実行します。 |
| `--install-cognee` | Cognee がない場合、現在の Python でインストールします。 |

ユーザーは UA install path を知る必要も `/understand` と入力する必要もありません。UA graph がない、または古い場合、`project compile` が `project refresh-understand-anything` を実行します。

## 2. グラフと projections をコンパイル

```bash
llm_wiki project compile
```

`project compile` は durable artifacts を書き込みます。

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

初回実行後は `--changed-only` を使うと、変更されていない markdown ファイルをスキップしつつ、ファイル変更がない場合に以前の graph を保持できます。Understand Anything が有効な場合、compile は最初に `.llm-wiki/external/understand-anything.md` を refresh/materialize します。Cognee runtime が有効な場合は、`.llm-wiki/cognee_bundle/` の書き込み後に Cognee も best-effort で更新します。

## 3. 静的 frontend をビルドして配信

```bash
llm_wiki project build-site
llm_wiki project serve --port 8765
```

開く:

```text
http://127.0.0.1:8765/
```

<!-- BEGIN: subagent-r-watch -->
### 保存時の自動リビルド

開発サーバーと polling watcher を組み合わせると、`data/` と `docs/` 以下の編集で incremental recompile がトリガーされます。

```bash
# terminal 1
python3 -m http.server 56821 --directory .llm-wiki/site

# terminal 2
llm_wiki project watch
```

`project watch` は 2 秒ごとに polling し、1 秒 debounce してから `compile --changed-only` を実行します。cron 風の rebuild には `--once`（snapshots vs `.llm-wiki/.watch-cache.json`）、custom watch dirs の追加には `--paths <dir>`、cadence の調整には `--interval` / `--debounce` を使います。
<!-- END: subagent-r-watch -->

表示されるすべての route（home、sources、concepts、entities、papers、repos、topics、syntheses、questions、timeline、graph、さらに AI siblings）の注釈付き tour は [`docs/frontend-redesign.md`](frontend-redesign.ja.md) を参照してください。

Frontend は dependency-light で、次を書き込みます。

```text
.llm-wiki/site/index.html
.llm-wiki/site/sessions/index.html
.llm-wiki/site/graph.json
.llm-wiki/site/search-index.json
.llm-wiki/site/llms.txt
```

## 4. ローカル agent セッション履歴をインポート

セッション履歴のインポートは明示的です。通常の compile/build は正規化済みセッションを読みますが、private Claude Code や Codex transcript stores を自動でスキャンしません。

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

インポートされたセッションは global Sessions section、site search、home Browse cards に表示されます。セッション詳細ページは user/assistant turns を読みやすい markdown としてレンダリングし、tool-use blocks を直前の assistant turn の下に付け、`#turn-N` navigation 用の左側 turn rail を提供します。privacy notes、import formats、現在の transcript typography map は [`docs/session-history.md`](session-history.ja.md) を参照してください。

## 5. Wiki を lint

```bash
llm_wiki project lint
```

Compiled graph + wiki + site を巡回し、orphan papers、stale citations、graph と wiki/ の drift、ghost synthesis inputs などを検出します。`.llm-wiki/lint-report.md` と `.llm-wiki/lint-report.json` を書き込みます。安全な auto-fixes（missing `implemented_in` edges、ghost-input pruning）を適用するには `--fix-trivial`、errors の場合だけ exit code を失敗させるには `--severity error` を渡します。

## 6. Wiki に問い合わせる

```bash
llm_wiki project query "What is Gaussian Splatting?"
```

デフォルトは search-only です。`.llm-wiki/site/search-index.json` 上の BM25 と、マッチした `wiki/<kind>/<slug>.md` からの 200 文字 excerpt を使います。絞り込むには `--kind papers`（または `concepts`、`repos` など）、広げるには `--top-k N`、構造化出力には `--json` を渡します。`[node_id]` citations 付きの合成回答を Claude に求めるには `--llm` を追加（または `LLM_WIKI_QUERY_LLM=1` を設定）します。`--interactive` は readline REPL を開き、空行または EOF で終了します。`LLM_WIKI_QUERY_DRY_RUN=1` は API 呼び出しなしで prompt を試します。

## 7. Agent harness ファイルを export

```bash
llm_wiki project export-agent-harness
```

サポート対象:

- Claude Code
- Codex
- Gemini
- Kiro
- Cursor
- OpenCode

部分例:

```bash
llm_wiki project export-agent-harness \
  --target claude-code \
  --target cursor \
  --target opencode
```

## 8. Obsidian vault を export

```bash
llm_wiki project export-obsidian
```

または既存 vault に書き込み:

```bash
llm_wiki project export-obsidian --vault "$OBSIDIAN_VAULT_PATH"
```

Vault には markdown projections、`.obsidian` defaults、graph coloring、`raw/assets/`、Dataview dashboard が含まれます。

## 9. MCP を設定

```bash
llm_wiki project mcp-config --server-name my_project_wiki
```

出力を `~/.hermes/config.yaml` の `mcp_servers` の下に貼り付け、Hermes/gateway を再起動します。

## 10. Graphiti export / sync

依存関係なしの episode export:

```bash
llm_wiki project export-graphiti
```

Graphiti をインストールせずに dry-run sync smoke:

```bash
llm_wiki project sync-graphiti --dry-run
```

Live sync には `graphiti_core` と到達可能な Neo4j backend が必要です。

```bash
llm_wiki project sync-graphiti \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-password '<password>'
```

## 11. GitHub Pages にデプロイ

`.llm-wiki/site/` の compiled site をプロジェクト git origin の `gh-pages` branch に push します。

```bash
llm_wiki project deploy --build --enable-pages
```

`--build` は最初に `project compile` を実行し、site を最新にします。`--enable-pages` は `gh` CLI で Pages を有効化します（idempotent。`gh` がない場合はヒント付きでスキップ）。push せず stage/commit するには `--dry-run`、defaults を上書きするには `--branch` / `--remote`、dirty working tree でのデプロイを許可するには `--force` を使います。

サイトは `https://<owner>.github.io/<repo>/` で到達可能になります。
