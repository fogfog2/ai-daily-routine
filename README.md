# AI Daily — Claude 루틴 업무 정리

매일 수행하는 **AI 뉴스 수집 → 요약 → 기능 페이지 생성** 루틴의 전체 정의서입니다.
이 문서 하나로 (1) 루틴이 무엇을 하는지, (2) 어떻게 복제하는지, (3) 작업 과정이 어떻게 기록되는지를 모두 볼 수 있습니다.

---

## 1. 루틴 개요

| 항목 | 내용 |
|---|---|
| 이름 | `ai-daily` |
| 주기 | 매일 1회 (기본 09:00 KST) |
| 입력 | 웹 검색 / 공식 블로그 / 릴리스 노트 |
| 출력 | ① 일자별 마크다운 리포트 ② HTML 기능 페이지 ③ 실행 로그 |
| 실행 주체 | Claude Code (`/ai-daily` 스킬 또는 스케줄러) |

### 하루 한 사이클

```
[1] 수집        웹에서 최근 24시간 AI 뉴스·릴리스 스캔
      ↓
[2] 선별        중복 제거 → 중요도 판정 → 상위 5~8건 확정
      ↓
[3] 심층 확인   각 항목 원문 확인 (제목만 보고 요약 금지)
      ↓
[4] 요약        항목별 3줄 요약 + "그래서 뭐가 달라지나" 한 줄
      ↓
[5] 페이지 생성 archive/YYYY-MM-DD.md + site/index.html 갱신
      ↓
[6] 기록        RUNLOG.md에 실행 결과 1줄 추가
```

각 단계의 판단 기준은 [ROUTINE.md](ai-daily/ROUTINE.md)에 상세히 있습니다.

---

## 2. 폴더 구조

```
ai-daily/
├── README.md                    ← 지금 이 문서 (전체 개요)
├── ROUTINE.md                   ← 단계별 상세 작업 지침
├── RUNLOG.md                    ← 매일 실행 기록 (작업 과정 추적)
├── .claude/
│   └── skills/ai-daily/
│       └── SKILL.md             ← /ai-daily 슬래시 커맨드 정의
├── scripts/
│   ├── new-day.sh               ← 오늘자 리포트 뼈대 생성
│   └── build-site.sh            ← archive/*.md → site/index.html 빌드
├── archive/
│   └── YYYY-MM-DD.md            ← 일자별 뉴스 리포트
└── site/
    └── index.html               ← 기능 페이지 (누적 뷰)
```

---

## 3. 복제 방법

### 방법 A — 폴더 통째로 복사 (가장 빠름)

```bash
cp -r /home/sj/src/study/ai-daily /path/to/new-project
cd /path/to/new-project
rm -rf archive/*.md RUNLOG.md      # 기존 기록 비우기
./scripts/new-day.sh               # 첫 날짜 파일 생성
```

`.claude/skills/ai-daily/`가 함께 복사되므로, 새 폴더에서 Claude Code를 열면
`/ai-daily`가 **그대로 동작**합니다. 별도 설정 불필요.

### 방법 B — 다른 주제로 변형

주제만 바꿔 재사용하려면 두 곳만 수정합니다.

1. `ROUTINE.md`의 **수집 대상 소스** 목록
2. `.claude/skills/ai-daily/SKILL.md`의 `description` 및 검색 키워드

예시 — "AI" 대신 "반도체" 루틴으로:

```bash
cp -r ai-daily semiconductor-daily
cd semiconductor-daily
# ROUTINE.md의 소스 테이블, SKILL.md의 키워드를 반도체로 교체
```

### 방법 C — 매일 자동 실행

Claude Code에서 아래를 입력하면 스케줄이 등록됩니다.

```
/schedule 매일 오전 9시에 ai-daily 폴더에서 /ai-daily 실행
```

수동 확인용으로는 `/loop`도 사용 가능합니다.

---

## 4. 작업 과정 확인 방법

