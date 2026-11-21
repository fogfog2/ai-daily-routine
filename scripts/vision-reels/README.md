# 비전 연구 영상

## 발행 순서와 제작 자료

| 차례 | 문서와 연구 | 길이 | 화면에서 검토할 질문 |
| --- | --- | --- | --- |
| 1 | 깊이 추정 · EndoDA3 | 2분 50초 | 같은 픽셀에서 재투영 깊이, 잔차, 예측 신뢰도가 어떻게 연결되는가? SCARED 표 3에서 비교 가능한 조건은 무엇인가? |
| 2 | RF-DETR · Atto | 1분 50초 | 디코더 0층에서 상위 300개 후보는 어떻게 나오는가? T4 엔진 시간 1.0ms가 포함하는 구간은 어디인가? |
| 3 | 초해상도 · 모바일 INT8 | 2분 35초 | 같은 두 가중치의 반올림 순서를 바꾸면 무엇이 달라지는가? 표 4의 두 행에서 함께 달라진 조건은 무엇인가? |
| 4 | 지역 특징 · LoMa | 2분 15초 | 반복 무늬의 잘못된 대응을 허용 픽셀 반경과 상대 포즈 오차가 각각 어떻게 평가하는가? |
| 5 | 깊이 추정 · EndoStreamDepth | 2분 05초 | 다중 스케일 상태가 이전 프레임의 정보를 다음 프레임으로 어떻게 전달하는가? |
| 6 | DETR 계보 · RT-DETRv4 | 2분 25초 | 학습 전용 교사의 특징을 어떤 위치에서 정렬하고, 에폭별 기울기 비율로 증류 가중치를 어떻게 바꾸는가? |
| 7 | 광류 · All-Pairs Correlation | 1분 45초 | 같은 국소 조회 결과를 얻으면서 어떤 상관 타일의 계산과 저장을 줄이는가? |
| 8 | 디블러링 · GyroDVD | 1분 47초 | 회전과 병진 성분을 노출 구간에서 합치면 픽셀의 흐림 궤적이 어떻게 달라지는가? |
| 9 | 노이즈 제거 · 모바일 RAW | 1분 45초 | 이전 프레임을 어떤 위치에서 결합하고 배포 비용을 어떻게 측정하는가? |
| 10 | 분할 · CAR-SAM | 1분 52초 | 4비트 양자화가 양방향 어텐션에 미치는 오차를 어떻게 보정하는가? |
| 11 | HDR 톤 매핑 · FastGaMer | 1분 44초 | 채널별 게인과 국소·전역 보정을 조합하면 어떤 색을 표현할 수 있는가? |
| 12 | ISP · 다중분광 색 보정 | 1분 47초 | RGB가 같을 때 분광 대역을 늘리면 무엇을 구별할 수 있는가? |
| 13 | 점 추적 · Verifier | 1분 55초 | 가림 뒤 두 후보가 갈라질 때 좌표와 가시성을 각각 어떻게 선택하는가? |
| 14 | 가지치기 · NuWa | 1분 51초 | 목표 클래스에 맞춰 중간 채널을 지우면 양쪽 선형층의 연결과 기기 지연은 어떻게 달라지는가? |
| 15 | 3D 가우시안 · SEELE | 1분 56초 | 시점별 선별과 픽셀 그룹의 기여도 검사가 각각 어떤 계산을 줄이는가? |
| 16 | 화질 평가 · PR-IQA | 1분 54초 | 참조 사진과 겹치는 영역과 새로 보인 영역은 어떤 근거로 화질을 판단하는가? |
| 17 | YOLOX · SimOTA | 1분 45초 | 정답 상자 하나에 몇 개의 후보를 배정할까? |
| 18 | NMS · Soft-NMS | 1분 31초 | 겹친 검출 상자의 점수를 얼마나 낮출까? |
| 19 | ViT · 패치 토큰 | 1분 28초 | 사진을 자르는 크기가 어텐션을 얼마나 바꿀까? |
| 20 | CLIP · 제로샷 분류 | 1분 34초 | 사진과 설명문은 어떻게 같은 좌표에서 만날까? |
| 21 | ControlNet · 영 초기화 연결 | 1분 39초 | 윤곽선 조건을 더해도 첫 출력이 그대로인 이유는? |
| 22 | LoRA · BiLaLoRA | 1분 49초 | 안개 제거 모델의 어느 층을 바꿀까? |
| 23 | NAS · 예산 적응형 평가 | 1분 46초 | 후보 모델을 전부 학습하지 않고 어떻게 줄을 세울까? |
| 24 | 온디바이스 양자화 · 기울기 기반 비트 배정 | 1분 48초 | 같은 비트 예산을 어느 층에 더 써야 할까? |
| 25 | Mixture of Experts · MoECLIP | 1분 45초 | 한 장의 검사 이미지에서 패치마다 다른 전문가를 고를까? |
| 26 | 데이터 품질 · 합성 스테레오 | 1분 47초 | 실내에서 잘 맞힌 스테레오가 도로에서 틀리는 이유는? |

