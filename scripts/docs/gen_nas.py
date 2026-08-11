#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f1f1", panel="#e5e8e8", ink="#141a1a", **{
    "ink-soft": "#4b5757", "ink-faint": "#7a8686", "rule": "#ccd3d3",
    "rule-strong": "#a9b1b1", "accent": "#3a5a7a", "accent-fill": "#dde6ef",
    "accent-line": "#5b80a3", "muted": "#83888c", "muted-fill": "#dee1e1", "warn": "#a34a28",
})
DARK = dict(paper="#0f1213", panel="#171b1c", ink="#e4eaea", **{
    "ink-soft": "#a1abab", "ink-faint": "#707a7a", "rule": "#212726", "rule-strong": "#374040",
    "accent": "#83aecc", "accent-fill": "#12242f", "accent-line": "#54809b",
    "muted": "#868d8d", "muted-fill": "#191f1f", "warn": "#e0855c",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>정할 것이 너무 많다</h2>
    <p>
      <a href="efficient-backbone.html">경량 백본</a> 문서에서
      <em>"경량 모델에는 정할 것이 많고, 손으로 조율하기에는 조합이 너무 많다"</em>고 했다.
      실제로 얼마나 많은지 세어 보자.
    </p>
    <div class="eq">
      <span class="cap">층 하나마다 고를 것</span>
      <div class="line">· 커널 크기&nbsp;&nbsp;&nbsp; 3 × 3 · 5 × 5 · 7 × 7</div>
      <div class="line">· 확장 비율&nbsp;&nbsp;&nbsp; 3배 · 4배 · 6배</div>
      <div class="line">· 채널 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 여러 후보</div>
      <div class="line">· 반복 횟수&nbsp;&nbsp;&nbsp; 1~4</div>
      <div class="line">· 다운샘플 위치</div>
      <div class="line">&nbsp;</div>
      <div class="line">// 층이 20개면 조합이 <strong>천문학적</strong>이 된다</div>
    </div>
    <p>
      사람이 고르는 방식은 <em>경험과 직관</em>이다.
      잘 작동해 왔지만 한계가 분명하다 —
      <strong>사람이 시도해 본 것 중에서만</strong> 고르게 된다.
      그리고 목표 장비가 바뀔 때마다 다시 조율해야 한다.
    </p>
    <p>
      <strong>NAS</strong>(신경망 구조 탐색)는 이것을 <em>최적화 문제</em>로 바꾼다.
      구조를 탐색 공간의 한 점으로 보고, 좋은 점을 자동으로 찾는다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>평가가 비싸다는 것이 핵심 난점</h2>
    <p>
      최적화라면 후보를 평가해야 한다. 그런데 <strong>구조 하나를 평가하려면
      학습을 끝까지 돌려야</strong> 한다 — 며칠이 걸린다.
    </p>
    <p>
      초기 NAS 가 <em>수천 GPU-일</em>을 썼다는 보고가 나온 이유다.
      연구 결과로는 흥미롭지만 실무에서는 쓸 수 없는 비용이다.
    </p>
    <p>
      그래서 이 분야의 발전은 대부분 <strong>"어떻게 싸게 평가할 것인가"</strong>였다.
    </p>

    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>방법</th><th>어떻게 아끼나</th><th>위험</th></tr>
        </thead>
        <tbody>
          <tr><td>조기 종료</td><td>몇 에폭만 학습해 순위를 본다</td><td class="hi">초반 순위가 최종과 다르다</td></tr>
          <tr><td>대리 과제</td><td>작은 데이터·작은 모델로 대신</td><td>전이가 안 될 수 있다</td></tr>
          <tr><td class="hi">가중치 공유</td><td class="hi">한 번 학습해 모든 후보가 나눠 쓴다</td><td class="hi">순위 신뢰도 논란</td></tr>
          <tr><td>성능 예측</td><td>학습 없이 구조만 보고 추정</td><td>예측기 자체가 부정확</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      <strong>가중치 공유</strong>가 판을 바꿨다.
      모든 후보 구조를 포함하는 <em>거대한 하나의 망</em>(supernet)을 학습하고,
      후보는 그 부분망으로 평가한다.
      수천 GPU-일이 <strong>며칠</strong>로 줄었다.
    </p>
    <div class="note">
      <b>다만 논란이 있는 방법이다.</b> 공유된 가중치로 잰 순위가
      <em>따로 학습했을 때의 순위와 일치하는가</em>가 핵심 전제인데,
      상관이 낮다는 보고가 여러 번 나왔다.
      무작위로 고른 구조가 탐색 결과와 비슷했다는 결과도 있다 —
      <a href="few-shot-learning.html">Few-Shot</a>에서 본
      <em>"단순 기준선이 강하다"</em>는 지적과 같은 계열이다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>미분 가능하게 만들기</h2>
    <p>
      구조 선택은 <strong>이산적</strong>이다 — 3×3 이냐 5×5 냐 중 하나를 고른다.
      이산 선택은 미분할 수 없어 경사하강을 쓸 수 없다.
    </p>
    <p>
      <strong>DARTS</strong> 의 해법은 <em>고르지 말고 섞는 것</em>이다.
      모든 후보 연산을 동시에 적용하고 <strong>가중 평균</strong>을 취한다.
      그 가중치를 학습하면 <em>어느 연산이 좋은지</em>가 드러난다.
    </p>
    <div class="eq">
      <span class="cap">이산 선택을 연속 완화로</span>
      <div class="line">o(x) = Σ<sub>i</sub> softmax(α)<sub>i</sub> · o<sub>i</sub>(x)</div>
      <div class="line">&nbsp;</div>
      <div class="line">o<sub>i</sub> = 후보 연산 (3×3, 5×5, 풀링, 항등, …)</div>
      <div class="line">α = <strong>학습되는 구조 파라미터</strong></div>
      <div class="line">&nbsp;</div>
      <div class="line">// 학습이 끝나면 α 가 가장 큰 것만 남긴다 (이산화)</div>
    </div>
    <p>
      <a href="qat.html">QAT 의 STE</a>가 반올림의 미분 불가를 우회했듯,
      여기서는 <em>선택을 가중 평균으로 바꿔</em> 우회한다.
      <strong>이산 문제를 연속으로 완화하는</strong> 같은 계열의 요령이다.
    </p>
    <div class="note">
      <b>이산화 격차가 문제다.</b> 학습 중에는 <em>섞인 상태</em>로 평가되는데
      마지막에 하나만 남긴다. 그 순간 성능이 달라질 수 있다.
      게다가 DARTS 는 <strong>항등·풀링처럼 파라미터 없는 연산으로 쏠리는</strong>
      경향이 보고됐다 — 학습 초기에 안정적이라 α 가 커지고,
      결과적으로 <em>얕고 단순한 구조</em>가 선택되는 문제다.
    </div>
  </section>

  <section>
    <h2><span class="n">04</span>무엇을 목표로 둘 것인가</h2>
    <p>
      온디바이스 관점에서 NAS 의 진짜 가치는 <em>구조를 찾는 것</em>보다
      <strong>목표에 실제 지연을 넣을 수 있다는 것</strong>이다.
    </p>
    <p>
      <a href="efficient-backbone.html">경량 백본</a>에서 봤듯
      <em>FLOPs 를 줄여도 안 빨라지는</em> 경우가 많다.
      그렇다면 FLOPs 대신 <strong>목표 장비에서 잰 시간</strong>을 목표에 넣으면 된다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 230" role="img" aria-label="NAS의 목표 설정 비교. FLOPs를 목표로 하면 실제 지연과 어긋날 수 있고, 목표 장비에서 실측한 지연을 목표로 하면 그 장비에 맞는 구조를 찾지만 다른 장비로 옮기면 이점이 사라진다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="ns-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <text x="24" y="18" font-size="9.5" letter-spacing="1.2" fill="var(--warn)">FLOPs 를 목표로 하면</text>

            <rect x="24" y="30" width="80" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="64" y="47" text-anchor="middle" font-size="8" fill="var(--ink-soft)">후보 구조</text>
            <path d="M110 43 L132 43" stroke="var(--warn)" stroke-width="1.2" marker-end="url(#ns-a)"/>
            <rect x="136" y="30" width="80" height="26" fill="var(--warn)" opacity="0.2" stroke="var(--warn)" stroke-width="1.1"/>
            <text x="176" y="47" text-anchor="middle" font-size="8" fill="var(--ink)">FLOPs 계산</text>
            <text x="230" y="40" font-size="8" fill="var(--warn)">값싸고 빠르다</text>
            <text x="230" y="54" font-size="8" fill="var(--warn)">그런데 실제 지연과 어긋난다</text>
            <text x="24" y="76" font-size="8" fill="var(--ink-faint)">depthwise 는 FLOPs 가 작지만 대역폭에 묶여 예상만큼 안 빠르다</text>

            <line x1="24" y1="92" x2="674" y2="92" stroke="var(--rule)" stroke-width="1"/>

            <text x="24" y="112" font-size="9.5" letter-spacing="1.2" fill="var(--accent)">실측 지연을 목표로</text>

            <rect x="24" y="124" width="80" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="64" y="141" text-anchor="middle" font-size="8" fill="var(--ink-soft)">후보 구조</text>
            <path d="M110 137 L132 137" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#ns-a)"/>
            <rect x="136" y="124" width="96" height="26" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.4"/>
            <text x="184" y="141" text-anchor="middle" font-size="8" fill="var(--accent)">목표 기기에서 측정</text>
            <path d="M238 137 L260 137" stroke="var(--accent-line)" stroke-width="1.2" marker-end="url(#ns-a)"/>
            <rect x="264" y="124" width="120" height="26" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.1"/>
            <text x="324" y="141" text-anchor="middle" font-size="8" fill="var(--ink-soft)">정확도 × 지연 벌점</text>

            <text x="400" y="132" font-size="8" fill="var(--accent)">그 장비에 맞는 구조가 나온다</text>
            <text x="400" y="146" font-size="8" fill="var(--ink-faint)">연산자 지원·메모리 특성까지 반영</text>

            <text x="24" y="172" font-size="8.5" fill="var(--warn)">대가 — 결과가 장비에 묶인다</text>
            <text x="24" y="188" font-size="8" fill="var(--ink-faint)">A 폰에서 최적인 구조가 B 폰에서는 아닐 수 있다. 가속기마다 지원 연산자와 최적화가 다르다.</text>
            <text x="24" y="206" font-size="8" fill="var(--ink-faint)">측정 자체도 비싸므로, 층별 지연을 미리 재서 <tspan fill="var(--accent)">더해 추정하는</tspan> 방식이 흔히 쓰인다.</text>
            <text x="24" y="222" font-size="8" fill="var(--warn)">다만 그 가산 가정도 근사다 — 연산자 융합이 일어나면 맞지 않는다.</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        NAS 의 실질적 기여는 <strong>목표를 바꿀 수 있다는 것</strong>이다.
        정확도만 보던 것에서 <em>정확도와 실측 지연의 절충</em>으로 목표를 옮기면,
        같은 탐색 기법으로 전혀 다른 구조가 나온다.
        <a href="mobile-runtime.html">배포 제약</a>을 설계 단계에 넣는 방법이기도 하다.
      </figcaption>
    </figure>

    <p>
      <strong>Once-for-All</strong> 계열은 여기서 한 걸음 더 간다.
      supernet 을 한 번 학습해 두고, <em>장비마다 다른 부분망을 뽑아 쓴다</em>.
      기기별로 탐색을 다시 돌릴 필요가 없어져
      <a href="mobile-runtime.html">기기 파편화</a> 문제에 실용적 답이 된다.
    </p>
  </section>

  <section>
    <h2><span class="n">05</span>NAS 는 무엇을 남겼나</h2>
    <p>
      냉정하게 보면 NAS 는 <em>기대만큼 판을 바꾸지는 못했다</em>.
      "사람을 대체하는 자동 설계"라는 초기 서사와 달리,
      실제로는 <strong>사람이 좁혀 놓은 공간 안에서 미세 조정</strong>하는 도구에 가깝다.
    </p>
    <p>
      탐색 공간을 설계하는 것 자체가 <em>강한 사전지식</em>을 요구한다 —
      어떤 연산을 후보로 둘지, 블록을 어떻게 구성할지는 사람이 정한다.
      <a href="efficient-backbone.html">MobileNetV3</a> 가 탐색 결과에
      사람의 판단(마지막 단계의 비싼 층 제거, 활성함수 교체)을 더한 것이 상징적이다.
    </p>
    <div class="note">
      <b>비교 기준이 흔들린 것도 문제였다.</b> NAS 로 찾은 구조가 좋아 보였는데,
      <em>같은 학습 레시피</em>로 기존 구조를 학습하니 격차가 크게 줄었다는 결과가 반복됐다.
      구조의 이득과 <strong>학습 방법의 이득</strong>이 섞여 있었던 것이다 —
      <a href="yolov5.html">YOLOv5</a>·<a href="cnn-basics.html">ConvNeXt</a> 에서 본
      <em>"구조보다 잘 조율된 학습"</em>이라는 결론이 여기서도 반복된다.
    </div>
    <p>
      그럼에도 남은 것이 있다.
    </p>
    <ul>
      <li><strong>하드웨어 인지 설계라는 관점</strong> — 목표에 실측 지연을 넣는 것이 표준이 됐다</li>
      <li><strong>한 번 학습해 여러 크기를 뽑는 방식</strong> — 기기 파편화에 대한 실용적 답</li>
      <li><strong>탐색 공간을 명시하는 습관</strong> — 무엇을 고정하고 무엇을 열어 둘지 문서화하게 됐다</li>
    </ul>
    <p>
      실무 판단은 이렇게 정리된다.
      <em>이미 검증된 경량 백본으로 시작하는 것</em>이 대개 낫고,
      NAS 는 <strong>특수한 하드웨어나 극단적 제약</strong>이 있을 때
      — 그리고 탐색 비용을 감당할 수 있을 때 — 값어치가 있다.
      <a href="knowledge-distillation.html">증류</a>나 <a href="ondevice-quantization.html">양자화</a>가
      대체로 더 확실한 이득을 준다.
    </p>
  </section>
"""

READING = [
    "Zoph &amp; Le, <em>Neural Architecture Search with Reinforcement Learning</em> (arXiv:1611.01578) — 초기 NAS. 막대한 탐색 비용.",
    "Pham et al., <em>Efficient Neural Architecture Search via Parameter Sharing</em> (arXiv:1802.03268) — 가중치 공유로 비용을 낮춘 전환점.",
    "Liu et al., <em>DARTS: Differentiable Architecture Search</em> (arXiv:1806.09055) — 이산 선택의 연속 완화.",
    "Tan et al., <em>MnasNet: Platform-Aware Neural Architecture Search for Mobile</em> (arXiv:1807.11626) — 실측 지연을 목표에 넣기.",
    "Cai et al., <em>Once-for-All: Train One Network and Specialize it for Efficient Deployment</em> (arXiv:1908.09791) — 기기별 부분망 추출.",
    "Yu et al., <em>Evaluating the Search Phase of Neural Architecture Search</em> (arXiv:1902.08142) — 무작위 기준선과의 비교.",
]

write(
    "nas.html",
    title="NAS — 구조를 자동으로 찾기",
    eyebrow="Architecture · On-Device · 2016–2026",
    h1="NAS",
    subtitle="구조를 자동으로 찾기 — 그리고 목표를 바꾸는 일",
    dek=(
        "층마다 커널 크기·확장 비율·채널 수를 고르면 조합이 천문학적이 된다. "
        "NAS 는 이것을 최적화 문제로 바꾸지만, "
        "<strong>후보 하나를 평가하려면 학습을 끝까지 돌려야</strong> 한다는 난점이 있다. "
        "이 분야의 발전은 대부분 <em>어떻게 싸게 평가할 것인가</em>였다."
    ),
    spec=[
        ("핵심 난점", "평가가 비싸다"),
        ("전환점", "가중치 공유 (supernet)"),
        ("미분 가능화", "이산 선택 → 가중 평균"),
        ("실질적 기여", "목표에 실측 지연"),
        ("냉정한 평가", "학습 레시피 이득과 섞임"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-11",
)
