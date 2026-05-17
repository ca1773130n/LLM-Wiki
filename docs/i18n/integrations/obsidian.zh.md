# Obsidian —— 把编译好的 wiki 作为真正的 vault 打开

<!-- translations:start -->
<p align="center"><a href="../../integrations/obsidian.md">English</a> · <a href="obsidian.ko.md">한국어</a> · <a href="obsidian.ja.md">日本語</a> · <a href="obsidian.ru.md">Русский</a> · <a href="obsidian.es.md">Español</a> · <a href="obsidian.fr.md">Français</a> · <a href="obsidian.de.md">Deutsch</a></p>
<!-- translations:end -->

LLM-Wiki 的 Obsidian 导出会把你编译好的类型化图谱转化为一个真正的、有明确风格的 [Obsidian](https://obsidian.md) vault。不是一个普通的 markdown 目录 —— 而是带有 `.obsidian/` 配置、类型感知的 [callouts](https://help.obsidian.md/Editing+and+formatting/Callouts)、可被 [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) 查询的 frontmatter、vault 仪表盘，以及跨 vault `wiki://` 引用索引的完整 vault。

## 先决条件

先编译项目：

```bash
cd /path/to/your-project
llm_wiki project setup
llm_wiki project compile
```

编译会产出 `.llm-wiki/graph.json`（真理之源）以及位于 `.llm-wiki/markdown_projection/` 的普通 markdown 投影。Obsidian 导出在该投影之上构建，并在每个页面叠加 Obsidian 原生的增强信息。

## 1) 导出 vault

```bash
llm_wiki project export-obsidian --vault ~/Documents/llm-wiki-vault
```

如果目录不存在会自动创建。重复运行会幂等地覆盖 —— 在相同图谱下，markdown 投影是确定性的。

落到磁盘上的内容如下：

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

## 2) 用 Obsidian 打开该目录

`File → Open vault... → Open folder as vault → ~/Documents/llm-wiki-vault`。

Obsidian 会检测到 `.obsidian/`，把它识别为真正的 vault 并加载。社区插件列表里包含 Dataview，Obsidian 会提示你启用（建议启用 —— 不启用的话 dataview 块会被渲染成普通代码块）。

`Settings → Community plugins → Browse → "Dataview" → Install → Enable`。

## 3) 巡览 vault

### 入口

- `README.md` —— 这个 vault 是什么，以及如何刷新
- `index.md` —— 按区块（papers、concepts、claims）列出的每一个节点，并附带 wikilinks
- `_meta/dashboard.md` —— dataview 总览：近期页面、papers、concepts/claims

### 每页的增强

每个节点页面现在都自带：

**类型感知的 callouts。** 页面顶部的语义 callout 让节点类型一目了然：

```markdown
> [!quote] Paper
> The paper triggered a wave of follow-on work: SuGaR aligns Gaussians...

> [!warning] Limitation
> No current method can achieve real-time display rates at 1080p...

> [!question] Open question
> How does dynamic-scene reconstruction scale...
```

映射关系（节选）：`Paper → quote`、`Repository → info`、`Contribution → success`、`Performance → info`、`Limitation → warning`、`Causal → important`、`OpenQuestion → question`、`Evidence → example`。

**可被 Dataview 查询的边。** Frontmatter 现在以嵌套映射的形式承载类型化的边：

```yaml
edges_out:
  uses: [gaussian-splatting, volumetric-rendering]
  part_of: [3d-4d-vision-and-reconstruction]
  supports_claim: [performance-claim-..., comparison-...]
edges_in:
  mentioned_in: [project-pulse, topic-visual-slam]
```

你可以写出这样的查询：

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

**跨 vault 桥接。** 节点描述或元数据中提到的任何 `wiki://<alias>/<kind>/<slug>` URI，都会同时以 frontmatter 字段的形式被浮现出来：

```yaml
cross_vault: [wiki://research/concepts/rlhf, wiki://notes/papers/arxiv-2510-12323]
```

也会以一节 `Cross-vault references` 的形式出现在正文中。vault 级别的 `_bridges.md` 索引会把每一条对外引用按目标别名聚合，让你可以从一个页面上审计所有跨 vault 链接。

**Related（dataview）块。** 每个页面以一条查询作为结尾，自动列出反向链接到本页的页面：

````markdown
```dataview
LIST
FROM "papers" OR "concepts" OR "claims"
WHERE contains(file.outlinks, this.file.link) AND file.name != this.file.name
SORT file.name
LIMIT 25
```
````

### Vault 仪表盘

`_meta/dashboard.md` 自带最实用的几个聚合视图的 dataview 块：最近更新的页面、所有 paper 及其元数据列、所有 concepts 和 claims 按类型排序。你可以随意修改它 —— 它只是一个起点，而不是固定契约。

### Vault 图谱视图

Obsidian 内置的图谱视图（`Ctrl/Cmd+G`）已经能直接读取 `## Outgoing` / `## Incoming` 区块里写出的 wikilinks。预置的 `.obsidian/graph.json` 会按 `papers/`、`concepts/`、`claims/` 路径着色，方便定位。你可以在上面叠加经 dataview 过滤的视图，获得更细的切片。

## 跨 vault 工作流

注册多个 LLM-Wiki vault，让 `wiki://` URI 能跨 vault 解析：

```bash
llm_wiki register-project /path/to/research --name research
llm_wiki register-project /path/to/notes    --name notes
```

注册之后重新导出每个 vault。导出后的 `_bridges.md` 会按别名分组，显示 vault 之间可解析的引用。

Obsidian 本身不会原生跟随 `wiki://` URI —— 它们会被渲染成内联文本 —— 但 `_bridges.md` 加上每页的 `Cross-vault references` 区块，在专用 Obsidian 插件出现之前，可以充当一份手工索引。

## 刷新工作流

Obsidian vault 是类型化图谱的 **只读导出**。在 Obsidian 中的编辑不会回流到 `.llm-wiki/graph.json`。要纳入新的源或修正：

```bash
# Edit source files under your project's source dirs (NOT the vault), then:
llm_wiki project compile
llm_wiki project export-obsidian --vault ~/Documents/llm-wiki-vault
```

Obsidian 会热重载磁盘上变更的文件。如果你在 vault 里添加了一些并非从图谱投影出来的 markdown 笔记（例如你自己的个人批注），它们会被保留 —— 导出只覆盖它自己拥有的文件：`papers/`、`concepts/`、`claims/` 下的页面，以及 `index.md`、`_bridges.md`、`_meta/dashboard.md` 和 `README.md`。

## 何时用它、何时用静态站点

编译产出的 HTML 站点（`llm_wiki project build-site` → `.llm-wiki/site/`）适合 **分享** —— 推到 GitHub Pages、S3 或任意静态主机。Obsidian vault 则适合在本地配合 Dataview 和 Obsidian 图谱视图 **阅读和查询**。两者都从同一个图谱投影出来，因此永远不会发生漂移。