스물여섯 편의 원문과 장면별 대사는 각 에피소드 JSON에서 관리한다. 영상·자막·시간표 대본·비교 도식은 공개 사이트의 `media/vision/<id>/`에 함께 들어간다. 입력 장면은 합성 예시이며 실측 그래프는 논문 또는 개발사의 공개 수치를 사용한다.

## 후속 두 편의 스토리보드

**LoMa** · 0–23초에 반복 무늬 속 같은 모서리와 한 칸 옆의 모서리를 표시한다. 23–58초에 두 영상의 점 사이에 대응선을 그리며 모호한 질감과 넓은 문맥을 비교한다. 58–104초에는 손으로 대응을 표기한 HardMatch의 평가 방식을 설명하고 추정 기본 행렬에 대한 정답 대응의 에피폴라 오차 허용 폭에 따라 PCK가 바뀌는 예를 계산한다. 104–135초에는 같은 대응의 픽셀 오차와 상대 포즈의 각도 오차를 함께 본다. 합성 예와 벤치마크 값을 구분한다. [연구진의 모델 및 평가 자료](https://www.davnords.com/loma)

**EndoStreamDepth** · 0–24초에 같은 지점의 깊이가 프레임 사이에서 흔들리는 합성 시퀀스를 연다. 24–59초에 다중 스케일의 Mamba 상태가 프레임마다 갱신되는 경로를 표시한다. 59–99초에는 프레임별 최적 스케일의 표준편차로 시간적 안정성을 측정한다. 99–125초에는 그림 4의 시간 일관성 결과와 표 9의 추론 시간 측정 조건을 살펴본다. 합성 깊이 궤적에는 설명용 표기를 넣는다. [MIDL 논문](https://proceedings.mlr.press/v315/li26f.html)

## 재생성

Node.js, FFmpeg, 한글 글꼴(Noto Sans CJK KR), Python 환경에 Supertonic 1.3.1과 로컬 Supertonic 3 모델이 필요하다. 제작 음성은 한국어 F2다. Remotion이 지원하는 Chrome을 직접 지정할 때는 `REMOTION_BROWSER`에 실행 파일 경로를 설정한다.

```sh
npm install
python -m pip install 'supertonic==1.3.1' soundfile numpy
python voice.py /path/to/supertonic-3 /tmp/vision-work endoda3 rf-detr-atto mobile-int8-sr loma endostreamdepth rt-detr-v4 flow-correlation gyrodvd mobile-raw-denoising car-sam fastgamer spectral-mobile-color verifier-point-tracking nuwa-vit seele-3dgs pr-iqa yolox-simota soft-nms vit-patch-tokens clip-zero-shot controlnet-zero-conv bilalora-dehazing budget-vision-nas gradient-bit-allocation moeclip-patches stereo-training-data
node render.cjs /tmp/vision-work ../../site-pages/media/vision endoda3 rf-detr-atto mobile-int8-sr loma endostreamdepth rt-detr-v4 flow-correlation gyrodvd mobile-raw-denoising car-sam fastgamer spectral-mobile-color verifier-point-tracking nuwa-vit seele-3dgs pr-iqa yolox-simota soft-nms vit-patch-tokens clip-zero-shot controlnet-zero-conv bilalora-dehazing budget-vision-nas gradient-bit-allocation moeclip-patches stereo-training-data
```

`voice.py`는 문장별 음성을 작업 디렉터리에 캐시한다. 대사가 바뀐 문장은 다시 합성한다. 장면 안에서는 문장별 발화 길이에 맞춰 자막을 배치하고, 장면 전체는 편집 시간표에 맞춘다. 영상은 720×1280 H.264/AAC이며 한국어 자막을 영상에 표시한다. WebVTT와 시간표 대본도 따로 제공한다. 저장소 루트에서 `python scripts/build-docs.py`를 실행하면 대상 글의 제목 아래에 영상 패널을 붙인다.
