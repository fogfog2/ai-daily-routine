---
name: ai-daily
description: 매일 수행하는 AI 뉴스 수집·요약 및 기능 페이지 갱신 루틴. 사용자가 "오늘 AI 뉴스", "ai-daily 실행", "일일 AI 리포트"를 요청하거나 스케줄러가 이 루틴을 호출할 때 사용한다.
---

# AI Daily 루틴

`ROUTINE.md`의 6단계를 순서대로 수행한다. 아래는 실행용 요약이다.

## 실행 절차

1. **오늘 날짜 확인** 후 `./scripts/new-day.sh` 실행 (파일이 이미 있으면 건너뛴다).

2. **수집** — WebSearch로 최근 24시간 AI 관련 소식을 검색한다.
   서로 다른 3개 이상 각도로 검색할 것:
   - 회사·제품명 (Anthropic, OpenAI, Google DeepMind, Meta AI)
   - 사건 유형 (model release, benchmark, AI regulation)
   - 도메인 (AI coding tools, multimodal, agents)

3. **선별** — `ROUTINE.md`의 점수표로 상위 5~8건을 고른다.
   중복 사건은 가장 1차 출처에 가까운 것만 남긴다.
   후보가 적으면 적은 대로 낸다. 숫자를 채우지 않는다.

4. **심층 확인** — 선별된 항목은 WebFetch로 원문을 연다.
   제목만 보고 요약하지 않는다. 열지 못한 항목은 `(미확인)`으로 표시한다.

5. **작성** — `archive/YYYY-MM-DD.md`에 `ROUTINE.md`의 항목 형식대로 작성한다.
   사실 3줄은 숫자·버전·날짜를 포함하고, `그래서:` 한 줄은 해석으로 분리한다.

6. **빌드 및 배포**
   ```bash
   ./scripts/build-site.sh    # 로컬 site/index.html
   ./scripts/publish.sh       # 게임 서버 public/ai/ 로 내보내기
   ```
   그리고 `RUNLOG.md` 표 맨 아래에 실행 결과 한 줄을 추가한다.

   앱 오프라인 사본까지 갱신해야 하면 `$HOME/src/game/tools/bundle-web.sh` 를
   실행한다. 서버로만 볼 것이면 필요 없다.

   > 클라우드(Claude Code routines)에서 돌 때는 집 서버·게임 저장소가 없다.
   > `build-site.sh` / `publish.sh` 는 건너뛰고, 뉴스는 `archive/` 에 커밋만 한다.
   > 이것은 정상이며 오류로 보고하지 않는다.

7. **기술문서 영향 판정** — 오늘 선별한 항목이 기존 기술문서(49편)를 낡게 만드는지 본다.
   `ai-docs` 스킬의 판정 모드를 이어서 수행한다. 기준은 `DOCS-BACKLOG.md` 에 있다.

   해당하는 것만 대기열에 쌓고 **문서는 고치지 않는다.** 실제 작성은 주간 반영에서 한다.
   해당 없으면 아무것도 하지 않는다 — 대부분의 날은 여기에 해당한다.

## 완료 보고

사용자에게 아래를 보고한다.
- 선별 건수와 분류 구성
- 특히 주목할 항목 1~2개
- 확인 실패했거나 건너뛴 항목이 있으면 명시
- **기술문서 대기열에 추가한 것이 있으면 그 내용** (없으면 없다고)

건수가 평소보다 적으면 그 사실을 그대로 말한다. 채워 넣지 않는다.
