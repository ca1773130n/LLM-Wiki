# Understand Anything 配套工作流

<!-- translations:start -->
<p align="center"><a href="../../integrations/understand-anything.md">English</a> · <a href="understand-anything.ko.md">한국어</a> · <a href="understand-anything.zh.md">中文</a> · <a href="understand-anything.ja.md">日本語</a> · <a href="understand-anything.ru.md">Русский</a> · <a href="understand-anything.es.md">Español</a> · <a href="understand-anything.fr.md">Français</a></p>
<!-- translations:end -->
[Understand Anything](https://github.com/Lum1104/Understand-Anything) 和 LLM-Wiki 是互补项目。

- Understand Anything 擅长生成代码库知识图谱和交互式仪表板。
- LLM-Wiki 专注于长期存在的智能体记忆：文档、markdown/wiki 编译、静态发布、会话历史以及面向智能体的导出。

LLM-Wiki 不应内置或吸收 Understand Anything。应将其视为一个独立的配套工具，用来生成有用的图谱产物。

## 为什么两者都用？

Understand Anything 可以写入：

```text
.understand-anything/knowledge-graph.json
```

该图谱捕获文件、函数、类、模块、概念、依赖、层和导览等代码结构。

随后 LLM-Wiki 可以将该产物与项目记忆的其余部分一起保存：

- 源文档和 markdown 页面；
- 仓库文件；
- 研究笔记；
- 本地 Claude Code / Codex 会话历史；
- 生成的静态 wiki 页面；
- 2D / 3D 图谱网站视图；
- `llms.txt`、`llms-full.txt`、`search-index.json`、`graph.json` 以及每页对应的智能体 sibling。

## 当前低摩擦工作流

推荐路径是设置向导：

```bash
llm_wiki project setup
```

在配套工具步骤中选择 Understand Anything。LLM-Wiki 会在请求时安装/更新配套 skills，并把受管理的刷新命令写入 `.llm-wiki/config.json`。之后调用 `llm_wiki project compile` 时，如果 UA 图谱缺失或过期，就会自动运行该包装命令。

对于非交互式自动化，请使用：

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex
llm_wiki project compile
```

存储的命令由 LLM-Wiki 管理，不需要用户自行构造：

```bash
llm_wiki project refresh-understand-anything --platform codex
```

编译期间，LLM-Wiki 会：

1. 检查 `.understand-anything/knowledge-graph.json` 是否存在，并在元数据可用时确认它与当前 git 提交匹配；
2. 仅当图谱缺失/过期或强制刷新时，运行已配置的智能体平台（`codex`、`opencode` 或 `claude`）；
3. 验证图谱已经写入；
4. 生成 `.llm-wiki/external/understand-anything.md`；
5. 继续正常的记忆编译。

你可以在编译前强制运行所有已配置的外部刷新命令：

```bash
llm_wiki project compile --refresh-external-tools
```

也需要 Cognee？在同一 setup 命令中添加运行时记忆标志：

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

## 手动等效流程

推荐使用受管理的设置路径。如果你有意在 LLM-Wiki 之外使用 UA，请先在你的智能体环境中运行 Understand Anything：

```bash
/understand
```

然后运行 `llm_wiki project setup --with-understand-anything`，让 LLM-Wiki 记录 markdown 投影源。直接的 JSON 文件会保留为原始配套产物，而不是手动输入的源路径。

```bash
llm_wiki project setup --with-understand-anything
llm_wiki project compile
llm_wiki project build-site
```

如果你还想要本地智能体会话记忆：

```bash
llm_wiki project sessions discover --import
llm_wiki project build-site
```

## 可能的未来桥接

未来可选的桥接可以更直接地把 Understand Anything 的图谱 schema 映射到 LLM-Wiki 的 typed graph ontology。

可能的映射：

| Understand Anything | LLM-Wiki 方向 |
|---|---|
| `project` | 仓库/项目元数据 |
| `nodes[type=file]` | 源/文档/文件节点 |
| `nodes[type=function]` | 函数/代码符号节点 |
| `nodes[type=class]` | 类/代码符号节点 |
| `nodes[type=module]` | 模块/包节点 |
| `nodes[type=concept]` | 概念节点 |
| `edges[type=imports]` | import/依赖边 |
| `edges[type=contains]` | 包含边 |
| `edges[type=calls]` | 调用/引用边 |
| `layers[]` | 架构分组元数据 |
| `tour[]` | 入门/综合页面 |

除非两个项目都同意稳定的交换契约，否则请保持该桥接为可选且外部的。

## 协作原则

不要把 LLM-Wiki 描述为 Understand Anything 的替代品。

更好的表述：

- Understand Anything 帮助开发者当下理解代码库。
- LLM-Wiki 帮助智能体长期记忆、搜索、引用、更新并发布项目知识。
