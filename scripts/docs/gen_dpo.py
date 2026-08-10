#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f2", panel="#e6e6ea", ink="#16161c", **{
    "ink-soft": "#4f4f5c", "ink-faint": "#7e7e8c", "rule": "#d1d1d9",
    "rule-strong": "#adadb7", "accent": "#3d3f9e", "accent-fill": "#dfdff5",
    "accent-line": "#6062c0", "muted": "#84868e", "muted-fill": "#dfe0e4", "warn": "#a0442a",
})
DARK = dict(paper="#101017", panel="#18181f", ink="#e6e6ee", **{
    "ink-soft": "#a3a3b2", "ink-faint": "#75757f", "rule": "#212129", "rule-strong": "#37374a",
    "accent": "#9b9df0", "accent-fill": "#1a1a36", "accent-line": "#6062b5",
    "muted": "#868892", "muted-fill": "#1a1a20", "warn": "#e08560",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>강화학습을 걷어낸 자리</h2>
    <p>
      RLHF의 파이프라인은 무겁다. 선호 데이터로 보상 모델을 학습하고,
      그 보상으로 PPO를 돌린다. 모델 네 개가 GPU에 상주하고,
      학습 중에 계속 샘플링을 해야 하며, 하이퍼파라미터가 많고 불안정하다.
    </p>
    <p>
      DPO의 결론은 <strong>그 전부가 필요 없다</strong>는 것이다.
      RLHF가 푸는 목적함수의 최적해를 역으로 풀면 보상이 정책의 함수로 표현되고,
      그것을 선호 확률 식에 대입하면 <em>보상 모델이 소거된다</em>.
      (유도 과정은 <a href="rlhf.html">RLHF 문서</a>에서 다뤘다.)
    </p>
    <div class="eq">
      <span class="cap">DPO 손실 — 남는 것은 두 모델의 로그 비율뿐</span>
      <div class="line">L = − log σ( β·s(y<sub>w</sub>) − β·s(y<sub>l</sub>) )</div>
      <div class="line">s(y) = log π<sub>θ</sub>(y|x) − log π<sub>ref</sub>(y|x)&nbsp;&nbsp;← <strong>암묵적 보상</strong></div>
      <div class="line">// 참조 모델은 고정. 학습되는 것은 π_θ 뿐.</div>
    </div>
    <p>
      형태를 보면 <strong>이진 분류에 가깝다</strong>.
      "선택된 답의 점수를 높이고 기각된 답의 점수를 낮춰라."
      샘플링도, 가치 함수도, 보상 모델도 없다. 지도학습처럼 안정적으로 돈다.
    </p>
    <div class="note">
      <b>보상 모델이 사라진 게 아니라 접혀 들어갔다.</b>
      <code>β·log(π<sub>θ</sub>/π<sub>ref</sub>)</code>가 곧 암묵적 보상이다.
      학습이 끝난 DPO 모델에서 이 값을 계산하면 <em>보상 모델처럼 쓸 수도</em> 있다.
      다른 목표를 세운 것이 아니라 <strong>같은 목표의 다른 풀이법</strong>이다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>실제로 무슨 일이 일어나는가 — 확률이 함께 내려간다</h2>
    <p>
      DPO 학습을 돌려보면 예상 밖의 현상이 관찰된다.
      <strong>기각된 답의 확률만 내려가는 게 아니라 선택된 답의 확률도 함께 내려간다.</strong>
    </p>
    <p>
      손실 식을 보면 이유가 보인다. 최적화 대상은 두 점수의 <em>차이</em>다.
      차이만 벌어지면 손실이 줄어들므로, <strong>둘 다 내려가되 기각 쪽이 더 빨리 내려가는</strong>
      경로도 유효한 해법이다. 실제로 학습은 자주 그 경로를 택한다.
    </p>
    <p>
      결과가 좋지 않다. 선택된 답조차 확률이 낮아지면
      모델은 <em>선호 데이터에 없던 엉뚱한 출력</em> 쪽으로 확률 질량을 옮길 수 있다.
      DPO 학습 후 답변이 짧아지거나 이상해지는 사례들이 여기서 나온다.
    </p>
    <p>
      완화책이 여럿 나왔다.
    </p>
    <ul>
      <li><strong>SFT 손실 병행.</strong> 선택된 답에 대한 일반적인 지도학습 손실을 함께 걸어 확률이 내려가지 못하게 붙든다.</li>
      <li><strong>참조 모델 정합.</strong> 참조 모델이 SFT를 거치지 않은 상태면 학습 초기부터 어긋난다. <em>선호 데이터와 같은 분포로 SFT한 모델</em>을 참조로 써야 한다.</li>
      <li><strong>β 조절.</strong> 작으면 참조에서 멀리 벗어나고, 크면 거의 변하지 않는다.</li>
    </ul>
  </section>

  <section>
    <h2><span class="n">03</span>변형들 — 무엇을 바꿨나</h2>
    <p>
      DPO 이후 손실 함수를 손본 변형이 쏟아졌다. 각각이 겨냥한 문제가 다르다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>이름</th><th>바꾼 지점</th><th>겨냥한 문제</th></tr>
        </thead>
        <tbody>
          <tr><td>IPO</td><td>시그모이드 대신 제곱 손실</td><td>결정론적 선호에서의 과적합</td></tr>
          <tr><td>KTO</td><td class="hi">쌍이 아닌 개별 좋음/나쁨 라벨</td><td>선호 쌍 수집 비용</td></tr>
          <tr><td>ORPO</td><td class="hi">SFT 손실에 odds ratio 항 추가</td><td>참조 모델 자체를 제거</td></tr>
          <tr><td>SimPO</td><td>길이 정규화 · 참조 불필요</td><td>길이 편향</td></tr>
          <tr><td>cDPO</td><td>라벨 스무딩</td><td>선호 라벨의 노이즈</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>KTO</strong>가 실무적으로 흥미롭다. 선호 <em>쌍</em>을 만들려면
      같은 질문에 두 답을 생성하고 비교시켜야 하는데, 서비스 로그에는
      보통 <em>답 하나에 대한 좋아요/싫어요</em>만 있다. KTO는 그 형태를 그대로 쓴다.
    </p>
    <p>
      <strong>ORPO</strong>는 아예 참조 모델을 없앤다.
      SFT 손실에 "선택된 답의 odds가 기각된 답보다 커야 한다"는 항을 더해,
      <em>SFT와 선호 학습을 한 단계로 합친다</em>. 상주 모델이 하나가 된다.
    </p>
    <p>
      <strong>IPO</strong>는 이론적 지적에서 출발한다. Bradley-Terry 가정 아래
      선호가 결정론적이면(항상 A가 B보다 낫다) DPO의 최적해가 발산한다 —
      확률 비를 무한히 벌리려 한다. IPO는 손실 형태를 바꿔 이를 막는다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>길이 편향 — 가장 흔한 실패</h2>
    <p>
      선호 학습 전반에서 가장 자주 관찰되는 부작용은 <strong>답변이 길어지는 것</strong>이다.
      사람 라벨러가 긴 답을 더 자주 선택하는 경향이 있고, 모델은 그 상관을 학습한다.
      "길이"라는 <em>표면적 특징</em>이 "좋음"의 대리 지표가 되어 버린다.
    </p>
    <p>
      이것이 문제인 이유는 정보량이 늘지 않는데 토큰만 늘기 때문이다.
      추론 비용이 오르고, 읽는 사람도 피곤하다.
    </p>
    <div class="eq">
      <span class="cap">SimPO — 평균 로그 확률로 길이를 상쇄</span>
      <div class="line">DPO:&nbsp;&nbsp; s(y) = log π<sub>θ</sub>(y|x) − log π<sub>ref</sub>(y|x)&nbsp;&nbsp;// 길이에 비례해 커짐</div>
      <div class="line">SimPO: s(y) = (1/|y|) · log π<sub>θ</sub>(y|x) − γ&nbsp;&nbsp;&nbsp;// <strong>토큰 수로 나눈다</strong></div>
      <div class="line">// 참조 모델도 필요 없어진다</div>
    </div>
    <p>
      로그 확률은 토큰마다 음수가 더해지므로 <strong>긴 문장일수록 절댓값이 커진다</strong>.
      길이로 나누면 이 효과가 상쇄된다.
      평가 단계에서도 같은 문제가 있어, 길이를 통제한 승률 지표가 표준이 되어가는 중이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="DPO 학습 중 선택된 답과 기각된 답의 로그 확률 변화 그래프. 두 곡선이 모두 아래로 내려가되 기각 쪽이 더 가파르게 내려가, 차이는 벌어지지만 선택된 답의 확률도 함께 낮아지는 현상을 보여준다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--ink-soft)">DPO 학습 중 로그 확률 — 둘 다 내려간다</text>

            <line x1="60" y1="40" x2="60" y2="170" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <line x1="60" y1="170" x2="360" y2="170" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="40" y="52" font-size="8.5" fill="var(--ink-faint)">높음</text>
            <text x="40" y="166" font-size="8.5" fill="var(--ink-faint)">낮음</text>
            <text x="200" y="188" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">학습 스텝 →</text>

            <path d="M60 62 C 130 70, 220 86, 360 100" fill="none" stroke="var(--accent-line)" stroke-width="2"/>
            <text x="368" y="103" font-size="9" fill="var(--accent)">선택 y_w</text>

            <path d="M60 78 C 130 104, 220 138, 360 156" fill="none" stroke="var(--warn)" stroke-width="2"/>
            <text x="368" y="159" font-size="9" fill="var(--warn)">기각 y_l</text>

            <line x1="300" y1="94" x2="300" y2="148" stroke="var(--ink-faint)" stroke-width="1" stroke-dasharray="3 2"/>
            <text x="308" y="126" font-size="8.5" fill="var(--ink-soft)">차이는 벌어짐 ✓</text>

            <path d="M76 66 L76 96" stroke="var(--accent-line)" stroke-width="1.2" stroke-dasharray="2 2"/>
            <text x="84" y="86" font-size="8.5" fill="var(--warn)">선택된 답도 내려감 ✗</text>

            <line x1="404" y1="30" x2="404" y2="200" stroke="var(--rule)" stroke-width="1"/>

            <text x="428" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">왜 문제인가</text>

            <text x="428" y="48" font-size="9" fill="var(--ink-soft)">손실은 <tspan fill="var(--accent)">차이</tspan>만 본다.</text>
            <text x="428" y="64" font-size="9" fill="var(--ink-faint)">둘 다 내려가도 손실은 줄어든다.</text>

            <text x="428" y="90" font-size="9" fill="var(--ink-soft)">선택된 답의 확률까지 낮아지면</text>
            <text x="428" y="106" font-size="9" fill="var(--ink-faint)">확률 질량이 <tspan fill="var(--warn)">데이터에 없던 출력</tspan>으로</text>
            <text x="428" y="120" font-size="9" fill="var(--ink-faint)">옮겨갈 수 있다.</text>

            <rect x="428" y="136" width="230" height="1" fill="var(--rule)"/>

            <text x="428" y="158" font-size="9" fill="var(--accent)">완화책</text>
            <text x="428" y="174" font-size="8.5" fill="var(--ink-faint)">· SFT 손실을 함께 걸어 붙든다</text>
            <text x="428" y="188" font-size="8.5" fill="var(--ink-faint)">· 참조 모델을 선호 분포에 맞춰 SFT</text>
            <text x="428" y="202" font-size="8.5" fill="var(--ink-faint)">· ORPO 처럼 SFT 와 한 단계로 합친다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        DPO의 목적함수는 <strong>상대적 차이</strong>만 규정한다.
        절대 수준을 붙들어 두는 항이 없다는 것이 이 계열의 구조적 특징이고,
        변형들 상당수가 결국 <em>그 자유도를 어떻게 묶을 것인가</em>를 다룬다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>온라인이냐 오프라인이냐</h2>
    <p>
      DPO의 근본적 제약은 <strong>고정된 데이터셋을 쓴다</strong>는 것이다.
      학습이 진행돼 정책이 변해도 선호 데이터는 그대로다.
      정책이 데이터 분포를 벗어난 답을 내기 시작하면 <em>그 영역에 대한 신호가 없다</em>.
    </p>
    <p>
      PPO는 이 점이 다르다. 보상 모델이 살아 있으므로
      <strong>현재 정책이 방금 만든 답</strong>에 즉시 점수를 줄 수 있다.
      잘 튜닝된 PPO가 여전히 더 높은 천장을 보인다는 보고가 이어지는 이유다.
    </p>
    <p>
      절충안이 <strong>반복적/온라인 DPO</strong>다.
      현재 정책으로 답을 생성하고, 그것을 사람이나 심판 모델이 비교해 새 선호 쌍을 만들고,
      다시 DPO를 돌린다. 이 순환을 몇 번 반복한다.
      PPO의 온라인성을 얻으면서 DPO의 안정성을 유지하려는 시도다.
    </p>
    <div class="note">
      <b>어느 쪽을 쓸지는 자원이 정한다.</b>
      GPU가 넉넉하고 보상 모델을 잘 만들 수 있으면 PPO 계열이 유리하고,
      제한된 자원에서 빠르게 정렬하려면 DPO 계열이 압도적으로 실용적이다.
      오픈소스 모델 대부분이 DPO 계열을 쓰는 것은 <em>이론적 우위 때문이 아니라
      두 장의 GPU로 돌아가기 때문</em>이다.
    </div>
    <p>
      마지막으로 두 방법 모두 공유하는 한계가 있다.
      <strong>선호 데이터의 질을 넘어설 수 없다.</strong>
      라벨러가 길고 정중한 답을 선호하면 모델도 그렇게 된다.
      알고리즘을 바꾸는 것은 <em>번역의 정확도</em>를 높이는 일이지,
      원본을 바꾸는 일이 아니다.
    </p>
  </section>
"""

READING = [
    "Rafailov et al., <em>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</em> (arXiv:2305.18290) — DPO 원 논문.",
    "Azar et al., <em>A General Theoretical Paradigm to Understand Learning from Human Preferences</em> (arXiv:2310.12036) — IPO. 결정론적 선호에서의 발산 문제.",
    "Ethayarajh et al., <em>KTO: Model Alignment as Prospect Theoretic Optimization</em> (arXiv:2402.01306) — 쌍이 아닌 개별 라벨.",
    "Hong et al., <em>ORPO: Monolithic Preference Optimization without Reference Model</em> (arXiv:2403.07691) — 참조 모델 제거.",
    "Meng et al., <em>SimPO: Simple Preference Optimization with a Reference-Free Reward</em> (arXiv:2405.14734) — 길이 정규화.",
    "Xu et al., <em>Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study</em> (arXiv:2404.10719) — 온라인·오프라인 비교.",
]

write(
    "dpo-alignment.html",
    title="DPO — 보상 모델을 지워버린 정렬",
    eyebrow="Alignment · Preference Optimization · 2023–2026",
    h1="DPO",
    subtitle="보상 모델을 지워버린 정렬 — 그리고 그 대가",
    dek=(
        "DPO는 RLHF의 최적해를 역산해 <strong>보상 모델도 강화학습도 없이</strong> "
        "같은 목표에 도달한다. 모델 넷이 둘로 줄고 학습이 지도학습처럼 안정된다. "
        "다만 손실이 <em>차이</em>만 규정하기 때문에 "
        "선택된 답의 확률까지 함께 내려가는 현상이 생긴다 — "
        "쏟아진 변형들 상당수가 결국 그 자유도를 묶는 이야기다."
    ),
    spec=[
        ("상주 모델", "2개 (정책·참조)"),
        ("암묵적 보상", "β·log(π_θ/π_ref)"),
        ("알려진 현상", "선택 확률 동반 하락"),
        ("흔한 편향", "길이"),
        ("구조적 제약", "오프라인 (고정 데이터)"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
