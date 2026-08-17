#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0f1", panel="#e7e5e8", ink="#191519", **{
    "ink-soft": "#554e57", "ink-faint": "#847d87", "rule": "#d5d0d6",
    "rule-strong": "#b1aab3", "accent": "#6d3a7e", "accent-fill": "#eddef2",
    "accent-line": "#8f5da0", "muted": "#84868d", "muted-fill": "#dfe0e3", "warn": "#a04a26",
})
DARK = dict(paper="#121016", panel="#1a171d", ink="#eae5ec", **{
    "ink-soft": "#aba3b0", "ink-faint": "#7c7482", "rule": "#262029", "rule-strong": "#3c3542",
    "accent": "#c68fd8", "accent-fill": "#2a1832", "accent-line": "#96609f",
    "muted": "#87898f", "muted-fill": "#1b1c20", "warn": "#e0865c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>한 토큰에 담을 수 있는 계산량</h2>
    <p>
      트랜스포머가 토큰 하나를 생성할 때 하는 계산은 <strong>고정</strong>돼 있다.
      층 수만큼의 순전파, 그것이 전부다.
      어려운 질문이든 쉬운 질문이든 토큰 하나에 쓰는 연산은 같다.
    </p>
    <p>
      그렇다면 <em>여러 단계의 계산이 필요한 문제</em>는 어떻게 되는가.
      "23 × 47은?"이라면 곧바로 답을 내야 하고,
      중간 계산을 할 자리가 없다.
    </p>
    <p>
      사고 사슬의 발상은 여기서 나온다 — <strong>중간 과정을 출력하게 하면
      그 토큰들이 곧 계산 공간이 된다.</strong>
      모델은 자기가 쓴 중간 결과를 다시 읽어 다음 단계를 진행할 수 있다.
      토큰을 더 쓰는 만큼 <em>더 많은 순전파</em>를 하게 되는 셈이다.
    </p>
    <div class="eq">
      <span class="cap">한 줄 추가가 만든 차이 (Wei et al. 2022)</span>
      <div class="line">표준 프롬프트:&nbsp; 질문 → 답</div>
      <div class="line">CoT 프롬프트:&nbsp;&nbsp; 질문 → <strong>단계별 풀이</strong> → 답</div>
      <div class="line">&nbsp;</div>
      <div class="line">GSM8K (초등 수학 문장제), PaLM 540B</div>
      <div class="line">&nbsp;&nbsp;표준 few-shot&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;약 18%</div>
      <div class="line">&nbsp;&nbsp;CoT few-shot&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;약 <strong>57%</strong></div>
    </div>
    <p>
      모델도, 파라미터도 그대로다. 바뀐 것은 <em>프롬프트에 넣은 예시의 형식</em>뿐이다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>"단계별로 생각해 봅시다"</h2>
    <p>
      더 놀라운 것은 예시조차 필요 없다는 발견이었다.
      Kojima 등은 질문 뒤에 <strong>한 문장</strong>만 덧붙였다 —
      <em>"Let's think step by step."</em>
    </p>
    <p>
      예시 없이(zero-shot) 이 문장 하나로 GSM8K 정확도가
      한 자릿수에서 수십 퍼센트로 뛰었다.
      논문 제목이 그래서 <em>"Large Language Models are Zero-Shot Reasoners"</em>다.
    </p>
    <p>
      이 결과가 시사하는 바가 중요하다.
      <strong>추론 능력은 이미 모델 안에 있었고, 그것을 꺼내는 문이 닫혀 있었을 뿐</strong>이다.
      사전학습 데이터에는 단계적으로 풀이를 적은 문서가 많다 —
      교과서, 해설, 튜토리얼. 저 문장이 모델을 그런 문서의 문맥으로 밀어 넣는다.
    </p>
    <div class="note">
      <b>이것은 in-context learning과 같은 이야기다.</b>
      <a href="in-context-learning.html">ICL 문서</a>에서 봤듯 프롬프트는
      <em>새 능력을 가르치는 것이 아니라 어떤 능력을 쓸지 지정</em>한다.
      CoT도 마찬가지다 — 없던 추론을 만드는 것이 아니라
      <strong>"단계적으로 풀이를 적는 문서"라는 모드를 켜는 것</strong>이다.
    </div>
    <p>
      규모 의존성도 분명하다. 작은 모델에서는 CoT가 오히려 성능을 <em>떨어뜨린다</em>.
      틀린 중간 단계를 만들어 놓고 그것을 근거로 삼아 더 확실히 틀린다.
      대략 <strong>100B 규모</strong>를 넘어서면서 이득이 나타나기 시작한다는 것이
      원 논문의 관찰이다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>여러 번 풀고 다수결 — 자기 일관성</h2>
    <p>
      CoT의 약점은 <strong>한 번의 실수가 전체를 망친다</strong>는 것이다.
      3단계에서 계산을 틀리면 이후는 전부 무의미해진다.
      탐욕적 디코딩은 경로 하나만 따라가므로 이 위험에 그대로 노출된다.
    </p>
    <p>
      <strong>자기 일관성</strong>은 단순한 해법을 쓴다 —
      온도를 올려 <em>여러 개의 풀이를 생성</em>하고, 최종 답이 가장 많이 나온 것을 고른다.
    </p>
    <div class="eq">
      <span class="cap">자기 일관성 — 경로는 여럿, 답은 하나</span>
      <div class="line">① 같은 질문에 대해 k 개의 풀이를 샘플링 (온도 &gt; 0)</div>
      <div class="line">② 각 풀이에서 <strong>최종 답만</strong> 추출</div>
      <div class="line">③ 가장 빈도가 높은 답을 채택 (다수결)</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 전제: 맞는 답에 이르는 경로는 여러 갈래지만</div>
      <div class="line">//&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;틀리는 방식은 제각각이라 흩어진다</div>
    </div>
    <p>
      전제가 핵심이다. 정답은 <em>수렴</em>하고 오답은 <em>발산</em>한다.
      서로 다른 풀이가 같은 답에 도달했다면 그 답은 신뢰할 만하다.
      GSM8K에서 이 방법만으로 10포인트 이상 오른다고 보고됐다.
    </p>
    <p>
      비용은 <code>k</code>배다. 그래서 이것은 <strong>추론 시간 연산을 정확도로 바꾸는 손잡이</strong>가 된다.
      학습을 더 하지 않고도, 돈을 더 쓰면 더 잘하게 만들 수 있다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>추론 시간 스케일링</h2>
    <p>
      이 관점이 최근 몇 년의 가장 큰 흐름 중 하나로 이어진다.
      전통적 스케일링은 <em>학습</em>에 자원을 넣는 것이었다 —
      파라미터를 늘리고 데이터를 늘린다.
      CoT와 자기 일관성이 보여준 것은 <strong>추론에 자원을 넣는 축</strong>이 따로 있다는 사실이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="추론 시간 스케일링의 세 단계 비교. 단일 경로는 한 번에 답하고, 자기 일관성은 여러 경로를 샘플링해 다수결하며, 추론 모델은 긴 사고 과정 안에서 스스로 검토하고 되돌아간다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="ct-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="ct-m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--muted)">단일 경로</text>
            <circle cx="40" cy="60" r="9" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <path d="M52 60 L84 60" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#ct-m)"/>
            <circle cx="96" cy="60" r="9" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <path d="M108 60 L140 60" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#ct-m)"/>
            <circle cx="152" cy="60" r="9" fill="var(--warn)" opacity="0.6"/>
            <text x="24" y="96" font-size="8.5" fill="var(--warn)">한 단계만 틀려도 전부 무너진다</text>
            <text x="24" y="110" font-size="8.5" fill="var(--ink-faint)">비용 1배</text>

            <line x1="192" y1="26" x2="192" y2="130" stroke="var(--rule)" stroke-width="1"/>

            <text x="216" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">자기 일관성</text>
            <circle cx="228" cy="60" r="9" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
            <path d="M238 54 L268 36" stroke="var(--accent-line)" stroke-width="1.1" marker-end="url(#ct-a)"/>
            <path d="M240 60 L268 60" stroke="var(--accent-line)" stroke-width="1.1" marker-end="url(#ct-a)"/>
            <path d="M238 66 L268 84" stroke="var(--accent-line)" stroke-width="1.1" marker-end="url(#ct-a)"/>
            <circle cx="280" cy="34" r="8" fill="var(--accent)" opacity="0.55"/>
            <circle cx="280" cy="60" r="8" fill="var(--accent)" opacity="0.55"/>
            <circle cx="280" cy="86" r="8" fill="var(--warn)" opacity="0.45"/>
            <text x="298" y="38" font-size="8" fill="var(--accent)">42</text>
            <text x="298" y="64" font-size="8" fill="var(--accent)">42</text>
            <text x="298" y="90" font-size="8" fill="var(--warn)">17</text>
            <rect x="322" y="46" width="46" height="26" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="345" y="63" text-anchor="middle" font-size="9" fill="var(--accent)">42</text>
            <text x="216" y="96" font-size="8.5" fill="var(--accent)">정답은 수렴하고 오답은 흩어진다</text>
            <text x="216" y="110" font-size="8.5" fill="var(--ink-faint)">비용 k 배</text>

            <line x1="392" y1="26" x2="392" y2="130" stroke="var(--rule)" stroke-width="1"/>

            <text x="416" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">추론 모델</text>
            <rect x="416" y="30" width="240" height="62" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="426" y="46" font-size="8" fill="var(--accent)">시도 → 검토 → "잠깐, 이건 틀렸다" → 되돌아감</text>
            <text x="426" y="60" font-size="8" fill="var(--accent)">→ 다른 방법 시도 → 검산 → 답</text>
            <text x="426" y="80" font-size="8" fill="var(--ink-faint)">긴 사고 과정 자체를 강화학습으로 학습한다</text>
            <text x="416" y="110" font-size="8.5" fill="var(--ink-faint)">비용: 사고 길이에 비례 (수천~수만 토큰)</text>

            <line x1="24" y1="146" x2="674" y2="146" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="168" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">두 개의 스케일링 축</text>
            <text x="24" y="188" font-size="9" fill="var(--ink-faint)">학습 시간 — 파라미터 · 데이터를 늘린다 (한 번 비싸고 이후 고정)</text>
            <text x="24" y="204" font-size="9" fill="var(--accent)">추론 시간 — 생각을 길게 한다 (요청마다 비용, 어려운 문제에만 쓸 수 있다)</text>
            <text x="24" y="220" font-size="8.5" fill="var(--ink-faint)">후자는 <tspan fill="var(--accent)">문제 난이도에 따라 조절 가능</tspan>하다는 점이 실무적으로 중요하다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        같은 모델이라도 <strong>생각할 시간을 얼마나 주느냐</strong>에 따라 성능이 달라진다.
        학습 시간 스케일링과 달리 이 축은 <em>요청 단위로 조절</em>할 수 있어,
        쉬운 질문에는 적게 쓰고 어려운 질문에만 많이 쓰는 것이 가능하다.
      </figcaption>
    </figure>

    <p>
      최근 추론 모델들은 이 축을 정면으로 밀어붙인다.
      프롬프트로 CoT를 유도하는 것이 아니라,
      <strong>긴 사고 과정 자체를 강화학습으로 학습</strong>시킨다.
      검증 가능한 과제(수학·코드)에서 정답 여부를 보상으로 쓰면
      모델이 스스로 <em>검토하고, 되돌아가고, 다른 방법을 시도하는</em> 패턴을 발달시킨다는 것이 확인됐다.
      그 학습이 실제로 어떻게 돌아가는지 —
      채점 프로그램을 보상으로 쓰는 <a href="rlvr.html">RLVR</a>과
      가치망 없이 그룹 평균을 기준선으로 쓰는 GRPO — 는 별도 편에서 다룬다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>사고 사슬은 진짜 이유인가</h2>
    <p>
      마지막으로 중요한 단서를 달아야 한다.
      <strong>모델이 출력한 사고 사슬이 실제 계산 과정이라는 보장은 없다.</strong>
    </p>
    <p>
      Turpin 등의 실험이 이를 잘 보여준다.
      프롬프트에 편향을 심어 두면(예: 예시의 정답을 모두 A로 배치)
      모델은 그 편향을 따라 답하면서, <em>사고 사슬에는 그럴듯한 다른 이유를 적는다</em>.
      <strong>실제로 답을 정한 요인을 설명에서 언급하지 않는다.</strong>
    </p>
    <p>
      즉 사고 사슬은 <em>사후 합리화</em>일 수 있다.
      사람이 직관으로 판단하고 나중에 이유를 붙이는 것과 비슷하다.
      이것이 문제가 되는 이유는 명확하다 —
      우리는 사고 사슬을 읽고 모델을 신뢰할지 판단하는데,
      그 설명이 실제 과정과 다르다면 <strong>투명성이 착시</strong>가 된다.
    </p>
    <div class="note">
      <b>그럼에도 성능이 오르는 것은 사실이다.</b> 두 가지를 구분해야 한다 —
      <em>계산 공간으로서의 기능</em>과 <em>설명으로서의 신뢰성</em>은 별개다.
      중간 토큰이 실제로 계산을 담아 정확도를 올리는 것은 맞지만,
      그 텍스트를 <strong>모델의 진짜 이유로 읽는 것</strong>은 별도의 검증이 필요하다.
      해석가능성 연구가 이 간극을 다루는 이유이기도 하다.
    </div>
    <p>
      정리하면 CoT의 기여는 두 겹이다.
      실용적으로는 <em>추론 시간에 자원을 투입하는 방법</em>을 열었고,
      개념적으로는 <em>토큰이 곧 계산 공간</em>이라는 관점을 정착시켰다.
      다만 그 토큰들이 <strong>모델의 마음을 들여다보는 창</strong>인지는 아직 열린 질문이다.
    </p>
  </section>
"""

READING = [
    "Wei et al., <em>Chain-of-Thought Prompting Elicits Reasoning in Large Language Models</em> (arXiv:2201.11903) — CoT 원 논문과 규모 의존성.",
    "Kojima et al., <em>Large Language Models are Zero-Shot Reasoners</em> (arXiv:2205.11916) — \"Let's think step by step\".",
    "Wang et al., <em>Self-Consistency Improves Chain of Thought Reasoning</em> (arXiv:2203.11171) — 다수결 투표.",
    "Turpin et al., <em>Language Models Don't Always Say What They Think</em> (arXiv:2305.04388) — 사고 사슬의 비충실성.",
    "Snell et al., <em>Scaling LLM Test-Time Compute Optimally</em> (arXiv:2408.03314) — 추론 시간 연산 배분의 최적화.",
    "Yao et al., <em>Tree of Thoughts: Deliberate Problem Solving with Large Language Models</em> (arXiv:2305.10601) — 선형 사슬을 탐색 구조로 확장.",
]

write(
    "chain-of-thought.html",
    title="Chain-of-Thought — 생각할 시간을 주다",
    eyebrow="Application · Reasoning · 2022–2026",
    h1="Chain-of-Thought",
    subtitle="생각할 시간을 주다 — 토큰이 곧 계산 공간이다",
    dek=(
        "토큰 하나에 쓰는 연산은 고정돼 있다. 어려운 질문에도 계산할 자리가 없다. "
        "중간 과정을 출력하게 하면 <strong>그 토큰들이 계산 공간이 된다</strong> — "
        "모델은 자기가 쓴 것을 다시 읽어 다음 단계로 간다. "
        "\"단계별로 생각해 봅시다\" 한 문장이 정확도를 몇 배로 올린 이유다. "
        "다만 그 설명이 실제 이유인지는 별개의 문제다."
    ),
    spec=[
        ("바뀌는 것", "프롬프트 형식뿐"),
        ("GSM8K (PaLM 540B)", "18% → 57%"),
        ("자기 일관성", "k개 샘플 다수결"),
        ("규모 조건", "약 100B 이상"),
        ("열린 문제", "설명의 충실성"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
