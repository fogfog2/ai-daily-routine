#!/usr/bin/env python3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import write

LIGHT = dict(paper="#f0f0f1", panel="#e6e6e8", ink="#15161a", **{
    "ink-soft": "#4e5058", "ink-faint": "#7d7f88", "rule": "#d0d1d5",
    "rule-strong": "#acadb3", "accent": "#0a5f92", "accent-fill": "#d7e8f4",
    "accent-line": "#2a83b8", "muted": "#84868c", "muted-fill": "#dfe0e3", "warn": "#a3452a",
})
DARK = dict(paper="#101114", panel="#18191d", ink="#e6e7ec", **{
    "ink-soft": "#a2a4ad", "ink-faint": "#757882", "rule": "#212226", "rule-strong": "#383a42",
    "accent": "#54b6ea", "accent-fill": "#0d2738", "accent-line": "#3080b0",
    "muted": "#86888f", "muted-fill": "#1a1b1f", "warn": "#e0855e",
})

BODY = r"""
  <section>
    <h2><span class="n">01</span>왜 32비트를 쓰고 있었나</h2>
    <p>
      딥러닝은 오랫동안 fp32를 기본값으로 썼다. 이유는 관성에 가깝다 —
      과학 계산의 표준이 그랬고, 정밀도가 부족해 학습이 실패하는 것을 겪고 싶지 않았다.
    </p>
    <p>
      그런데 16비트로 내리면 얻는 것이 여럿이다.
    </p>
    <ul>
      <li><strong>메모리 절반.</strong> 가중치·활성값·그래디언트 모두 절반이 된다.</li>
      <li><strong>대역폭 절반.</strong> 같은 데이터를 절반의 시간에 읽는다. memory-bound 구간이 그만큼 짧아진다.</li>
      <li><strong>텐서 코어.</strong> 이것이 가장 크다. 최신 GPU는 16비트 행렬곱 전용 유닛을 갖고 있고, fp32 대비 <em>수 배에서 십수 배</em> 빠르다.</li>
    </ul>
    <p>
      문제는 16비트가 담을 수 있는 <strong>범위</strong>다.
      비트를 어디에 배분하느냐에 따라 이야기가 완전히 달라진다.
    </p>
  </section>

  <section>
    <h2><span class="n">02</span>fp16과 bf16 — 지수부를 지킬 것인가</h2>
    <p>
      부동소수점은 <strong>부호 · 지수부 · 가수부</strong>로 나뉜다.
      지수부는 <em>표현 범위</em>를, 가수부는 <em>정밀도</em>를 정한다.
      16비트를 어떻게 쪼개느냐가 두 형식을 가른다.
    </p>
    <div class="eq">
      <span class="cap">비트 배분이 성격을 정한다</span>
      <div class="line">fp32&nbsp;&nbsp; 부호 1 · 지수 <strong>8</strong> · 가수 23&nbsp;&nbsp;&nbsp;범위 ~1e±38</div>
      <div class="line">fp16&nbsp;&nbsp; 부호 1 · 지수 <strong>5</strong> · 가수 10&nbsp;&nbsp;&nbsp;범위 ~6e−8 ~ 65504</div>
      <div class="line">bf16&nbsp;&nbsp; 부호 1 · 지수 <strong>8</strong> · 가수 7&nbsp;&nbsp;&nbsp;&nbsp;범위 fp32 와 동일</div>
    </div>
    <p>
      <strong>bf16은 fp32의 지수부를 그대로 유지</strong>하고 가수부를 희생했다.
      정밀도는 fp16보다 낮지만 <em>표현 범위가 fp32와 같다</em>.
      이 선택이 결정적이었던 이유는 다음 절에서 드러난다.
    </p>
    <div class="note">
      <b>딥러닝에는 정밀도보다 범위가 중요했다.</b> 신경망은 노이즈에 강해
      가수부 몇 비트가 줄어드는 것을 잘 견딘다. 반면 값이 표현 범위를 벗어나
      <code>0</code>이나 <code>inf</code>가 되면 그 순간 학습이 망가진다.
      <em>조금 부정확한 값</em>과 <em>완전히 사라진 값</em>은 전혀 다른 문제다.
    </div>
  </section>

  <section>
    <h2><span class="n">03</span>fp16이 무너지는 곳 — 그래디언트 언더플로</h2>
    <p>
      fp16의 최소 정규값은 약 <code>6e−5</code>다(비정규값까지 쓰면 <code>6e−8</code>).
      그런데 <strong>학습 후반의 그래디언트는 이보다 작은 경우가 흔하다</strong>.
      특히 층이 깊고 학습이 수렴에 가까워질수록 그렇다.
    </p>
    <p>
      범위를 벗어난 값은 <code>0</code>이 된다. 그래디언트가 0이면 그 가중치는 갱신되지 않는다.
      전체가 터지지도 않고 조용히 학습이 멈춘다 — 진단하기 어려운 종류의 실패다.
    </p>
    <p>
      해법이 <strong>손실 스케일링</strong>이다. 발상은 단순하다 —
      역전파 전에 손실에 큰 수를 곱해 <em>그래디언트를 표현 가능한 구간으로 밀어 올린다</em>.
      갱신 직전에 같은 수로 나눠 되돌린다.
    </p>
    <div class="eq">
      <span class="cap">손실 스케일링 — 곱했다가 나눈다</span>
      <div class="line">① L' = L × S&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(S ≈ 2¹⁵ 등)</div>
      <div class="line">② 역전파 → 모든 그래디언트가 S 배로 커진 채 계산됨</div>
      <div class="line">③ 옵티마이저 직전에 g ← g / S 로 되돌림</div>
      <div class="line">④ inf/NaN 이 나오면 <strong>그 스텝을 버리고</strong> S 를 절반으로</div>
      <div class="line">&nbsp;&nbsp;&nbsp;한동안 문제없으면 S 를 다시 키운다 (동적 스케일링)</div>
    </div>
    <p>
      곱셈의 연쇄 법칙 덕분에 손실에 <code>S</code>를 곱하면 모든 그래디언트가 정확히 <code>S</code>배가 된다.
      값을 왜곡하지 않고 <em>지수만 이동</em>시키는 셈이다.
    </p>
    <p>
      <strong>bf16에는 이 장치가 필요 없다.</strong> 지수부가 fp32와 같아 언더플로가 나지 않는다.
      손실 스케일링 코드가 통째로 사라지고, 그와 함께 "스케일이 잘못돼 스텝이 계속 버려지는"
      골치 아픈 실패 모드도 사라진다.
      A100 이후 하드웨어가 bf16을 지원하면서 실무의 기본값이 옮겨간 이유다.
    </p>
  </section>

  <section>
    <h2><span class="n">04</span>fp32 마스터 사본 — 왜 여전히 필요한가</h2>
    <p>
      혼합 정밀도라는 이름이 붙은 이유는 <strong>전부를 16비트로 하지 않기</strong> 때문이다.
      가중치의 fp32 사본을 따로 유지하고, 그것을 실제 갱신 대상으로 삼는다.
    </p>
    <p>
      이유는 <strong>작은 갱신량이 삼켜지기</strong> 때문이다.
      학습 후반의 한 스텝 갱신량은 가중치 값에 비해 아주 작다.
      16비트 가수부로는 그 차이를 표현할 수 없어, 더해도 값이 그대로다.
    </p>
    <div class="eq">
      <span class="cap">가수부가 부족하면 덧셈이 무시된다</span>
      <div class="line">w = 1.0,&nbsp; Δw = 0.0001 인 경우</div>
      <div class="line">fp32 (가수 23비트): 1.0 + 0.0001 = 1.0001&nbsp;&nbsp;✓</div>
      <div class="line">bf16 (가수 7비트):&nbsp; 1.0 + 0.0001 = <strong>1.0</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;✗ 갱신 소실</div>
    </div>
    <p>
      그래서 표준 절차는 이렇게 굴러간다.
    </p>

    <figure>
      <div class="plate">
        <svg viewBox="0 0 700 226" role="img" aria-label="혼합 정밀도 학습의 한 스텝 흐름도. fp32 마스터 가중치를 16비트로 변환해 순전파와 역전파를 수행하고, 손실 스케일링으로 그래디언트를 키운 뒤 되돌려 fp32 마스터 가중치를 갱신한다.">
          <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
            <defs>
              <marker id="mp-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-line)"/>
              </marker>
            </defs>

            <rect x="26" y="86" width="104" height="48" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.8"/>
            <text x="78" y="106" text-anchor="middle" font-size="9.5" fill="var(--accent)">fp32 마스터</text>
            <text x="78" y="120" text-anchor="middle" font-size="8.5" fill="var(--accent)">가중치</text>

            <path d="M134 100 L166 100" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#mp-a)"/>
            <text x="150" y="92" text-anchor="middle" font-size="7.5" fill="var(--ink-faint)">캐스트</text>

            <rect x="170" y="80" width="88" height="40" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="214" y="97" text-anchor="middle" font-size="9" fill="var(--ink-soft)">bf16 가중치</text>
            <text x="214" y="110" text-anchor="middle" font-size="8" fill="var(--ink-faint)">사본</text>

            <path d="M262 100 L294 100" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#mp-a)"/>

            <rect x="298" y="72" width="96" height="56" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.3"/>
            <text x="346" y="92" text-anchor="middle" font-size="9" fill="var(--ink-soft)">순전파</text>
            <text x="346" y="106" text-anchor="middle" font-size="9" fill="var(--ink-soft)">역전파</text>
            <text x="346" y="120" text-anchor="middle" font-size="7.5" fill="var(--accent)">텐서 코어</text>

            <path d="M398 100 L430 100" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#mp-a)"/>

            <rect x="434" y="80" width="96" height="40" fill="var(--muted-fill)" stroke="var(--rule-strong)" stroke-width="1.2"/>
            <text x="482" y="97" text-anchor="middle" font-size="9" fill="var(--ink-soft)">bf16</text>
            <text x="482" y="110" text-anchor="middle" font-size="8" fill="var(--ink-faint)">그래디언트</text>

            <path d="M482 124 L482 152" stroke="var(--accent-line)" stroke-width="1.4" marker-end="url(#mp-a)"/>
            <path d="M430 166 L134 166" stroke="var(--accent-line)" stroke-width="1.4" fill="none" marker-end="url(#mp-a)"/>
            <path d="M482 180 L482 190 L78 190 L78 140" stroke="var(--accent-line)" stroke-width="1.4" fill="none" marker-end="url(#mp-a)"/>

            <rect x="434" y="156" width="96" height="24" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.3"/>
            <text x="482" y="172" text-anchor="middle" font-size="8.5" fill="var(--accent)">fp32 로 변환</text>

            <text x="270" y="162" text-anchor="middle" font-size="8" fill="var(--ink-faint)">옵티마이저 스텝은 fp32 에서</text>

            <text x="26" y="30" font-size="9.5" letter-spacing="1.2" fill="var(--ink-soft)">fp16 에만 필요한 장치</text>
            <rect x="26" y="38" width="230" height="30" fill="var(--warn)" opacity="0.15" stroke="var(--warn)" stroke-width="1.2"/>
            <text x="141" y="50" text-anchor="middle" font-size="8" fill="var(--ink)">손실 × S → 역전파 → 그래디언트 / S</text>
            <text x="141" y="62" text-anchor="middle" font-size="8" fill="var(--warn)">inf 나오면 스텝 버리고 S 절반으로</text>

            <rect x="270" y="38" width="230" height="30" fill="var(--accent-fill)" stroke="var(--accent-line)" stroke-width="1.2"/>
            <text x="385" y="50" text-anchor="middle" font-size="8" fill="var(--accent)">bf16 은 지수부가 fp32 와 같아</text>
            <text x="385" y="62" text-anchor="middle" font-size="8" fill="var(--accent)">손실 스케일링이 필요 없다</text>

            <text x="546" y="94" font-size="8.5" fill="var(--ink-soft)">왜 마스터가 필요한가</text>
            <text x="546" y="110" font-size="8" fill="var(--ink-faint)">bf16 가수부는 7비트뿐이라</text>
            <text x="546" y="122" font-size="8" fill="var(--ink-faint)">작은 갱신량이 덧셈에서</text>
            <text x="546" y="134" font-size="8" fill="var(--warn)">그대로 삼켜진다</text>

            <text x="546" y="158" font-size="8" fill="var(--ink-faint)">누적·정규화·softmax 도</text>
            <text x="546" y="170" font-size="8" fill="var(--ink-faint)">fp32 로 계산한다</text>
          </g>
        </svg>
      </div>
      <figcaption>
        <span class="tag">Fig. 1</span>
        <strong>무거운 연산은 16비트로, 누적과 갱신은 32비트로.</strong>
        행렬곱은 텐서 코어에서 16비트로 하되 <em>누산은 fp32</em>로 하고,
        정규화·softmax처럼 값의 범위가 넓은 연산도 fp32를 유지한다.
        "혼합"이라는 이름은 이 역할 분담에서 왔다.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2><span class="n">05</span>더 아래로 — fp8과 그 조건</h2>
    <p>
      Hopper 세대부터 <strong>fp8</strong>이 하드웨어에서 지원된다.
      형식이 둘인데, 쓰임이 다르다.
    </p>
    <div class="scroller">
      <table class="data">
        <thead>
          <tr><th>형식</th><th>지수 / 가수</th><th>성격</th><th>주 용도</th></tr>
        </thead>
        <tbody>
          <tr><td>E4M3</td><td>4 / 3</td><td>범위 좁음 · 정밀도 나음</td><td class="hi">순전파 (가중치·활성값)</td></tr>
          <tr><td>E5M2</td><td>5 / 2</td><td class="hi">범위 넓음 · 정밀도 낮음</td><td>역전파 (그래디언트)</td></tr>
        </tbody>
      </table>
    </div>
    <p>
      배분이 앞의 논리를 그대로 반복한다 —
      <strong>그래디언트는 범위가 중요하고 활성값은 정밀도가 중요하다.</strong>
      그래서 그래디언트에 지수부가 넓은 E5M2를 쓴다.
    </p>
    <p>
      fp8 학습은 텐서마다 스케일 인자를 따로 관리해야 하고
      민감한 층은 높은 정밀도로 남겨야 해서, 여전히 손이 많이 간다.
      그럼에도 최근 대형 모델 학습에서 실제로 쓰였다는 보고가 늘고 있다.
    </p>
    <div class="note">
      <b>추론에서의 저정밀도와는 다른 문제다.</b>
      <a href="quantization.html">양자화</a>는 <em>학습이 끝난</em> 가중치를 4비트로 줄이는 일이라
      그래디언트를 신경 쓸 필요가 없다.
      학습 중 저정밀도가 훨씬 까다로운 이유는 <strong>역전파를 통과해야</strong> 하기 때문이다 —
      한 번 0이 된 그래디언트는 복구할 방법이 없다.
    </div>
    <p>
      정리하면 혼합 정밀도의 교훈은 하나로 압축된다.
      <em>비트를 줄일 때 먼저 물어야 할 것은 정밀도가 아니라 범위다.</em>
      bf16이 fp16을 밀어낸 것도, fp8이 두 형식으로 나뉜 것도 같은 이유에서다.
    </p>
  </section>
"""

