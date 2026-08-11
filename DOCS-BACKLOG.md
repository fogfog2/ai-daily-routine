# DOCS-BACKLOG — 문서 후보 목록

**매일 1편**을 여기서 골라 씁니다. 절차는 [ROUTINE.md](ROUTINE.md) `[B]` 를 따릅니다.

> **고르는 원칙.** 가장 좋은 후보는 **기존 문서가 여러 번 언급했는데 전용 문서가 없는 것**입니다.
> 이미 맥락이 깔려 있어 링크로 이을 곳이 많고, 읽는 사람이 궁금해할 지점이기 때문입니다.
>
> **vision 분야를 우선합니다.**

---

## 후보를 찾는 법

기존 문서 본문에서 자주 나오는데 전용 문서가 없는 주제를 센다.

```bash
python3 - <<'PY'
import re, pathlib, sys
sys.path.insert(0, "scripts")
from catalog import DOCS
slugs = {d[3] for d in DOCS}
txt = "\n".join(p.read_text(encoding="utf-8")
                for p in pathlib.Path("site-pages/docs").glob("*.html"))
for c in ["NMS", "IoU", "ResNet", "U-Net", "Segmentation", "Optical Flow"]:
    n = len(re.findall(re.escape(c), txt, re.I))
    if n and c.lower().replace(" ", "-") not in slugs:
        print(f"{n:>4}  {c}")
PY
```

---

## 태그로 균형 보기

문서마다 태그가 붙어 있으므로 **어느 쪽이 비었는지 숫자로 보인다.**
주제를 고를 때 이 분포를 먼저 확인한다.

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, "scripts")
from catalog import DOCS, TAGS
from collections import Counter
c = Counter(t for d in DOCS for t in d[7])
for g in ("domain", "topic"):
    print(g)
    for t in TAGS:
        if t["group"] == g:
            print(f"   {t['name']:10} {c[t['id']]:2}편")
