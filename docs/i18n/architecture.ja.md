<!-- translations:start -->
<p align="center"><a href="../architecture.md">English</a> · <a href="architecture.ko.md">한국어</a> · <a href="architecture.zh.md">中文</a> · <a href="architecture.ja.md">日本語</a> · <a href="architecture.ru.md">Русский</a> · <a href="architecture.es.md">Español</a> · <a href="architecture.fr.md">Français</a> · <a href="architecture.de.md">Deutsch</a></p>
<!-- translations:end -->
＃ 建築

LLM-Wiki は、ソース素材のディレクトリを制御された型付きナレッジ グラフに変換し、耐久性のあるマークダウン Wiki レイヤーを介してグラフを作成し、静的で AI フレンドリーな Web サイトを作成するプロジェクトを作成します。 2026 年 4 月の再設計では、Karpathy の 3 層モデルを中心にシステムが再編成されました。生の証拠は生のままで、型付きグラフがオントロジーを管理し、マークダウン Wiki レイヤーがグラフとレンダリングされた出力の間に配置されます。静的サイトは、[`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) 内の制御されたオントロジーをスキーマとして使用し、グラフの直接ダンプではなく、その Wiki レイヤーの *レンダラー* になりました。

## Karpathy の 3 層モデル

Andrej Karpathy による LLM フレンドリーなナレッジ ベースの構成は 3 つの層に分かれており、それぞれに独自の耐久性が保証されています。

|レイヤー |懸念事項 |リポジトリの場所 |オーナー |
|---|---|---|---|
| L1 — 生のソース |ユーザーが作成または収集したリテラル バイト。追加のみ。 | `data/`、`docs/`、`.llm-wiki/config.json` で参照されるプロジェクト ツリー |ユーザー |
| L2 — ウィキ | YAML フロントマターを使用した型付きマークダウン ページ (ソース、コンセプト、エンティティ、論文、リポジトリ、トピック、合成、質問)。冪等: コンパイルごとに再生成されますが、コンテンツのハッシュが変更された場合にのみ書き換えられます。 | `.llm-wiki/wiki/` | `WikiPageStore`、`WikiLayerProjector`、`SynthesisProjector` |
| L3 — レンダリング済み |静的 HTML サイト、AI 兄弟エクスポート、検索インデックス、サイトマップ、JSON-LD。コンパイルごとに消去および再書き込みされますが、再実行後もバイトは安定しています。 | `.llm-wiki/site/` | `StaticSiteBuilder` (`llm_wiki/site/`) |

スキーマは、別個の軸として 3 つのレイヤーすべてにまたがっています。`graph.json` の `ResearchGraph` は、L2 ページがリンクする制御されたオントロジーであり、[`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) の `ResearchNodeType` / エッジ ホワイトリストは、そもそもどのようなタイプが存在するのかの信頼できる情報源です。

再設計により、L2 が明示的に追加されました。 2026 年 4 月以前は、静的サイトは `graph.json` から直接投影されていました。 wiki レイヤーは Obsidian ボールト エクスポート内にのみ存在していました。それを分割すると次のようになりました。

- 人間が編集可能な単一のサーフェス (Obsidian または任意のマークダウン エディターで `.llm-wiki/wiki/` を開きます)。
- 冪等なリビルド: `project compile` を再実行すると、ソース コンテンツが変更されない限り、ファイルの差分はゼロになります。
- 進化ログ: 合成ページは時間の経過とともに蓄積され、プロジェクト自体が物語るようになります。

## パイプライン

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

すべてのステップは段階的に行われます。グラフ抽出プログラムは、`manifest.json` コンテンツ ハッシュを使用して、変更されていないソース ファイルをスキップします。本体ハッシュがすでにディスク上にあるものと一致する場合、`WikiPageStore.write_page` は `False` を返します (書き込みをスキップします)。 `StaticSiteBuilder` は `.llm-wiki/site/` を消去して書き換えますが、その出力は決定的です。以下の「冪等性の話」を参照してください。

## モジュールマップ

### Wiki + 総合 (L2)

|モジュール |責任 |
|---|---|
| [`llm_wiki/wiki_store.py`](../../llm_wiki/wiki_store.py) | `WikiPage` データクラス、ファイルシステム I/O の場合は `WikiPageStore`。 Stdlib 専用の YAML サブセット フロントマター パーサー。ボディハッシュ冪等性。 |
| [`llm_wiki/wiki_projector.py`](../../llm_wiki/wiki_projector.py) | `WikiLayerProjector`: Wiki レイヤー タイプの各 `ResearchGraph` ノードを、適切な `kind/` フォルダー内のマークダウン ページにマップします。 |
| [`llm_wiki/synthesis.py`](../../llm_wiki/synthesis.py) | `SynthesisProjector`: パルス、デイリーダイジェスト、ウィークリー、トピック、比較、フィールド概要の決定的テンプレート。 `Synthesis` ノードと `synthesizes` / `summarizes` エッジをグラフに追加します。 |

