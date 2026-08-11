#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f1", panel="#e5e6e9", ink="#15171b", **{
    "ink-soft": "#4e5158", "ink-faint": "#7d8088", "rule": "#d0d1d5",
    "rule-strong": "#acaeb3", "accent": "#0b5f6b", "accent-fill": "#d5e9ec",
    "accent-line": "#2a8794", "muted": "#84868c", "muted-fill": "#dfe0e3", "warn": "#a3492a",
})
DARK = dict(paper="#0f1113", panel="#171a1d", ink="#e5e8ea", **{
    "ink-soft": "#a1a6ab", "ink-faint": "#75797f", "rule": "#212527", "rule-strong": "#373d41",
    "accent": "#4fc2d3", "accent-fill": "#0c2a30", "accent-line": "#2d838f",
    "muted": "#86898f", "muted-fill": "#191c1f", "warn": "#e0855e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>합성곱 하나가 하는 두 가지 일</h2>
    <p>
      경량 백본의 거의 모든 아이디어는 관찰 하나에서 출발한다.
      <strong>표준 합성곱은 두 가지 일을 동시에 한다.</strong>
      (<a href="cnn-basics.html">CNN 기초</a>에서 본 지역 연결과 가중치 공유 위에서 하는 이야기다.)
    </p>
    <ul>
      <li><strong>공간적으로 섞는다</strong> — 이웃 픽셀을 본다 (3×3 창)</li>
      <li><strong>채널을 섞는다</strong> — 모든 입력 채널을 조합해 출력 채널을 만든다</li>
    </ul>
    <p>
      두 일을 한 연산에 묶어 두면 비용이 곱해진다.
      <code>C<sub>in</sub> × C<sub>out</sub> × k × k</code> 개의 파라미터가 필요하다.
      그렇다면 <em>둘을 분리하면</em> 어떻게 될까.
    </p>
    <div class="eq">
      <span class="cap">Depthwise Separable — 공간과 채널을 나눈다</span>
      <div class="line">① Depthwise&nbsp;&nbsp; 채널마다 따로 3×3&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;C<sub>in</sub> · k²</div>
      <div class="line">② Pointwise&nbsp;&nbsp; 1×1 로 채널만 섞기&nbsp;&nbsp;&nbsp; C<sub>in</sub> · C<sub>out</sub></div>
      <div class="line">&nbsp;</div>
      <div class="line">표준:&nbsp; C<sub>in</sub> · C<sub>out</sub> · k²</div>
      <div class="line">분리:&nbsp; C<sub>in</sub> · k² + C<sub>in</sub> · C<sub>out</sub></div>
      <div class="line">비율:&nbsp; <strong>1/C<sub>out</sub> + 1/k²</strong></div>
    </div>
    <p>
      마지막 줄이 핵심이다. <code>k = 3</code>이면 <code>1/9 ≈ 0.111</code>이 지배하고,
      <code>C<sub>out</sub></code>이 클수록 앞항은 사라진다.
      즉 <strong>대략 8~9배 절감</strong>이 상한이다.
    </p>
    <div class="eq">
      <span class="cap">실제 값 (k=3)</span>
      <div class="line">C<sub>in</sub>&nbsp; C<sub>out</sub>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;표준&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;분리&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;비율</div>
      <div class="line">&nbsp;32&nbsp;&nbsp; 64&nbsp;&nbsp;&nbsp; 18,432&nbsp;&nbsp;&nbsp;&nbsp; 2,336&nbsp;&nbsp; 0.127</div>
      <div class="line">128&nbsp; 128&nbsp;&nbsp; 147,456&nbsp;&nbsp;&nbsp; 17,536&nbsp;&nbsp; 0.119</div>
      <div class="line">256&nbsp; 512&nbsp; 1,179,648&nbsp;&nbsp; 133,376&nbsp;&nbsp; 0.113</div>
      <div class="line">512&nbsp; 512&nbsp; 2,359,296&nbsp;&nbsp; 266,752&nbsp;&nbsp; 0.113</div>
    </div>
    <p>
      MobileNet 이 이 구조를 전면에 세운 모델이다.
      정확도는 조금 내주지만 연산량이 한 자릿수 배로 줄어, <em>휴대폰에서 돌아가는</em> 급이 됐다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>좁은 곳에서 활성함수를 쓰지 않는다</h2>
    <p>
      MobileNetV2 는 블록 구조를 다시 짰다. 이름이 <strong>inverted residual</strong> 인데,
      기존 잔차 블록과 <em>반대 방향</em>이라 그렇다.
    </p>
    <p>
      ResNet 의 병목 블록은 <em>넓게 → 좁게 → 넓게</em> 간다.
      MobileNetV2 는 <em>좁게 → 넓게 → 좁게</em> 간다.
      1×1 로 채널을 늘리고, depthwise 로 공간을 처리하고, 1×1 로 다시 줄인다.
    </p>
    <div class="eq">
      <span class="cap">Inverted Residual — 잔차 연결은 좁은 쪽끼리</span>
      <div class="line">입력 (좁음, 24ch)</div>
      <div class="line">&nbsp;&nbsp;↓ 1×1 확장 (×6 → 144ch) + ReLU6</div>
      <div class="line">&nbsp;&nbsp;↓ 3×3 depthwise + ReLU6</div>
      <div class="line">&nbsp;&nbsp;↓ 1×1 축소 (→ 24ch)&nbsp;&nbsp;<strong>활성함수 없음</strong></div>
      <div class="line">출력 (좁음) ⊕ 입력</div>
    </div>
    <p>
      마지막 줄의 <strong>linear bottleneck</strong> 이 논문의 핵심 주장이다.
      ReLU 는 음수를 0으로 만들어 <em>정보를 지운다</em>.
      채널이 넓을 때는 다른 채널이 그 정보를 갖고 있을 확률이 높아 손실이 작지만,
      <strong>좁은 채널에서 ReLU 를 쓰면 복구 불가능한 손실</strong>이 난다.
      그래서 좁아진 뒤에는 활성함수를 붙이지 않는다.
    </p>
    <div class="note">
      <b>잔차 연결을 좁은 쪽에 두는 이유는 메모리다.</b>
      확장된 중간 텐서(144ch)는 블록 안에서만 존재하고 바로 버려진다.
      메모리에 남는 것은 좁은 입출력(24ch)뿐이라, 실제 peak 메모리가 크게 줄어든다.
      모바일에서는 연산량만큼이나 <em>메모리 상한</em>이 배포 가능 여부를 가른다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>FLOPs 를 줄였는데 안 빨라진다</h2>
    <p>
      여기서 이 분야의 가장 중요한 교훈이 나온다.
      <strong>연산량을 줄여도 실제 속도가 그만큼 빨라지지 않는다.</strong>
    </p>
    <p>
      <a href="pruning-sparsity.html">가지치기 문서</a>에서 본 것과 같은 종류의 함정이다.
      FLOPs 는 <em>곱셈 횟수</em>만 세고 <em>메모리 이동</em>을 세지 않는다.
      그런데 depthwise 합성곱은 계산 대비 메모리 접근이 많아 <strong>대역폭에 묶인다</strong>.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 232" role="img" aria-label="FLOPs와 실제 지연의 괴리. 표준 합성곱은 연산 집약적이라 하드웨어를 잘 쓰지만, depthwise 합성곱은 채널마다 독립이라 메모리 접근 대비 계산이 적어 대역폭에 묶이고, 그래서 FLOPs 절감이 속도로 그대로 이어지지 않는다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--muted)">표준 합성곱 — 읽은 데이터로 많이 계산한다</text>

            <rect x="24" y="30" width="60" height="60" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="54" y="64" text-anchor="middle" font-size="8" fill="var(--ink-soft)">입력 Cin</text>
            <path d="M92 60 L118 60" stroke="var(--muted)" stroke-width="1.3"/>
            <rect x="124" y="30" width="60" height="60" fill="var(--accent)" opacity="0.25" stroke="var(--accent-line)" stroke-width="1.3"/>
            <text x="154" y="56" text-anchor="middle" font-size="8" fill="var(--ink)">모든 채널</text>
            <text x="154" y="70" text-anchor="middle" font-size="8" fill="var(--ink)">× 모든 출력</text>
            <text x="196" y="52" font-size="8" fill="var(--accent)">연산 밀도 높음</text>
            <text x="196" y="66" font-size="8" fill="var(--ink-faint)">→ 하드웨어를 꽉 쓴다</text>

            <line x1="24" y1="106" x2="674" y2="106" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="126" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">Depthwise — 읽고 조금만 계산한다</text>

            <g>
              <rect x="24" y="138" width="18" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="46" y="138" width="18" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="68" y="138" width="18" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="90" y="138" width="18" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            </g>
            <text x="66" y="196" text-anchor="middle" font-size="8" fill="var(--ink-faint)">채널마다 독립</text>

            <path d="M116 160 L142 160" stroke="var(--warn)" stroke-width="1.3"/>
            <g>
              <rect x="148" y="138" width="18" height="44" fill="var(--warn)" opacity="0.22" stroke="var(--warn)" stroke-width="1"/>
              <rect x="170" y="138" width="18" height="44" fill="var(--warn)" opacity="0.22" stroke="var(--warn)" stroke-width="1"/>
              <rect x="192" y="138" width="18" height="44" fill="var(--warn)" opacity="0.22" stroke="var(--warn)" stroke-width="1"/>
              <rect x="214" y="138" width="18" height="44" fill="var(--warn)" opacity="0.22" stroke="var(--warn)" stroke-width="1"/>
            </g>
            <text x="244" y="152" font-size="8" fill="var(--warn)">채널 간 재사용이 없다</text>
            <text x="244" y="166" font-size="8" fill="var(--warn)">→ 메모리 대역폭에 묶인다</text>
            <text x="244" y="180" font-size="8" fill="var(--ink-faint)">FLOPs 는 1/9 인데 지연은 1/3 정도</text>

            <line x1="410" y1="114" x2="410" y2="222" stroke="var(--rule)" stroke-width="1"/>

            <text x="436" y="132" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">그래서 무엇을 봐야 하나</text>
            <text x="436" y="154" font-size="8.5" fill="var(--warn)">✗ FLOPs · 파라미터 수</text>
            <text x="436" y="168" font-size="8.5" fill="var(--ink-faint)">논문에 흔히 적히지만 대리 지표일 뿐</text>
            <text x="436" y="190" font-size="8.5" fill="var(--accent)">✓ 목표 장비에서 잰 실제 지연</text>
            <text x="436" y="204" font-size="8.5" fill="var(--ink-faint)">메모리 접근량(MAC)도 함께 본다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        ShuffleNetV2 논문이 이 점을 정면으로 다뤘다.
        FLOPs 가 같아도 지연이 크게 다를 수 있으므로,
        <strong>메모리 접근량을 줄이는 설계 지침</strong>을 실측으로 제시했다 —
        입출력 채널을 같게 하라, 그룹 수를 과하게 늘리지 마라, 분기를 줄여라 같은 것들이다.
      </figcaption>
    </figure>

    <p>
      같은 이유로 <em>학습 때와 추론 때 구조를 다르게</em> 하는 기법도 나왔다.
      학습에는 분기가 많은 구조로 성능을 올리고,
      추론 직전에 <strong>분기를 하나의 합성곱으로 합쳐</strong> 단순한 직렬 구조로 바꾼다.
      <a href="lora.html">LoRA</a> 가 학습 후 가중치를 병합하는 것과 같은 발상이다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>사람이 정하던 것을 탐색으로</h2>
    <p>
      경량 모델에는 정할 것이 많다 — 층마다 채널 수, 확장 비율, 커널 크기, 어디서 해상도를 줄일지.
      손으로 조율하기에는 조합이 너무 많다.
    </p>
    <p>
      <strong>NAS</strong>(신경망 구조 탐색)가 이 일을 자동화한다.
      중요한 것은 <em>무엇을 목표로 두느냐</em>다. 초기 NAS 는 정확도만 봤지만,
      모바일용 탐색은 <strong>실제 장비에서 잰 지연</strong>을 목표에 넣는다.
    </p>
    <div class="eq">
      <span class="cap">하드웨어 인지 탐색의 목표</span>
      <div class="line">maximize&nbsp; ACC(m) × [ LAT(m) / T ]<sup>w</sup></div>
      <div class="line">&nbsp;</div>
      <div class="line">LAT(m) = <strong>목표 장비에서 실측한 지연</strong> (FLOPs 아님)</div>
      <div class="line">T = 목표 지연,&nbsp; w &lt; 0 이면 초과 시 벌점</div>
    </div>
    <p>
      MnasNet 과 MobileNetV3 가 이 방식으로 만들어졌다.
      MobileNetV3 는 탐색 결과에 <em>사람의 판단</em>을 더했다 —
      마지막 단계의 비싼 층을 손으로 잘라내고, 활성함수를 hard-swish 로 바꿔
      모바일에서 계산하기 쉽게 만들었다.
    </p>
    <div class="note">
      <b>탐색 결과는 장비에 묶인다.</b> (<a href="mobile-runtime.html">모바일 런타임</a>에서 자세히 다룬다.) A 폰에서 최적인 구조가 B 폰에서는 아닐 수 있다.
      가속기마다 지원 연산자와 최적화가 다르기 때문이다.
      그래서 NAS 로 얻은 구조를 <em>다른 장비에 그대로 가져다 쓰면</em> 이점이 사라지는 경우가 있다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>백본만으로는 끝나지 않는다</h2>
    <p>
      경량 백본은 온디바이스의 <strong>한 조각</strong>일 뿐이다.
      실제 배포에서는 다른 축들과 함께 쓰인다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>축</th><th>무엇을 줄이나</th><th>재학습</th></tr>
        </thead>
        <tbody>
          <tr><td>경량 구조</td><td class="hi">연산량 · 파라미터</td><td>필요 (처음부터)</td></tr>
          <tr><td><a href="quantization.html">양자화</a></td><td class="hi">비트 수 → 메모리·대역폭</td><td>불필요 (사후 가능)</td></tr>
          <tr><td><a href="pruning-sparsity.html">가지치기</a></td><td>연결 수</td><td>대개 필요</td></tr>
          <tr><td><a href="knowledge-distillation.html">증류</a></td><td>—(작은 모델의 품질을 올림)</td><td>필요</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      실무 순서는 대개 이렇다. <strong>경량 백본으로 시작해 증류로 품질을 끌어올리고,
      마지막에 양자화한다.</strong> 양자화가 마지막인 이유는 사후 적용이 가능하고
      효과가 가장 확실하기 때문이다.
    </p>
    <div class="note">
      <b>경량 구조와 양자화는 충돌하기도 한다.</b>
      depthwise 층은 채널별 분포 편차가 커서 <em>채널 단위 양자화</em>가 아니면
      정확도가 크게 떨어지는 경우가 알려져 있다.
      "각각 잘 되니 합치면 잘 되겠지"가 성립하지 않는 지점이라,
      조합은 실측으로 확인해야 한다.
    </div>
    <p>
      마지막으로 관점 하나. 경량 백본의 역사는
      <em>"무엇을 줄일 것인가"에서 "무엇을 재고 있는가"로</em> 옮겨온 과정이다.
      파라미터를 줄이는 데서 시작해 FLOPs 로, 다시 실측 지연으로 목표가 바뀌었다.
      <a href="flash-attention.html">FlashAttention</a> 이 어텐션에서
      "병목은 곱셈이 아니라 메모리 왕복"이라고 진단한 것과 같은 결론에,
      비전 쪽에서 독립적으로 도달한 셈이다.
    </p>
  </section>
"""

READING = [
    "Howard et al., <em>MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications</em> (arXiv:1704.04861) — depthwise separable.",
    "Sandler et al., <em>MobileNetV2: Inverted Residuals and Linear Bottlenecks</em> (arXiv:1801.04381) — 좁은 곳에서 ReLU 를 쓰지 않는 이유.",
    "Ma et al., <em>ShuffleNet V2: Practical Guidelines for Efficient CNN Architecture Design</em> (arXiv:1807.11164) — FLOPs 가 아니라 실측 지연.",
    "Tan et al., <em>MnasNet: Platform-Aware Neural Architecture Search for Mobile</em> (arXiv:1807.11626) — 지연을 목표에 넣은 탐색.",
    "Howard et al., <em>Searching for MobileNetV3</em> (arXiv:1905.02244) — 탐색 결과에 사람의 조정을 더한 사례.",
    "Ding et al., <em>RepVGG: Making VGG-style ConvNets Great Again</em> (arXiv:2101.03697) — 학습 구조와 추론 구조의 분리.",
]

write(
    "efficient-backbone.html",
    title="경량 백본 — 휴대폰에서 도는 신경망",
    eyebrow="Vision · On-Device · 2017–2026",
    h1="경량 백본",
    subtitle="휴대폰에서 도는 신경망 — FLOPs 를 줄여도 빨라지지 않는 이유",
    dek=(
        "표준 합성곱은 <strong>공간과 채널을 동시에</strong> 섞는다. "
        "둘을 분리하면 연산량이 대략 <code>1/C + 1/k²</code> 로 줄어든다 — 3×3 이면 8~9배다. "
        "그런데 실측하면 그만큼 빨라지지 않는다. "
        "FLOPs 는 곱셈만 세고 <em>메모리 이동</em>을 세지 않기 때문이다."
    ),
    spec=[
        ("핵심", "공간 · 채널 분리"),
        ("절감 상한", "1/C_out + 1/k²"),
        ("V2 주장", "좁은 곳엔 ReLU 금지"),
        ("함정", "FLOPs ≠ 지연"),
        ("탐색 목표", "실측 지연"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)
