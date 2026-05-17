# Harness セッション履歴

<!-- translations:start -->
<p align="center"><a href="../session-history.md">English</a> · <a href="session-history.ko.md">한국어</a> · <a href="session-history.zh.md">中文</a> · <a href="session-history.ja.md">日本語</a> · <a href="session-history.ru.md">Русский</a> · <a href="session-history.es.md">Español</a> · <a href="session-history.fr.md">Français</a> · <a href="session-history.de.md">Deutsch</a></p>
<!-- translations:end -->
LLM-Wiki はローカルの AI-agent transcript をインポートし、静的サイトの `sessions/` セクションでプロジェクトメモリとしてレンダリングできます。

この機能は意図的に `export-agent-harness` と分離されています。

- `export-agent-harness` は Claude Code、Codex、Gemini、Cursor、Kiro、OpenCode などのツール向けの outbound context です。
- `project sessions ...` は inbound history です。現在のプロジェクトの過去の Claude Code/Codex セッションを正規化し、`.llm-wiki/harness_sessions/` に保存し、`project build-site` がセッションの index/detail ページを公開できるようにします。

## プライバシーモデル

セッションのインポートは明示的です。通常の `project compile` や `project build-site` は `.llm-wiki/harness_sessions/` にある正規化済みセッションを読みますが、非公開の harness transcript ディレクトリを不意に scrape することはありません。

インポートされたセッションレコードはローカルプロジェクトの成果物です。公開サイトに公開する前に確認してください。transcript に secrets、private paths、customer data、未公開コードが含まれる可能性がある場合は特に重要です。

## ローカルセッションの検出とインポート

プロジェクトルートで:

```bash
llm_wiki project sessions discover --import
```

Discovery は現在のプロジェクト作業ディレクトリに属するローカル Claude Code と Codex transcript root をスキャンします。特定の config ディレクトリをスキャンするには `--root` を使い、検出対象を制限するには `--harness` を繰り返します。

```bash
llm_wiki project sessions discover \
  --root ~/.claude \
  --root ~/.codex \
  --harness claude-code \
  --harness codex \
  --import
```

`--import` なしでは、discovery は正規化セッションレコードを書き込まず、見つかった内容だけを表示します。

## 正規化 JSON を直接インポート

別のツールが正規化済みの `HarnessSession` JSON をすでに生成している場合、1 つのファイルまたはファイル一覧をインポートできます。

```bash
llm_wiki project sessions import path/to/session.json path/to/more-sessions.json
```

各入力は 1 つのセッションオブジェクトまたはセッションオブジェクトのリストを含められます。

## インポート済みセッションの一覧

```bash
llm_wiki project sessions list
```

セッションは以下に保存されます。

```text
.llm-wiki/harness_sessions/
  manifest.json
  <harness>/
    <session>.json
    <session>.md
```

## 静的セッションページをビルド

セッションをインポートした後、サイトを再ビルドします。

```bash
llm_wiki project build-site
```

サイトは次を出力します。

```text
.llm-wiki/site/sessions/index.html
.llm-wiki/site/sessions/<project>/<session>.html
```

生成されたサイトは global rail、home Browse cards、search entries、各 session detail page の breadcrumb trail から Sessions へリンクします。

## セッション詳細ページのレイアウト

セッション詳細ページは単独の transcript dump ではなく、共有の static-site shell を使います。含まれるもの:

- hero と stat strip;
- high-level summary;
- timeline と size metadata;
- 存在する場合は decisions、files、commands、tools、errors;
- 折りたたまれた subagent tree;
- turn ごとの user/assistant conversation;
- 直前の assistant turn の下に付く折りたたみ tool-use blocks;
- `#turn-N` anchors にリンクする左側 conversation rail。

会話 markdown はサイトの markdown renderer を通してレンダリングされます。inline code、明示的な command/tag markup、paths、filenames、hashtags などの意味的な表面は compact chips として装飾されます。ランダムな大文字名詞は自動で chip 化されません。

現在の transcript typography:

| Surface | Selector | Size |
|---|---|---|
| 会話 markdown prose | `.session-turn-text`, prose children | `8px` |
| 一般的な会話 code fences | `.session-turn-text pre` | `10px` |
| Bash/shell fenced code content | `.session-code-block code.language-bash`, `.language-sh`, `.language-shell`, `.language-zsh` | `11px` |
| Tool details/summary | `.session-tool-details`, `.session-tool-details > summary` | `10px` |
| Tool-use header | `.session-tool-use-header` | `8px` |
| Tool payload text | `.session-tool-use-text` | `6px` |

## セッション公開チェックリスト

セッションを含む公開サイトをデプロイする前に:

1. `llm_wiki project sessions list` を実行し、件数が想定どおりか確認します。
2. 機密情報がないか `.llm-wiki/harness_sessions/` を確認します。
3. `llm_wiki project build-site` で再ビルドします。
4. ローカルで `sessions/index.html` と少なくとも 1 つのセッション詳細ページを開きます。
5. tool blocks がデフォルトで折りたたまれ、raw tool payloads を公開してよいことを確認します。
6. source tree を commit した後、`llm_wiki project deploy --build` でデプロイします。
