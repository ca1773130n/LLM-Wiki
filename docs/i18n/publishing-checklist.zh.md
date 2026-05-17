# 发布检查清单

<!-- translations:start -->
<p align="center"><a href="../publishing-checklist.md">English</a> · <a href="publishing-checklist.ko.md">한국어</a> · <a href="publishing-checklist.zh.md">中文</a> · <a href="publishing-checklist.ja.md">日本語</a> · <a href="publishing-checklist.ru.md">Русский</a> · <a href="publishing-checklist.es.md">Español</a> · <a href="publishing-checklist.fr.md">Français</a> · <a href="publishing-checklist.de.md">Deutsch</a></p>
<!-- translations:end -->
在公开展示 Tesserae 之前使用此检查清单。

## 仓库卫生

- [ ] README 说明项目是什么以及它解决什么问题。
- [ ] 安装命令可在全新的 shell 中运行。
- [ ] Quickstart 使用 `tesserae`，而不是 `python3 -m`。
- [ ] 架构文档解释原始证据 → 图谱 → 投影。
- [ ] 功能图列出已实现的功能，不夸大未来工作。
- [ ] 会话历史文档解释显式导入、隐私审查、生成的 routes 和 transcript typography。
- [ ] Self-dogfood 演示已经运行并记录。
- [ ] 生成的产物可复现，并且要么被忽略，要么有意发布。

## 验证

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -q
./scripts/install.sh --help
tesserae project setup --help
tesserae project compile --help
```

## Self-dogfood

```bash
tesserae project setup \
  --yes \
  --name tesserae_self \
  --source README.md \
  --source docs \
  --source tesserae \
  --source tests \
  --source scripts \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
tesserae project compile
tesserae project sessions list
tesserae project build-site
tesserae project serve --port 8765
```

## 演示要点

- Tesserae 不是通用的名词短语图谱。它使用受控 ontology。
- 研究和开发代码共享基础设施，但保持不同的 schema。
- Markdown 和 HTML 是投影，而不是权威事实存储。
- 默认路径是本地的，并且不需要 API key，易于使用。
- 智能体 harness 和 MCP 让编码智能体可以使用该图谱。
- 导入的 harness 会话页面把之前的 Claude Code/Codex 工作转化为可搜索的项目记忆，同时保持 transcript 发现为显式操作。
