#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ef", panel="#e7e6e4", ink="#191714", **{
    "ink-soft": "#55504a", "ink-faint": "#847e76", "rule": "#d4d1cd",
    "rule-strong": "#b0aca6", "accent": "#6b4794", "accent-fill": "#e8dcf4",
    "accent-line": "#8f6cba", "muted": "#84868c", "muted-fill": "#dfe0e2", "warn": "#9c4a24",
})
DARK = dict(paper="#121110", panel="#1a1917", ink="#eae8e5", **{
    "ink-soft": "#aaa49e", "ink-faint": "#7b756e", "rule": "#252320", "rule-strong": "#3b3833",
    "accent": "#b795e8", "accent-fill": "#241a36", "accent-line": "#8264b5",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#e0865c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>순전파가 남기고 가는 것</h2>
    <p>
      학습 메모리 이야기에서 가중치와 옵티마이저 상태는 자주 다뤄진다.
      그런데 실제로 배치 크기를 제한하는 것은 <strong>활성값</strong>인 경우가 많다.
    </p>
    <p>
      이유는 역전파의 구조에 있다. 연쇄 법칙으로 그래디언트를 계산하려면
      <em>순전파 때의 중간 결과</em>가 필요하다.
      예컨대 <code>y = Wx</code>의 <code>W</code>에 대한 그래디언트는 <code>x</code>를 필요로 한다.
      그래서 순전파는 층마다 중간값을 <strong>전부 저장해 둔 채</strong> 진행된다.
    </p>
    <div class="eq">
      <span class="cap">활성값 메모리는 배치와 길이에 비례해 자란다</span>
      <div class="line">활성값 ≈ 배치 × 시퀀스 길이 × 은닉 차원 × 층 수 × c</div>
      <div class="line">// c 는 층당 저장 지점 수 (어텐션·FFN·정규화 등)</div>
      <div class="line">&nbsp;</div>
      <div class="line">가중치는 배치와 <strong>무관</strong>하지만</div>
      <div class="line">활성값은 배치에 <strong>정비례</strong>한다 — 그래서 배치를 못 키운다</div>
    </div>
    <p>
      여기서 자연스러운 물음이 나온다. <em>저장하는 대신 필요할 때 다시 계산하면 안 되나.</em>
      그래디언트 체크포인팅의 발상이 정확히 이것이다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>버리고, 다시 만든다</h2>
    <p>
      절차는 단순하다. 순전파 때 <strong>일부 지점만</strong> 저장하고 나머지는 버린다.
      역전파에서 버린 값이 필요해지면, 가장 가까운 저장 지점에서 출발해
      <em>그 구간만 순전파를 다시 돌려</em> 복원한다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 224" role="img" aria-label="그래디언트 체크포인팅 도식. 일반 학습은 모든 층의 활성값을 저장하지만, 체크포인팅은 일부 지점만 저장하고 나머지는 버린 뒤 역전파 때 저장 지점에서 다시 순전파를 돌려 복원한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="gc-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
              <marker id="gc-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10" letter-spacing="1.2" fill="var(--muted)">일반 — 전부 저장</text>

            <g>
              <g fill="var(--warn)" opacity="0.45">
                <rect x="30" y="34" width="24" height="24"/><rect x="66" y="34" width="24" height="24"/>
                <rect x="102" y="34" width="24" height="24"/><rect x="138" y="34" width="24" height="24"/>
                <rect x="174" y="34" width="24" height="24"/><rect x="210" y="34" width="24" height="24"/>
                <rect x="246" y="34" width="24" height="24"/><rect x="282" y="34" width="24" height="24"/>
                <rect x="318" y="34" width="24" height="24"/>
              </g>
              <g stroke="var(--rule-strong)" stroke-width="1" fill="none">
                <rect x="30" y="34" width="24" height="24"/><rect x="66" y="34" width="24" height="24"/>
                <rect x="102" y="34" width="24" height="24"/><rect x="138" y="34" width="24" height="24"/>
                <rect x="174" y="34" width="24" height="24"/><rect x="210" y="34" width="24" height="24"/>
                <rect x="246" y="34" width="24" height="24"/><rect x="282" y="34" width="24" height="24"/>
                <rect x="318" y="34" width="24" height="24"/>
              </g>
            </g>
            <text x="356" y="50" font-size="9" fill="var(--warn)">메모리 O(n)</text>
            <text x="30" y="74" font-size="8.5" fill="var(--ink-faint)">9개 층의 활성값을 모두 들고 역전파를 기다린다</text>

            <line x1="26" y1="88" x2="674" y2="88" stroke="var(--rule)" stroke-width="1"/>

            <text x="26" y="110" font-size="10" letter-spacing="1.2" fill="var(--accent)">체크포인팅 — 3개만 저장</text>

            <g>
              <rect x="30" y="124" width="24" height="24" fill="var(--accent)" opacity="0.7"/>
              <rect x="66" y="124" width="24" height="24" fill="none" stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 2"/>
              <rect x="102" y="124" width="24" height="24" fill="none" stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 2"/>
              <rect x="138" y="124" width="24" height="24" fill="var(--accent)" opacity="0.7"/>
              <rect x="174" y="124" width="24" height="24" fill="none" stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 2"/>
              <rect x="210" y="124" width="24" height="24" fill="none" stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 2"/>
              <rect x="246" y="124" width="24" height="24" fill="var(--accent)" opacity="0.7"/>
              <rect x="282" y="124" width="24" height="24" fill="none" stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 2"/>
              <rect x="318" y="124" width="24" height="24" fill="none" stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 2"/>
              <g stroke="var(--accent-line)" stroke-width="1.3" fill="none">
                <rect x="30" y="124" width="24" height="24"/>
                <rect x="138" y="124" width="24" height="24"/>
                <rect x="246" y="124" width="24" height="24"/>
              </g>
            </g>
            <text x="356" y="140" font-size="9" fill="var(--accent)">메모리 O(√n)</text>
            <text x="30" y="164" font-size="8.5" fill="var(--ink-faint)">점선은 버려진 활성값 — 필요해지면 그때 다시 만든다</text>

            <path d="M258 154 L258 172 L162 172" stroke="var(--accent-line)" stroke-width="1.3" fill="none" marker-end="url(#gc-b)"/>
            <text x="270" y="186" font-size="8.5" fill="var(--accent)">역전파가 여기 도달하면</text>
            <text x="270" y="199" font-size="8.5" fill="var(--accent)">앞 체크포인트에서 구간만 재계산</text>

            <rect x="440" y="112" width="234" height="1" fill="var(--rule)"/>
            <text x="440" y="106" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">거래 조건</text>

            <text x="440" y="134" font-size="9" fill="var(--accent)">메모리&nbsp;&nbsp; O(n) → O(√n)</text>
            <text x="440" y="150" font-size="9" fill="var(--warn)">연산&nbsp;&nbsp;&nbsp;&nbsp; 순전파 1회 추가</text>
            <text x="440" y="166" font-size="9" fill="var(--ink-faint)">실측 속도&nbsp; 대략 20~30% 감소</text>

            <text x="440" y="192" font-size="8.5" fill="var(--ink-faint)">느려지는 대신 배치를 키울 수 있어,</text>
            <text x="440" y="205" font-size="8.5" fill="var(--ink-faint)">총 처리량은 오히려 오르기도 한다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>메모리를 연산으로 사는 거래</strong>다.
        저장 지점을 <code>√n</code> 간격으로 두면 메모리와 재계산 비용이 균형을 이룬다 —
        저장하는 체크포인트가 <code>√n</code>개, 구간마다 복원할 활성값도 <code>√n</code>개다.
      </figcaption>
    </figure>

    <div class="eq">
      <span class="cap">왜 √n 인가</span>
      <div class="line">n 개 층을 k 개 구간으로 나눈다고 하자</div>
      <div class="line">&nbsp;&nbsp;저장:&nbsp; 체크포인트 k 개</div>
      <div class="line">&nbsp;&nbsp;복원:&nbsp; 한 구간의 활성값 n/k 개를 동시에 들고 있어야 함</div>
      <div class="line">&nbsp;&nbsp;합계:&nbsp; k + n/k&nbsp;&nbsp;→ k = √n 에서 최소 = 2√n</div>
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>비용은 순전파 한 번</h2>
    <p>
      추가 비용은 생각보다 작다. 재계산되는 것은 <strong>순전파뿐</strong>이고,
      역전파는 원래 한 번만 돈다.
    </p>
    <p>
      일반적으로 역전파는 순전파의 대략 두 배 연산을 한다(입력에 대한 그래디언트와
      가중치에 대한 그래디언트를 모두 계산하므로).
      그러면 <code>순전파 1 + 역전파 2 = 3</code>이 기준이고,
      체크포인팅은 여기에 순전파 <code>1</code>을 더해 <code>4</code>가 된다.
      <strong>이론상 약 33% 증가</strong>다.
    </p>
    <p>
      실측에서는 보통 20~30% 정도 느려진다고 보고된다.
      재계산이 memory-bound가 아니라 compute-bound라 GPU를 효율적으로 쓰기 때문이다.
    </p>
    <div class="note">
      <b>느려지는데도 전체가 빨라지는 경우가 있다.</b> 메모리가 확보되면 배치를 키울 수 있고,
      배치가 크면 GPU 사용률이 올라간다. 스텝당 시간은 늘어도
      <em>초당 처리하는 샘플 수</em>는 늘어나는 구간이 존재한다.
      메모리 부족으로 배치 1을 쓰던 상황이라면 특히 그렇다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>어디를 저장할 것인가</h2>
    <p>
      실무에서는 <code>√n</code> 이론보다 단순한 규칙을 쓴다.
      <strong>트랜스포머 블록 하나를 단위로</strong> 삼아, 블록 경계만 저장하고
      블록 내부는 전부 버리는 방식이다. 구현이 간단하고 효과가 크다.
    </p>
    <p>
      더 정교한 선택도 가능하다. 재계산 비용과 저장 비용이 층마다 다르기 때문이다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>연산</th><th>활성값 크기</th><th>재계산 비용</th><th>판단</th></tr>
        </thead>
        <tbody>
          <tr><td>어텐션 행렬</td><td class="hi">매우 큼 (N²)</td><td>큼</td><td class="hi">버린다</td></tr>
          <tr><td>활성함수 출력</td><td>큼</td><td class="hi">거의 공짜</td><td class="hi">버린다</td></tr>
          <tr><td>정규화 통계</td><td>작음</td><td>중간</td><td>저장한다</td></tr>
          <tr><td>행렬곱 입력</td><td>중간</td><td class="hi">비쌈</td><td>저장한다</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      이 판단을 자동화한 것이 <strong>선택적 체크포인팅</strong>이다.
      "값싸게 다시 만들 수 있고 크기가 큰 것"을 우선 버린다.
      활성함수 출력이 대표적이다 — 저장하면 크지만
      입력만 있으면 원소별 연산 한 번으로 복원된다.
    </p>
    <div class="note">
      <b>FlashAttention은 어텐션에 대해 같은 일을 이미 한다.</b>
      <code>N×N</code> 어텐션 행렬을 저장하지 않고 역전파 때 SRAM 안에서 다시 만든다.
      그래서 FlashAttention을 쓰면 어텐션 부분의 활성값 문제가 상당 부분 해소되고,
      체크포인팅은 나머지(FFN 등)를 담당하게 된다. 두 기법은 겹치지 않고 보완한다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>같은 거래의 다른 형태들</h2>
    <p>
      "메모리를 다른 자원으로 바꾼다"는 발상은 체크포인팅만의 것이 아니다.
      무엇과 바꾸느냐에 따라 여러 기법이 갈라진다.
    </p>
    <ul>
      <li><strong>연산과 바꾼다</strong> — 그래디언트 체크포인팅. 재계산 비용을 낸다.</li>
      <li><strong>통신과 바꾼다</strong> — <a href="distributed-training.html">ZeRO-3</a>. 파라미터를 흩어 두고 필요할 때 모아 온다.</li>
      <li><strong>느린 메모리와 바꾼다</strong> — CPU 오프로딩. 옵티마이저 상태를 시스템 메모리에 두고 PCIe로 오간다. 가장 느리지만 가장 많이 확보된다.</li>
      <li><strong>정밀도와 바꾼다</strong> — <a href="mixed-precision.html">혼합 정밀도</a>. 비트 수를 줄인다.</li>
    </ul>
    <p>
      실무에서는 이 순서로 손을 댄다. 체크포인팅이 먼저인 이유는
      <em>구현이 한 줄이고, 부작용이 예측 가능하며, 수치적 결과가 완전히 동일하기</em> 때문이다.
      근사가 아니라 <strong>같은 값을 다시 계산하는 것</strong>이므로 학습 결과가 바뀌지 않는다.
    </p>
    <p>
      마지막으로 이 기법이 실제로 연 것을 짚어 두자.
      긴 문맥 학습이 가능해진 배경에는 체크포인팅이 있다.
      활성값이 시퀀스 길이에 비례하므로, 저장을 포기하지 않고서는
      긴 시퀀스를 다룰 수가 없었다.
      <em>"저장 대신 재계산"이라는 한 줄의 거래가 문맥 길이의 상한을 밀어 올린 셈</em>이다.
    </p>
  </section>
"""

READING = [
    "Chen et al., <em>Training Deep Nets with Sublinear Memory Cost</em> (arXiv:1604.06174) — √n 체크포인팅의 원 논문.",
    "Griewank &amp; Walther, <em>Algorithm 799: revolve</em> (ACM TOMS 2000) — 자동미분에서의 체크포인팅 이론.",
    "Korthikanti et al., <em>Reducing Activation Recomputation in Large Transformer Models</em> (arXiv:2205.05198) — 선택적 체크포인팅과 시퀀스 병렬.",
    "Dao et al., <em>FlashAttention</em> (arXiv:2205.14135) — 어텐션 행렬에 대한 재계산.",
    "Rajbhandari et al., <em>ZeRO-Infinity: Breaking the GPU Memory Wall for Extreme Scale Deep Learning</em> (arXiv:2104.07857) — 오프로딩까지 포함한 메모리 계층 활용.",
]

write(
    "gradient-checkpointing.html",
    title="Gradient Checkpointing — 메모리를 연산으로 사다",
    eyebrow="Infrastructure · Memory Optimization · 2016–2026",
    h1="Gradient Checkpointing",
    subtitle="메모리를 연산으로 사다 — 저장 대신 다시 계산한다",
    dek=(
        "역전파에는 순전파의 중간값이 필요하다. 그래서 활성값을 전부 들고 있어야 하고, "
        "그 크기는 <strong>배치와 시퀀스 길이에 정비례</strong>한다. "
        "체크포인팅은 일부만 저장하고 나머지는 버린 뒤, 필요해지면 그 구간만 다시 순전파한다. "
        "메모리가 <code>O(n)</code>에서 <code>O(√n)</code>이 되고, 값은 완전히 동일하다."
    ),
    spec=[
        ("문제", "활성값 ∝ 배치 × 길이"),
        ("거래", "메모리 ↔ 연산"),
        ("메모리", "O(n) → O(√n)"),
        ("비용", "순전파 1회 (약 30%)"),
        ("정확도", "동일 (근사 아님)"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