루틴이 "무엇을 했는지"는 세 곳에서 확인합니다.

| 보고 싶은 것 | 볼 파일 |
|---|---|
| 오늘 무슨 뉴스를 골랐나 | `archive/2026-08-08.md` |
| 며칠째 돌고 있나, 실패한 날은 | `RUNLOG.md` |
| 누적 결과를 한 화면에 | `site/index.html` (브라우저) |
| 각 단계에서 어떻게 판단하나 | `ROUTINE.md` |

`RUNLOG.md`는 매 실행마다 한 줄씩 append 되어, 루틴의 연속성과 누락일을 즉시 드러냅니다.

---

## 5. 게임 서버로 링크 배포 (`/ai/`)

`/home/sj/src/game` 의 서버·앱 구조를 **그대로 재사용**합니다. 새 서버를 띄우지 않습니다.

### 동작 방식

```
study/ai-daily/archive/*.md
        │  ./scripts/publish.sh
        ▼
game/public/ai/data/*.json      ← server.js 가 이미 public/ 을 정적 서빙
        │
        ├── 웹  http://<서버>:8080/ai/
        └── 앱  WebView 가 $base/ 를 열고, 허브의 AI DAILY 카드로 진입
```

기존 서버가 `public/` 전체를 서빙하므로 **server.js 수정이 전혀 없습니다.**
앱도 `$base/` 를 로드하므로 Dart 코드 변경이 없습니다.

### 배포

```bash
cd /home/sj/src/study/ai-daily
./scripts/publish.sh                  # archive/*.md → game/public/ai/data/*.json
cd /home/sj/src/game && node server.js # 서버 실행 (이미 떠 있으면 생략)
```

접속 주소는 앱의 서버 탐색 후보와 동일합니다.

| 위치 | 주소 |
|---|---|
| 이 PC | `http://localhost:8080/ai/` |
| 같은 WiFi | `http://<집 LAN IP>:8080/ai/` |
| 집 밖 (Tailscale) | `http://<Tailscale IP>:8080/ai/` |

> 실제 주소는 `ip addr` / `tailscale ip` 로 확인하세요.
> 저장소에 적어두지 않습니다 — 비공개라도 굳이 남길 이유가 없습니다.

### 오프라인(앱 내장) 사본까지 갱신

```bash
cd /home/sj/src/game && ./tools/bundle-web.sh
```

`public/` 을 앱 assets 로 복사합니다. `pubspec.yaml` 에 `assets/web/ai/` 와
`assets/web/ai/data/` 를 이미 등록해 두었습니다 — 빠뜨리면 **오프라인일 때만**
페이지가 안 열리므로 bundle 스크립트가 검사해 막습니다.

### 화면 구성

- **날짜 탭** — 최근 14일치 뉴스. `data/index.json` 기준.
- **🧩 기술문서 탭** — 기술 문서를 **파이프라인 6단계**로 묶어 보여줍니다.

뉴스가 아직 없어도 기술문서 탭은 정상 동작합니다(서로 독립).

---

## 6. 기술문서 분류 체계

### 왜 파이프라인 단계인가

분류 후보를 셋 놓고 골랐습니다.

| 안 | 문제 |
|---|---|
| 도메인별 (언어/비전/생성) | Transformer·MoE·Normalization은 도메인 무관. ViT는 비전이자 아키텍처 — **겹침이 심함** |
| 난이도별 (입문/중급/심화) | 주관적이고 문서가 늘 때마다 재조정 필요 |
| **파이프라인 단계별** ✅ | 겹침이 거의 없고, **순서 자체가 읽는 순서**가 됨 |

모델이 만들어져 서비스되기까지의 순서라 한 문서가 정확히 한 단계에 속합니다.
위에서부터 읽으면 하나의 흐름이 되고, 실무자는 필요한 단계로 바로 갈 수 있습니다.

### 9단계 · 49편

