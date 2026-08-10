# 기술문서 10편 제작 계획

## 기준 — 기존 문서에서 추출한 형식

최신작 **FlashAttention**(2026-08-09)이 현재 도달한 수준이며, 이를 기준으로 삼는다.
초기작(Transformer, Diffusion)은 입문 톤이지만 최근작은 훨씬 깊다. **최근 기준을 따른다.**

### 고정 구조

| 요소 | 규격 |
|---|---|
| 제목 | `개념명 — 한 줄 은유` (예: "얼린 가중치 옆에 샛길을 내다") |
| eyebrow | `분야 · 부제 · 연도` (예: `Systems · IO-Aware Attention · 2022–2024`) |
| dek | 통념을 하나 깨뜨리며 시작 ("절반만 맞는 말이다") |
| spec strip | `<dl class="spec">` 핵심 수치 4~5개 |
| 본문 | `<section>` 5개, `<span class="n">01</span>` 번호 |
| 수식 | `.eq` 블록 (mono, 좌측 accent 보더) |
| 그림 | 손으로 쓴 `<svg viewBox>` + `figcaption` (`Fig. N` 태그) |
| 반전 | `.note` — 통념을 뒤집는 한 문단 |
| 각주 | `더 읽을거리` — arXiv 번호 포함 실제 문헌 |
| colophon | `AI Concepts Archive · 자동 생성 학습 노트 · 날짜` |

### 공통 규칙

- 언어: 한국어 서술 + 영어 기술용어 (`code` 태그)
- 문체: **음슴체 아닌 평서체** ("~이다", "~한다"). 경어체 아님
- 폰트: Pretendard 계열 본문 + `ui-monospace` 수식/라벨
- 테마: `:root` 토큰 → `@media (prefers-color-scheme: dark)` → `[data-theme]` 3중 정의
- **팔레트는 편마다 다르게** (Transformer=자주, Archive=청록, Flash=황토)
- backlink 또는 colophon으로 Archive와 연결

---

## 선정한 10개 주제

기존 9편이 다루지 않은 영역을 메운다. 중복 없음을 확인함.

| # | 주제 | 부제 | 왜 이것인가 | 팔레트 방향 |
|---|---|---|---|---|
| 1 | **KV Cache & PagedAttention** | 문맥을 페이지로 관리하다 | Flash가 학습이면 이쪽은 추론. vLLM의 핵심 | 청회색 · 강청 |
| 2 | **Quantization (GPTQ/AWQ)** | 정밀도를 깎아 모델을 옮기다 | LoRA와 짝. 실무 배포 필수 | 강철 · 구리 |
| 3 | **RAG** | 모델 밖에 기억을 두다 | 가장 많이 쓰이는 실전 패턴 | 남색 · 청록 |
| 4 | **Speculative Decoding** | 초안을 쓰고 한 번에 검산하다 | 디코딩 가속. Flash 5절과 연결 | 자주 · 산호 |
| 5 | **BERT & Masked LM** | 빈칸을 메우며 언어를 익히다 | Transformer의 다른 갈래(인코더) | 진녹 · 라임 |
| 6 | **Vision Transformer** | 이미지를 단어처럼 자르다 | CLIP·YOLO와 연결되는 비전 축 | 보라 · 호박 |
| 7 | **Scaling Laws & Chinchilla** | 크기와 데이터의 최적 배분 | MoE·Transformer의 경제학 | 흑연 · 형광노랑 |
| 8 | **Tokenization (BPE)** | 글자와 단어 사이에서 타협하다 | 모든 LLM의 첫 단계, 의외로 미설명 | 세피아 · 진청 |
| 9 | **Batch/Layer Normalization** | 분포를 붙잡아 학습을 안정시키다 | 모든 구조의 기반 부품 | 회청 · 주황 |
| 10 | **Model Context Protocol** | 도구를 모델에 꽂는 규약 | 2024~2026 실무 흐름, 최신성 | 자홍 · 진회 |

### 배치 순서

에이전트 10개를 병렬로 돌리지 않는다 — 팔레트·톤 일관성이 깨진다.
**2편씩 5회**로 나눠 순차 작성하고, 매회 직전 편과 대조한다.

---

## 진행 절차

1. 편별로 HTML 작성 → `Artifact` 발행 → URL 확보
2. `game/public/ai/data/artifacts.json` 에 항목 추가
3. 10편 완료 후 **Archive 페이지 갱신** (기존 9 + 신규 10 = 19 entries)
4. `publish.sh` 불필요 (artifacts.json 직접 수정), `bundle-web.sh` 로 앱 사본 갱신

## 검증 항목

- [ ] 다크/라이트 양쪽에서 대비 확인
- [ ] `viewBox` SVG 가 좁은 화면에서 `overflow-x` 로 스크롤되는지
- [ ] arXiv 번호가 실재하는지 (추측 금지)
- [ ] 기존 9편과 팔레트가 겹치지 않는지
