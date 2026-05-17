# 公開チェックリスト

<!-- translations:start -->
<p align="center"><a href="../publishing-checklist.md">English</a> · <a href="publishing-checklist.ko.md">한국어</a> · <a href="publishing-checklist.zh.md">中文</a> · <a href="publishing-checklist.ja.md">日本語</a> · <a href="publishing-checklist.ru.md">Русский</a> · <a href="publishing-checklist.es.md">Español</a> · <a href="publishing-checklist.fr.md">Français</a> · <a href="publishing-checklist.de.md">Deutsch</a></p>
<!-- translations:end -->
Tesserae を公開する前に、このチェックリストを使用してください。

## リポジトリの衛生状態

- [ ] README が、プロジェクトの内容と解決する問題を説明している。
- [ ] インストールコマンドが新しい shell から動作する。
- [ ] Quickstart が `python3 -m` ではなく `tesserae` を使っている。
- [ ] アーキテクチャ文書が raw evidence → graph → projections を説明している。
- [ ] 機能マップが将来作業を誇張せず、実装済み機能を列挙している。
- [ ] セッション履歴ドキュメントが、明示的なインポート、プライバシーレビュー、生成された routes、transcript typography を説明している。
- [ ] Self-dogfood デモが実行され、文書化されている。
- [ ] 生成された成果物が再現可能であり、無視されるか意図的に公開される。

## 検証

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

## デモで話すポイント

- Tesserae は汎用的な名詞句グラフではありません。制御された ontology を使用します。
- 研究コードと開発コードはインフラを共有しますが、別々の schema を保ちます。
- Markdown と HTML は投影であり、権威ある真実の保存場所ではありません。
- デフォルトの経路はローカルで、API key がなくても使いやすいものです。
- エージェント harness と MCP により、コーディングエージェントがグラフを利用できます。
- インポートされた harness セッションページは、transcript の発見を明示的に保ちながら、以前の Claude Code/Codex 作業を検索可能なプロジェクトメモリに変換します。