| # | 단계 | 성격 | 편수 |
|---|---|---|---|
| 01 | 기초 | 모든 모델의 밑바닥 부품 | 4 |
| 02 | 아키텍처 | 무엇을 쌓을 것인가 | 7 |
| 03 | 학습 | 어떤 과제로 가르칠 것인가 | 7 |
| 04 | 적응·정렬 | 학습된 모델을 길들이기 | 6 |
| 05 | 추론 최적화 | 같은 모델을 싸고 빠르게 | 6 |
| 06 | 학습 인프라 | 어떻게 굴리는가 | 3 |
| 07 | 응용·시스템 | 실제로 쓰이는 형태 | 6 |
| 08 | 평가·안전 | 잘 됐는지 어떻게 아는가 | 4 |
| 09 | 특집 — 객체 검출 | 손으로 정하던 것을 학습으로 | 6 |

> 이전 분류(12개)는 19편 중 **7개가 1편짜리**라 사실상 분류로 기능하지 못했습니다.
> 지금은 1편짜리 분류가 없습니다.
>
> 06·08 단계는 나중에 신설했습니다. 기존 7단계가 *모델을 만드는 과정*만 다뤄
> **어떻게 굴리는가**(분산 학습·정밀도·메모리)와
> **잘 됐는지 어떻게 아는가**(평가·환각·보안·해석)가 통째로 비어 있었기 때문입니다.

### 문서 추가 방법

`scripts/catalog.py` 가 **단일 출처**입니다. `DOCS` 에 한 줄 추가하고 동기화합니다.

```python
("제목", "부제", "artifact-uuid", "slug", "단계id", "한 줄 요약", "2026-08-11"),
```

`artifact-uuid` 는 claude.ai 아티팩트에서 출발한 문서만 갖습니다.
**직접 쓴 문서는 빈 문자열**(`""`)로 두면 됩니다 — 검증에서 제외되고,
바깥에서 열리는 링크는 공개 사이트 주소로 대체됩니다.

```bash
./scripts/sync-catalog.sh          # 검증 → artifacts.json + archive.html + 네비 주입
cd /home/sj/src/game && ./tools/bundle-web.sh   # 앱 오프라인 사본
```

`sync-catalog.sh` 는 **중복 UUID·중복 slug·slug 형식·미정의 단계 참조·빈 단계**를 자동으로 잡습니다.

> `artifacts.json` 을 직접 편집하지 마세요 — 다음 동기화 때 덮어써집니다.

### 문서 본문 작성

49편 전부가 사이트에 **직접 수록**되어 있어, 외부 아티팩트 링크에 의존하지 않습니다.
생성기는 `scripts/docs/` 에 있습니다.

| 파일 | 역할 |
|---|---|
| `build.py` | 팔레트 + 본문 → 완성 HTML. `site-pages/docs/` 로 바로 씁니다 |
| `_shell.css` | 전 편 공통 CSS (편마다 다른 것은 팔레트와 본문뿐) |
| `check.py` | 태그 균형 · 테마 3중 정의 · SVG 접근성 · 미정의 CSS 변수 |
| `gen_<주제>.py` | 편별 생성기 — 팔레트·본문·읽을거리 |

```bash
cd scripts/docs
python3 gen_lora.py                       # 렌더
python3 check.py ../../site-pages/docs/lora.html   # 점검
```

문서 포맷은 **번호 절 · `.eq` 수식 블록 · 손으로 짠 SVG + `figcaption` ·
`.note` 강조 · arXiv 인용 · 편별 팔레트 · 평서체**입니다.
소스가 남아 있으므로 나중에 수치나 서술을 고칠 때 생성기를 수정해 다시 렌더하면 됩니다.

---

## 7. 외부 공개 사이트 (GitHub Pages)

테일스케일·집 서버 없이 **어디서나 접속되는** 공개 사이트입니다.

**https://fogfog2.github.io/ai-concepts/**

