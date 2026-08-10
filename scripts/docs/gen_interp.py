#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff0f1", panel="#e5e7e9", ink="#14171b", **{
    "ink-soft": "#4d535a", "ink-faint": "#7c828a", "rule": "#cfd2d6",
    "rule-strong": "#abaeb4", "accent": "#0f6070", "accent-fill": "#d6e9ee",
    "accent-line": "#2d8798", "muted": "#84878d", "muted-fill": "#dfe0e3", "warn": "#a04a28",
})
DARK = dict(paper="#0f1114", panel="#171a1e", ink="#e5e8ec", **{
    "ink-soft": "#a1a7ae", "ink-faint": "#747a82", "rule": "#212528", "rule-strong": "#373d42",
    "accent": "#4fc0d4", "accent-fill": "#0c2830", "accent-line": "#2d8798",
    "muted": "#868a90", "muted-fill": "#191d20", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>왜 안을 봐야 하는가</h2>
    <p>
      모델을 평가하는 방법은 이미 있다 — 입력을 주고 출력을 본다.
      그런데 <a href="evaluation-benchmarks.html">평가 문서</a>에서 봤듯
      행동 관찰에는 한계가 있다. <strong>테스트하지 않은 상황에서 어떻게 행동할지 알 수 없다.</strong>
    </p>
    <p>
      더 구체적인 문제도 있다. <a href="chain-of-thought.html">사고 사슬</a>이
      실제 계산 과정을 반영하지 않을 수 있다는 결과가 나왔다.
      모델에게 "왜 그렇게 답했니"라고 물어 얻는 설명은
      <em>또 하나의 생성물</em>이지 내부 과정의 기록이 아니다.
    </p>
    <p>
      해석가능성은 다른 접근을 택한다 — <strong>가중치와 활성값을 직접 들여다본다.</strong>
      모델이 말하는 것이 아니라 <em>실제로 계산하는 것</em>을 보려는 시도다.
    </p>
    <div class="note">
      <b>두 갈래를 구분해야 한다.</b>
      <em>사후 설명</em>(saliency map, 특징 중요도)은 "무엇이 출력에 영향을 줬는가"를 근사한다.
      <strong>기계적 해석가능성</strong>은 더 야심적이다 —
      신경망을 <em>이해 가능한 알고리즘으로 역공학</em>하려 한다.
      회로를 찾고, 그 회로가 무슨 계산을 하는지 서술하고, 개입해서 검증한다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>중첩 — 뉴런 하나가 여러 뜻을 가진다</h2>
    <p>
      가장 큰 걸림돌은 <strong>다의성</strong>이다.
      뉴런 하나를 골라 언제 활성화되는지 보면,
      전혀 관계없는 개념들에 함께 반응한다 —
      한국어 문장, 특정 코드 패턴, 고양이 이미지에 동시에 켜지는 식이다.
    </p>
    <p>
      이유가 <strong>중첩</strong>(superposition)이다.
      모델이 표현해야 할 개념의 수가 차원 수보다 훨씬 많으면,
      개념 하나에 뉴런 하나를 배정할 수 없다.
      대신 <em>여러 개념을 겹쳐서</em> 저장한다.
    </p>
    <div class="eq">
      <span class="cap">왜 겹쳐 담을 수 있는가</span>
      <div class="line">고차원 공간에서는 <strong>거의 직교하는</strong> 방향을 아주 많이 만들 수 있다</div>
      <div class="line">d 차원에 정확히 직교하는 벡터는 d 개뿐이지만,</div>
      <div class="line">"거의 직교"를 허용하면 <strong>d 보다 훨씬 많이</strong> 담긴다</div>
      <div class="line">&nbsp;</div>
      <div class="line">전제: 개념들이 <em>희소하게</em> 등장한다 (동시에 몇 개만 켜진다)</div>
      <div class="line">→ 간섭이 생겨도 대부분의 경우 문제가 되지 않는다</div>
    </div>
    <p>
      Anthropic의 toy model 연구가 이를 통제된 환경에서 재현했다.
      특징이 희소할수록 모델이 <strong>더 공격적으로 중첩</strong>을 사용한다는 것이 확인됐다.
      중첩은 버그가 아니라 <em>제한된 용량에서의 합리적 전략</em>이다.
    </p>
    <p>
      문제는 이것이 해석을 거의 불가능하게 만든다는 점이다.
      뉴런 단위로 읽으면 의미가 뒤섞여 있어 어떤 서술도 정확하지 않다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>희소 오토인코더 — 겹친 것을 풀어낸다</h2>
    <p>
      돌파구는 <strong>희소 오토인코더</strong>(SAE)였다.
      발상은 <a href="autoencoders-vae.html">오토인코더</a>를 뒤집는 것이다 —
      차원을 <em>줄이는</em> 대신 <strong>크게 늘리되 희소하게</strong> 만든다.
    </p>
    <div class="eq">
      <span class="cap">SAE — 넓히고 희소화한다</span>
      <div class="line">활성값 x ∈ ℝ<sup>d</sup>&nbsp;&nbsp;(예: d = 512)</div>
      <div class="line">f = ReLU( W<sub>enc</sub> x + b )&nbsp;&nbsp;&nbsp;f ∈ ℝ<sup>D</sup>,&nbsp; <strong>D ≫ d</strong>&nbsp;(예: D = 65536)</div>
      <div class="line">x̂ = W<sub>dec</sub> f</div>
      <div class="line">&nbsp;</div>
      <div class="line">L = ‖x − x̂‖² + λ‖f‖<sub>1</sub></div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ 복원 ──┘&nbsp;&nbsp;&nbsp;└ 희소성 벌점 ┘</div>
    </div>
    <p>
      L1 벌점이 핵심이다. <strong>가능한 한 적은 수의 유닛만 켜서</strong> 원본을 복원하라는 요구다.
      그러면 각 유닛이 <em>하나의 개념</em>에 대응하는 쪽으로 학습된다.
      중첩으로 접혀 있던 것을 넓은 공간에 펼쳐 놓는 셈이다.
    </p>
    <p>
      결과는 인상적이었다. 학습된 특징들이 사람이 읽을 수 있는 개념에 대응했다 —
      특정 인물, 프로그래밍 언어의 구문, 감정, 추상적 관계.
      단순한 단어 매칭이 아니라 <em>여러 언어와 여러 표현을 아우르는</em> 개념 단위였다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 224" role="img" aria-label="중첩과 희소 오토인코더 도식. 좁은 활성값 공간에는 여러 개념이 겹쳐 저장돼 뉴런 하나가 여러 뜻을 갖지만, 희소 오토인코더로 차원을 크게 넓히고 희소성을 강제하면 각 유닛이 하나의 개념에 대응하게 된다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="ip-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">중첩 — 뉴런 하나에 여러 개념</text>

            <g>
              <rect x="30" y="34" width="26" height="76" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <rect x="62" y="34" width="26" height="76" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <rect x="94" y="34" width="26" height="76" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
              <rect x="126" y="34" width="26" height="76" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>

              <rect x="30" y="40" width="26" height="18" fill="var(--warn)" opacity="0.55"/>
              <rect x="30" y="64" width="26" height="16" fill="var(--accent)" opacity="0.45"/>
              <rect x="30" y="86" width="26" height="18" fill="var(--accent-line)" opacity="0.5"/>
              <rect x="62" y="46" width="26" height="20" fill="var(--accent)" opacity="0.45"/>
              <rect x="62" y="74" width="26" height="18" fill="var(--warn)" opacity="0.55"/>
              <rect x="94" y="38" width="26" height="22" fill="var(--accent-line)" opacity="0.5"/>
              <rect x="94" y="72" width="26" height="20" fill="var(--accent)" opacity="0.45"/>
              <rect x="126" y="50" width="26" height="18" fill="var(--warn)" opacity="0.55"/>
              <rect x="126" y="80" width="26" height="20" fill="var(--accent-line)" opacity="0.5"/>
            </g>

            <text x="30" y="128" font-size="8" fill="var(--ink-faint)">한 뉴런이 한국어 · 코드 · 고양이에</text>
            <text x="30" y="141" font-size="8" fill="var(--ink-faint)">모두 반응한다 (다의성)</text>
            <text x="30" y="162" font-size="8.5" fill="var(--warn)">개념 수 ≫ 차원 수 이므로</text>
            <text x="30" y="176" font-size="8.5" fill="var(--warn)">겹쳐 담을 수밖에 없다</text>
            <text x="30" y="198" font-size="8" fill="var(--ink-faint)">고차원에서는 "거의 직교"한 방향을</text>
            <text x="30" y="211" font-size="8" fill="var(--ink-faint)">차원 수보다 훨씬 많이 만들 수 있다</text>

            <path d="M186 72 L232 72" stroke="var(--accent-line)" stroke-width="1.6" marker-end="url(#ip-a)"/>
            <text x="209" y="62" text-anchor="middle" font-size="8" fill="var(--accent)">SAE</text>
            <text x="209" y="88" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">D ≫ d</text>

            <text x="250" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">희소 오토인코더 — 넓히고 희소화</text>

            <g>
              <g fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.7">
                <rect x="250" y="34" width="13" height="76"/><rect x="266" y="34" width="13" height="76"/>
                <rect x="282" y="34" width="13" height="76"/><rect x="298" y="34" width="13" height="76"/>
                <rect x="314" y="34" width="13" height="76"/><rect x="330" y="34" width="13" height="76"/>
                <rect x="346" y="34" width="13" height="76"/><rect x="362" y="34" width="13" height="76"/>
                <rect x="378" y="34" width="13" height="76"/><rect x="394" y="34" width="13" height="76"/>
                <rect x="410" y="34" width="13" height="76"/><rect x="426" y="34" width="13" height="76"/>
                <rect x="442" y="34" width="13" height="76"/><rect x="458" y="34" width="13" height="76"/>
                <rect x="474" y="34" width="13" height="76"/><rect x="490" y="34" width="13" height="76"/>
              </g>
              <rect x="282" y="46" width="13" height="64" fill="var(--accent)" opacity="0.75"/>
              <rect x="378" y="62" width="13" height="48" fill="var(--accent)" opacity="0.75"/>
              <rect x="458" y="80" width="13" height="30" fill="var(--accent)" opacity="0.75"/>
            </g>

            <text x="250" y="128" font-size="8" fill="var(--accent)">대부분 0 — 몇 개만 켜진다</text>

            <line x1="250" y1="140" x2="674" y2="140" stroke="var(--rule)" stroke-width="1"/>

            <text x="250" y="160" font-size="8.5" fill="var(--ink-soft)">각 유닛이 하나의 개념에 대응한다</text>
            <text x="250" y="176" font-size="8" fill="var(--ink-faint)">· 여러 언어를 아우르는 개념 단위</text>
            <text x="250" y="189" font-size="8" fill="var(--ink-faint)">· 텍스트와 이미지 양쪽에 반응하기도</text>
            <text x="250" y="211" font-size="8.5" fill="var(--warn)">다만 특징이 몇 개인지는 아무도 모른다 — D 는 우리가 정하는 값이다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        SAE는 <strong>모델을 바꾸지 않는다</strong>. 활성값을 읽어 해석 가능한 좌표계로 옮길 뿐이다.
        결정적 검증은 <em>개입</em>이다 — 특정 특징을 강제로 켜거나 끄면
        모델의 출력이 예측한 대로 바뀌는지 확인한다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>회로 — 특징들이 어떻게 연결되는가</h2>
    <p>
      특징을 찾는 것은 어휘를 얻는 일이다. 다음 물음은 <strong>문법</strong>이다 —
      이 특징들이 어떻게 조합돼 계산을 이루는가.
    </p>
    <p>
      가장 잘 이해된 사례가 <a href="in-context-learning.html">귀납 헤드</a>다.
      두 어텐션 헤드가 협력해 <em>"앞서 A 다음에 B가 왔으니 지금 A 다음도 B"</em>라는
      패턴 복사를 수행한다. 이것이 in-context learning의 밑바닥에 있다는 정황이 제시됐다.
    </p>
    <p>
      회로를 찾는 표준 도구가 <strong>활성값 패칭</strong>이다.
    </p>
    <div class="eq">
      <span class="cap">활성값 패칭 — 인과를 확인하는 절차</span>
      <div class="line">① 정상 입력을 넣고 모든 활성값을 기록한다</div>
      <div class="line">② 살짝 바꾼 입력(오염된 입력)으로 다시 실행한다</div>
      <div class="line">③ 특정 위치의 활성값만 <strong>정상 실행의 값으로 바꿔치기</strong>한다</div>
      <div class="line">④ 출력이 정상 쪽으로 돌아오면 → 그 위치가 <em>인과적으로 중요</em>하다</div>
    </div>
    <p>
      상관이 아니라 <strong>인과</strong>를 본다는 점이 중요하다.
      단순히 "함께 활성화된다"가 아니라
      "이것을 바꾸면 결과가 바뀐다"를 확인하는 것이다.
      이 방법으로 간접 목적어 식별 같은 구체적 과제에서
      어떤 헤드들이 어떤 역할을 나눠 맡는지가 상당히 자세히 밝혀졌다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>어디까지 왔고 무엇이 남았나</h2>
    <p>
      실제로 무엇이 가능해졌는지부터 보자.
    </p>
    <ul>
      <li><strong>개념 조향.</strong> 특정 특징을 강제로 활성화하면 모델의 출력이 그쪽으로 기운다. 특정 개념에 집착하게 만드는 실험이 공개돼 화제가 됐다.</li>
      <li><strong>안전 관련 특징 발견.</strong> 기만, 위험한 코드, 아첨 같은 개념에 대응하는 특징들이 확인됐다. 모니터링에 쓸 가능성이 있다.</li>
      <li><strong>거절 방향.</strong> 모델의 거절 행동이 특정 방향과 연관돼 있고, 그것을 조작하면 행동이 바뀐다는 결과가 나왔다 — 안전장치가 얼마나 얕게 걸려 있을 수 있는지를 보여준다.</li>
    </ul>
    <p>
      한계도 분명하다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>문제</th><th>내용</th></tr>
        </thead>
        <tbody>
          <tr><td>규모</td><td class="hi">특징이 수천만 개일 수 있고, 사람이 다 확인할 수 없다</td></tr>
          <tr><td>특징 수의 임의성</td><td>SAE의 넓이 D 를 우리가 정한다 — 진짜 개수를 모른다</td></tr>
          <tr><td>완결성</td><td class="hi">찾은 회로가 그 과제를 전부 설명하는지 보장이 없다</td></tr>
          <tr><td>자동 해석의 신뢰</td><td>특징 설명을 LLM이 붙이는데, 그 설명 자체를 검증해야 한다</td></tr>
          <tr><td>복원 손실</td><td>SAE 를 끼우면 모델 성능이 조금 떨어진다 — 무언가를 놓치고 있다</td></tr>
        </tbody>
      </table>
    </div>
    <div class="note">
      <b>왜 이 분야에 자원이 투입되는가.</b> 모델의 능력이 올라갈수록
      <em>행동만 보고 신뢰를 판단하기</em>가 어려워진다.
      테스트를 통과했다는 것이 테스트하지 않은 상황에서의 행동을 보장하지 않기 때문이다.
      해석가능성은 <strong>확장성 감독</strong>의 한 갈래로 읽힌다 —
      <a href="constitutional-ai.html">CAI</a>가 판정을 위임하는 방향이었다면,
      이쪽은 <em>내부를 직접 검사하는</em> 방향이다.
    </div>
    <p>
      현재 상태를 정직하게 요약하면 이렇다.
      <strong>신경망이 완전히 불투명하다는 전제는 깨졌다.</strong>
      구체적 회로가 발견됐고, 개입으로 검증됐고, 특징을 조작해 행동을 바꿀 수 있게 됐다.
      다만 그것은 <em>거대한 프로그램의 몇 줄을 읽어낸 것</em>에 가깝고,
      전체를 이해하는 것과는 아직 거리가 멀다.
    </p>
  </section>
"""

READING = [
    "Elhage et al., <em>Toy Models of Superposition</em> (Anthropic, 2022) — 중첩이 왜 생기는지의 통제된 재현.",
    "Bricken et al., <em>Towards Monosemanticity: Decomposing Language Models With Dictionary Learning</em> (Anthropic, 2023) — SAE로 특징을 분리한 첫 대규모 결과.",
    "Templeton et al., <em>Scaling Monosemanticity</em> (Anthropic, 2024) — 실제 배포 규모 모델에서의 특징 추출과 조향.",
    "Olsson et al., <em>In-context Learning and Induction Heads</em> (Anthropic, 2022) — 회로 수준 설명의 대표 사례.",
    "Wang et al., <em>Interpretability in the Wild: a Circuit for Indirect Object Identification in GPT-2 small</em> (arXiv:2211.00593) — 활성값 패칭으로 회로를 특정.",
    "Arditi et al., <em>Refusal in Language Models Is Mediated by a Single Direction</em> (arXiv:2406.11717) — 거절 행동의 표현 수준 분석.",
]

write(
    "interpretability.html",
    title="해석가능성 — 안을 들여다볼 수 있는가",
    eyebrow="Evaluation · Mechanistic Interpretability · 2021–2026",
    h1="해석가능성",
    subtitle="안을 들여다볼 수 있는가 — 겹쳐 담긴 개념을 풀어내기",
    dek=(
        "모델에게 \"왜 그렇게 답했니\"라고 물어 얻는 설명은 "
        "<strong>또 하나의 생성물</strong>이지 내부 과정의 기록이 아니다. "
        "해석가능성은 가중치와 활성값을 직접 본다. "
        "가장 큰 걸림돌은 <em>중첩</em>이었다 — 개념 수가 차원 수보다 많아 "
        "뉴런 하나에 여러 뜻이 겹쳐 담긴다. 희소 오토인코더가 이것을 펼쳐 놓는다."
    ),
    spec=[
        ("보는 대상", "가중치 · 활성값"),
        ("핵심 걸림돌", "중첩 · 다의성"),
        ("돌파구", "희소 오토인코더"),
        ("검증 방법", "개입 (활성값 패칭)"),
        ("남은 문제", "규모 · 완결성"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
