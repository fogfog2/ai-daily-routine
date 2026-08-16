#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff0f2", panel="#e4e6ea", ink="#13161c", **{
    "ink-soft": "#4c525e", "ink-faint": "#7b8190", "rule": "#cfd2d9",
    "rule-strong": "#abafba", "accent": "#2a4f9e", "accent-fill": "#dde4f5",
    "accent-line": "#4a70c0", "muted": "#84888e", "muted-fill": "#dfe1e5", "warn": "#a0472a",
})
DARK = dict(paper="#0f1114", panel="#171a20", ink="#e5e8ee", **{
    "ink-soft": "#a2a8b6", "ink-faint": "#737a88", "rule": "#212530", "rule-strong": "#373d4c",
    "accent": "#7ba3ee", "accent-fill": "#141d33", "accent-line": "#4f6fb5",
    "muted": "#878d96", "muted-fill": "#1a1d23", "warn": "#e08560",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>어텐션이 치르는 값</h2>
    <p>
      트랜스포머는 모든 토큰이 모든 토큰을 본다. 그래서 강력하고, 그래서 비싸다.
      비용은 두 군데서 나온다.
    </p>
    <ul>
      <li><strong>학습:</strong> 시퀀스 길이 <code>L</code>에 대해 <code>O(L²)</code>. 문맥을 두 배로 늘리면 연산이 네 배가 된다.</li>
      <li><strong>추론:</strong> 토큰 하나를 생성할 때마다 지금까지의 KV 캐시 전부를 읽어야 한다. 캐시는 <code>L</code>에 비례해 계속 자란다.</li>
    </ul>
    <p>
      RNN에는 이 문제가 없었다. 상태 하나를 들고 순서대로 읽으므로
      토큰당 비용이 <strong>일정</strong>하다. 문맥이 100만이든 100이든 같다.
      대신 RNN은 <em>학습을 병렬화할 수 없다</em>는 치명적 약점이 있었다 —
      <code>h<sub>t</sub></code>를 알아야 <code>h<sub>t+1</sub></code>을 계산할 수 있으니 시간축을 따라 순차 실행해야 한다.
    </p>
    <div class="note">
      <b>둘 다 갖고 싶다.</b> RNN의 추론 효율(상태 하나, 일정 비용)과
      트랜스포머의 학습 병렬성. 상태공간 모델(SSM) 계열이 겨냥한 것이 정확히 이 조합이다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>상태공간 모델 — 연속 시스템에서 빌려온 형식</h2>
    <p>
      SSM은 제어 이론의 연속시간 시스템에서 출발한다.
      입력 신호가 들어오면 내부 상태가 갱신되고, 상태에서 출력이 나온다.
    </p>
    <div class="eq">
      <span class="cap">이산화된 상태공간 모델 — 형태는 RNN과 같다</span>
      <div class="line">h<sub>t</sub> = <strong>Ā</strong> h<sub>t−1</sub> + <strong>B̄</strong> x<sub>t</sub></div>
      <div class="line">y<sub>t</sub> = <strong>C</strong> h<sub>t</sub></div>
      <div class="line">// A ∈ ℝ^(N×N), N = 상태 차원 (보통 16 ~ 256)</div>
    </div>
    <p>
      결정적인 차이는 <code>A</code>, <code>B</code>, <code>C</code>가 <strong>입력과 무관한 상수</strong>라는 점이다.
      LSTM의 게이트는 입력에 따라 매번 달라지지만, 여기서는 고정이다.
      바로 그 덕분에 재귀를 <strong>펼쳐서 하나의 합성곱으로 바꿀 수 있다</strong>.
    </p>
    <div class="eq">
      <span class="cap">재귀를 합성곱으로 — 학습 시 병렬화의 근거</span>
      <div class="line">y = x ∗ K̄</div>
      <div class="line">K̄ = ( C B̄,&nbsp; C ĀB̄,&nbsp; C Ā²B̄,&nbsp; …,&nbsp; C Ā<sup>L−1</sup>B̄ )</div>
      <div class="line">// 커널을 미리 만들어 FFT 로 한 번에 계산 — 순차 실행 불필요</div>
    </div>
    <p>
      이것이 S4 계열의 핵심 재주다. <strong>학습 때는 합성곱</strong>으로 병렬 처리하고,
      <strong>추론 때는 재귀</strong>로 토큰당 상수 시간에 처리한다. 같은 모델의 두 가지 얼굴이다.
    </p>
    <p>
      남은 문제는 <code>A</code>를 어떻게 정하느냐였다. 무작위로 두면 장거리 정보가 소실된다.
      S4는 HiPPO라는 이론으로 <em>과거를 다항식 기저로 압축 기억하는</em> 특별한 <code>A</code>를 유도해 이를 해결했다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>고정 파라미터의 한계 — 선택하지 못한다</h2>
    <p>
      그런데 <code>A, B, C</code>가 상수라는 바로 그 성질이 심각한 약점을 낳는다.
      <strong>내용에 따라 다르게 반응할 수 없다.</strong>
    </p>
    <p>
      언어에서는 이것이 치명적이다. "그런데", "음" 같은 토큰은 흘려보내고
      고유명사나 핵심 술어는 오래 기억해야 하는데, 고정 SSM은 모든 토큰을 <em>똑같이</em> 처리한다.
      필터가 입력을 보지 않으니 무엇을 기억하고 무엇을 버릴지 고를 수 없다.
    </p>
    <p>
      이를 드러내는 대표적 과제가 <strong>선택적 복사</strong>와 <strong>귀납 헤드</strong>다.
      "관련 있는 토큰만 골라 기억했다가 나중에 꺼내라"는 요구인데,
      어텐션은 자연스럽게 하고 고정 SSM은 실패한다.
    </p>
    <p>
      Mamba의 답은 단순하다 — <strong>파라미터를 입력의 함수로 만든다.</strong>
    </p>
    <div class="eq">
      <span class="cap">선택적 SSM — B, C, Δ 가 토큰마다 달라진다</span>
      <div class="line">B<sub>t</sub> = Linear<sub>B</sub>(x<sub>t</sub>)&nbsp;&nbsp;&nbsp;C<sub>t</sub> = Linear<sub>C</sub>(x<sub>t</sub>)</div>
      <div class="line">Δ<sub>t</sub> = softplus( Linear<sub>Δ</sub>(x<sub>t</sub>) )&nbsp;&nbsp;← 시간 간격도 입력에 따라</div>
      <div class="line">h<sub>t</sub> = Ā(Δ<sub>t</sub>) h<sub>t−1</sub> + B̄<sub>t</sub> x<sub>t</sub></div>
    </div>
    <p>
      <code>Δ<sub>t</sub></code>의 역할이 특히 직관적이다. 크면 현재 입력을 강하게 반영하고
      과거를 잊으며(리셋에 가깝다), 작으면 현재를 무시하고 상태를 유지한다.
      <strong>사실상 게이트</strong>다 — LSTM이 하던 일을 상태공간 형식 안에서 되살린 셈이다.
    </p>
    <div class="note">
      <b>그런데 이러면 합성곱으로 못 바꾼다.</b> 커널 <code>K̄</code>를 미리 만들려면
      <code>Ā, B̄</code>가 시점에 무관해야 하는데 이제 매 시점 달라진다.
      Mamba가 얻은 표현력은 <em>학습 병렬화 방식을 잃는 대가</em>로 온 것이다.
      이 문제를 하드웨어 쪽에서 되찾는 것이 다음 절이다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>병렬 스캔과 커널 융합으로 되찾기</h2>
    <p>
      합성곱을 못 쓰게 됐지만, 재귀 자체를 병렬화하는 다른 길이 있다.
      <strong>병렬 스캔</strong>(prefix sum의 일반화)이다.
      결합법칙이 성립하는 연산은 트리 구조로 묶어 <code>O(log L)</code> 깊이에 계산할 수 있고,
      선형 재귀가 마침 그 조건을 만족한다.
    </p>
    <p>
      여기에 FlashAttention과 같은 발상을 얹는다. 상태 <code>h</code>는
      <code>(배치 × 길이 × 채널 × 상태차원)</code> 크기라 HBM에 쓰면 감당이 안 된다.
      Mamba는 <strong>확장된 상태를 SRAM 안에서만 다루고 HBM에는 쓰지 않는다.</strong>
      역전파에 필요한 중간값은 저장 대신 재계산한다 — FlashAttention의 recomputation과 같은 거래다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="어텐션과 선택적 상태공간 모델의 비교. 어텐션은 모든 이전 토큰의 KV 캐시를 참조해 길이에 비례하는 비용이 들고, Mamba는 고정 크기 상태 하나만 갱신해 토큰당 비용이 일정하지만 그 상태 안에 과거를 압축해 넣어야 한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="mb-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
              <marker id="mb-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--muted)">어텐션 — 전부 다시 본다</text>

            <g>
              <rect x="26" y="34" width="26" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="58" y="34" width="26" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="90" y="34" width="26" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="122" y="34" width="26" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="154" y="34" width="26" height="24" fill="var(--warn)" opacity="0.25" stroke="var(--warn)" stroke-width="1.3"/>
              <text x="167" y="50" text-anchor="middle" font-size="9" fill="var(--ink)">t</text>
            </g>
            <path d="M39 62 L160 62" stroke="var(--muted)" stroke-width="1" marker-end="url(#mb-a)"/>
            <path d="M71 68 L162 68" stroke="var(--muted)" stroke-width="1" marker-end="url(#mb-a)"/>
            <path d="M103 74 L164 74" stroke="var(--muted)" stroke-width="1" marker-end="url(#mb-a)"/>
            <path d="M135 80 L166 80" stroke="var(--muted)" stroke-width="1" marker-end="url(#mb-a)"/>

            <text x="26" y="102" font-size="9" fill="var(--warn)">KV 캐시가 L 에 비례해 자란다</text>
            <text x="26" y="116" font-size="9" fill="var(--ink-faint)">토큰당 비용 O(L) · 학습 O(L²)</text>
            <text x="26" y="134" font-size="9" fill="var(--accent)">✓ 과거를 손실 없이 참조</text>

            <line x1="230" y1="24" x2="230" y2="216" stroke="var(--rule)" stroke-width="1"/>

            <text x="258" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">Mamba — 상태 하나만 들고 간다</text>

            <g>
              <rect x="258" y="34" width="26" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="290" y="34" width="26" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="322" y="34" width="26" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="354" y="34" width="26" height="24" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
              <rect x="386" y="34" width="26" height="24" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
              <text x="399" y="50" text-anchor="middle" font-size="9" fill="var(--accent)">t</text>
            </g>

            <rect x="258" y="72" width="154" height="26" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="335" y="89" text-anchor="middle" font-size="9" fill="var(--accent)">상태 h — 크기 고정 (N=16)</text>

            <path d="M271 62 L271 70" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#mb-b)"/>
            <path d="M303 62 L303 70" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#mb-b)"/>
            <path d="M335 62 L335 70" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#mb-b)"/>
            <path d="M367 62 L367 70" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#mb-b)"/>
            <path d="M399 62 L399 70" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#mb-b)"/>

            <text x="258" y="116" font-size="9" fill="var(--accent)">토큰당 비용 O(1) · 학습 O(L)</text>
            <text x="258" y="134" font-size="9" fill="var(--warn)">✗ 상태에 안 담긴 과거는 되살릴 수 없다</text>

            <rect x="26" y="150" width="648" height="1" fill="var(--rule)"/>

            <text x="26" y="172" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">Δ_t 가 게이트 역할을 한다</text>
            <rect x="26" y="182" width="150" height="20" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1"/>
            <text x="101" y="196" text-anchor="middle" font-size="8.5" fill="var(--accent)">Δ 큼 → 현재 반영, 과거 잊음</text>
            <rect x="182" y="182" width="150" height="20" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1"/>
            <text x="257" y="196" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">Δ 작음 → 현재 무시, 상태 유지</text>

            <text x="352" y="180" font-size="9" fill="var(--ink-faint)">이 선택 능력을 얻은 대가로 합성곱 병렬화를 잃었고,</text>
            <text x="352" y="194" font-size="9" fill="var(--ink-faint)">병렬 스캔 + SRAM 커널 융합으로 되찾았다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        차이는 <strong>과거를 어떻게 들고 가는가</strong>에 있다.
        어텐션은 전부 보관해 필요할 때 정확히 꺼내고, Mamba는 고정 크기 상태에 압축해 넣는다.
        압축이므로 <em>버린 것은 되살릴 수 없다</em> — 이것이 다음 절의 한계로 이어진다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>남은 한계와 현재의 결론 — 하이브리드</h2>
    <p>
      Mamba는 언어·오디오·유전체에서 같은 크기의 트랜스포머와 대등하거나 나은 성능을 보였고,
      추론 처리량은 수 배 높았다. 그러나 이후 후속 연구들이 <strong>구조적 한계</strong>를 분명히 했다.
    </p>
    <p>
      핵심은 <strong>상태가 유한하다</strong>는 사실이다.
      "앞에서 한 번 지나간 임의의 세부사항을 정확히 인용하라"는 과제 —
      긴 문서에서 특정 문자열 찾기, 다중 정보 검색 같은 것들 —
      에서 어텐션에 밀린다. 압축한 것을 무손실로 복원할 수는 없다.
    </p>
    <p>
      Mamba-2는 이 지점을 정면으로 다룬다. <strong>SSD</strong>(구조적 상태공간 이중성)라는 틀로
      SSM과 선형 어텐션이 사실상 같은 대상의 두 표현임을 보이고,
      그 이론에 기대어 <strong>상태 차원을 8배로</strong> 키웠다.
      상태를 키울수록 기억 용량이 늘어 성능이 오른다는 것은 실험적으로 확인된 경향이다.
    </p>
    <div class="note">
      <b>상태를 무한정 키우면 어텐션이 된다.</b> Mamba-2 층의 상태 크기는
      바닐라 트랜스포머의 KV 캐시와 같은 규모에 이른다.
      즉 SSM의 효율은 <em>"과거를 얼마나 압축하느냐"</em>에서 나오고,
      압축을 포기하면 이점도 사라진다. 공짜가 아니라 <strong>교환</strong>이다.
    </div>
    <p>
      그래서 현재의 실무적 결론은 <strong>둘 중 하나가 아니라 섞는 것</strong>이다.
      Jamba, Zamba 같은 모델은 대부분의 층을 Mamba로 두고
      일정 간격마다 어텐션 층을 끼워 넣는다.
      평상시 토큰 처리는 선형 비용으로 하되, 정확한 참조가 필요한 순간에는 어텐션이 맡는 구성이다.
    </p>
    <p>
      이 교환이 어디에서 문제가 되는지는 <a href="long-context.html">긴 문맥</a> 편에서
      다른 방향의 처방들과 나란히 놓고 볼 수 있다 —
      창을 자르는 쪽, 캐시를 압축하는 쪽, 그리고 여기처럼 구조를 바꾸는 쪽이
      각각 무엇을 내주는지가 갈린다.
    </p>
    <p>
      Mamba가 남긴 것을 한 문장으로 줄이면 이렇다 —
      <em>어텐션의 이차 비용은 필연이 아니었지만, 그것이 사주던 무손실 참조 능력도 공짜가 아니었다.</em>
    </p>
  </section>
"""

READING = [
    "Gu &amp; Dao, <em>Mamba: Linear-Time Sequence Modeling with Selective State Spaces</em> (arXiv:2312.00752) — 선택적 SSM과 하드웨어 인식 병렬 스캔.",
    "Dao &amp; Gu, <em>Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality</em> (arXiv:2405.21060) — Mamba-2와 SSD 이론.",
    "Gu et al., <em>Efficiently Modeling Long Sequences with Structured State Spaces</em> (arXiv:2111.00396) — S4. HiPPO 기반 A 행렬.",
    "Waleffe et al., <em>An Empirical Study of Mamba-based Language Models</em> (arXiv:2406.07887) — 8B 규모 비교. 하이브리드가 나은 이유의 실증.",
    "Lieber et al., <em>Jamba: A Hybrid Transformer-Mamba Language Model</em> (arXiv:2403.19887) — 실제 배포된 하이브리드 구성.",
    "Jelassi et al., <em>Repeat After Me: Transformers are Better than State Space Models at Copying</em> (arXiv:2402.01032) — 유한 상태의 구조적 한계.",
]

write(
    "mamba-ssm.html",
    title="Mamba & State Space Models — 다시 순서대로, 그러나 빠르게",
    eyebrow="Architecture · Sequence Modeling · 2021–2026",
    h1="Mamba &amp; SSM",
    subtitle="다시 순서대로, 그러나 빠르게 — 선형 비용으로 되돌아가기",
    dek=(
        "어텐션은 모든 토큰이 서로를 봐서 강력하고, 그래서 <code>O(L²)</code>다. "
        "RNN은 상태 하나만 들고 가 싸지만 학습을 병렬화할 수 없었다. "
        "Mamba는 <strong>파라미터를 입력의 함수로</strong> 만들어 선택 능력을 얻고, "
        "잃어버린 병렬성은 하드웨어 쪽에서 되찾는다. "
        "다만 유한한 상태에 과거를 압축하는 이상, 버린 것은 되살릴 수 없다."
    ),
    spec=[
        ("학습", "O(L)"),
        ("추론", "토큰당 O(1)"),
        ("핵심", "Δ, B, C 가 입력 의존"),
        ("병렬화", "합성곱 → 병렬 스캔"),
        ("약점", "정확한 인용·복사"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
