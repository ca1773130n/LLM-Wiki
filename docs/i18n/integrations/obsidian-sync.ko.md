# Obsidian 양방향 동기화 — 제안된 설계

<!-- translations:start -->
<p align="center"><a href="../../integrations/obsidian-sync.md">English</a> · <a href="obsidian-sync.zh.md">中文</a> · <a href="obsidian-sync.ja.md">日本語</a> · <a href="obsidian-sync.ru.md">Русский</a> · <a href="obsidian-sync.es.md">Español</a> · <a href="obsidian-sync.fr.md">Français</a> · <a href="obsidian-sync.de.md">Deutsch</a></p>
<!-- translations:end -->

> **상태: 제안됨 (2026-05-17).** 이 문서는 설계 명세이며 아직 구현된 기능이 아닙니다. LLM-Wiki가 사용자가 Obsidian에서 투영된 위키 페이지를 편집하고, 그 편집이 다음 `project compile`에서도 살아남도록 하는 방법을 설명합니다. 구현은 이 설계가 확정되어야 진행됩니다.

오늘날의 [Obsidian export](obsidian.ko.md)는 엄격히 단방향입니다. `.llm-wiki/graph.json`의 타입 그래프가 vault로 투영되며, `project compile`은 투영된 파일을 덮어씁니다. 사용자들은 그 반대 방향도 요청해 왔습니다 — Obsidian에서 설명을 편집하고, 재컴파일 후에도 그것이 살아남는 것을요.

이 문서는 데이터 모델의 일관성을 해치지 않으면서 그것이 어떻게 작동할지를 명확히 정리합니다.

## 전략적 전환, 분명히 명시하기

현재 README는 라이브 편집을 부인합니다:

> LLM-Wiki는 라이브 편집 대신 소스로부터의 컴파일을 택합니다. UI에서 노트를 편집하고 싶다면 Logseq나 Obsidian을 사용하세요.

양방향 동기화는 일부 필드에 대해 **그 계약을 변경합니다.** 의도적일 가치가 있는 변경입니다. 목표는 "Obsidian이 에디터가 되는 것"이 아니라 — "사용자의 Obsidian 편집이 재컴파일 시 조용히 파괴되지 않는 것"입니다.

## 핵심 아이디어: 병합이 아니라 오버레이

동일 노드의 두 개의 갈라진 사본을 병합하려 하지 말고, vault를 투영 위의 **diff 레이어**로 취급합니다:

```text
source markdown  ──extract──▶  base_graph
                                    +
                              vault_overrides     ◀── computed from vault
                                    ↓
                              final_graph  ──project──▶  vault (.md files)
```

`vault_overrides.json`은 `.llm-wiki/`에 위치하며 작성되는 것이 아니라 **계산되는** 것입니다. 매 컴파일마다 LLM-Wiki는 vault를 순회하면서, 각 투영된 페이지를 이전 투영이 기록한 내용과 비교하고, 사용자가 도입한 모든 변경 사항을 오버레이 항목으로 기록합니다. 최종 그래프는 오버레이가 적용된 `base_graph`입니다. 다음 투영은 그 결과를 디스크에 다시 씁니다.

왕복(round-trip)이 안정적입니다. 소스 측 변경 없이 동일한 vault를 재컴파일하면 어떤 diff도 발생하지 않습니다.

## 필드별 소유권

노드의 각 필드는 소유자를 갖습니다. 소유권은 소스와 vault가 충돌할 때 어떤 일이 일어나는지를 결정합니다.