READING = [
    "Micikevicius et al., <em>Mixed Precision Training</em> (arXiv:1710.03740) — fp32 마스터 사본과 손실 스케일링.",
    "Kalamkar et al., <em>A Study of BFLOAT16 for Deep Learning Training</em> (arXiv:1905.12322) — bf16이 왜 더 안전한가.",
    "Micikevicius et al., <em>FP8 Formats for Deep Learning</em> (arXiv:2209.05433) — E4M3·E5M2 배분의 근거.",
    "Wang et al., <em>Training Deep Neural Networks with 8-bit Floating Point Numbers</em> (NeurIPS 2018) — 8비트 학습의 초기 연구.",
    "Peng et al., <em>FP8-LM: Training FP8 Large Language Models</em> (arXiv:2310.18313) — 실제 LLM 학습에 적용한 사례.",
]

write(
    "mixed-precision.html",
    title="Mixed Precision — 16비트로 학습하기",
    eyebrow="Infrastructure · Numerical Stability · 2017–2026",
    h1="Mixed Precision",
    subtitle="16비트로 학습하기 — 정밀도가 아니라 범위가 문제였다",
    dek=(
        "16비트로 내리면 메모리와 대역폭이 절반이 되고 텐서 코어를 쓸 수 있다. "
        "그런데 fp16은 <strong>작은 그래디언트를 0으로 삼켜</strong> 학습을 조용히 멈춘다. "
        "bf16은 가수부를 희생하는 대신 fp32의 지수부를 지켜 이 문제를 없앴다. "
        "신경망은 부정확한 값은 견디지만 사라진 값은 견디지 못한다."
    ),
    spec=[
        ("fp16", "지수 5 · 언더플로 위험"),
        ("bf16", "지수 8 · fp32와 동일 범위"),
        ("fp16 필수 장치", "손실 스케일링"),
        ("마스터 사본", "fp32 (갱신 소실 방지)"),
        ("fp8", "E4M3 순전파 · E5M2 역전파"),
    ],
    body=BODY,
    reading=READING,
    light=LIGHT,
    dark=DARK,
    date="2026-08-10",
)
