#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1eff1", panel="#e7e4e8", ink="#1a141a", **{
    "ink-soft": "#554c58", "ink-faint": "#847b88", "rule": "#d5cfd7",
    "rule-strong": "#b1aab4", "accent": "#8a2f6b", "accent-fill": "#f2dcec",
    "accent-line": "#b0518e", "muted": "#82868f", "muted-fill": "#dee0e4", "warn": "#a04a24",
})
DARK = dict(paper="#131017", panel="#1b171d", ink="#ebe5ec", **{
    "ink-soft": "#aca2b0", "ink-faint": "#7d7482", "rule": "#272029", "rule-strong": "#3d3542",
    "accent": "#e28cc4", "accent-fill": "#2e1526", "accent-line": "#a85a8c",
    "muted": "#888d96", "muted-fill": "#1c1f24", "warn": "#e08a5c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>격자도 수열도 아닌 데이터</h2>
    <p>
      CNN은 이미지가 <strong>격자</strong>라는 사실을 이용한다. 픽셀에는 위와 아래, 왼쪽과 오른쪽이 있고
      이웃의 개수가 항상 같다. 그래서 3×3 커널을 밀고 다닐 수 있다.
      트랜스포머는 <strong>수열</strong>을 전제한다. 토큰에는 순서가 있고 위치를 번호로 매길 수 있다.
    </p>
    <p>
      그런데 세상의 많은 데이터는 둘 다 아니다.
      분자에서 원자는 몇 번째가 아니고, 소셜 그래프에서 사람마다 친구 수가 다르며,
      도로망에는 시작점이 없다. 이런 데이터에는 두 가지 성질이 있다.
    </p>
    <ul>
      <li><strong>이웃 수가 제각각이다.</strong> 고정 크기 커널을 쓸 수 없다.</li>
      <li><strong>순서가 없다.</strong> 노드에 번호를 어떻게 매기든 같은 그래프다. 모델의 출력도 번호 매기기에 따라 달라지면 안 된다 — <em>순열 불변성</em>이 요구된다.</li>
    </ul>
    <p>
      그래프 신경망은 이 두 제약을 정면으로 받아들인 구조다.
      해법은 <strong>이웃에게 메시지를 받아 자신을 갱신하는 것</strong>이고,
      받는 방식을 <em>순서에 무관한 연산</em>(합, 평균, 최댓값)으로 두면 순열 불변성이 자동으로 성립한다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>메시지 패싱 — 한 층이 하는 일</h2>
    <p>
      거의 모든 GNN은 하나의 틀로 설명된다. 각 층에서 세 단계를 밟는다.
    </p>
    <div class="eq">
      <span class="cap">메시지 패싱 — 만들고, 모으고, 갱신한다</span>
      <div class="line">1) 메시지:&nbsp; m<sub>u→v</sub> = M( h<sub>u</sub><sup>(k)</sup>, h<sub>v</sub><sup>(k)</sup>, e<sub>uv</sub> )</div>
      <div class="line">2) 집계:&nbsp;&nbsp; a<sub>v</sub> = <strong>⊕</strong><sub>u ∈ 𝒩(v)</sub> m<sub>u→v</sub>&nbsp;&nbsp;&nbsp;// ⊕ 는 순서 무관 연산</div>
      <div class="line">3) 갱신:&nbsp;&nbsp; h<sub>v</sub><sup>(k+1)</sup> = U( h<sub>v</sub><sup>(k)</sup>, a<sub>v</sub> )</div>
    </div>
    <p>
      2단계의 <code>⊕</code>가 이 구조의 핵심이다. 합·평균·최댓값처럼
      <strong>입력 순서가 바뀌어도 결과가 같은</strong> 연산이어야 한다.
      그래야 노드 번호를 어떻게 매기든 같은 답이 나온다.
    </p>
    <p>
      층을 <code>k</code>개 쌓으면 각 노드는 <strong><code>k</code> 홉 떨어진 이웃까지</strong>의 정보를 본다.
      1층이면 직접 이웃, 2층이면 친구의 친구까지다.
      CNN에서 층을 쌓아 수용 영역이 넓어지는 것과 같은 원리다.
    </p>
    <p>
      구체적 모델들은 이 틀의 특수한 경우다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>모델</th><th>집계 방식</th><th>특징</th></tr>
        </thead>
        <tbody>
          <tr><td>GCN</td><td>차수로 정규화한 평균</td><td>가장 단순. 이웃을 동등하게 본다</td></tr>
          <tr><td>GraphSAGE</td><td>이웃 샘플링 + 평균/LSTM/풀링</td><td>대규모 그래프용. 전체를 안 봐도 된다</td></tr>
          <tr><td>GAT</td><td class="hi">어텐션 가중 합</td><td>어느 이웃이 중요한지 학습한다</td></tr>
          <tr><td>GIN</td><td class="hi">합 (sum)</td><td>이론적 표현력이 가장 높다</td></tr>
        </tbody>
      </table>
    </div>
    <div class="note">
      <b>왜 GIN은 합을 쓰는가.</b> 평균과 최댓값은 정보를 잃는다.
      이웃이 {A, A, B}인 노드와 {A, B}인 노드는 평균이 같을 수 있다 — <em>개수를 구분하지 못한다</em>.
      합은 구분한다. 이 차이가 다음 절의 표현력 한계와 직결된다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>표현력의 상한 — 1-WL 검사</h2>
    <p>
      메시지 패싱 GNN에는 <strong>이론적으로 증명된 한계</strong>가 있다.
      이 계열은 <em>1차원 Weisfeiler-Lehman 그래프 동형성 검사</em>보다 강할 수 없다.
    </p>
    <p>
      1-WL은 고전적인 그래프 구분 알고리즘이다. 각 노드에 색을 주고,
      매 라운드마다 "내 색 + 이웃 색들의 다중집합"을 해시해 새 색으로 삼는다.
      두 그래프의 색 분포가 갈라지면 서로 다른 그래프다.
    </p>
    <p>
      메시지 패싱이 하는 일이 정확히 이것과 같은 형태이므로,
      <strong>1-WL이 구분하지 못하는 두 그래프는 GNN도 구분하지 못한다.</strong>
      대표적인 예가 <em>정규 그래프</em>다 — 모든 노드의 차수가 같으면
      구조가 전혀 달라도(예: 6각형 하나 vs 삼각형 두 개) 모든 노드가 같은 메시지를 주고받아
      영원히 같은 표현에 머문다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 240" role="img" aria-label="메시지 패싱 도식과 표현력 한계. 왼쪽은 중심 노드가 이웃들로부터 메시지를 받아 집계하고 갱신하는 과정이며, 오른쪽은 6각형 하나와 삼각형 두 개처럼 모든 노드의 차수가 2로 같은 두 그래프를 메시지 패싱 GNN이 구분하지 못하는 예다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="gn-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">메시지 패싱 — 한 층</text>

            <g stroke="var(--rule-strong)" stroke-width="1.2">
              <line x1="120" y1="96" x2="52" y2="52"/>
              <line x1="120" y1="96" x2="196" y2="54"/>
              <line x1="120" y1="96" x2="46" y2="140"/>
              <line x1="120" y1="96" x2="190" y2="144"/>
            </g>

            <path d="M64 60 L106 86" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#gn-a)"/>
            <path d="M184 62 L134 86" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#gn-a)"/>
            <path d="M58 132 L106 106" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#gn-a)"/>
            <path d="M178 136 L134 106" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#gn-a)"/>

            <circle cx="52" cy="52" r="14" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="52" y="56" text-anchor="middle" font-size="9" fill="var(--ink-soft)">u₁</text>
            <circle cx="196" cy="54" r="14" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="196" y="58" text-anchor="middle" font-size="9" fill="var(--ink-soft)">u₂</text>
            <circle cx="46" cy="140" r="14" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="46" y="144" text-anchor="middle" font-size="9" fill="var(--ink-soft)">u₃</text>
            <circle cx="190" cy="144" r="14" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="190" y="148" text-anchor="middle" font-size="9" fill="var(--ink-soft)">u₄</text>

            <circle cx="120" cy="96" r="18" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.8"/>
            <text x="120" y="100" text-anchor="middle" font-size="10" fill="var(--accent)">v</text>

            <text x="26" y="184" font-size="9" fill="var(--ink-soft)">h_v ← U( h_v, ⊕ m_u→v )</text>
            <text x="26" y="200" font-size="9" fill="var(--ink-faint)">⊕ 가 순서 무관이라 노드 번호와 무관하다</text>
            <text x="26" y="216" font-size="9" fill="var(--ink-faint)">층을 k 개 쌓으면 k 홉까지 본다</text>

            <line x1="256" y1="24" x2="256" y2="230" stroke="var(--rule)" stroke-width="1"/>

            <text x="286" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--warn)">구분하지 못하는 두 그래프</text>

            <g stroke="var(--rule-strong)" stroke-width="1.3" fill="none">
              <polygon points="356,44 392,64 392,106 356,126 320,106 320,64"/>
            </g>
            <g fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2">
              <circle cx="356" cy="44" r="8"/><circle cx="392" cy="64" r="8"/><circle cx="392" cy="106" r="8"/>
              <circle cx="356" cy="126" r="8"/><circle cx="320" cy="106" r="8"/><circle cx="320" cy="64" r="8"/>
            </g>
            <text x="356" y="150" text-anchor="middle" font-size="9" fill="var(--ink-soft)">6각형 하나</text>

            <g stroke="var(--rule-strong)" stroke-width="1.3" fill="none">
              <polygon points="470,48 496,94 444,94"/>
              <polygon points="560,48 586,94 534,94"/>
            </g>
            <g fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2">
              <circle cx="470" cy="48" r="8"/><circle cx="496" cy="94" r="8"/><circle cx="444" cy="94" r="8"/>
              <circle cx="560" cy="48" r="8"/><circle cx="586" cy="94" r="8"/><circle cx="534" cy="94" r="8"/>
            </g>
            <text x="515" y="150" text-anchor="middle" font-size="9" fill="var(--ink-soft)">삼각형 두 개</text>

            <text x="286" y="180" font-size="9" fill="var(--warn)">모든 노드의 차수가 2 — 주고받는 메시지가 항상 동일하다</text>
            <text x="286" y="196" font-size="9" fill="var(--ink-faint)">연결 관계는 전혀 다르지만 표현이 영원히 같다.</text>
            <text x="286" y="212" font-size="9" fill="var(--ink-faint)">1-WL 검사의 한계가 곧 메시지 패싱 GNN 의 한계다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        메시지 패싱은 <strong>국소 이웃 구조만</strong> 본다.
        차수가 같으면 전역 구조가 달라도 같은 신호를 받는다.
        위치 인코딩을 더하거나 부분 구조를 세어 넣는 방식으로 이 한계를 우회한다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>층을 쌓으면 뭉개진다</h2>
    <p>
      CNN은 수십 층을 쌓는다. GNN은 보통 <strong>2~3층</strong>에서 멈춘다.
      더 쌓으면 성능이 떨어지는데, 두 가지 다른 현상이 원인이다.
    </p>
    <p>
      <strong>과평활화(over-smoothing).</strong>
      메시지 패싱은 본질적으로 이웃과 값을 섞는 연산이다.
      반복하면 확산 방정식처럼 값이 고르게 퍼지고,
      결국 <em>모든 노드의 표현이 서로 비슷해진다</em>.
      노드를 구분해야 하는 과제에서 층을 쌓을수록 구분이 사라지는 역설이 생긴다.
    </p>
    <p>
      <strong>과압축(over-squashing).</strong>
      <code>k</code>홉 떨어진 이웃의 수는 지수적으로 늘어난다.
      그 모든 정보가 <em>고정 크기 벡터 하나</em>로 압축돼 들어와야 한다.
      멀리 있는 정보일수록 병목에 눌려 사라진다. 특히 그래프에 좁은 다리 구조가 있으면 심하다.
    </p>
    <div class="note">
      <b>두 문제의 처방이 다르다.</b> 과평활화에는
      <a href="residual-connections.html">잔차 연결</a>, 정규화, 초기 표현을 다시 섞어주는 방법이 쓰인다 —
      다만 잔차는 <em>최적화</em>를 돕는 장치라 뭉개짐 자체를 없애지는 못하고 늦출 뿐이다.
      과압축은 <em>그래프 구조 자체</em>의 문제라 재배선(rewiring)으로 병목을 완화하거나,
      아예 모든 노드를 연결한 <strong>그래프 트랜스포머</strong>로 옮겨간다 —
      다만 그러면 <code>O(N²)</code> 비용과 함께 "그래프 구조를 어떻게 알려줄 것인가"라는 문제가 새로 생긴다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>어디에 쓰이는가</h2>
    <p>
      GNN은 세 가지 층위의 과제에 쓰인다 —
      <strong>노드</strong> 분류(이 사용자는 봇인가), <strong>엣지</strong> 예측(이 둘은 아는 사이인가),
      <strong>그래프</strong> 전체 분류(이 분자는 독성인가).
    </p>
    <ul>
      <li><strong>신약·재료.</strong> 분자는 원자가 노드, 결합이 엣지인 자연스러운 그래프다. 물성 예측에 표준으로 쓰인다.</li>
      <li><strong>추천.</strong> 사용자-상품 이분 그래프에서 링크를 예측한다. 대규모 서비스에 실제로 배포된 사례가 많다.</li>
      <li><strong>물리 시뮬레이션·기상.</strong> 입자나 격자점을 노드로 두고 상호작용을 학습한다. 기상 예측에서 수치 모델과 겨루는 결과가 나왔다.</li>
      <li><strong>이상 탐지.</strong> 금융 거래망에서 사기 패턴은 <em>개별 거래가 아니라 연결 구조</em>에 나타난다.</li>
    </ul>
    <p>
      다만 정직하게 덧붙일 것이 있다.
      <strong>단순한 기준선이 의외로 강하다.</strong>
      노드 특징만 쓰는 MLP나 라벨 전파 같은 고전적 방법이
      잘 조율되면 GNN과 비슷한 성능을 내는 경우가 벤치마크에서 반복 보고됐다.
      그래프 구조가 <em>실제로 신호를 담고 있는지</em>부터 확인하는 것이 순서다.
    </p>
    <p>
      한 문장으로 줄이면, GNN은 <em>"이웃이 누구인지가 나를 설명한다"</em>는 가정을 구조로 옮긴 것이다.
      그 가정이 맞는 데이터에서는 강력하고, 아닌 곳에서는 비싼 MLP가 된다.
    </p>
  </section>