PY
```

**2026-08-11 기준 — 관심사 대비 비어 있는 곳**

| 태그 | 편수 | 판단 |
|---|---|---|
| `enhance` 화질 개선 | 1편 | 초해상 1편 추가됨. denoise·평가지표·ISP 남음 |
| `feature` 특징·매칭 | 3편 (vision 은 CLIP 1편) | 관심 분야 대비 얇다 |
| `on-device` 온디바이스 | 6편 (vision 은 3편) | 검출 계열에만 붙어 있다 |
| `vision` 도메인 | 11편 (LLM 15편) | 관심 비중과 반대다 |

**고를 때의 원칙**

1. 위 표에서 **0편이거나 관심사 대비 얇은 태그**를 먼저 채운다
2. vision 이 LLM 편수를 따라잡을 때까지 vision 을 우선한다
3. 같은 태그가 연달아 3편 이상 나오지 않게 한다 — 한쪽으로 쏠리면 흐름이 끊긴다

---

## 후보 목록

`언급` = 기존 49편 본문에 등장한 횟수. 많을수록 연결할 곳이 많다는 뜻이다.

### 우선 — vision 기반 (언급 많음)

| 언급 | 주제 | 단계 | 왜 필요한가 | 상태 |
|---|---|---|---|---|
| 33 | **NMS & 중복 제거** | 09 특집 | 검출 문서 6편이 전부 언급하지만 원리·변형(Soft-NMS·NMS-free)을 다룬 곳이 없다 | 대기 |
| 23 | **DINO & 자기증류 시각 표현** | 02 아키텍처 | RF-DETR 백본이자 자기지도 문서에서 언급만 하고 지나간다 | 대기 |
| 14 | **IoU 계열 손실** | 09 특집 | GIoU·DIoU·CIoU 가 검출 성능을 가른 축인데 설명이 없다 | 대기 |
| 9 | **SAM & 프롬프트 분할** | 09 특집 | 분할 자체가 49편에 없다. vision 쪽 큰 결손 | 대기 |
| 9 | **ResNet & 잔차 연결** | 02 아키텍처 | 거의 모든 문서가 전제하는데 정작 설명이 없다 | 대기 |
| 3 | **U-Net & 인코더-디코더** | 02 아키텍처 | 확산 모델이 쓰는 구조인데 별도 설명이 없다 | 대기 |

### 관심사 — 화질 개선 `enhance` (현재 0편)

| 주제 | 단계 | 태그 | 왜 필요한가 |
|---|---|---|---|
| ~~초해상 (Super-Resolution)~~ | 03 학습 | `vision` `enhance` | **완료 2026-08-11** (9b271d6) — 03 학습 단계에 배치 |
| **denoise·복원** | 09 특집 | `vision` `enhance` | 확산 모델이 왜 복원에 잘 맞는지 — 노이즈 제거가 곧 학습 목표였다 |
| **화질 평가 지표** | 08 평가 | `vision` `enhance` `safety` | PSNR·SSIM 이 사람 눈과 어긋나는 지점, LPIPS 가 나온 이유 |
| **ISP 와 학습 기반 파이프라인** | 09 특집 | `vision` `enhance` `on-device` | RAW→RGB 를 신경망이 대체하는 흐름. 온디바이스와 직결 |

### 관심사 — 특징·매칭 `feature` (현재 vision 은 1편)

| 주제 | 단계 | 태그 | 왜 필요한가 |
|---|---|---|---|
| **메트릭 러닝** | 03 학습 | `vision` `feature` | **같은 객체는 가깝게, 다른 객체는 멀게** — 관심사의 핵심. contrastive·triplet·ArcFace |
| **재식별 (Re-ID)** | 09 특집 | `vision` `feature` | 같은 물체를 다른 뷰·다른 카메라에서 같다고 판정하는 문제 그 자체 |
| **지역 특징과 매칭** | 09 특집 | `vision` `feature` | SIFT 에서 SuperPoint·LightGlue 까지. 뷰가 달라도 대응점을 찾는 법 |
| **벡터 검색 (ANN)** | 07 응용 | `common` `feature` `systems` | 뽑은 특징으로 실제 검색하려면 필요. HNSW·IVF-PQ |
| **유사도 임계값 정하기** | 08 평가 | `vision` `feature` `safety` | 같은 품목/다른 품목의 스코어 분포가 겹칠 때 어디서 자를 것인가 |

### 관심사 — 온디바이스 `on-device` (vision 은 검출에만)

| 주제 | 단계 | 태그 | 왜 필요한가 |
|---|---|---|---|
| **경량 백본** | 02 아키텍처 | `vision` `on-device` `arch` | MobileNet·EfficientNet·ShuffleNet. depthwise separable 이 아끼는 것 |
| **NAS 와 하드웨어 인지 설계** | 02 아키텍처 | `vision` `on-device` | FLOPs 가 아니라 실제 지연을 목표로 구조를 찾는 방식 |
| **모바일 추론 런타임** | 07 응용 | `vision` `on-device` `systems` | TFLite·NCNN·CoreML. 연산자 지원 여부가 모델 선택을 정한다 |

### vision — 아직 언급은 적지만 결손

| 주제 | 단계 | 왜 필요한가 | 상태 |
|---|---|---|---|
| **Semantic / Instance / Panoptic 분할** | 09 특집 | 검출은 6편인데 분할은 0편이다 | 대기 |
| **CNN 기초 — 합성곱·풀링·수용영역** | 01 기초 | ViT 문서가 "합성곱 편향"을 논하는데 그 편향의 정체가 설명돼 있지 않다 | 대기 |
| **Optical Flow & 동영상** | 09 특집 | 시간 축이 통째로 빠져 있다 | 대기 |
| **NeRF & 3D 표현** | 09 특집 | 3D 가 없다. Gaussian Splatting 과 묶어도 좋다 | 대기 |
| **ControlNet & 조건부 생성 제어** | 03 학습 | 확산 문서가 CFG 까지만 다룬다 | 대기 |
| **Vision-Language 모델** | 07 응용 | CLIP 이후가 비어 있다 | 대기 |

### 비-vision 결손

| 주제 | 단계 | 왜 필요한가 | 상태 |
|---|---|---|---|
| **Batch Normalization 상세** | 01 기초 | 정규화 문서가 있지만 배치 의존성·추론 동작은 얕다 | 대기 |
| **토크나이저 이후 — 임베딩 검색** | 07 응용 | RAG 문서가 벡터 검색을 전제하는데 설명이 없다 | 대기 |
| **긴 문맥 처리 기법** | 05 추론 | 문맥 확장이 계속 화제인데 다룬 곳이 없다 | 대기 |

---

## 상태 값

- `대기` — 아직 안 씀
- `작업중` — 오늘 작업 대상
- `완료 YYYY-MM-DD` — 커밋 해시 병기
- `보류` — 사유 병기

---

## 다 떨어지면

위 목록이 비면 **새로 채운다.** 아래 순서로 찾는다.

1. 위의 탐색 스크립트를 다시 돌린다 (문서가 늘면 새 언급이 생긴다)
2. 최근 뉴스에서 **6개월 뒤에도 유효할 기반 기술**을 고른다
3. 기존 문서를 읽으며 "이 부분은 따로 한 편이 필요하다" 싶은 곳을 표시한다

**후보가 없다고 문서를 대충 쓰지 않는다.** 그럴 땐 사용자에게 알리고 목록 보강을 제안한다.
