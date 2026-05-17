# Obsidian — コンパイル済み wiki を本物のヴォルトとして開く

<!-- translations:start -->
<p align="center"><a href="../../integrations/obsidian.md">English</a> · <a href="obsidian.ko.md">한국어</a> · <a href="obsidian.zh.md">中文</a> · <a href="obsidian.ru.md">Русский</a> · <a href="obsidian.es.md">Español</a> · <a href="obsidian.fr.md">Français</a></p>
<!-- translations:end -->

LLM-Wiki の Obsidian エクスポートは、コンパイル済みの型付きグラフを、意見のある本物の [Obsidian](https://obsidian.md) ヴォルトに変換します。単なる markdown のディレクトリではなく、`.obsidian/` 設定、型を意識した [callouts](https://help.obsidian.md/Editing+and+formatting/Callouts)、[Dataview](https://blacksmithgu.github.io/obsidian-dataview/) でクエリ可能な frontmatter、ヴォルトダッシュボード、そしてヴォルト横断の `wiki://` 参照インデックスを備えたヴォルトです。

## 前提条件

まずプロジェクトをコンパイルしてください:

```bash
cd /path/to/your-project
llm_wiki project setup
llm_wiki project compile
```

コンパイルすると `.llm-wiki/graph.json`（信頼できる情報源）と、プレーンな markdown 射影が `.llm-wiki/markdown_projection/` に生成されます。Obsidian エクスポートはこの射影の上に構築されますが、各ページに Obsidian ネイティブのエンリッチメントを重ねます。

## 1) ヴォルトをエクスポートする

```bash
llm_wiki project export-obsidian --vault ~/Documents/llm-wiki-vault
```

ディレクトリが存在しない場合は作成されます。再実行すると冪等に上書きされます — 同じグラフが与えられれば markdown 射影は決定論的です。

ディスク上に何が配置されるか:

```text
llm-wiki-vault/
  .obsidian/                  # Obsidian config (app.json, graph.json, plugins)
  README.md                   # Vault entry point
  index.md                    # All nodes grouped by section
  _bridges.md                 # Cross-vault wiki:// references, grouped by alias
  _meta/
    dashboard.md              # Dataview overview tables
  papers/                     # Paper / Repository / SourceDocument pages
  concepts/                   # Concept / Topic / Field / Method / Algorithm pages
  claims/                     # Claim / OpenQuestion / Evidence pages
  raw/                        # Optional raw-source attachments (created lazily)
```

## 2) ディレクトリを Obsidian で開く

`File → Open vault... → Open folder as vault → ~/Documents/llm-wiki-vault`。

Obsidian は `.obsidian/` を検出して本物のヴォルトとして認識し、読み込みます。コミュニティプラグイン一覧には Dataview が含まれているため、Obsidian は有効化を促します（推奨 — 有効でないと dataview ブロックはコードフェンスとしてレンダリングされます）。

`Settings → Community plugins → Browse → "Dataview" → Install → Enable`。

## 3) ヴォルトを見て回る

### エントリーポイント

- `README.md` — このヴォルトが何であるか、どう更新するか
- `index.md` — セクション（papers、concepts、claims）ごとに wikilink 付きで並んだ全 node
- `_meta/dashboard.md` — dataview の概観: 最近のページ、papers、concepts/claims

### ページごとのエンリッチメント

各 node ページには次が同梱されます:

**型を意識した callouts。** 各ページ先頭のセマンティック callout により、node の type が一目で分かります:

```markdown
> [!quote] Paper
> The paper triggered a wave of follow-on work: SuGaR aligns Gaussians...

> [!warning] Limitation
> No current method can achieve real-time display rates at 1080p...

> [!question] Open question
> How does dynamic-scene reconstruction scale...
```

主なマッピング: `Paper → quote`、`Repository → info`、`Contribution → success`、`Performance → info`、`Limitation → warning`、`Causal → important`、`OpenQuestion → question`、`Evidence → example`。

**Dataview でクエリ可能な edges。** frontmatter には型付き edges がネストしたマップとして格納されます:

```yaml
edges_out:
  uses: [gaussian-splatting, volumetric-rendering]
  part_of: [3d-4d-vision-and-reconstruction]
  supports_claim: [performance-claim-..., comparison-...]
edges_in:
  mentioned_in: [project-pulse, topic-visual-slam]
```

次のようなクエリを書けます:

````markdown
```dataview
LIST FROM "papers" WHERE contains(edges_out.uses, "nerf")
```

```dataview
TABLE edges_out.supports_claim AS "Claims"
FROM "papers"
WHERE length(edges_out.supports_claim) > 3
SORT length(edges_out.supports_claim) DESC
LIMIT 10
```
````

**ヴォルト横断ブリッジ。** node の説明やメタデータで言及された `wiki://<alias>/<kind>/<slug>` URI は、frontmatter フィールドとしても:

```yaml
cross_vault: [wiki://research/concepts/rlhf, wiki://notes/papers/arxiv-2510-12323]
```

`Cross-vault references` 本文セクションとしても露出します。ヴォルトレベルの `_bridges.md` インデックスは、すべての外向き参照を destination alias でグルーピングして集約するため、1 ページからヴォルト横断リンクを監査できます。

**Related (dataview) ブロック。** 各ページの末尾には、リンクバックしているページを自動で表示するクエリが配置されます:

````markdown
```dataview
LIST
FROM "papers" OR "concepts" OR "claims"
WHERE contains(file.outlinks, this.file.link) AND file.name != this.file.name
SORT file.name
LIMIT 25
```
````

### ヴォルトダッシュボード

`_meta/dashboard.md` は最も役立つ集計ビュー（最近更新されたページ、メタデータ列付きの全 paper、type 順にソートされた全 concept と claim）の dataview ブロックを同梱します。自由に編集してください — これは出発点であり、固定された契約ではありません。

### ヴォルトのグラフビュー

Obsidian 組み込みのグラフビュー（`Ctrl/Cmd+G`）は、`## Outgoing` / `## Incoming` セクションに出力された wikilink に対してすでに機能します。同梱の `.obsidian/graph.json` は方向感のために `papers/`、`concepts/`、`claims/` のパスをカラーコード付きにします。より豊かな切り口のために dataview でフィルタしたビューを上に重ねることもできます。

## ヴォルト横断のワークフロー

複数の LLM-Wiki ヴォルトを登録して `wiki://` URI がヴォルト間で解決されるようにします:

```bash
llm_wiki register-project /path/to/research --name research
llm_wiki register-project /path/to/notes    --name notes
```

登録後、各ヴォルトを再エクスポートしてください。各エクスポートの `_bridges.md` には alias でグルーピングされた、ヴォルト間で解決可能な参照が表示されます。

Obsidian 自体は `wiki://` URI をネイティブにたどりません — インラインテキストとしてレンダリングされます — が、`_bridges.md` とページごとの `Cross-vault references` セクションが、専用の Obsidian プラグインが登場するまでの手動インデックスを提供します。

## 更新ワークフロー

Obsidian ヴォルトは型付きグラフの**読み取り専用エクスポート**です。Obsidian での編集は `.llm-wiki/graph.json` には反映されません。新しいソースや修正を取り込むには:

```bash
# Edit source files under your project's source dirs (NOT the vault), then:
llm_wiki project compile
llm_wiki project export-obsidian --vault ~/Documents/llm-wiki-vault
```

Obsidian はディスク上で変更されたファイルをホットリロードします。ヴォルト内にグラフから射影されない markdown メモ（例: 個人的な注釈）を追加してあれば、それらは残ります — エクスポートは自身が所有するファイル（`papers/`、`concepts/`、`claims/` 配下、および `index.md`、`_bridges.md`、`_meta/dashboard.md`、`README.md`）のみを上書きします。

## 静的サイトとの使い分け

コンパイル済みの HTML サイト（`llm_wiki project build-site` → `.llm-wiki/site/`）は共有のためのものです — GitHub Pages、S3、任意の静的ホストへプッシュしてください。Obsidian ヴォルトは Dataview と Obsidian のグラフビューを使って**ローカルで読んでクエリする**ためのものです。両者は同じグラフから射影されるため、ドリフトすることはありません。