### グラフ + オントロジー

|モジュール |責任 |
|---|---|
| [`llm_wiki/research_graph.py`](../../llm_wiki/research_graph.py) | `ResearchNodeType` 列挙型 (`SYNTHESIS` を含む)、エッジタイプのホワイトリスト (`synthesizes`、`summarizes` を含む)、検証。 |
| [`llm_wiki/canonicalization.py`](../../llm_wiki/canonicalization.py) |エイリアスの正規化 + ほぼ重複したレビュー キュー。 |
| [`llm_wiki/code_graph.py`](../../llm_wiki/code_graph.py) |開発スライス用の決定論的 Python AST エクストラクター。 |
| [`llm_wiki/llm_extractor.py`](../../llm_wiki/llm_extractor.py) | Claude CLI/OAuth 選択的エクストラクター。 |

### サイトレンダラー (L3)

|モジュール |責任 |
|---|---|
| [`llm_wiki/site/__init__.py`](../../llm_wiki/site/__init__.py) | `StaticSiteBuilder.write_site`: サイトをワイプ + 再構築し、すべてのルートを歩き、エクスポート + AI 兄弟 + マニフェストを生成します。 |
| [`llm_wiki/site/pages.py`](../../llm_wiki/site/pages.py) |ルートごとに 1 つのレンダラー (ホーム、インデックス、詳細ページ、タイムライン、グラフ、概要)。 `SiteContext` は事前計算されたインデックスを保持するため、レンダラーは純粋な状態を保ちます。 |
| [`llm_wiki/site/components.py`](../../llm_wiki/site/components.py) | HTML プリミティブ: `breadcrumbs`、`card`、`badge`、`node_table`、`edge_list`、`sparkline_svg`、`heatmap_svg`、`toc`、`page_shell`、`ai_siblings_footer`。 |
| [`llm_wiki/site/tokens.py`](../../llm_wiki/site/tokens.py) |デザイントークン — CSS変数、ライトテーマとダークテーマ、レイアウト、タイポグラフィー、ここでスタイル設定されたすべてのコンポーネント。 |
| [`llm_wiki/site/js.py`](../../llm_wiki/site/js.py) |クライアント JS バンドル: 検索パレット、テーマ切り替え、シグマ + 3D フォース グラフ ビュー。 |
| [`llm_wiki/site/markdown.py`](../../llm_wiki/site/markdown.py) | Stdlib 専用のマークダウン レンダラー (リンク、自動リンク、コード、強調、見出し)。外部依存性はありません。 |
| [`llm_wiki/site/relevance.py`](../../llm_wiki/site/relevance.py) |すべての `Related` セクションで使用される 4 つのシグナル関連性スコアリング (ダイレクト リンク、ソース オーバーラップ、Adamic-Adar、タイプ アフィニティ)。 |
| [`llm_wiki/site/search.py`](../../llm_wiki/site/search.py) | `search-index.json`ビルダー。 Wiki レイヤーの種類のみ。 |
| [`llm_wiki/site/sessions.py`](../../llm_wiki/site/sessions.py) |インポートされたハーネス履歴のセッション インデックス/詳細レンダラー: プロジェクト メモリ概要セクション、会話ターン レール、マークダウン トランスクリプト レンダリング、および折りたたまれたツール使用ブロック。 |
| [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) | `llms.txt`、`llms-full.txt`、`graph.jsonld`、`sitemap.xml`、`rss.xml`、`robots.txt`、`ai-readme.md`、ページごとの `.txt`/`.json` の兄弟。 |

### パイプラインオーケストレーション

|モジュール |責任 |
|---|---|
| [`llm_wiki/project.py`](../../llm_wiki/project.py) | `ProjectWiki.compile`: ドライブ抽出 → グラフ → Wiki レイヤー → サイト。 `ProjectPaths`（`config`、`graph`、`manifest`、`wiki`、`site`など）所有。 |
| [`llm_wiki/cli.py`](../../llm_wiki/cli.py) | `compile`、`build-site`、`serve`、`watch`、`deploy` を含む、すべての `llm_wiki project …` サブコマンド。 |
| [`llm_wiki/deploy.py`](../../llm_wiki/deploy.py) | `project deploy`: ワークツリー経由で `.llm-wiki/site/` を `gh-pages` ブランチにプッシュし、オプションで `gh` 経由でページを有効にします。 |

### 外部アダプター (今回は変更なし)

