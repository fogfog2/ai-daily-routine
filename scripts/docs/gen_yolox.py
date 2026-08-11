#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eef0f0", panel="#e3e7e6", ink="#121817", **{
    "ink-soft": "#4a5553", "ink-faint": "#798482", "rule": "#ccd2d1",
    "rule-strong": "#a8b0ae", "accent": "#0f6b62", "accent-fill": "#d5eae6",
    "accent-line": "#2a8b80", "muted": "#82888c", "muted-fill": "#dde1e2", "warn": "#a1442a",
})
DARK = dict(paper="#0e1211", panel="#161b1a", ink="#e3eae8", **{
    "ink-soft": "#a0aba8", "ink-faint": "#6f7a77", "rule": "#202726", "rule-strong": "#364040",
    "accent": "#48cbb8", "accent-fill": "#0f2a27", "accent-line": "#2e8d80",
    "muted": "#868d90", "muted-fill": "#191f1e", "warn": "#df8258",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>앵커가 실제로 요구했던 것들</h2>
    <p>
      앵커는 좌표 예측을 쉽게 만들어 준 대신 <strong>사람이 정해야 할 것들</strong>을 잔뜩 만들었다.
      YOLOX는 이것들을 하나씩 걷어낸 모델이다. 먼저 앵커가 요구한 목록을 보자.
    </p>
    <ul>
      <li><strong>앵커 크기와 종횡비.</strong> 보통 학습 데이터에 k-means를 돌려 정한다. 도메인이 바뀌면 다시 정해야 한다 — 사람 검출용 앵커로 위성 사진의 차량을 잡기 어렵다.</li>
      <li><strong>매칭 임계값.</strong> IoU 몇 이상을 양성으로 볼 것인가. 0.5인가 0.7인가.</li>
      <li><strong>예측 개수.</strong> 칸마다 앵커 3개면 예측 수도 3배다. 대부분은 배경이다.</li>
      <li><strong>도메인 이식성.</strong> 앵커 설계가 데이터셋에 묶여 있어 일반화가 나쁘다.</li>
    </ul>
    <p>
      앵커프리는 이 모두를 없앤다. 격자 한 칸이 <strong>예측 하나</strong>를 내고,
      상자는 그 지점에서 <em>네 변까지의 거리</em>로 표현한다.
      앵커 크기도, 종횡비도, IoU 임계값도 사라진다.
    </p>
    <div class="eq">
      <span class="cap">앵커프리 디코딩 — 격자점에서 네 변까지의 거리</span>
      <div class="line">각 격자점 (c<sub>x</sub>, c<sub>y</sub>) 에서 (l, t, r, b) 를 예측</div>
      <div class="line">x<sub>1</sub> = c<sub>x</sub> − l,&nbsp;&nbsp; y<sub>1</sub> = c<sub>y</sub> − t</div>
      <div class="line">x<sub>2</sub> = c<sub>x</sub> + r,&nbsp;&nbsp; y<sub>2</sub> = c<sub>y</sub> + b</div>
      <div class="line">예측 수: 25,200 → <strong>8,400</strong> (640 입력, 1/3)</div>
    </div>
    <p>
      논문의 실측으로는 앵커프리 전환만으로 파라미터와 GFLOPs가 줄고
      AP는 오히려 소폭 올랐다. 앵커는 <strong>필요악이 아니라 그냥 짐이었다</strong>는 결론이다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>머리를 나눈다 — 두 과제는 다른 것을 본다</h2>
    <p>
      YOLOv5까지는 분류와 회귀가 <strong>같은 특징 맵</strong>을 공유하고 마지막 1×1 합성곱에서만 갈라졌다.
      YOLOX는 이를 두 갈래로 완전히 분리한다.
    </p>
    <p>
      근거는 두 과제가 요구하는 특징이 다르다는 데 있다.
      <strong>분류</strong>는 "이게 무엇인가"이므로 위치가 조금 틀려도 되고 의미적 특징이 중요하다.
      <strong>회귀</strong>는 "경계가 정확히 어디인가"이므로 위치 민감도가 핵심이다.
      한 특징 맵으로 둘을 동시에 만족시키려 하면 서로를 방해한다.
    </p>
    <div class="note">
      <b>수렴 속도가 눈에 띄게 달라진다.</b> 논문은 decoupled head가 AP를 올릴 뿐 아니라
      <em>학습 곡선이 훨씬 빨리 올라간다</em>고 보고한다.
      대가는 연산량이 조금 늘어난다는 것인데, 1×1 합성곱으로 채널을 먼저 줄인 뒤
      두 갈래로 나누는 방식으로 그 증가를 억제했다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>SimOTA — 라벨 할당을 계산으로 넘기다</h2>
    <p>
      YOLOX의 진짜 기여는 앵커프리도 decoupled head도 아니다.
      <strong>어떤 예측을 정답에 배정할 것인가</strong>를 사람이 정한 규칙 대신
      <em>손실 기반 계산</em>으로 푼 것이다.
    </p>
    <p>
      기존 방식은 전부 고정 규칙이었다 — "중심이 있는 칸", "IoU 0.5 이상", "이웃 2칸".
      그런데 좋은 배정은 상황에 따라 다르다.
      물체가 겹쳐 있으면 어느 예측이 어느 물체를 맡아야 할지가 간단하지 않고,
      큰 물체는 많은 예측이 필요하지만 작은 물체는 그렇지 않다.
    </p>
    <p>
      SimOTA는 이것을 <strong>할당 문제</strong>로 본다. 예측과 정답 사이의 비용을 정의하고,
      비용이 낮은 쌍을 고른다. 비용은 분류 손실과 회귀 손실의 합이다.
    </p>
    <div class="eq">
      <span class="cap">SimOTA — 비용과 동적 k</span>
      <div class="line">c<sub>ij</sub> = L<sup>cls</sup><sub>ij</sub> + λ · L<sup>reg</sup><sub>ij</sub>&nbsp;&nbsp;&nbsp;(λ = 3)</div>
      <div class="line">&nbsp;</div>
      <div class="line">1) 정답 j 주변의 후보만 남긴다 (중심 영역 필터)</div>
      <div class="line">2) k<sub>j</sub> = Σ (상위 10개 후보의 IoU) 를 정수로 절단 &nbsp;← <strong>동적</strong></div>
      <div class="line">3) 비용이 낮은 순으로 k<sub>j</sub> 개를 정답 j 에 배정</div>
      <div class="line">4) 한 예측이 두 정답에 걸리면 비용이 낮은 쪽만 남긴다</div>
    </div>
    <p>
      2번이 핵심이다. <strong>몇 개를 배정할지를 데이터가 정한다.</strong>
      정답 상자와 잘 맞는 후보가 많다면(IoU 합이 크다면) 그만큼 많이 배정하고,
      적으면 적게 배정한다. 큰 물체에는 자연스럽게 많은 양성이, 작은 물체에는 적은 양성이 간다.
      사람이 "이웃 2칸"이라고 박아둘 필요가 없다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 240" role="img" aria-label="정적 라벨 할당과 SimOTA의 비교. 정적 할당은 물체 크기와 무관하게 고정된 개수의 예측을 배정하지만, SimOTA는 후보들의 IoU 합으로 배정 개수를 물체마다 다르게 정해 큰 물체에는 많이, 작은 물체에는 적게 배정한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--muted)">정적 할당 — 크기와 무관하게 같은 규칙</text>

            <rect x="26" y="32" width="150" height="110" fill="none" stroke="var(--rule)" stroke-width="1"/>
            <rect x="44" y="48" width="76" height="76" fill="none" stroke="var(--ink-soft)" stroke-width="1.3" stroke-dasharray="4 3"/>
            <text x="82" y="42" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">큰 물체</text>
            <circle cx="82" cy="86" r="3.4" fill="var(--warn)"/>
            <circle cx="70" cy="74" r="3.4" fill="var(--warn)"/>
            <circle cx="94" cy="74" r="3.4" fill="var(--warn)"/>
            <text x="132" y="90" font-size="9" fill="var(--warn)">3개</text>

            <rect x="26" y="150" width="150" height="76" fill="none" stroke="var(--rule)" stroke-width="1"/>
            <rect x="66" y="172" width="30" height="30" fill="none" stroke="var(--ink-soft)" stroke-width="1.3" stroke-dasharray="4 3"/>
            <text x="82" y="166" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">작은 물체</text>
            <circle cx="81" cy="187" r="3.4" fill="var(--warn)"/>
            <circle cx="71" cy="178" r="3.4" fill="var(--warn)"/>
            <circle cx="91" cy="178" r="3.4" fill="var(--warn)"/>
            <text x="132" y="192" font-size="9" fill="var(--warn)">3개</text>

            <text x="26" y="238" font-size="9" fill="var(--ink-faint)">사람이 정한 숫자가 그대로 적용된다</text>

            <line x1="216" y1="24" x2="216" y2="234" stroke="var(--rule)" stroke-width="1"/>

            <text x="244" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">SimOTA — 데이터가 개수를 정한다</text>

            <rect x="244" y="32" width="164" height="110" fill="none" stroke="var(--rule)" stroke-width="1"/>
            <rect x="262" y="48" width="86" height="86" fill="none" stroke="var(--accent-line)" stroke-width="1.4" stroke-dasharray="4 3"/>
            <text x="305" y="42" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">큰 물체 — IoU 합 큼</text>
            <circle cx="305" cy="91" r="3.4" fill="var(--accent)"/>
            <circle cx="290" cy="76" r="3.4" fill="var(--accent)"/>
            <circle cx="320" cy="76" r="3.4" fill="var(--accent)"/>
            <circle cx="290" cy="106" r="3.4" fill="var(--accent)"/>
            <circle cx="320" cy="106" r="3.4" fill="var(--accent)"/>
            <circle cx="305" cy="61" r="3.4" fill="var(--accent)"/>
            <text x="364" y="94" font-size="9" fill="var(--accent)">k = 6</text>

            <rect x="244" y="150" width="164" height="76" fill="none" stroke="var(--rule)" stroke-width="1"/>
            <rect x="290" y="174" width="28" height="28" fill="none" stroke="var(--accent-line)" stroke-width="1.4" stroke-dasharray="4 3"/>
            <text x="304" y="166" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">작은 물체 — IoU 합 작음</text>
            <circle cx="304" cy="188" r="3.4" fill="var(--accent)"/>
            <text x="364" y="192" font-size="9" fill="var(--accent)">k = 1</text>

            <text x="244" y="238" font-size="9" fill="var(--accent)">k_j = Σ(상위 10 후보의 IoU) — 물체마다 다르다</text>

            <rect x="440" y="40" width="234" height="1" fill="var(--rule)"/>
            <text x="440" y="34" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">비용 행렬로 푸는 배정</text>

            <text x="440" y="60" font-size="9" fill="var(--ink-faint)">c = L_cls + 3 · L_reg</text>

            <g>
              <rect x="440" y="72" width="30" height="20" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="455" y="86" text-anchor="middle" font-size="8" fill="var(--accent)">0.2</text>
              <rect x="474" y="72" width="30" height="20" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
              <text x="489" y="86" text-anchor="middle" font-size="8" fill="var(--ink-faint)">1.8</text>
              <rect x="508" y="72" width="30" height="20" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="523" y="86" text-anchor="middle" font-size="8" fill="var(--accent)">0.4</text>
              <rect x="542" y="72" width="30" height="20" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
              <text x="557" y="86" text-anchor="middle" font-size="8" fill="var(--ink-faint)">2.1</text>

              <rect x="440" y="96" width="30" height="20" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
              <text x="455" y="110" text-anchor="middle" font-size="8" fill="var(--ink-faint)">1.5</text>
              <rect x="474" y="96" width="30" height="20" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
              <text x="489" y="110" text-anchor="middle" font-size="8" fill="var(--accent)">0.3</text>
              <rect x="508" y="96" width="30" height="20" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
              <text x="523" y="110" text-anchor="middle" font-size="8" fill="var(--ink-faint)">1.9</text>
              <rect x="542" y="96" width="30" height="20" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="1"/>
              <text x="557" y="110" text-anchor="middle" font-size="8" fill="var(--ink-faint)">2.4</text>
            </g>
            <text x="584" y="86" font-size="8.5" fill="var(--ink-faint)">← 정답 1</text>
            <text x="584" y="110" font-size="8.5" fill="var(--ink-faint)">← 정답 2</text>

            <text x="440" y="140" font-size="9" fill="var(--ink-soft)">비용이 낮은 쌍부터 배정하고,</text>
            <text x="440" y="154" font-size="9" fill="var(--ink-soft)">겹치면 낮은 쪽만 남긴다.</text>

            <text x="440" y="180" font-size="9" fill="var(--accent)">원래 OTA 는 최적수송 문제를</text>
            <text x="440" y="194" font-size="9" fill="var(--accent)">Sinkhorn 으로 풀었다.</text>
            <text x="440" y="212" font-size="9" fill="var(--ink-faint)">SimOTA 는 그것을 top-k 근사로</text>
            <text x="440" y="226" font-size="9" fill="var(--ink-faint)">바꿔 학습 시간을 되돌렸다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        SimOTA의 <em>Sim</em>은 simplified다. 선행 연구 OTA는 이 배정을
        최적수송 문제로 정식화해 Sinkhorn-Knopp으로 풀었는데, 학습 시간이 25% 늘었다.
        YOLOX는 <strong>동적 k와 top-k 선택</strong>이라는 근사로 바꿔
        이득의 대부분을 유지하면서 비용을 없앴다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>기여를 뜯어 보면</h2>
    <p>
      논문의 ablation이 유용한 이유는 <strong>무엇이 실제로 성능을 올렸는지</strong>를 분리해 보여주기 때문이다.
      YOLOv3 기준선에서 하나씩 더해간 결과다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>단계</th><th>COCO AP</th><th>증분</th></tr>
        </thead>
        <tbody>
          <tr><td>YOLOv3 기준선</td><td>38.5</td><td>—</td></tr>
          <tr><td>+ Decoupled head</td><td>39.6</td><td>+1.1</td></tr>
          <tr><td>+ 강한 증강 (Mosaic·MixUp)</td><td>42.0</td><td>+2.4</td></tr>
          <tr><td>+ 앵커프리</td><td>42.9</td><td>+0.9</td></tr>
          <tr><td>+ 다중 양성</td><td>45.0</td><td>+2.1</td></tr>
          <tr><td>+ SimOTA</td><td class="hi">47.3</td><td class="hi">+2.3</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      눈에 띄는 것은 <strong>백본을 전혀 바꾸지 않았다</strong>는 점이다.
      38.5에서 47.3까지 8.8포인트가 올랐는데, 그 전부가
      <em>머리 구조·증강·라벨 할당</em>에서 나왔다. 특징 추출기는 그대로다.
    </p>
    <div class="note">
      <b>이것이 이 시기 검출기 연구의 성격을 말해준다.</b>
      성능을 가른 것은 "무엇을 보는가"(백본)가 아니라
      <em>"본 것을 어떻게 정답과 연결하는가"</em>(할당)였다.
      DETR이 헝가리안 매칭으로 같은 문제를 다르게 푼 것도 이 맥락에서 읽어야 한다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>실무에서 — tiny·nano, 그리고 라이선스</h2>
    <p>
      YOLOX도 여러 크기로 제공된다. 경량 모델은 별도 계열로 두었다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>모델</th><th>입력</th><th>파라미터</th><th>COCO AP</th></tr>
        </thead>
        <tbody>
          <tr><td>YOLOX-Nano</td><td>416</td><td>0.91M</td><td>25.8</td></tr>
          <tr><td>YOLOX-Tiny</td><td>416</td><td class="hi">5.06M</td><td class="hi">32.8</td></tr>
          <tr><td>YOLOX-S</td><td>640</td><td>9.0M</td><td>40.5</td></tr>
          <tr><td>YOLOX-M</td><td>640</td><td>25.3M</td><td>46.9</td></tr>
          <tr><td>YOLOX-L</td><td>640</td><td>54.2M</td><td>49.7</td></tr>
          <tr><td>YOLOX-X</td><td>640</td><td>99.1M</td><td>51.1</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>YOLOv5s(7.2M / 37.4 @640)와 YOLOX-Tiny(5.06M / 32.8 @416)를 직접 비교할 때는 주의가 필요하다</strong> —
      입력 해상도가 다르다. 같은 640 기준으로 맞추면 YOLOX-S가 9.0M에 40.5로,
      YOLOv5s보다 파라미터는 약간 많고 AP는 3.1포인트 높다.
      Tiny는 416 입력을 전제로 한 <em>더 가벼운 영역</em>의 모델이다.
    </p>
    <div class="note">
      <b>라이선스가 실무 선택을 가르는 경우가 많다.</b>
      YOLOX는 <strong>Apache 2.0</strong>이다. Ultralytics 계열(YOLOv5·v8·11)의
      AGPL-3.0과 달리 상용 배포 시 소스 공개 의무가 없다.
      성능이 비슷한 두 모델 중 하나를 골라야 할 때, 제품에 넣는 것이라면
      이 차이가 성능 몇 포인트보다 결정적일 수 있다.
    </div>
    <p>
      YOLOX가 남긴 것은 결국 방향이다 —
      <em>사람이 손으로 정하던 것을 하나씩 학습이나 계산으로 넘긴다.</em>
      앵커를 없앴고, 할당을 계산으로 넘겼다. 남은 수작업은 <a href="nms.html"><strong>NMS</strong></a>였고,
      그것을 없애는 일은 DETR 계열과 이후 YOLO 세대의 몫이 된다.
    </p>
  </section>