| | 집 서버 `/ai/` | 공개 사이트 |
|---|---|---|
| 접속 | 같은 WiFi 또는 테일스케일 | 어디서나 |
| 첫 화면 | 최신 뉴스 | 기술 문서 |
| 게임·대시보드 | 있음 | 없음 |
| PC 꺼지면 | 접속 불가 | 정상 동작 |

소스는 [site-pages/](site-pages/) 이고 저장소는 `fogfog2/ai-concepts` 입니다.

### 갱신 방법

```bash
./scripts/sync-catalog.sh                    # 세 곳 동시 갱신
cd site-pages && git add -A && git commit -m "문서 갱신" && git push
```

푸시 후 1~2분이면 반영됩니다.

---

## 8. 기술문서 최신성 유지 루틴

문서 49편을 계속 최신으로 두기 위한 루틴입니다. **두 개의 주기로 나눠 돕니다.**

### 왜 매일 쓰지 않는가

Transformer 문서의 내용은 어제 모델이 나왔다고 달라지지 않습니다.
기술문서는 일간 주기의 대상이 아니라서, 매일 한 편씩 채우면 분량만 늘고 질이 떨어집니다.

일간으로 의미 있는 것은 **신호 수집**입니다. 그 신호가 쌓여 임계에 닿았을 때만 문서를 건드립니다.

| 주기 | 하는 일 | 문서를 고치는가 |
|---|---|---|
| **일간** (뉴스 직후) | 오늘 소식이 기존 문서를 낡게 만드는지 판정 → 대기열에 축적 | ✗ |
| **주간** | 대기열에서 우선순위 높은 1~2건을 실제로 작성·갱신·배포 | ✓ |

대기열이 비면 **아무것도 하지 않습니다.** 그것이 정상 결과입니다.

### 구성 요소

| 파일 | 역할 |
|---|---|
| `.claude/skills/ai-docs/SKILL.md` | 루틴 정의 (판정 모드 / 반영 모드) |
| `.claude/skills/ai-daily/SKILL.md` | 뉴스 루틴 7단계에서 판정을 이어받음 |
| `DOCS-BACKLOG.md` | 판정 기준 + 대기열 + 재등록 방법 |
| `scripts/ship-docs.sh` | 검증 5단계 → 커밋 → 푸시 |

### 배포 게이트

`ship-docs.sh` 는 **하나라도 실패하면 커밋하지 않고 멈춥니다.**
사람이 눈으로 확인하지 않는 자동 루틴이라는 전제로 짰습니다.

```
1. 카탈로그 검증      중복 slug · 미정의 단계 · 빈 단계
2. 동기화             artifacts.json · archive.html · 네비 주입
3. 문서 점검          태그 균형 · 테마 3중 정의 · SVG 접근성 · 미정의 CSS 변수
4. 내부 상호링크      깨진 링크 0건인지
5. 유출 스캔          내부 IP · 로컬 경로 · 키 (공개 저장소이므로 필수)
```

```bash
./scripts/ship-docs.sh --dry-run "메시지"   # 검증까지만
./scripts/ship-docs.sh "메시지"             # 통과하면 커밋·푸시
```

### 실행

```
ai-daily 실행해줘                      # 뉴스 + 문서 영향 판정
기술문서 갱신해줘                       # 대기열에서 골라 작성·배포
ai-daily 와 ai-docs 스케줄 등록해줘      # 자동 실행 (세션 종속)
```

> **스케줄은 세션에 종속됩니다.** Claude Code 의 cron 은 세션이 끝나면 사라지고 7일 뒤 만료됩니다.
> 스킬 자체는 파일이라 남으므로, 새 세션에서 위 마지막 줄만 다시 말하면 복구됩니다.

---

## 9. 빠른 시작

```bash
cd /home/sj/src/study/ai-daily
./scripts/new-day.sh      # 오늘자 뼈대 생성
# Claude Code에서 → /ai-daily
./scripts/build-site.sh   # 페이지 갱신
```