"""

READING = [
    "Kipf &amp; Welling, <em>Semi-Supervised Classification with Graph Convolutional Networks</em> (arXiv:1609.02907) — GCN. 이 분야의 실질적 출발점.",
    "Gilmer et al., <em>Neural Message Passing for Quantum Chemistry</em> (arXiv:1704.01212) — 메시지 패싱이라는 통합 틀.",
    "Veličković et al., <em>Graph Attention Networks</em> (arXiv:1710.10903) — 이웃에 어텐션을 거는 GAT.",
    "Xu et al., <em>How Powerful are Graph Neural Networks?</em> (arXiv:1810.00826) — GIN과 1-WL 표현력 한계 증명.",
    "Hamilton et al., <em>Inductive Representation Learning on Large Graphs</em> (arXiv:1706.02216) — GraphSAGE. 이웃 샘플링.",
    "Alon &amp; Yahav, <em>On the Bottleneck of Graph Neural Networks and its Practical Implications</em> (arXiv:2006.05205) — 과압축 현상.",
]

write(
    "graph-neural-networks.html",
    title="Graph Neural Networks — 격자도 수열도 아닌 데이터",
    eyebrow="Architecture · Relational Learning · 2016–2026",
    h1="Graph Neural Networks",
    subtitle="격자도 수열도 아닌 데이터 — 이웃이 나를 설명한다",
    dek=(
        "CNN은 이미지가 격자라서, 트랜스포머는 문장이 수열이라서 성립한다. "
        "분자·소셜망·도로망은 둘 다 아니다 — 이웃 수가 제각각이고 순서가 없다. "
        "GNN은 <strong>이웃에게 메시지를 받아 자신을 갱신</strong>하는 구조로 이 제약을 받아들인다. "
        "대신 층을 쌓으면 표현이 뭉개지고, 이론적 표현력에도 상한이 있다."
    ),
    spec=[
        ("전제", "순열 불변성"),
        ("연산", "메시지 → 집계 → 갱신"),
        ("표현력 상한", "1-WL 검사"),
        ("층 수", "보통 2~3층"),
        ("한계", "과평활화 · 과압축"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
