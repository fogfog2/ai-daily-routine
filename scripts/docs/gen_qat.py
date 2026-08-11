#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0eff2", panel="#e6e4ea", ink="#16141c", **{
    "ink-soft": "#504c5b", "ink-faint": "#7f7b8b", "rule": "#d1cfd8",
    "rule-strong": "#adaab6", "accent": "#4b3a8c", "accent-fill": "#e1dcf3",
    "accent-line": "#6d5cb5", "muted": "#84868e", "muted-fill": "#dfe0e4", "warn": "#a04628",
})
DARK = dict(paper="#100f17", panel="#18171f", ink="#e6e5ee", **{
    "ink-soft": "#a3a1b0", "ink-faint": "#767384", "rule": "#212029", "rule-strong": "#383546",
    "accent": "#9d8ee8", "accent-fill": "#1b1836", "accent-line": "#6a5cb5",
    "muted": "#868892", "muted-fill": "#1a1a21", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>PTQ 가 안 될 때</h2>
    <p>
      <a href="calibration.html">캘리브레이션</a>을 아무리 잘 해도
      정확도가 회복되지 않는 경우가 있다. 그때 남는 선택이 <strong>QAT</strong>다 —
      <em>학습 과정에 양자화를 넣는 것</em>이다.
    </p>
    <p>
      PTQ 와 QAT 의 차이를 한 줄로 하면 이렇다.
    </p>
    <div class="eq">
      <span class="cap">언제 양자화를 아는가</span>
      <div class="line">PTQ&nbsp; 학습 → <strong>끝난 뒤</strong> 양자화</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 모델은 양자화될 줄 모른 채 학습됐다</div>
      <div class="line">&nbsp;</div>
      <div class="line">QAT&nbsp; 학습 <strong>중에</strong> 양자화를 시뮬레이션</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 모델이 <em>양자화 오차를 보상하도록</em> 학습된다</div>
    </div>
    <p>
      핵심은 마지막 줄이다. QAT 는 양자화를 <em>피하는</em> 것이 아니라,
      <strong>양자화가 있는 상태에서 최선인 가중치</strong>를 찾는다.
      오차가 생기는 것은 같지만 그 오차를 전제로 나머지가 조정된다.
    </p>
    <div class="note">
      <b>QAT 를 먼저 시도하지 않는 이유.</b> 학습 파이프라인을 다시 세워야 하고,
      데이터·라벨·GPU 시간이 든다. <a href="calibration.html">PTQ</a> 는 라벨 없는 수백 장과 순전파 몇 분이면 끝난다.
      <em>비용 차이가 크므로</em> PTQ 로 되는지 먼저 확인하고, 안 될 때만 올라간다.
      대개 <strong>경량 모델·낮은 비트·민감한 과제</strong>에서 QAT 가 필요해진다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>round 는 미분할 수 없다</h2>
    <p>
      학습에 양자화를 넣으려면 문제가 하나 있다.
      <strong>반올림은 미분 가능하지 않다.</strong>
    </p>
    <div class="eq">
      <span class="cap">round 의 기울기 — 쓸 수가 없다</span>
      <div class="line">round(0.2) = 0&nbsp;&nbsp; 기울기 0</div>
      <div class="line">round(0.7) = 1&nbsp;&nbsp; 기울기 0</div>
      <div class="line">round(1.4) = 1&nbsp;&nbsp; 기울기 0</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 계단 함수다 — 평평한 곳은 기울기 0, 경계는 불연속</div>
      <div class="line">// 그대로 역전파하면 <strong>학습 신호가 전혀 안 흐른다</strong></div>
    </div>
    <p>
      해법이 <strong>Straight-Through Estimator</strong>다. 발상은 대담할 만큼 단순하다 —
      <em>순전파에서는 반올림하고, 역전파에서는 반올림이 없었던 셈 친다.</em>
    </p>
    <div class="eq">
      <span class="cap">STE — 순전파와 역전파가 다른 함수를 쓴다</span>
      <div class="line">순전파:&nbsp; q = round(x / s) · s&nbsp;&nbsp;&nbsp;&nbsp;// 실제로 양자화한다</div>
      <div class="line">역전파:&nbsp; ∂L/∂x := ∂L/∂q&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// 그대로 통과시킨다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 수학적으로 옳은 그래디언트가 아니라 <em>근사</em>다</div>
      <div class="line">// 그런데 실제로 잘 작동한다</div>
    </div>
    <p>
      정당화는 사후적이다. 양자화를 <em>작은 노이즈</em>로 보면
      항등 함수가 그 기댓값의 그럴듯한 근사가 된다는 설명이 흔히 쓰인다.
      엄밀하지는 않지만 <strong>QAT 를 가능하게 한 실용적 트릭</strong>이고,
      다른 이산 연산에서도 널리 재사용된다.
    </p>
    <div class="note">
      <b>클리핑 구간에서는 예외를 둔다.</b> 값이 표현 범위를 넘어 잘리는 구간에서는
      그래디언트를 <em>0으로</em> 만드는 것이 보통이다.
      이미 포화된 값을 더 밀어봐야 출력이 바뀌지 않기 때문이다.
      그래디언트를 그대로 통과시키면 가중치가 계속 바깥으로 밀려나 학습이 불안정해진다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>가짜 양자화 — 학습은 실수로 한다</h2>
    <p>
      QAT 라고 해서 정수로 학습하는 것이 아니다.
      <strong>fp32 로 학습하되 양자화 오차만 흉내</strong>낸다.
      이것을 <em>fake quantization</em> 이라 부른다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 234" role="img" aria-label="가짜 양자화 노드의 동작. 학습 중에는 fp32 값을 양자화했다가 곧바로 되돌려 오차만 남기고, 그래디언트는 STE로 통과시킨다. 배포 시에는 이 노드가 실제 정수 연산으로 대체된다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="qa-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="qa-g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--warn)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">학습 중 — 가짜 양자화 노드</text>

            <rect x="24" y="34" width="60" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="54" y="51" text-anchor="middle" font-size="8" fill="var(--ink-soft)">fp32 값</text>
            <path d="M88 47 L112 47" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#qa-a)"/>

            <rect x="116" y="30" width="84" height="34" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="158" y="45" text-anchor="middle" font-size="8" fill="var(--accent)">양자화</text>
            <text x="158" y="57" text-anchor="middle" font-size="8" fill="var(--accent)">→ 역양자화</text>

            <path d="M204 47 L228 47" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#qa-a)"/>
            <rect x="232" y="34" width="80" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="272" y="51" text-anchor="middle" font-size="8" fill="var(--ink-soft)">fp32 (오차 포함)</text>

            <path d="M316 47 L340 47" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#qa-a)"/>
            <rect x="344" y="34" width="70" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="379" y="51" text-anchor="middle" font-size="8" fill="var(--ink-soft)">다음 층</text>

            <text x="430" y="44" font-size="8" fill="var(--ink-faint)">값은 fp32 이지만</text>
            <text x="430" y="56" font-size="8" fill="var(--ink-faint)">INT8 로 표현 가능한 값만 남는다</text>

            <path d="M272 78 L158 78" stroke="var(--warn)" stroke-width="1.4" marker-end="url(#qa-g)"/>
            <path d="M150 78 L60 78" stroke="var(--warn)" stroke-width="1.4" marker-end="url(#qa-g)"/>
            <text x="200" y="94" text-anchor="middle" font-size="8" fill="var(--warn)">역전파 — STE 로 그대로 통과</text>

            <line x1="24" y1="110" x2="674" y2="110" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="130" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">배포 시 — 노드가 사라지고 정수 연산으로</text>

            <rect x="24" y="144" width="60" height="26" fill="var(--accent)" opacity="0.35" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="54" y="161" text-anchor="middle" font-size="8" fill="var(--ink)">INT8</text>
            <path d="M88 157 L112 157" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#qa-a)"/>
            <rect x="116" y="144" width="84" height="26" fill="var(--accent)" opacity="0.35" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="158" y="161" text-anchor="middle" font-size="8" fill="var(--ink)">정수 곱셈</text>
            <path d="M204 157 L228 157" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#qa-a)"/>
            <rect x="232" y="144" width="80" height="26" fill="var(--accent)" opacity="0.35" stroke="var(--accent-line)" stroke-width="1.1"/>
            <text x="272" y="161" text-anchor="middle" font-size="8" fill="var(--ink)">INT32 누산</text>

            <text x="340" y="155" font-size="8" fill="var(--accent)">학습 때 시뮬레이션한 그대로</text>
            <text x="340" y="167" font-size="8" fill="var(--ink-faint)">실제 정수 파이프라인이 된다</text>

            <line x1="24" y1="186" x2="674" y2="186" stroke="var(--rule)" stroke-width="1"/>
            <text x="24" y="206" font-size="8.5" fill="var(--ink-soft)">핵심: 학습과 배포의 <tspan fill="var(--accent)">수치 동작이 일치</tspan>해야 한다 — 어긋나면 QAT 의 의미가 없다</text>
            <text x="24" y="222" font-size="8" fill="var(--warn)">런타임의 반올림 방식·연산자 융합까지 시뮬레이션이 따라가야 정확히 재현된다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        가짜 양자화 노드는 <strong>양자화했다가 곧바로 되돌린다</strong>.
        값은 여전히 fp32 지만 <em>INT8 로 표현 가능한 값만</em> 남으므로,
        모델은 그 제약 아래에서 최선을 찾도록 학습된다.
        배포할 때 이 노드가 실제 정수 연산으로 대체된다.
      </figcaption>
    </figure>

    <p>
      <strong>학습과 배포의 일치</strong>가 QAT 의 전제다.
      시뮬레이션이 런타임의 실제 동작과 다르면 — 반올림 방식이 다르거나,
      런타임이 합성곱과 배치정규화를 융합하는데 학습에서는 안 했다면 —
      QAT 로 얻은 이득이 배포에서 사라진다.
      그래서 <em>BN 융합을 학습 그래프에도 반영</em>하는 것이 표준 절차다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>스케일도 학습한다</h2>
    <p>
      초기 QAT 는 스케일을 <a href="calibration.html">캘리브레이션</a>처럼 통계로 정하고 고정했다.
      그런데 <strong>스케일 자체를 학습 파라미터로</strong> 두면 더 나아진다는 것이 밝혀졌다.
    </p>
    <p>
      스케일은 <em>클리핑 범위</em>를 정하는 값이다.
      어디서 자를지를 사람이 정한 규칙이 아니라 <strong>손실이 정하게</strong> 하는 것이다.
      <a href="calibration.html">캘리브레이션 문서</a>에서 본 클리핑·반올림 오차의 균형점을
      경사하강이 직접 찾는 셈이다.
    </p>
    <div class="eq">
      <span class="cap">학습되는 스케일 (LSQ 계열)</span>
      <div class="line">q = clip( round(x/s), −Q, Q ) · s&nbsp;&nbsp;&nbsp;// s 도 학습 대상</div>
      <div class="line">&nbsp;</div>
      <div class="line">∂q/∂s 를 유도해 s 에도 그래디언트를 흘린다</div>
      <div class="line">→ 층마다 최적 범위를 <strong>손실 기준으로</strong> 찾는다</div>
    </div>
    <p>
      이 방향이 잘 통한 이유는 앞 문서들과 이어진다.
      <a href="calibration.html">캘리브레이션</a>의 MSE·KL 기준은 <em>텐서 하나의 오차</em>를 줄이는
      대리 지표였다. 스케일을 학습하면 <strong>최종 손실을 직접</strong> 줄이게 되므로,
      대리 지표와 진짜 목표 사이의 간극이 사라진다.
    </p>
    <div class="note">
      <b>4비트 이하에서 차이가 커진다.</b> INT8 은 PTQ 로도 대체로 충분하지만,
      비트가 내려갈수록 표현 가능한 값이 급격히 줄어 오차가 커진다.
      <em>학습된 스케일 + QAT</em> 조합이 저비트에서 특히 유효하다는 결과가 반복 보고됐다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>실무에서의 QAT</h2>
    <p>
      QAT 는 처음부터 학습하지 않는다. <strong>이미 학습된 모델에서 출발</strong>해
      짧게 미세조정하는 것이 표준이다.
    </p>
    <div class="eq">
      <span class="cap">통상적 절차</span>
      <div class="line">1) fp32 로 정상 학습을 마친다</div>
      <div class="line">2) 가짜 양자화 노드를 삽입한다</div>
      <div class="line">3) <strong>낮은 학습률</strong>로 몇 에폭 미세조정 (전체의 5~10% 수준)</div>
      <div class="line">4) BN 통계를 고정하거나 재추정한다</div>
      <div class="line">5) 정수 모델로 변환해 <strong>수치 일치를 검증</strong>한다</div>
    </div>
    <p>
      3번의 학습률이 중요하다. 원래 학습률로 돌리면
      <em>양자화 적응이 아니라 재학습</em>이 되어 원래 성능을 잃을 수 있다.
      이미 좋은 해 근처에 있으므로 <strong>살짝만 움직이게</strong> 한다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th></th><th>PTQ</th><th>QAT</th></tr>
        </thead>
        <tbody>
          <tr><td>필요한 것</td><td class="hi">라벨 없는 수백 장</td><td>학습 데이터 + 라벨 + GPU</td></tr>
          <tr><td>소요</td><td class="hi">수 분</td><td>수 시간 ~ 수 일</td></tr>
          <tr><td>INT8 정확도</td><td>대체로 충분</td><td class="hi">더 나음</td></tr>
          <tr><td>4비트 이하</td><td>손실이 큼</td><td class="hi">유효</td></tr>
          <tr><td>경량 모델</td><td class="hi">취약 (depthwise)</td><td class="hi">회복 가능</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      마지막 줄이 실무의 흔한 상황이다.
      <a href="efficient-backbone.html">MobileNet 계열</a>은 PTQ 에서 유독 손실이 크고,
      QAT 로 상당 부분 회복된다.
      <em>작게 만들수록 양자화에 취약해지는</em> 역설이 있어,
      경량 구조와 양자화를 함께 쓸 때는 QAT 를 염두에 두는 편이 안전하다.
    </p>
    <div class="note">
      <b>대안도 있다.</b> QAT 가 부담스러우면 중간 지점이 있다 —
      <em>층별로 소량의 데이터만 써서 재구성 오차를 줄이는</em> 방식(AdaRound·BRECQ 계열)이다.
      전체 역전파 없이 층 단위로 최적화하므로 PTQ 에 가까운 비용으로 QAT 에 근접한다.
      선택지가 <strong>PTQ 냐 QAT 냐의 이분법이 아니다</strong>.
    </div>
    <p>
      정리하면 QAT 는 <em>"양자화가 있다는 사실을 모델에게 알려주는"</em> 것이다.
      PTQ 가 <strong>끝난 뒤 깎는</strong> 것이라면 QAT 는 <strong>깎일 것을 알고 자라게</strong> 하는 것이고,
      그 차이가 저비트·경량 모델에서 크게 벌어진다.
      다만 비용이 크므로 <a href="calibration.html">PTQ</a> 로 안 될 때 올라가는 순서를 지키는 것이 낫다.
    </p>
  </section>
