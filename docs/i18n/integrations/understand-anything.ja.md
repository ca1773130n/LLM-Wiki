# Understand Anything 連携ワークフロー

<!-- translations:start -->
<p align="center"><a href="../../integrations/understand-anything.md">English</a> · <a href="understand-anything.ko.md">한국어</a> · <a href="understand-anything.zh.md">中文</a> · <a href="understand-anything.ja.md">日本語</a> · <a href="understand-anything.ru.md">Русский</a> · <a href="understand-anything.es.md">Español</a> · <a href="understand-anything.fr.md">Français</a></p>
<!-- translations:end -->
[Understand Anything](https://github.com/Lum1104/Understand-Anything) と LLM-Wiki は相互補完的なプロジェクトです。

- Understand Anything は、コードベースの知識グラフとインタラクティブなダッシュボードの生成に優れています。
- LLM-Wiki は、長期的なエージェントメモリに注力しています: ドキュメント、markdown/wiki コンパイル、静的公開、セッション履歴、エージェント向けエクスポート。

LLM-Wiki は Understand Anything をベンダー化したり取り込んだりすべきではありません。有用なグラフ成果物を生成できる独立した連携ツールとして扱ってください。

## なぜ両方を使うのか？

Understand Anything は次を書き込めます:

```text
.understand-anything/knowledge-graph.json
```

このグラフは、ファイル、関数、クラス、モジュール、概念、依存関係、レイヤー、ツアーなどのコード構造を捉えます。

その後、LLM-Wiki はその成果物をプロジェクトメモリの残りと一緒に保存できます:

- ソースドキュメントと markdown ページ;
- リポジトリファイル;
- 調査メモ;
- ローカルの Claude Code / Codex セッション履歴;
- 生成された静的 wiki ページ;
- 2D / 3D グラフ Web サイトビュー;
- `llms.txt`、`llms-full.txt`、`search-index.json`、`graph.json`、ページごとのエージェント sibling。

## 現在の低摩擦ワークフロー

推奨される経路はセットアップウィザードです:

```bash
llm_wiki project setup
```

連携ツールのステップで Understand Anything を選択します。LLM-Wiki は要求に応じて連携 skills をインストール/更新し、管理された更新コマンドを `.llm-wiki/config.json` に書き込みます。以降の `llm_wiki project compile` 呼び出しでは、UA グラフが存在しない、または古い場合に、そのラッパーが自動実行されます。

非対話型の自動化には次を使います:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex
llm_wiki project compile
```

保存されるコマンドはユーザーが考案するものではなく、LLM-Wiki が所有するものです:

```bash
llm_wiki project refresh-understand-anything --platform codex
```

コンパイル中、LLM-Wiki は次を行います:

1. `.understand-anything/knowledge-graph.json` が存在し、メタデータが利用可能な場合は現在の git コミットと一致するか確認します;
2. グラフが欠落/古い場合、または更新が強制された場合にのみ、設定されたエージェントプラットフォーム（`codex`、`opencode`、または `claude`）を実行します;
3. グラフが書き込まれたことを検証します;
4. `.llm-wiki/external/understand-anything.md` を具体化します;
5. 通常のメモリコンパイルを続行します。

コンパイル前に、設定済みの外部更新コマンドをすべて強制実行できます:

```bash
llm_wiki project compile --refresh-external-tools
```

Cognee も必要ですか？同じ setup コマンドにランタイムメモリのフラグを追加してください:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

## 手動での同等手順

管理されたセットアップ経路が推奨です。意図的に LLM-Wiki の外で UA を使いたい場合は、まずエージェント環境内で Understand Anything を実行してください:

```bash
/understand
```

次に `llm_wiki project setup --with-understand-anything` を実行し、LLM-Wiki に markdown 投影ソースを記録させます。直接の JSON ファイルは手入力のソースパスではなく、生の連携成果物として保持されます。

```bash
llm_wiki project setup --with-understand-anything
llm_wiki project compile
llm_wiki project build-site
```

ローカルのエージェントセッションメモリも必要な場合:

```bash
llm_wiki project sessions discover --import
llm_wiki project build-site
```

## 将来あり得るブリッジ

将来の任意ブリッジでは、Understand Anything のグラフ schema を LLM-Wiki の typed graph ontology により直接マッピングできる可能性があります。

想定されるマッピング:

| Understand Anything | LLM-Wiki の方向性 |
|---|---|
| `project` | リポジトリ/プロジェクトメタデータ |
| `nodes[type=file]` | ソース/ドキュメント/ファイルノード |
| `nodes[type=function]` | 関数/コードシンボルノード |
| `nodes[type=class]` | クラス/コードシンボルノード |
| `nodes[type=module]` | モジュール/パッケージノード |
| `nodes[type=concept]` | 概念ノード |
| `edges[type=imports]` | import/依存関係エッジ |
| `edges[type=contains]` | 包含エッジ |
| `edges[type=calls]` | 呼び出し/参照エッジ |
| `layers[]` | アーキテクチャのグループ化メタデータ |
| `tour[]` | オンボーディング/総合ページ |

両プロジェクトが安定した交換契約に合意しない限り、このブリッジは任意かつ外部のものとして維持してください。

## 協業の原則

LLM-Wiki を Understand Anything の置き換えとして位置づけないでください。

より良い位置づけ:

- Understand Anything は、開発者が今コードベースを理解するのを助けます。
- LLM-Wiki は、エージェントが時間をかけてプロジェクト知識を記憶、検索、引用、更新、公開するのを助けます。