| 필드 | 소스 소유 | vault 오버라이드 가능 | 비고 |
|---|---|---|---|
| `id`, `type` | 예 | 아니오 | 스키마 제어; 추출기 소유 |
| `name` | 초기값 | 예 | 정규 명칭은 추출기보다 사용자가 더 잘 아는 경우가 많음 |
| `aliases` | 초기값 | 예 | vault로부터는 추가 전용; vault 항목은 항상 보존 |
| `description` | 초기값 | **예** | 가장 흔한 Obsidian 편집 대상 |
| `source_path` | 예 | 아니오 | 출처(provenance); 편집으로 제거 불가 |
| `metadata` (선언된 키) | 초기값 | 예 | 예: `arxiv_id`, `github_repo` — 사용자가 정정 가능 |
| `metadata.user.*` | 해당 없음 | 예 | 사용자 전용 키를 위한 예약 네임스페이스; 추출기는 절대 쓰지 않음 |
| 발신 엣지(타입 부여됨) | 예 | 아니오 | 엣지는 vault가 아닌 온톨로지에 존재 |
| 사용자가 타이핑한 새로운 wikilink | 해당 없음 | 예 | `edge_type=user_link`로 노출되어 그래프에 기록됨 |
| `<!-- user-notes -->` 본문 블록 | 절대 쓰지 않음 | 항상 보존 | 투영기가 절대 건드리지 않는 추가 전용 영역 |

## 충돌 사례와 기본값

| 사례 | 기본값 | 이유 |
|---|---|---|
| vault의 `description`이 재추출된 소스의 `description`과 다름 | **vault 승리**, `.llm-wiki/lint-report.md`의 "diverged fields"에 로그 | 사용자 편집 존중: 사용자가 분명히 의도한 편집임. 감사 흔적이 있어 나중에 검토 가능 |
| 소스 파일이 삭제되었으나 투영된 페이지가 여전히 vault에 남아 있음 | 그래프에서 노드 제거, `.llm-wiki/orphans.md`에 나열 | 존재에 대해서는 소스가 권위; 고아 로그를 통해 복원할지 받아들일지 결정 가능 |
| 사용자가 존재하지 않는 슬러그로 wikilink 작성 | tombstone 노드(타입 `Stub`) 생성, lint 리포트에 노출 | 사용자 의도를 놓치지 않음; 정리 대상으로 표시 |
| 사용자가 스키마가 모르는 frontmatter 키 추가 | `metadata.user.<key>`로 보존, 절대 덮어쓰지 않음 | 타입 그래프를 오염시키지 않으면서 전방 호환성 확보 |
| 서로 다른 머신의 두 vault가 같은 노드를 편집하고, 둘 다 Obsidian Sync로 동기화됨 | **v1에서는 범위 외.** 파일시스템 수준에서 마지막 쓰기 우선. | 진정한 멀티 vault 페더레이션은 Tier 3; 실제 사용 사례가 나올 때까지 보류 |

## 사용자 노트 추가 영역

모든 투영된 페이지는 투영기가 절대 건드리지 않는 펜스로 둘러싸인 영역을 가집니다:

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

두 가지 실용적 효과:
1. 사용자는 어떤 페이지든(예: "내 노트의 4장을 보라") 주석을 달 수 있으며 리빌드 시 잃지 않습니다.
2. pull 단계는 user-notes 블록에서 wikilink를 스캔하여 온톨로지 타입의 `user_link` 엣지로 노출하며, 정식 엣지 타입을 오염시키지 않으면서도 그래프 도달성을 제공합니다.

## 원격 전송 — 명시적 비목표

LLM-Wiki는 동기화 서버, 인증 레이어, 충돌 해결 데몬, 호스팅 vault를 **만들지 않습니다.** 여기서 "양방향"이라는 말은 "컴파일이 vault에서 읽는다"는 뜻이며 — vault를 컴파일을 수행하는 머신까지 어떻게 가져올지는 이미 존재하는 도구로 해결할 사용자의 문제입니다:

| 스택 | 비용 | 비고 |
|---|---|---|
| Obsidian Sync | 유료, 월 $4-8 | E2E 암호화, 공식, 매우 단순 |
| iCloud / Dropbox / OneDrive | OS 번들 | 작동하지만 충돌 UX가 적대적 |
| Syncthing | 무료, 셀프호스팅 | 1인용 다중 기기에 최적 |
| Git (vault를 커밋) | 무료 | 충돌 UX는 기술 사용자에게 최선 |
| LiveSync (CouchDB 플러그인) | 무료, 서버 필요 | 실시간 다중 기기 |