|モジュール |責任 |
|---|---|
| [`llm_wiki/obsidian_adapter.py`](../../llm_wiki/obsidian_adapter.py) | Obsidian ボールト投影 (グラフの色分け、データビュー ダッシュボード、生のアセット)。 |
| [`llm_wiki/agent_harness.py`](../../llm_wiki/agent_harness.py) | Claude コード / Codex / Gemini / Kiro / Cursor / OpenCode ハーネスのエクスポート。 |
| [`llm_wiki/harness_sessions.py`](../../llm_wiki/harness_sessions.py) |インバウンド Claude コード/Codex セッションの検出、正規化、`.llm-wiki/harness_sessions/` での保存、および編集されたマークダウンの概要。 |
| [`llm_wiki/graphiti_adapter.py`](../../llm_wiki/graphiti_adapter.py) |時間的事実の JSONL + オプションのライブ Graphiti 同期。 |
| [`llm_wiki/cognee_adapter.py`](../../llm_wiki/cognee_adapter.py) | Cognee ノード/エッジ JSONL バンドルと直接追加/認識パス。 |
| [`llm_wiki/mcp_server.py`](../../llm_wiki/mcp_server.py) | `schema`、`graph_summary`、`search_nodes`、`node_context`、`search_facts`、`timeline` を公開する MCP stdio サーバー。 |

## プロジェクトワークスペースのレイアウト

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

各ファイルは手動で編集できます。次のコンパイルでは、本体ハッシュがプロジェクターが書き込むものと異なる限り、ユーザーの編集が尊重されます。 (本文のみの編集が有効です。フロントマターの編集は次のコンパイル時に失われます。これは、フロントマターが再生成されるためです。) Obsidian ユーザーは、`.llm-wiki/wiki/` を直接開くことができます。既存の `obsidian_vault/` アダプターは別個の投影であり、代替品ではありません。

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

## 意図的に除外されたもの

再設計では、明示的な境界線が引かれました。 コード クラス ノードとコード関数ノードは `graph.json` に残ります (つまり、MCP、Cognee、Graphiti のコンシューマーには引き続き表示されます) が、HTML ページを取得したり、`search-index.json` に表示されたり、ナビゲーションに表示されたりすることはありません。これがユーザー側の契約です。Wiki はドキュメントファーストの知識ベースであり、関数ブラウザーではありません。

具体的には、`StaticSiteBuilder` は、タイプが L2 wiki 種類マップ (`llm_wiki/wiki_projector.py::_KIND_FOR_TYPE`) にないノードをスキップします。

- L2 + L3 から除外: `CodeClass`、`CodeFunction`、`CodeModule`、`Dependency`、`EvidenceSpan`、`SourceFile`、すべての `Claim` バリアント (`Claim`、`ContributionClaim`、`PerformanceClaim`、`ComparisonClaim`、`LimitationClaim`、`CausalClaim`)。
- それらが引き続き表示される場所を表示します: 箇条書き、バッジ、近隣カウント、または証拠の抜粋として、関連する Wiki ページのインラインで、および下流のツール用に `graph.json` で表示されます。

コードレベルの参照が必要な場合は、LSP / コールグラフ ツールをソース ツリーに直接指定します。これは、「このプロジェクトが知っていることの Wiki」とは別の問題です。

## 冪等性の話

再設計は、*変更されていない入力に対する 2 つの連続した `project compile` 実行でバイトが同一の出力**を目指しています。ピース:

1. **ソース抽出**では、`manifest.json` コンテンツ ハッシュを使用します。変更されていないファイルはスキップされるため、グラフは安定したままになります。
2. **Wiki レイヤーの書き込み**は本体レベルで冪等です。 `WikiPageStore.write_page` は、既存のファイルを読み取り、フロントマターを削除し、ボディを sha256 で実行し、新しいボディのハッシュが同じであれば、新しいフロントマターの `generated_at` タイムスタンプが異なる場合でもショートサーキットします。これは、リビルド時に git diff を厳密に保つための重要なトリックです。
3. **合成出力** は前付に `content_hash: sha256-…` を持ちます。本体ハッシュは `generated_at` を使用せずに計算されるため、同じグラフでコンパイルを繰り返すと同じハッシュが生成され、`Synthesis` ノードはグラフ メタデータに同じ `content_hash` を保持します。
4. **サイト レンダリング** は、`write_site` の開始時に `site/` をワイプし、決定的に書き込みます。ルートはソートされ、辞書は `sort_keys=True` でダンプされ、`manifest.json` は `sorted(rglob("*"))` を経由してウォークされます。 2 回実行すると、マニフェストを含むバイト同一のファイルが生成されます。

これは、`tests/test_site_pages.py` および `tests/test_project_e2e_redesign.py` のエンドツーエンド スモークによって検証されます (コンパイルを 2 回、サイトの差分を行い、ファイル デルタはゼロであると予想されます)。

## スケーリングノート

