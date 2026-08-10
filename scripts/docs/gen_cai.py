#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f0ec", panel="#e8e6e0", ink="#1a1712", **{
    "ink-soft": "#565046", "ink-faint": "#857e72", "rule": "#d5d1c9",
    "rule-strong": "#b1aca1", "accent": "#7b4a12", "accent-fill": "#f0e2cd",
    "accent-line": "#a67230", "muted": "#82868e", "muted-fill": "#dee0e3", "warn": "#9a3a26",
})
DARK = dict(paper="#13110e", panel="#1c1a15", ink="#ece8e1", **{
    "ink-soft": "#ada699", "ink-faint": "#7d766a", "rule": "#27241d", "rule-strong": "#3e392e",
    "accent": "#dda55c", "accent-fill": "#2f2312", "accent-line": "#a67a38",
    "muted": "#888d95", "muted-fill": "#1c1f23", "warn": "#e07a5f",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>사람 라벨의 두 가지 비용</h2>
    <p>
      RLHF는 사람이 붙인 선호 라벨에 의존한다. 유용성만 다룰 때는 견딜 만하지만,
      <strong>무해성</strong>으로 넘어가면 비용이 다른 성격을 띤다.
    </p>
    <ul>
      <li><strong>사람이 감당해야 하는 비용.</strong> 유해한 출력을 골라내려면 라벨러가 그것을 계속 읽어야 한다. 폭력·학대·자해 관련 텍스트를 하루 종일 판정하는 일이다.</li>
      <li><strong>일관성 비용.</strong> 무엇이 유해한지는 사람마다 다르게 판단한다. 규모가 커지면 라벨러 간 불일치가 누적되고, 그 기준이 <em>어디에도 명시적으로 적혀 있지 않다</em>.</li>
    </ul>
    <p>
      두 번째가 특히 중요하다. RLHF로 정렬된 모델의 가치 기준은
      <strong>수만 개의 개별 판정 안에 암묵적으로 흩어져</strong> 있다.
      모델이 왜 그렇게 답하는지 물어도 "라벨러들이 그렇게 골랐기 때문"이라고밖에 말할 수 없다.
      기준을 바꾸려면 데이터를 다시 모아야 한다.
    </p>
    <p>
      Constitutional AI의 제안은 <strong>기준을 문서로 꺼내 놓는 것</strong>이다.
      원칙을 자연어로 적어 두고, 사람 대신 <em>모델이 그 원칙에 비춰 판정하게</em> 한다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>1단계 — 스스로 비판하고 고쳐 쓰게 한다</h2>
    <p>
      첫 단계는 지도학습이고, 세 번의 프롬프트로 이루어진다.
    </p>
    <div class="eq">
      <span class="cap">비판 → 수정 → 학습</span>
      <div class="line">① 유해할 수 있는 질문을 모델에 던져 <strong>초기 응답</strong>을 받는다</div>
      <div class="line">② 헌법에서 원칙 하나를 뽑아 <strong>비판</strong>을 요청한다</div>
      <div class="line">&nbsp;&nbsp;&nbsp;"위 응답이 해롭거나 비윤리적인 지점을 지적하라"</div>
      <div class="line">③ 그 비판을 근거로 <strong>수정본</strong>을 쓰게 한다</div>
      <div class="line">④ (질문 → 수정본) 쌍으로 원래 모델을 파인튜닝한다</div>
    </div>
    <p>
      비판 단계를 <em>거쳐서</em> 수정하게 하는 것이 핵심이다.
      곧바로 "안전하게 다시 써라"라고 하는 것보다,
      무엇이 문제인지 먼저 말하게 한 뒤 고치게 하면 결과가 낫다.
      사고 사슬이 여기서도 작동한다.
    </p>
    <p>
      학습에 쓰이는 것은 <strong>수정본뿐</strong>이다. 비판문은 데이터를 만드는 과정에서만 쓰이고 버려진다.
      결과적으로 모델은 <em>"처음부터 그렇게 답하는 법"</em>을 배운다.
    </p>
    <div class="note">
      <b>회피와 무해성은 다르다.</b> 유해한 질문에 "답할 수 없습니다"만 반복하는 모델은
      무해성 점수는 높지만 쓸모가 없다. 논문이 강조하는 목표는
      <strong>회피하지 않는 무해성</strong>이다 — 왜 그 요청에 응하지 않는지 설명하고,
      가능한 대안을 제시하며 대화를 이어가는 쪽이다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>2단계 — RLAIF, 사람 대신 모델이 고른다</h2>
    <p>
      두 번째 단계는 RLHF와 구조가 같다. 선호 쌍을 모아 선호 모델을 학습하고
      그것을 보상으로 강화학습을 돌린다. <strong>다른 것은 라벨을 누가 붙이는가</strong>다.
    </p>
    <div class="eq">
      <span class="cap">RLAIF — 판정자를 사람에서 모델로 교체</span>
      <div class="line">① 1단계 모델로 같은 질문에 <strong>응답 두 개</strong>를 생성</div>
      <div class="line">② 헌법 원칙 하나와 함께 <strong>다른 모델에게 판정</strong>을 요청</div>
      <div class="line">&nbsp;&nbsp;&nbsp;"어느 응답이 이 원칙에 더 부합하는가?"</div>
      <div class="line">③ 그 판정으로 <strong>선호 모델</strong>을 학습</div>
      <div class="line">④ 선호 모델을 보상으로 강화학습 (이후는 RLHF 와 동일)</div>
    </div>
    <p>
      원칙은 매번 무작위로 하나씩 뽑아 쓴다.
      한 원칙에 과적합되지 않고 여러 기준이 고루 반영되게 하기 위해서다.
    </p>
    <p>
      실무적으로 중요한 절충이 하나 있다.
      <strong>유용성 데이터는 여전히 사람이 붙인다.</strong>
      CAI가 대체하는 것은 <em>무해성</em> 라벨이지 전부가 아니다.
      "무엇이 도움이 되는가"는 사람의 판단을 계속 필요로 한다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="RLHF와 Constitutional AI의 비교 도식. RLHF는 사람이 두 응답을 비교해 선호 라벨을 만들지만, Constitutional AI는 문서로 적힌 원칙을 근거로 모델이 스스로 비판하고 수정한 뒤 다른 모델이 원칙에 비춰 판정한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="ca-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
              <marker id="ca-m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/>
              </marker>
            </defs>

            <text x="26" y="18" font-size="10" letter-spacing="1.2" fill="var(--muted)">RLHF — 사람이 판정</text>

            <rect x="26" y="30" width="60" height="22" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="56" y="45" text-anchor="middle" font-size="8" fill="var(--ink-soft)">응답 A</text>
            <rect x="26" y="58" width="60" height="22" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="56" y="73" text-anchor="middle" font-size="8" fill="var(--ink-soft)">응답 B</text>

            <path d="M90 55 L112 55" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#ca-m)"/>
            <rect x="116" y="42" width="70" height="26" fill="var(--warn)" opacity="0.2" stroke="var(--warn)" stroke-width="1.3"/>
            <text x="151" y="59" text-anchor="middle" font-size="8.5" fill="var(--ink)">사람 라벨러</text>

            <path d="M190 55 L212 55" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#ca-m)"/>
            <rect x="216" y="42" width="70" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="251" y="59" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">선호 라벨</text>

            <text x="26" y="102" font-size="8.5" fill="var(--warn)">기준이 수만 개 판정 안에 흩어져 있다</text>
            <text x="26" y="116" font-size="8.5" fill="var(--ink-faint)">유해 텍스트를 사람이 계속 읽어야 한다</text>

            <line x1="26" y1="132" x2="674" y2="132" stroke="var(--rule)" stroke-width="1"/>

            <text x="26" y="154" font-size="10" letter-spacing="1.2" fill="var(--accent)">Constitutional AI — 문서로 적힌 원칙이 판정</text>

            <rect x="26" y="166" width="82" height="52" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.6"/>
            <text x="67" y="184" text-anchor="middle" font-size="8.5" fill="var(--accent)">헌법</text>
            <line x1="36" y1="192" x2="98" y2="192" stroke="var(--accent-line)" stroke-width="0.8"/>
            <line x1="36" y1="199" x2="98" y2="199" stroke="var(--accent-line)" stroke-width="0.8"/>
            <line x1="36" y1="206" x2="86" y2="206" stroke="var(--accent-line)" stroke-width="0.8"/>
            <text x="67" y="232" text-anchor="middle" font-size="8" fill="var(--ink-faint)">명시적 원칙</text>

            <path d="M112 192 L134 192" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#ca-a)"/>

            <rect x="138" y="170" width="76" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="176" y="188" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">모델이</text>
            <text x="176" y="202" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">비판</text>

            <path d="M218 192 L240 192" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#ca-a)"/>

            <rect x="244" y="170" width="76" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="282" y="188" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">스스로</text>
            <text x="282" y="202" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">수정</text>

            <path d="M324 192 L346 192" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#ca-a)"/>

            <rect x="350" y="170" width="82" height="44" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="391" y="188" text-anchor="middle" font-size="8.5" fill="var(--accent)">SFT</text>
            <text x="391" y="202" text-anchor="middle" font-size="8" fill="var(--accent)">(1단계 끝)</text>

            <path d="M436 192 L458 192" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#ca-a)"/>

            <rect x="462" y="170" width="94" height="44" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="509" y="188" text-anchor="middle" font-size="8.5" fill="var(--ink-soft)">모델이 판정</text>
            <text x="509" y="202" text-anchor="middle" font-size="8" fill="var(--ink-faint)">RLAIF</text>

            <path d="M560 192 L582 192" stroke="var(--accent-line)" stroke-width="1.3" marker-end="url(#ca-a)"/>
            <rect x="586" y="170" width="88" height="44" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.5"/>
            <text x="630" y="188" text-anchor="middle" font-size="8.5" fill="var(--accent)">정렬된 모델</text>
            <text x="630" y="202" text-anchor="middle" font-size="8" fill="var(--accent)">(2단계 끝)</text>

            <text x="138" y="232" font-size="8.5" fill="var(--ink-faint)">무해성 라벨에 사람이 개입하지 않는다 — 다만 유용성 라벨은 여전히 사람이 붙인다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        바뀐 것은 <strong>기준이 놓인 자리</strong>다.
        RLHF에서 기준은 데이터 안에 암묵적으로 있고,
        CAI에서는 <em>읽고 고칠 수 있는 문서</em>로 밖에 나와 있다.
        감독의 <strong>확장성</strong>과 <strong>투명성</strong>을 동시에 노린 설계다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">04</span>무엇이 나아졌고 무엇이 남았나</h2>
    <p>
      논문이 보고한 핵심 결과는 <strong>유용성을 크게 희생하지 않으면서
      무해성을 개선했고, 회피가 줄었다</strong>는 것이다.
      기존 RLHF 모델이 민감한 질문에 입을 닫는 경향을 보인 반면,
      CAI 모델은 <em>왜 응하지 않는지 설명하며</em> 대화를 유지했다.
    </p>
    <p>
      부수적 이점도 분명하다.
    </p>
    <ul>
      <li><strong>수정이 싸다.</strong> 기준을 바꾸려면 원칙 문장을 고치면 된다. 수만 건의 라벨을 다시 모을 필요가 없다.</li>
      <li><strong>감사 가능하다.</strong> 무엇을 기준으로 삼았는지 외부에서 읽고 비판할 수 있다.</li>
      <li><strong>사람의 노출이 준다.</strong> 유해 콘텐츠를 반복해서 읽는 노동이 줄어든다.</li>
    </ul>
    <p>
      다만 남는 문제도 분명하다.
    </p>
    <div class="note">
      <b>원칙은 여전히 사람이 쓴다.</b> "누가 헌법을 쓰는가"라는 질문이 그대로 남는다.
      라벨러의 암묵적 판단을 소수가 쓴 명시적 문장으로 바꾼 것이지,
      <em>가치 판단이 사라진 것은 아니다</em>.
      Anthropic이 이후 공개 의견을 수렴해 헌법을 작성하는 실험을 진행한 것도 이 지점을 겨냥한다.
    </div>
    <p>
      더 근본적인 제약은 <strong>모델이 원칙을 이해할 만큼 유능해야 한다</strong>는 점이다.
      비판과 판정을 모델이 수행하므로, 모델의 판단력이 곧 상한이 된다.
      약한 모델로는 이 방법이 잘 작동하지 않는다.
      또 모델 자신의 편향이 판정에 그대로 실린다 —
      사람 라벨의 편향을 <em>모델 편향으로 교체</em>한 셈이라는 지적이 가능하다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>확장성 감독이라는 더 큰 문제</h2>
    <p>
      CAI를 개별 기법으로만 보면 요점을 놓친다.
      이 방법이 겨냥하는 것은 <strong>확장성 감독</strong>(scalable oversight)이라는 더 큰 문제다.
    </p>
    <p>
      모델이 사람보다 특정 영역에서 유능해지면,
      <em>사람이 그 출력을 평가할 수 없게 된다</em>.
      전문가도 검증하기 어려운 코드나 논증을 모델이 내놓을 때
      "좋은 답인지" 판정할 방법이 필요하다.
      사람이 모든 출력을 직접 평가하는 방식은 어느 지점에서 한계에 부딪힌다.
    </p>
    <p>
      CAI의 답은 <strong>사람이 규칙을 정하고 판정은 모델에게 위임하는 것</strong>이다.
      사람의 역할이 <em>모든 사례를 판정하는 것</em>에서
      <em>기준을 정하고 그 기준이 잘 적용되는지 감사하는 것</em>으로 옮겨간다.
    </p>
    <p>
      이 발상은 CAI 이후 널리 퍼졌다. 모델을 심판으로 쓰는 평가 방식,
      AI 피드백으로 만든 선호 데이터셋, 모델이 스스로 데이터를 만들어 학습하는 절차 —
      모두 같은 계보다. 지금은 <strong>AI 피드백이 정렬 파이프라인의 표준 구성 요소</strong>가 됐고,
      순수한 사람 라벨만 쓰는 대형 모델은 오히려 드물다.
    </p>
    <p>
      한 문장으로 줄이면, Constitutional AI는
      <em>"모델을 무엇에 맞출 것인가"를 데이터에서 문서로 옮긴 시도</em>다.
      그것으로 감독을 확장할 수 있게 됐지만,
      문서를 누가 쓰느냐는 물음은 공학이 답할 수 있는 것이 아니다.
    </p>
  </section>
"""

READING = [
    "Bai et al., <em>Constitutional AI: Harmlessness from AI Feedback</em> (arXiv:2212.08073) — 원 논문. 두 단계와 RLAIF.",
    "Bai et al., <em>Training a Helpful and Harmless Assistant with RLHF</em> (arXiv:2204.05862) — CAI가 출발점으로 삼은 RLHF 결과.",
    "Lee et al., <em>RLAIF vs. RLHF: Scaling Reinforcement Learning from Human Feedback with AI Feedback</em> (arXiv:2309.00267) — AI 피드백과 사람 피드백의 직접 비교.",
    "Ganguli et al., <em>Red Teaming Language Models to Reduce Harms</em> (arXiv:2209.07858) — 유해성 평가 데이터의 구성.",
    "Bowman et al., <em>Measuring Progress on Scalable Oversight for Large Language Models</em> (arXiv:2211.03540) — 확장성 감독 문제의 정식화.",
]

write(
    "constitutional-ai.html",
    title="Constitutional AI — 사람 라벨 대신 원칙",
    eyebrow="Alignment · Scalable Oversight · 2022–2026",
    h1="Constitutional AI",
    subtitle="사람 라벨 대신 원칙 — 기준을 데이터에서 문서로",
    dek=(
        "RLHF에서 모델의 가치 기준은 <strong>수만 개 판정 안에 흩어져</strong> 있다. "
        "읽을 수도, 고칠 수도 없다. 게다가 유해 텍스트를 사람이 계속 읽어야 한다. "
        "CAI는 원칙을 문서로 꺼내 놓고 <strong>모델이 스스로 비판하고 수정하게</strong> 한 뒤, "
        "판정도 모델에게 맡긴다. 다만 그 문서를 누가 쓰느냐는 물음은 남는다."
    ),
    spec=[
        ("1단계", "비판 → 수정 → SFT"),
        ("2단계", "RLAIF"),
        ("대체 대상", "무해성 라벨만"),
        ("목표", "회피하지 않는 무해성"),
        ("겨냥한 문제", "확장성 감독"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
