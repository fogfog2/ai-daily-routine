#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0ef", panel="#e6e6e4", ink="#18181a", **{
    "ink-soft": "#515259", "ink-faint": "#808289", "rule": "#d2d2d3",
    "rule-strong": "#aeaeb0", "accent": "#00646b", "accent-fill": "#d4e9eb",
    "accent-line": "#238a92", "muted": "#85868a", "muted-fill": "#dfdfe1", "warn": "#a04628",
})
DARK = dict(paper="#111213", panel="#191a1c", ink="#e7e8ea", **{
    "ink-soft": "#a4a6ab", "ink-faint": "#777980", "rule": "#222325", "rule-strong": "#383a3d",
    "accent": "#48c3cb", "accent-fill": "#0d2a2d", "accent-line": "#2b868d",
    "muted": "#87898f", "muted-fill": "#1b1c1f", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>대부분의 가중치는 놀고 있다</h2>
    <p>
      학습이 끝난 신경망의 가중치 분포를 보면 <strong>0 근처에 몰려 있다</strong>.
      절댓값이 아주 작은 가중치들은 출력에 거의 기여하지 않는다.
      그렇다면 잘라내도 되지 않을까 — 가지치기의 출발점이다.
    </p>
    <p>
      실제로 놀랄 만큼 많이 잘라낼 수 있다.
      정확도를 거의 유지한 채 <strong>가중치의 80~90%를 제거</strong>했다는 결과가
      여러 구조에서 반복 보고됐다.
    </p>
    <p>
      왜 이렇게 남아도는가에 대한 흥미로운 설명이 <strong>복권 가설</strong>이다.
      큰 네트워크는 무작위 초기화 속에 우연히 학습이 잘 되는 <em>부분망</em>을 여럿 품고 있고,
      학습은 사실상 그중 당첨된 것을 찾아내는 과정이라는 관점이다.
      나머지는 그 탐색을 돕는 발판 역할을 하고, 끝나면 필요 없어진다.
    </p>
    <div class="note">
      <b>양자화와는 다른 축이다.</b> 양자화는 <em>각 숫자를 몇 비트로 적을지</em>를 줄이고,
      가지치기는 <em>숫자의 개수 자체</em>를 줄인다.
      둘은 독립적이라 함께 적용할 수 있고, 실무에서도 대개 같이 쓴다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>무엇을 기준으로 자를 것인가</h2>
    <p>
      가장 단순한 기준은 <strong>크기</strong>다. 절댓값이 작은 순서로 잘라낸다.
      값싸고 놀랍도록 잘 작동해서 오랫동안 기본값이었다.
    </p>
    <p>
      더 원리적인 기준은 <em>"이 가중치를 없애면 손실이 얼마나 오르는가"</em>다.
      손실을 2차까지 전개하면 헤시안이 등장한다.
    </p>
    <div class="eq">
      <span class="cap">가중치 하나를 없앨 때의 손실 증가 (OBD/OBS 계열)</span>
      <div class="line">δL ≈ ½ · H<sub>ii</sub> · w<sub>i</sub>²&nbsp;&nbsp;&nbsp;// 1차 항은 수렴점에서 0</div>
      <div class="line">// 크기만 보는 것은 H_ii 를 모두 같다고 가정한 특수 경우</div>
    </div>
    <p>
      전체 헤시안은 파라미터 수의 제곱이라 계산할 수 없다.
      그래서 대각 근사나 층별 근사를 쓴다.
      LLM에서 표준이 된 방법들이 이 계보다 — 층 단위로 입력 활성값의 상관을 이용해
      <em>가중치를 자르면서 남은 가중치를 보정</em>하는 방식이다.
    </p>
    <p>
      LLM에서 특히 잘 작동하는 기준이 하나 더 있다.
      <strong>가중치 크기와 입력 활성값 크기를 함께</strong> 보는 것이다.
      큰 활성값을 받는 연결은 가중치가 작아도 영향이 크기 때문이다.
      이 단순한 조합(Wanda)이 훨씬 무거운 방법과 비슷한 성능을 낸다는 결과가 나왔다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>비정형 희소성의 함정</h2>
    <p>
      여기서 이 분야의 가장 중요한 사실이 나온다.
      <strong>90%를 잘라도 90% 빨라지지 않는다. 대개는 전혀 빨라지지 않는다.</strong>
    </p>
    <p>
      개별 가중치를 아무 데나 0으로 만드는 것을 <strong>비정형 희소성</strong>이라 한다.
      메모리에는 여전히 같은 크기의 밀집 행렬이 있고, 그 안에 0이 흩어져 있을 뿐이다.
      GPU는 밀집 행렬 곱셈에 최적화된 장치라,
      <em>0을 곱하는 것과 다른 수를 곱하는 것의 비용이 같다</em>.
    </p>
    <p>
      희소 행렬 형식으로 저장하면 메모리는 줄지만 다른 문제가 생긴다 —
      인덱스를 함께 저장해야 하고, 접근 패턴이 불규칙해져
      메모리 지역성이 깨진다. 희소도가 <strong>95%를 넘어서야</strong>
      비로소 밀집 연산보다 유리해진다는 것이 통상적인 관찰이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="비정형 희소성과 구조적 희소성의 비교. 비정형은 0이 불규칙하게 흩어져 있어 밀집 연산으로 처리되므로 속도 이득이 없고, 2대4 구조적 희소성은 네 개 중 두 개를 규칙적으로 비워 하드웨어가 압축 형식으로 처리할 수 있다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">비정형 — 0이 흩어져 있다</text>

            <g>
              <rect x="24" y="30" width="132" height="88" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <g fill="var(--accent)" opacity="0.7">
                <rect x="30" y="36" width="14" height="14"/><rect x="80" y="36" width="14" height="14"/>
                <rect x="130" y="36" width="14" height="14"/><rect x="55" y="58" width="14" height="14"/>
                <rect x="105" y="58" width="14" height="14"/><rect x="30" y="80" width="14" height="14"/>
                <rect x="80" y="80" width="14" height="14"/><rect x="130" y="80" width="14" height="14"/>
                <rect x="55" y="98" width="14" height="14"/>
              </g>
              <g stroke="var(--rule)" stroke-width="0.5" fill="none">
                <line x1="49" y1="30" x2="49" y2="118"/><line x1="74" y1="30" x2="74" y2="118"/>
                <line x1="99" y1="30" x2="99" y2="118"/><line x1="124" y1="30" x2="124" y2="118"/>
                <line x1="24" y1="52" x2="156" y2="52"/><line x1="24" y1="74" x2="156" y2="74"/>
                <line x1="24" y1="96" x2="156" y2="96"/>
              </g>
            </g>
            <text x="24" y="136" font-size="8.5" fill="var(--ink-faint)">희소도 90%</text>
            <text x="24" y="156" font-size="8.5" fill="var(--warn)">✗ GPU 는 여전히 밀집 곱셈을 한다</text>
            <text x="24" y="170" font-size="8.5" fill="var(--warn)">✗ 0 을 곱하는 비용 = 다른 수를 곱하는 비용</text>
            <text x="24" y="190" font-size="8.5" fill="var(--ink-faint)">메모리는 줄지만 속도 이득은 거의 없다.</text>
            <text x="24" y="204" font-size="8.5" fill="var(--ink-faint)">95% 를 넘겨야 희소 커널이 유리해진다.</text>

            <line x1="196" y1="26" x2="196" y2="214" stroke="var(--rule)" stroke-width="1"/>

            <text x="220" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">2:4 구조적 — 4칸 중 2칸을 비운다</text>

            <g>
              <rect x="220" y="30" width="176" height="88" fill="var(--muted-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
              <g fill="var(--accent)" opacity="0.75">
                <rect x="224" y="34" width="18" height="14"/><rect x="268" y="34" width="18" height="14"/>
                <rect x="312" y="34" width="18" height="14"/><rect x="356" y="34" width="18" height="14"/>
                <rect x="246" y="56" width="18" height="14"/><rect x="290" y="56" width="18" height="14"/>
                <rect x="334" y="56" width="18" height="14"/><rect x="378" y="56" width="18" height="14"/>
                <rect x="224" y="78" width="18" height="14"/><rect x="268" y="78" width="18" height="14"/>
                <rect x="312" y="78" width="18" height="14"/><rect x="356" y="78" width="18" height="14"/>
                <rect x="246" y="100" width="18" height="14"/><rect x="290" y="100" width="18" height="14"/>
                <rect x="334" y="100" width="18" height="14"/><rect x="378" y="100" width="18" height="14"/>
              </g>
              <g stroke="var(--accent-line)" stroke-width="0.9" fill="none" opacity="0.55">
                <line x1="264" y1="30" x2="264" y2="118"/><line x1="308" y1="30" x2="308" y2="118"/>
                <line x1="352" y1="30" x2="352" y2="118"/>
              </g>
            </g>
            <text x="220" y="136" font-size="8.5" fill="var(--accent)">희소도 50% — 하지만 <tspan fill="var(--accent)">규칙적</tspan>이다</text>
            <text x="220" y="156" font-size="8.5" fill="var(--accent)">✓ 압축 형식 + 인덱스 2비트로 저장</text>
            <text x="220" y="170" font-size="8.5" fill="var(--accent)">✓ Sparse Tensor Core 가 직접 처리</text>
            <text x="220" y="190" font-size="8.5" fill="var(--ink-faint)">Ampere 이후 하드웨어가 지원하며,</text>
            <text x="220" y="204" font-size="8.5" fill="var(--ink-faint)">이론상 최대 2배 처리량을 낸다.</text>

            <line x1="430" y1="26" x2="430" y2="214" stroke="var(--rule)" stroke-width="1"/>

            <text x="454" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">구조적 가지치기 — 통째로</text>

            <g>
              <rect x="454" y="34" width="30" height="76" fill="var(--accent)" opacity="0.6" stroke="var(--rule-strong)" stroke-width="0.8"/>
              <rect x="490" y="34" width="30" height="76" fill="var(--warn)" opacity="0.25" stroke="var(--warn)" stroke-width="1.1" stroke-dasharray="3 2"/>
              <rect x="526" y="34" width="30" height="76" fill="var(--accent)" opacity="0.6" stroke="var(--rule-strong)" stroke-width="0.8"/>
              <rect x="562" y="34" width="30" height="76" fill="var(--warn)" opacity="0.25" stroke="var(--warn)" stroke-width="1.1" stroke-dasharray="3 2"/>
              <rect x="598" y="34" width="30" height="76" fill="var(--accent)" opacity="0.6" stroke="var(--rule-strong)" stroke-width="0.8"/>
            </g>
            <text x="505" y="126" text-anchor="middle" font-size="8" fill="var(--warn)">제거</text>
            <text x="577" y="126" text-anchor="middle" font-size="8" fill="var(--warn)">제거</text>

            <text x="454" y="156" font-size="8.5" fill="var(--accent)">✓ 행렬이 실제로 작아진다</text>
            <text x="454" y="170" font-size="8.5" fill="var(--accent)">✓ 어떤 하드웨어에서도 빨라진다</text>
            <text x="454" y="190" font-size="8.5" fill="var(--warn)">✗ 정확도 손실이 훨씬 크다</text>
            <text x="454" y="204" font-size="8.5" fill="var(--ink-faint)">채널·헤드·층 단위로 자른다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        이 분야의 핵심 긴장이 여기 있다.
        <strong>자유롭게 자를수록 정확도는 잘 유지되지만 빨라지지 않고,
        규칙적으로 자를수록 빨라지지만 정확도를 잃는다.</strong>
        2:4는 그 사이에서 하드웨어 지원을 받는 절충점이다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>구조적 희소성 — 실제로 빨라지는 쪽</h2>
    <p>
      속도를 얻으려면 <strong>규칙적으로</strong> 잘라야 한다. 두 갈래가 있다.
    </p>
    <p>
      <strong>2:4 반구조적 희소성</strong>은 "연속된 4개 중 정확히 2개를 0으로" 라는 제약을 건다.
      희소도는 50%로 고정이지만 패턴이 규칙적이라
      가중치를 절반 크기로 압축하고 어느 자리가 살아 있는지 2비트 인덱스로 표현할 수 있다.
      Ampere 세대 이후 GPU의 Sparse Tensor Core가 이 형식을 직접 처리해
      <em>이론상 최대 2배</em>의 행렬곱 처리량을 낸다.
    </p>
    <p>
      <strong>구조적 가지치기</strong>는 더 나아가 어텐션 헤드, FFN 채널, 층 전체를 통째로 제거한다.
      행렬 자체가 작아지므로 <em>특별한 하드웨어 없이도</em> 확실히 빨라지고 메모리도 준다.
      대신 한 번에 많은 것을 지우므로 정확도 손실이 크고,
      대개 회복을 위한 추가 학습이 필요하다.
    </p>
    <div class="note">
      <b>어텐션 헤드는 생각보다 많이 잘린다.</b> 학습된 트랜스포머에서
      상당수의 헤드를 제거해도 성능이 거의 유지된다는 분석이 여럿 나왔다.
      다수의 층에서 <em>헤드 하나만 남겨도</em> 큰 손실이 없는 경우가 보고됐다.
      다만 어떤 헤드가 중요한지는 층마다 다르고, 과제에 따라서도 달라진다.
    </div>
  </section>

  <section>
    <h2><span class="n">05</span>LLM에서의 현재 위치</h2>
    <p>
      대형 언어모델에서 가지치기의 사정은 조금 다르다.
      <strong>재학습이 사실상 불가능</strong>하기 때문이다.
      수천 GPU-시간이 드는 사전학습을 다시 돌릴 수는 없으니,
      <em>학습 없이 한 번에 자르는</em> 방법이 필요하다.
    </p>
    <p>
      그래서 나온 것이 <strong>사후 가지치기</strong>다. 소량의 보정 데이터만 흘려보내
      층별로 어떤 가중치를 자를지 정하고, 남은 가중치를 조금 조정해 오차를 보상한다.
      SparseGPT는 이 방식으로 재학습 없이 50% 희소화를 달성했고,
      Wanda는 가중치와 활성값의 곱이라는 훨씬 단순한 기준으로 비슷한 결과를 냈다.
    </p>
    <p>
      다만 정직하게 말하면, <strong>LLM 실무에서 가지치기는 양자화보다 덜 쓰인다.</strong>
      이유는 명확하다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>기준</th><th>양자화 (4비트)</th><th>가지치기 (50%)</th></tr>
        </thead>
        <tbody>
          <tr><td>메모리 절감</td><td class="hi">약 4배 · 확실</td><td>2배 · 형식에 의존</td></tr>
          <tr><td>속도 이득</td><td class="hi">대역폭 감소로 직결</td><td>2:4 또는 구조적일 때만</td></tr>
          <tr><td>품질 손실</td><td class="hi">작음</td><td>같은 압축률에서 더 큼</td></tr>
          <tr><td>도구 성숙도</td><td class="hi">높음 (GPTQ·AWQ 등)</td><td>상대적으로 낮음</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      요약하면 가지치기의 교훈은 기술적이면서 동시에 방법론적이다.
      <em>이론적 연산 감소가 실제 속도로 이어지려면 하드웨어가 그 패턴을 처리할 수 있어야 한다.</em>
      FLOPs를 세는 것만으로는 부족하다는 점에서,
      FlashAttention이 메모리 왕복을 세야 한다고 말한 것과 같은 계열의 교훈이다.
    </p>
  </section>
"""

READING = [
    "Han et al., <em>Learning both Weights and Connections for Efficient Neural Networks</em> (arXiv:1506.02626) — 크기 기반 가지치기의 표준 절차.",
    "Frankle &amp; Carbin, <em>The Lottery Ticket Hypothesis</em> (arXiv:1803.03635) — 왜 그렇게 많이 잘려도 되는가.",
    "Frantar &amp; Alistarh, <em>SparseGPT: Massive Language Models Can Be Accurately Pruned in One-Shot</em> (arXiv:2301.00774) — 재학습 없는 사후 가지치기.",
    "Sun et al., <em>A Simple and Effective Pruning Approach for Large Language Models</em> (arXiv:2306.11695) — Wanda. 가중치 × 활성값 기준.",
    "Mishra et al., <em>Accelerating Sparse Deep Neural Networks</em> (arXiv:2104.08378) — 2:4 구조적 희소성과 하드웨어 지원.",
    "Michel et al., <em>Are Sixteen Heads Really Better than One?</em> (arXiv:1905.10650) — 어텐션 헤드의 중복성.",
]

write(
    "pruning-sparsity.html",
    title="Pruning & Sparsity — 쓰지 않는 연결을 잘라내다",
    eyebrow="Inference · Model Compression · 2015–2026",
    h1="Pruning &amp; Sparsity",
    subtitle="쓰지 않는 연결을 잘라내다 — 그런데 왜 빨라지지 않는가",
    dek=(
        "학습된 신경망은 가중치의 80~90%를 잘라내도 정확도를 유지한다. "
        "그런데 <strong>90%를 잘라도 대개 전혀 빨라지지 않는다</strong> — "
        "GPU에게 0을 곱하는 비용과 다른 수를 곱하는 비용이 같기 때문이다. "
        "자유롭게 자를수록 정확도는 지키지만 느리고, 규칙적으로 자를수록 빠르지만 손실이 크다."
    ),
    spec=[
        ("가장 단순한 기준", "가중치 크기"),
        ("LLM 기준", "가중치 × 활성값"),
        ("비정형", "메모리만 · 속도 X"),
        ("2:4 반구조적", "최대 2배 (Ampere+)"),
        ("실무 현황", "양자화가 우세"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
