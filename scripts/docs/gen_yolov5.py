#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ec", panel="#e7e5df", ink="#191713", **{
    "ink-soft": "#55503f", "ink-faint": "#847e6b", "rule": "#d3d0c6",
    "rule-strong": "#b0ab9c", "accent": "#7a5310", "accent-fill": "#f0e6cd",
    "accent-line": "#a37725", "muted": "#82868c", "muted-fill": "#dee0e2", "warn": "#a04222",
})
DARK = dict(paper="#12110d", panel="#1b1914", ink="#ebe8df", **{
    "ink-soft": "#aaa593", "ink-faint": "#7d786a", "rule": "#26241c", "rule-strong": "#3c392c",
    "accent": "#d9ad55", "accent-fill": "#2c2411", "accent-line": "#9d7f34",
    "muted": "#888e95", "muted-fill": "#1b1e21", "warn": "#df8355",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>격자 한 칸이 무엇을 책임지는가</h2>
    <p>
      1단계 검출기의 구조는 단순하다. 이미지를 격자로 나누고, 각 칸이 그 근처의 물체를 책임진다.
      YOLOv5는 세 개의 해상도에서 이 일을 한다 — 640 입력이면 <code>80×80</code>, <code>40×40</code>, <code>20×20</code>이다.
      각각 stride 8, 16, 32에 해당하고, 작은 물체는 촘촘한 격자가, 큰 물체는 성긴 격자가 맡는다.
    </p>
    <p>
      칸마다 <strong>앵커</strong>가 3개씩 있다. 앵커는 미리 정해 둔 상자 모양(폭·높이)이고,
      모델은 절대 좌표를 예측하는 대신 <em>앵커로부터 얼마나 벗어났는지</em>를 예측한다.
      맨땅에서 좌표를 맞히는 것보다 훨씬 배우기 쉬운 문제가 된다.
    </p>
    <div class="eq">
      <span class="cap">출력 텐서의 모양 — COCO 80클래스 기준</span>
      <div class="line">각 스케일: (배치, 앵커 3, H, W, 5 + 80)</div>
      <div class="line">           5 = t<sub>x</sub>, t<sub>y</sub>, t<sub>w</sub>, t<sub>h</sub>, objectness</div>
      <div class="line">640 입력 총 예측 수 = (80²+40²+20²) × 3 = <strong>25,200</strong></div>
    </div>
    <p>
      2만 5천 개의 후보 중 실제 물체는 몇 개뿐이다.
      이 압도적 불균형을 어떻게 다루느냐가 1단계 검출기 설계의 핵심이 된다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>디코딩 공식 — v3에서 한 번 고쳐진 곳</h2>
    <p>
      모델의 원시 출력 <code>t</code>를 실제 상자로 바꾸는 식이 YOLOv5의 특징적인 부분이다.
      YOLOv3의 공식과 비교하면 어디를 왜 고쳤는지가 드러난다.
    </p>
    <div class="eq">
      <span class="cap">YOLOv3 → YOLOv5 디코딩</span>
      <div class="line">v3:&nbsp; b<sub>x</sub> = σ(t<sub>x</sub>) + c<sub>x</sub></div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp; b<sub>w</sub> = p<sub>w</sub> · e<sup>t<sub>w</sub></sup></div>
      <div class="line">&nbsp;</div>
      <div class="line">v5:&nbsp; b<sub>x</sub> = (<strong>2·σ(t<sub>x</sub>) − 0.5</strong>) + c<sub>x</sub></div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp; b<sub>w</sub> = p<sub>w</sub> · (<strong>2·σ(t<sub>w</sub>)</strong>)²</div>
    </div>
    <p>
      두 곳이 바뀌었고 이유가 각각 분명하다.
    </p>
    <p>
      <strong>중심 좌표.</strong> v3에서 <code>σ(t<sub>x</sub>)</code>는 <code>(0, 1)</code> 범위라
      물체 중심이 칸 경계에 정확히 놓이면 <code>t<sub>x</sub></code>가 <code>±∞</code>로 발산해야 한다.
      v5는 범위를 <code>(−0.5, 1.5)</code>로 넓혀 <strong>유한한 값으로 경계에 도달</strong>할 수 있게 했다.
      덤으로 한 칸이 자기 영역을 살짝 넘어 예측할 수 있게 되는데, 이것이 다음 절의 라벨 할당과 맞물린다.
    </p>
    <p>
      <strong>폭·높이.</strong> v3의 <code>e<sup>t<sub>w</sub></sup></code>는 상한이 없어
      학습 초기에 값이 폭주할 수 있었다. v5는 <code>(2σ)²</code>로 <strong>0~4배 사이로 제한</strong>한다.
      앵커의 4배를 넘는 상자는 아예 표현할 수 없지만, 그 대가로 학습이 안정된다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>이웃 칸까지 정답으로 인정한다</h2>
    <p>
      어떤 예측을 정답과 짝지을 것인가 — <strong>라벨 할당</strong>이 검출기 성능을 가르는 지점이다.
      YOLOv3까지는 물체 중심이 놓인 칸에서 IoU가 가장 큰 앵커 <strong>하나</strong>만 양성이었다.
      양성 표본이 극도로 적어 학습이 느렸다.
      짝을 지은 다음 그 상자를 어떤 손실로 다듬는지는 또 다른 축인데,
      YOLOv5 이후로는 좌표에 거는 L1 대신 <a href="iou-losses.html">IoU 계열 손실</a>이 표준이 됐다.
    </p>
    <p>
      YOLOv5는 두 가지를 완화한다.
    </p>
    <ul>
      <li><strong>IoU 대신 종횡비로 앵커를 고른다.</strong> 정답 상자와 앵커의 폭·높이 비율이 4배 이내면 매칭으로 인정한다. 조건을 만족하는 앵커가 여럿이면 <em>모두</em> 양성이 된다.</li>
      <li><strong>중심이 놓인 칸의 이웃까지 쓴다.</strong> 중심이 칸의 어느 쪽으로 치우쳤는지 보고, 가까운 이웃 칸 2개를 추가 양성으로 삼는다. 양성 수가 대략 3배가 된다.</li>
    </ul>
    <p>
      두 번째가 앞 절의 <code>(−0.5, 1.5)</code> 범위와 정확히 맞물린다.
      이웃 칸이 자기 영역 밖의 중심을 예측해야 하는데, 확장된 범위가 그것을 가능하게 한다.
      <strong>디코딩 공식과 라벨 할당이 한 세트로 설계된 것</strong>이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="YOLOv5의 라벨 할당 도식. 왼쪽은 물체 중심이 있는 칸 하나만 양성으로 삼는 이전 방식, 오른쪽은 중심 칸에 더해 중심이 치우친 방향의 이웃 칸 두 개까지 양성으로 삼아 양성 표본을 세 배로 늘리는 YOLOv5 방식.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--muted)">v3 — 중심 칸 1개만 양성</text>

            <g stroke="var(--rule)" stroke-width="1">
              <line x1="26" y1="34" x2="206" y2="34"/><line x1="26" y1="94" x2="206" y2="94"/>
              <line x1="26" y1="154" x2="206" y2="154"/><line x1="26" y1="214" x2="206" y2="214"/>
              <line x1="26" y1="34" x2="26" y2="214"/><line x1="86" y1="34" x2="86" y2="214"/>
              <line x1="146" y1="34" x2="146" y2="214"/><line x1="206" y1="34" x2="206" y2="214"/>
            </g>
            <rect x="86" y="94" width="60" height="60" fill="var(--warn)" opacity="0.2"/>
            <rect x="70" y="78" width="92" height="92" fill="none" stroke="var(--ink-soft)" stroke-width="1.4" stroke-dasharray="4 3"/>
            <circle cx="103" cy="111" r="4" fill="var(--warn)"/>
            <text x="116" y="130" font-size="9" fill="var(--warn)">양성 1</text>
            <text x="26" y="232" font-size="9" fill="var(--ink-faint)">중심이 어디 있든 그 칸 하나뿐</text>

            <line x1="246" y1="24" x2="246" y2="230" stroke="var(--rule)" stroke-width="1"/>

            <text x="274" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">v5 — 이웃 칸까지 3개</text>

            <g stroke="var(--rule)" stroke-width="1">
              <line x1="274" y1="34" x2="454" y2="34"/><line x1="274" y1="94" x2="454" y2="94"/>
              <line x1="274" y1="154" x2="454" y2="154"/><line x1="274" y1="214" x2="454" y2="214"/>
              <line x1="274" y1="34" x2="274" y2="214"/><line x1="334" y1="34" x2="334" y2="214"/>
              <line x1="394" y1="34" x2="394" y2="214"/><line x1="454" y1="34" x2="454" y2="214"/>
            </g>
            <rect x="334" y="94" width="60" height="60" fill="var(--accent)" opacity="0.3"/>
            <rect x="274" y="94" width="60" height="60" fill="var(--accent)" opacity="0.15"/>
            <rect x="334" y="34" width="60" height="60" fill="var(--accent)" opacity="0.15"/>
            <rect x="318" y="78" width="92" height="92" fill="none" stroke="var(--ink-soft)" stroke-width="1.4" stroke-dasharray="4 3"/>
            <circle cx="351" cy="111" r="4" fill="var(--accent)"/>

            <text x="304" y="128" font-size="8.5" fill="var(--accent)">이웃</text>
            <text x="352" y="70" font-size="8.5" fill="var(--accent)" text-anchor="middle">이웃</text>
            <text x="364" y="130" font-size="8.5" fill="var(--accent)">중심</text>

            <text x="274" y="232" font-size="9" fill="var(--ink-faint)">중심이 좌·상단으로 치우쳤으므로 그쪽 이웃을 택한다</text>

            <text x="486" y="60" font-size="9.5" fill="var(--ink-soft)">중심 좌표 범위</text>
            <text x="486" y="76" font-size="9" fill="var(--ink-faint)">v3: (0, 1) — 자기 칸 안에서만</text>
            <text x="486" y="92" font-size="9" fill="var(--accent)">v5: (−0.5, 1.5) — 칸 밖까지</text>

            <rect x="486" y="106" width="188" height="1" fill="var(--rule)"/>

            <text x="486" y="128" font-size="9.5" fill="var(--ink-soft)">그래서 이웃 칸이</text>
            <text x="486" y="144" font-size="9" fill="var(--ink-faint)">자기 영역 밖 중심을 예측할 수 있다.</text>
            <text x="486" y="164" font-size="9" fill="var(--accent)">디코딩 범위와 라벨 할당은</text>
            <text x="486" y="178" font-size="9" fill="var(--accent)">한 세트로 설계됐다.</text>

            <text x="486" y="206" font-size="9" fill="var(--ink-faint)">양성 표본 ≈ 3배</text>
            <text x="486" y="220" font-size="9" fill="var(--ink-faint)">→ 수렴이 빨라진다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        양성 표본을 늘리는 것이 YOLOv5 성능 향상의 큰 축이었다.
        다만 이 규칙은 여전히 <strong>사람이 정한 것</strong>이다 — 4배, 이웃 2개 같은 숫자가 손으로 박혀 있다.
        이 마지막 수작업을 학습으로 넘긴 것이 뒤이은 YOLOX의 SimOTA다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>Mosaic — 배치 하나에 네 장면을</h2>
    <p>
      YOLOv5의 성능 상당 부분은 구조가 아니라 <strong>증강</strong>에서 나온다.
      대표가 <strong>Mosaic</strong>이다. 이미지 4장을 무작위 비율로 잘라 한 장으로 붙인다.
    </p>
    <p>
      효과가 여러 겹이다. 한 번의 순전파에 네 장면이 들어가므로
      배치 크기를 키우지 않고도 배치 통계가 다양해진다.
      잘린 물체가 자연스럽게 많이 생기므로 <strong>부분만 보이는 물체</strong>에 강해진다.
      축소되어 붙는 경우가 많아 <strong>작은 물체 표본</strong>이 늘어난다.
    </p>
    <div class="note">
      <b>마지막 에폭에는 Mosaic을 끈다.</b> 합성 이미지는 실제 사진의 분포와 다르다.
      학습 내내 켜 두면 모델이 그 인위적 분포에 맞춰지므로,
      끝에서 10~15 에폭 정도는 증강을 꺼 <em>실제 분포로 되돌린다</em>.
      YOLOX 등 이후 모델들도 이 관행을 그대로 따른다.
    </div>
    <p>
      나머지 증강도 목록은 평범하지만 조합이 공격적이다 —
      HSV 색상 지터, 좌우 반전, 이동·확대·기울임, 그리고 두 이미지를 섞는 MixUp.
      YOLOv5가 "논문 없이 저장소로 발전한 모델"이라 불리는 이유가 여기 있다.
      기여의 상당 부분이 <em>이론적 발견이 아니라 잘 조율된 학습 레시피</em>였다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>다섯 개의 크기, 그리고 s가 기준선이 된 이유</h2>
    <p>
      YOLOv5는 같은 구조를 두 개의 계수로 스케일링해 다섯 모델을 만든다.
      <strong>깊이 계수</strong>는 CSP 블록의 반복 횟수를, <strong>폭 계수</strong>는 채널 수를 곱한다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>모델</th><th>깊이</th><th>폭</th><th>파라미터</th><th>COCO mAP<sub>50-95</sub></th></tr>
        </thead>
        <tbody>
          <tr><td>YOLOv5n</td><td>0.33</td><td>0.25</td><td>1.9M</td><td>28.0</td></tr>
          <tr><td>YOLOv5s</td><td>0.33</td><td>0.50</td><td class="hi">7.2M</td><td class="hi">37.4</td></tr>
          <tr><td>YOLOv5m</td><td>0.67</td><td>0.75</td><td>21.2M</td><td>45.4</td></tr>
          <tr><td>YOLOv5l</td><td>1.00</td><td>1.00</td><td>46.5M</td><td>49.0</td></tr>
          <tr><td>YOLOv5x</td><td>1.33</td><td>1.25</td><td>86.7M</td><td>50.7</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <code>s</code>가 실무의 기본값이 된 데에는 이유가 있다.
      7.2M 파라미터는 임베디드 장비에도 올라가고, 640 입력에서 37.4 mAP는
      대부분의 산업 응용에 충분하며, 무엇보다 <strong>학습이 빠르고 잘 수렴한다</strong>.
      데이터가 수천 장 규모일 때 큰 모델은 과적합하기 쉬운데 <code>s</code>는 그 위험이 적다.
    </p>
    <p>
      구조의 나머지 요소들은 당시 표준의 조합이다 —
      백본은 CSPDarknet(그래디언트 흐름을 두 갈래로 나눠 중복 계산을 줄이는 CSP 구조),
      넥은 PANet(FPN의 하향 경로에 상향 경로를 더해 저수준 위치 정보를 위로 올린다),
      그리고 SPPF(서로 다른 크기의 풀링을 이어 붙여 수용 영역을 넓히되, 직렬화로 속도를 개선한 버전).
    </p>
    <div class="note">
      <b>라이선스는 짚고 넘어가야 한다.</b> Ultralytics YOLOv5는 <strong>AGPL-3.0</strong>이다.
      이 모델을 쓴 서비스를 네트워크로 제공하면 소스 공개 의무가 생길 수 있다.
      상용 배포에는 별도 라이선스가 필요하며, 같은 조건이 YOLOv8·YOLO11에도 적용된다.
      앵커프리 계열인 YOLOX가 <strong>Apache 2.0</strong>이라는 점이 실무 선택에 영향을 주는 이유다.
    </div>
    <p>
      YOLOv5를 한 문장으로 요약하면 이렇다 —
      <em>새 이론 없이, 격자·앵커라는 기존 틀 안에서 디코딩·라벨 할당·증강을 촘촘히 다듬어
      실용성의 기준선을 만든 모델.</em> 다음 세대가 걷어낸 것은 바로 그 틀 자체였다.
    </p>
  </section>
"""

READING = [
    "Jocher et al., <em>Ultralytics YOLOv5</em> (github.com/ultralytics/yolov5) — 논문이 없으므로 저장소와 이슈가 1차 자료다.",
    "Redmon &amp; Farhadi, <em>YOLOv3: An Incremental Improvement</em> (arXiv:1804.02767) — 디코딩 공식과 다중 스케일 예측의 출발점.",
    "Bochkovskiy et al., <em>YOLOv4: Optimal Speed and Accuracy of Object Detection</em> (arXiv:2004.10934) — Mosaic·CSP·PAN 조합의 근거.",
    "Wang et al., <em>CSPNet: A New Backbone that can Enhance Learning Capability of CNN</em> (arXiv:1911.11929) — CSP 구조.",
    "Liu et al., <em>Path Aggregation Network for Instance Segmentation</em> (arXiv:1803.01534) — PANet 넥.",
]

write(
    "yolov5.html",
    title="YOLOv5 — 격자 위에 앵커를 놓다",
    eyebrow="Detection · Anchor-Based One-Stage · 2020",
    h1="YOLOv5",
    subtitle="격자 위에 앵커를 놓다 — 디코딩·라벨 할당·증강의 합",
    dek=(
        "YOLOv5에는 논문이 없다. 새 이론을 제시한 모델이 아니기 때문이다. "
        "대신 격자와 앵커라는 기존 틀 안에서 "
        "<strong>디코딩 공식·라벨 할당·증강 레시피</strong>를 촘촘히 다듬어 "
        "오랫동안 실무의 기준선 노릇을 했다. "
        "그 손으로 박은 규칙들이 다음 세대가 걷어낸 대상이 된다."
    ),
    spec=[
        ("구조", "앵커 기반 1단계"),
        ("예측 수", "25,200 (640 입력)"),
        ("중심 범위", "(−0.5, 1.5)"),
        ("양성 표본", "중심 + 이웃 2칸"),
        ("라이선스", "AGPL-3.0"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
