# 클라우드에서 루틴 돌리기 (PC 꺼도 됨)

`claude.ai/code/routines` 에 등록하면 PC 전원과 무관하게 루틴이 실행됩니다.
그러려면 **루틴 본체가 git 에 올라가 있어야** 합니다.

> **왜 지금까지는 안 됐나.** `fogfog2/ai-concepts` 에 올라간 것은 **결과물(HTML)뿐**이었습니다.
> 스킬·카탈로그·생성기 29개·배포 스크립트는 전부 이 PC 에만 있어서,
> 클라우드에서 저장소를 열어도 실행할 것이 없었습니다.

---

## 저장소 두 개의 역할

| 저장소 | 공개 | 내용 | 누가 쓰나 |
|---|---|---|---|
| `fogfog2/ai-concepts` | **Public** | 완성된 HTML 49편 (GitHub Pages) | 방문자 |
| `fogfog2/ai-daily-routine` | **Private** | 스킬·카탈로그·생성기·스크립트 | 루틴 |

분리한 이유는 두 가지입니다. 공개 사이트에 작업 도구가 섞이지 않고,
스킬·스크립트에 들어 있는 **집 경로와 서버 설정이 공개되지 않습니다.**

루틴은 비공개 저장소에서 돌면서, 배포할 때만 공개 저장소를 clone 해 푸시합니다.
`ship-docs.sh` 가 알아서 합니다.

---

## 1단계 — 비공개 저장소 만들기 (직접 해주셔야 합니다)

이 환경에 `gh` CLI 가 없어서 저장소 생성만 사람 손이 필요합니다.

1. https://github.com/new
2. **Repository name**: `ai-daily-routine`
3. **Private** 선택 ← 중요
4. README·.gitignore·license **전부 체크 해제** (이미 있습니다)
5. **Create repository**

만든 뒤 "만들었어" 라고 알려주시면 나머지는 제가 밀어 넣습니다.

---

## 2단계 — 푸시 (제가 함)

```bash
cd ai-daily
git init && git branch -M main
git remote add origin git@github.com:fogfog2/ai-daily-routine.git
git add -A && git commit -m "루틴 본체"
git push -u origin main
```

---

## 3단계 — routines 등록

https://claude.ai/code/routines 에서 **Create routine**.

| 항목 | 값 |
|---|---|
| Repository | `fogfog2/ai-daily-routine` |
| Schedule | 매일 오전 9:37 |
| Prompt | 아래 |

```
ai-daily 루틴을 실행해줘. .claude/skills/ai-daily/SKILL.md 절차를 따르고,
7단계(기술문서 영향 판정)까지 포함해서 오늘 뉴스가 기존 49편 문서를 낡게 만드는지
DOCS-BACKLOG.md 기준으로 판정해 대기열에만 쌓아줘. 문서 자체는 고치지 마.
해당 없으면 없다고 그대로 보고해. 끝나면 변경사항을 커밋·푸시해줘.
```

주간 반영은 별도 루틴으로 하나 더 만듭니다. **토요일 오전 10:23**.

```
ai-docs 반영 모드를 실행해줘. .claude/skills/ai-docs/SKILL.md 의 "주간 — 반영 모드"
절차를 따라. DOCS-BACKLOG.md 에서 우선순위 높음부터 1~2건만 골라 처리하고,
수치는 반드시 직접 계산하거나 1차 출처로 확인한 뒤 작성해.
./scripts/ship-docs.sh 로 검증·배포하고 대기열과 RUNLOG.md 를 갱신해줘.
대기열이 비어 있으면 아무것도 하지 말고 그렇게 보고해.
```

---

## 클라우드에서 달라지는 것

루틴은 두 환경에서 똑같이 돌지만, 클라우드에는 없는 것이 있습니다.
**전부 자동으로 건너뛰도록 처리돼 있습니다.**

| 항목 | 집 PC | 클라우드 | 처리 |
|---|---|---|---|
| 공개 사이트 (`site-pages/`) | 있음 | 없음 | `ship-docs.sh` 가 clone |
| 집 서버 (`~/src/game`) | 있음 | 없음 | `sync-catalog.sh` 가 건너뜀 |
| 앱 오프라인 사본 | 가능 | 불가 | 건너뜀 |
| GitHub Pages 배포 | 가능 | **가능** | SSH 키만 있으면 동일 |

> 클라우드 실행 시 집 서버 `/ai/` 페이지는 갱신되지 않습니다.
> 다음에 PC 를 켜고 `./scripts/sync-catalog.sh` 를 한 번 돌리면 따라잡습니다.

---

## 인증

배포하려면 클라우드 환경에서 `fogfog2` 로 GitHub 에 푸시할 수 있어야 합니다.
routines 설정에서 저장소 접근 권한을 주면, 그 저장소에는 푸시가 됩니다.

다만 **공개 사이트는 다른 저장소**라 별도 권한이 필요합니다.
푸시가 막히면 `ship-docs.sh` 가 검증까지만 하고 멈추므로,
잘못된 내용이 올라가는 일은 없습니다. 실패하면 그때 알려주시면 방법을 찾겠습니다.
