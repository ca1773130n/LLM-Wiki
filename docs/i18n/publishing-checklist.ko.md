# 게시 체크리스트

<!-- translations:start -->
<p align="center"><a href="../publishing-checklist.md">English</a> · <a href="publishing-checklist.ko.md">한국어</a> · <a href="publishing-checklist.zh.md">中文</a> · <a href="publishing-checklist.ja.md">日本語</a> · <a href="publishing-checklist.ru.md">Русский</a> · <a href="publishing-checklist.es.md">Español</a> · <a href="publishing-checklist.fr.md">Français</a></p>
<!-- translations:end -->
LLM-Wiki를 공개적으로 소개하기 전에 이 체크리스트를 사용하세요.

## 저장소 위생

- [ ] README가 프로젝트가 무엇이며 어떤 문제를 해결하는지 설명한다.
- [ ] 새 shell에서 설치 명령이 동작한다.
- [ ] Quickstart가 `python3 -m`이 아니라 `llm_wiki`를 사용한다.
- [ ] 아키텍처 문서가 원시 증거 → 그래프 → 투영을 설명한다.
- [ ] 기능 맵이 미래 작업을 과장하지 않고 구현된 기능을 나열한다.
- [ ] 세션 기록 문서가 명시적 가져오기, 프라이버시 검토, 생성된 routes, transcript typography를 설명한다.
- [ ] Self-dogfood 데모가 실행되고 문서화되었다.
- [ ] 생성된 아티팩트가 재현 가능하며 무시되거나 의도적으로 게시된다.

## 검증

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -q
./scripts/install.sh --help
llm_wiki project setup --help
llm_wiki project compile --help
```

## Self-dogfood

```bash
llm_wiki project setup \
  --yes \
  --name llm_wiki_self \
  --source README.md \
  --source docs \
  --source llm_wiki \
  --source tests \
  --source scripts \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
llm_wiki project compile
llm_wiki project sessions list
llm_wiki project build-site
llm_wiki project serve --port 8765
```

## 데모 설명 포인트

- LLM-Wiki는 일반적인 명사구 그래프가 아닙니다. 제어된 ontology를 사용합니다.
- 연구 및 개발 코드는 인프라를 공유하지만 서로 다른 schema를 유지합니다.
- Markdown과 HTML은 투영이며, 권위 있는 진실 저장소가 아닙니다.
- 기본 경로는 로컬이며 API 키 없이 사용하기 쉽습니다.
- 에이전트 harness와 MCP는 코딩 에이전트가 그래프를 사용할 수 있게 합니다.
- 가져온 harness 세션 페이지는 transcript 발견을 명시적으로 유지하면서 이전 Claude Code/Codex 작업을 검색 가능한 프로젝트 메모리로 바꿉니다.
