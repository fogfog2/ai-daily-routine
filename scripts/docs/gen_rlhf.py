#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1ee", panel="#e5e7e2", ink="#151812", **{
    "ink-soft": "#4f564a", "ink-faint": "#7d8577", "rule": "#d1d4cc",
    "rule-strong": "#adb2a5", "accent": "#2f6b3c", "accent-fill": "#dceadf",
    "accent-line": "#4a8c58", "muted": "#828790", "muted-fill": "#dee1e4", "warn": "#a34b28",
})
DARK = dict(paper="#101210", panel="#181b17", ink="#e6ebe3", **{
    "ink-soft": "#a5ada0", "ink-faint": "#7b8376", "rule": "#232720", "rule-strong": "#39402f",
    "accent": "#6fce85", "accent-fill": "#132618", "accent-line": "#468f58",
    "muted": "#888f97", "muted-fill": "#1b1f22", "warn": "#e08a5f",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>좋은 답에는 정답지가 없다</h2>
    <p>
      사전학습의 목표는 명확하다 — 다음 토큰을 맞힌다. 정답이 데이터에 들어 있다.
      Instruction tuning도 마찬가지다. 사람이 쓴 모범 답안을 따라 하면 된다.
    </p>
    <p>
      그런데 <em>"이 답이 저 답보다 낫다"</em>는 판단은 어디에도 적혀 있지 않다.
      정중함, 유용함, 안전함 같은 것들은 손실 함수로 쓸 수가 없다.
      사람에게 "좋은 답을 써 주세요"라고 시켜서 따라 하게 만드는 것에도 한계가 있다 —
      <strong>사람이 직접 쓰는 것보다 두 답 중 나은 쪽을 고르는 것이 훨씬 쉽고 일관되기 때문</strong>이다.
    </p>
    <p>
      RLHF의 출발점이 여기다. 사람에게 <strong>비교</strong>만 시킨다.
      A와 B 중 어느 쪽이 나은가. 그리고 그 비교들을 <strong>숫자로 된 보상</strong>으로 번역한 뒤,
      그 보상을 최대화하도록 모델을 밀어붙인다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>선호를 보상으로 — Bradley-Terry</h2>
    <p>
      "A가 B보다 낫다"는 이진 판정들로부터 어떻게 연속적인 점수를 만들까.
      해묵은 통계 모형 하나가 정확히 이 일을 한다. <strong>Bradley-Terry 모형</strong>은
      각 항목에 잠재 점수를 부여하고, 비교에서 이길 확률을 점수 차의 시그모이드로 본다.
    </p>
    <div class="eq">
      <span class="cap">보상 모델 학습 — 이긴 쪽 점수를 높이고 진 쪽을 낮춘다</span>
      <div class="line">P(y<sub>w</sub> ≻ y<sub>l</sub> | x) = σ( r(x, y<sub>w</sub>) − r(x, y<sub>l</sub>) )</div>
      <div class="line">L<sub>RM</sub> = − E<sub>(x, y<sub>w</sub>, y<sub>l</sub>)</sub> [ log σ( r(x,y<sub>w</sub>) − r(x,y<sub>l</sub>) ) ]</div>
      <div class="line">// y_w = 선택된 답, y_l = 버려진 답</div>
    </div>
    <p>
      보상 모델 <code>r</code>은 보통 정책 모델과 같은 구조에 스칼라 출력 헤드를 붙인 것이다.
      주목할 점은 <strong>절댓값이 아니라 차이만 학습된다</strong>는 것이다.
      모든 보상에 상수를 더해도 손실은 같으므로, 보상의 절대 크기 자체에는 의미가 없다.
    </p>
    <div class="note">
      <b>여기서 이미 균열이 생긴다.</b> 보상 모델은 사람 선호의 <em>근사</em>일 뿐이다.
      학습 분포 안에서는 잘 맞지만, 정책이 그 분포를 벗어난 답을 만들기 시작하면
      보상 모델의 예측은 신뢰할 수 없어진다. 그런데 강화학습은 <strong>보상이 높은 곳을 정확히 찾아가는</strong> 절차다.
      즉 보상 모델이 잘못 높은 점수를 주는 구석을 기어이 찾아낸다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>PPO와 목줄 역할의 KL</h2>
    <p>
      보상이 생겼으니 강화학습을 돌린다. 언어 모델을 정책으로 보면
      상태는 지금까지의 토큰, 행동은 다음 토큰이다. 표준 선택은 <strong>PPO</strong>다.
    </p>
    <p>
      그런데 보상만 최대화시키면 앞서 말한 <em>보상 해킹</em>이 일어난다.
      보상 모델이 긴 답을 좋아하면 한없이 길어지고, 특정 문구를 좋아하면 그것만 반복한다.
      막는 장치가 <strong>KL 페널티</strong>다.
    </p>
    <div class="eq">
      <span class="cap">RLHF 목표 — 보상을 좇되 원래 모델에서 멀어지지 말 것</span>
      <div class="line">max<sub>π</sub>&nbsp; E<sub>x,y~π</sub> [ r(x,y) ] − β · KL( π(y|x) ‖ π<sub>ref</sub>(y|x) )</div>
      <div class="line">// π_ref = 정렬 전 모델 (SFT 결과). 학습 내내 고정.</div>
      <div class="line">// β 가 작으면 보상 해킹, 크면 아무것도 안 바뀐다.</div>
    </div>
    <p>
      <code>π<sub>ref</sub></code>에서 너무 멀어지면 벌점을 준다.
      "언어 능력은 유지한 채 선호 방향으로만 조금 기울어라"는 요구다.
      실무에서 <code>β</code> 조율은 RLHF에서 가장 손이 많이 가는 부분 중 하나다.
    </p>
    <p>
      운영 부담도 만만치 않다. PPO를 돌리려면 <strong>모델 네 개</strong>를 동시에 들고 있어야 한다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>모델</th><th>역할</th><th>학습</th></tr>
        </thead>
        <tbody>
          <tr><td>정책 (policy)</td><td>답을 생성</td><td class="hi">O</td></tr>
          <tr><td>참조 (reference)</td><td>KL 계산 기준</td><td>X (고정)</td></tr>
          <tr><td>보상 (reward)</td><td>점수 부여</td><td>X (고정)</td></tr>
          <tr><td>가치 (value)</td><td>이득 추정 (PPO용)</td><td class="hi">O</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>DPO — 보상 모델을 지워버리다</h2>
    <p>
      DPO의 물음은 이것이다. <em>보상 모델을 거치지 않고 선호 데이터로 직접 정책을 학습할 수는 없나.</em>
      답은 놀랍게도 "있다"였고, 유도는 두 걸음이면 된다.
    </p>
    <p>
      먼저 위 목적함수의 <strong>최적해가 닫힌 형태로 알려져 있다</strong>.
      KL 제약이 붙은 보상 최대화 문제의 해는 참조 정책을 보상으로 지수 가중한 분포다.
    </p>
    <div class="eq">
      <span class="cap">1단계 — 최적 정책의 형태</span>
      <div class="line">π*(y|x) = (1/Z(x)) · π<sub>ref</sub>(y|x) · exp( r(x,y) / β )</div>
    </div>
    <p>
      여기서 <strong>보상에 대해 역으로 푼다</strong>. 보상을 정책의 함수로 표현하는 것이다.
    </p>
    <div class="eq">
      <span class="cap">2단계 — 보상을 정책으로 바꿔 쓰기</span>
      <div class="line">r(x,y) = β · log( π*(y|x) / π<sub>ref</sub>(y|x) ) + β · log Z(x)</div>
    </div>
    <p>
      이제 이것을 Bradley-Terry 식에 대입한다. <strong>결정적인 일이 벌어진다</strong> —
      보상이 <em>차이</em>로만 등장하므로, 계산 불가능했던 분배함수 <code>log Z(x)</code>가
      같은 <code>x</code>에 대해 동일하여 <strong>소거된다</strong>.
    </p>
    <div class="eq">
      <span class="cap">DPO 손실 — 보상 모델도, 강화학습도 없다</span>
      <div class="line">L<sub>DPO</sub> = − E [ log σ( β·log(π<sub>θ</sub>(y<sub>w</sub>|x)/π<sub>ref</sub>(y<sub>w</sub>|x)) − β·log(π<sub>θ</sub>(y<sub>l</sub>|x)/π<sub>ref</sub>(y<sub>l</sub>|x)) ) ]</div>
      <div class="line">// 모델 4개 → 2개 (정책, 참조). 샘플링도, 가치 함수도 필요 없다.</div>
    </div>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 216" role="img" aria-label="RLHF와 DPO의 파이프라인 비교. RLHF는 선호 데이터로 보상 모델을 학습한 뒤 PPO로 정책을 학습하며 모델 네 개가 필요하고, DPO는 선호 데이터로 정책을 직접 학습하며 모델 두 개만 필요하다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="rl-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
              <marker id="rl-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--muted)">RLHF — 두 단계, 모델 4개</text>

            <rect x="26" y="32" width="92" height="34" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="72" y="48" text-anchor="middle" font-size="9" fill="var(--ink-soft)">선호 데이터</text>
            <text x="72" y="60" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">(y_w ≻ y_l)</text>

            <path d="M126 49 L152 49" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#rl-a)"/>

            <rect x="156" y="32" width="88" height="34" fill="var(--warn)" opacity="0.16" stroke="var(--warn)" stroke-width="1.3"/>
            <text x="200" y="53" text-anchor="middle" font-size="9.5" fill="var(--ink)">보상 모델 r</text>

            <path d="M252 49 L278 49" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#rl-a)"/>

            <rect x="282" y="26" width="150" height="46" fill="var(--warn)" opacity="0.16" stroke="var(--warn)" stroke-width="1.3"/>
            <text x="357" y="44" text-anchor="middle" font-size="9.5" fill="var(--ink)">PPO 루프</text>
            <text x="357" y="58" text-anchor="middle" font-size="8.5" fill="var(--warn)">정책·참조·보상·가치 상주</text>

            <path d="M440 49 L466 49" stroke="var(--muted)" stroke-width="1.3" marker-end="url(#rl-a)"/>
            <rect x="470" y="32" width="88" height="34" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="514" y="53" text-anchor="middle" font-size="9.5" fill="var(--ink-soft)">정렬된 모델</text>

            <text x="576" y="46" font-size="9" fill="var(--warn)">샘플링 필요</text>
            <text x="576" y="60" font-size="9" fill="var(--warn)">불안정 · β 조율</text>

            <line x1="26" y1="94" x2="674" y2="94" stroke="var(--rule)" stroke-width="1"/>

            <text x="26" y="118" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">DPO — 한 단계, 모델 2개</text>

            <rect x="26" y="130" width="92" height="34" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="72" y="146" text-anchor="middle" font-size="9" fill="var(--ink-soft)">선호 데이터</text>
            <text x="72" y="158" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">(같은 데이터)</text>

            <path d="M126 147 L278 147" stroke="var(--accent-line)" stroke-width="1.6" marker-end="url(#rl-b)"/>
            <rect x="150" y="132" width="104" height="16" fill="var(--paper)"/>
            <text x="202" y="144" text-anchor="middle" font-size="8.5" fill="var(--accent)">보상 모델 없음</text>

            <rect x="282" y="124" width="150" height="46" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="357" y="142" text-anchor="middle" font-size="9.5" fill="var(--accent)">DPO 손실로 직접 학습</text>
            <text x="357" y="156" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">정책·참조만 상주</text>

            <path d="M440 147 L466 147" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#rl-b)"/>
            <rect x="470" y="130" width="88" height="34" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
            <text x="514" y="151" text-anchor="middle" font-size="9.5" fill="var(--accent)">정렬된 모델</text>

            <text x="576" y="144" font-size="9" fill="var(--accent)">샘플링 불필요</text>
            <text x="576" y="158" font-size="9" fill="var(--accent)">지도학습처럼 안정</text>

            <text x="26" y="196" font-size="9.5" fill="var(--ink-soft)">보상 모델이 사라진 것이 아니라 <tspan fill="var(--accent)">정책 안에 접혀 들어갔다</tspan> — β·log(π_θ/π_ref) 가 곧 암묵적 보상이다.</text>
            <text x="26" y="210" font-size="9" fill="var(--ink-faint)">같은 목적함수의 다른 풀이법이지, 다른 목표를 세운 것이 아니다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        DPO는 RLHF와 <strong>같은 목적함수</strong>를 푼다. 다만 보상 모델을 명시적으로 두는 대신
        정책 자신의 로그 비율에 접어 넣어, 강화학습 루프 전체를
        <em>이진 분류에 가까운 지도학습</em>으로 바꾼다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>그래서 무엇을 쓰는가</h2>
    <p>
      DPO가 나온 뒤 오픈소스 정렬은 대부분 DPO 계열로 옮겨갔다. 이유는 단순하다 —
      GPU 두 장이면 되고, 학습이 안정적이며, 하이퍼파라미터가 <code>β</code> 하나에 가깝다.
    </p>
    <p>
      그렇다고 PPO가 죽은 것은 아니다. 차이는 <strong>온라인이냐 오프라인이냐</strong>에 있다.
    </p>
    <ul>
      <li><strong>DPO는 고정된 선호 데이터셋을 쓴다.</strong> 학습이 진행돼 정책이 변해도 데이터는 그대로다. 정책이 데이터 분포를 벗어나면 신호가 흐려진다.</li>
      <li><strong>PPO는 현재 정책이 만든 답에 즉시 점수를 받는다.</strong> 보상 모델이 살아 있으므로 새 영역에도 피드백을 줄 수 있다. 잘 튜닝하면 여전히 더 높은 천장을 보인다는 보고가 많다.</li>
      <li><strong>보상 모델은 재사용된다.</strong> 한 번 학습해 두면 여러 정책·여러 실험에 계속 쓸 수 있다. DPO는 매번 데이터에서 다시 시작한다.</li>
    </ul>
    <p>
      실제 대형 모델의 정렬은 대개 <strong>여러 단계의 조합</strong>이다.
      SFT로 형식을 잡고, 선호 학습으로 방향을 맞추고,
      검증 가능한 과제(수학·코드)에는 규칙 기반 보상으로 강화학습을 돌린다.
      마지막 갈래는 사람 선호가 아니라 <em>정답 여부</em>를 보상으로 쓰기 때문에
      보상 해킹의 여지가 훨씬 적고, 최근 추론 모델들이 이 경로를 크게 활용했다.
    </p>
    <div class="note">
      <b>남는 근본 문제는 그대로다.</b> 무엇을 좋은 답으로 볼지는 결국 라벨러가 정한다.
      선호 데이터에 담긴 편향, "길면 좋다"는 식의 표면적 신호,
      정중하지만 회피적인 답을 선호하게 되는 경향은 방법론을 바꾼다고 사라지지 않는다.
      RLHF든 DPO든 <em>사람의 판단을 손실 함수로 번역하는 장치</em>일 뿐이고,
      번역의 원본이 흐리면 결과도 흐리다.
    </div>
  </section>
"""

READING = [
    "Ouyang et al., <em>Training language models to follow instructions with human feedback</em> (arXiv:2203.02155) — InstructGPT. RLHF 3단계 파이프라인의 표준.",
    "Rafailov et al., <em>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</em> (arXiv:2305.18290) — DPO 유도 전문.",
    "Christiano et al., <em>Deep Reinforcement Learning from Human Preferences</em> (arXiv:1706.03741) — 선호 기반 보상 학습의 원형.",
    "Schulman et al., <em>Proximal Policy Optimization Algorithms</em> (arXiv:1707.06347) — PPO 원 논문.",
    "Bai et al., <em>Training a Helpful and Harmless Assistant with RLHF</em> (arXiv:2204.05862) — 유용성·무해성 상충과 보상 모델 규모 효과.",
    "Gao et al., <em>Scaling Laws for Reward Model Overoptimization</em> (arXiv:2210.10760) — 보상 해킹이 일어나는 지점의 정량화.",
]

write(
    "rlhf.html",
    title="RLHF — 선호를 손실 함수로 번역하다",
    eyebrow="Alignment · Preference Learning · 2017–2026",
    h1="RLHF",
    subtitle="선호를 손실 함수로 번역하다 — 그리고 보상 모델을 지운 DPO",
    dek=(
        "\"좋은 답\"은 데이터에 적혀 있지 않다. 사람은 좋은 답을 쓰는 것보다 "
        "<strong>둘 중 나은 쪽을 고르는 일</strong>을 훨씬 잘한다. "
        "RLHF는 그 비교를 보상으로 번역해 강화학습을 돌린다. "
        "DPO는 같은 목적함수를 역산해, 보상 모델도 강화학습도 없이 같은 곳에 도달한다."
    ),
    spec=[
        ("입력", "선호 쌍 (y_w ≻ y_l)"),
        ("보상 모형", "Bradley-Terry"),
        ("제약", "KL(π ‖ π_ref)"),
        ("RLHF 상주", "모델 4개"),
        ("DPO 상주", "모델 2개"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