"""

READING = [
    "Ge et al., <em>YOLOX: Exceeding YOLO Series in 2021</em> (arXiv:2107.08430) — 원 논문. ablation 표가 여기 있다.",
    "Ge et al., <em>OTA: Optimal Transport Assignment for Object Detection</em> (arXiv:2103.14259) — SimOTA가 단순화한 원본.",
    "Tian et al., <em>FCOS: Fully Convolutional One-Stage Object Detection</em> (arXiv:1904.01355) — 앵커프리 거리 회귀의 출처.",
    "Song et al., <em>Revisiting the Sibling Head in Object Detector</em> (arXiv:2003.07540) — 분류·회귀 분리의 근거.",
    "Zhang et al., <em>Bridging the Gap Between Anchor-based and Anchor-free Detection via ATSS</em> (arXiv:1912.02424) — 차이의 본질이 라벨 할당임을 보인 연구.",
]

write(
    "yolox.html",
    title="YOLOX — 앵커를 걷어내고 머리를 나누다",
    eyebrow="Detection · Anchor-Free · 2021",
    h1="YOLOX",
    subtitle="앵커를 걷어내고 머리를 나누다 — 성능을 올린 것은 백본이 아니었다",
    dek=(
        "YOLOX는 YOLOv3 기준선에서 AP를 8.8포인트 올렸는데, "
        "<strong>백본은 전혀 바꾸지 않았다</strong>. "
        "올린 것은 머리 구조·증강·라벨 할당이고, 그중 가장 큰 몫이 SimOTA다. "
        "사람이 정하던 배정 규칙을 손실 기반 계산으로 넘긴 것 — "
        "이 시기 검출기 연구의 성격이 여기 압축돼 있다."
    ),
    spec=[
        ("구조", "앵커프리 1단계"),
        ("예측 수", "8,400 (640 입력)"),
        ("머리", "분류·회귀 분리"),
        ("할당", "SimOTA · 동적 k"),
        ("라이선스", "Apache 2.0"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
