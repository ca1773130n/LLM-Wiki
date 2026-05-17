# Obsidian 双方向同期 — 提案設計

<!-- translations:start -->
<p align="center"><a href="../../integrations/obsidian-sync.md">English</a> · <a href="obsidian-sync.ko.md">한국어</a> · <a href="obsidian-sync.zh.md">中文</a> · <a href="obsidian-sync.ru.md">Русский</a> · <a href="obsidian-sync.es.md">Español</a> · <a href="obsidian-sync.fr.md">Français</a> · <a href="obsidian-sync.de.md">Deutsch</a></p>
<!-- translations:end -->

> **ステータス: 提案 (2026-05-17)。** このドキュメントは設計仕様であり、まだ実装された機能ではありません。LLM-Wiki が射影された wiki ページをユーザーに Obsidian 上で編集させ、その編集を次の `project compile` 後も保持させる方法を示しています。実装はこの設計が確定することを前提とします。

現在の [Obsidian エクスポート](obsidian.md)は厳密に一方向です: `.llm-wiki/graph.json` 内の型付きグラフがヴォルトへ射影され、`project compile` が射影されたファイルを上書きします。ユーザーからは逆方向 — Obsidian で説明を編集し、再コンパイル後もそれを残したい — という要望も寄せられています。

このドキュメントは、データモデルを破綻させずにそれをどう実現するかを明文化します。

## 戦略的な方針転換、率直に

現在の README はライブ編集を否認しています:

> LLM-Wiki はライブ編集ではなくソースからのコンパイルを選びます。UI でノートを編集したい場合は Logseq または Obsidian を使ってください。

双方向同期は、フィールドの一部について**この契約を変更します**。これは意図的に行う価値があります。目標は「Obsidian をエディタにする」ではなく — 「ユーザーの Obsidian での編集が再コンパイル時に黙って消されないようにする」ことです。

## 核心アイデア: マージではなくオーバーレイ

同じ node のダイバージした 2 つのコピーをマージしようとする代わりに、ヴォルトを射影に対する**差分レイヤー**として扱います:

```text
source markdown  ──extract──▶  base_graph
                                    +
                              vault_overrides     ◀── computed from vault
                                    ↓
                              final_graph  ──project──▶  vault (.md files)
```

`vault_overrides.json` は `.llm-wiki/` 配下に置かれ、手書きされるものではなく**計算される**ものです。コンパイルのたびに LLM-Wiki はヴォルトを巡回し、射影された各ページを前回の射影が書き出した内容と比較し、ユーザーによる変更をすべてオーバーレイエントリとして記録します。最終的なグラフは `base_graph` にオーバーレイを適用したものです。次の射影はその結果をディスクに書き戻します。

ラウンドトリップは安定しています。ソース側に変更のない同じヴォルトを再コンパイルしても差分は生じません。

## フィールドごとの所有権

node の各フィールドには所有者があります。所有権はソースとヴォルトが食い違ったときに何が起こるかを決めます。

| フィールド | ソース所有 | ヴォルト上書き可 | 備考 |
|---|---|---|---|
| `id`, `type` | yes | no | スキーマ管理対象。extractor が所有 |
| `name` | initial | yes | 正規名はユーザーの方が extractor よりよく知っていることが多い |
| `aliases` | initial | yes | ヴォルトからは追記のみ。ヴォルト側のエントリは常に保持される |
| `description` | initial | **yes** | Obsidian での最も一般的な編集対象 |
| `source_path` | yes | no | 由来情報。編集で消すことはできない |
| `metadata`（宣言済みキー） | initial | yes | 例: `arxiv_id`, `github_repo` — ユーザーが訂正可能 |
| `metadata.user.*` | n/a | yes | ユーザー専用キーの予約名前空間。extractor は書き込まない |
| Outgoing edges（型付き） | yes | no | edges はオントロジーに属し、ヴォルトには属さない |
| ユーザーが書いた新しい wikilink | n/a | yes | `edge_type=user_link` として浮上させ、グラフに書き込む |
| `<!-- user-notes -->` 本文ブロック | never written | always preserved | 射影器が決して触らない追記専用ゾーン |

## 競合ケースとデフォルト

| ケース | デフォルト | 理由 |
|---|---|---|
| ヴォルトの `description` が再抽出されたソースの `description` と異なる | **ヴォルトの勝ち**、`.llm-wiki/lint-report.md` の「diverged fields」配下に記録 | ユーザー編集を尊重する: ユーザーが明確に編集を意図していた。監査証跡で後から見直せる。 |
| ソースファイルが削除されたが射影ページがヴォルトに残っている | node をグラフから除去し、`.llm-wiki/orphans.md` に列挙 | 存在についてはソースが正典。孤児ログにより復元するか受け入れるかを判断できる |
| ユーザーが存在しない slug への wikilink を書いた | トゥームストーン node（type `Stub`）を作成し、lint レポートに浮上させる | ユーザーの意図を捨てず、整理のためにフラグを立てる |
| ユーザーがスキーマの知らない frontmatter キーを追加した | `metadata.user.<key>` として保存し、決して上書きしない | 型付きグラフを汚さずに前方互換性を確保 |
| 異なるマシンの 2 つのヴォルトが同じ node を編集し、両方が Obsidian Sync で同期されている | **v1 の範囲外。** ファイルシステムレベルで最後の書き手が勝つ。 | 真のマルチヴォルト連合は Tier 3。実際のユースケースが現れるまで延期 |

## ユーザーノート追記ゾーン

射影された各ページには、射影器が決して触らないフェンス付きゾーンが用意されます:

```markdown
> [!quote] Paper
> Headline contribution and method sketch projected from the graph...

<!-- user-notes:start -->

Your notes here. Anything between the markers survives recompile forever.
Wikilinks here become `user_link` edges in the graph on the next pull.

<!-- user-notes:end -->

## Outgoing
- ...
```

実用的な効果は 2 つ:
1. ユーザーは任意のページに注釈（例:「自分のノートの第 4 章を参照」）を、リビルドで失うことなく付けられる。
2. プルパスはユーザーノートブロックを wikilink について走査し、それらをオントロジー型 `user_link` の edges として浮上させ、形式的な edge type を汚さずにグラフ到達性を与える。

## リモート転送 — 明示的な非ゴール

LLM-Wiki は同期サーバー、認証レイヤー、競合解消デーモン、ホスト型ヴォルトを構築**しません**。ここでの「双方向」は「コンパイルがヴォルトから読む」という意味であり — コンパイルを実行するマシンへヴォルトをどう届けるかはユーザーの問題で、すでに存在するツールで解決されます:

| スタック | コスト | 備考 |
|---|---|---|
| Obsidian Sync | 有料、$4-8/月 | E2E 暗号化、公式、極めてシンプル |
| iCloud / Dropbox / OneDrive | OS バンドル | 機能はするが競合 UX は厳しい |
| Syncthing | 無料、セルフホスト | 一人クロスデバイスに最適 |
| Git（ヴォルトをコミット） | 無料 | 技術者には競合 UX が最良 |
| LiveSync（CouchDB プラグイン） | 無料、サーバー要 | リアルタイムのマルチデバイス |

5 つすべてがオーバーレイモデルと互換です。LLM-Wiki はヴォルトをミューテーションのストリームではなく、ディスク上のファイルとして見るためです。

## CLI 表面（提案）

```bash
# Pull-only sync (Tier 1a): overlay reader runs as part of compile by default.
llm_wiki project compile                  # always pulls vault overrides if vault exists

# Inspect what would change before letting compile apply
llm_wiki project obsidian-sync --dry-run

# Skip the pull for a single compile (recovery mode)
llm_wiki project compile --no-vault-pull

# Long-running watch (Tier 2)
llm_wiki project obsidian-sync --watch --vault ~/Documents/llm-wiki-vault
```

## フェーズ分け

| Tier | スコープ | 工数 |
|---|---|---|
| **1a** | オーバーレイリーダー: ヴォルトを巡回し `vault_overrides.json` を構築し、コンパイル時に適用。lint がダイバージェンスを報告。 | 約 3 日 |
| **1b** | ユーザーノート追記ゾーン: 射影器は `<!-- user-notes:start --> ... <!-- user-notes:end -->` ブロックを決して触らない。 | 約 1 日 |
| **2** | ウォッチモード: 長時間動作する `obsidian-sync --watch` がファイルシステムイベントでオーバーレイを再実行し、適用前にプロンプトを出す。 | 約 1 週間 |
| **3** | マルチヴォルト連合: グラフがヴォルトごとの由来情報を保持し、同期されたヴォルト間の同時編集をサポート。 | 約 1 か月、実際のユースケースが現れるまで延期 |

## 非ゴール（明示的に）

- 同期サーバー / 認証 / ホスト型バックエンド。
- Obsidian 内でのリアルタイム共同編集（必要なら LiveSync を使ってください）。
- すべてのフィールドをラウンドトリップさせるために extractor を書き直すこと — オーバーレイテーブル外のものについては、ソース markdown が引き続き正典である。
- 静的 HTML サイトの同期（`build-site` は引き続き射影専用）。

## 実装前に決定すべき未解決事項

これらには提案デフォルトがありますが、コードが入る前に最終確認の価値があります:

1. **lint レポートの形。** ダイバージしたフィールドは別ファイル `.llm-wiki/diverged-fields.md` として出すべきか、それとも既存の `lint-report.md` の新セクションとして出すべきか。提案: git で差分を取れるよう専用ファイル。
2. **トゥームストーン node の型。** `Stub` を実スキーマ型として追加するか、それとも `OpenQuestion` に `_kind: stub` 識別子を付けて流用するか。提案: 実型、名前は `Stub`、公開インデックスから非表示。
3. **コンパイル時プルのデフォルト。** デフォルト ON か OFF か。提案: 設定されたパスにヴォルトが存在する場合は ON。初回起動時のみ確認プロンプトを出し、ユーザーが意図的にオプトインできるようにする。
4. **差分のための「前回の射影」とは何か。** スナップショットを `.llm-wiki/vault_snapshot.json` に保存するか、それともコンパイルのたびに即時に再射影するか。提案: スナップショット方式で、各コンパイルの終わりに書き出す。安価で、extractor の非決定性がオーバーレイに漏れることを避けられる。
5. **多言語ヴォルト射影。** 現在の射影は単一言語（ソース）です。オーバーレイはロケール対応にすべきか（例: 韓国語ヴォルトでの `description` 編集は韓国語射影のみに適用）。提案: v1 の範囲外。ヴォルトはプロジェクトの主言語に合わせた単一言語とする。

## これを `obsidian.md` でどう露出するか

ユーザー向けガイドは「ヴォルトを読んでクエリできる」に焦点を絞り続けます。実装が入り次第、末尾の短い「双方向同期」セクションからここへリンクし、1 行サマリ「Obsidian でフィールドを編集すれば再コンパイル後も残ります。完全なモデルは [obsidian-sync.md](obsidian-sync.md) を参照。」を添えます。

それまでの間、`obsidian.md` の既存の読み取り専用免責はそのまま残ります — この設計はロードマップであり、出荷済みの機能ではありません。
