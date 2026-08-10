#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ee", panel="#e8e6e2", ink="#1a1815", **{
    "ink-soft": "#565149", "ink-faint": "#857f76", "rule": "#d5d1cb",
    "rule-strong": "#b1aca4", "accent": "#8c4020", "accent-fill": "#f4dfd3",
    "accent-line": "#b06840", "muted": "#83868d", "muted-fill": "#dee0e3", "warn": "#8a5a12",
})
DARK = dict(paper="#131110", panel="#1c1a16", ink="#ece9e4", **{
    "ink-soft": "#ada79d", "ink-faint": "#7d776e", "rule": "#27231f", "rule-strong": "#3e3931",
    "accent": "#e08a5f", "accent-fill": "#2f1d13", "accent-line": "#a86540",
    "muted": "#87898f", "muted-fill": "#1c1d20", "warn": "#d9a441",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>거짓말이 아니라 구조의 결과</h2>
    <p>
      모델이 존재하지 않는 논문을 인용하고, 없는 API를 그럴듯하게 설명한다.
      흔히 "거짓말한다"고 표현하지만 정확하지 않다.
      <strong>모델에게는 참과 거짓을 구분하는 별도의 기제가 없다.</strong>
    </p>
    <p>
      학습 목표를 되짚으면 분명해진다. 사전학습은 <em>다음 토큰의 확률</em>을 맞히는 일이다.
      "이 문장이 사실인가"를 묻는 항목은 손실 함수 어디에도 없다.
      모델이 최적화한 것은 <strong>그럴듯함</strong>이지 <em>참</em>이 아니다.
    </p>
    <p>
      그리고 대부분의 경우 둘은 일치한다. 학습 데이터가 대체로 사실이므로
      그럴듯한 텍스트는 대체로 사실이다.
      문제는 <strong>둘이 갈라지는 지점</strong>이다 —
      모르는 것을 물었을 때, 모델은 "모른다"보다 <em>그럴듯한 형태</em>를 생성한다.
      존재하지 않는 논문 제목이 진짜 논문 제목처럼 생긴 이유가 이것이다.
    </p>
    <div class="note">
      <b>형식은 맞고 내용만 틀리다.</b> 가짜 인용은 저자명·연도·학회명·arXiv 번호 형식까지
      완벽하게 갖춘다. 모델이 학습한 것은 <em>인용이 어떻게 생겼는가</em>이고,
      그 형식을 채우는 것은 잘한다. 채워 넣을 사실이 없을 때도 형식은 그대로 완성된다.
      환각이 알아채기 어려운 이유가 여기 있다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>어디서 생기는가 — 네 갈래</h2>
    <p>
      환각을 하나로 뭉뚱그리면 대응책이 안 보인다. 발생 지점별로 나누면 처방이 갈린다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>원인</th><th>내용</th><th>대응</th></tr>
        </thead>
        <tbody>
          <tr><td>데이터에 없음</td><td>애초에 학습하지 않은 사실</td><td class="hi">검색으로 문맥 제공</td></tr>
          <tr><td>데이터가 틀림</td><td>학습 데이터 자체의 오류·구식 정보</td><td>데이터 정제 · 출처 명시</td></tr>
          <tr><td>희소한 사실</td><td class="hi">한 번만 등장한 정보는 잘 기억 못 함</td><td>검색 · 신뢰도 표시</td></tr>
          <tr><td>정렬 부작용</td><td class="hi">"모른다"보다 답하도록 학습됨</td><td>거절을 선호 데이터로 학습</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      네 번째가 특히 중요하다. <a href="instruction-tuning.html">SFT</a>는
      <em>모범 답안을 따라 하게</em> 하는 학습이다.
      그 답안에 모델이 실제로 모르는 사실이 들어 있으면,
      모델은 <strong>"모르는 것도 자신 있게 말하는 법"</strong>을 배운다.
      정렬이 환각을 <em>줄이는 것이 아니라 늘릴 수</em> 있다는 지적이 여기서 나온다.
    </p>
    <p>
      학습 데이터에서의 <strong>등장 빈도</strong>도 강한 예측 변수다.
      여러 문서에 반복 등장한 사실은 안정적으로 재현되지만,
      한두 번만 나온 정보는 정확히 기억되지 않는다.
      유명한 사람의 생년은 맞히고 덜 알려진 사람은 지어내는 패턴이 이것이다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>모델은 자기가 모른다는 걸 아는가</h2>
    <p>
      흥미로운 연구 갈래가 있다. <strong>모델 내부에 "이건 확실하지 않다"는 신호가 있는가</strong>다.
      있다면 그것을 읽어 환각을 걸러낼 수 있다.
    </p>
    <p>
      부분적으로는 그렇다는 증거가 쌓였다.
      출력 확률의 엔트로피, 내부 표현에서 학습한 선형 분류기,
      여러 번 생성했을 때의 일관성 등이 정확도와 상관을 보인다.
    </p>
    <div class="eq">
      <span class="cap">자기 일관성으로 환각 탐지하기</span>
      <div class="line">① 같은 질문에 여러 번 답을 생성한다 (온도 &gt; 0)</div>
      <div class="line">② 답들이 <strong>서로 일치</strong>하면 → 실제로 아는 것일 가능성이 높다</div>
      <div class="line">③ 답들이 <strong>제각각</strong>이면 → 지어내고 있을 가능성이 높다</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 사실은 하나뿐이지만, 지어내는 방식은 매번 다르다</div>
    </div>
    <p>
      전제가 <a href="chain-of-thought.html">자기 일관성</a>과 같다 —
      <em>정답은 수렴하고 오답은 발산한다.</em>
      다만 완벽하지 않다. 모델이 <strong>일관되게 틀리는</strong> 경우가 있기 때문이다.
      학습 데이터에 널리 퍼진 오해나, 그럴듯한 오답이 강하게 자리 잡은 경우다.
    </p>
    <p>
      더 근본적인 문제는 <strong>보정</strong>이다.
      사전학습만 마친 모델은 확률이 비교적 잘 보정돼 있다는 관찰이 있는데,
      <em>RLHF를 거치면 이 보정이 나빠진다</em>는 보고가 나왔다.
      정렬이 모델을 <strong>더 자신 있게</strong> 만드는 쪽으로 작용하기 때문이다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>완화 — 제거가 아니라 관리</h2>
    <p>
      실무적으로 가장 효과가 큰 것은 <strong>모델에게 답을 외우게 하지 않는 것</strong>이다.
      필요한 사실을 문맥에 넣어 주면, 모델은 <em>기억을 인출</em>하는 대신
      <em>주어진 것을 읽고 정리</em>하면 된다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 216" role="img" aria-label="환각 완화 방법의 층위. 문맥 제공, 출처 강제, 검증 단계, 거절 학습 순으로 배치되며 위로 갈수록 효과가 크고 구현이 쉽다는 것을 보여준다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="hl-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">완화 수단과 그 한계</text>

            <rect x="26" y="30" width="300" height="38" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="38" y="46" font-size="9" fill="var(--accent)">① 문맥으로 제공 (RAG)</text>
            <text x="38" y="60" font-size="8" fill="var(--ink-soft)">기억 인출 → 읽고 정리하기로 과제를 바꾼다</text>

            <rect x="26" y="76" width="300" height="38" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="38" y="92" font-size="9" fill="var(--ink-soft)">② 출처 인용 강제</text>
            <text x="38" y="106" font-size="8" fill="var(--ink-faint)">문맥에 없는 주장을 억제 · 검증 가능하게 만든다</text>

            <rect x="26" y="122" width="300" height="38" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="38" y="138" font-size="9" fill="var(--ink-soft)">③ 생성 후 검증</text>
            <text x="38" y="152" font-size="8" fill="var(--ink-faint)">주장을 쪼개 하나씩 사실 확인 · 비용이 든다</text>

            <rect x="26" y="168" width="300" height="38" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="38" y="184" font-size="9" fill="var(--ink-soft)">④ 거절을 학습</text>
            <text x="38" y="198" font-size="8" fill="var(--ink-faint)">"모른다"를 선호 데이터로 · 과잉 거절 위험</text>

            <line x1="360" y1="26" x2="360" y2="206" stroke="var(--rule)" stroke-width="1"/>

            <text x="386" y="46" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">그래도 남는 것</text>

            <text x="386" y="72" font-size="8.5" fill="var(--ink-soft)">· 문맥이 <tspan fill="var(--warn)">틀렸으면</tspan> 그대로 따라간다</text>
            <text x="386" y="88" font-size="8.5" fill="var(--ink-soft)">· 문맥에 있는데도 <tspan fill="var(--warn)">잘못 읽는</tspan> 경우</text>
            <text x="386" y="104" font-size="8.5" fill="var(--ink-soft)">· 인용은 붙였으나 <tspan fill="var(--warn)">내용과 무관</tspan>한 경우</text>
            <text x="386" y="120" font-size="8.5" fill="var(--ink-soft)">· 여러 문서를 <tspan fill="var(--warn)">잘못 종합</tspan>하는 경우</text>

            <rect x="386" y="136" width="270" height="1" fill="var(--rule)"/>

            <text x="386" y="158" font-size="8.5" fill="var(--accent)">과잉 거절도 실패다.</text>
            <text x="386" y="174" font-size="8.5" fill="var(--ink-faint)">아는 것까지 "모른다"고 하면 쓸모가 없다.</text>
            <text x="386" y="196" font-size="8.5" fill="var(--ink-faint)">정확도와 응답률은 맞바꾸는 관계이고,</text>
            <text x="386" y="210" font-size="8.5" fill="var(--ink-faint)">어디에 둘지는 용도가 정한다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        완화는 여러 층으로 쌓는 것이지 하나로 해결되지 않는다.
        <strong>검색을 붙여도 환각이 사라지지 않는다</strong> —
        검색 결과가 틀렸거나, 맞는 문서를 잘못 읽거나,
        인용은 달았지만 그 문서가 주장을 뒷받침하지 않는 경우가 남는다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>왜 완전히 없앨 수 없나</h2>
    <p>
      환각을 <em>줄일</em> 수는 있어도 <em>제거</em>할 수 없다는 주장에는 몇 가지 근거가 있다.
    </p>
    <p>
      <strong>첫째, 생성 자체가 확률적이다.</strong>
      모델은 분포에서 샘플링한다. 낮은 확률의 토큰도 언젠가 뽑힌다.
      온도를 0으로 두어도 <em>가장 확률 높은 답이 틀린</em> 경우는 남는다.
    </p>
    <p>
      <strong>둘째, 무엇이 참인지 모델 안에서 정의되지 않는다.</strong>
      모델에는 세계에 대한 접근 권한이 없고, 텍스트 분포만 있다.
      학습 데이터가 널리 공유하는 오해는 모델에게 <em>참과 구별되지 않는다</em>.
    </p>
    <p>
      <strong>셋째, 유용성과 상충한다.</strong>
      확실한 것만 말하게 하면 대부분의 질문에 답하지 못한다.
      추론과 추측 사이에 명확한 선이 없기 때문에,
      <em>추론을 허용하는 한 잘못된 추론도 허용된다.</em>
    </p>
    <div class="note">
      <b>그래서 문제는 "없앨 수 있는가"가 아니라 "어떻게 다룰 것인가"가 된다.</b>
      실무의 방향은 대체로 셋이다 — <em>검증 가능하게 만들기</em>(출처와 인용),
      <em>영향 제한하기</em>(되돌릴 수 없는 작업에는 사람 승인),
      <em>기대치 조정하기</em>(모델 출력을 초안으로 다루기).
      <a href="ai-agents-tool-use.html">에이전트</a>에서 이 문제가 더 커지는 이유도 같다 —
      틀린 정보가 답변에 머무는 것과 <strong>행동으로 옮겨지는 것</strong>은 다르다.
    </div>
    <p>
      마지막으로 용어에 대해 한마디 덧붙이면, "환각"이라는 말 자체가
      <em>모델이 평소에는 사실을 안다</em>는 전제를 깔고 있어 오해를 부른다는 비판이 있다.
      모델은 언제나 같은 일을 하고 있다 — <strong>그럴듯한 다음 토큰을 고르는 것</strong>.
      우리가 환각이라 부르는 것은 <em>그 결과가 사실과 어긋난 경우</em>일 뿐,
      모델 내부에서 다른 모드가 켜진 것이 아니다.
    </p>
  </section>
"""

READING = [
    "Ji et al., <em>Survey of Hallucination in Natural Language Generation</em> (arXiv:2202.03629) — 유형 분류와 원인 정리.",
    "Kandpal et al., <em>Large Language Models Struggle to Learn Long-Tail Knowledge</em> (arXiv:2211.08411) — 등장 빈도와 정확도의 관계.",
    "Schulman, <em>Reinforcement Learning from Human Feedback: Progress and Challenges</em> (2023) — 정렬이 환각을 유도하는 구조.",
    "Manakul et al., <em>SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection</em> (arXiv:2303.08896) — 자기 일관성 기반 탐지.",
    "Kadavath et al., <em>Language Models (Mostly) Know What They Know</em> (arXiv:2207.05221) — 내부 확신 신호의 존재.",
    "Min et al., <em>FActScore: Fine-grained Atomic Evaluation of Factual Precision</em> (arXiv:2305.14251) — 주장 단위 사실성 평가.",
]

write(
    "hallucination.html",
    title="환각 — 왜 그럴듯하게 틀리는가",
    eyebrow="Evaluation · Factuality · 2022–2026",
    h1="환각",
    subtitle="왜 그럴듯하게 틀리는가 — 최적화된 것은 참이 아니라 그럴듯함이다",
    dek=(
        "모델에게는 참과 거짓을 구분하는 기제가 없다. "
        "학습 목표는 다음 토큰의 확률이었고, \"이것이 사실인가\"는 손실 함수에 없었다. "
        "대개는 그럴듯한 것이 사실이라 문제가 없다가, "
        "<strong>모르는 것을 물었을 때 갈라진다</strong> — "
        "모델은 \"모른다\" 대신 형식이 완벽한 가짜를 만든다."
    ),
    spec=[
        ("최적화 대상", "그럴듯함 (참 아님)"),
        ("강한 예측 변수", "학습 데이터 등장 빈도"),
        ("정렬의 역설", "SFT가 자신감을 키운다"),
        ("탐지 단서", "여러 생성의 일관성"),
        ("현실적 목표", "제거 아닌 관리"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