"""

READING = [
    "Jacob et al., <em>Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference</em> (arXiv:1712.05877) — 가짜 양자화와 QAT 의 표준 형식.",
    "Bengio et al., <em>Estimating or Propagating Gradients Through Stochastic Neurons</em> (arXiv:1308.3432) — STE 의 출처.",
    "Esser et al., <em>Learned Step Size Quantization</em> (arXiv:1902.08153) — 스케일을 학습 파라미터로.",
    "Nagel et al., <em>Up or Down? Adaptive Rounding for Post-Training Quantization</em> (arXiv:2004.10568) — AdaRound. PTQ 와 QAT 사이의 절충.",
    "Li et al., <em>BRECQ: Pushing the Limit of Post-Training Quantization by Block Reconstruction</em> (arXiv:2102.05426) — 블록 단위 재구성.",
    "Nagel et al., <em>A White Paper on Neural Network Quantization</em> (arXiv:2106.08295) — PTQ·QAT 선택 기준 정리.",
]

write(
    "qat.html",
    title="QAT — 깎일 것을 알고 자라게 하기",
    eyebrow="On-Device · Quantization-Aware Training · 2017–2026",
    h1="QAT",
    subtitle="깎일 것을 알고 자라게 하기 — 학습에 양자화를 넣는다",
    dek=(
        "PTQ 는 학습이 <em>끝난 뒤</em> 깎는다. 모델은 양자화될 줄 모른 채 학습됐다. "
        "QAT 는 학습 중에 양자화를 시뮬레이션해 "
        "<strong>양자화가 있는 상태에서 최선인 가중치</strong>를 찾는다. "
        "문제는 반올림이 미분 불가라는 것 — 그래디언트가 0이라 학습 신호가 아예 안 흐른다."
    ),
    spec=[
        ("PTQ 와 차이", "양자화를 알고 학습"),
        ("핵심 트릭", "STE (순전파≠역전파)"),
        ("학습 방식", "가짜 양자화 (fp32 로)"),
        ("발전", "스케일도 학습 대상"),
        ("전제", "학습·배포 수치 일치"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)
