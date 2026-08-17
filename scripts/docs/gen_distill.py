#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#eff0f2", panel="#e5e6ea", ink="#14161c", **{
    "ink-soft": "#4d505c", "ink-faint": "#7c808c", "rule": "#cfd1d8",
    "rule-strong": "#abadb6", "accent": "#5a3a94", "accent-fill": "#e4dcf3",
    "accent-line": "#7c5cba", "muted": "#84878e", "muted-fill": "#dfe0e4", "warn": "#a04628",
})
DARK = dict(paper="#101116", panel="#18191f", ink="#e6e7ee", **{
    "ink-soft": "#a3a5b2", "ink-faint": "#757885", "rule": "#212228", "rule-strong": "#383a48",
    "accent": "#ad93ec", "accent-fill": "#1e1834", "accent-line": "#7761b8",
    "muted": "#868892", "muted-fill": "#1a1b21", "warn": "#e0865e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>정답만 가르치면 잃는 것</h2>
    <p>
      작은 모델을 만드는 가장 단순한 방법은 작은 모델을 처음부터 학습시키는 것이다.
      그런데 같은 데이터로 학습해도 큰 모델을 따라잡지 못한다.
      지식 증류의 물음은 여기서 나온다 — <em>이미 학습된 큰 모델의 판단을 옮겨 담을 수는 없나.</em>
    </p>
    <p>
      열쇠는 <strong>큰 모델이 내놓는 확률 분포</strong>에 있다.
      개 이미지를 분류할 때 정답 라벨은 <code>[개=1, 고양이=0, 자동차=0]</code>이지만,
      학습된 모델은 <code>[개=0.9, 고양이=0.09, 자동차=0.01]</code> 같은 값을 낸다.
    </p>
    <p>
      이 차이가 중요하다. "고양이일 확률이 자동차보다 9배 높다"는 정보는
      <strong>정답 라벨에는 없는 것</strong>이다. 클래스들이 서로 얼마나 닮았는지,
      즉 모델이 학습한 <em>구조</em>가 거기 담겨 있다.
      Hinton은 이를 <strong>암흑 지식</strong>이라 불렀다.
    </p>
    <div class="note">
      <b>정답 라벨은 정보량이 적다.</b> one-hot 벡터는 "이것이 정답"이라고만 말하고
      나머지 클래스에 대해서는 전부 똑같이 "아니다"라고 한다.
      교사 모델의 출력은 <em>오답들 사이의 순위와 거리</em>까지 알려주므로,
      한 표본당 전달되는 정보가 훨씬 많다.
    </div>
  </section>

  <section>
    <h2><span class="n">02</span>온도 — 작은 확률을 들여다보기</h2>
    <p>
      문제가 하나 있다. 잘 학습된 모델은 대개 <strong>지나치게 확신한다</strong>.
      정답 확률이 0.999이고 나머지가 <code>1e-6</code> 수준이면,
      그 미세한 차이가 손실에 거의 기여하지 못한다. 암흑 지식이 묻혀 버린다.
    </p>
    <p>
      해법이 <strong>온도</strong>다. softmax에 들어가기 전 로짓을 <code>T</code>로 나눈다.
    </p>
    <div class="eq">
      <span class="cap">온도가 붙은 softmax — 분포를 부드럽게 편다</span>
      <div class="line">p<sub>i</sub> = exp( z<sub>i</sub> / T ) / Σ<sub>j</sub> exp( z<sub>j</sub> / T )</div>
      <div class="line">T = 1&nbsp;&nbsp; 원래 분포&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[0.999, 0.0009, 0.0001]</div>
      <div class="line">T = 4&nbsp;&nbsp; 부드러워짐&nbsp;&nbsp;&nbsp;&nbsp;[0.79,&nbsp; 0.14,&nbsp;&nbsp; 0.08]</div>
      <div class="line">T → ∞&nbsp; 균등분포에 수렴</div>
    </div>
    <p>
      온도를 높이면 작은 확률들이 상대적으로 커져 손실에 기여하게 된다.
      학생과 교사 <strong>양쪽에 같은 온도</strong>를 적용해 비교한다.
    </p>
    <div class="eq">
      <span class="cap">증류 손실 — 두 항의 가중합</span>
      <div class="line">L = α · T² · KL( p<sup>T</sup><sub>교사</sub> ‖ p<sup>T</sup><sub>학생</sub> ) + (1−α) · CE( y, p<sub>학생</sub> )</div>
      <div class="line">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ 부드러운 목표 ──────────┘&nbsp;&nbsp;└ 정답 라벨 ──┘</div>
      <div class="line">// T² 를 곱하는 이유: 온도가 그래디언트 크기를 1/T² 로 줄이므로 보정</div>
    </div>
    <p>
      <code>T²</code> 항이 실무적으로 중요하다. 이걸 빼먹으면
      온도를 바꿀 때마다 실질 학습률이 함께 변해 조율이 꼬인다.
    </p>
  </section>

  <section>
    <h2><span class="n">03</span>무엇을 옮길 것인가 — 세 갈래</h2>
    <p>
      출력 분포만 옮기는 것이 전부가 아니다. 증류는 <strong>무엇을 맞추게 하느냐</strong>에 따라 갈린다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>종류</th><th>맞추는 대상</th><th>특징</th></tr>
        </thead>
        <tbody>
          <tr><td>응답 기반</td><td>최종 출력 분포</td><td class="hi">구조가 달라도 가능</td></tr>
          <tr><td>특징 기반</td><td>중간 층의 표현</td><td>더 강한 신호 · 층 대응 필요</td></tr>
          <tr><td>관계 기반</td><td class="hi">표본 사이의 관계</td><td>차원이 달라도 됨</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>응답 기반</strong>이 가장 널리 쓰인다. 교사와 학생의 내부 구조가 전혀 달라도 되고,
      교사가 API 너머에 있어도 출력만 받으면 된다.
    </p>
    <p>
      <strong>특징 기반</strong>은 중간 층의 활성값까지 맞추게 한다.
      신호가 풍부해 성능이 좋지만, "교사의 12층은 학생의 4층에 대응한다"는 식의
      <em>층 매핑을 정해야</em> 하고 차원이 다르면 투영 층이 추가로 필요하다.
    </p>
    <p>
      <strong>관계 기반</strong>은 발상이 다르다. 개별 표현이 아니라
      <em>표본 A와 표본 B가 표현 공간에서 얼마나 떨어져 있는가</em>를 맞추게 한다.
      절대 위치가 아니라 상대 구조를 옮기므로 차원 불일치 문제가 사라진다.
    </p>
    <div class="note">
      <b>DistilBERT가 좋은 사례다.</b> 교사의 층을 하나 걸러 하나씩 가져와 학생을 초기화하고,
      증류 손실·마스크 언어모델 손실·<em>임베딩 코사인 유사도 손실</em> 세 개를 함께 걸었다.
      결과는 파라미터 40% 감소, 속도 60% 향상, 성능 97% 유지로 보고됐다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>왜 잘 되는가 — 그리고 언제 안 되는가</h2>
    <p>
      증류가 효과적인 이유에 대한 설명은 여럿이다.
    </p>
    <ul>
      <li><strong>정규화 효과.</strong> 부드러운 목표는 라벨 스무딩처럼 작동해 과신을 막는다.</li>
      <li><strong>라벨 노이즈 완화.</strong> 데이터셋의 틀린 라벨을 교사가 이미 걸러낸 판단을 준다.</li>
      <li><strong>정보 밀도.</strong> 표본당 전달되는 정보가 많아 적은 데이터로도 학습이 된다.</li>
      <li><strong>최적화가 쉬워진다.</strong> 교사의 분포가 손실 지형을 부드럽게 만들어 준다는 해석.</li>
    </ul>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 224" role="img" aria-label="정답 라벨과 교사 모델 출력의 정보량 비교. one-hot 라벨은 정답 하나만 표시하고 나머지를 모두 0으로 두지만, 교사의 부드러운 분포는 오답들 사이의 순위와 거리까지 담아 클래스 간 유사 구조를 전달한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="kd-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="26" y="20" font-size="10" letter-spacing="1.2" fill="var(--muted)">정답 라벨 (one-hot)</text>

            <g>
              <rect x="30" y="36" width="30" height="76" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
              <rect x="30" y="36" width="30" height="76" fill="var(--warn)" opacity="0.5"/>
              <text x="45" y="126" text-anchor="middle" font-size="8" fill="var(--ink-soft)">개</text>
              <text x="45" y="30" text-anchor="middle" font-size="8" fill="var(--warn)">1.0</text>

              <rect x="68" y="36" width="30" height="76" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
              <text x="83" y="126" text-anchor="middle" font-size="8" fill="var(--ink-faint)">고양이</text>
              <text x="83" y="30" text-anchor="middle" font-size="8" fill="var(--ink-faint)">0</text>

              <rect x="106" y="36" width="30" height="76" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
              <text x="121" y="126" text-anchor="middle" font-size="8" fill="var(--ink-faint)">자동차</text>
              <text x="121" y="30" text-anchor="middle" font-size="8" fill="var(--ink-faint)">0</text>
            </g>

            <text x="26" y="152" font-size="8.5" fill="var(--warn)">고양이와 자동차가 똑같이 "아니다"</text>
            <text x="26" y="166" font-size="8.5" fill="var(--ink-faint)">클래스 간 관계 정보가 없다</text>

            <line x1="182" y1="26" x2="182" y2="212" stroke="var(--rule)" stroke-width="1"/>

            <text x="208" y="20" font-size="10" letter-spacing="1.2" fill="var(--accent)">교사 출력 (T = 4)</text>

            <g>
              <rect x="212" y="36" width="30" height="76" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
              <rect x="212" y="55" width="30" height="57" fill="var(--accent)" opacity="0.6"/>
              <text x="227" y="126" text-anchor="middle" font-size="8" fill="var(--ink-soft)">개</text>
              <text x="227" y="49" text-anchor="middle" font-size="8" fill="var(--accent)">0.79</text>

              <rect x="250" y="36" width="30" height="76" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
              <rect x="250" y="98" width="30" height="14" fill="var(--accent)" opacity="0.6"/>
              <text x="265" y="126" text-anchor="middle" font-size="8" fill="var(--ink-soft)">고양이</text>
              <text x="265" y="92" text-anchor="middle" font-size="8" fill="var(--accent)">0.14</text>

              <rect x="288" y="36" width="30" height="76" fill="var(--muted-fill)" stroke="var(--rule)" stroke-width="0.8"/>
              <rect x="288" y="107" width="30" height="5" fill="var(--accent)" opacity="0.6"/>
              <text x="303" y="126" text-anchor="middle" font-size="8" fill="var(--ink-soft)">자동차</text>
              <text x="303" y="101" text-anchor="middle" font-size="8" fill="var(--accent)">0.08</text>
            </g>

            <text x="208" y="152" font-size="8.5" fill="var(--accent)">"고양이가 자동차보다 1.7배 가깝다"</text>
            <text x="208" y="166" font-size="8.5" fill="var(--ink-faint)">→ 정답에 없던 구조 정보 (암흑 지식)</text>

            <line x1="360" y1="26" x2="360" y2="212" stroke="var(--rule)" stroke-width="1"/>

            <text x="386" y="20" font-size="10" letter-spacing="1.2" fill="var(--ink-soft)">증류 구조</text>

            <rect x="386" y="36" width="96" height="34" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3"/>
            <text x="434" y="52" text-anchor="middle" font-size="9" fill="var(--ink-soft)">교사 (큰 모델)</text>
            <text x="434" y="64" text-anchor="middle" font-size="8" fill="var(--ink-faint)">얼림 ❄</text>

            <path d="M434 74 L434 96" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#kd-a)"/>
            <text x="444" y="90" font-size="8" fill="var(--accent)">부드러운 목표</text>

            <rect x="386" y="100" width="96" height="34" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="434" y="116" text-anchor="middle" font-size="9" fill="var(--accent)">학생 (작은 모델)</text>
            <text x="434" y="128" text-anchor="middle" font-size="8" fill="var(--accent)">학습</text>

            <rect x="506" y="100" width="80" height="34" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="546" y="121" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">정답 라벨</text>
            <path d="M502 117 L490 117" stroke="var(--rule-strong)" stroke-width="1.2" marker-end="url(#kd-a)"/>

            <text x="386" y="160" font-size="8.5" fill="var(--ink-soft)">L = α·T²·KL(교사‖학생) + (1−α)·CE(정답)</text>
            <text x="386" y="178" font-size="8.5" fill="var(--ink-faint)">교사는 학습하지 않는다 — 신호원일 뿐이다.</text>
            <text x="386" y="192" font-size="8.5" fill="var(--warn)">교사가 너무 크면 오히려 잘 안 옮겨진다</text>
            <text x="386" y="206" font-size="8.5" fill="var(--ink-faint)">(용량 격차 문제 → 조교 모델을 둔다)</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        옮겨지는 것은 정답이 아니라 <strong>클래스 사이의 구조</strong>다.
        그래서 같은 데이터로 처음부터 학습한 작은 모델보다 나은 결과가 나온다 —
        학생이 보는 것은 데이터가 아니라 <em>교사가 데이터에서 배운 것</em>이기 때문이다.
      </figcaption>
    </figure>

    <p>
      실패하는 경우도 알려져 있다. <strong>용량 격차</strong>가 너무 크면
      학생이 교사의 함수를 근사할 수 없어 증류가 오히려 해가 된다.
      처방은 <em>조교 모델</em>을 중간에 두고 단계적으로 증류하는 것이다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>LLM 시대의 증류</h2>
    <p>
      대형 언어모델에서는 증류의 의미가 조금 달라졌다.
      어휘가 수만 개라 전체 확률 분포를 다루는 비용이 크고,
      무엇보다 <strong>교사가 API 뒤에 있어</strong> 로짓을 못 받는 경우가 많다.
    </p>
    <p>
      그래서 실무에서 "증류"라 부르는 것 중 상당수는 <strong>출력 텍스트를 그대로 쓰는</strong>
      방식이다. 강한 모델에게 답을 생성시켜 그것으로 작은 모델을 SFT한다.
      엄밀히는 분포를 옮기는 게 아니라 <em>합성 데이터 생성</em>에 가깝다.
    </p>
    <div class="note">
      <b>이 방식의 한계는 앞서 지적된 바 있다.</b> 강한 모델의 출력을 흉내 내면
      <em>말투와 형식은 빠르게 닮지만 사실성과 추론 능력은 따라오지 않는다</em>는 분석이 있다.
      벤치마크 점수가 오르는 것과 실제 능력이 오르는 것이 갈리는 대표적 지점이다.
    </div>
    <p>
      더 정교한 접근도 나왔다. <strong>사고 사슬 증류</strong>는 답만이 아니라
      <em>추론 과정 전체</em>를 학습시킨다. 큰 모델이 단계별 풀이를 생성하고,
      작은 모델이 그 과정을 따라 하게 한다.
      최근 소형 추론 모델들이 이 방식으로 만들어졌다.
      교사의 추론 능력 자체가 어떻게 만들어졌는지는 한 층 아래 이야기다 —
      대개 <a href="rlvr.html">검증 가능한 보상으로 돌린 강화학습</a>의 산물이고,
      증류는 그 결과를 작은 모델로 옮기는 단계다.
    </p>
    <p>
      또 하나 흥미로운 갈래는 <strong>확산 모델 증류</strong>다.
      수십 단계가 필요한 확산 모델을 1~4단계로 줄이는데,
      여기서 교사는 "다단계 샘플링 과정"이고 학생은 그 결과를 한 번에 내도록 학습된다.
      이때 적대적 손실을 함께 쓰는 것이 표준이 됐다 — GAN의 발상이 부품으로 들어온 자리다.
    </p>
    <p>
      정리하면 증류의 핵심은 변하지 않았다 —
      <em>학습된 모델의 판단은 원본 데이터보다 정보가 풍부하다.</em>
      다만 무엇을 어떻게 옮길지가 대상에 따라 계속 다시 설계되고 있다.
    </p>
  </section>
"""

READING = [
    "Hinton et al., <em>Distilling the Knowledge in a Neural Network</em> (arXiv:1503.02531) — 원 논문. 온도와 암흑 지식.",
    "Sanh et al., <em>DistilBERT, a distilled version of BERT</em> (arXiv:1910.01108) — 40% 작고 60% 빠르며 97% 성능.",
    "Romero et al., <em>FitNets: Hints for Thin Deep Nets</em> (arXiv:1412.6550) — 중간 층 특징 증류.",
    "Park et al., <em>Relational Knowledge Distillation</em> (arXiv:1904.05068) — 표본 간 관계를 옮기는 방식.",
    "Mirzadeh et al., <em>Improved Knowledge Distillation via Teacher Assistant</em> (arXiv:1902.03393) — 용량 격차 문제와 조교 모델.",
    "Hsieh et al., <em>Distilling Step-by-Step!</em> (arXiv:2305.02301) — 추론 과정까지 증류.",
]

write(
    "knowledge-distillation.html",
    title="Knowledge Distillation — 큰 모델의 판단을 옮겨 담다",
    eyebrow="Inference · Model Compression · 2015–2026",
    h1="Knowledge Distillation",
    subtitle="큰 모델의 판단을 옮겨 담다 — 정답보다 풍부한 신호",
    dek=(
        "정답 라벨은 \"이것이 답\"이라고만 말한다. "
        "학습된 모델의 출력은 <strong>오답들 사이의 순위와 거리</strong>까지 담고 있다 — "
        "고양이가 자동차보다 개에 가깝다는 정보다. "
        "증류는 이 <em>암흑 지식</em>을 작은 모델로 옮긴다. "
        "그래서 같은 데이터로 처음부터 학습하는 것보다 나은 결과가 나온다."
    ),
    spec=[
        ("옮기는 것", "확률 분포 (구조)"),
        ("핵심 장치", "온도 T"),
        ("보정", "그래디언트에 T² 곱"),
        ("실패 조건", "용량 격차 과대"),
        ("LLM 실무", "출력 텍스트 SFT"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
