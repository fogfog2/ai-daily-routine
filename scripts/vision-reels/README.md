# 비전 연구 영상

## 발행 순서와 제작 자료

| 차례 | 문서와 연구 | 길이 | 화면에서 검토할 질문 |
| --- | --- | --- | --- |
| 1 | 깊이 추정 · EndoDA3 | 2분 50초 | 같은 픽셀에서 재투영 깊이, 잔차, 예측 신뢰도가 어떻게 연결되는가? SCARED 표 3에서 비교 가능한 조건은 무엇인가? |
| 2 | RF-DETR · Atto | 1분 50초 | 디코더 0층에서 상위 300개 후보는 어떻게 나오는가? T4 엔진 시간 1.0ms가 포함하는 구간은 어디인가? |
| 3 | 초해상도 · 모바일 INT8 | 2분 35초 | 같은 두 가중치의 반올림 순서를 바꾸면 무엇이 달라지는가? 표 4의 두 행에서 함께 달라진 조건은 무엇인가? |
| 4 | 지역 특징 · LoMa | 2분 15초 | 반복 무늬의 잘못된 대응을 허용 픽셀 반경과 상대 포즈 오차가 각각 어떻게 평가하는가? |
| 5 | 깊이 추정 · EndoStreamDepth | 2분 05초 | 다중 스케일 상태가 이전 프레임의 정보를 다음 프레임으로 어떻게 전달하는가? |

다섯 편의 원문과 장면별 대사는 각 에피소드 JSON에서 관리한다. 영상·자막·시간표 대본·비교 도식은 공개 사이트의 `media/vision/<id>/`에 함께 들어간다. 입력 장면은 합성 예시이며 실측 그래프는 논문 또는 개발사의 공개 수치를 사용한다.

## 후속 두 편의 스토리보드

**LoMa** · 0–23초에 반복 무늬 속 같은 모서리와 한 칸 옆의 모서리를 표시한다. 23–58초에 두 영상의 점 사이에 대응선을 그리며 모호한 질감과 넓은 문맥을 비교한다. 58–104초에는 손으로 대응을 표기한 HardMatch의 평가 방식을 설명하고 추정 기본 행렬에 대한 정답 대응의 에피폴라 오차 허용 폭에 따라 PCK가 바뀌는 예를 계산한다. 104–135초에는 같은 대응의 픽셀 오차와 상대 포즈의 각도 오차를 함께 본다. 합성 예와 벤치마크 값을 구분한다. [연구진의 모델 및 평가 자료](https://www.davnords.com/loma)

**EndoStreamDepth** · 0–24초에 같은 지점의 깊이가 프레임 사이에서 흔들리는 합성 시퀀스를 연다. 24–59초에 다중 스케일의 Mamba 상태가 프레임마다 갱신되는 경로를 표시한다. 59–99초에는 프레임별 최적 스케일의 표준편차로 시간적 안정성을 측정한다. 99–125초에는 그림 4의 시간 일관성 결과와 표 9의 추론 시간 측정 조건을 살펴본다. 합성 깊이 궤적에는 설명용 표기를 넣는다. [MIDL 논문](https://proceedings.mlr.press/v315/li26f.html)

## 재생성

Node.js, FFmpeg, 한글 글꼴(Noto Sans CJK KR), Python 환경에 Supertonic 1.3.1과 로컬 Supertonic 3 모델이 필요하다. 제작 음성은 한국어 F2다. Remotion이 지원하는 Chrome을 직접 지정할 때는 `REMOTION_BROWSER`에 실행 파일 경로를 설정한다.

```sh
npm install
python -m pip install 'supertonic==1.3.1' soundfile numpy
python voice.py /path/to/supertonic-3 /tmp/vision-work endoda3 rf-detr-atto mobile-int8-sr loma endostreamdepth
node render.cjs /tmp/vision-work ../../site-pages/media/vision endoda3 rf-detr-atto mobile-int8-sr loma endostreamdepth
```

`voice.py`는 문장별 음성을 작업 디렉터리에 캐시한다. 대사가 바뀐 문장은 다시 합성한다. 장면 안에서는 문장별 발화 길이에 맞춰 자막을 배치하고, 장면 전체는 편집 시간표에 맞춘다. 영상은 720×1280 H.264/AAC이며 한국어 자막을 영상에 표시한다. WebVTT와 시간표 대본도 따로 제공한다. 저장소 루트에서 `python scripts/build-docs.py`를 실행하면 대상 글의 제목 아래에 영상 패널을 붙인다.