다섯 가지 모두 오버레이 모델과 호환됩니다. LLM-Wiki가 vault를 변경 스트림이 아닌 디스크상의 파일로 보기 때문입니다.

## CLI 인터페이스 (제안)

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

## 단계화

| Tier | 범위 | 공수 |
|---|---|---|
| **1a** | 오버레이 리더: vault 순회, `vault_overrides.json` 생성, 컴파일 시 적용. Lint가 발산을 보고. | 약 3일 |
| **1b** | 사용자 노트 추가 영역: 투영기는 `<!-- user-notes:start --> ... <!-- user-notes:end -->` 블록을 절대 건드리지 않음. | 약 1일 |
| **2** | 감시 모드: 장기 실행 `obsidian-sync --watch`가 파일시스템 이벤트에 따라 오버레이를 재실행하고, 적용 전에 프롬프트를 표시. | 약 1주 |
| **3** | 멀티 vault 페더레이션: 그래프가 vault별 출처를 저장하고, 동기화된 vault 간 동시 편집을 지원. | 약 1개월, 실제 사용 사례 나올 때까지 보류 |

## 비목표 (명시적으로)

- 동기화 서버 / 인증 / 호스팅 백엔드.
- Obsidian 내부에서의 실시간 협업 편집 (필요하면 LiveSync 사용).
- 모든 필드를 왕복시키도록 추출기를 다시 작성하는 일 — 소스 markdown은 오버라이드 테이블 밖의 모든 것에 대해 정규로 유지됨.
- 정적 HTML 사이트의 동기화 (`build-site`는 투영 전용으로 유지).

## 구현 전 미결정 사항

다음 항목들은 제안된 기본값을 가지지만, 코드가 들어가기 전에 최종 점검이 필요합니다:

1. **Lint 리포트 형태.** 발산된 필드는 별도의 `.llm-wiki/diverged-fields.md` 파일로 노출되어야 하나, 아니면 기존 `lint-report.md`의 새 섹션으로 들어가야 하나? 제안: git에서 diff할 수 있도록 전용 파일.
2. **Tombstone 노드 타입.** `Stub`을 실제 스키마 타입으로 추가할지, 아니면 `_kind: stub` 식별자를 가진 `OpenQuestion`에 얹을지? 제안: `Stub`이라는 이름의 실제 타입, 공개 인덱스에서는 숨김.
3. **컴파일 시 pull의 기본값.** 기본 ON, 기본 OFF? 제안: 설정된 경로에 vault가 존재할 때 ON, 사용자가 의도적으로 옵트인하도록 처음 활성화될 때 일회성 확인 프롬프트 표시.
4. **diff를 위한 "이전 투영"은 무엇으로 정의하나?** `.llm-wiki/vault_snapshot.json`에 저장된 스냅샷, 아니면 매 컴파일마다 즉석에서 재투영? 제안: 스냅샷, 매 컴파일 끝에 기록. 더 저렴하고 추출기의 비결정성이 오버레이로 새는 것을 막음.
5. **다국어 vault 투영.** 오늘날의 투영은 단일 언어(소스)입니다. 오버레이가 로케일을 인식해야 하나(예: 한국어 vault 오버레이의 `description` 편집은 한국어 투영에만 적용)? 제안: v1 범위 외; vault는 프로젝트의 주 언어와 일치하는 단일 언어.

## 이것이 `obsidian.md`에는 어떻게 드러나나

사용자 대상 가이드는 "vault를 읽고 쿼리할 수 있다"에 계속 초점을 둡니다. 구현이 완료되면 끝부분의 짧은 "양방향 동기화" 섹션이 한 줄 요약과 함께 여기로 링크할 것입니다: "Obsidian에서 필드를 편집하면 재컴파일 후에도 살아남습니다. 전체 모델은 [obsidian-sync.md](obsidian-sync.md)를 참조."

그때까지는 `obsidian.md`의 기존 읽기 전용 면책 조항이 유지됩니다 — 이 설계는 로드맵이지 출시된 기능이 아닙니다.