- **グラフ ビュー ノード キャップ** [`MAX_GRAPH_NODES = 1500`](../../llm_wiki/site/pages.py) は、インタラクティブなフォース レイアウトのページ埋め込みペイロードを制限します。ノードが 1500 を超えると、ミッドレンジのハードウェアではブラウザ側のシミュレーションが遅くなるため、ノード数が上限を超えると、ページは最初に最下位の wiki レイヤー ノードを削除します。エクスポートされた `graph.json` は影響を受けません。常に完全なグラフが含まれています。コード ノードは、キャップが適用される前にフィルターで除外されます。
- **`llms-full.txt` の上限。** 5 MB の安全上限は [`llm_wiki/site/exports.py`](../../llm_wiki/site/exports.py) に適用されます。キャップに達すると、ファイルは `[TRUNCATED — see graph.jsonld for the full set]` マーカーで終わります。 JSON-LD コンシューマは完全なセットを期待しているため、`graph.jsonld` には上限がありません。
- **検索インデックス。** Wiki レイヤーの種類のみ。コードグラフ ノードが `search-index.json` に入ることはありません。再設計の目標はドッグフード コーパスの 500 KB 未満であり、現在はそれを大きく下回っています。
- **ページごとのバイト予算 (経験則)。** 各詳細ページ < 60 KB gz HTML、共有 CSS < 30 KB、共有 JS < 25 KB、グラフ ページのシグマ ベンダーのみ (~60 KB)。グラフ ビューは 3D-force-graph + Three.js を 1 回ロードして使用します。他のページはすべてバニラのままです。
- **dogfood でのコンパイル時間。** 最近の開発マシンでは、最大 300 個のマークダウン ファイルが 5 秒以内に抽出されます。サイトのレンダリングではさらに約 2 秒が追加されます。 wiki 層の冪等性は、後続のコンパイルが変更されたパスのみに影響することを意味します。

## フロントエンド インタラクション サーフェス

- **検索パレット** — `cmd+k` / `ctrl+k` / `/`。 Wiki の種類に限定された、`search-index.json` に対するあいまい一致。最近のページは `localStorage` に残りました。
- **テーマの切り替え** — 右上のボタン; `data-theme="dark"` は `localStorage` に保存され、フラッシュを避けるためにペイント前に適用されます。
- **右に貼り付けられた目次** — デスクトップのみ。モバイルでは `<details>` ドロワーに折りたたまれます。ページ本文の `<h2>` / `<h3>` から生成されます。
- **アクティビティ ヒートマップ** — 月と曜日のラベルが付いた 26 週間の SVG。セルは、その日の `digest.md` ソース ページが存在する場合、そのページにリンクします。 (日ごとのタイムライン詳細ページ — `/timeline/<YYYY-MM-DD>.html` — は明示的なフォローアップです。`render_timeline` のインライン通知でフラグが立てられます。⚠ 進行中です。)
- **グラフ表示** — `/graph/`。ホバー ツールチップ、エッジ ラベル、カーソル アンカー ズーム、および 2D フォールバック ビューを備えた 3D フォース レイアウト (3d-force-graph + Three.js)。ノードの色は `ResearchNodeType` から取得されます。
- **モバイル シェル** — ドロワー レール、ボトム ナビゲーション、流体タイプ、タッチセーフ ヒット ターゲット (≥ 44 ピクセル)。

## テスト戦略

- **ユニット** — `tests/test_wiki_store.py`、`tests/test_synthesis.py`、`tests/test_site_components.py`、`tests/test_site_pages.py`、`tests/test_site_exports.py`、`tests/test_relevance.py`。
- **冪等** — `tests/test_project_e2e_redesign.py` は 2 回コンパイルされ、`wiki/` と `site/` の差分がゼロであるとアサートされます。
- **リンクの整合性** - `tests/test_frontend.py` は、出力されたすべての HTML を href に対して解析し、すべての内部リンクが生成されたファイルに解決されることをアサートします。 `nodes/codeclass-*.html`は生産しておりません。
- **AI 兄弟** — すべての `path/foo.html` について、テスト スイートは `path/foo.txt` と `path/foo.json` が存在することをアサートします。 JSON は解析され、`{title, kind, body, links}` が含まれます。
- **Playwright なし** — `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` でのバニラ pytest。

## 関連ドキュメント

- [クイックスタート](quickstart.ja.md) — `project init` から閲覧可能なサイトまでの最小パス。
- [フロントエンド再設計ウォークスルー](frontend-redesign.ja.md) — すべてのルートの注釈付きツアー。
- [機能マップ](feature-map.ja.md) — 出荷されたもの、進行中のもの、ファイル ポインター付き。
- [Self-dogfood デモ](self-dogfood.ja.md) — 独自のリポジトリに対して LLM-Wiki を実行します。
