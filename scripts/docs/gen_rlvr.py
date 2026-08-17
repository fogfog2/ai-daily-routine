#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f1f2f0", panel="#e5e9e5", ink="#15181a", **{
    "ink-soft": "#4c5457", "ink-faint": "#7b8487", "rule": "#d2d7d3",
    "rule-strong": "#aab2ad", "accent": "#1f6b5e", "accent-fill": "#d9ece6",
    "accent-line": "#3d8f7f", "muted": "#848b88", "muted-fill": "#dfe3e0", "warn": "#a04a28",
})
DARK = dict(paper="#0e1213", panel="#161b1c", ink="#e4e9e7", **{
    "ink-soft": "#9fa9a6", "ink-faint": "#71797a", "rule": "#1f2527", "rule-strong": "#354044",
    "accent": "#6fd4bd", "accent-fill": "#0f2a26", "accent-line": "#3f8f80",
    "muted": "#858c8a", "muted-fill": "#171c1d", "warn": "#e08a5f",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>보상을 사람에게서 채점기로 옮기다</h2>
    <p>
      <a href="rlhf.html">RLHF</a>의 구조를 한 줄로 줄이면 이렇다 —
      사람의 선호를 신경망(보상 모델)에 담고, 그 신경망이 주는 점수를 최대화한다.
      이 구조에는 피할 수 없는 약점이 하나 있다.
      <strong>보상 모델은 사람 판단의 근사이고, 근사는 결국 뚫린다.</strong>
      정책이 충분히 오래 학습되면 보상 모델이 잘못 높은 점수를 주는 구석을 찾아낸다.
      RLHF 문서에서 <em>보상 해킹</em>이라 부른 현상이다.
    </p>
    <p>
      RLVR은 그 자리를 다르게 채운다. 보상을 주는 것이 학습된 모델이 아니라
      <strong>프로그램</strong>이다. 수학 문제면 최종 답을 정답과 대조하고,
      코드면 테스트를 돌려 통과 여부를 보고, 형식 요구가 있으면 정규식으로 확인한다.
      점수는 대개 <code>0</code> 또는 <code>1</code>이다.
    </p>
    <div class="eq">
      <span class="cap">보상의 출처가 바뀐다</span>
      <div class="line">RLHF:&nbsp; r(x, y) = <strong>r<sub>φ</sub>(x, y)</strong>&nbsp;&nbsp;// 선호 데이터로 학습된 신경망</div>
      <div class="line">RLVR:&nbsp; r(x, y) = <strong>verify(y, y*)</strong>&nbsp;&nbsp;// 채점 프로그램. 파라미터가 없다</div>
      <div class="line">// 학습되지 않는 함수는 과최적화로 무너지지 않는다</div>
    </div>
    <p>
      이 교체가 만드는 차이는 생각보다 크다.
      보상 모델을 쓰면 <em>얼마나 오래 최적화할 것인가</em>가 하이퍼파라미터가 된다.
      너무 밀면 보상 점수는 계속 오르는데 실제 품질은 떨어지기 시작한다 —
      보상 모델 과최적화로 정량화된 현상이다.
      채점 프로그램에는 그 지점이 없다. 정답을 맞히는 것 말고 올릴 방법이 없기 때문이다.
    </p>
    <div class="note">
      <b>용어는 두 갈래에서 거의 동시에 나왔다.</b>
      <em>RLVR</em>(Reinforcement Learning with Verifiable Rewards)이라는 이름은
      Tulu 3(arXiv:2411.15124)이 붙였고, 같은 시기 DeepSeekMath(arXiv:2402.03300)는
      <em>GRPO</em>라는 학습 알고리즘으로 같은 일을 하고 있었다.
      이 편은 <strong>보상을 무엇으로 줄 것인가</strong>(RLVR)와
      <strong>그 보상으로 어떻게 학습할 것인가</strong>(GRPO)를 나눠서 본다.
      둘은 자주 한 덩어리로 불리지만 서로 독립이다 —
      검증 가능한 보상을 PPO로 돌려도 되고, GRPO에 보상 모델을 물려도 된다.
    </div>
    <p>
      대신 <strong>적용 범위</strong>를 내준다.
      채점기를 쓸 수 있는 과제만 이 경로를 탈 수 있다.
      "이 문단을 더 설득력 있게 고쳐라"에는 verify 함수가 없다.
      <a href="dpo-alignment.html">DPO</a> 계열의 선호 학습이 사라지지 않는 이유가 여기 있다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>GRPO — 가치망을 그룹 평균으로 바꾸다</h2>
    <p>
      보상을 채점기로 바꿔도 학습 알고리즘은 그대로 PPO를 쓸 수 있다.
      그런데 PPO에는 <strong>가치망</strong>(critic)이 붙어 있다.
      지금 상태에서 앞으로 받을 보상의 기댓값을 추정해 기준선으로 삼는 역할인데,
      실무에서는 대개 정책과 비슷한 크기의 모델을 하나 더 학습시킨다.
    </p>
    <p>
      GRPO의 관찰은 단순하다. <strong>기준선이 꼭 학습된 함수일 필요는 없다.</strong>
      같은 프롬프트에 답을 G개 샘플링하면, 그 그룹의 평균 보상이 곧 기준선이다.
      추정하지 않고 <em>측정한다</em>.
    </p>
    <div class="eq">
      <span class="cap">그룹 상대 이점 — 기준선을 그룹 안에서 구한다</span>
      <div class="line">한 프롬프트 x 에 답을 G개 샘플링: y<sub>1</sub> … y<sub>G</sub>,&nbsp; 보상 r<sub>1</sub> … r<sub>G</sub></div>
      <div class="line">Â<sub>i</sub> = ( r<sub>i</sub> − mean(r) ) / std(r)&nbsp;&nbsp;&nbsp;// 그룹 안에서 표준화</div>
      <div class="line">// 같은 프롬프트의 모든 토큰이 같은 Â 를 쓴다 (토큰별 가치 추정이 없다)</div>
    </div>
    <p>
      정의상 <strong>Σ Â<sub>i</sub> = 0</strong> 이다.
      그룹 안에서 평균보다 잘한 답은 밀어 올리고 못한 답은 눌러 내린다.
      절대 점수는 아무 의미가 없고 <em>같은 문제를 푼 형제 답들 사이의 순위</em>만 본다.
      보상의 눈금이 어떻든 결과가 같아진다는 뜻이기도 하다.
    </p>
    <p>
      실무에서 체감되는 것은 <strong>상주 모델 수</strong>다.
      RLHF 문서의 표에서 PPO는 넷을 들고 있어야 했다 —
      정책·참조·보상 모델·가치망. GRPO에 규칙 기반 보상을 물리면
      보상 모델과 가치망이 동시에 사라진다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>구성</th><th>상주 모델</th><th>7B · bf16 가중치</th><th>70B · bf16 가중치</th></tr>
        </thead>
        <tbody>
          <tr><td>PPO + 보상 모델</td><td>정책 · 참조 · 보상 · 가치 (4)</td><td>52.2 GiB</td><td>521.5 GiB</td></tr>
          <tr><td class="hi">GRPO + 검증 보상</td><td class="hi">정책 · 참조 (2)</td><td class="hi">26.1 GiB</td><td class="hi">260.8 GiB</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      가중치만 센 값이고 옵티마이저 상태·활성값·KV 캐시는 뺐다
      (사본 하나가 7B에서 13.0 GiB, 70B에서 130.4 GiB다).
      그래도 방향은 분명하다 — 학습되지 않는 두 모델을 걷어내면 절반이 빈다.
      <a href="mixed-precision.html">Mixed Precision</a>이나
      <a href="distributed-training.html">분산 학습</a>으로 짜내던 여유가
      알고리즘 교체 하나로 나온 셈이다.
    </p>
    <div class="note">
      <b>공짜는 아니다.</b> 가치망은 <em>토큰마다</em> 다른 기준선을 준다.
      GRPO는 한 답 전체에 같은 이점을 부여하므로,
      긴 답에서 <strong>어느 토큰이 좋았는지</strong>를 구분하지 못한다.
      대신 답을 G개 뽑아야 하니 <em>샘플링 비용이 G배</em>다.
      메모리를 연산으로 바꾼 거래에 가깝다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>그룹이 만들어내는 새 실패 — 신호가 죽는 문항</h2>
    <p>
      기준선을 그룹에서 구하는 대가가 하나 더 있다.
      <strong>그룹 안의 보상이 전부 같으면 std가 0이고, 이점이 전부 0이 된다.</strong>
      G개를 전부 샘플링하고 채점까지 마쳤는데 그래디언트가 하나도 나오지 않는다.
    </p>
    <p>
      이진 보상에서 이것은 <em>전원 정답</em>이거나 <em>전원 오답</em>인 경우다.
      즉 <strong>너무 쉬운 문항과 너무 어려운 문항이 똑같이 버려진다.</strong>
      모델의 그 문항 정답률을 p라 하면, 신호가 죽을 확률은 p<sup>G</sup> + (1−p)<sup>G</sup> 다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>정답률 p</th><th>G=4</th><th>G=8</th><th>G=16</th><th>G=32</th></tr>
        </thead>
        <tbody>
          <tr><td>0.05 (거의 못 품)</td><td>81.5%</td><td>66.3%</td><td>44.0%</td><td class="hi">19.4%</td></tr>
          <tr><td>0.10</td><td>65.6%</td><td>43.1%</td><td>18.5%</td><td>3.4%</td></tr>
          <tr><td>0.30</td><td>24.8%</td><td>5.8%</td><td>0.3%</td><td>0.0%</td></tr>
          <tr><td class="hi">0.50 (가장 유익)</td><td class="hi">12.5%</td><td class="hi">0.8%</td><td>0.0%</td><td>0.0%</td></tr>
          <tr><td>0.90</td><td>65.6%</td><td>43.1%</td><td>18.5%</td><td>3.4%</td></tr>
          <tr><td>0.95 (거의 다 품)</td><td>81.5%</td><td>66.3%</td><td>44.0%</td><td>19.4%</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      표는 p<sup>G</sup> + (1−p)<sup>G</sup> 를 직접 계산한 것이다.
      읽는 법은 이렇다 — <strong>정답률 5%짜리 문항을 G=4로 돌리면 열 번 중 여덟 번은 헛돈다.</strong>
      G를 32까지 올려도 다섯 번에 한 번은 여전히 버려진다.
      반대로 정답률 50% 부근에서는 G=8만 돼도 낭비가 1% 아래로 떨어진다.
    </p>
    <p>
      여기서 나오는 결론이 실무적으로 중요하다.
      <strong>RLVR의 학습 효율은 데이터셋의 난이도 분포가 정한다.</strong>
      모델이 이미 다 푸는 문제집도, 하나도 못 푸는 문제집도 GPU만 쓰고 아무것도 가르치지 못한다.
      <a href="curriculum-data-quality.html">커리큘럼</a>이 "있으면 좋은 것"이 아니라
      <em>비용에 직접 걸리는 항</em>이 되는 지점이다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 236" role="img" aria-label="문항 정답률에 따라 그룹 학습 신호가 살아남는 비율을 나타낸 곡선. 정답률 0.5 부근에서 신호가 가장 잘 살아남고 양 끝(너무 쉽거나 너무 어려운 문항)으로 갈수록 급격히 떨어지며, 그룹 크기 G를 4에서 32로 키우면 곡선 전체가 위로 올라가지만 양 끝의 손실은 남는다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <text x="26" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--ink-soft)">살아남는 학습 신호 = 1 − (p^G + (1−p)^G)</text>

            <line x1="66" y1="42" x2="66" y2="176" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <line x1="66" y1="176" x2="386" y2="176" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="36" y="48" font-size="8.5" fill="var(--ink-faint)">100%</text>
            <text x="46" y="180" font-size="8.5" fill="var(--ink-faint)">0%</text>
            <text x="60" y="194" font-size="8.5" fill="var(--ink-faint)">p=0</text>
            <text x="212" y="194" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">0.5</text>
            <text x="374" y="194" font-size="8.5" fill="var(--ink-faint)">1.0</text>
            <text x="212" y="210" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">문항 정답률 p &rarr;</text>

            <line x1="212" y1="42" x2="212" y2="176" stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 3"/>

            <path d="M66 176 C 108 82, 150 50, 212 46 C 274 50, 316 82, 358 176" fill="none" stroke="var(--accent)" stroke-width="2"/>
            <text x="222" y="60" font-size="9" fill="var(--accent)">G = 32</text>

            <path d="M66 176 C 112 118, 156 74, 212 66 C 268 74, 312 118, 358 176" fill="none" stroke="var(--accent-line)" stroke-width="1.7" stroke-dasharray="5 3"/>
            <text x="222" y="86" font-size="9" fill="var(--accent-line)">G = 8</text>

            <path d="M66 176 C 118 150, 162 122, 212 116 C 262 122, 306 150, 358 176" fill="none" stroke="var(--warn)" stroke-width="1.7"/>
            <text x="222" y="112" font-size="9" fill="var(--warn)">G = 4</text>

            <text x="72" y="166" font-size="8.5" fill="var(--warn)">너무 어려움</text>
            <text x="300" y="166" font-size="8.5" fill="var(--warn)">너무 쉬움</text>

            <line x1="416" y1="30" x2="416" y2="214" stroke="var(--rule)" stroke-width="1"/>

            <text x="438" y="20" font-size="10.5" letter-spacing="1.3" fill="var(--accent)">무엇이 걸리는가</text>

            <text x="438" y="46" font-size="9" fill="var(--ink-soft)">그룹 보상이 전부 같으면</text>
            <text x="438" y="60" font-size="9" fill="var(--ink-faint)">std = 0 &rarr; 이점 전부 0.</text>
            <text x="438" y="74" font-size="9" fill="var(--ink-faint)">샘플링·채점 비용만 쓰고 버려진다.</text>

            <rect x="438" y="88" width="234" height="1" fill="var(--rule)"/>

            <text x="438" y="108" font-size="9" fill="var(--ink-soft)">G 를 키우면 곡선이 올라가지만</text>
            <text x="438" y="122" font-size="9" fill="var(--ink-faint)">비용도 <tspan fill="var(--warn)">G 에 비례</tspan>해 늘어난다.</text>
            <text x="438" y="136" font-size="9" fill="var(--ink-faint)">p=0.05 은 G=32 에서도 19% 손실.</text>

            <rect x="438" y="150" width="234" height="1" fill="var(--rule)"/>

            <text x="438" y="170" font-size="9" fill="var(--accent)">실무 대응</text>
            <text x="438" y="186" font-size="8.5" fill="var(--ink-faint)">· 동적 샘플링 — 죽은 그룹은 버리고 다시 뽑는다</text>
            <text x="438" y="200" font-size="8.5" fill="var(--ink-faint)">· 난이도로 문항을 미리 거른다</text>
            <text x="438" y="214" font-size="8.5" fill="var(--ink-faint)">· 학습이 진행되면 난이도를 다시 맞춘다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        곡선은 p<sup>G</sup> + (1−p)<sup>G</sup> 로 계산한 값이다.
        <strong>배치를 채웠다고 학습 신호를 채운 것이 아니다.</strong>
        DAPO가 도입한 <em>동적 샘플링</em>은 보상이 전부 같은 그룹을 배치에서 빼고
        유효한 그룹이 찰 때까지 다시 뽑는다 — 곡선을 바꾸는 대신 배치의 정의를 바꾼 대응이다.
      </figcaption>
    </figure>

    <p>
      한 가지 덧붙일 것은 <strong>이 현상이 학습 도중에 움직인다</strong>는 점이다.
      모델이 좋아지면 정답률 p가 오르고, 어제 유익하던 문항이 오늘은 전원 정답이 된다.
      난이도를 한 번 맞춰 두고 끝낼 수 없고, 학습이 진행되는 동안 계속 다시 맞춰야 한다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>목줄은 남는다 — KL 을 어떻게 재는가</h2>
    <p>
      보상이 규칙으로 바뀌어도 <a href="rlhf.html">RLHF</a>에서 본 KL 페널티는 대개 남는다.
      정답만 좇다 보면 <em>정답은 맞는데 문장이 무너지는</em> 상태로 갈 수 있기 때문이다.
      참조 모델에서 너무 멀어지지 말라는 제약은 여전히 필요하다.
    </p>
    <p>
      그런데 KL 을 정확히 계산할 수는 없다.
      가능한 모든 시퀀스에 대한 합이라 셀 수 없는 크기다.
      실제로는 <strong>정책이 방금 뽑은 표본으로 추정</strong>한다.
      그리고 어떤 추정량을 쓰느냐가 학습 안정성에 눈에 띄게 걸린다.
    </p>
    <div class="eq">
      <span class="cap">두 추정량 — 같은 기댓값, 다른 성질</span>
      <div class="line">t = π<sub>ref</sub>(y|x) / π<sub>θ</sub>(y|x)&nbsp;&nbsp;&nbsp;// 표본 y ~ π<sub>θ</sub></div>
      <div class="line">k1 = −log t&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// 정의를 그대로 옮긴 것</div>
      <div class="line">k3 = t − log t − 1&nbsp;&nbsp;&nbsp;// GRPO 가 쓰는 쪽</div>
      <div class="line">// 둘 다 기댓값은 KL(π_θ ‖ π_ref) 로 같다</div>
    </div>
    <p>
      k3 의 성질을 직접 확인해 보면 차이가 분명하다.
      먼저 <strong>t − log t − 1 은 t &gt; 0 에서 항상 0 이상</strong>이고 t = 1 에서만 0 이다.
      즉 <em>표본 하나하나가 이미 KL 처럼 생겼다</em> — 음수가 나오지 않는다.
      k1 은 그렇지 않다. π<sub>ref</sub> 가 π<sub>θ</sub> 보다 높은 확률을 준 표본에서는 음수가 된다.
    </p>
    <p>
      네 값짜리 이산 분포로 두 추정량을 20만 번 표본추출해 재면 이렇게 나온다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>추정량</th><th>기댓값</th><th>음수 표본 비율</th><th>표본 분산</th></tr>
        </thead>
        <tbody>
          <tr><td>참값 KL</td><td>0.025267</td><td>—</td><td>—</td></tr>
          <tr><td>k1 = −log t</td><td>0.025267</td><td class="hi">29.9%</td><td class="hi">0.04899</td></tr>
          <tr><td class="hi">k3 = t − log t − 1</td><td>0.025267</td><td>0.0%</td><td>0.00025</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>기댓값은 소수점 아래 열여섯 자리까지 같은데 분산이 약 196배 차이 난다.</strong>
      추정이 틀려서가 아니라 <em>흔들려서</em> 문제가 되는 종류의 차이다.
      배치마다 KL 항이 음수로 튀면 페널티가 순간적으로 <q>더 멀어져라</q>가 되고,
      그 잡음이 정책 업데이트에 그대로 실린다.
    </p>
    <div class="note">
      <b>불편(unbiased)과 저분산은 다른 요구다.</b>
      k1 은 정의에 가장 충실하지만 실무에서 쓰기 나쁘고,
      k3 는 형태가 낯설지만 같은 기댓값을 훨씬 조용하게 준다.
      Monte Carlo 추정에서 <em>보정항을 더해 분산을 줄이는</em> 표준적인 수법이고,
      기댓값이 0인 항 (t − 1) 을 얹었을 뿐이라 편향이 생기지 않는다.
    </div>
    <p>
      덧붙여, KL 페널티를 <strong>아예 빼는</strong> 구성도 늘고 있다.
      검증 가능한 보상에서는 보상 해킹의 압력이 낮으므로 목줄을 풀어
      참조 모델에서 더 멀리 가도록 두는 편이 추론 성능에 유리하다는 보고가 있다.
      다만 그만큼 원래 모델의 다른 능력이 흔들릴 여지도 커진다 —
      무엇을 지키고 무엇을 내줄지의 선택이지 정답이 있는 항목은 아니다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>무엇이 검증 가능한가 — 그리고 해킹은 어디로 갔는가</h2>
    <p>
      RLVR을 <q>보상 해킹이 없는 강화학습</q>으로 요약하면 절반만 맞다.
      정확히는 <strong>해킹의 표적이 옮겨간 것</strong>이다.
      보상 모델의 <em>근사 오차</em>를 노리던 압력이 이제 채점기의 <em>명세 구멍</em>을 노린다.
    </p>
    <ul>
      <li><strong>테스트만 통과하는 코드.</strong> 단위 테스트가 보상이면, 문제를 푸는 대신 테스트 케이스를 특수 처리하는 답이 나온다.</li>
      <li><strong>답만 맞는 풀이.</strong> 최종 답만 대조하면 과정이 틀렸는데 답이 맞는 경우를 가려내지 못한다. 객관식에서 특히 심하다.</li>
      <li><strong>형식 보상만 먹기.</strong> 사고 과정을 태그로 감싸라는 형식 보상을 주면, 태그는 정확히 채우고 안은 비우는 출력이 나온다.</li>
      <li><strong>길이 폭주.</strong> 길게 쓸수록 정답 확률이 오르는 문항에서는 답이 계속 길어진다. <a href="dpo-alignment.html">선호 학습에서 본 길이 편향</a>과 원인은 다르지만 결과는 닮았다.</li>
    </ul>
    <p>
      차이가 있다면 <strong>이쪽 구멍은 눈에 보인다</strong>는 점이다.
      보상 모델의 어느 부분이 뚫렸는지는 들여다보기 어렵지만,
      채점 함수는 사람이 읽을 수 있는 코드다.
      테스트를 늘리고, 과정을 함께 검증하고, 길이에 제약을 걸 수 있다.
      <em>고칠 수 있는 실패</em>와 <em>진단하기 어려운 실패</em>의 차이다.
    </p>
    <p>
      더 근본적인 경계는 <strong>검증 가능성 자체</strong>다.
      수학·코드·형식 준수·구조화된 추출은 채점기를 쓸 수 있다.
      글쓰기·조언·요약·대화의 어조는 그렇지 않다.
      이 경계를 넘으려는 시도가 <em>심판 모델</em>과 <em>루브릭 채점</em>인데,
      그 순간 보상은 다시 학습된 근사가 된다.
      <strong>RLVR이 피했던 문제가 정확히 그 형태로 돌아온다.</strong>
      경계를 넓히는 대가로 성질을 내주는 거래다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>보상의 출처</th><th>적용 범위</th><th>과최적화</th><th>대표 용례</th></tr>
        </thead>
        <tbody>
          <tr><td class="hi">검증 프로그램</td><td class="hi">좁다</td><td class="hi">거의 없다</td><td>수학·코드·형식</td></tr>
          <tr><td>심판 모델 · 루브릭</td><td>중간</td><td>있다</td><td>개방형 과제</td></tr>
          <tr><td>학습된 보상 모델</td><td>넓다</td><td>뚜렷하다</td><td>일반 선호 정렬</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      그래서 실제 파이프라인은 하나를 고르지 않는다.
      <a href="instruction-tuning.html">SFT</a>로 형식을 잡고,
      선호 학습으로 어조와 안전성을 맞추고,
      검증 가능한 영역에만 RLVR을 얹는다.
      최근 추론 모델들이 크게 밀어붙인 것이 마지막 단계이고,
      <a href="chain-of-thought.html">Chain-of-Thought</a> 문서에서
      <q>추론 시간을 늘리면 성능이 오른다</q>고 적었던 축을
      <em>학습으로 옮긴</em> 것이 이 경로다.
      길게 생각하라고 프롬프트로 시키는 대신, 길게 생각해서 맞힌 궤적에 보상을 준다.
    </p>
    <div class="note">
      <b>가장 크게 남은 질문.</b>
      RLVR이 <em>없던 능력을 만드는지</em>, 아니면 <em>이미 있던 능력을 꺼내 쓰게 만드는지</em>가
      아직 정리되지 않았다. 정책이 한 번도 맞히지 못하는 문제는 보상이 0으로만 나오므로
      — 03 절의 죽은 그룹이 바로 그것이다 —
      학습 신호 자체가 기저 모델이 <em>가끔은 맞히는</em> 범위 안에서만 생긴다.
      그렇다면 RLVR은 분포를 <strong>날카롭게 만드는</strong> 장치에 가깝다.
      이 해석이 맞다면 사전학습의 몫은 줄지 않는다.
    </div>
    <p>
      마지막으로 실무의 관점에서 한 줄 —
      검증 가능한 보상의 진짜 매력은 성능 수치가 아니라
      <strong>사람 라벨러 없이 데이터를 늘릴 수 있다</strong>는 데 있다.
      정답이 붙은 문제집만 있으면 되고, 문제집은 사람 선호 데이터보다 훨씬 싸다.
      이 편에서 본 세 가지 — 죽은 그룹, KL 추정량, 채점기 명세 —
      는 전부 그 값싼 신호를 <em>낭비 없이 쓰는 방법</em>에 관한 이야기였다.
    </p>
  </section>
"""

READING = [
    "Shao et al., <em>DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models</em> (arXiv:2402.03300) — GRPO 원 논문. 가치망 제거와 그룹 상대 이점.",
    "Lambert et al., <em>Tulu 3: Pushing Frontiers in Open Language Model Post-Training</em> (arXiv:2411.15124) — RLVR 이라는 이름과 검증 보상 파이프라인.",
    "DeepSeek-AI, <em>DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning</em> (arXiv:2501.12948) — 규칙 기반 보상만으로 추론 능력을 끌어올린 사례.",
    "Yu et al., <em>DAPO: An Open-Source LLM Reinforcement Learning System at Scale</em> (arXiv:2503.14476) — 동적 샘플링으로 죽은 그룹을 걸러낸다.",
    "Gao et al., <em>Scaling Laws for Reward Model Overoptimization</em> (arXiv:2210.10760) — 학습된 보상이 과최적화로 무너지는 지점의 정량화. RLVR 이 피하려는 곡선.",
    "Schulman et al., <em>Proximal Policy Optimization Algorithms</em> (arXiv:1707.06347) — GRPO 가 물려받은 클리핑 목적함수의 출처.",
]

write(
    "rlvr.html",
    title="RLVR — 채점 가능한 것만 보상한다",
    eyebrow="Alignment · Verifiable Rewards · 2024–2026",
    h1="RLVR",
    subtitle="채점 가능한 것만 보상한다 — 그리고 GRPO",
    dek=(
        "보상을 신경망이 아니라 <strong>채점 프로그램</strong>이 준다. "
        "학습되지 않는 보상은 과최적화로 무너지지 않고, "
        "GRPO 는 그 위에서 가치망까지 걷어내 상주 모델을 넷에서 둘로 줄인다. "
        "대신 <em>그룹 보상이 전부 같으면 학습 신호가 통째로 사라지는</em> 새 실패가 생긴다 — "
        "너무 쉬운 문항과 너무 어려운 문항이 똑같이 버려진다."
    ),
    spec=[
        ("보상의 출처", "채점 프로그램 (파라미터 없음)"),
        ("상주 모델", "2개 (정책·참조)"),
        ("이점", "(r − mean) / std · 그룹 내"),
        ("새 실패", "std = 0 → 신호 소멸"),
        ("적용 경계", "수학·코드·형식"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-17",
)
